"""Select the plate fine-tuning subset, split it without leakage, and write the ledger.

Rules (agreed 2026-11-07, see Memory.md):
- car photos only; labels must exactly match the file name (verified), except that
  visually checked RAK / UAQ car photos may join train only;
- the same plate identity or near-identical car photos never cross splits;
- all smaller-emirate plates and every image with X, Y or Z are included first,
  then Dubai fills the rest;
- every selected image is counted in the fine-tuning ledger;
- Umm Al Quwain and plates without an emirate box are left out (too few examples);
  the product sends them straight to human review.
"""

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from loguru import logger

from smart_parking.common.config import PlateDataConfig
from smart_parking.plates.classes import remap_table, target_names

RARE_CHARS = ("X", "Y", "Z")
# Dataset type-class spellings -> emirate names.
EMIRATE = {
    "DUBAI": "Dubai",
    "abudabi": "Abu Dhabi",
    "sharka": "Sharjah",
    "fujira": "Fujairah",
    "fujairah": "Fujairah",
    "RAK": "Ras Al Khaimah",
    "ajman": "Ajman",
    "am": "Umm Al Quwain",
    "none": "unknown",
}
SPLITS = ("train", "val", "test")


def main_family(plates: pd.DataFrame) -> pd.Series:
    """Emirate of each image's largest plate with characters (e.g. "Dubai", "Ras Al Khaimah")."""
    main = (
        plates[plates["n_chars"] > 0]
        .assign(area=lambda d: d["plate_w_px"] * d["plate_h_px"])
        .sort_values("area")
        .groupby("image")
        .last()
    )
    first = main["plate_type"].str.split("+").str[0]
    return first.str.replace(r"^(new|old)_", "", regex=True).map(EMIRATE).fillna("other")


def similarity_groups(images: pd.DataFrame, pairs: pd.DataFrame) -> pd.Series:
    """Group id per image: same plate identity, or near-identical car photos, share a group."""
    parent = {i: i for i in images["image"]}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        parent[find(a)] = find(b)

    for _, g in images.groupby("identity"):
        names = list(g["image"])
        for other in names[1:]:
            union(names[0], other)
    kind = images.set_index("image")["kind"]
    for a, b in zip(pairs["image_a"], pairs["image_b"], strict=True):
        if a in parent and b in parent and kind[a] == kind[b] == "car_photo":
            union(a, b)
    return images["image"].map(find)


def select_and_split(
    images: pd.DataFrame,
    extra_train: list[str],
    total: int,
    val_size: int,
    test_size: int,
    seed: int,
) -> pd.DataFrame:
    """Return the selected images with a `split` column.

    `images` holds verified candidates (with family, group, rare-character flag).
    `extra_train` are checked unverified images that may only go to train.
    """
    rng = np.random.default_rng(seed)
    pool = images[~images["image"].isin(extra_train)].copy()
    n_verified = total - len(extra_train)
    priority = (pool["family"] != "Dubai") | pool["has_rare_char"]
    must = pool[priority]
    rest = pool[~priority]
    if len(must) > n_verified:
        raise ValueError("Priority images alone exceed the requested total")
    fill = rest.iloc[rng.permutation(len(rest))[: n_verified - len(must)]]
    chosen = pd.concat([must, fill])

    # Per-family quotas for val and test, proportional to the family's share.
    shares = chosen["family"].value_counts()
    quotas = {}
    for name, size in (("val", val_size), ("test", test_size)):
        q = (shares * size / len(chosen)).round().astype(int)
        q[q.idxmax()] += size - q.sum()
        quotas[name] = q

    chosen["split"] = "train"
    groups = chosen.groupby("group")
    order = list(groups.groups)
    rng.shuffle(order)
    filled = {s: pd.Series(0, index=shares.index) for s in ("val", "test")}
    for gid in order:
        g = groups.get_group(gid)
        fam = g["family"].iloc[0]
        for s in ("test", "val"):
            if filled[s][fam] + len(g) <= quotas[s][fam]:
                chosen.loc[g.index, "split"] = s
                filled[s][fam] += len(g)
                break
    for s in ("val", "test"):
        n = int((chosen["split"] == s).sum())
        if n != (val_size if s == "val" else test_size):
            logger.bind(stage="plate_split").warning("{} has {} images (target not met)", s, n)

    extra = images[images["image"].isin(extra_train)].assign(split="train")
    return pd.concat([chosen, extra]).reset_index(drop=True)


def check_no_leakage(selected: pd.DataFrame) -> None:
    """Fail if a plate identity, similarity group or identical file crosses splits."""
    for col in ("identity", "group", "md5"):
        n = selected.groupby(col)["split"].nunique()
        if (n > 1).any():
            raise ValueError(f"{int((n > 1).sum())} values of '{col}' appear in several splits")
    logger.bind(stage="plate_split").info("Leakage checks passed")


def remap_label_text(text: str, table: dict[int, int]) -> str:
    """Rewrite a YOLO label file to training class ids, dropping removed classes."""
    out = []
    for line in text.split("\n"):
        parts = line.split()
        if parts and int(parts[0]) in table:
            out.append(" ".join([str(table[int(parts[0])]), *parts[1:]]))
    return "\n".join(out) + ("\n" if out else "")


def write_yolo_dataset(selected: pd.DataFrame, cfg: PlateDataConfig, names: list[str]) -> Path:
    """YOLO folder layout with symlinked images and remapped labels, plus data.yaml."""
    table = remap_table(names)
    root = cfg.processed_dir / "yolo"
    for split in SPLITS:
        for sub in ("images", "labels"):
            folder = root / split / sub
            folder.mkdir(parents=True, exist_ok=True)
            for old in folder.iterdir():
                old.unlink()
    for r in selected.itertuples():
        src_img = (cfg.raw_root / r.source_split / "images" / r.image).resolve()
        src_lbl = cfg.raw_root / r.source_split / "labels" / f"{Path(r.image).stem}.txt"
        os.symlink(src_img, root / r.split / "images" / r.image)
        (root / r.split / "labels" / src_lbl.name).write_text(
            remap_label_text(src_lbl.read_text(), table)
        )
    data = {
        "path": str(root.resolve()),
        "train": "train/images",
        "val": "val/images",
        "test": "test/images",
        "nc": len(target_names(names)),
        "names": target_names(names),
    }
    (root / "data.yaml").write_text(yaml.safe_dump(data, sort_keys=False))
    return root


def ledger_summary(selected: pd.DataFrame, cap: int) -> dict:
    """Counts per split and family, and the total against the fine-tuning cap."""
    return {
        "total_items": len(selected),
        "cap": cap,
        "remaining": cap - len(selected),
        "per_split": selected["split"].value_counts().reindex(SPLITS).to_dict(),
        "per_split_family": pd.crosstab(selected["family"], selected["split"])
        .reindex(columns=list(SPLITS), fill_value=0)
        .to_dict(orient="index"),
        "verified": int(selected["verified"].sum()),
        "unverified_checked_train_only": int((~selected["verified"]).sum()),
        "images_with_rare_chars": int(selected["has_rare_char"].sum()),
    }


def write_markdown(summary: dict, path: Path) -> None:
    """Write the fine-tuning ledger summary as Markdown."""
    lines = [
        "# Plate fine-tuning subset and ledger",
        "",
        f"Items used: **{summary['total_items']}** of the {summary['cap']} project cap "
        f"({summary['remaining']} left). Verified: {summary['verified']}; checked unverified "
        f"(train only): {summary['unverified_checked_train_only']}; images with X/Y/Z: "
        f"{summary['images_with_rare_chars']}.",
        "",
        "| Emirate | Train | Val | Test |",
        "|---|---|---|---|",
        *[
            f"| {fam} | {d['train']} | {d['val']} | {d['test']} |"
            for fam, d in sorted(
                summary["per_split_family"].items(), key=lambda kv: -kv[1]["train"]
            )
        ],
        f"| **Total** | {summary['per_split']['train']} | {summary['per_split']['val']} "
        f"| {summary['per_split']['test']} |",
        "",
    ]
    path.write_text("\n".join(lines))


def main() -> None:
    """Select and split the plate fine-tuning subset; write the YOLO dataset and ledger."""
    from smart_parking.common.config import load_config
    from smart_parking.common.log import setup_logging

    cfg = load_config()
    setup_logging(cfg.logging)
    pcfg = cfg.plate_data
    proc = pcfg.processed_dir
    images = pd.read_csv(proc / "images.csv")
    plates = pd.read_csv(proc / "plates.csv")
    boxes = pd.read_csv(proc / "boxes.csv")
    pairs = pd.read_csv(proc / "near_duplicate_pairs.csv")

    images = images.rename(columns={"split": "source_split"})
    images["family"] = images["image"].map(main_family(plates))
    images["group"] = similarity_groups(images, pairs)
    rare = boxes.loc[boxes["cls"].isin(RARE_CHARS), "image"].unique()
    images["has_rare_char"] = images["image"].isin(rare)
    images["verified"] = (
        (images["kind"] == "car_photo") & images["plate_named"] & (images["match"] == "exact")
    )
    review = yaml.safe_load(pcfg.manual_review_file.read_text())
    # Emirates routed straight to human review are not trained or tested on.
    allowed = ~images["family"].isin(pcfg.review_only_emirates)
    extra_ok = images["image"].isin(review.get("approved_train_only", [])) & allowed
    extra = list(images.loc[extra_ok, "image"])
    candidates = images[(images["verified"] & allowed) | extra_ok]

    selected = select_and_split(
        candidates, extra, pcfg.subset_total, pcfg.val_size, pcfg.test_size, cfg.seed
    )
    check_no_leakage(selected)
    names = yaml.safe_load((pcfg.raw_root / "data.yaml").read_text())["names"]
    root = write_yolo_dataset(selected, pcfg, names)
    cols = ["image", "split", "source_split", "family", "identity", "group", "verified"]
    pcfg.report_dir.mkdir(parents=True, exist_ok=True)
    selected[cols].sort_values(["split", "image"]).to_csv(
        pcfg.report_dir / "finetune_ledger.csv", index=False
    )
    summary = ledger_summary(selected, pcfg.finetune_cap)
    (pcfg.report_dir / "finetune_ledger.json").write_text(json.dumps(summary, indent=2))
    write_markdown(summary, pcfg.report_dir / "finetune_ledger.md")
    logger.info("YOLO dataset at {}: {}", root, summary["per_split"])


if __name__ == "__main__":
    main()
