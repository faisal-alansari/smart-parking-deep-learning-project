"""Two choices once informed by night video 1, made again on block 4 (validation) only.

Block 4 of night video 2 is split into two folds of alternating 60-second blocks (time halves
would leave one fold with parked cars only); each check fits on one fold and is measured on the
other, both ways. Rules fixed before running (Memory.md, 2026-11-26):
1. **Model A confidence:** Platt scaling only if its mean held-out ECE is lower than the raw
   probability's; otherwise (or a tie) the raw probability.
2. **Feature-distance bay check:** used only if its held-out false-alarm rate is at most 2% and
   it catches at least 5% of corrupted block-4 frames that the blocked, view and sharpness checks
   miss.
No test data is read. Plate caching, the third choice, is decided in `just efficiency`.
`just validation-choices`.
"""

import json

import numpy as np
import pandas as pd
import yaml
from loguru import logger
from sklearn.covariance import LedoitWolf

from smart_parking.common.config import load_config
from smart_parking.common.log import setup_logging
from smart_parking.occupancy.adapt import VIDEO_TRAIN, build_crops
from smart_parking.trust.calibration import apply_platt, ece, platt
from smart_parking.trust.common import OUT, md, occupancy_models, occupancy_scores
from smart_parking.trust.ood import (
    DETECTOR,
    EVERY,
    _corrupt,
    _crops,
    _frame_at,
    _frames,
    bay_distance,
    features,
    frame_check,
    sharpness,
    small_view,
    view_similarity,
)

CORRUPTIONS = ("camera moved (shifted and zoomed)", "heavy blur", "over-exposed (x3)",
               "lens almost covered", "pure noise")  # fmt: skip


FOLD_SECONDS = 60
FOLDS = ("even minutes", "odd minutes")


def _folds(t: np.ndarray) -> list[np.ndarray]:
    """Boolean masks of the two folds: alternating 60-second blocks of video time."""
    even = (np.asarray(t) // FOLD_SECONDS) % 2 == 0
    return [even, ~even]


def calibration_choice() -> tuple[pd.DataFrame, str]:
    """Raw against Platt-scaled Model A probability, each fold held out in turn."""
    images, meta = build_crops(VIDEO_TRAIN, 64)
    va = (meta["split"] == "validation").to_numpy()
    meta = meta[va].reset_index(drop=True)
    p, _ = occupancy_scores(images[va], occupancy_models())
    y = meta["label"].to_numpy()
    rows = []
    for name, held in zip(FOLDS, _folds(meta["t"].to_numpy()), strict=True):
        ab = platt(y[~held], p[~held])
        rows.append({"held-out fold": name, "crops": int(held.sum()),
                     "ECE raw": round(ece(y[held], p[held]), 4),
                     "ECE Platt (fit on the other fold)":
                         round(ece(y[held], apply_platt(p[held], ab)), 4)})  # fmt: skip
    table = pd.DataFrame(rows)
    raw, scaled = table["ECE raw"].mean(), table["ECE Platt (fit on the other fold)"].mean()
    return table, "platt" if scaled < raw else "raw"


def bay_check_choice() -> tuple[pd.DataFrame, bool]:
    """Held-out false alarms of the bay check and the corrupted frames only it catches."""
    cfg = yaml.safe_load(VIDEO_TRAIN.read_text())
    boxes = cfg["boxes"]
    model, mean, std, _ = occupancy_models()[0]
    parts = (model, mean, std)
    images, meta = build_crops(VIDEO_TRAIN, 64)
    lw = LedoitWolf().fit(features(*parts, images[(meta["split"] == "train").to_numpy()]))
    det = {"center": lw.location_, "precision": lw.precision_}
    saved = np.load(DETECTOR)
    sim_cut, sharp_cut = float(saved["similarity_cutoff"]), float(saved["sharpness_cutoff"])
    block4 = next(f["video"] for f in cfg["files"] if f["split"] == "validation")
    snap = _frame_at(block4, 90)
    ref, ref_sharp = small_view(snap, boxes)[0], sharpness(snap)
    frames = _frames(VIDEO_TRAIN, "validation", EVERY)

    def distance(im) -> float:  # noqa: ANN001
        return float(bay_distance(det, features(*parts, _crops(im, boxes))).max())

    def caught_by_product(im) -> bool:  # noqa: ANN001
        return bool(
            frame_check(im)
            or view_similarity(ref, im, boxes) < sim_cut
            or sharpness(im) / ref_sharp < sharp_cut
        )

    dist = np.array([distance(im) for im in frames])
    rows, alarms, extra = [], [], []
    rng = np.random.default_rng(0)
    seconds = np.arange(len(frames)) * EVERY  # `_frames` keeps every EVERY-th second in order
    for name, held in zip(FOLDS, _folds(seconds), strict=True):
        cut = float(np.percentile(dist[~held], 99))
        alarm = float((dist[held] > cut).mean())
        bad = [_corrupt(im, kind, rng) for kind in CORRUPTIONS
               for im, h in zip(frames, held, strict=True) if h]  # fmt: skip
        only_bay = np.mean([distance(im) > cut and not caught_by_product(im) for im in bad])
        alarms.append(alarm)
        extra.append(float(only_bay))
        rows.append({"held-out fold": name, "normal frames": int(held.sum()),
                     "bay check false alarms": f"{alarm:.1%}",
                     "corrupted frames": len(bad),
                     "caught only by the bay check": f"{only_bay:.1%}"})  # fmt: skip
    use = float(np.mean(alarms)) <= 0.02 and float(np.mean(extra)) >= 0.05
    return pd.DataFrame(rows), use


def main() -> None:
    """Run both checks on block 4 and write `outputs/trust/validation_choices.md`."""
    setup_logging(load_config().logging)
    cal, method = calibration_choice()
    bay, use_bay = bay_check_choice()
    (OUT / "validation_choices.json").write_text(
        json.dumps({"occupancy_confidence": method, "bay_check": use_bay}, indent=2) + "\n"
    )
    (OUT / "validation_choices.md").write_text(
        "# Choices made on block 4 (validation) only\n\n"
        + __doc__.split("\n\n", 1)[1].split("`just")[0].strip()
        + "\n\n## 1. Model A confidence\n\n"
        + md(cal)
        + f"\n\n**Chosen: {method}.**\n\n## 2. Feature-distance bay check\n\n"
        + md(bay)
        + f"\n\n**Bay check: {'used' if use_bay else 'not used'}.**\n"
    )
    logger.info("Block 4 choices: A confidence {}, bay check {}", method, use_bay)


if __name__ == "__main__":
    main()
