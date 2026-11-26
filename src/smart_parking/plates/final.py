"""Final YOLO11n runs (one per seed) and the one-time test comparison with the baseline.

`--train` trains the settings chosen by the validation experiments with every seed
(seed 42 reuses the identical experiment run). `--evaluate` is the only code path
that reads the test split.
"""

import argparse
import json
import shutil
import time
from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger
from ultralytics import YOLO

from smart_parking.common.config import PlateTrainConfig, load_config
from smart_parking.common.log import setup_logging
from smart_parking.plates.metrics import PLATE_METRICS, summarise
from smart_parking.plates.train import ground_truth, predict_boxes, score, train_run


def _selected(cfg: PlateTrainConfig) -> dict:
    return json.loads((cfg.results_dir / "experiments_val.json").read_text())["selected"]


def _final_cfg(cfg: PlateTrainConfig) -> PlateTrainConfig:
    sel = _selected(cfg)
    return cfg.model_copy(
        update={"imgsz": sel["imgsz"], "freeze": sel["freeze"], "train_size": sel["train_size"]}
    )


def train_final(cfg: PlateTrainConfig) -> None:
    """Train the selected settings once per seed."""
    final = _final_cfg(cfg)
    sel = _selected(cfg)
    for seed in cfg.seeds:
        name = f"final_s{seed}"
        if seed == 42:
            src = sel["seed42_run"]
            shutil.copy(cfg.checkpoint_dir / f"{src}.pt", cfg.checkpoint_dir / f"{name}.pt")
            dst = cfg.run_dir / name
            dst.mkdir(parents=True, exist_ok=True)
            summary = json.loads((cfg.run_dir / src / "summary.json").read_text())
            summary["copied_from"] = src
            (dst / "summary.json").write_text(json.dumps(summary, indent=2))
            logger.info("final_s42 reuses the identical experiment run {}", src)
        else:
            train_run(final, name, seed)


def _ci_over_seeds(rows_per_model: list[list[dict]], n_boot: int, seed: int = 0) -> dict:
    """95% CI of each metric averaged over models, resampling test images."""
    rng = np.random.default_rng(seed)
    n = len(rows_per_model[0])
    draws = {m: [] for m in PLATE_METRICS}
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        per = [summarise([rows[i] for i in idx]) for rows in rows_per_model]
        for m in PLATE_METRICS:
            draws[m].append(np.mean([p[m] for p in per]))
    return {
        m: (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))) for m, v in draws.items()
    }


def _evaluate_models(cfg: PlateTrainConfig, names: list[str], imgsz: int, truth: dict) -> dict:
    images = sorted((cfg.yolo_dir / "test" / "images").iterdir())
    rows_all, latency, detection = [], [], []
    for name in names:
        weights = cfg.checkpoint_dir / f"{name}.pt"
        summary = json.loads((cfg.run_dir / name / "summary.json").read_text())
        start = time.time()
        boxes = predict_boxes(weights, images, imgsz, cfg.device)
        latency.append(1000 * (time.time() - start) / len(images))
        rows_all.append(score(truth, boxes, summary["threshold"]))
        m = YOLO(str(weights)).val(
            data=str(cfg.yolo_dir / "data.yaml"),
            split="test",
            imgsz=imgsz,
            device=cfg.device,
            verbose=False,
            plots=False,
        )
        detection.append({"map50": float(m.box.map50), "map50_95": float(m.box.map)})
    per_model = [summarise(r) for r in rows_all]
    return {
        "models": names,
        "metrics": {
            k: {
                "mean": float(np.mean([p[k] for p in per_model])),
                "std": float(np.std([p[k] for p in per_model])),
            }
            for k in PLATE_METRICS
        },
        "ci95": _ci_over_seeds(rows_all, cfg.bootstrap_samples),
        "detection": {k: float(np.mean([d[k] for d in detection])) for k in ("map50", "map50_95")},
        "ms_per_image": float(np.mean(latency)),
        "rows": rows_all,
    }


def evaluate(cfg: PlateTrainConfig) -> dict:
    """Score the fine-tuned seeds and the from-scratch baseline on the test split."""
    final = _final_cfg(cfg)
    truth = ground_truth(cfg, "test", allow_test=True)
    ledger = pd.read_csv(cfg.ledger_csv).set_index("image")
    emirate = {Path(i).stem: f for i, f in ledger["family"].items()}
    tuned = _evaluate_models(cfg, [f"final_s{s}" for s in cfg.seeds], final.imgsz, truth)
    base = _evaluate_models(cfg, [_selected(cfg)["baseline_run"]], final.imgsz, truth)

    per_emirate = {}
    keys = list(truth)
    for fam in sorted({emirate[k] for k in keys}):
        idx = [i for i, k in enumerate(keys) if emirate[k] == fam]
        per_emirate[fam] = {
            "images": len(idx),
            "exact_match": float(
                np.mean([summarise([r[i] for i in idx])["exact_match"] for r in tuned["rows"]])
            ),
            "misread_rate": float(
                np.mean([summarise([r[i] for i in idx])["misread_rate"] for r in tuned["rows"]])
            ),
        }
    reads = pd.DataFrame(tuned["rows"][0]).assign(emirate=lambda d: d["image"].map(emirate))
    reads["truth_text"] = reads["image"].map(lambda k: truth[k].text)
    reads["truth_emirate"] = reads["image"].map(lambda k: truth[k].emirate)
    cfg.results_dir.mkdir(parents=True, exist_ok=True)
    reads.to_csv(cfg.results_dir / "test_reads_final_s42.csv", index=False)
    results = {
        "test_images": len(truth),
        "fine_tuned": {k: v for k, v in tuned.items() if k != "rows"},
        "from_scratch_baseline": {k: v for k, v in base.items() if k != "rows"},
        "per_emirate_fine_tuned": per_emirate,
        "settings": _selected(cfg),
    }
    (cfg.results_dir / "final_results.json").write_text(json.dumps(results, indent=2))
    _write_markdown(results, cfg)
    return results


def _write_markdown(results: dict, cfg: PlateTrainConfig) -> None:
    labels = {
        "exact_match": "Full-plate exact match",
        "coverage": "Coverage (answered)",
        "answered_accuracy": "Accuracy when answered",
        "misread_rate": "Misread rate",
        "plate_found": "Plate found",
        "emirate_accuracy": "Emirate correct",
        "cer": "Character error rate",
    }
    ft, bl = results["fine_tuned"], results["from_scratch_baseline"]
    lines = [
        "# Plate reading: final comparison on the test split",
        "",
        f"{results['test_images']} test images, one plate identity each. Thresholds chosen on "
        "validation. Fine-tuned = mean over seeds "
        f"{cfg.seeds} (± std). Brackets = 95% bootstrap CI over images. "
        "A review request counts as not correct.",
        "",
        "| Metric | Fine-tuned YOLO11n | From-scratch baseline |",
        "|---|---|---|",
    ]
    for k, label in labels.items():
        f, b = ft["metrics"][k], bl["metrics"][k]
        lines.append(
            f"| {label} | {f['mean']:.4f} ± {f['std']:.4f} [{ft['ci95'][k][0]:.3f}, "
            f"{ft['ci95'][k][1]:.3f}] | {b['mean']:.4f} [{bl['ci95'][k][0]:.3f}, "
            f"{bl['ci95'][k][1]:.3f}] |"
        )
    lines += [
        f"| Detection mAP50 | {ft['detection']['map50']:.4f} | {bl['detection']['map50']:.4f} |",
        f"| Detection mAP50-95 | {ft['detection']['map50_95']:.4f} | "
        f"{bl['detection']['map50_95']:.4f} |",
        f"| Milliseconds per image | {ft['ms_per_image']:.0f} | {bl['ms_per_image']:.0f} |",
        "",
        "## Fine-tuned model by emirate",
        "",
        "| Emirate | Test images | Exact match | Misread rate |",
        "|---|---|---|---|",
        *[
            f"| {fam} | {d['images']} | {d['exact_match']:.4f} | {d['misread_rate']:.4f} |"
            for fam, d in sorted(
                results["per_emirate_fine_tuned"].items(), key=lambda kv: -kv[1]["images"]
            )
        ],
        "",
    ]
    (cfg.results_dir / "final_results.md").write_text("\n".join(lines))


def main() -> None:
    """Train the final plate seeds and/or evaluate them."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", action="store_true")
    parser.add_argument("--evaluate", action="store_true")
    args = parser.parse_args()
    cfg = load_config()
    setup_logging(cfg.logging)
    if args.train:
        train_final(cfg.plates)
    if args.evaluate:
        evaluate(cfg.plates)


if __name__ == "__main__":
    main()
