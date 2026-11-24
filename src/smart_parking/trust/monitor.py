"""Monitoring: rolling signals of the running product, and alerts when they leave normal range.

Per frame the monitor records: brightness, the camera check's view similarity, whether the frame
was sent to a person, Model A's unsure share (bays with a probability between 0.2 and 0.8),
the share of bays needing review, and the time per frame. Normal ranges come from block 4
(validation). Over a rolling window of 30 frames (one minute at one frame every 2 s):

Alert conditions and the maintainer's response are in `RULES` and `ACTIONS` below.

Alerts are logged (Loguru, `alert` field) once when they start and once when they clear.
`just monitor-demo` replays the other night (one frame every 2 s) with two problems injected:
the street light dims gradually from 4:00, and the camera is knocked at 7:00.
"""

import json
import time
from collections import deque
from datetime import timedelta
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402
from loguru import logger  # noqa: E402
from PIL import Image  # noqa: E402

from smart_parking.common.config import load_config  # noqa: E402
from smart_parking.common.log import setup_logging  # noqa: E402
from smart_parking.trust.common import OUT, md  # noqa: E402
from smart_parking.trust.ood import ViewGuard, view_similarity  # noqa: E402

WINDOW = 30
ACTIONS = {
    "camera_problem": "check the lens and the camera's position; if it was moved on purpose, "
    "take a new snapshot and redraw the bay boxes",
    "lighting_change": "check the street light; watch the review rate",
    "many_reviews": "look at the evidence frames; if the scene changed for good, collect frames "
    "and re-adapt Model A",
    "model_unsure": "as above: a sign of a new kind of scene",
    "slow": "check the Mac's load; lower the frame rate",
    "commands_misread": "read the feedback records; teach the owner the fixed form; consider "
    "changing Model C",
}
RULES = {
    "camera_problem": "over 20% of frames fail the camera check",
    "lighting_change": "mean brightness outside normal +- 3 sd",
    "many_reviews": "over 30% of bays need a person",
    "model_unsure": "Model A unsure share over 3x normal",
    "slow": "time per frame p95 over 500 ms",
    "commands_misread": "owner rejected over 30% of the last 20 proposals",
}


class Monitor:
    """Rolling-window checks over the product's per-frame signals."""

    def __init__(self, normal: dict[str, float], window: int = WINDOW) -> None:
        self.normal, self.window = normal, deque(maxlen=window)
        self.active: set[str] = set()

    @staticmethod
    def signals(image: Image.Image, guard: ViewGuard, rows: list[dict], ms: float) -> dict:
        p = [r["occupancy_p"] for r in rows if r["occupancy_p"] is not None]
        return {
            "brightness": float(np.asarray(image.convert("L"), dtype=np.float32).mean()),
            "similarity": view_similarity(guard.view, image, guard.boxes),
            "camera_failed": float(any(r["occupied"] == -1 for r in rows)),
            "unsure": float(np.mean([0.2 < q < 0.8 for q in p])) if p else 0.0,
            "review": float(np.mean([r["status"] == "NEEDS_REVIEW" for r in rows])),
            "ms": ms,
        }

    def update(self, s: dict, feedback: Path | None = None) -> list[str]:
        """Add one frame's signals; return the alerts active now."""
        self.window.append(s)
        w = pd.DataFrame(self.window)
        n = self.normal
        firing = set()
        if len(w) == self.window.maxlen:
            if w.camera_failed.mean() > 0.2:
                firing.add("camera_problem")
            if abs(w.brightness.mean() - n["brightness_mean"]) > 3 * n["brightness_sd"]:
                firing.add("lighting_change")
            if w.review.mean() > 0.3:
                firing.add("many_reviews")
            if w.unsure.mean() > max(3 * n["unsure"], 0.1):
                firing.add("model_unsure")
            if np.percentile(w.ms, 95) > 500:
                firing.add("slow")
        if feedback is not None and feedback.exists():
            recent = [json.loads(x) for x in feedback.read_text().splitlines()[-20:]]
            if len(recent) >= 10 and np.mean([not r["accepted"] for r in recent]) > 0.3:
                firing.add("commands_misread")
        for alert in firing - self.active:
            logger.bind(alert=alert).warning("Monitor alert: {} ({})", alert, RULES[alert])
        for alert in self.active - firing:
            logger.bind(alert=alert).info("Monitor alert cleared: {}", alert)
        self.active = firing
        return sorted(firing)


def _stream(config: Path, every: float):  # noqa: ANN202
    from smart_parking.pipeline import video_frames

    cfg = yaml.safe_load(config.read_text())
    video = cfg["video"] if "video" in cfg else cfg["files"][-1]["video"]
    yield from video_frames(Path(video), every)


def demo() -> None:
    from smart_parking.commands.schema import Action, ParsedCommand, PermitTable
    from smart_parking.occupancy.adapt import VIDEO_TEST, VIDEO_TRAIN
    from smart_parking.pipeline import Pipeline, video_start
    from smart_parking.trust.robustness import stress

    pipe = Pipeline(commands=False)
    table = PermitTable()
    for n in ("33044", "66705"):  # the owner's permanent list (the cars in the video)
        table.apply(ParsedCommand(action=Action.ALLOW, number=n), confirm=lambda q: True)
    # Normal ranges from block 4 (validation), with its own snapshot
    cfg2 = yaml.safe_load(VIDEO_TRAIN.read_text())
    frames = list(_stream(VIDEO_TRAIN, 4))
    guard2 = ViewGuard.from_snapshot(frames[22][1], cfg2["boxes"])
    base = []
    for _, im in frames:
        start = time.perf_counter()
        rows = pipe.frame(
            im, cfg2["boxes"], video_start(Path(cfg2["files"][-1]["video"])), table, guard2
        )
        base.append(Monitor.signals(im, guard2, rows, (time.perf_counter() - start) * 1000))
    b = pd.DataFrame(base)
    normal = {"brightness_mean": b.brightness.mean(), "brightness_sd": b.brightness.std(),
              "unsure": b.unsure.mean(), "review": b.review.mean()}  # fmt: skip
    # The stream: the other night with injected problems
    cfg1 = yaml.safe_load(VIDEO_TEST.read_text())
    start_at = video_start(Path(cfg1["video"]))
    stream = list(_stream(VIDEO_TEST, 2))
    guard = ViewGuard.from_snapshot(next(im for t, im in stream if t >= 340), cfg1["boxes"])
    monitor, rng, log = Monitor(normal), np.random.default_rng(0), []
    for t, im in stream:
        if t >= 240:  # the street light dims over two minutes, down to 15%
            im = stress(im, "darkness", max(0.15, 1 - 0.85 * (t - 240) / 120), rng)
        if t >= 420:  # the camera is knocked: shifted and zoomed
            w, h = im.size
            im = im.crop((int(0.10 * w), int(0.05 * h), w, h)).resize((w, h))
        start = time.perf_counter()
        rows = pipe.frame(im, cfg1["boxes"], start_at + timedelta(seconds=t), table, guard)
        s = Monitor.signals(im, guard, rows, (time.perf_counter() - start) * 1000)
        log.append({"t": t, **s, "alerts": ", ".join(monitor.update(s))})
    d = pd.DataFrame(log)
    fig, axes = plt.subplots(4, 1, figsize=(9, 7), sharex=True)
    for ax, col, label in zip(axes, ["brightness", "similarity", "review", "unsure"],
                              ["brightness", "view similarity", "bays sent to a person",
                               "Model A unsure share"], strict=True):  # fmt: skip
        ax.plot(d.t / 60, d[col], lw=0.8)
        ax.plot(d.t / 60, d[col].rolling(WINDOW, min_periods=1).mean(), lw=1.5)
        ax.set_ylabel(label, fontsize=8)
        for x in (4, 7):
            ax.axvline(x, color="red", ls="--", lw=0.8)
        alerted = d[d.alerts != ""]
        ax.scatter(alerted.t / 60, [ax.get_ylim()[1]] * len(alerted), s=4, color="orange")
    axes[-1].set_xlabel("minutes (red: problem injected; orange: an alert is active)")
    fig.tight_layout()
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "figures" / "monitoring.png", dpi=150)
    events = []
    prev: set[str] = set()
    for r in d.itertuples():
        now = set(filter(None, r.alerts.split(", ")))
        for a in sorted(now - prev):
            events.append({"time": f"{int(r.t // 60)}:{int(r.t % 60):02d}", "event": f"alert: {a}"})
        for a in sorted(prev - now):
            events.append(
                {"time": f"{int(r.t // 60)}:{int(r.t % 60):02d}", "event": f"cleared: {a}"}
            )
        prev = now
    (OUT / "monitoring.md").write_text(
        "# Monitoring demonstration\n\n"
        + __doc__.split("\n\n", 1)[1].split("`just")[0].strip()
        + "\n\n"
        + md(
            pd.DataFrame(
                [
                    {"alert": k, "condition": RULES[k], "what the maintainer does": v}
                    for k, v in ACTIONS.items()
                ]
            )
        )  # fmt: skip
        + "\n\n## Normal ranges (block 4, validation)\n\n"
        + md(pd.DataFrame([{k: round(v, 3) for k, v in normal.items()}]))
        + "\n\n## The replayed stream: what the monitor saw\n\nProblems injected: the street light "
        "dims from 4:00 (to 15% by 6:00); the camera is knocked at 7:00.\n\n"
        + md(pd.DataFrame(events))
        + "\n\n## What this shows\n\n"
        "- The dimming light was flagged (`lighting_change`) about a minute after it began, and "
        "Model A then became unsure (`model_unsure`).\n"
        "- The knocked camera was flagged (`camera_problem`) only after about 1.5 minutes: on "
        "this night, normal frames already score 0.75-0.97 on the view check (headlights and "
        "parked cars change the scene), and the knocked view scored about 0.74, just above the "
        "cut-off set on the training night (0.725). It crossed it only when a car drove in.\n"
        "- Before any problem, the monitor fired twice: while a car stood across both bays for "
        "minutes (one bay always needs a person) and while cars were manoeuvring (Model A "
        "unsure). The first is useful news for the owner; the second is a false alarm that a "
        "longer window would reduce.\n\n![Monitoring](figures/monitoring.png)\n"
    )
    logger.info("Monitoring demo -> {}", OUT / "monitoring.md")


def main() -> None:
    setup_logging(load_config().logging)
    demo()


if __name__ == "__main__":
    main()
