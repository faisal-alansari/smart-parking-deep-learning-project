"""YOLO11n training-choice experiments, judged on validation only (seed 42).

Stages in order; an option replaces the current choice only if validation
full-plate exact match rises by more than `min_val_gain`:
1. image size: 640 vs 960
2. adaptation: full fine-tuning vs detection head only (freeze layers 0-22)
3. training-set size: 2,500 vs 5,000 (quality-vs-cost study)
Then the from-scratch baseline (random weights) is trained with the chosen settings.
"""

import json

from loguru import logger

from smart_parking.common.config import PlateTrainConfig, load_config
from smart_parking.common.log import setup_logging
from smart_parking.plates.train import train_run, val_detection_metrics

STAGES = [
    ("image_size", [{"imgsz": 640}, {"imgsz": 960}]),
    ("adaptation", [{"freeze": None}, {"freeze": 23}]),
    ("train_size", [{"train_size": 5000}, {"train_size": 2500}]),
]


def _name(cfg: PlateTrainConfig, pretrained: bool = True) -> str:
    freeze = "head" if cfg.freeze else "full"
    init = "" if pretrained else "_scratch"
    return f"exp_img{cfg.imgsz}_{freeze}_n{cfg.train_size}{init}"


def run_experiments(base: PlateTrainConfig, seed: int, report_only: bool = False) -> dict:
    """Run (or, with `report_only`, read back) every option and the from-scratch baseline."""
    current = base.model_copy()
    rows, done = [], {}

    def run(cfg: PlateTrainConfig, pretrained: bool = True) -> dict:
        name = _name(cfg, pretrained)
        saved = cfg.run_dir / name / "summary.json"
        if name not in done and saved.exists():  # finished in an earlier, interrupted run
            summary = json.loads(saved.read_text())
            if "val_detection" in summary:
                done[name] = summary
        if name not in done and report_only:
            raise SystemExit(f"{saved} is missing: run `just plate-experiments` to train it.")
        if name not in done:
            summary = train_run(cfg, name, seed, pretrained)
            summary["val_detection"] = val_detection_metrics(cfg.checkpoint_dir / f"{name}.pt", cfg)
            (cfg.run_dir / name / "summary.json").write_text(json.dumps(summary, indent=2))
            done[name] = summary
        return done[name]

    for stage, options in STAGES:
        results = [(o, run(current.model_copy(update=o))) for o in options]
        incumbent = results[0]
        winner = incumbent
        for option, summary in results[1:]:
            if (
                summary["val"]["exact_match"]
                > incumbent[1]["val"]["exact_match"] + base.min_val_gain
            ):
                winner = (option, summary)
        if stage != "train_size":  # size is a cost study; the full 5,000 is kept
            current = current.model_copy(update=winner[0])
        logger.bind(stage=stage).info("Chosen {}", winner[0])
        for option, s in results:
            rows.append({"stage": stage, "option": str(option), "chosen": option == winner[0], **s})
    baseline = run(current, pretrained=False)
    rows.append(
        {"stage": "baseline_from_scratch", "option": "random init", "chosen": False, **baseline}
    )
    selected = {
        "imgsz": current.imgsz,
        "freeze": current.freeze,
        "train_size": current.train_size,
        "seed42_run": _name(current),
        "baseline_run": _name(current, pretrained=False),
    }
    return {"rows": rows, "selected": selected}


def write_report(result: dict, cfg: PlateTrainConfig) -> None:
    """Write the validation experiment results as JSON and a Markdown table."""
    cfg.results_dir.mkdir(parents=True, exist_ok=True)
    (cfg.results_dir / "experiments_val.json").write_text(json.dumps(result, indent=2))
    lines = [
        "# YOLO11n training-choice experiments (validation split, seed 42)",
        "",
        "An option replaces the current choice only if val exact match rises by more than "
        f"{cfg.min_val_gain}.",
        "Exact match counts a review request as not correct.",
        "",
        "| Stage | Option | Exact match | Coverage | Answered acc. | Misread rate | CER "
        "| mAP50 | Conf | Epochs | Minutes | Chosen |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in result["rows"]:
        v, d = r["val"], r["val_detection"]
        lines.append(
            f"| {r['stage']} | {r['option']} | {v['exact_match']:.4f} | {v['coverage']:.4f} | "
            f"{v['answered_accuracy']:.4f} | {v['misread_rate']:.4f} | {v['cer']:.4f} | "
            f"{d['map50']:.4f} | {r['threshold']} | {r['epochs_run']} | "
            f"{r['train_seconds'] / 60:.0f} | {'yes' if r['chosen'] else ''} |"
        )
    lines += ["", f"Selected: `{result['selected']}`", ""]
    (cfg.results_dir / "experiments_val.md").write_text("\n".join(lines))


def main() -> None:
    """Train missing options (default) or rebuild the table from logged runs (`--report`)."""
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", action="store_true", help="read logged runs; never train")
    args = ap.parse_args()
    cfg = load_config()
    setup_logging(cfg.logging)
    result = run_experiments(cfg.plates, cfg.seed, report_only=args.report)
    write_report(result, cfg.plates)
    logger.info("Plate experiments finished. Selected: {}", result["selected"])


if __name__ == "__main__":
    main()
