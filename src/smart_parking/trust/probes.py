"""Explainability as an investigation: controlled probes, each with a hypothesis.

Model A (bay crops of the other night, test; the adapted model against the public-only one):
- A1 where it looks: grey out the top, middle or bottom third of crops holding a car;
- A2 glare: add a headlight-like glow to empty bays;
- A3 half a car: grey out the left or right half of crops holding a car.
Model B (public plate test images with a clear, correct read):
- B1 cover the last character of the plate;
- B2 cover the left quarter of the plate (the emirate and code side).
Model C (minimal pairs of owner commands, made-up numbers).
System: the same parked car with and without a permit, and with a changed plate read.
`just probes`.
"""

import json

import numpy as np
import pandas as pd
from loguru import logger
from PIL import Image, ImageDraw, ImageFilter

from smart_parking.common.config import load_config
from smart_parking.common.log import setup_logging
from smart_parking.occupancy.train import load_checkpoint, pick_device, predict, to_tensor
from smart_parking.trust.common import OUT, PLATE_SEED, md, occupancy_models, occupancy_sets

GREY = 128


def _probs(models: list[tuple], images: np.ndarray) -> np.ndarray:
    x = to_tensor(images, next(models[0][0].parameters()).device)
    return np.mean([predict(m, x, mean, std) for m, mean, std, _ in models], axis=0)


def _mask(images: np.ndarray, region: str) -> np.ndarray:
    out = images.copy()
    h, w = out.shape[1:3]
    cut = {
        "top third": (slice(0, h // 3), slice(None)),
        "middle third": (slice(h // 3, 2 * h // 3), slice(None)),
        "bottom third": (slice(2 * h // 3, h), slice(None)),
        "left half": (slice(None), slice(0, w // 2)),
        "right half": (slice(None), slice(w // 2, w)),
    }[region]
    out[:, cut[0], cut[1]] = GREY
    return out


def _glare(images: np.ndarray, strength: float) -> np.ndarray:
    h, w = images.shape[1:3]
    glow = Image.new("L", (w, h), 0)
    ImageDraw.Draw(glow).ellipse((w * 0.2, h * 0.45, w * 0.8, h * 0.85), fill=255)
    g = np.asarray(glow.filter(ImageFilter.GaussianBlur(w / 8)), np.float32)[None, ..., None] / 255
    return np.clip(images + g * strength * 255, 0, 255).astype(np.uint8)


def model_a() -> pd.DataFrame:
    cfg, d = load_config().occupancy, load_config().decision
    images, meta = occupancy_sets()["test"]
    y = meta["label"].to_numpy()
    normal = (meta["slice"] == "normal").to_numpy()
    cars, empty = images[(y == 1) & normal], images[(y == 0) & normal]
    device = pick_device()
    variants = {
        "adapted (product)": (occupancy_models(), d.occupancy_threshold),
        "public only": (
            [load_checkpoint(cfg.checkpoint_dir / f"final_s{s}.pt", device) for s in cfg.seeds],
            0.5,
        ),
    }
    rows = []
    for name, (models, t) in variants.items():

        def share(imgs: np.ndarray, models: list = models, t: float = t) -> str:
            return f"{(_probs(models, imgs) >= t).mean():.0%}"

        rows += [
            {
                "probe": "A1 where it looks",
                "model": name,
                "input": "cars, unchanged",
                "called occupied": share(cars),
            },
            *[
                {
                    "probe": "A1 where it looks",
                    "model": name,
                    "input": f"cars, {r} greyed",
                    "called occupied": share(_mask(cars, r)),
                }
                for r in ("top third", "middle third", "bottom third")
            ],
            {
                "probe": "A2 glare",
                "model": name,
                "input": "empty bays, unchanged",
                "called occupied": share(empty),
            },
            *[
                {
                    "probe": "A2 glare",
                    "model": name,
                    "input": f"empty bays, glare {g}",
                    "called occupied": share(_glare(empty, g)),
                }
                for g in (0.3, 0.6, 0.9)
            ],
            *[
                {
                    "probe": "A3 half a car",
                    "model": name,
                    "input": f"cars, {r} greyed",
                    "called occupied": share(_mask(cars, r)),
                }
                for r in ("left half", "right half")
            ],
        ]
    return pd.DataFrame(rows)


def model_b(n: int = 300) -> pd.DataFrame:
    from ultralytics import YOLO

    from smart_parking.decision import gate_plate
    from smart_parking.plates.reader import Box, read_plates
    from smart_parking.plates.train import ground_truth

    cfg, d = load_config().plates, load_config().decision
    summary = json.loads((cfg.run_dir / f"final_s{PLATE_SEED}" / "summary.json").read_text())
    model = YOLO(str(cfg.checkpoint_dir / f"final_s{PLATE_SEED}.pt"))
    truth = ground_truth(cfg, "test", allow_test=True)

    def read(im: Image.Image, t) -> object:  # noqa: ANN001
        res = model.predict(
            im, imgsz=summary["imgsz"], conf=0.05, verbose=False, device=cfg.device
        )[0]
        boxes = [
            Box(res.names[int(c)], float(p), *map(float, b))
            for c, p, b in zip(
                res.boxes.cls.cpu().numpy(),
                res.boxes.conf.cpu().numpy(),
                res.boxes.xyxy.cpu().numpy(),
                strict=True,
            )
        ]
        reads = [gate_plate(r, d) for r in read_plates(boxes, summary["threshold"])]
        tx = (t.box[0] + t.box[2]) / 2
        near = [r for r in reads if r.box[0] <= tx <= r.box[2]]
        return max(near, key=lambda r: r.box[2] - r.box[0], default=None)

    counts = {
        k: {"still right": 0, "asks a person": 0, "silent misread": 0, "plate lost": 0}
        for k in ("B1 last character covered", "B2 left quarter covered")
    }
    used = 0
    for key in sorted(truth):
        if used >= n:
            break
        t = truth[key]
        im = Image.open(cfg.yolo_dir / "test" / "images" / f"{key}.jpg").convert("RGB")
        base = read(im, t)
        if base is None or base.decision != "READ" or base.text != t.text:
            continue  # probe only plates the reader gets right
        used += 1
        x0, y0, x1, y1 = t.box
        for probe, box in (
            ("B1 last character covered", (x1 - 0.16 * (x1 - x0), y0, x1, y1)),
            ("B2 left quarter covered", (x0, y0, x0 + 0.25 * (x1 - x0), y1)),
        ):
            covered = im.copy()
            ImageDraw.Draw(covered).rectangle(box, fill=(GREY, GREY, GREY))
            r = read(covered, t)
            outcome = (
                "plate lost"
                if r is None
                else "asks a person"
                if r.decision != "READ"
                else "still right"
                if r.text == t.text and r.emirate == t.emirate
                else "silent misread"
            )
            counts[probe][outcome] += 1
    rows = [
        {"probe": k, "plates": used, **{o: f"{v / used:.0%}" for o, v in c.items()}}
        for k, c in counts.items()
    ]
    return pd.DataFrame(rows)


PAIRS = [
    ("C1 the verb decides the action", ["allow car 52817 until 6 pm", "remove car 52817"]),
    ("C2 negation", ["remove car 52817", "don't allow car 52817 anymore"]),
    (
        "C3 spoken digits = written digits",
        ["allow car 52817 until tomorrow", "allow car five two eight one seven until tomorrow"],
    ),
    (
        "C4 a bay number is ignored",
        ["allow car 52817 until 6 pm", "allow car 52817 in bay 2 until 6 pm"],
    ),
    ("C5 AM/PM is never guessed", ["allow car 52817 until 6 pm", "allow car 52817 until 6"]),
    (
        "C6 a dropped day is asked about",
        [
            "allow car 52817 until tomorrow 9:30 pm",
            "allow car 52817 until tomorrow nine thirty p.m.",
        ],
    ),
    (
        "C7 no action word, no change",
        ["add car 52817 till tomorrow", "and car 52817 till tomorrow"],
    ),
]


def model_c() -> pd.DataFrame:
    from datetime import datetime
    from zoneinfo import ZoneInfo

    from smart_parking.commands.score import PARSERS

    decide = PARSERS["tiered"].load(load_config().commands).decide
    now = datetime(2026, 11, 25, 9, 30, tzinfo=ZoneInfo("Asia/Dubai"))
    rows = []
    for probe, texts in PAIRS:
        for text in texts:
            r = decide({"text": text}, now)
            shown = (
                f"{r.action.value} {r.number}" + (f" until {r.until:%a %H:%M}" if r.until else "")
                if hasattr(r, "action")
                else f"asks: {r.reason}"
                if hasattr(r, "reason")
                else "unsupported"
            )
            rows.append({"probe": probe, "command": text, "Model C": shown})
    return pd.DataFrame(rows)


def system() -> pd.DataFrame:
    from datetime import datetime
    from zoneinfo import ZoneInfo

    from smart_parking.commands.schema import Action, ParsedCommand, PermitTable
    from smart_parking.loop import bay_status
    from smart_parking.plates.reader import PlateRead

    at = datetime(2026, 11, 25, 21, 0, tzinfo=ZoneInfo("Asia/Dubai"))
    read = PlateRead(
        emirate="Dubai",
        text="G52817",
        confidence=0.9,
        decision="READ",
        reason=None,
        box=(0, 0, 1, 1),
    )
    with_permit = PermitTable()
    with_permit.apply(
        ParsedCommand(action=Action.ALLOW, number="52817", until=at.replace(hour=23)),
        confirm=lambda q: True,
    )
    cases = [
        ("occupied, plate G52817, no permit", True, read, PermitTable()),
        ("same, with a permit until 23:00", True, read, with_permit),
        (
            "same permit, plate read as G52617",
            True,
            read.model_copy(update={"text": "G52617"}),
            with_permit,
        ),
        (
            "same permit, plate unclear",
            True,
            read.model_copy(update={"decision": "NEEDS_REVIEW"}),
            with_permit,
        ),
        ("same permit, bay called empty", False, read, with_permit),
    ]
    return pd.DataFrame(
        [
            {"S1 the same car, one thing changed": name, "status": bay_status(occ, r, at, table)}
            for name, occ, r, table in cases
        ]
    )


def run() -> None:
    a, b, c, s = model_a(), model_b(), model_c(), system()
    (OUT / "probes.md").write_text(
        "# Explainability probes\n\n"
        + __doc__.split("\n\n", 1)[1].split("`just")[0].strip()
        + "\n\n## Model A\n\nHypotheses: A1, the model looks at the car itself (middle and "
        "bottom: body, bumper, plate) rather than the row of cars behind (top); A2, headlight "
        "glare on an empty bay looks like a car to the public-only model but not to the adapted "
        "one; A3, the adapted model needs most of a car, which would explain the bay holding half "
        "of a car standing across both bays.\n\n"
        + md(a)
        + "\n\n## Model B\n\nHypotheses: B1, with its last character hidden the reader should ask "
        "a person (too few characters), not read a different number; B2, with the emirate and "
        "code side hidden it should ask (no emirate, or a Dubai plate without its code).\n\n"
        + md(b)
        + "\n\n## Model C\n\n"
        + md(c)
        + "\n\n## System: does the decision really use the text and the table?\n\n"
        + md(s)
        + "\n"
    )
    logger.info("Probes -> {}", OUT / "probes.md")


def main() -> None:
    setup_logging(load_config().logging)
    run()


if __name__ == "__main__":
    main()
