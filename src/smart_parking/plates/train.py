"""Fine-tune YOLO11n on the plate subset and score plate reads on validation.

Ultralytics runs offline (no usage data sent). Horizontal and vertical flips are
off because mirrored plates never occur. Test images are only read by `final.py`.
"""

import os

os.environ.setdefault("YOLO_OFFLINE", "1")

import gc
import json
import re
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import yaml
from loguru import logger
from torch.utils.tensorboard import SummaryWriter
from ultralytics import YOLO

from smart_parking.common.config import PlateTrainConfig
from smart_parking.plates.metrics import score_image, summarise
from smart_parking.plates.reader import Box, PlateRead, read_plates

IMAGE_W, IMAGE_H = 1440, 1280
LOW_CONF = 0.05
PREDICT_CHUNK = 16
TEST_SPLITS = ("test",)


def _stem_chars(image: str) -> str:
    stem = re.sub(r"_(png|jpe?g|webp)$", "", image.split("_jpg.rf.")[0], flags=re.IGNORECASE)
    return "".join(sorted(c for c in stem if c.isalnum()))


def ground_truth(
    cfg: PlateTrainConfig, split: str, allow_test: bool = False
) -> dict[str, PlateRead]:
    """Main labelled plate per image: the plate whose characters match the file name,
    else the largest plate with characters."""
    if split in TEST_SPLITS and not allow_test:
        raise PermissionError("The test split is reserved for the final evaluation")
    names = yaml.safe_load((cfg.yolo_dir / "data.yaml").read_text())["names"]
    truth = {}
    for lbl in sorted((cfg.yolo_dir / split / "labels").glob("*.txt")):
        boxes = []
        for ln in lbl.read_text().split("\n"):
            if ln.strip():
                c, cx, cy, w, h = ln.split()
                cx, cy, w, h = map(float, (cx, cy, w, h))
                boxes.append(
                    Box(
                        names[int(c)],
                        1.0,
                        (cx - w / 2) * IMAGE_W,
                        (cy - h / 2) * IMAGE_H,
                        (cx + w / 2) * IMAGE_W,
                        (cy + h / 2) * IMAGE_H,
                    )
                )
        reads = [r for r in read_plates(boxes, 0.5) if r.text]
        if not reads:
            continue
        target = _stem_chars(lbl.stem)
        named = [r for r in reads if "".join(sorted(r.text)) == target]
        pool = named or reads
        truth[lbl.stem] = max(pool, key=lambda r: (r.box[2] - r.box[0]) * (r.box[3] - r.box[1]))
    return truth


def predict_boxes(
    weights: Path, images: list[Path], imgsz: int, device: str
) -> dict[str, list[Box]]:
    """All detections above a low confidence, per image stem.

    Images go in small chunks: Ultralytics stacks a whole list source into one
    batch, which runs out of GPU memory at 960 px.
    """
    model = YOLO(str(weights))
    out = {}
    paths = [str(p) for p in images]
    results = (
        res
        for i in range(0, len(paths), PREDICT_CHUNK)
        for res in model.predict(
            source=paths[i : i + PREDICT_CHUNK],
            imgsz=imgsz,
            conf=LOW_CONF,
            device=device,
            stream=True,
            verbose=False,
            max_det=100,
        )
    )
    for res in results:
        names = res.names
        xyxy = res.boxes.xyxy.cpu().numpy()
        out[Path(res.path).stem] = [
            Box(names[int(c)], float(p), *map(float, b))
            for c, p, b in zip(
                res.boxes.cls.cpu().numpy(), res.boxes.conf.cpu().numpy(), xyxy, strict=True
            )
        ]
    return out


def score(truth: dict[str, PlateRead], boxes: dict[str, list[Box]], conf: float) -> list[dict]:
    """Per-image scores at one confidence threshold."""
    return [
        {"image": k, **score_image(t, read_plates(boxes.get(k, []), conf))}
        for k, t in truth.items()
    ]


def choose_threshold(truth, boxes, grid: list[float]) -> tuple[float, dict]:
    """Confidence threshold with the best validation exact match."""
    results = {c: summarise(score(truth, boxes, c)) for c in grid}
    best = max(grid, key=lambda c: results[c]["exact_match"])
    return best, results[best]


def _train_list(cfg: PlateTrainConfig, size: int, seed: int) -> Path:
    """data.yaml for training on `size` images (stratified by emirate) or the full train set."""
    if size >= 5000:
        return cfg.yolo_dir / "data.yaml"
    ledger = pd.read_csv(cfg.ledger_csv)
    train = ledger[ledger["split"] == "train"]
    frac = size / len(train)
    part = train.groupby("family", group_keys=False).sample(frac=frac, random_state=seed)
    part = part.iloc[:size]
    lst = cfg.yolo_dir / f"train_{size}.txt"
    # absolute(), not resolve(): images are symlinks to the raw download, and Ultralytics
    # finds each label next to the image path, so resolving would load the raw labels.
    lst.write_text(
        "\n".join(str((cfg.yolo_dir / "train" / "images" / i).absolute()) for i in part["image"])
    )
    data = yaml.safe_load((cfg.yolo_dir / "data.yaml").read_text())
    data["train"] = str(lst.resolve())
    out = cfg.yolo_dir / f"data_train{size}.yaml"
    out.write_text(yaml.safe_dump(data, sort_keys=False))
    return out


def _export_tensorboard(run: Path) -> None:
    """Write the Ultralytics per-epoch results.csv as TensorBoard scalars."""
    csv = run / "results.csv"
    if not csv.exists():
        return
    df = pd.read_csv(csv)
    df.columns = [c.strip() for c in df.columns]
    with SummaryWriter(str(run / "tensorboard")) as w:
        for row in df.itertuples(index=False):
            for k, v in row._asdict().items():
                if k != "epoch":
                    w.add_scalar(k, float(v), int(row.epoch))


def _fit(cfg: PlateTrainConfig, run_name: str, seed: int, pretrained: bool) -> None:
    """Run Ultralytics training, then free the GPU memory it held."""
    data = _train_list(cfg, cfg.train_size, seed)
    model = YOLO(str(cfg.pretrained_weights) if pretrained else "yolo11n.yaml")
    logger.bind(run=run_name).info(
        "Training ({}, imgsz {}, freeze {}, {} images)",
        "pretrained" if pretrained else "random init",
        cfg.imgsz,
        cfg.freeze,
        cfg.train_size,
    )
    model.train(
        data=str(data),
        imgsz=cfg.imgsz,
        epochs=cfg.epochs,
        patience=cfg.patience,
        batch=cfg.batch,
        device=cfg.device,
        workers=cfg.workers,
        seed=seed,
        deterministic=True,
        pretrained=pretrained,
        freeze=cfg.freeze,
        fliplr=0.0,
        flipud=0.0,
        project=str(cfg.run_dir.resolve()),
        name=run_name,
        exist_ok=True,
        plots=True,
        verbose=False,
    )
    del model
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()


def train_run(cfg: PlateTrainConfig, run_name: str, seed: int, pretrained: bool = True) -> dict:
    """Train one model on train, keep the best epoch by validation mAP, then tune the
    reading threshold on validation and return the validation summary."""
    log = logger.bind(run=run_name)
    run = cfg.run_dir / run_name
    weights = cfg.checkpoint_dir / f"{run_name}.pt"
    if weights.exists():  # training finished earlier; only redo the validation scoring
        log.info("Reusing trained weights {}", weights)
    else:
        _fit(cfg, run_name, seed, pretrained)
        _export_tensorboard(run)
        cfg.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(run / "weights" / "best.pt", weights)
    history = pd.read_csv(run / "results.csv")

    truth = ground_truth(cfg, "val")
    images = sorted((cfg.yolo_dir / "val" / "images").iterdir())
    boxes = predict_boxes(weights, images, cfg.imgsz, cfg.device)
    threshold, val = choose_threshold(truth, boxes, cfg.conf_grid)
    params = sum(p.numel() for p in YOLO(str(weights)).model.parameters())
    summary = {
        "run": run_name,
        "seed": seed,
        "pretrained": pretrained,
        "imgsz": cfg.imgsz,
        "freeze": cfg.freeze,
        "train_size": cfg.train_size,
        "params": int(params),
        "threshold": threshold,
        "val": val,
        "train_seconds": round(float(history["time"].iloc[-1]), 1),
        "epochs_run": int(len(history)),
    }
    (run / "summary.json").write_text(json.dumps(summary, indent=2))
    log.info(
        "Val exact match {:.4f} at conf {} ({} s)",
        val["exact_match"],
        threshold,
        summary["train_seconds"],
    )
    return summary


def val_detection_metrics(weights: Path, cfg: PlateTrainConfig) -> dict:
    """Ultralytics mAP on validation (all classes and the plate class)."""
    m = YOLO(str(weights)).val(
        data=str(cfg.yolo_dir / "data.yaml"),
        split="val",
        imgsz=cfg.imgsz,
        device=cfg.device,
        verbose=False,
        plots=False,
    )
    return {
        "map50": float(m.box.map50),
        "map50_95": float(m.box.map),
        "mean_precision": float(m.box.mp),
        "mean_recall": float(m.box.mr),
        "n_val": int(np.size(m.box.maps)),
    }
