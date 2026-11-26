"""Evidence for the plate reader rules added on 2026-11-20 (see `plates.reader`).

1. Labels (train + val): how often real neighbouring characters overlap sideways, and
   whether Dubai plates always carry a code letter (the main plate, named in the file,
   and the other, smaller plates in the background).
2. Validation (final seed 42, its threshold): plate-read scores with the rules off,
   each rule alone, and the merge cut-off at 70%, 60%, 50% and 40%.

Validation only; the test split is never read here. Writes
`outputs/plates/rule_evidence.md`.
"""

import json
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import yaml

from smart_parking.common.config import PlateTrainConfig, load_config
from smart_parking.plates import reader
from smart_parking.plates.classes import CHARACTERS, PLATE
from smart_parking.plates.metrics import summarise
from smart_parking.plates.reader import Box, read_plates
from smart_parking.plates.train import IMAGE_H, IMAGE_W, ground_truth, predict_boxes, score

SEED = 42
CUTOFFS = [0.7, 0.6, 0.5, 0.4]
OFF = 9.9  # a side overlap share can never exceed 1, so this switches the merge rule off


@contextmanager
def rules(merge: float = OFF, code: bool = False):
    """Run the reader with a given merge cut-off and code-letter rule, then restore."""
    old = reader.DUPLICATE_SIDE_OVERLAP, reader.CODE_REQUIRED
    reader.DUPLICATE_SIDE_OVERLAP = merge
    reader.CODE_REQUIRED = {"Dubai"} if code else set()
    try:
        yield
    finally:
        reader.DUPLICATE_SIDE_OVERLAP, reader.CODE_REQUIRED = old


def _label_boxes(path: Path, names: list[str]) -> list[Box]:
    boxes = []
    for line in path.read_text().split("\n"):
        if line.strip():
            c, x, y, w, h = line.split()[:5]
            x, y, w, h = map(float, (x, y, w, h))
            boxes.append(Box(names[int(c)], 1.0, x - w / 2, y - h / 2, x + w / 2, y + h / 2))
    return boxes


def _same_box(a: tuple[float, ...] | None, b: tuple[float, ...]) -> bool:
    return a is not None and all(abs(x - y) < 1e-3 for x, y in zip(a, b, strict=True))


def label_evidence(cfg: PlateTrainConfig) -> dict:
    """Side overlap of same-row character pairs, and code letters on Dubai plates."""
    names = yaml.safe_load((cfg.yolo_dir / "data.yaml").read_text())["names"]
    names = names if isinstance(names, list) else [names[i] for i in sorted(names)]
    overlaps = []
    dubai = {"main": [0, 0], "other": [0, 0]}  # [plates, plates without a code letter]
    for split in ("train", "val"):
        with rules():
            main = {
                k: (r.box[0] / IMAGE_W, r.box[1] / IMAGE_H, r.box[2] / IMAGE_W, r.box[3] / IMAGE_H)
                for k, r in ground_truth(cfg, split).items()
            }
        for f in sorted((cfg.yolo_dir / split / "labels").glob("*.txt")):
            boxes = _label_boxes(f, names)
            for p in (b for b in boxes if b.name == PLATE):
                chars = [b for b in boxes if b.name in CHARACTERS and reader._inside(b, p)]
                for i, a in enumerate(chars):
                    for b in chars[i + 1 :]:
                        if abs(a.cy - b.cy) < 0.5 * (a.h + b.h) / 2:
                            inter = max(0.0, min(a.x1, b.x1) - max(a.x0, b.x0))
                            narrow = min(a.x1 - a.x0, b.x1 - b.x0)
                            overlaps.append(inter / narrow if narrow > 0 else 0.0)
            with rules():
                reads = read_plates(boxes, 0.5)
            for r in reads:
                if r.emirate == "Dubai" and r.text:
                    kind = dubai["main" if _same_box(main.get(f.stem), r.box) else "other"]
                    kind[0] += 1
                    kind[1] += not any(ch.isalpha() for ch in r.text)
    o = np.array(overlaps)
    return {
        "pairs": len(o),
        "over": {c: int((o > c).sum()) for c in CUTOFFS},
        "dubai": dubai,
    }


def validation_evidence(cfg: PlateTrainConfig) -> list[dict]:
    """Validation scores for each rule setting, on one set of detections."""
    summary = json.loads((cfg.run_dir / f"final_s{SEED}" / "summary.json").read_text())
    images = sorted((cfg.yolo_dir / "val" / "images").iterdir())
    boxes = predict_boxes(
        cfg.checkpoint_dir / f"final_s{SEED}.pt", images, summary["imgsz"], cfg.device
    )
    with rules():  # truth straight from the labels, no new rules
        truth = ground_truth(cfg, "val")
    settings = [("rules off (before)", OFF, False)]
    settings += [(f"merge only, cut-off {c:.0%}", c, False) for c in CUTOFFS]
    settings += [
        ("code-letter rule only", OFF, True),
        ("both rules, cut-off 50% (after)", 0.5, True),
    ]
    rows = []
    for name, merge, code in settings:
        with rules(merge, code):
            s = summarise(score(truth, boxes, summary["threshold"]))
        rows.append({"setting": name, **s})
    return rows


def write_report(labels: dict, val: list[dict], path: Path) -> None:
    """Write the label and validation evidence for the plate reader rules as Markdown."""
    over = " | ".join(f"> {c:.0%}: {n}" for c, n in labels["over"].items())
    lines = [
        "# Evidence for the plate reader rules",
        "",
        "Reproduce with `just plate-rule-evidence`. Validation only; test not used.",
        "",
        "## Labels (train + val)",
        "",
        f"- Same-row character pairs inside a plate: {labels['pairs']:,}.",
        f"- Pairs whose sideways overlap is more than a share of the narrower box: {over}.",
        "- Dubai main plates (the plate named in the file): "
        f"{labels['dubai']['main'][0]:,}; without a code letter: {labels['dubai']['main'][1]}.",
        f"- Other Dubai plates (smaller, in the background): {labels['dubai']['other'][0]:,}; "
        f"without a code letter: {labels['dubai']['other'][1]}. Many of these have only some "
        "characters labelled.",
        "",
        f"## Validation (final seed {SEED}, its threshold, same detections for every row)",
        "",
        "| setting | exact match | answered | accuracy when answered | misread |",
        "|---|---|---|---|---|",
    ]
    lines += [
        f"| {r['setting']} | {r['exact_match']:.3f} | {r['coverage']:.3f} | "
        f"{r['answered_accuracy']:.3f} | {r['misread_rate']:.3f} |"
        for r in val
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    """Gather the evidence for the plate reader rules and write `rule_evidence.md`."""
    cfg = load_config().plates
    write_report(
        label_evidence(cfg), validation_evidence(cfg), cfg.results_dir / "rule_evidence.md"
    )


if __name__ == "__main__":
    main()
