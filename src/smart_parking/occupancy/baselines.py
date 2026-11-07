"""Two occupancy baselines, fitted on train and tuned on validation only.

1. Texture threshold: one image statistic and a cut-off (empty asphalt looks flat).
2. HOG features + logistic regression.
"""

import json
from pathlib import Path

import joblib
import numpy as np
from loguru import logger
from skimage.feature import hog
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from smart_parking.common.config import OccupancyTrainConfig
from smart_parking.occupancy.images import SplitData, load_split
from smart_parking.occupancy.metrics import best_threshold, binary_metrics

TEXTURE_FEATURES = ("contrast", "edges")


def _gray(images: np.ndarray) -> np.ndarray:
    return images.astype(np.float32) @ np.array([0.299, 0.587, 0.114], dtype=np.float32)


def texture_features(images: np.ndarray) -> dict[str, np.ndarray]:
    """Per-crop grey-level standard deviation and mean gradient magnitude."""
    g = _gray(images)
    gy, gx = np.gradient(g, axis=(1, 2))
    return {
        "contrast": g.std(axis=(1, 2)),
        "edges": np.sqrt(gx**2 + gy**2).mean(axis=(1, 2)),
    }


def texture_scores(images: np.ndarray, feature: str) -> np.ndarray:
    """Score used by the texture baseline (higher = more likely occupied)."""
    return texture_features(images)[feature]


def hog_features(images: np.ndarray) -> np.ndarray:
    """HOG descriptor of each grey crop (9 orientations, 8x8 cells, 2x2 blocks)."""
    return np.stack(
        [
            hog(g, orientations=9, pixels_per_cell=(8, 8), cells_per_block=(2, 2))
            for g in _gray(images)
        ]
    ).astype(np.float32)


def fit_texture(val: SplitData) -> dict:
    """Pick the feature and cut-off with the best validation F1.

    The rule has no trainable weights, so the train split is not needed.
    """
    best: dict = {}
    feats = texture_features(val.images)
    for name in TEXTURE_FEATURES:
        thr = best_threshold(val.labels, feats[name])
        m = binary_metrics(val.labels, feats[name] >= thr)
        logger.bind(baseline="texture").info("{}: val F1 {:.4f} at {:.3f}", name, m["f1"], thr)
        if not best or m["f1"] > best["val"]["f1"]:
            best = {"feature": name, "threshold": thr, "val": m}
    return best


def fit_hog(train: SplitData, val: SplitData, c_grid: list[float], seed: int):
    """Fit HOG + logistic regression on train; pick C and the threshold on validation."""
    xtr, xva = hog_features(train.images), hog_features(val.images)
    best: dict = {}
    for c in c_grid:
        model = make_pipeline(
            StandardScaler(), LogisticRegression(C=c, max_iter=3000, random_state=seed)
        )
        model.fit(xtr, train.labels)
        score = model.predict_proba(xva)[:, 1]
        thr = best_threshold(val.labels, score)
        m = binary_metrics(val.labels, score >= thr)
        logger.bind(baseline="hog_lr").info("C={}: val F1 {:.4f} at {:.3f}", c, m["f1"], thr)
        if not best or m["f1"] > best["val"]["f1"]:
            best = {"C": c, "threshold": thr, "val": m, "model": model}
    return best


def run_baselines(cfg: OccupancyTrainConfig, seed: int) -> dict:
    """Fit both baselines, save them, and return their validation results."""
    args = (cfg.dataset_csv, cfg.raw_root, cfg.cache_dir)
    train = load_split("train", cfg.baseline_size, *args)
    val = load_split("val", cfg.baseline_size, *args)
    cfg.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    cfg.results_dir.mkdir(parents=True, exist_ok=True)

    texture = fit_texture(val)
    (cfg.checkpoint_dir / "texture_threshold.json").write_text(json.dumps(texture, indent=2))

    hog_best = fit_hog(train, val, cfg.hog_c_grid, seed)
    joblib.dump(
        {"model": hog_best.pop("model"), "threshold": hog_best["threshold"]},
        cfg.checkpoint_dir / "hog_lr.joblib",
    )
    results = {"texture_threshold": texture, "hog_lr": hog_best}
    Path(cfg.results_dir / "baselines_val.json").write_text(json.dumps(results, indent=2))
    logger.info("Baselines saved to {}", cfg.checkpoint_dir)
    return results


def main() -> None:
    from smart_parking.common.config import load_config
    from smart_parking.common.log import setup_logging
    from smart_parking.common.seed import set_seed

    cfg = load_config()
    setup_logging(cfg.logging)
    set_seed(cfg.seed)
    run_baselines(cfg.occupancy, cfg.seed)


if __name__ == "__main__":
    main()
