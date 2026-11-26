"""Controlled probes on a local photo set, to find why the full loop fails.

Run after `local_pilot` on the same set (it reads that run's `predictions.csv`):
- the same bays cropped differently (background cut, floor only, sides trimmed,
  zoomed out) and rescored by the 3 final CNN seeds;
- what goes with the false alarms on empty bays: a wheel stop in the box (marked by
  eye in the set's config as `wheel_stop`) and crop brightness;
- whether the 3 seeds agreeing makes an answer more likely to be right;
- for cars whose plate was misread or sent to review: the confidence of the letter
  boxes on the plate, kept or dropped by the reading threshold.

Indicative only: the probes look at the set they explain. No plate text is written.
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from PIL import Image, ImageOps

from smart_parking.common.config import load_config
from smart_parking.occupancy.local_pilot import (
    PLATE_SEED,
    _detect,
    _load_photo,
    _md_table,
    bay_box,
    search_area,
)
from smart_parking.occupancy.train import load_checkpoint, pick_device, predict, to_tensor
from smart_parking.plates.classes import PLATE

from ultralytics import YOLO  # isort: skip  (after local_pilot, which sets YOLO_OFFLINE)

VARIANTS = {
    "original": (0.0, 0.0, 0.0, 0.0),
    "background_cut": (0.0, 0.30, 0.0, 0.0),  # drop the top 30% (other rows, buildings)
    "floor_only": (0.0, 0.55, 0.0, 0.0),  # keep the lower 45%
    "sides_trimmed": (0.12, 0.0, 0.12, 0.0),  # drop 12% on each side (neighbours)
    "zoomed_out": (-0.10, -0.25, -0.10, -0.10),  # grow the box: more background
}


def _variant(box: list[float], cut: tuple[float, float, float, float]) -> tuple[float, ...]:
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    return (
        max(0.0, x0 + cut[0] * w),
        max(0.0, y0 + cut[1] * h),
        min(1.0, x1 - cut[2] * w),
        min(1.0, y1 - cut[3] * h),
    )


def bay_votes(pilot: dict) -> pd.DataFrame:
    """Per bay and box variant: each seed's vote, the majority, and crop brightness."""
    cfg = load_config().occupancy
    device = pick_device()
    models = [
        load_checkpoint(cfg.checkpoint_dir / f"{cfg.deploy}_s{s}.pt", device) for s in cfg.seeds
    ]
    rows = []
    for photo in pilot["photos"]:
        path = Path(pilot["photo_dir"]) / f"{photo['name']}.jpg"
        im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        w, h = im.size
        for bay, info in photo["bays"].items():
            for name, cut in VARIANTS.items():
                x0, y0, x1, y1 = _variant(bay_box(pilot, bay, info), cut)
                crop = im.crop((round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h)))
                small = np.asarray(crop.resize((cfg.input_size,) * 2, Image.Resampling.BILINEAR))
                x = to_tensor(small[None].copy(), device)
                votes = [
                    int(float(predict(m, x, mean, std)[0]) >= s["threshold"])
                    for m, mean, std, s in models
                ]
                rows.append(
                    {
                        "photo": photo["name"],
                        "bay": bay,
                        "variant": name,
                        "truth": int(info["occupied"]),
                        "wheel_stop": info.get("wheel_stop"),
                        "votes": sum(votes),
                        "pred": int(sum(votes) >= 2),
                        "brightness": float(small.mean()),
                    }
                )
    return pd.DataFrame(rows)


def _of(part: pd.Series, whole: pd.Series) -> str:
    return f"{int(part.sum())} of {int(whole.sum())}"


def box_variants(d: pd.DataFrame) -> pd.DataFrame:
    """Occupancy result of each box variant over all bays."""
    out = []
    for name in VARIANTS:
        g = d[d.variant == name]
        empty, occ = g.truth == 0, g.truth == 1
        out.append(
            {
                "box": name,
                "correct": _of(g.pred == g.truth, g.truth >= 0),
                "false_alarms": _of(empty & (g.pred == 1), empty),
                "missed_cars": _of(occ & (g.pred == 0), occ),
            }
        )
    return pd.DataFrame(out)


def wheel_stops(d: pd.DataFrame) -> pd.DataFrame:
    """False alarms on empty bays with and without a wheel stop in the box."""
    out = []
    for name in ("original", "background_cut"):
        g = d[(d.variant == name) & (d.truth == 0)]
        alarm, stop, no_stop = g.pred == 1, g.wheel_stop.eq(True), g.wheel_stop.eq(False)
        out.append(
            {
                "box": name,
                "false_alarms_with_wheel_stop": _of(alarm & stop, stop),
                "false_alarms_without": _of(alarm & no_stop, no_stop),
                "share_of_false_alarms_with_a_stop": _of(alarm & stop, alarm),
            }
        )
    return pd.DataFrame(out)


def brightness(d: pd.DataFrame) -> pd.DataFrame:
    """Mean brightness (0-255) of empty-bay crops: false alarms vs correct."""
    g = d[(d.variant == "original") & (d.truth == 0)]
    return pd.DataFrame(
        {
            "empty_bays": ["false alarm", "correct"],
            "n": [int((g.pred == 1).sum()), int((g.pred == 0).sum())],
            "mean_brightness": [
                round(g[g.pred == 1].brightness.mean()),
                round(g[g.pred == 0].brightness.mean()),
            ],
        }
    )


def seed_agreement(d: pd.DataFrame) -> pd.DataFrame:
    """How often the majority answer is right when the 3 seeds agree or split."""
    g = d[d.variant == "original"]
    unanimous = g.votes.isin([0, 3])
    right = g.pred == g.truth
    return pd.DataFrame(
        {
            "seeds": ["all 3 agree", "split 2-1"],
            "right": [_of(right & unanimous, unanimous), _of(right & ~unanimous, ~unanimous)],
        }
    )


def code_letters(pilot: dict, res: pd.DataFrame) -> pd.DataFrame:
    """Letter boxes on the plate of each car whose plate was misread or sent to review."""
    cfg = load_config().plates
    summary = json.loads((cfg.run_dir / f"final_s{PLATE_SEED}" / "summary.json").read_text())
    model = YOLO(str(cfg.checkpoint_dir / f"final_s{PLATE_SEED}.pt"))
    threshold = summary["threshold"]
    infos = {(p["name"], b): i for p in pilot["photos"] for b, i in p["bays"].items()}
    rows = []
    for r in res[res.truth.eq(1) & res.bay_outcome.isin(["misread", "review"])].itertuples():
        im = _load_photo(pilot, r.photo)
        w, h = im.size
        x0, y0, x1, y1 = bay_box(pilot, r.bay, infos[(r.photo, r.bay)])
        area = search_area((x0 * w, y0 * h, x1 * w, y1 * h), w, h)
        boxes = _detect(model, im.crop(area), summary["imgsz"])
        plates = [b for b in boxes if b.name == PLATE and b.conf >= threshold]
        if not plates:
            continue
        p = max(plates, key=lambda b: b.x1 - b.x0)
        letters = sorted(
            (b.conf for b in boxes if b.name.isalpha() and len(b.name) == 1 and _in(b, p)),
            reverse=True,
        )
        rows.append(
            {
                "photo": r.photo,
                "bay": r.bay,
                "outcome": r.bay_outcome,
                "decision": r.bay_decision,
                "letters_kept": ", ".join(f"{c:.2f}" for c in letters if c >= threshold) or "-",
                "letters_dropped": ", ".join(f"{c:.2f}" for c in letters if c < threshold) or "-",
            }
        )
    return pd.DataFrame(rows)


def _in(child, parent) -> bool:
    return parent.x0 <= child.cx <= parent.x1 and parent.y0 <= child.cy <= parent.y1


def main() -> None:
    """Write the occupancy and plate probe tables for a photo set to `probes.md`."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/local_night_1.yaml"))
    args = parser.parse_args()
    pilot = yaml.safe_load(args.config.read_text())
    out = load_config().occupancy.results_dir / args.config.stem
    res = pd.read_csv(out / "predictions.csv", keep_default_na=False)
    d = bay_votes(pilot)
    has_stops = d.wheel_stop.notna().any()
    parts = [
        f"# Probes: {pilot.get('title', args.config.stem)}\n\n"
        "Indicative only: these probes explain the same photos they look at.\n",
        "## Occupancy: same bays, different box shapes\n\n" + _md_table(box_variants(d)),
        "## Occupancy: false alarms and wheel stops\n\n"
        "Wheel stops were marked by eye on the empty bays (`wheel_stop` in the config).\n\n"
        + (_md_table(wheel_stops(d)) if has_stops else "Not marked for this set.\n"),
        "## Occupancy: brightness of empty bays\n\n" + _md_table(brightness(d)),
        "## Occupancy: do the 3 seeds agree?\n\n" + _md_table(seed_agreement(d)),
        "## Plates: letter boxes on misread or reviewed plates\n\n"
        "Confidence of each letter box the detector found on the plate (kept: at or above "
        "the reading threshold; dropped: below it, down to 0.05).\n\n"
        + _md_table(code_letters(pilot, res)),
    ]
    (out / "probes.md").write_text("\n".join(p.rstrip("\n") + "\n" for p in parts))


if __name__ == "__main__":
    main()
