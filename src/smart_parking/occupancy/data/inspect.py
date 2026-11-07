"""Contact sheets for visual inspection of labelled crops."""

from pathlib import Path

import pandas as pd
from loguru import logger
from PIL import Image, ImageDraw

LABEL_COLOUR = {0: (40, 170, 70), 1: (215, 50, 50)}  # green = free, red = busy


def make_sheet(
    rows: pd.DataFrame, raw_root: Path, out_path: Path, cols: int = 10, tile: int = 72
) -> None:
    """Save a grid of crops; border colour shows the CSV label, text shows the crop id."""
    n = len(rows)
    if n == 0:
        logger.warning("No rows for sheet {}", out_path.name)
        return
    caption = 12
    n_rows = (n + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tile, n_rows * (tile + caption)), "white")
    draw = ImageDraw.Draw(sheet)
    for i, r in enumerate(rows.itertuples()):
        x, y = (i % cols) * tile, (i // cols) * (tile + caption)
        with Image.open(raw_root / r.path) as im:
            sheet.paste(im.convert("RGB").resize((tile - 6, tile - 6)), (x + 3, y + 3))
        draw.rectangle([x, y, x + tile - 1, y + tile - 1], outline=LABEL_COLOUR[r.label], width=3)
        draw.text((x + 2, y + tile), r.crop_id[:13], fill="black", font_size=9)
    sheet.save(out_path)
    logger.bind(stage="inspect").info("Wrote {} crops to {}", n, out_path)


def inspection_sheets(m: pd.DataFrame, raw_root: Path, out_dir: Path, seed: int) -> None:
    """Write the standard set of inspection sheets."""
    out_dir.mkdir(parents=True, exist_ok=True)
    overview = (
        m.groupby(["camera", "label"]).sample(5, random_state=seed).sort_values(["camera", "label"])
    )
    make_sheet(overview, raw_root, out_dir / "sheet_overview_by_camera.png")
    make_sheet(m[~m["label_agrees"]], raw_root, out_dir / "sheet_label_disagreements.png")
    dark = m[(m["brightness"] < 40) & (m["contrast"] > 0)]
    make_sheet(dark.sample(40, random_state=seed), raw_root, out_dir / "sheet_dark.png")
    low_busy = m[(m["label"] == 1) & (m["contrast"] < 8)]
    make_sheet(
        low_busy.sample(40, random_state=seed), raw_root, out_dir / "sheet_busy_low_contrast.png"
    )
    conflict = m[m["dhash"].duplicated(keep=False)]
    keys = conflict.groupby("dhash")["label"].nunique()
    conflict = conflict[conflict["dhash"].isin(keys[keys > 1].index)].sort_values("dhash")
    make_sheet(conflict, raw_root, out_dir / "sheet_hash_conflicts.png")
