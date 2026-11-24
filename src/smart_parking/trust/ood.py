"""Unfamiliar-input (OOD) detection for the fixed camera, and the abstention it triggers.

Model A is adapted to the owner's camera, so the product must notice frames that do not look
like it. Three tiers, cheapest first:
1. **blocked camera** (fixed rule): a nearly black or white frame;
2. **view check**: the background of the frame (everything outside the two bay boxes, small and
   grey) is compared with a snapshot taken when the camera was set up (Pearson correlation).
   Cars come and go inside the bays, but another car park, a moved camera, a blurred or noisy
   lens all change the background;
   **sharpness check**: the frame's sharpness against the snapshot's (a blurred lens);
3. **bay check** (evaluated, not used): the Mahalanobis distance of each bay crop's Model A
   features (the pooled last conv layer of the first deployed seed) from the training crops
   (night video 2, blocks 1-3).
Cut-offs come from block 4 (validation, in-distribution): the view check flags the lowest 1% of
its similarities, the bay check the highest 1% of its distances. Evaluated on frames of the other
night (in-distribution, test) against other car parks, a moved camera, a camera set up again
without a new snapshot, and corrupted frames. An unfamiliar frame returns NEEDS_REVIEW for both
bays with the reason (`camera_blocked`, `unfamiliar_view` or `blurred_view`): the product never
guesses on a view it does not know. `just ood`.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import torch
import yaml
from loguru import logger
from PIL import Image, ImageFilter, ImageOps
from sklearn.covariance import LedoitWolf
from sklearn.metrics import roc_auc_score

from smart_parking.common.config import load_config
from smart_parking.common.log import setup_logging
from smart_parking.occupancy.adapt import VIDEO_TEST, VIDEO_TRAIN, build_crops
from smart_parking.occupancy.train import to_tensor
from smart_parking.trust.common import OUT, md, occupancy_models

DETECTOR = Path("checkpoints/occupancy/ood_detector.npz")
REFERENCE = Path("checkpoints/occupancy/reference_view.npz")  # small grey view: no plates
VIEW = (54, 96)  # (width, height) of the small grey frame used by the view check
DARK, BRIGHT = 12, 243
EVERY = 10  # seconds between evaluation frames


# --- The three tiers -----------------------------------------------------------------------


def frame_check(image: Image.Image) -> str | None:
    """Tier 1: a blocked or blinded camera."""
    level = float(np.asarray(image.convert("L"), dtype=np.float32).mean())
    return "camera_blocked" if level < DARK or level > BRIGHT else None


def small_view(image: Image.Image, boxes: dict) -> tuple[np.ndarray, np.ndarray]:
    """The frame as a small grey array and a mask of the background (outside the bay boxes)."""
    grey = np.asarray(image.convert("L").resize(VIEW, Image.BILINEAR), dtype=np.float32)
    mask = np.ones_like(grey, dtype=bool)
    for x0, y0, x1, y1 in boxes.values():
        rows = slice(int(y0 * VIEW[1]), int(np.ceil(y1 * VIEW[1])))
        mask[rows, int(x0 * VIEW[0]) : int(np.ceil(x1 * VIEW[0]))] = False
    return grey, mask


def view_similarity(reference: np.ndarray, image: Image.Image, boxes: dict) -> float:
    """Tier 2: correlation of the background with the set-up snapshot."""
    grey, mask = small_view(image, boxes)
    a, b = grey[mask], reference[mask]
    return float(np.corrcoef(a, b)[0, 1]) if a.std() > 1e-3 else 0.0


def sharpness(image: Image.Image) -> float:
    """Tier 2b: variance of the Laplacian of a mid-size grey frame (low = blurred lens). The
    frame is first scaled to zero mean and unit spread, so a darker scene is not taken for blur
    (the first version, without this, flagged every frame 40% darker than usual)."""
    g = np.asarray(image.convert("L").resize((270, 480), Image.BILINEAR), dtype=np.float32)
    g = (g - g.mean()) / max(float(g.std()), 1e-3)
    lap = g[1:-1, 1:-1] * 4 - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]
    return float(lap.var())


@torch.no_grad()
def features(model, mean: torch.Tensor, std: torch.Tensor, images: np.ndarray) -> np.ndarray:  # noqa: ANN001
    """Pooled last-conv features of Model A for uint8 crops (N, H, W, 3)."""
    model.eval()
    out = []
    for i in range(0, len(images), 512):
        x = (to_tensor(images[i : i + 512], mean.device).float() / 255 - mean) / std
        out.append(
            torch.nn.functional.adaptive_avg_pool2d(model.features(x), 1).flatten(1).cpu().numpy()
        )
    return np.concatenate(out)


def bay_distance(det: dict, f: np.ndarray) -> np.ndarray:
    """Tier 3: Mahalanobis distance of bay-crop features from the training crops."""
    d = f - det["center"]
    return np.sqrt(np.einsum("ij,jk,ik->i", d, det["precision"], d))


class ViewGuard:
    """The product's camera check (tiers 1-2): blocked, unfamiliar or blurred view."""

    def __init__(self, view: np.ndarray, sharp: float, boxes: dict) -> None:
        det = np.load(DETECTOR)
        self.view, self.sharp, self.boxes = view, sharp, boxes
        self.sim_cut, self.sharp_cut = (
            float(det["similarity_cutoff"]),
            float(det["sharpness_cutoff"]),
        )

    @classmethod
    def owner_camera(cls) -> ViewGuard:
        """The owner's camera as set up on night 2 (default boxes and snapshot)."""
        ref = np.load(REFERENCE)
        boxes = {k[4:]: list(map(float, ref[k])) for k in ref.files if k.startswith("box_")}
        return cls(ref["view"], float(ref["sharpness"]), boxes)

    @classmethod
    def from_snapshot(cls, image: Image.Image, boxes: dict) -> ViewGuard:
        """A camera set up now: this frame is its snapshot."""
        return cls(small_view(image, boxes)[0], sharpness(image), boxes)

    def check(self, image: Image.Image) -> str | None:
        """None if the frame looks like this camera, else the reason to ask a person."""
        if reason := frame_check(image):
            return reason
        if view_similarity(self.view, image, self.boxes) < self.sim_cut:
            return "unfamiliar_view"
        if sharpness(image) / self.sharp < self.sharp_cut:
            return "blurred_view"
        return None


# --- Evaluation ----------------------------------------------------------------------------


def _frames(config: Path, split: str | None, every: int) -> list[Image.Image]:
    from smart_parking.occupancy.adapt import video_files
    from smart_parking.pipeline import video_frames

    cfg = yaml.safe_load(config.read_text())
    out = []
    for f in video_files(cfg):
        if split is None or f["split"] == split:
            out += [im for _, im in video_frames(Path(f["video"]), every)]
    return out


def _frame_at(video: str, seconds: float) -> Image.Image:
    from smart_parking.pipeline import video_frames

    return next(im for t, im in video_frames(Path(video), seconds) if t >= seconds)


def _corrupt(im: Image.Image, kind: str, rng: np.random.Generator) -> Image.Image:
    a = np.asarray(im).astype(np.float32)
    if kind == "heavy blur":
        return im.filter(ImageFilter.GaussianBlur(12))
    if kind == "over-exposed (x3)":
        return Image.fromarray(np.clip(a * 3, 0, 255).astype(np.uint8))
    if kind == "lens almost covered":
        return Image.fromarray((a * 0.04).astype(np.uint8))
    if kind == "pure noise":
        return Image.fromarray(rng.integers(0, 255, a.shape, dtype=np.uint8))
    if kind == "camera moved (shifted and zoomed)":
        w, h = im.size
        return im.crop((int(0.12 * w), int(0.06 * h), w, h)).resize((w, h))
    raise ValueError(kind)


def _crops(im: Image.Image, boxes: dict) -> np.ndarray:
    w, h = im.size
    out = []
    for x0, y0, x1, y1 in boxes.values():
        crop = im.crop((round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h)))
        out.append(np.asarray(crop.resize((64, 64), Image.BILINEAR)))
    return np.stack(out)


def run() -> None:
    cfg2, cfg1 = yaml.safe_load(VIDEO_TRAIN.read_text()), yaml.safe_load(VIDEO_TEST.read_text())
    model, mean, std, _ = occupancy_models()[0]
    parts = (model, mean, std)
    images, meta = build_crops(VIDEO_TRAIN, 64)
    lw = LedoitWolf().fit(features(*parts, images[(meta["split"] == "train").to_numpy()]))
    det = {"center": lw.location_, "precision": lw.precision_}
    # Set-up snapshots: an empty-bay frame of each installation (night 2: block 4 at 1:30;
    # night 1: 5:40, the same frame as the alignment guide)
    block4 = next(f["video"] for f in cfg2["files"] if f["split"] == "validation")
    snap2, snap1 = _frame_at(block4, 90), _frame_at(cfg1["video"], 340)
    ref2, ref1 = small_view(snap2, cfg2["boxes"])[0], small_view(snap1, cfg1["boxes"])[0]
    sharp = {id(ref2): sharpness(snap2), id(ref1): sharpness(snap1)}
    val = _frames(VIDEO_TRAIN, "validation", EVERY)

    def scores(frames: list[Image.Image], ref: np.ndarray, boxes: dict) -> pd.DataFrame:
        rows = []
        for im in frames:
            d = bay_distance(det, features(*parts, _crops(im, boxes))).max()
            rows.append({"blocked": frame_check(im) is not None,
                         "similarity": view_similarity(ref, im, boxes),
                         "sharpness": sharpness(im) / sharp[id(ref)],
                         "distance": float(d)})  # fmt: skip
        return pd.DataFrame(rows)

    v = scores(val, ref2, cfg2["boxes"])
    sim_cut, dist_cut = float(np.percentile(v.similarity, 1)), float(np.percentile(v.distance, 99))
    sharp_cut = float(np.percentile(v.sharpness, 1))
    np.savez(DETECTOR, center=det["center"], precision=det["precision"], distance_cutoff=dist_cut,
             similarity_cutoff=sim_cut, sharpness_cutoff=sharp_cut)  # fmt: skip
    np.savez(
        REFERENCE,
        view=ref2,
        sharpness=sharp[id(ref2)],
        **{f"box_{k}": np.array(b) for k, b in cfg2["boxes"].items()},
    )
    test = _frames(VIDEO_TEST, None, EVERY)
    rng = np.random.default_rng(0)
    in_test = scores(test, ref1, cfg1["boxes"])
    groups = {
        "in: night 2, block 4 (validation)": v,
        "in: night 1 (test, its own snapshot)": in_test,
    }
    photos = []
    for config in ("configs/local_night_1.yaml", "configs/local_pilot.yaml"):
        pilot = yaml.safe_load(Path(config).read_text())
        for p in pilot["photos"]:
            im = Image.open(Path(pilot["photo_dir"]) / f"{p['name']}.jpg")
            photos.append(ImageOps.exif_transpose(im).convert("RGB"))
    groups["out: other car parks (51 photos)"] = scores(photos, ref2, cfg2["boxes"])
    groups["out: camera set up again, old snapshot (night 2 vs night 1)"] = scores(
        val[::3], ref1, cfg1["boxes"]
    )
    for kind in ("camera moved (shifted and zoomed)", "heavy blur", "over-exposed (x3)",
                 "lens almost covered", "pure noise"):  # fmt: skip
        groups[f"out: night 1, {kind}"] = scores(
            [_corrupt(im, kind, rng) for im in test], ref1, cfg1["boxes"]
        )
    base = groups["in: night 1 (test, its own snapshot)"]
    rows = []
    for name, s in groups.items():
        view, bay = s.similarity < sim_cut, s.distance > dist_cut
        blur = s.sharpness < sharp_cut
        row = {"frames": name, "n": len(s), "blocked": f"{s.blocked.mean():.0%}",
               "view check": f"{view.mean():.0%}", "sharpness check": f"{blur.mean():.0%}",
               "product (blocked, view or sharpness)": f"{(s.blocked | view | blur).mean():.0%}",
               "bay check (not used)": f"{bay.mean():.0%}"}  # fmt: skip
        if name.startswith("out"):
            y = np.r_[np.zeros(len(base)), np.ones(len(s))]
            row["view AUROC"] = round(roc_auc_score(y, -np.r_[base.similarity, s.similarity]), 3)
            row["sharpness AUROC"] = round(roc_auc_score(y, -np.r_[base.sharpness, s.sharpness]), 3)
            row["bay AUROC"] = round(roc_auc_score(y, np.r_[base.distance, s.distance]), 3)
        rows.append(row)
    (OUT / "ood.md").write_text(
        "# Unfamiliar inputs (OOD) and abstention\n\n"
        + __doc__.split("\n\n", 1)[1].split("`just")[0].strip()
        + "\n\nAfter the first run the bay check flagged 13% of normal frames on the other night "
        "(1% on block 4): its cut-off is tuned to the training night, the same lesson as "
        "calibration. "
        "The product therefore uses the blocked, view and sharpness checks; the bay check is "
        "reported but not used (a choice informed by the test). The sharpness check (frame "
        "sharpness divided by the snapshot's) was added after the first run showed that heavy "
        "blur passes the view check."
        + f"\n\nCut-offs: view similarity below {sim_cut:.3f}, sharpness ratio below "
        f"{sharp_cut:.3f}, bay distance above {dist_cut:.2f}; "
        f"blocked: mean pixel value below {DARK} or above {BRIGHT}. One frame every {EVERY} s. "
        "AUROC: how well each check separates these frames from the in-distribution test "
        "frames (1 = perfectly).\n\n" + md(pd.DataFrame(rows).fillna("")) + "\n"
    )
    logger.info("OOD cut-offs: similarity {:.3f}, distance {:.2f}", sim_cut, dist_cut)


def main() -> None:
    setup_logging(load_config().logging)
    run()


if __name__ == "__main__":
    main()
