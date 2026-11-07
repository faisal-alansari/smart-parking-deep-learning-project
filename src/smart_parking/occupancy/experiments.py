"""Training-choice experiments for the OccupancyCNN, judged on validation only.

Stages run in order. In each stage the current choice is kept unless another
option raises validation F1 by more than `min_val_gain`. The winner carries
forward to the next stage. All runs use seed 42; seeds vary only in the final runs.
"""

import json

from loguru import logger

from smart_parking.common.config import OccupancyTrainConfig, load_config
from smart_parking.common.log import setup_logging
from smart_parking.occupancy.train import train_run

STAGES: list[tuple[str, str, list[dict]]] = [
    ("learning_rate", "lr", [{"lr": 3e-4}, {"lr": 1e-3}, {"lr": 3e-3}]),
    (
        "augmentation",
        "augment",
        [{"augment": "none"}, {"augment": "photo"}, {"augment": "photo_hflip"}],
    ),
    (
        "regularization",
        "reg",
        [
            {"weight_decay": 0.0, "dropout": 0.0},
            {"weight_decay": 1e-4, "dropout": 0.3},
            {"weight_decay": 1e-3, "dropout": 0.5},
        ],
    ),
    ("input_size", "size", [{"input_size": 64}, {"input_size": 96}]),
]


def _label(option: dict) -> str:
    return "_".join(f"{k}-{v}" for k, v in option.items())


def run_experiments(base: OccupancyTrainConfig, seed: int) -> dict:
    """Run all stages and return the rows and the selected settings."""
    current = base.model_copy()
    rows, done = [], {}
    for stage, short, options in STAGES:
        results = []
        for option in options:
            cfg = current.model_copy(update=option)
            key = json.dumps(cfg.model_dump(mode="json"), sort_keys=True)
            if key not in done:
                done[key] = train_run(cfg, seed, f"exp_{short}_{_label(option)}")
            results.append((option, done[key]))
        incumbent = next(
            (o, s) for o, s in results if all(getattr(current, k) == v for k, v in o.items())
        )
        winner = incumbent
        for option, summary in results:
            if summary["val"]["f1"] > winner[1]["val"]["f1"] + (
                base.min_val_gain if winner is incumbent else 0.0
            ):
                winner = (option, summary)
        current = current.model_copy(update=winner[0])
        logger.bind(stage=stage).info(
            "Chosen {} (val F1 {:.4f})", winner[0], winner[1]["val"]["f1"]
        )
        for option, summary in results:
            rows.append(
                {
                    "stage": stage,
                    "option": _label(option),
                    "chosen": option == winner[0],
                    "run": summary["run"],
                    "best_epoch": summary["best_epoch"],
                    "train_seconds": summary["train_seconds"],
                    **{f"val_{k}": v for k, v in summary["val"].items()},
                }
            )
    selected = {
        k: getattr(current, k) for k in ("lr", "augment", "weight_decay", "dropout", "input_size")
    }
    return {"rows": rows, "selected": selected}


def write_report(result: dict, cfg: OccupancyTrainConfig) -> None:
    """Write the experiment table as JSON and Markdown."""
    cfg.results_dir.mkdir(parents=True, exist_ok=True)
    (cfg.results_dir / "experiments_val.json").write_text(json.dumps(result, indent=2))
    lines = [
        "# OccupancyCNN training-choice experiments (validation split, seed 42)",
        "",
        f"An option replaces the current choice only if val F1 rises by > {cfg.min_val_gain}.",
        "",
        "| Stage | Option | Val F1 | Recall | Precision | FPR | Accuracy | Best epoch "
        "| Seconds | Chosen |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in result["rows"]:
        lines.append(
            f"| {r['stage']} | {r['option']} | {r['val_f1']:.4f} | {r['val_recall']:.4f} | "
            f"{r['val_precision']:.4f} | {r['val_fpr']:.4f} | {r['val_accuracy']:.4f} | "
            f"{r['best_epoch']} | {r['train_seconds']} | {'yes' if r['chosen'] else ''} |"
        )
    lines += ["", f"Selected settings: `{result['selected']}`", ""]
    (cfg.results_dir / "experiments_val.md").write_text("\n".join(lines))


def main() -> None:
    cfg = load_config()
    setup_logging(cfg.logging)
    result = run_experiments(cfg.occupancy, cfg.seed)
    write_report(result, cfg.occupancy)
    logger.info("Experiments finished. Selected: {}", result["selected"])


if __name__ == "__main__":
    main()
