"""Load prepared occupancy crops into memory, with an on-disk cache.

Test splits can only be loaded with `allow_test=True`, which only the final
evaluation passes. Training, tuning and thresholds use train and val alone.
"""

from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger
from PIL import Image

TRAIN_VAL = ("train", "val")
TEST_SPLITS = ("test", "test_unseen_camera", "test_unseen_site")


@dataclass
class SplitData:
    """Images (N, H, W, 3) uint8, labels (N,) int64 and per-crop metadata."""

    images: np.ndarray
    labels: np.ndarray
    meta: pd.DataFrame


def _load_one(args: tuple[Path, int]) -> np.ndarray:
    path, size = args
    with Image.open(path) as im:
        im = im.convert("RGB").resize((size, size), Image.Resampling.BILINEAR)
        return np.asarray(im, dtype=np.uint8)


def load_split(
    split: str,
    size: int,
    dataset_csv: Path,
    raw_root: Path,
    cache_dir: Path,
    workers: int = 8,
    allow_test: bool = False,
) -> SplitData:
    """Return the used crops of one split, resized to `size` x `size`."""
    if split in TEST_SPLITS and not allow_test:
        raise PermissionError(f"Split '{split}' is reserved for the final evaluation")
    if split not in TRAIN_VAL + TEST_SPLITS:
        raise ValueError(f"Unknown split '{split}'")
    df = pd.read_csv(dataset_csv, dtype={"dhash": str})
    meta = df[(df["split"] == split) & df["use"]].reset_index(drop=True)
    cache = cache_dir / f"{split}_{size}.npz"
    if cache.exists():
        stored = np.load(cache, allow_pickle=False)
        if list(stored["crop_id"]) == meta["crop_id"].tolist():
            logger.bind(split=split).info("Loaded {} crops from cache", len(meta))
            return SplitData(stored["images"], meta["label"].to_numpy(np.int64), meta)
    cache_dir.mkdir(parents=True, exist_ok=True)
    jobs = [(raw_root / p, size) for p in meta["path"]]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        images = np.stack(list(pool.map(_load_one, jobs, chunksize=500)))
    np.savez(cache, images=images, crop_id=meta["crop_id"].to_numpy(str))
    logger.bind(split=split).info("Decoded {} crops at {}px and cached them", len(meta), size)
    return SplitData(images, meta["label"].to_numpy(np.int64), meta)
