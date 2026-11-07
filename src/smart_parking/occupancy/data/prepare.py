"""Prepare the occupancy dataset: manifest, inspection sheets, splits and sampling.

Run with `just prepare-data`. Outputs:
- data/processed/manifest.csv: every crop with metadata and image statistics
- data/processed/occupancy_dataset.csv: manifest plus split, use flag and drop reason
- outputs/data/data_report.json and data_report.md: counts for every stage
- outputs/data/sheet_*.png: contact sheets for visual inspection
"""

import argparse
import json
from pathlib import Path

import pandas as pd
from loguru import logger

from smart_parking.common.config import OccupancyDataConfig, load_config
from smart_parking.common.log import setup_logging
from smart_parking.common.seed import set_seed
from smart_parking.occupancy.data.inspect import inspection_sheets
from smart_parking.occupancy.data.manifest import build_manifest
from smart_parking.occupancy.data.sample import balance_train, mark_near_copies
from smart_parking.occupancy.data.split import (
    SPLITS,
    assign_splits,
    check_no_leakage,
    quality_flags,
    read_days,
)


def build_dataset(m: pd.DataFrame, cfg: OccupancyDataConfig, seed: int) -> pd.DataFrame:
    """Add split, use flag and drop reason to the manifest."""
    m = m.copy()
    day_lists = {name: read_days(cfg.raw_root, name) for name in ("train", "val", "test")}
    m["split"] = assign_splits(m, day_lists, cfg.unseen_cameras, cfg.unseen_site_sources)
    m["drop_reason"] = quality_flags(m, cfg.dark_threshold)
    m.loc[m["drop_reason"] != "", "split"] = "excluded"
    check_no_leakage(m)

    kept = m["split"] != "excluded"
    near = mark_near_copies(m[kept], cfg.near_copy_max_distance)
    m.loc[near[near].index, "drop_reason"] = "near_copy"

    pool = m[(m["split"] == "train") & (m["drop_reason"] == "")]
    chosen = balance_train(pool, cfg.train_target_per_class, seed)
    m.loc[pool.index.difference(chosen), "drop_reason"] = "not_sampled"
    m["use"] = m["drop_reason"] == ""
    return m


def summarise(m: pd.DataFrame) -> dict:
    """Counts behind the data report."""
    used = m[m["use"]]
    return {
        "total_crops": len(m),
        "drop_reasons": m["drop_reason"].replace("", "kept").value_counts().to_dict(),
        "used_per_split": {
            s: {
                "crops": int((used["split"] == s).sum()),
                "free": int(((used["split"] == s) & (used["label"] == 0)).sum()),
                "busy": int(((used["split"] == s) & (used["label"] == 1)).sum()),
                "cameras": sorted(used.loc[used["split"] == s, "camera"].unique().tolist()),
                "days": int(used.loc[used["split"] == s, "date"].nunique()),
            }
            for s in SPLITS
        },
        "train_crops_per_camera": used[used["split"] == "train"]
        .groupby(["camera", "label"])
        .size()
        .unstack()
        .to_dict(orient="index"),
        "fine_tuning_items_used": 0,
        "fine_tuning_note": "Occupancy model is trained from scratch; its data is outside the cap.",
    }


def write_markdown(summary: dict, path: Path) -> None:
    """Write a short human-readable data report."""
    lines = [
        "# Occupancy data report (CNRPark+EXT)",
        "",
        f"Total crops: {summary['total_crops']}",
        "",
        "| Status | Crops |",
        "|---|---|",
        *[f"| {k} | {v} |" for k, v in summary["drop_reasons"].items()],
        "",
        "| Split | Crops | Free | Busy | Free share | Cameras | Days |",
        "|---|---|---|---|---|---|---|",
    ]
    for s, d in summary["used_per_split"].items():
        share = d["free"] / d["crops"] if d["crops"] else 0
        cells = [
            s,
            d["crops"],
            d["free"],
            d["busy"],
            f"{share:.0%}",
            ", ".join(d["cameras"]),
            d["days"],
        ]
        lines.append("| " + " | ".join(str(c) for c in cells) + " |")
    lines += [
        "",
        f"Fine-tuning items used: {summary['fine_tuning_items_used']} "
        f"({summary['fine_tuning_note']})",
        "",
    ]
    path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare the occupancy dataset.")
    parser.add_argument("--config", type=Path, default=Path("configs/default.yaml"))
    args = parser.parse_args()

    cfg = load_config(args.config)
    setup_logging(cfg.logging)
    set_seed(cfg.seed)
    dcfg = cfg.occupancy_data
    dcfg.processed_dir.mkdir(parents=True, exist_ok=True)
    dcfg.report_dir.mkdir(parents=True, exist_ok=True)

    manifest = build_manifest(dcfg.raw_root, dcfg.workers)
    manifest.to_csv(dcfg.processed_dir / "manifest.csv", index=False)
    inspection_sheets(manifest, dcfg.raw_root, dcfg.report_dir, cfg.seed)

    dataset = build_dataset(manifest, dcfg, cfg.seed)
    dataset.to_csv(dcfg.processed_dir / "occupancy_dataset.csv", index=False)
    summary = summarise(dataset)
    (dcfg.report_dir / "data_report.json").write_text(json.dumps(summary, indent=2))
    write_markdown(summary, dcfg.report_dir / "data_report.md")
    logger.info("Data preparation finished: {}", summary["drop_reasons"])


if __name__ == "__main__":
    main()
