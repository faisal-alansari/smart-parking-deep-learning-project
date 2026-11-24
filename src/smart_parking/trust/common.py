"""Shared inputs for the trust checks: Model A probabilities and Model B reads with confidence.

Model A: the deployed seeds (`occupancy.deploy`) on the video crops; validation = night video 2
block 4, test = the first night video. Model B: the deployed plate model (seed 42) on the public
plate validation and test splits. Results are cached in data/processed/trust/ (not in Git).
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from smart_parking.common.config import load_config
from smart_parking.occupancy.adapt import VIDEO_TEST, VIDEO_TRAIN, build_crops
from smart_parking.occupancy.train import load_checkpoint, pick_device, predict, to_tensor
from smart_parking.plates.metrics import MATCH_IOU, score_image
from smart_parking.plates.reader import Box, iou, read_plates

CACHE = Path("data/processed/trust")
OUT = Path("outputs/trust")
PLATE_SEED = 42


def occupancy_models(device: torch.device | None = None) -> list[tuple]:
    cfg = load_config().occupancy
    device = device or pick_device()
    return [
        load_checkpoint(cfg.checkpoint_dir / f"{cfg.deploy}_s{s}.pt", device) for s in cfg.seeds
    ]


def occupancy_scores(images: np.ndarray, models: list[tuple]) -> tuple[np.ndarray, np.ndarray]:
    """(mean probability of the seeds, the product's majority-vote decision)."""
    device = next(models[0][0].parameters()).device
    x = to_tensor(images, device)
    probs = [predict(m, x, mean, std) for m, mean, std, _ in models]
    votes = np.mean([p >= s["threshold"] for p, (_, _, _, s) in zip(probs, models, strict=True)], 0)
    return np.mean(probs, axis=0), votes > 0.5


def occupancy_sets() -> dict[str, tuple[np.ndarray, pd.DataFrame]]:
    """Validation (block 4) and test (first video) crops with their labels."""
    images, meta = build_crops(VIDEO_TRAIN, 64)
    va = (meta["split"] == "validation").to_numpy()
    test_images, test_meta = build_crops(VIDEO_TEST, 64)
    return {"validation": (images[va], meta[va].reset_index(drop=True)),
            "test": (test_images, test_meta)}  # fmt: skip


def plate_rows(split: str) -> pd.DataFrame:
    """One row per public plate image: the matched read, its confidence and whether it is right."""
    cache = CACHE / f"plate_reads_{split}.csv"
    if cache.exists():
        return pd.read_csv(cache, keep_default_na=False)
    from smart_parking.plates.train import ground_truth, predict_boxes

    cfg = load_config().plates
    summary = json.loads((cfg.run_dir / f"final_s{PLATE_SEED}" / "summary.json").read_text())
    truth = ground_truth(cfg, split, allow_test=split == "test")
    images = sorted((cfg.yolo_dir / split / "images").iterdir())
    boxes = predict_boxes(cfg.checkpoint_dir / f"final_s{PLATE_SEED}.pt", images, summary["imgsz"],
                          cfg.device)  # fmt: skip
    rows = []
    for key, t in truth.items():
        reads = read_plates(boxes.get(key, []), summary["threshold"])
        tb = Box("plate", 1.0, *t.box)
        best = max(reads, key=lambda r: iou(tb, Box("plate", 1.0, *r.box)), default=None)
        if best is not None and iou(tb, Box("plate", 1.0, *best.box)) < MATCH_IOU:
            best = None
        s = score_image(t, reads)
        rows.append({"image": key, "found": s["found"], "answered": s["answered"],
                     "correct": s["correct"], "confidence": best.confidence if best else 0.0,
                     "reason": s["reason"] or ""})  # fmt: skip
    CACHE.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(cache, index=False)
    return df


def md(df: pd.DataFrame) -> str:
    lines = ["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)]
    lines += ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(lines)
