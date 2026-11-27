"""One decision per car's stay, for video input (rule fixed before it was run; report Appendix A).

Per bay, frame by frame:
- the bay changes between empty and occupied only after `CONFIRM_FRAMES` frames in a row
  agree (10 s at one frame every 2 s): a car needs several seconds to park or leave;
- the stay's plate is the clear read (READ) seen most often since the arrival began; it must
  appear at least `MIN_READS` times and in more than half of the clear reads, else the stay
  goes to a person;
- the permit check is redone at every frame's time;
- a frame the camera check rejects (occupancy -1, unknown) neither confirms nor ends a stay:
  the bay keeps its state and its answer is NEEDS_REVIEW until the view is usable again;
- each change of a bay's answer is one notification to the owner;
- once the stay's plate has been read the same way `SETTLE_READS` times, Model B stops reading
  that bay until the car leaves (added after the efficiency study).

`just video-night-1-stays` applies it to the saved per-frame results of the night video
(no models are run again) and compares it with frame-by-frame answers.
"""

import argparse
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import yaml
from loguru import logger

from smart_parking.commands.schema import Action, ParsedCommand, PermitTable
from smart_parking.common.config import load_config
from smart_parking.common.log import setup_logging
from smart_parking.loop import Status, _md

CONFIRM_FRAMES = 5
MIN_READS = 2
# Plate caching (efficiency study, outputs/trust/efficiency.md): once a stay's plate has been
# read the same way this many times, Model B is not run on that bay until the car leaves.
SETTLE_READS = 3
PU = "POTENTIALLY_UNAUTHORIZED"
UNKNOWN = -1  # per-frame occupancy when the camera check rejects the frame


def stay_plate(reads: list[str]) -> str | None:
    """The stay's plate: the most frequent clear read, if frequent enough."""
    if not reads:
        return None
    (text, n), *rest = Counter(reads).most_common()
    tie = bool(rest) and rest[0][1] == n
    return text if n >= MIN_READS and n * 2 > len(reads) and not tie else None


@dataclass
class BayTracker:
    """The smoothed state of one bay and the clear plate reads of the current stay."""

    occupied: bool = False
    streak: int = 0  # frames in a row that disagree with `occupied`
    pending: list[str] = field(default_factory=list)  # reads while an arrival is confirmed
    reads: list[str] = field(default_factory=list)
    confirm: int = CONFIRM_FRAMES
    settle_after: int | None = None  # stop reading plates once the stay's plate has this many

    @property
    def needs_read(self) -> bool:
        """Whether Model B must run on this bay now (False once the stay's plate is settled)."""
        if self.settle_after is None or not self.occupied:
            return True
        plate = stay_plate(self.reads)
        return plate is None or self.reads.count(plate) < self.settle_after

    def update(self, occupied: bool, read: str | None) -> tuple[bool, str | None]:
        """One frame: Model A's answer and Model B's clear read ('' or None if none).
        Returns the smoothed occupancy and the stay's plate."""
        if occupied == self.occupied:
            self.streak, self.pending = 0, []
        else:
            self.streak += 1
        if occupied and read:
            (self.reads if self.occupied else self.pending).append(read)
        if self.streak >= self.confirm:
            self.occupied, self.streak = occupied, 0
            self.reads, self.pending = (self.pending, []) if occupied else ([], [])
        return self.occupied, stay_plate(self.reads) if self.occupied else None


def stay_update(
    tracker: BayTracker, occupied: int, read: str | None
) -> tuple[bool, str | None, bool]:
    """One frame through the shared temporal step used by the CLI, the demo and every replay.

    `occupied` is 1, 0 or `UNKNOWN`; `read` is a new clear plate read (None for no read or a
    cached one, so a cached read is never counted twice). Returns the smoothed occupancy, the
    stay's plate and whether the frame could be judged (False: the bay must go to a person)."""
    if occupied == UNKNOWN:
        return tracker.occupied, stay_plate(tracker.reads) if tracker.occupied else None, False
    occ, plate = tracker.update(occupied == 1, read)
    return occ, plate, True


def stay_status(
    occupied: bool, plate: str | None, at: datetime, table: PermitTable, judged: bool = True
) -> Status:
    """The answer for a bay's current stay; an unjudged frame always goes to a person."""
    if not judged:
        return "NEEDS_REVIEW"
    if not occupied:
        return "EMPTY"
    if plate is None:
        return "NEEDS_REVIEW"
    return "AUTHORIZED" if table.find(plate, at) else PU


def apply_stays(frames: pd.DataFrame, start: datetime, owner: PermitTable) -> pd.DataFrame:
    """Add per-stay columns to the per-frame results (one row per frame and bay)."""
    out = []
    for _bay, g in frames.sort_values("t").groupby("bay", sort=False):
        tracker = BayTracker(settle_after=SETTLE_READS)
        for r in g.itertuples():
            clear = isinstance(r.plate, str) and str(r.plate_decision).startswith("READ")
            text = r.plate.rsplit(" ", 1)[-1] if clear and tracker.needs_read else None
            occ, plate, judged = stay_update(tracker, int(r.occupied), text)
            at = start + timedelta(seconds=float(r.t))
            visitor = stay_status(occ, plate, at, PermitTable(), judged)
            out.append({**r._asdict(), "stay_occupied": int(occ), "stay_plate": plate or "",
                        "stay_status": stay_status(occ, plate, at, owner, judged),
                        "stay_status_visitor": visitor})  # fmt: skip
    return pd.DataFrame(out).drop(columns="Index").sort_values(["t", "bay"])


def runs(g: pd.DataFrame, col: str) -> list[tuple[float, float, str]]:
    """(start, end, value) runs of one column over time; end = the next run's start."""
    g = g.sort_values("t")
    ids = (g[col] != g[col].shift()).cumsum()
    t = list(g["t"]) + [float(g["t"].iloc[-1]) + 2]
    out, i = [], 0
    for _, r in g.groupby(ids, sort=False):
        i += len(r)
        out.append((float(r["t"].iloc[0]), float(t[i]), r[col].iloc[0]))
    return out


def changes(g: pd.DataFrame, col: str) -> int:
    """How many times a column's value changes over time."""
    return len(runs(g, col)) - 1


def report(d: pd.DataFrame, cfg: dict) -> str:
    """Markdown comparing per-frame and per-stay answers, each true stay, and phantom stays."""
    from smart_parking.pipeline import clock

    scored = d[~d["moving"]]
    compare = {}
    for name, status, visitor, occ in (
        ("frame by frame", "status", "status_visitor", "occupied"),
        ("per stay", "stay_status", "stay_status_visitor", "stay_occupied"),
    ):
        s, empty = scored, scored[scored.truth_occupied == 0]
        compare[name] = {
            "occupancy right (scored)": f"{(s[occ] == s.truth_occupied).mean():.0%}",
            "empty bay called occupied (scored)": f"{int((empty[occ] == 1).sum())} of {len(empty)}",
            "owner's cars: answer right (scored)": f"{(s[status] == s.true_status).mean():.0%}",
            "as visitors: answer right (scored)":
                f"{(s[visitor] == s.true_status_visitor).mean():.0%}",
            "owner's cars: frames with a false alert (all)": int((d[status] == PU).sum()),
            "notifications to the owner, left + right (all)":
                " + ".join(str(changes(g, status)) for _, g in d.groupby("bay")),
        }  # fmt: skip
    table = pd.DataFrame(compare)
    table.insert(0, "measure", table.index)
    stays = []
    for car in cfg["cars"]:
        for bay in ["left", "right"] if car["bay"] == "both" else [car["bay"]]:
            g = d[(d.bay == bay) & (d.t >= car["from"]) & (d.t < car["to"])]
            occ = g[g.stay_occupied == 1]
            last = g.iloc[-1] if len(g) else None
            stays.append({
                "bay": bay, "true stay": f"{clock(car['from'])}-{clock(car['to'])}",
                "across both bays": "yes" if car["bay"] == "both" else "",
                "seen as occupied from": clock(occ.t.min()) if len(occ) else "never",
                "plate found": "yes" if (g.stay_plate != "").any() else "no",
                "answer at the end (owner's car)": last.stay_status if last is not None else "",
                "answer at the end (as a visitor)":
                    last.stay_status_visitor if last is not None else "",
            })  # fmt: skip
    phantom = []
    for bay, g in d.groupby("bay"):
        for a, b, v in runs(g, "stay_occupied"):
            if v and not g[(g.t >= a) & (g.t < b)].truth_occupied.any():
                phantom.append(f"{bay} {clock(a)}-{clock(b)}")
    return (
        "# Night video: one decision per stay\n\n"
        "The rule was fixed before it was run (report Appendix A, 2026-11-22): a bay changes state "
        f"only after {CONFIRM_FRAMES} frames in a row agree ({CONFIRM_FRAMES * cfg['every_s']} s), "
        f"and the stay's plate must be the most frequent clear read, seen at least {MIN_READS} "
        "times and in more than half of the clear reads. Same per-frame model outputs as "
        "`video_night_1.md`. **This video had already been seen, so this is a seen check, not "
        "a clean test.** Counts and times only. `(scored)`: frames while a car moves in or out "
        "are left out; `(all)`: every frame.\n\n"
        + _md(table)
        + "\n\n## Each true stay\n\n"
        + _md(pd.DataFrame(stays))
        + f"\n\nStays seen with no car there: {len(phantom)}"
        + (f" ({', '.join(phantom)})" if phantom else "")
        + ".\n"
    )


def main() -> None:
    """Apply the per-stay rule to night 1's per-frame results; write the CSV and report."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", type=Path, default=Path("configs/local_video_night_1.yaml"))
    args = ap.parse_args()
    setup_logging(load_config().logging)
    cfg = yaml.safe_load(args.config.read_text())
    from smart_parking.pipeline import config_start

    frames = pd.read_csv(Path("outputs/loop/local/video_night_1.csv"), keep_default_na=False)
    owner = PermitTable()
    for n in cfg["permanent"]:
        owner.apply(ParsedCommand(action=Action.ALLOW, number=str(n)), confirm=lambda q: True)
    d = apply_stays(frames, config_start(cfg), owner)
    d.to_csv(Path("outputs/loop/local/video_night_1_stays.csv"), index=False)
    out = Path("outputs/loop/video_night_1_stays.md")
    out.write_text(report(d, cfg))
    logger.info("Per-stay check -> {}", out)


if __name__ == "__main__":
    main()
