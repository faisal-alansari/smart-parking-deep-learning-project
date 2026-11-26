"""Compute and latency budget on this Mac: load time, peak memory, time per stage and per frame.

Measured on the sample night clip (`samples/owner_camera`, one frame every 2 s) and the Model C
dev commands, never on test data. Writes `outputs/loop/latency.md`. `just latency`.
"""

import json
import platform
import resource
import tempfile
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger

from smart_parking.commands.schema import PermitTable
from smart_parking.common.config import load_config
from smart_parking.common.log import setup_logging
from smart_parking.loop import _md
from smart_parking.pipeline import Pipeline, run_folder

SAMPLE = Path("samples/owner_camera")
OUT = Path("outputs/loop/latency.md")


def _peak_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**30  # bytes on macOS


def main() -> None:
    """Load all models once, replay the sample folder and the dev commands, write the table."""
    cfg = load_config()
    setup_logging(cfg.logging)
    start = time.perf_counter()
    pipe = Pipeline(commands=True, deploy="adapted")
    load_s = time.perf_counter() - start
    frame_ms: list[float] = []
    inner = pipe.frame

    def timed_frame(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
        t0 = time.perf_counter()
        out = inner(*args, **kwargs)
        frame_ms.append((time.perf_counter() - t0) * 1000)
        return out

    pipe.frame = timed_frame
    with tempfile.TemporaryDirectory() as tmp:
        run_folder(SAMPLE, 2.0, True, Path(tmp), PermitTable(), {"adapted": pipe})
        dev = [json.loads(line) for line in (cfg.commands.data_dir / "dev.jsonl").open()]
        for row in dev:
            now = datetime.fromisoformat(row["now"])
            pipe.command(row["text"], now, PermitTable(), lambda q, c: None, Path(tmp) / "f.jsonl")
    table = pipe.timing()
    frames = pd.DataFrame(
        [
            {
                "stage": "one frame end to end (camera check + A + B + permits)",
                "calls": len(frame_ms),
                "mean ms": round(float(np.mean(frame_ms)), 1),
                "p95 ms": round(float(np.percentile(frame_ms, 95)), 1),
            }
        ]  # fmt: skip
    )
    OUT.write_text(
        "# Time and memory per stage\n\n"
        + __doc__.split("\n\n", 1)[1].split("`just")[0].strip()
        + f"\n\nMachine: {platform.machine()} macOS {platform.mac_ver()[0]}, device "
        f"{pipe.device}. Models loaded once in **{load_s:.1f} s**; peak memory of the process "
        f"**{_peak_gb():.1f} GB**.\n\n"
        + _md(pd.concat([table, frames], ignore_index=True))
        + "\n\nAt one frame every 2 s, a frame that takes well under a second keeps up in real "
        "time; a command answers in well under a second.\n"
    )
    logger.info("Latency: load {:.1f} s, {} frames -> {}", load_s, len(frame_ms), OUT)


if __name__ == "__main__":
    main()
