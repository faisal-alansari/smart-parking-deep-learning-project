"""Shared inputs for the trust checks: Model A probabilities and Model B reads with confidence.

Model A: the deployed seeds (`occupancy.deploy`) on the video crops; validation = night video 2
block 4, test = the sealed night video 3. Model B: the deployed plate model (seed 42) on the public
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
FITTED_CHANGED = (
    "{} differs from the saved, validation-fitted value. `just evaluate` never changes fitted "
    "settings; run `just refit` on purpose (validation data only) and commit the change."
)
FITTED_MISSING = (
    "{} is missing. `just evaluate` never creates fitted settings; restore it from Git or run "
    "`just refit` on purpose (validation data only)."
)
OUT = Path("outputs/trust")
PLATE_SEED = 42


def occupancy_models(device: torch.device | None = None) -> list[tuple]:
    """The deployed Model A checkpoint for each seed: (model, mean, std, summary)."""
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
    """Validation (block 4) and test (sealed night video 3) crops with their labels."""
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


def camera_plate_rows(config: Path, split: str) -> pd.DataFrame:
    """The owner's camera: Model B's raw read in every bay holding a car (one frame every 2 s,
    moving periods left out) and whether it is exactly right. Cached; real plates stay local."""
    cache = CACHE / f"plate_reads_{config.stem}_{split}.csv"
    if cache.exists():
        return pd.read_csv(cache, keep_default_na=False)
    import yaml

    from smart_parking.occupancy.adapt import video_files
    from smart_parking.pipeline import Pipeline, in_any, video_frames

    cfg = yaml.safe_load(config.read_text())
    pipe = Pipeline(commands=False)
    rows = []
    for f in video_files(cfg):
        if f["split"] != split:
            continue
        for t, im in video_frames(Path(f["video"]), cfg["every_s"]):
            if in_any(t, f["moving"]):
                continue
            for bay, box in cfg["boxes"].items():
                here = [c for c in f["cars"] if c["from"] <= t < c["to"]]
                plate = next((c["plate"] for c in here if c["bay"] in (bay, "both")), None)
                if plate is None:
                    continue
                read = pipe.plate_raw(im, box)
                answered = read is not None and read.decision == "READ"
                rows.append({"t": t, "bay": bay, "found": read is not None, "answered": answered,
                             "correct": answered and read.text == plate,
                             "confidence": read.confidence if read else 0.0})  # fmt: skip
    CACHE.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(cache, index=False)
    return df


def md(df: pd.DataFrame) -> str:
    """A DataFrame as a Markdown table."""
    lines = ["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)]
    lines += ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(lines)


def same_numbers(saved: dict, fitted: dict, tol: float = 1e-6) -> bool:
    """Whether two flat or nested dicts of numbers and strings agree (numbers within tol)."""
    if saved.keys() != fitted.keys():
        return False
    for k, a in saved.items():
        b = fitted[k]
        if isinstance(a, dict):
            if not isinstance(b, dict) or not same_numbers(a, b, tol):
                return False
        elif isinstance(a, int | float) and isinstance(b, int | float):
            if not np.isclose(a, b, rtol=tol, atol=tol):
                return False
        elif a != b:
            return False
    return True


def refit_flag() -> bool:
    """`--refit`: store newly fitted settings; default: check them against the saved ones."""
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--refit", action="store_true", help="store newly fitted settings")
    return ap.parse_args().refit
