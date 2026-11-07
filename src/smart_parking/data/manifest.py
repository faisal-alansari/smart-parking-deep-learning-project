"""Build a validated manifest of CNRPark+EXT crops with label cross-checks."""

import hashlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
from loguru import logger
from PIL import Image
from pydantic import BaseModel, ConfigDict

CSV_NAME = "CNRPark+EXT.csv"
EXT_DIR = "CNR-EXT-Patches-150x150"
PARK_DIR = "CNRPark-Patches-150x150"


class CropRecord(BaseModel):
    """One labelled parking-space crop."""

    model_config = ConfigDict(extra="forbid")

    crop_id: str
    path: str
    source: Literal["CNR-EXT", "CNRPark"]
    camera: str
    slot_id: int
    date: str
    timestamp: str
    hour: int
    weather: Literal["S", "O", "R"]
    label: Literal[0, 1]


def _local_path(image_url: str) -> str:
    """Map the CSV image_url to the path inside raw_root."""
    if image_url.startswith("CNRPark/"):
        return image_url.replace("CNRPark/", f"{PARK_DIR}/", 1)
    return image_url.replace("CNR-EXT/", f"{EXT_DIR}/", 1)


def _parse_csv(raw_root: Path) -> pd.DataFrame:
    """Read the official CSV and normalise its columns."""
    df = pd.read_csv(raw_root / CSV_NAME, dtype=str)
    source = df["image_url"].str.split("/").str[0]
    ts = pd.to_datetime(
        df["year"]
        + "-"
        + df["month"].str.zfill(2)
        + "-"
        + df["day"].str.zfill(2)
        + " "
        + df["hour"].str.zfill(2)
        + ":"
        + df["minute"].str.zfill(2)
    )
    out = pd.DataFrame(
        {
            "path": df["image_url"].map(_local_path),
            "source": source,
            "camera": source.map({"CNR-EXT": "C", "CNRPark": ""}) + df["camera"],
            "slot_id": df["slot_id"].astype(int),
            "date": ts.dt.strftime("%Y-%m-%d"),
            "timestamp": ts.dt.strftime("%Y-%m-%d %H:%M"),
            "hour": ts.dt.hour,
            "weather": df["weather"],
            "label": df["occupancy"].astype(int),
        }
    )
    out.insert(
        0,
        "crop_id",
        out["camera"] + "_" + out["slot_id"].astype(str) + "_" + ts.dt.strftime("%Y%m%d%H%M"),
    )
    return out


def _official_labels(raw_root: Path) -> dict[str, int]:
    """Labels from the dataset's own label files and folder names, keyed by local path."""
    labels: dict[str, int] = {}
    for line in (raw_root / EXT_DIR / "LABELS" / "all.txt").read_text().split("\n"):
        if line.strip():
            rel, y = line.split()
            labels[f"{EXT_DIR}/PATCHES/{rel}"] = int(y)
    for p in (raw_root / PARK_DIR).glob("*/*/*.jpg"):
        labels[str(p.relative_to(raw_root))] = 1 if p.parent.name == "busy" else 0
    return labels


def _image_stats(path: Path) -> tuple[str, str, int, int, float, float]:
    """Return md5, 64-bit difference hash, width, height, mean and std brightness."""
    data = path.read_bytes()
    md5 = hashlib.md5(data).hexdigest()
    with Image.open(path) as im:
        w, h = im.size
        gray = im.convert("L")
        arr = np.asarray(gray, dtype=np.float32)
        small = np.asarray(gray.resize((9, 8), Image.Resampling.BILINEAR), dtype=np.int16)
    bits = (small[:, 1:] > small[:, :-1]).flatten()
    dhash = f"{int(''.join('1' if b else '0' for b in bits), 2):016x}"
    return md5, dhash, w, h, float(arr.mean()), float(arr.std())


def _stats_or_none(path: Path) -> tuple | None:
    try:
        return _image_stats(path)
    except OSError:
        return None


def build_manifest(raw_root: Path, workers: int) -> pd.DataFrame:
    """Build the manifest: metadata, label cross-check and per-image statistics."""
    log = logger.bind(stage="manifest")
    df = _parse_csv(raw_root)
    log.info("Loaded {} rows from {}", len(df), CSV_NAME)

    if df["crop_id"].duplicated().any():
        raise ValueError("crop_id is not unique")
    df.apply(lambda r: CropRecord.model_validate(r.to_dict()), axis=1)
    log.info("All rows passed schema validation")

    official = _official_labels(raw_root)
    df["official_label"] = df["path"].map(official).astype("Int64")
    df["label_agrees"] = df["official_label"] == df["label"]
    log.info(
        "Label cross-check: {} agree, {} disagree, {} without official label",
        int(df["label_agrees"].sum()),
        int((df["official_label"].notna() & ~df["label_agrees"].fillna(False)).sum()),
        int(df["official_label"].isna().sum()),
    )

    paths = [raw_root / p for p in df["path"]]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        stats = list(pool.map(_stats_or_none, paths, chunksize=500))
    ok = [s is not None for s in stats]
    cols = ["md5", "dhash", "width", "height", "brightness", "contrast"]
    filled = [s if s is not None else (None,) * len(cols) for s in stats]
    df[cols] = pd.DataFrame(filled, index=df.index)
    df["readable"] = ok
    log.info("Image checks: {} readable, {} unreadable", sum(ok), len(ok) - sum(ok))
    return df
