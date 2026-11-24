"""Efficiency study: can the system do less work for the same answers?

Two ideas, measured on the other night (the saved per-frame results, one frame every 2 s):
1. **frame rate:** one frame every 2, 4 or 8 s, keeping the same 10 s to confirm a stay;
2. **plate caching:** once a stay's plate has been read the same way 3 times, stop running
   Model B on that bay until the car leaves (today it re-reads the same parked car every frame).
Quality: the answer at the end of each true stay (as the owner's car and as a visitor), per-stay
answers right on scored frames, notifications, and how late an arrival is confirmed. Cost: model
time per minute of video, from the measured time per call (outputs/loop/video_night_1.md).
`just efficiency`.
"""

import math
import re
from datetime import timedelta
from pathlib import Path

import pandas as pd
import yaml
from loguru import logger

from smart_parking.commands.schema import Action, ParsedCommand, PermitTable
from smart_parking.common.config import load_config
from smart_parking.common.log import setup_logging
from smart_parking.occupancy.adapt import VIDEO_TEST
from smart_parking.stays import BayTracker, stay_status
from smart_parking.trust.common import OUT, md

CONFIRM_SECONDS = 10


def _ms_per_call() -> tuple[float, float]:
    text = Path("outputs/loop/video_night_1.md").read_text()
    a = float(re.search(r"\| A occupancy[^|]*\| \d+ \| ([\d.]+) \|", text).group(1))
    b = float(re.search(r"\| B plate read[^|]*\| \d+ \| ([\d.]+) \|", text).group(1))
    return a, b


def simulate(
    d: pd.DataFrame, every: int, settle: int | None, owner: PermitTable, start, cars: list[dict]
) -> dict:  # noqa: ANN001
    """Replay the saved frames at a lower rate and/or with plate caching."""
    d = d[(d["t"] % every) == 0].sort_values("t")
    confirm = math.ceil(CONFIRM_SECONDS / every)
    rows, b_calls = [], 0
    for bay, g in d.groupby("bay"):
        tracker = BayTracker(confirm=confirm, settle_after=settle)
        for r in g.itertuples():
            raw_occ = r.occupied == 1
            if raw_occ and tracker.needs_read:
                b_calls += 1
                clear = str(r.plate_decision).startswith("READ") and r.plate
                read = r.plate.rsplit(" ", 1)[-1] if clear else None
            else:
                read = None
            occ, plate = tracker.update(raw_occ, read)
            at = start + timedelta(seconds=float(r.t))
            rows.append(
                {
                    "t": r.t,
                    "bay": bay,
                    "occ": occ,
                    "owner": stay_status(occ, plate, at, owner),
                    "visitor": stay_status(occ, plate, at, PermitTable()),
                    "true_owner": r.true_status,
                    "true_visitor": r.true_status_visitor,
                    "moving": str(r.moving) == "True",
                }
            )
    s = pd.DataFrame(rows)
    scored = s[~s.moving]
    end_right, delays = 0, []
    for car in cars:
        for bay in ("left", "right") if car["bay"] == "both" else (car["bay"],):
            g = s[(s.bay == bay) & (s.t >= car["from"]) & (s.t < car["to"])]
            if len(g):
                last = g.iloc[-1]
                end_right += (last.owner == last.true_owner) + (last.visitor == last.true_visitor)
            seen = g[g.occ]
            if car["bay"] != "both" and len(seen):
                delays.append(seen.t.min() - car["from"])
    notes = sum(
        (g.sort_values("t").owner != g.sort_values("t").owner.shift()).sum() - 1
        for _, g in s.groupby("bay")
    )
    return {
        "frames": s.t.nunique(),
        "A calls": s.t.nunique(),
        "B calls": b_calls,
        "stay-end answers right (of 12)": int(end_right),
        "per-stay answers right (scored)": f"{(scored.owner == scored.true_owner).mean():.0%}",
        "notifications": int(notes),
        "mean arrival delay (s)": round(sum(delays) / max(len(delays), 1), 1),
    }


def run() -> None:
    from smart_parking.pipeline import video_start

    cfg = yaml.safe_load(VIDEO_TEST.read_text())
    d = pd.read_csv("outputs/loop/local/video_night_1.csv", keep_default_na=False)
    owner = PermitTable()
    for n in yaml.safe_load(Path("configs/local_loop.yaml").read_text())["permanent"]:
        owner.apply(ParsedCommand(action=Action.ALLOW, number=str(n)), confirm=lambda q: True)
    start = video_start(Path(cfg["video"]))
    a_ms, b_ms = _ms_per_call()
    minutes = (d["t"].max() + 2) / 60
    rows = []
    for every in (2, 4, 8):
        for settle in (None, 3):
            r = simulate(d, every, settle, owner, start, cfg["cars"])
            cost = (r["A calls"] * a_ms + r["B calls"] * b_ms) / minutes
            rows.append(
                {
                    "frame every (s)": every,
                    "plate caching": "after 3 reads" if settle else "off",
                    **r,
                    "model time per minute of video (ms)": round(cost),
                }
            )
    table = pd.DataFrame(rows)
    base = table.iloc[0]["model time per minute of video (ms)"]
    table["cost vs today"] = (table["model time per minute of video (ms)"] / base).map(
        "{:.0%}".format
    )
    (OUT / "efficiency.md").write_text(
        "# Efficiency study (quality against cost)\n\n"
        + __doc__.split("\n\n", 1)[1].split("`just")[0].strip()
        + f"\n\nMeasured time per call: Model A {a_ms} ms per frame (both bays), Model B {b_ms} ms "
        "per occupied bay. The first row is today's product.\n\n" + md(table) + "\n"
    )
    logger.info("Efficiency -> {}", OUT / "efficiency.md")


def main() -> None:
    setup_logging(load_config().logging)
    run()


if __name__ == "__main__":
    main()
