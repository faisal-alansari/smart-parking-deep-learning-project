"""Train one OccupancyCNN run on train, select the epoch and threshold on validation."""

import csv
import json
import time
from pathlib import Path

import numpy as np
import torch
from loguru import logger
from torch.nn import functional as F
from torch.utils.tensorboard import SummaryWriter

from smart_parking.common.config import OccupancyTrainConfig
from smart_parking.common.seed import set_seed
from smart_parking.occupancy.images import SplitData, load_split
from smart_parking.occupancy.metrics import best_threshold, binary_metrics
from smart_parking.occupancy.model import OccupancyCNN, count_parameters

MAX_SCRATCH_PARAMS = 50_000_000


def pick_device() -> torch.device:
    """Apple GPU when available, else CPU."""
    return torch.device("mps" if torch.backends.mps.is_available() else "cpu")


def augment(x: torch.Tensor, mode: str, gen: torch.Generator) -> torch.Tensor:
    """Batch augmentation on float images in [0, 1], shape (N, 3, H, W).

    "photo": brightness, contrast, light blur and a small shift.
    "photo_hflip": the same plus random horizontal flips. Vertical flips are never used.
    """
    if mode == "none":
        return x
    n, dev = x.shape[0], x.device

    def rand(*shape: int) -> torch.Tensor:
        return torch.rand(*shape, generator=gen).to(dev)

    brightness = 0.6 + 0.8 * rand(n, 1, 1, 1)
    contrast = 0.7 + 0.6 * rand(n, 1, 1, 1)
    mean = x.mean(dim=(1, 2, 3), keepdim=True)
    x = ((x - mean) * contrast + mean) * brightness
    blur = rand(n, 1, 1, 1) < 0.2
    x = torch.where(blur, F.avg_pool2d(x, 3, stride=1, padding=1, count_include_pad=False), x)
    pad = 4
    padded = F.pad(x, (pad, pad, pad, pad), mode="reflect")
    dx, dy = (torch.randint(0, 2 * pad + 1, (2,), generator=gen)).tolist()
    x = padded[:, :, dy : dy + x.shape[2], dx : dx + x.shape[3]]
    if mode == "photo_hflip":
        flip = rand(n, 1, 1, 1) < 0.5
        x = torch.where(flip, x.flip(3), x)
    return x.clamp(0, 1)


def to_tensor(images: np.ndarray, device: torch.device) -> torch.Tensor:
    """(N, H, W, 3) uint8 -> (N, 3, H, W) uint8 on device."""
    return torch.from_numpy(images).permute(0, 3, 1, 2).contiguous().to(device)


@torch.no_grad()
def predict(
    model: OccupancyCNN,
    images: torch.Tensor,
    mean: torch.Tensor,
    std: torch.Tensor,
    batch_size: int = 1024,
) -> np.ndarray:
    """Probability of "occupied" for uint8 images already on the model's device."""
    model.eval()
    out = []
    for i in range(0, len(images), batch_size):
        x = (images[i : i + batch_size].float() / 255 - mean) / std
        out.append(torch.sigmoid(model(x)).cpu())
    return torch.cat(out).numpy()


def train_run(cfg: OccupancyTrainConfig, seed: int, run_name: str) -> dict:
    """Train one model. Returns its validation summary and writes logs and a checkpoint."""
    set_seed(seed)
    log = logger.bind(run=run_name)
    device = pick_device()
    args = (cfg.dataset_csv, cfg.raw_root, cfg.cache_dir)
    train: SplitData = load_split("train", cfg.input_size, *args)
    val: SplitData = load_split("val", cfg.input_size, *args)

    xtr, xva = to_tensor(train.images, device), to_tensor(val.images, device)
    ytr = torch.from_numpy(train.labels).float().to(device)
    # Normalisation statistics come from the training split only.
    mean = (xtr.float() / 255).mean(dim=(0, 2, 3), keepdim=True)
    std = (xtr.float() / 255).std(dim=(0, 2, 3), keepdim=True)

    model = OccupancyCNN(cfg.channels, cfg.dropout).to(device)
    n_params = count_parameters(model)
    if n_params > MAX_SCRATCH_PARAMS:
        raise ValueError(f"OccupancyCNN has {n_params} parameters, above the 50M limit")
    opt = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
    steps_per_epoch = (len(xtr) + cfg.batch_size - 1) // cfg.batch_size
    sched = torch.optim.lr_scheduler.OneCycleLR(
        opt, max_lr=cfg.lr, total_steps=cfg.epochs * steps_per_epoch, pct_start=0.15
    )
    gen = torch.Generator().manual_seed(seed)

    run_dir = cfg.run_dir / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    writer = SummaryWriter(str(run_dir))
    history = []
    best_f1, best_state, best_epoch = -1.0, None, -1
    log.info("Training {} params on {} for {} epochs", n_params, device, cfg.epochs)
    start = time.time()
    for epoch in range(1, cfg.epochs + 1):
        model.train()
        order = torch.randperm(len(xtr), generator=gen).to(device)
        total = 0.0
        for i in range(0, len(xtr), cfg.batch_size):
            idx = order[i : i + cfg.batch_size]
            x = augment(xtr[idx].float() / 255, cfg.augment, gen)
            loss = F.binary_cross_entropy_with_logits(model((x - mean) / std), ytr[idx])
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            sched.step()
            total += loss.item() * len(idx)
        prob = predict(model, xva, mean, std)
        val_loss = float(
            F.binary_cross_entropy(
                torch.from_numpy(prob).clamp(1e-7, 1 - 1e-7), torch.from_numpy(val.labels).float()
            )
        )
        m = binary_metrics(val.labels, prob >= 0.5)
        row = {
            "epoch": epoch,
            "train_loss": total / len(xtr),
            "val_loss": val_loss,
            **{f"val_{k}": v for k, v in m.items()},
        }
        history.append(row)
        for k, v in row.items():
            if k != "epoch":
                writer.add_scalar(k, v, epoch)
        writer.add_scalar("lr", sched.get_last_lr()[0], epoch)
        log.info(
            "epoch {} train_loss {:.4f} val_loss {:.4f} val_f1 {:.4f}",
            epoch,
            row["train_loss"],
            val_loss,
            m["f1"],
        )
        if m["f1"] > best_f1:
            best_f1, best_epoch = m["f1"], epoch
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
    writer.close()

    model.load_state_dict(best_state)
    prob = predict(model, xva, mean, std)
    threshold = best_threshold(val.labels, prob)
    val_metrics = binary_metrics(val.labels, prob >= threshold)
    summary = {
        "run": run_name,
        "seed": seed,
        "params": n_params,
        "best_epoch": best_epoch,
        "threshold": threshold,
        "val": val_metrics,
        "val_f1_at_0.5": best_f1,
        "train_seconds": round(time.time() - start, 1),
        "config": cfg.model_dump(mode="json"),
    }
    with (run_dir / "history.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(history[0]))
        w.writeheader()
        w.writerows(history)
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    cfg.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    torch.save(
        {"state_dict": best_state, "mean": mean.cpu(), "std": std.cpu(), "summary": summary},
        cfg.checkpoint_dir / f"{run_name}.pt",
    )
    log.info(
        "Best epoch {} val F1 {:.4f} (threshold {:.3f})", best_epoch, val_metrics["f1"], threshold
    )
    return summary


def load_checkpoint(
    path: Path, device: torch.device
) -> tuple[OccupancyCNN, torch.Tensor, torch.Tensor, dict]:
    """Rebuild a trained model and its normalisation from a checkpoint."""
    ckpt = torch.load(path, map_location="cpu", weights_only=False)
    cfg = ckpt["summary"]["config"]
    model = OccupancyCNN(cfg["channels"], cfg["dropout"])
    model.load_state_dict(ckpt["state_dict"])
    return model.to(device), ckpt["mean"].to(device), ckpt["std"].to(device), ckpt["summary"]
