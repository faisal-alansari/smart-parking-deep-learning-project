"""Audit the AddingUAE plate dataset (YOLO format).

Builds one table of every labelled box, assembles each plate's text from its
character boxes, and measures counts, class balance, duplicates and leakage
between the export's train / valid / test splits.
"""

import hashlib
import json
import re
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from loguru import logger
from PIL import Image

SPLITS = ("train", "valid", "test")
CHARS = set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
PLATE = "plate"
# File names like "K-67810" or "2-11596" carry the main plate's text (code-number).
PLATE_NAME = re.compile(r"^[A-Z0-9]{1,2}-\d{1,5}$")
FILE_SUFFIX = re.compile(r"_(png|jpeg|jpg|webp)$", re.IGNORECASE)
# A plate wider than this share of the image means a plate-only picture, not a car photo.
PLATE_ONLY_WIDTH = 0.5


def describe_images(boxes: pd.DataFrame, plates: pd.DataFrame) -> pd.DataFrame:
    """One row per image: name stem, whether the name is plate text, and image kind."""
    images = boxes[["split", "image", "source"]].drop_duplicates().reset_index(drop=True)
    images["stem"] = images["source"].str.replace(FILE_SUFFIX, "", regex=True)
    images["plate_named"] = images["stem"].str.match(PLATE_NAME)
    widest = boxes[boxes["cls"] == PLATE].groupby("image")["w"].max()
    images["max_plate_width"] = images["image"].map(widest).fillna(0.0)
    has_plate_box = images["max_plate_width"] > 0
    images["kind"] = np.select(
        [~has_plate_box, images["max_plate_width"] > PLATE_ONLY_WIDTH],
        ["plate_only_no_plate_box", "plate_closeup"],
        "car_photo",
    )
    main = (
        plates[plates["n_chars"] > 0]
        .assign(area=lambda d: d["plate_w_px"] * d["plate_h_px"])
        .sort_values("area")
        .groupby("image")
        .last()
    )
    family = main["plate_type"].str.replace(r"^(new|old)_", "", regex=True).str.lower()
    label_text = family + ":" + main["text"].str.replace("/", "", regex=False)
    images["label_identity"] = images["image"].map(label_text)
    # Plate identity used for splitting: the file name when it is plate text, else the
    # ordered label text, else the image itself (unknown identity).
    images["identity"] = np.where(
        images["plate_named"],
        "name:" + images["stem"],
        np.where(
            images["label_identity"].notna(),
            "label:" + images["label_identity"].fillna(""),
            "image:" + images["image"],
        ),
    )
    return images


def read_boxes(root: Path) -> tuple[pd.DataFrame, list[str]]:
    """All labelled boxes, one row each, with normalized centre/size coordinates."""
    names = yaml.safe_load((root / "data.yaml").read_text())["names"]
    rows = []
    for split in SPLITS:
        for img in sorted((root / split / "images").iterdir()):
            label = root / split / "labels" / f"{img.stem}.txt"
            base = {"split": split, "image": img.name, "source": img.name.split("_jpg.rf.")[0]}
            lines = label.read_text().split("\n") if label.exists() else []
            boxes = [ln.split() for ln in lines if ln.strip()]
            if not boxes:
                rows.append({**base, "cls": None})
            for b in boxes:
                cx, cy, w, h = map(float, b[1:5])
                rows.append({**base, "cls": names[int(b[0])], "cx": cx, "cy": cy, "w": w, "h": h})
    return pd.DataFrame(rows), names


def _order_characters(chars: pd.DataFrame) -> str:
    """Read characters in order: one row left to right, or top row then bottom row."""
    if chars.empty:
        return ""
    ys = np.sort(chars["cy"].to_numpy())
    gaps = np.diff(ys)
    if len(gaps) and gaps.max() > 0.6 * chars["h"].mean():
        cut = ys[int(gaps.argmax())]
        top = chars[chars["cy"] <= cut].sort_values("cx")
        bottom = chars[chars["cy"] > cut].sort_values("cx")
        return "".join(top["cls"]) + "/" + "".join(bottom["cls"])
    return "".join(chars.sort_values("cx")["cls"])


def assemble_plates(boxes: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """One row per plate box: emirate/type class, text, and character count.

    Characters and type boxes belong to the plate whose box contains their centre.
    Returns the plates and the number of character/type boxes that fit no plate.
    """
    plates, orphans = [], 0
    for (split, image, source), g in boxes.dropna(subset=["cls"]).groupby(
        ["split", "image", "source"]
    ):
        pboxes = g[g["cls"] == PLATE]
        others = g[g["cls"] != PLATE]
        owner = pd.Series(-1, index=others.index)
        for i, p in enumerate(pboxes.itertuples()):
            inside = ((others["cx"] - p.cx).abs() <= p.w / 2) & (
                (others["cy"] - p.cy).abs() <= p.h / 2
            )
            owner[inside & (owner == -1)] = i
        orphans += int((owner == -1).sum())
        for i, p in enumerate(pboxes.itertuples()):
            mine = others[owner == i]
            chars = mine[mine["cls"].isin(CHARS)]
            kinds = sorted(set(mine["cls"]) - CHARS)
            plates.append(
                {
                    "split": split,
                    "image": image,
                    "source": source,
                    "plate_type": "+".join(kinds) if kinds else "none",
                    "text": _order_characters(chars),
                    "n_chars": len(chars),
                    "plate_w_px": p.w * 1440,
                    "plate_h_px": p.h * 1280,
                    "char_h_px": float(chars["h"].median() * 1280) if len(chars) else np.nan,
                }
            )
    return pd.DataFrame(plates), orphans


def _hashes(path: Path) -> tuple[str, str]:
    data = path.read_bytes()
    with Image.open(path) as im:
        small = np.asarray(
            im.convert("L").resize((9, 8), Image.Resampling.BILINEAR), dtype=np.int16
        )
    bits = (small[:, 1:] > small[:, :-1]).flatten()
    return hashlib.md5(data).hexdigest(), f"{int(''.join('1' if b else '0' for b in bits), 2):016x}"


def image_hashes(root: Path, images: pd.DataFrame, workers: int) -> pd.DataFrame:
    """md5 and 64-bit difference hash for every image."""
    paths = [root / s / "images" / n for s, n in zip(images["split"], images["image"], strict=True)]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        out = list(pool.map(_hashes, paths, chunksize=100))
    return images.assign(md5=[o[0] for o in out], dhash=[o[1] for o in out])


def near_duplicate_pairs(images: pd.DataFrame, max_distance: int) -> pd.DataFrame:
    """All image pairs whose difference hashes differ by at most `max_distance` bits."""
    h = np.array([int(x, 16) for x in images["dhash"]], dtype=np.uint64)
    pairs = []
    for i in range(len(h)):
        d = np.bitwise_count(h[i + 1 :] ^ h[i])
        for j in np.flatnonzero(d <= max_distance):
            pairs.append((i, i + 1 + int(j), int(d[j])))
    a = images.iloc[[p[0] for p in pairs]].reset_index(drop=True)
    b = images.iloc[[p[1] for p in pairs]].reset_index(drop=True)
    return pd.DataFrame(
        {
            "image_a": a["image"],
            "split_a": a["split"],
            "image_b": b["image"],
            "split_b": b["split"],
            "distance": [p[2] for p in pairs],
        }
    )


def _multiset(text: str) -> str:
    return "".join(sorted(c for c in text if c in CHARS))


def match_filenames(plates: pd.DataFrame, images: pd.DataFrame) -> pd.DataFrame:
    """Compare each image's file name (the main plate's text) with its labelled characters.

    Status per image: "exact" (one plate has exactly the file-name characters),
    "partial" (best plate shares some characters), "no_chars" (no plate has characters).
    """
    out = []
    by_image = dict(tuple(plates.groupby("image")))
    for img in images.itertuples():
        target = _multiset(img.stem)
        ps = by_image.get(img.image)
        if ps is None or ps["n_chars"].sum() == 0:
            out.append({"image": img.image, "match": "no_chars", "best_text": ""})
            continue
        sets = [_multiset(t) for t in ps["text"]]
        if target in sets:
            out.append(
                {
                    "image": img.image,
                    "match": "exact",
                    "best_text": ps["text"].iloc[sets.index(target)],
                }
            )
            continue
        overlap = [len(set(s) & set(target)) for s in sets]
        out.append(
            {
                "image": img.image,
                "match": "partial",
                "best_text": ps["text"].iloc[int(np.argmax(overlap))],
            }
        )
    return images.merge(pd.DataFrame(out), on="image")


def summarise(boxes, plates, images, pairs, orphans) -> dict:
    """Counts behind the audit report."""
    per_split = {}
    for s in SPLITS:
        p = plates[plates["split"] == s]
        per_split[s] = {
            "images": int((images["split"] == s).sum()),
            "plate_boxes": len(p),
            "plates_with_characters": int((p["n_chars"] > 0).sum()),
        }
    ident = images[images["plate_named"]].groupby("stem")["split"].agg(["nunique", "size"])
    lab = images.groupby("identity")["split"].agg(["nunique", "size"])
    kind = images.set_index("image")["kind"]
    cross = pairs[pairs["split_a"] != pairs["split_b"]]
    car_cross = cross[
        (cross["image_a"].map(kind) == "car_photo") & (cross["image_b"].map(kind) == "car_photo")
    ]
    exact_md5 = images[images["md5"].duplicated(keep=False)]
    typed = plates[plates["plate_type"] != "none"]["plate_type"].str.split("+").str[0]
    return {
        "images": len(images),
        "boxes": len(boxes),
        "per_split": per_split,
        "class_counts": boxes["cls"].value_counts().to_dict(),
        "plate_types": typed.value_counts().to_dict(),
        "plates_without_type_box": int((plates["plate_type"] == "none").sum()),
        "plates_without_characters": int((plates["n_chars"] == 0).sum()),
        "boxes_outside_any_plate": orphans,
        "plates_per_image": plates.groupby("image").size().value_counts().sort_index().to_dict(),
        "plate_style_filenames": int(images["plate_named"].sum()),
        "filename_vs_labels_plate_named": images.loc[images["plate_named"], "match"]
        .value_counts()
        .to_dict(),
        "filename_vs_labels_other_names": images.loc[~images["plate_named"], "match"]
        .value_counts()
        .to_dict(),
        "image_kinds": images["kind"].value_counts().to_dict(),
        "image_kinds_per_split": pd.crosstab(images["kind"], images["split"]).to_dict(),
        "filename_identities": int(len(ident)),
        "filename_identities_with_several_images": int((ident["size"] > 1).sum()),
        "filename_identities_in_several_splits": int((ident["nunique"] > 1).sum()),
        "plate_identities": int(len(lab)),
        "plate_identities_with_several_images": int((lab["size"] > 1).sum()),
        "plate_identities_in_several_splits": int((lab["nunique"] > 1).sum()),
        "images_with_identity_in_several_splits": int(
            images["identity"].isin(lab[lab["nunique"] > 1].index).sum()
        ),
        "exact_duplicate_images": int(len(exact_md5)),
        "near_duplicate_pairs": len(pairs),
        "near_duplicate_pairs_across_splits": len(cross),
        "near_duplicate_car_photo_pairs_across_splits": len(car_cross),
        "char_height_px_quantiles": {
            str(q): round(float(plates["char_h_px"].quantile(q)), 1)
            for q in (0.05, 0.25, 0.5, 0.75, 0.95)
        },
    }


def write_markdown(summary: dict, path: Path) -> None:
    """Short human-readable audit report."""
    cc = summary["class_counts"]
    rare = {k: v for k, v in sorted(cc.items(), key=lambda kv: kv[1]) if v < 100}
    named = summary["filename_vs_labels_plate_named"]
    n_named = sum(named.values())
    lines = [
        "# AddingUAE plate data audit",
        "",
        f"Images: {summary['images']}. Boxes: {summary['boxes']}. "
        f"Exact duplicate images: {summary['exact_duplicate_images']}.",
        "",
        "| Split | Images | Plate boxes | Plates with characters |",
        "|---|---|---|---|",
        *[
            f"| {s} | {d['images']} | {d['plate_boxes']} | {d['plates_with_characters']} |"
            for s, d in summary["per_split"].items()
        ],
        "",
        "## Image kinds",
        "",
        "| Kind | Images |",
        "|---|---|",
        *[f"| {k} | {v} |" for k, v in summary["image_kinds"].items()],
        "",
        "## Label check against file names (file name = main plate text)",
        "",
        f"Plate-style file names: {n_named}. "
        + ", ".join(f"{k}: {v} ({v / n_named:.1%})" for k, v in named.items()),
        "",
        f"Character or type boxes outside any plate box: {summary['boxes_outside_any_plate']}. "
        f"Plate boxes without characters: {summary['plates_without_characters']}. "
        f"Plate boxes without an emirate/type box: {summary['plates_without_type_box']}.",
        "",
        "## Leakage between the export's splits",
        "",
        f"- Plate identities: {summary['plate_identities']}; with several images: "
        f"{summary['plate_identities_with_several_images']}; in several splits: "
        f"{summary['plate_identities_in_several_splits']} "
        f"({summary['images_with_identity_in_several_splits']} images).",
        f"- Near-duplicate image pairs: {summary['near_duplicate_pairs']}; across splits: "
        f"{summary['near_duplicate_pairs_across_splits']}; of which car photos: "
        f"{summary['near_duplicate_car_photo_pairs_across_splits']}.",
        "",
        "## Plate types (emirate and style)",
        "",
        "| Type | Plates |",
        "|---|---|",
        *[f"| {k} | {v} |" for k, v in summary["plate_types"].items()],
        "",
        f"Rare classes (< 100 boxes): {rare}",
        "",
        f"Character height in pixels (quantiles): {summary['char_height_px_quantiles']}",
        "",
    ]
    path.write_text("\n".join(lines))


def plate_crop_sheet(
    root: Path, boxes: pd.DataFrame, images: pd.DataFrame, out_path: Path, n: int, seed: int
) -> None:
    """Crops around each sampled image's plates with character boxes drawn.

    Caption: file-name text | assembled label text.
    """
    from PIL import ImageDraw

    sample = images.sample(min(n, len(images)), random_state=seed)
    tw, th, cols = 240, 120, 4
    rows = (len(sample) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 14)), "white")
    draw = ImageDraw.Draw(sheet)
    for k, img in enumerate(sample.itertuples()):
        g = boxes[(boxes["image"] == img.image) & (boxes["split"] == img.split)]
        plates = g[g["cls"] == PLATE]
        with Image.open(root / img.split / "images" / img.image) as im:
            im = im.convert("RGB")
            W, H = im.size
            d = ImageDraw.Draw(im)
            for b in g.itertuples():
                x0, y0 = (b.cx - b.w / 2) * W, (b.cy - b.h / 2) * H
                x1, y1 = (b.cx + b.w / 2) * W, (b.cy + b.h / 2) * H
                d.rectangle(
                    [x0, y0, x1, y1], outline=(0, 200, 0) if b.cls == PLATE else (255, 0, 0)
                )
            if len(plates):
                p = plates.loc[(plates["w"] * plates["h"]).idxmax()]
                m = 0.6
                box = (
                    max(0, (p.cx - p.w * (0.5 + m)) * W),
                    max(0, (p.cy - p.h * (0.5 + m)) * H),
                    min(W, (p.cx + p.w * (0.5 + m)) * W),
                    min(H, (p.cy + p.h * (0.5 + m)) * H),
                )
                im = im.crop(box)
            im.thumbnail((tw, th))
        x, y = (k % cols) * tw, (k // cols) * (th + 14)
        sheet.paste(im, (x, y))
        caption = f"{img.stem[:14]} | {img.best_text[:14]}"
        draw.text((x + 2, y + th), caption, fill="black", font_size=11)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)
    logger.bind(stage="plate_audit").info("Wrote {} crops to {}", len(sample), out_path)


def main() -> None:
    """Audit the raw plate data; write the boxes, plates, images, duplicates and report."""
    from smart_parking.common.config import load_config
    from smart_parking.common.log import setup_logging

    cfg = load_config()
    setup_logging(cfg.logging)
    pcfg = cfg.plate_data
    log = logger.bind(stage="plate_audit")
    boxes, _ = read_boxes(pcfg.raw_root)
    plates, orphans = assemble_plates(boxes)
    images = describe_images(boxes, plates)
    images = match_filenames(plates, images)
    images = image_hashes(pcfg.raw_root, images, pcfg.workers)
    pairs = near_duplicate_pairs(images, pcfg.near_duplicate_max_distance)
    log.info(
        "{} images, {} boxes, {} plates, {} near-duplicate pairs",
        len(images),
        len(boxes),
        len(plates),
        len(pairs),
    )

    pcfg.processed_dir.mkdir(parents=True, exist_ok=True)
    boxes.to_csv(pcfg.processed_dir / "boxes.csv", index=False)
    plates.to_csv(pcfg.processed_dir / "plates.csv", index=False)
    images.to_csv(pcfg.processed_dir / "images.csv", index=False)
    pairs.to_csv(pcfg.processed_dir / "near_duplicate_pairs.csv", index=False)

    summary = summarise(boxes, plates, images, pairs, orphans)
    pcfg.report_dir.mkdir(parents=True, exist_ok=True)
    (pcfg.report_dir / "audit_report.json").write_text(json.dumps(summary, indent=2))
    write_markdown(summary, pcfg.report_dir / "audit_report.md")
    named = images[images["plate_named"]]
    plate_crop_sheet(
        pcfg.raw_root,
        boxes,
        named[named["match"] == "exact"],
        pcfg.report_dir / "sheet_exact_matches.png",
        24,
        cfg.seed,
    )
    plate_crop_sheet(
        pcfg.raw_root,
        boxes,
        named[named["match"] == "partial"],
        pcfg.report_dir / "sheet_mismatches.png",
        24,
        cfg.seed,
    )
    plate_crop_sheet(
        pcfg.raw_root,
        boxes,
        images[images["match"] == "no_chars"],
        pcfg.report_dir / "sheet_no_characters.png",
        12,
        cfg.seed,
    )
    log.info("Audit written to {}", pcfg.report_dir)


if __name__ == "__main__":
    main()
