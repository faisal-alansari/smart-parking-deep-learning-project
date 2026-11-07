"""Quality filtering and leakage-safe splits for the occupancy data."""

from pathlib import Path

import pandas as pd
from loguru import logger

SPLITS = ("train", "val", "test", "test_unseen_camera", "test_unseen_site")


def quality_flags(m: pd.DataFrame, dark_threshold: float) -> pd.Series:
    """Reason a crop is excluded from the main splits, or empty string if it is kept."""
    reason = pd.Series("", index=m.index)
    reason[m["brightness"] < dark_threshold] = "too_dark_to_verify"
    reason[~m["label_agrees"]] = "label_conflict"
    reason[m["contrast"] == 0] = "blank_image"
    return reason


def read_days(raw_root: Path, name: str) -> set[str]:
    """Read one of the official CNR-EXT day lists."""
    text = (raw_root / "splits" / "CNRPark-EXT" / f"{name}_days.txt").read_text()
    return {d.strip() for d in text.split() if d.strip()}


def assign_splits(
    m: pd.DataFrame,
    day_lists: dict[str, set[str]],
    unseen_cameras: list[str],
    unseen_site_sources: list[str],
) -> pd.Series:
    """Assign each crop to a split.

    Unseen-site sources and unseen cameras are held out completely. The remaining
    cameras are split by day with the official day lists, so no day is shared.
    """
    split = pd.Series("unassigned", index=m.index)
    for name, days in day_lists.items():
        split[m["date"].isin(days)] = name
    split[m["camera"].isin(unseen_cameras)] = "test_unseen_camera"
    split[m["source"].isin(unseen_site_sources)] = "test_unseen_site"
    left = int((split == "unassigned").sum())
    if left:
        raise ValueError(f"{left} crops have a day that is in no official day list")
    logger.bind(stage="split").info("Split sizes: {}", split.value_counts().to_dict())
    return split


def check_no_leakage(m: pd.DataFrame) -> None:
    """Fail if a day, held-out camera, or identical file is shared across splits."""
    main = m[m["split"].isin(["train", "val", "test"])]
    days = main.groupby("date")["split"].nunique()
    if (days > 1).any():
        raise ValueError(f"Days shared across splits: {list(days[days > 1].index)}")
    train_cams = set(m.loc[m["split"] == "train", "camera"])
    held = set(m.loc[m["split"].str.startswith("test_unseen"), "camera"])
    if train_cams & held:
        raise ValueError(f"Held-out cameras in train: {train_cams & held}")
    kept = m[m["split"] != "excluded"]
    md5 = kept.groupby("md5")["split"].nunique()
    if (md5 > 1).any():
        raise ValueError(f"{int((md5 > 1).sum())} identical files shared across splits")
    logger.bind(stage="split").info("Leakage checks passed")
