"""Final OccupancyCNN runs (one per seed) and the one-time test comparison.

`--train` trains the selected configuration with every seed in the config.
`--evaluate` is the only code path that opens the test splits. It scores the two
baselines and the CNN with thresholds chosen earlier on validation.
"""

import argparse
import json

import joblib
import numpy as np
import pandas as pd
from loguru import logger

from smart_parking.common.config import OccupancyTrainConfig, load_config
from smart_parking.common.log import setup_logging
from smart_parking.occupancy.baselines import hog_features, texture_scores
from smart_parking.occupancy.images import TEST_SPLITS, load_split
from smart_parking.occupancy.metrics import METRICS, binary_metrics, cluster_bootstrap_ci
from smart_parking.occupancy.train import (
    load_checkpoint,
    pick_device,
    predict,
    to_tensor,
    train_run,
)

METHODS = ("texture_threshold", "hog_lr", "occupancy_cnn")


def train_final(cfg: OccupancyTrainConfig) -> list[dict]:
    """Train the selected configuration once per seed."""
    return [train_run(cfg, seed, f"final_s{seed}") for seed in cfg.seeds]


def _method_predictions(cfg: OccupancyTrainConfig, split: str) -> tuple[dict, pd.DataFrame]:
    """Binary predictions of every method on one test split (CNN: one array per seed)."""
    args = (cfg.dataset_csv, cfg.raw_root, cfg.cache_dir)
    small = load_split(split, cfg.baseline_size, *args, allow_test=True)
    texture = json.loads((cfg.checkpoint_dir / "texture_threshold.json").read_text())
    hog = joblib.load(cfg.checkpoint_dir / "hog_lr.joblib")
    preds = {
        "texture_threshold": [
            texture_scores(small.images, texture["feature"]) >= texture["threshold"]
        ],
        "hog_lr": [
            hog["model"].predict_proba(hog_features(small.images))[:, 1] >= hog["threshold"]
        ],
    }
    data = load_split(split, cfg.input_size, *args, allow_test=True)
    device = pick_device()
    images = to_tensor(data.images, device)
    cnn = []
    for seed in cfg.seeds:
        model, mean, std, summary = load_checkpoint(
            cfg.checkpoint_dir / f"final_s{seed}.pt", device
        )
        cnn.append(predict(model, images, mean, std) >= summary["threshold"])
    preds["occupancy_cnn"] = cnn
    return preds, data.meta


def evaluate(cfg: OccupancyTrainConfig) -> dict:
    """Score all methods on all test splits, with cluster-bootstrap CIs by bay."""
    results: dict = {}
    pred_rows = []
    for split in TEST_SPLITS:
        preds, meta = _method_predictions(cfg, split)
        y = meta["label"].to_numpy()
        clusters = (meta["camera"] + "_" + meta["slot_id"].astype(str)).to_numpy()
        results[split] = {"crops": len(y), "bays": int(len(set(clusters))), "methods": {}}
        for method, ps in preds.items():
            per_seed = [binary_metrics(y, p) for p in ps]
            ci = cluster_bootstrap_ci(y, ps, clusters, cfg.bootstrap_samples)
            results[split]["methods"][method] = {
                m: {
                    "mean": float(np.mean([r[m] for r in per_seed])),
                    "std": float(np.std([r[m] for r in per_seed])),
                    "ci95": ci[m],
                }
                for m in METRICS
            }
            logger.bind(split=split, method=method).info(
                "F1 {:.4f}", results[split]["methods"][method]["f1"]["mean"]
            )
        frame = meta[["crop_id", "camera", "slot_id", "label"]].assign(split=split)
        for method, ps in preds.items():
            for i, p in enumerate(ps):
                frame[f"{method}_{i}" if len(ps) > 1 else method] = p.astype(int)
        pred_rows.append(frame)
    cfg.results_dir.mkdir(parents=True, exist_ok=True)
    pd.concat(pred_rows).to_csv(cfg.results_dir / "test_predictions.csv", index=False)
    (cfg.results_dir / "final_results.json").write_text(json.dumps(results, indent=2))
    _write_markdown(results, cfg)
    return results


def _write_markdown(results: dict, cfg: OccupancyTrainConfig) -> None:
    lines = [
        "# Occupancy: final comparison on the test splits",
        "",
        "Positive class = occupied. Thresholds and settings were chosen on validation only.",
        f"CNN = mean over seeds {cfg.seeds} (± std across seeds). "
        "Brackets = 95% bootstrap CI, resampling whole bays.",
        "",
    ]
    for split, r in results.items():
        lines += [
            f"## {split} ({r['crops']} crops, {r['bays']} bays)",
            "",
            "| Method | F1 | Recall | Precision | FPR | Accuracy |",
            "|---|---|---|---|---|---|",
        ]
        for method, ms in r["methods"].items():
            cells = []
            for m in METRICS:
                v = ms[m]
                sd = f" ± {v['std']:.4f}" if method == "occupancy_cnn" else ""
                cells.append(f"{v['mean']:.4f}{sd} [{v['ci95'][0]:.3f}, {v['ci95'][1]:.3f}]")
            lines.append(f"| {method} | " + " | ".join(cells) + " |")
        lines.append("")
    (cfg.results_dir / "final_results.md").write_text("\n".join(lines))


def main() -> None:
    """Train the final occupancy seeds and/or run the test comparison."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", action="store_true", help="train the final seeds")
    parser.add_argument("--evaluate", action="store_true", help="run the test comparison")
    args = parser.parse_args()
    cfg = load_config()
    setup_logging(cfg.logging)
    if args.train:
        train_final(cfg.occupancy)
    if args.evaluate:
        evaluate(cfg.occupancy)


if __name__ == "__main__":
    main()
