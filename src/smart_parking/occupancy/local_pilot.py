"""Check the full loop on the owner's own photos of the two bays.

1. Occupancy: each bay is cropped with a hand-drawn box (configs/local_pilot.yaml),
   resized like the training crops and scored by the three final OccupancyCNN seeds
   (majority vote at their validation thresholds).
2. Plate: for each bay called occupied, the fine-tuned YOLO11n (final seed 42, its
   validation threshold) reads the plate inside that bay's area. Reading from the
   whole photo is also scored, as a comparison.

A check only: these photos are never used for training, model choice or
thresholds. The crop sheet shows plates, so it stays in data/ (not in Git).
"""

import argparse
import json
import math
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from loguru import logger
from PIL import Image, ImageDraw, ImageOps

from smart_parking.common.config import OccupancyTrainConfig, PlateTrainConfig, load_config
from smart_parking.common.log import setup_logging
from smart_parking.occupancy.train import load_checkpoint, pick_device, predict, to_tensor
from smart_parking.plates.reader import Box, PlateRead, fits_bay, read_plates
from smart_parking.plates.train import LOW_CONF

from ultralytics import YOLO  # isort: skip  (after plates.train, which sets YOLO_OFFLINE)

DEFAULT_CONFIG = Path("configs/local_pilot.yaml")
PLATE_SEED = 42
BAY_MARGIN = 0.1  # plate search area = bay box grown by 10% on each side


def prepare_photos(raw_dir: Path, photo_dir: Path) -> None:
    """Copy JPEGs and convert iPhone HEIC photos to JPEG (macOS `sips`)."""
    photo_dir.mkdir(parents=True, exist_ok=True)
    for src in sorted(raw_dir.iterdir()):
        out = photo_dir / f"{src.stem}.jpg"
        if out.exists():
            continue
        if src.suffix.lower() == ".heic":
            subprocess.run(
                ["sips", "-s", "format", "jpeg", str(src), "--out", str(out)],
                check=True,
                capture_output=True,
            )
        elif src.suffix.lower() in {".jpg", ".jpeg"}:
            shutil.copy(src, out)


def bay_box(pilot: dict, bay: str, info: dict) -> list[float]:
    """The bay's own box, else the set's shared box (one pair for all photos, like a
    fixed camera set up once)."""
    return info.get("box") or pilot["default_boxes"][bay]


def crop_bays(pilot: dict, size: int) -> tuple[np.ndarray, pd.DataFrame, list[Image.Image]]:
    """One crop per bay: the box cut from the full photo, resized to size x size."""
    crops, rows, previews = [], [], []
    for photo in pilot["photos"]:
        path = Path(pilot["photo_dir"]) / f"{photo['name']}.jpg"
        im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        w, h = im.size
        for bay, info in photo["bays"].items():
            x0, y0, x1, y1 = bay_box(pilot, bay, info)
            crop = im.crop((round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h)))
            previews.append(crop.resize((160, 160), Image.Resampling.BILINEAR))
            crops.append(np.asarray(crop.resize((size, size), Image.Resampling.BILINEAR)))
            plate = info.get("plate")
            rows.append(
                {
                    "photo": photo["name"],
                    "light": photo["light"],
                    "bay": bay,
                    "truth": int(info["occupied"]),
                    "true_plate": f"{plate['emirate']} {plate['text']}" if plate else "",
                }
            )
    return np.stack(crops), pd.DataFrame(rows), previews


def score(cfg: OccupancyTrainConfig, images: np.ndarray, rows: pd.DataFrame) -> pd.DataFrame:
    """Probability and decision of each final seed, plus the majority vote."""
    device = pick_device()
    x = to_tensor(images, device)
    out = rows.copy()
    votes = []
    for seed in cfg.seeds:
        model, mean, std, summary = load_checkpoint(
            cfg.checkpoint_dir / f"final_s{seed}.pt", device
        )
        prob = predict(model, x, mean, std)
        out[f"p_s{seed}"] = prob.astype(float).round(3)
        votes.append(prob >= summary["threshold"])
    out["pred"] = (np.mean(votes, axis=0) > 0.5).astype(int)
    out["correct"] = out["pred"] == out["truth"]
    return out


def _load_photo(pilot: dict, name: str) -> Image.Image:
    path = Path(pilot["photo_dir"]) / f"{name}.jpg"
    return ImageOps.exif_transpose(Image.open(path)).convert("RGB")


def _detect(model: YOLO, image: Image.Image, imgsz: int) -> list[Box]:
    """All detections above a low confidence, in the image's pixel frame."""
    res = model.predict(image, imgsz=imgsz, conf=LOW_CONF, verbose=False, max_det=100)[0]
    return [
        Box(res.names[int(c)], float(p), *map(float, b))
        for c, p, b in zip(
            res.boxes.cls.cpu().numpy(),
            res.boxes.conf.cpu().numpy(),
            res.boxes.xyxy.cpu().numpy(),
            strict=True,
        )
    ]


def search_area(bay_px: tuple[float, ...], w: int, h: int) -> tuple[int, int, int, int]:
    """Plate search area: the bay box in pixels, grown by BAY_MARGIN on each side."""
    mx, my = BAY_MARGIN * (bay_px[2] - bay_px[0]), BAY_MARGIN * (bay_px[3] - bay_px[1])
    return (
        max(0, round(bay_px[0] - mx)),
        max(0, round(bay_px[1] - my)),
        min(w, round(bay_px[2] + mx)),
        min(h, round(bay_px[3] + my)),
    )


def _pick(reads: list[PlateRead], box: tuple[float, float, float, float]) -> PlateRead | None:
    """The largest plate whose centre lies in the bay box.

    The car parked in the bay is the closest one, so its plate is the largest; plates of
    cars further back can also fall inside the box from a low camera.
    """
    x0, y0, x1, y1 = box
    inside = [
        r
        for r in reads
        if x0 <= (r.box[0] + r.box[2]) / 2 <= x1 and y0 <= (r.box[1] + r.box[3]) / 2 <= y1
    ]
    return max(inside, key=lambda r: r.box[2] - r.box[0], default=None)


def _check_size(read: PlateRead | None, bay_width: float) -> PlateRead | None:
    """A plate too small for the parked car goes to review (it belongs to a car behind)."""
    if read is None or fits_bay(read, bay_width):
        return read
    return read.model_copy(update={"decision": "NEEDS_REVIEW", "reason": "plate_too_small"})


def _outcome(read: PlateRead | None, truth: str, occupied: bool) -> str:
    if not occupied:  # the occupancy model called an empty bay occupied
        return "empty_bay_read" if read and read.decision == "READ" else "empty_bay_review"
    if read is None:
        return "no_plate_found" if truth else "correct_no_plate"
    if read.decision == "NEEDS_REVIEW":
        return "review" if truth else "correct_review_no_plate"
    if not truth:
        return "read_a_missing_plate"
    return "correct" if f"{read.emirate} {read.text}" == truth else "misread"


def read_bay_plates(pilot: dict, cfg: PlateTrainConfig, res: pd.DataFrame) -> pd.DataFrame:
    """Plate step for every bay the occupancy model called occupied.

    `bay` mode reads from the bay area (the product loop); `photo` mode reads the whole
    photo and keeps the plate whose centre falls in the bay (comparison only).
    """
    summary = json.loads((cfg.run_dir / f"final_s{PLATE_SEED}" / "summary.json").read_text())
    model = YOLO(str(cfg.checkpoint_dir / f"final_s{PLATE_SEED}.pt"))
    imgsz, threshold = summary["imgsz"], summary["threshold"]
    boxes = {
        (p["name"], bay): bay_box(pilot, bay, info)
        for p in pilot["photos"]
        for bay, info in p["bays"].items()
    }
    out = res.copy()
    cols = {k: [] for k in ("bay_read", "bay_decision", "bay_conf", "plate_width", "bay_outcome")}
    cols |= {k: [] for k in ("photo_read", "photo_outcome")}
    photo_reads: dict[str, list[PlateRead]] = {}
    for row in res.itertuples():
        if row.pred == 0:  # the loop only reads plates in bays called occupied
            for v in cols.values():
                v.append("")
            continue
        im = _load_photo(pilot, row.photo)
        w, h = im.size
        x0, y0, x1, y1 = boxes[(row.photo, row.bay)]
        bay_px = (x0 * w, y0 * h, x1 * w, y1 * h)
        area = search_area(bay_px, w, h)
        reads = read_plates(_detect(model, im.crop(area), imgsz), threshold)
        local = (
            bay_px[0] - area[0],
            bay_px[1] - area[1],
            bay_px[2] - area[0],
            bay_px[3] - area[1],
        )
        bay_read = _check_size(_pick(reads, local), bay_px[2] - bay_px[0])
        if row.photo not in photo_reads:
            photo_reads[row.photo] = read_plates(_detect(model, im, imgsz), threshold)
        photo_read = _check_size(_pick(photo_reads[row.photo], bay_px), bay_px[2] - bay_px[0])
        for prefix, read in (("bay", bay_read), ("photo", photo_read)):
            cols[f"{prefix}_read"].append(f"{read.emirate} {read.text}" if read else "none")
            cols[f"{prefix}_outcome"].append(_outcome(read, row.true_plate, bool(row.truth)))
        cols["bay_decision"].append(bay_read.decision if bay_read else "NEEDS_REVIEW")
        cols["bay_conf"].append(round(bay_read.confidence, 2) if bay_read else "")
        cols["plate_width"].append(  # plate width as a share of the bay width
            round((bay_read.box[2] - bay_read.box[0]) / (bay_px[2] - bay_px[0]), 2)
            if bay_read
            else ""
        )
        if bay_read and bay_read.reason:
            cols["bay_decision"][-1] += f" ({bay_read.reason})"
    for k, v in cols.items():
        out[k] = v
    out["loop_ok"] = [
        (not r.truth and not r.pred)
        or (
            r.truth
            and r.pred
            and r.bay_outcome in {"correct", "correct_no_plate", "correct_review_no_plate"}
        )
        for r in out.itertuples()
    ]
    return out


def summarise(res: pd.DataFrame) -> pd.DataFrame:
    """Accuracy, false alarms (empty called occupied) and missed cars, by light."""
    groups = [("all", res)] + [(k, g) for k, g in res.groupby("light", sort=False)]
    return pd.DataFrame(
        [
            {
                "light": name,
                "bays": len(g),
                "correct": int(g["correct"].sum()),
                "accuracy": round(float(g["correct"].mean()), 3),
                "false_alarms": f"{int(((g.pred == 1) & (g.truth == 0)).sum())}"
                f" of {int((g.truth == 0).sum())} empty",
                "missed_cars": f"{int(((g.pred == 0) & (g.truth == 1)).sum())}"
                f" of {int((g.truth == 1).sum())} occupied",
            }
            for name, g in groups
        ]
    )


def _md_table(df: pd.DataFrame) -> str:
    """Markdown table without extra dependencies."""
    lines = ["| " + " | ".join(df.columns) + " |", "|" + "---|" * len(df.columns)]
    lines += ["| " + " | ".join(str(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join(lines)


def save_sheet(previews: list[Image.Image], res: pd.DataFrame, path: Path) -> None:
    """Grid of bay crops with truth, prediction and mean probability."""
    sheet = Image.new("RGB", (160 * 4, 190 * math.ceil(len(previews) / 4)), "white")
    probs = res.filter(like="p_s").mean(axis=1)
    for i, (crop, row) in enumerate(zip(previews, res.itertuples(), strict=True)):
        x, y = (i % 4) * 160, (i // 4) * 190
        sheet.paste(crop, (x, y))
        d = ImageDraw.Draw(sheet)
        d.rectangle((x, y, x + 159, y + 159), outline="green" if row.correct else "red", width=4)
        truth = "occ" if row.truth else "empty"
        pred = "occ" if row.pred else "empty"
        d.text((x + 4, y + 162), f"{row.photo[-4:]} {row.bay} {row.light}", fill="black")
        d.text((x + 4, y + 175), f"true {truth} | pred {pred} p={probs[i]:.2f}", fill="black")
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path, quality=90)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="photo set YAML")
    args = parser.parse_args()
    name = args.config.stem
    project = load_config()
    setup_logging(project.logging)
    cfg = project.occupancy
    pilot = yaml.safe_load(args.config.read_text())
    prepare_photos(Path(pilot["raw_dir"]), Path(pilot["photo_dir"]))
    images, rows, previews = crop_bays(pilot, cfg.input_size)
    res = score(cfg, images, rows)
    res = read_bay_plates(pilot, project.plates, res)
    summary = summarise(res)
    out = cfg.results_dir / name
    out.mkdir(parents=True, exist_ok=True)
    res.to_csv(out / "predictions.csv", index=False)
    occ_cols = ["photo", "light", "bay", "truth", "p_s42", "p_s43", "p_s44", "pred", "correct"]
    plate_cols = ["photo", "light", "bay", "truth", "pred", "true_plate", "bay_read"]
    plate_cols += ["bay_decision", "bay_conf", "plate_width", "bay_outcome"]
    plate_cols += ["photo_read", "photo_outcome"]
    called = res[res["pred"] == 1]
    (out / "results.md").write_text(
        f"# Full loop: {pilot.get('title', name)}\n\n"
        f"{len(pilot['photos'])} photos, {len(res)} bays. Both models trained on public data "
        "only. Small sample: indicative only.\n\n"
        "## 1. Occupancy (majority vote of the 3 final CNN seeds)\n\n"
        + _md_table(summary)
        + "\n\n"
        + _md_table(res[occ_cols])
        + "\n\n## 2. Plate reading in bays called occupied "
        f"(YOLO11n final seed {PLATE_SEED})\n\n"
        "`bay` = read from the bay area (the product loop); `photo` = read from the whole "
        "photo (comparison). `plate_width` = plate width as a share of the bay width.\n\n"
        + _md_table(called[plate_cols])
        + "\n\n## 3. End to end\n\n"
        f"Bays fully right (occupancy right and, if occupied, the plate read right or a "
        f"missing plate sent to review): {int(res['loop_ok'].sum())} of {len(res)}.\n"
    )
    save_sheet(previews, res, Path("data/processed") / name / "crop_sheet.jpg")
    logger.info(
        "Occupancy {} of {} bays right; full loop {} of {}",
        int(res["correct"].sum()),
        len(res),
        int(res["loop_ok"].sum()),
        len(res),
    )


if __name__ == "__main__":
    main()
