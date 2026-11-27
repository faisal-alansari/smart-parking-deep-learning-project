"""Adapt Model A (OccupancyCNN) to the owner's fixed camera at night (plan: report Appendix A).

Data: bay crops cut from the owner's night video 2 exactly as the product cuts them (64 px), one
frame every 2 s, moving periods left out, labels from the owner-checked truth. Blocks 1-3 train,
block 4 chooses. Night video 3, recorded for the test only and sealed until the end, is the
final test (`--reproduce` scores the deployed copies on it); night video 1 was the first final
test (`--final`, run once) and is now a seen check.

Options (each with seeds 42, 43, 44; deployed as the majority vote of the three):
- a: no training, a new threshold per seed chosen on block 4;
- b: fine-tune the last conv block and the head;
- c: fine-tune the whole model at a low learning rate (1e-4 and 3e-4);
- d: a wider CNN (32-64-128-256) trained from scratch on public + local crops.
b-d mix equal numbers of public and local crops in every epoch.

Choice: the best majority-vote balanced accuracy on block 4, provided the option misses no more
parked cars than the current model on block 4 and keeps public validation F1 within 1 point.

`just adapt-occupancy` (choose on block 4) then `just adapt-occupancy-final` (test once).
Counts only in outputs/occupancy/adaptation_*.md; crops stay in data/ (they show plates).
"""

import argparse
import json
import shutil
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
import yaml
from loguru import logger
from PIL import Image

from smart_parking.common.config import OccupancyTrainConfig, load_config
from smart_parking.common.log import setup_logging
from smart_parking.common.seed import set_seed
from smart_parking.occupancy.images import load_split
from smart_parking.occupancy.metrics import binary_metrics
from smart_parking.occupancy.model import OccupancyCNN, count_parameters
from smart_parking.occupancy.train import (
    MAX_SCRATCH_PARAMS,
    augment,
    load_checkpoint,
    pick_device,
    predict,
    to_tensor,
)

VIDEO_TRAIN = Path("configs/local_video_night_2.yaml")
VIDEO_TEST = Path("configs/local_video_night_3.yaml")  # sealed: test only, run once
VIDEO_SEEN = Path("configs/local_video_night_1.yaml")  # the earlier test, now a seen check
CROPS = Path("data/processed/video_crops")
RUNS = Path("experiments/occupancy_adapt")
WIDE = [32, 64, 128, 256]
OPTIONS = {  # name: (what is trained, learning rate, epochs)
    "b_last_block": ("last_block", 1e-3, 10),
    "c_full_lr1e-4": ("full", 1e-4, 10),
    "c_full_lr3e-4": ("full", 3e-4, 10),
    "d_wide_scratch": ("scratch", 1e-3, 12),
}
ORDER = ["a_threshold", *OPTIONS]  # simpler first: wins ties
LOCAL_BATCH = 64  # local crops per batch; the same number of public crops is added


# --- Crops from the videos ---------------------------------------------------------------


def video_files(cfg: dict) -> list[dict]:
    """Both video config formats as a list of files."""
    if "files" in cfg:
        return cfg["files"]
    slices = {"car across both bays": cfg.get("straddle", []), **(cfg.get("slices") or {})}
    # a blocked lens shows no bay: left out of crop-level scores, like a moving car
    return [{"video": cfg["video"], "split": "test", "cars": cfg["cars"],
             "moving": cfg["moving"] + cfg.get("blocked", []), "slices": slices}]  # fmt: skip


def truth(cars: list[dict], bay: str, t: float) -> int:
    """1 if a car is in this bay at time t (a car across both bays counts for each)."""
    return int(any(c["from"] <= t < c["to"] and c["bay"] in (bay, "both") for c in cars))


def build_crops(config: Path, size: int) -> tuple[np.ndarray, pd.DataFrame]:
    """Every scored bay crop of one video config (cached in data/, local only)."""
    from smart_parking.pipeline import in_any, video_frames

    cache = CROPS / f"{config.stem}_{size}.npz"
    if cache.exists():
        stored = np.load(cache, allow_pickle=False)
        return stored["images"], pd.read_csv(cache.with_suffix(".csv"))
    cfg = yaml.safe_load(config.read_text())
    images, rows = [], []
    for f in video_files(cfg):
        for t, im in video_frames(Path(f["video"]), cfg["every_s"]):
            if in_any(t, f["moving"]):
                continue
            w, h = im.size
            slice_ = next((k for k, v in (f.get("slices") or {}).items() if in_any(t, v)), "normal")
            for bay, (x0, y0, x1, y1) in cfg["boxes"].items():
                crop = im.crop((round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h)))
                images.append(np.asarray(crop.resize((size, size), Image.BILINEAR)))
                label = truth(f["cars"], bay, t)
                rows.append({"file": Path(f["video"]).name, "split": f["split"], "t": t,
                             "bay": bay, "label": label, "slice": slice_})  # fmt: skip
        logger.info("Crops from {}: {}", Path(f["video"]).name, len(rows))
    CROPS.mkdir(parents=True, exist_ok=True)
    meta = pd.DataFrame(rows)
    np.savez(cache, images=np.stack(images))
    meta.to_csv(cache.with_suffix(".csv"), index=False)
    return np.stack(images), meta


# --- Metrics -------------------------------------------------------------------------------


def balanced(y: np.ndarray, pred: np.ndarray) -> float:
    """Average of the right rate on empty and on occupied bays."""
    y, pred = y.astype(bool), pred.astype(bool)
    return float(((pred & y).sum() / max(y.sum(), 1) + (~pred & ~y).sum() / max((~y).sum(), 1)) / 2)


def best_balanced_threshold(y: np.ndarray, prob: np.ndarray) -> tuple[float, float]:
    """The threshold with the best balanced accuracy, and that accuracy."""
    candidates = np.unique(np.concatenate([np.quantile(prob, np.linspace(0, 1, 401)), [0.5]]))
    scores = [balanced(y, prob >= c) for c in candidates]
    i = int(np.argmax(scores))
    return float(candidates[i]), scores[i]


def vote(probs: list[np.ndarray], thresholds: list[float]) -> np.ndarray:
    """Majority vote of the seeds, each with its own threshold."""
    return np.mean([p >= t for p, t in zip(probs, thresholds, strict=True)], axis=0) > 0.5


def summary_row(y: np.ndarray, pred: np.ndarray) -> dict:
    """Balanced accuracy, missed cars, empty bays called occupied and F1."""
    return {"balanced accuracy": round(balanced(y, pred), 4),
            "parked cars missed": int((y.astype(bool) & ~pred).sum()),
            "empty bays called occupied": int((~y.astype(bool) & pred).sum()),
            "F1": round(binary_metrics(y, pred)["f1"], 4)}  # fmt: skip


# --- Training ------------------------------------------------------------------------------


def train_option(name: str, seed: int, cfg: OccupancyTrainConfig, data: dict) -> dict:
    """One run of option b, c or d; the best epoch and threshold are chosen on block 4."""
    what, lr, epochs = OPTIONS[name]
    set_seed(seed)
    device = pick_device()
    xl, yl = data["local_x"], data["local_y"]
    xp, yp = data["public_x"], data["public_y"]
    if what == "scratch":
        channels = WIDE
        model = OccupancyCNN(channels, cfg.dropout).to(device)
        mean, std = data["public_mean"], data["public_std"]
    else:
        model, mean, std, base = load_checkpoint(cfg.checkpoint_dir / f"final_s{seed}.pt", device)
        channels = base["config"]["channels"]
    n_params = count_parameters(model)
    if n_params > MAX_SCRATCH_PARAMS:
        raise ValueError(f"{n_params} parameters, above the 50M limit")
    frozen = model.features[:21] if what == "last_block" else None  # all but the last block
    if frozen is not None:
        for p in frozen.parameters():
            p.requires_grad = False
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=lr, weight_decay=cfg.weight_decay)
    n_local = len(xp) if what == "scratch" else len(xl)  # crops of each kind per epoch
    steps = epochs * ((n_local + LOCAL_BATCH - 1) // LOCAL_BATCH)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=lr, total_steps=steps, pct_start=0.15)
    gen = torch.Generator().manual_seed(seed)
    best = (-1.0, None, 0, 0.5)
    history = []
    start = time.time()
    for epoch in range(1, epochs + 1):
        model.train()
        if frozen is not None:
            frozen.eval()  # keep the frozen batch-norm statistics
        li = (
            torch.randint(len(xl), (n_local,), generator=gen)
            if what == "scratch"
            else torch.randperm(len(xl), generator=gen)
        )
        pi = torch.randint(len(xp), (n_local,), generator=gen)
        for i in range(0, n_local, LOCAL_BATCH):
            idx_l, idx_p = li[i : i + LOCAL_BATCH].to(device), pi[i : i + LOCAL_BATCH].to(device)
            x = torch.cat([xl[idx_l], xp[idx_p]]).float() / 255
            y = torch.cat([yl[idx_l], yp[idx_p]])
            x = augment(x, cfg.augment, gen)
            loss = F.binary_cross_entropy_with_logits(model((x - mean) / std), y)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            sched.step()
        prob = predict(model, data["val_x"], mean, std)
        threshold, score = best_balanced_threshold(data["val_y"], prob)
        history.append({"epoch": epoch, "val_balanced": score, "threshold": threshold})
        if score > best[0]:
            state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            best = (score, state, epoch, threshold)
    score, state, epoch, threshold = best
    model.load_state_dict(state)
    public = predict(model, data["public_val_x"], mean, std)
    summary = {
        "run": f"{name}_s{seed}", "seed": seed, "option": name, "params": n_params,
        "best_epoch": epoch, "threshold": threshold, "block4_balanced": score,
        "public_val_f1": binary_metrics(data["public_val_y"], public >= threshold)["f1"],
        "train_seconds": round(time.time() - start, 1),
        "config": {**cfg.model_dump(mode="json"), "channels": channels, "lr": lr, "epochs": epochs},
    }  # fmt: skip
    RUNS.mkdir(parents=True, exist_ok=True)
    torch.save({"state_dict": state, "mean": mean.cpu(), "std": std.cpu(), "summary": summary},
               RUNS / f"{name}_s{seed}.pt")  # fmt: skip
    pd.DataFrame(history).to_csv(RUNS / f"{name}_s{seed}_history.csv", index=False)
    logger.info("{} seed {}: block 4 balanced {:.4f} (epoch {}), public val F1 {:.4f}, {} s",
                name, seed, score, epoch, summary["public_val_f1"],
                summary["train_seconds"])  # fmt: skip
    return summary


def load_data(cfg: OccupancyTrainConfig, device: torch.device) -> dict:
    """Local video crops and public train and validation sets as tensors, with public stats."""
    images, meta = build_crops(VIDEO_TRAIN, cfg.input_size)
    tr, va = (meta["split"] == "train").to_numpy(), (meta["split"] == "validation").to_numpy()
    args = (cfg.dataset_csv, cfg.raw_root, cfg.cache_dir)
    public, public_val = (
        load_split("train", cfg.input_size, *args),
        load_split("val", cfg.input_size, *args),
    )
    xp = to_tensor(public.images, device)
    return {
        "meta": meta,
        "local_x": to_tensor(images[tr], device),
        "local_y": torch.from_numpy(meta["label"].to_numpy()[tr]).float().to(device),
        "val_x": to_tensor(images[va], device),
        "val_y": meta["label"].to_numpy()[va],
        "public_x": xp,
        "public_y": torch.from_numpy(public.labels).float().to(device),
        "public_mean": (xp.float() / 255).mean(dim=(0, 2, 3), keepdim=True),
        "public_std": (xp.float() / 255).std(dim=(0, 2, 3), keepdim=True),
        "public_val_x": to_tensor(public_val.images, device),
        "public_val_y": public_val.labels,
    }


# --- Choosing on block 4 -------------------------------------------------------------------


def _md(df: pd.DataFrame) -> str:
    lines = ["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)]
    lines += ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(lines)


def ensemble(paths: list[Path], device: torch.device, x: torch.Tensor,
             thresholds: list[float] | None = None) -> tuple[np.ndarray, list[float]]:  # fmt: skip
    """Majority vote of the checkpoints on x (given or saved thresholds), and the probs."""
    probs, ts = [], []
    for p in paths:
        model, mean, std, s = load_checkpoint(p, device)
        probs.append(predict(model, x, mean, std))
        ts.append(s["threshold"])
    return vote(probs, thresholds or ts), probs


def choose(cfg: OccupancyTrainConfig, report_only: bool = False) -> None:
    """Choose the adaptation option on block 4. With `report_only`, the saved runs are read
    back (never trained) and the choice must equal the stored one."""
    device = pick_device()
    data = load_data(cfg, device)
    yv, ypv = data["val_y"], data["public_val_y"]
    current = [cfg.checkpoint_dir / f"final_s{s}.pt" for s in cfg.seeds]
    rows, runs = {}, []
    pred, probs = ensemble(current, device, data["val_x"])
    public_now, _ = ensemble(current, device, data["public_val_x"])
    rows["current model (public data only)"] = {
        **summary_row(yv, pred),
        "public val F1": round(binary_metrics(ypv, public_now)["f1"], 4),
    }
    limit_missed = rows["current model (public data only)"]["parked cars missed"]
    limit_f1 = rows["current model (public data only)"]["public val F1"] - 0.01
    # a: the same weights, a new threshold per seed chosen on block 4
    ts = [best_balanced_threshold(yv, p)[0] for p in probs]
    _, public_probs = ensemble(current, device, data["public_val_x"])
    RUNS.mkdir(parents=True, exist_ok=True)
    for seed, path, t in zip(cfg.seeds, current, ts, strict=True):
        if report_only:
            break
        ckpt = torch.load(path, map_location="cpu", weights_only=False)
        ckpt["summary"] = {**ckpt["summary"], "run": f"a_threshold_s{seed}",
                           "option": "a_threshold", "threshold": t}  # fmt: skip
        torch.save(ckpt, RUNS / f"a_threshold_s{seed}.pt")
    public_f1 = binary_metrics(ypv, vote(public_probs, ts))["f1"]
    rows["a_threshold"] = {**summary_row(yv, vote(probs, ts)), "public val F1": round(public_f1, 4)}
    for name in OPTIONS:
        for seed in cfg.seeds:
            if report_only:
                saved = torch.load(RUNS / f"{name}_s{seed}.pt", map_location="cpu",
                                   weights_only=False)  # fmt: skip
                runs.append(saved["summary"])
            else:
                runs.append(train_option(name, seed, cfg, data))
        paths = [RUNS / f"{name}_s{s}.pt" for s in cfg.seeds]
        pred, _ = ensemble(paths, device, data["val_x"])
        public_pred, _ = ensemble(paths, device, data["public_val_x"])
        public_f1 = binary_metrics(ypv, public_pred)["f1"]
        rows[name] = {**summary_row(yv, pred), "public val F1": round(public_f1, 4)}
    table = pd.DataFrame(rows).T
    table["allowed"] = (table["parked cars missed"] <= limit_missed) & (
        table["public val F1"] >= limit_f1
    )
    options = table.loc[ORDER]
    allowed = options[options["allowed"]]
    winner = str(allowed["balanced accuracy"].astype(float).idxmax()) if len(allowed) else "none"
    table.insert(0, "option", table.index)
    by_seed = pd.DataFrame(runs)[
        ["run", "best_epoch", "threshold", "block4_balanced", "public_val_f1", "train_seconds"]
    ].round(4)
    meta = data["meta"]
    counts = meta.groupby(["split", "label"]).size().unstack(fill_value=0)
    counts.columns = ["empty", "occupied"]
    counts.insert(0, "split", counts.index)
    out = cfg.results_dir / "adaptation_val.md"
    out.write_text(
        "# Model A adaptation: choosing on block 4 (validation)\n\n"
        "Plan fixed before training (report Appendix A, 2026-11-25). Local crops from the "
        "owner's night video 2: blocks 1-3 train, block 4 chooses; moving periods left out. "
        "Each option is the majority vote of seeds 42, 43, 44. Allowed: no more parked cars "
        f"missed than the current model ({limit_missed}) and public validation F1 at least "
        f"{limit_f1:.4f}.\n\n"
        "## Crops\n\n"
        + _md(counts)
        + "\n\n## Options (block 4)\n\n"
        + _md(table)
        + f"\n\n**Chosen: {winner}**\n\n## Each run\n\n"
        + _md(by_seed)
        + "\n"
    )
    choice = cfg.results_dir / "adaptation_choice.json"
    if report_only and json.loads(choice.read_text())["option"] != winner:
        raise SystemExit(f"Block 4 now chooses {winner}, not the stored option: check the runs.")
    choice.write_text(json.dumps({"option": winner}))
    logger.info("Chosen option: {} -> {}", winner, out)


# --- The one final test --------------------------------------------------------------------


def final_test(cfg: OccupancyTrainConfig, reproduce: bool = False) -> None:
    """Test once: the sealed night video 3, the public test sets and the local photos."""
    winner = json.loads((cfg.results_dir / "adaptation_choice.json").read_text())["option"]
    if winner == "none":
        raise SystemExit("No option met the rules; the current model stays.")
    if (cfg.results_dir / "adaptation_test.md").exists() and not reproduce:
        raise SystemExit(
            "The final test has already been run once; use --reproduce to "
            "regenerate its tables (nothing is chosen again)."
        )
    device = pick_device()
    before = [cfg.checkpoint_dir / f"final_s{s}.pt" for s in cfg.seeds]
    after = [RUNS / f"{winner}_s{s}.pt" for s in cfg.seeds]
    if reproduce:  # the deployed copies (the run folder's checkpoints are not in Git)
        after = [cfg.checkpoint_dir / f"adapted_s{s}.pt" for s in cfg.seeds]
    sections = []
    # 1. Night video 3 (sealed; a different night from training)
    images, meta = build_crops(VIDEO_TEST, cfg.input_size)
    x, y = to_tensor(images, device), meta["label"].to_numpy()
    rows = []
    for name, paths in (("before", before), ("after", after)):
        pred, _ = ensemble(paths, device, x)
        for slice_, idx in [
            ("all", np.ones(len(y), bool)),
            *[(k, (meta["slice"] == k).to_numpy()) for k in meta["slice"].unique()],
        ]:
            rows.append(
                {
                    "model": name,
                    "frames": slice_,
                    "bay checks": int(idx.sum()),
                    **summary_row(y[idx], pred[idx]),
                }
            )
    sections.append(
        "## 1. Night video 3 (the sealed final test; a different night)\n\n"
        + _md(pd.DataFrame(rows))
    )
    # 2. Public test sets (did adapting break the public data?)
    rows = []
    for split in ("test", "test_unseen_camera", "test_unseen_site"):
        data = load_split(
            split, cfg.input_size, cfg.dataset_csv, cfg.raw_root, cfg.cache_dir, allow_test=True
        )
        xt = to_tensor(data.images, device)
        for name, paths in (("before", before), ("after", after)):
            pred, _ = ensemble(paths, device, xt)
            m = binary_metrics(data.labels, pred)
            rows.append(
                {
                    "split": split,
                    "model": name,
                    "F1": round(m["f1"], 4),
                    "accuracy": round(m["accuracy"], 4),
                }
            )
    sections.append("## 2. Public test sets\n\n" + _md(pd.DataFrame(rows)))
    # 3. Local photos (other car parks and the day/night pilot; boxes change per photo)
    from smart_parking.occupancy import local_pilot as lp

    rows = []
    for config in (Path("configs/local_pilot.yaml"), Path("configs/local_night_1.yaml")):
        pilot = yaml.safe_load(config.read_text())
        imgs, meta_p, _ = lp.crop_bays(pilot, cfg.input_size)
        xt, yt = to_tensor(imgs, device), meta_p["truth"].to_numpy()
        for name, paths in (("before", before), ("after", after)):
            pred, _ = ensemble(paths, device, xt)
            photos = config.stem.replace("local_", "")
            rows.append({"photos": photos, "model": name, "bays": len(yt),
                         **summary_row(yt, pred)})  # fmt: skip
    sections.append(
        "## 3. Local photos (other car parks; check only)\n\n" + _md(pd.DataFrame(rows))
    )
    if not reproduce:
        for seed, path in zip(cfg.seeds, after, strict=True):  # the deployed Model A
            shutil.copy(path, cfg.checkpoint_dir / f"adapted_s{seed}.pt")
    out = cfg.results_dir / "adaptation_test.md"
    out.write_text(
        f"# Model A adaptation: the one final test (chosen option: {winner})\n\n"
        "Run once, after the choice on block 4; results accepted as they are. `before` = the "
        "model trained on public data only; `after` = the adapted model. Counts only.\n\n"
        + "\n\n".join(sections)
        + "\n"
    )
    logger.info("Final test -> {}", out)


def main() -> None:
    """Run the final test (or rebuild its tables), else choose the adaptation."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--final", action="store_true", help="the one final test")
    ap.add_argument("--reproduce", action="store_true", help="regenerate the final test tables")
    ap.add_argument(
        "--report-choice", action="store_true", help="rebuild the block-4 table (no training)"
    )
    args = ap.parse_args()
    project = load_config()
    setup_logging(project.logging)
    if args.final or args.reproduce:
        final_test(project.occupancy, reproduce=args.reproduce)
    else:
        choose(project.occupancy, report_only=args.report_choice)


if __name__ == "__main__":
    main()
