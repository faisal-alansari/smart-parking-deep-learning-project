"""Controlled probes on a local photo set, to find why the full loop fails.

Run after `local_pilot` on the same set: the same bays cropped differently
(background cut, floor only, sides trimmed, zoomed out) and rescored by the 3 final
CNN seeds. Indicative only: the probes look at the set they explain.

(The plate safety rules first tried here as a what-if are now part of the reader;
see `smart_parking.plates.reader`.)
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from PIL import Image, ImageOps

from smart_parking.common.config import load_config
from smart_parking.occupancy.local_pilot import _md_table, bay_box
from smart_parking.occupancy.train import load_checkpoint, pick_device, predict, to_tensor

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


def box_variants(pilot: dict) -> pd.DataFrame:
    """Occupancy result of each box variant over all bays."""
    cfg = load_config().occupancy
    device = pick_device()
    models = [load_checkpoint(cfg.checkpoint_dir / f"final_s{s}.pt", device) for s in cfg.seeds]
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
                votes = sum(
                    float(predict(m, x, mean, std)[0]) >= s["threshold"]
                    for m, mean, std, s in models
                )
                rows.append(
                    {"variant": name, "truth": int(info["occupied"]), "pred": int(votes >= 2)}
                )
    d = pd.DataFrame(rows)
    out = []
    for name in VARIANTS:
        g = d[d.variant == name]
        out.append(
            {
                "box": name,
                "correct": f"{int((g.pred == g.truth).sum())} of {len(g)}",
                "false_alarms": f"{int(((g.pred == 1) & (g.truth == 0)).sum())}"
                f" of {int((g.truth == 0).sum())}",
                "missed_cars": f"{int(((g.pred == 0) & (g.truth == 1)).sum())}"
                f" of {int((g.truth == 1).sum())}",
            }
        )
    return pd.DataFrame(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/local_night_1.yaml"))
    args = parser.parse_args()
    pilot = yaml.safe_load(args.config.read_text())
    out = load_config().occupancy.results_dir / args.config.stem
    (out / "probes.md").write_text(
        f"# Probes: {pilot.get('title', args.config.stem)}\n\n"
        "Indicative only: these probes explain the same photos they look at.\n\n"
        "## Occupancy: same bays, different box shapes\n\n" + _md_table(box_variants(pilot)) + "\n"
    )


if __name__ == "__main__":
    main()
