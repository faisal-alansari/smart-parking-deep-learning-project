"""Efficiency study: can the system do less work for the same answers?

Two ideas, chosen on block 4 of night video 2 (validation; one frame every 2 s through the
product), then shown on night video 1 as a seen check:
1. **frame rate:** one frame every 2, 4 or 8 s, keeping the same 10 s to confirm a stay;
2. **plate caching:** once a stay's plate has been read the same way 3 times, stop running
   Model B on that bay until the car leaves.
Quality: the answer at the end of each true stay (as the owner's car and as a visitor), per-stay
answers right on scored frames, notifications, and how late an arrival is confirmed. Cost: model
time per minute of video, from the measured time per call (`outputs/loop/latency.md`).
Caching is kept only if, on block 4, it answers at least as many stay ends right, per-stay
answers stay within 1 point and Model B runs fewer times (rule fixed first; report Appendix A).
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
from smart_parking.occupancy.adapt import VIDEO_SEEN, VIDEO_TRAIN
from smart_parking.stays import BayTracker, stay_status, stay_update
from smart_parking.trust.common import OUT, md

CONFIRM_SECONDS = 10


BLOCK4_FRAMES = Path("outputs/loop/local/video_night_2_block4.csv")


def _ms_per_call() -> tuple[float, float]:
    text = Path("outputs/loop/latency.md").read_text()
    a = float(re.search(r"\| A occupancy[^|]*\| \d+ \| ([\d.]+) \|", text).group(1))
    b = float(re.search(r"\| B plate read[^|]*\| \d+ \| ([\d.]+) \|", text).group(1))
    return a, b


def block4_config() -> dict:
    """Night video 2, block 4 (validation) in the single-video form used by `frame_table`."""
    cfg = yaml.safe_load(VIDEO_TRAIN.read_text())
    f = next(f for f in cfg["files"] if f["split"] == "validation")
    straddle = (f.get("slices") or {}).get("car across both bays", [])
    return {
        "video": f["video"],
        "boxes": cfg["boxes"],
        "cars": f["cars"],
        "moving": f["moving"],
        "straddle": straddle,
        "permanent": cfg["permanent"],
        "every_s": cfg["every_s"],
        "snapshot_s": 90,
    }  # fmt: skip  (the camera check's empty-bay set-up frame)


def block4_frames() -> pd.DataFrame:
    """Block 4 through the product, frame by frame (cached; local plates, kept in Git)."""
    if not BLOCK4_FRAMES.exists():
        from smart_parking.pipeline import frame_table

        d, _ = frame_table(block4_config())
        BLOCK4_FRAMES.parent.mkdir(parents=True, exist_ok=True)
        d.to_csv(BLOCK4_FRAMES, index=False)
    return pd.read_csv(BLOCK4_FRAMES, keep_default_na=False)


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
            if r.occupied == 1 and tracker.needs_read:
                b_calls += 1
                clear = str(r.plate_decision).startswith("READ") and r.plate
                read = r.plate.rsplit(" ", 1)[-1] if clear else None
            else:
                read = None
            occ, plate, judged = stay_update(tracker, int(r.occupied), read)
            at = start + timedelta(seconds=float(r.t))
            rows.append(
                {
                    "t": r.t,
                    "bay": bay,
                    "occ": occ,
                    "owner": stay_status(occ, plate, at, owner, judged),
                    "visitor": stay_status(occ, plate, at, PermitTable(), judged),
                    "true_owner": r.true_status,
                    "true_visitor": r.true_status_visitor,
                    "moving": str(r.moving) == "True",
                }
            )
    s = pd.DataFrame(rows)
    scored = s[~s.moving]
    end_right, delays, n_ends = 0, [], 0
    for car in cars:
        for bay in ("left", "right") if car["bay"] == "both" else (car["bay"],):
            g = s[(s.bay == bay) & (s.t >= car["from"]) & (s.t < car["to"])]
            if len(g):
                n_ends += 1
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
        "stay-end answers right": f"{int(end_right)} of {2 * n_ends}",
        "per-stay answers right (scored)": f"{(scored.owner == scored.true_owner).mean():.0%}",
        "notifications": int(notes),
        "mean arrival delay (s)": round(sum(delays) / max(len(delays), 1), 1),
    }


def study(d: pd.DataFrame, cfg: dict, a_ms: float, b_ms: float) -> pd.DataFrame:
    """Every frame rate with and without caching on one video's saved per-frame results."""
    from smart_parking.pipeline import config_start

    owner = PermitTable()
    for n in cfg["permanent"]:
        owner.apply(ParsedCommand(action=Action.ALLOW, number=str(n)), confirm=lambda q: True)
    start = config_start(cfg)
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
    table["cost vs no caching"] = (table["model time per minute of video (ms)"] / base).map(
        "{:.0%}".format
    )
    return table


def keep_caching(table: pd.DataFrame) -> bool:
    """The rule fixed before running: same or more stay ends right, per-stay answers within
    1 point, fewer Model B runs (both at one frame every 2 s)."""
    off, on = table.iloc[0], table.iloc[1]
    ends = [int(str(r["stay-end answers right"]).split(" of ")[0]) for r in (off, on)]
    per_stay = [float(str(r["per-stay answers right (scored)"]).rstrip("%")) for r in (off, on)]
    return ends[1] >= ends[0] and per_stay[1] >= per_stay[0] - 1 and on["B calls"] < off["B calls"]


def run() -> None:
    """Study plate caching on block 4 and night 1; write `efficiency.md`."""
    a_ms, b_ms = _ms_per_call()
    val = study(block4_frames(), block4_config(), a_ms, b_ms)
    keep = keep_caching(val)
    night1 = yaml.safe_load(VIDEO_SEEN.read_text())
    seen = study(
        pd.read_csv("outputs/loop/local/video_night_1.csv", keep_default_na=False), night1, a_ms,
        b_ms,
    )  # fmt: skip
    (OUT / "efficiency.md").write_text(
        "# Efficiency study (quality against cost)\n\n"
        + __doc__.split("\n\n", 1)[1].split("`just")[0].strip()
        + f"\n\nMeasured time per call: Model A {a_ms} ms per frame (both bays), Model B {b_ms} ms "
        "per occupied bay.\n\n## Block 4 (validation): the choice\n\n"
        + md(val)
        + f"\n\n**Plate caching: {'kept' if keep else 'not kept'}** under the rule.\n\n"
        "## Night video 1 (seen check, not used to choose)\n\n" + md(seen) + "\n"
    )
    logger.info(
        "Efficiency: caching {} -> {}", "kept" if keep else "not kept", OUT / "efficiency.md"
    )


def main() -> None:
    """Set up logging and run the efficiency study."""
    setup_logging(load_config().logging)
    run()


if __name__ == "__main__":
    main()
