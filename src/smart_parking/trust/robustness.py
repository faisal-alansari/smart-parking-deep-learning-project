"""Image robustness at increasing severity, for the risks of a night parking camera.

Stresses (4 levels each): darkness (the street light fails), blur (a dirty or fogged lens),
sensor noise (night grain), JPEG compression (a weak video link) and headlight glare (a bright
blob over the bays). Each is applied to the whole frame.

- Model A + the camera check: frames of night video 1 (a seen night, one every 4 s, moving periods
  left out). For each level: how often the camera check asks a person (graceful abstention),
  and Model A's balanced accuracy on the frames it still answers.
- Model B: 400 public plate test images under the same stresses: exact full-plate reads,
  wrong reads and coverage, with the product's confidence gate.
Command robustness (typos, missing pieces, ambiguity, off-topic, tricks) is in
outputs/commands/robustness.md. `just robustness-images`.
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402
from loguru import logger  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

from smart_parking.common.config import load_config  # noqa: E402
from smart_parking.common.log import setup_logging  # noqa: E402
from smart_parking.decision import gate_plate, occupancy_decision  # noqa: E402
from smart_parking.occupancy.adapt import VIDEO_SEEN, balanced, truth, video_files  # noqa: E402
from smart_parking.occupancy.train import predict, to_tensor  # noqa: E402
from smart_parking.trust.common import OUT, md, occupancy_models  # noqa: E402
from smart_parking.trust.ood import ViewGuard, _crops, sharpness, small_view  # noqa: E402

LEVELS = {
    "darkness (brightness x)": [1.0, 0.6, 0.35, 0.2, 0.1],
    "blur (radius px)": [0, 2, 4, 8, 16],
    "sensor noise (sd)": [0, 10, 20, 40, 80],
    "JPEG compression (quality)": [95, 40, 20, 10, 5],
    "headlight glare (strength)": [0.0, 0.25, 0.5, 0.75, 1.0],
}


def stress(im: Image.Image, kind: str, level: float, rng: np.random.Generator) -> Image.Image:
    """Apply one image stress (darkness, blur, noise, JPEG, headlight) at a level."""
    a = np.asarray(im).astype(np.float32)
    if kind.startswith("darkness"):
        return Image.fromarray(np.clip(a * level, 0, 255).astype(np.uint8))
    if kind.startswith("blur"):
        return im.filter(ImageFilter.GaussianBlur(level)) if level else im
    if kind.startswith("sensor"):
        return Image.fromarray(np.clip(a + rng.normal(0, level, a.shape), 0, 255).astype(np.uint8))
    if kind.startswith("JPEG"):
        import io

        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=int(level))
        return Image.open(buf).convert("RGB")
    if kind.startswith("headlight"):
        w, h = im.size
        glow = Image.new("L", im.size, 0)
        ImageDraw.Draw(glow).ellipse((0.25 * w, 0.42 * h, 0.75 * w, 0.62 * h), fill=255)
        glow = (
            np.asarray(glow.filter(ImageFilter.GaussianBlur(w / 12)), np.float32)[..., None] / 255
        )
        return Image.fromarray(np.clip(a + glow * level * 255, 0, 255).astype(np.uint8))
    raise ValueError(kind)


def _test_frames() -> tuple[list[tuple[float, Image.Image]], dict, dict]:
    from smart_parking.pipeline import in_any, video_frames

    cfg = yaml.safe_load(VIDEO_SEEN.read_text())
    f = video_files(cfg)[0]
    frames = [(t, im) for t, im in video_frames(Path(f["video"]), 4) if not in_any(t, f["moving"])]
    return frames, cfg, f


def occupancy_robustness() -> pd.DataFrame:
    """Model A and the camera check on night-1 frames at each stress level."""
    frames, cfg, f = _test_frames()
    boxes = cfg["boxes"]
    snap = next(im for t, im in frames if t >= 340)
    guard = ViewGuard(small_view(snap, boxes)[0], sharpness(snap), boxes)
    models, d = occupancy_models(), load_config().decision
    y = np.array([[truth(f["cars"], b, t) for b in boxes] for t, _ in frames])
    rng = np.random.default_rng(0)
    rows = []
    for kind, levels in LEVELS.items():
        for level in levels:
            ims = [stress(im, kind, level, rng) for _, im in frames]
            asked = np.array([guard.check(im) is not None for im in ims])
            crops = np.concatenate([_crops(im, boxes) for im in ims])
            x = to_tensor(crops, next(models[0][0].parameters()).device)
            probs = [predict(m, x, mean, std) for m, mean, std, _ in models]
            occ = occupancy_decision(probs, d)[1].reshape(len(ims), len(boxes))
            keep = ~asked
            rows.append({
                "stress": kind, "level": level, "frames": len(ims),
                "camera check asks a person": round(float(asked.mean()), 3),
                "Model A balanced acc. (answered)":
                    round(balanced(y[keep].ravel(), occ[keep].ravel()), 3) if keep.any() else "",
                "Model A balanced acc. (no camera check)":
                    round(balanced(y.ravel(), occ.ravel()), 3),
                "parked cars missed (answered)": int((y[keep] & ~occ[keep]).sum()),
                "empty called occupied (answered)": int((~y[keep].astype(bool) & occ[keep]).sum()),
            })  # fmt: skip
    return pd.DataFrame(rows)


def plate_robustness(n: int = 400) -> pd.DataFrame:
    """Model B on the first n public test images at each stress level."""
    from smart_parking.plates.metrics import score_image, summarise
    from smart_parking.plates.reader import Box, read_plates
    from smart_parking.plates.train import ground_truth
    from smart_parking.trust.common import PLATE_SEED

    cfg, d = load_config().plates, load_config().decision
    summary = json.loads((cfg.run_dir / f"final_s{PLATE_SEED}" / "summary.json").read_text())
    from ultralytics import YOLO

    model = YOLO(str(cfg.checkpoint_dir / f"final_s{PLATE_SEED}.pt"))
    truth_ = ground_truth(cfg, "test", allow_test=True)
    keys = sorted(truth_)[:n]
    images = {
        k: Image.open(cfg.yolo_dir / "test" / "images" / f"{k}.jpg").convert("RGB") for k in keys
    }
    rng = np.random.default_rng(0)
    rows = []
    for kind, levels in LEVELS.items():
        for level in levels:
            scored = []
            for k in keys:
                res = model.predict(stress(images[k], kind, level, rng), imgsz=summary["imgsz"],
                                    conf=0.05, verbose=False, device=cfg.device)[0]  # fmt: skip
                boxes = [Box(res.names[int(c)], float(p), *map(float, b)) for c, p, b in
                         zip(res.boxes.cls.cpu().numpy(), res.boxes.conf.cpu().numpy(),
                             res.boxes.xyxy.cpu().numpy(), strict=True)]  # fmt: skip
                reads = [gate_plate(r, d) for r in read_plates(boxes, summary["threshold"])]
                scored.append(score_image(truth_[k], reads))
            s = summarise(scored)
            rows.append({"stress": kind, "level": level, "images": len(keys),
                         "exact": round(s["exact_match"], 3),
                         "wrong reads": round(s["misread_rate"], 3),
                         "answered": round(s["coverage"], 3)})  # fmt: skip
    return pd.DataFrame(rows)


def run() -> None:
    """Run the robustness tests, plot them and write `robustness_images.md`."""
    a, b = occupancy_robustness(), plate_robustness()
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.4))
    for kind, g in a.groupby("stress", sort=False):
        x = np.arange(len(g))
        axes[0].plot(x, g["camera check asks a person"], "o-", label=kind)
        axes[1].plot(x, g["Model A balanced acc. (no camera check)"], "o-", label=kind)
    for kind, g in b.groupby("stress", sort=False):
        axes[2].plot(np.arange(len(g)), g["wrong reads"], "o-", label=kind)
    titles = ["Camera check asks a person", "Model A balanced accuracy (all frames)",
              "Model B wrong reads (with the gate)"]  # fmt: skip
    for ax, title in zip(axes, titles, strict=True):
        ax.set(title=title, xlabel="severity level (0 = none)", xticks=range(5))
        ax.title.set_fontsize(9)
    axes[0].legend(fontsize=6)
    fig.tight_layout()
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "figures" / "robustness_images.png", dpi=150)
    (OUT / "robustness_images.md").write_text(
        "# Image robustness (increasing severity)\n\n"
        + __doc__.split("\n\n", 1)[1].split("`just")[0].strip()
        + "\n\n## Model A and the camera check (the other night)\n\n"
        + md(a)
        + "\n\n## Model B (public plate test images)\n\n"
        + md(b)
        + "\n\n![Robustness](figures/robustness_images.png)\n"
    )
    logger.info("Image robustness -> {}", OUT / "robustness_images.md")


def main() -> None:
    """Set up logging and run the image robustness tests."""
    setup_logging(load_config().logging)
    run()


if __name__ == "__main__":
    main()
