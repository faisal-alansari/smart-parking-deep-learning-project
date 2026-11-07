"""Near-copy removal and class balancing for the occupancy data."""

import pandas as pd
from loguru import logger


def _hamming(a: str, b: str) -> int:
    return (int(a, 16) ^ int(b, 16)).bit_count()


def mark_near_copies(m: pd.DataFrame, max_distance: int) -> pd.Series:
    """Flag crops that look the same as the last kept snapshot of the same bay.

    Snapshots of one bay are walked in time order. A crop is kept when its label
    changed or its image hash differs by more than `max_distance` bits.
    """
    near_copy = pd.Series(False, index=m.index)
    for _, g in m.sort_values("timestamp").groupby(["camera", "slot_id"], sort=False):
        last_hash, last_label = None, None
        for idx, h, y in zip(g.index, g["dhash"], g["label"], strict=True):
            if last_hash is not None and y == last_label and _hamming(h, last_hash) <= max_distance:
                near_copy[idx] = True
            else:
                last_hash, last_label = h, y
    logger.bind(stage="sample").info("Near-copies flagged: {}", int(near_copy.sum()))
    return near_copy


def _camera_quotas(sizes: pd.Series, total: int) -> dict[str, int]:
    """Share `total` crops as evenly as possible over cameras, capped by what each has."""
    take: dict[str, int] = {}
    remaining, open_cams = total, sorted(sizes.index)
    while open_cams:
        quota = remaining // len(open_cams)
        small = [c for c in open_cams if sizes[c] <= quota]
        if not small:
            extra = remaining - quota * len(open_cams)
            for i, c in enumerate(open_cams):
                take[c] = quota + (1 if i < extra else 0)
            break
        for c in small:
            take[c] = int(sizes[c])
            remaining -= int(sizes[c])
            open_cams.remove(c)
    return take


def balance_train(train: pd.DataFrame, target_per_class: int, seed: int) -> pd.Index:
    """Pick a class-balanced training set, spreading each class evenly over cameras."""
    per_class = min(target_per_class, int(train["label"].value_counts().min()))
    chosen = []
    for _, g in train.groupby("label"):
        for cam, n in _camera_quotas(g["camera"].value_counts(), per_class).items():
            chosen.append(g[g["camera"] == cam].sample(n, random_state=seed).index)
    idx = chosen[0].append(chosen[1:])
    logger.bind(stage="sample").info("Balanced train: {} crops ({} per class)", len(idx), per_class)
    return idx
