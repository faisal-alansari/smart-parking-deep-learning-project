"""The one final test of the whole system on the sealed night video 3.

Night video 3 was recorded for this test only (docs/planning/test_video_checklist.md) and never
used for training, validation or any choice. Its truth (configs/local_video_night_3.yaml) was
marked from the frames and checked by the owner before any model saw the video. The rules and
the primary measure were fixed in Memory.md (2026-11-27) before the run.

1. The owner's typed commands (`commands.txt` beside the video) go through Model C as in the
   product. Each proposal is accepted as proposed, so a Model C mistake reaches the bays. The
   intended permit table is built by hand from the same lines (`commands` in the config).
2. Every frame (one every 2 s) goes through the camera check, Model A and Model B against the
   table Model C built.
3. The per-stay rule (`smart_parking.stays`, with plate caching) gives one answer per stay.

**Primary measure:** of the true stays of at least 30 s, the share whose answer at the stay's
last parked frame is right (owner's table). Stays under 30 s are reported on their own.
The models run once; `--report` rebuilds the report from the saved per-frame results.
`just final-test`.
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import yaml
from loguru import logger

from smart_parking.commands.schema import Action, ParsedCommand, PermitTable
from smart_parking.common.config import load_config
from smart_parking.common.log import setup_logging
from smart_parking.loop import TZ, _md, true_status
from smart_parking.stays import PU, apply_stays, changes, runs

CONFIG = Path("configs/local_video_night_3.yaml")
OUT = Path("outputs/final_test")
FRAMES = OUT / "local" / "night_3_frames.csv"
SHORT_S = 30  # stays shorter than this are reported on their own


def read_commands(path: Path) -> list[tuple[datetime, str]]:
    """(time, text) per line of a commands.txt (`2026-11-26 21:05 | allow car 66705`)."""
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            when, text = line.split("|", 1)
            out.append((datetime.fromisoformat(when.strip()).replace(tzinfo=TZ), text.strip()))
    return out


def _time(text: str | None) -> datetime | None:
    return datetime.fromisoformat(text).replace(tzinfo=TZ) if text else None


def intended_table(cfg: dict) -> PermitTable:
    """The owner's intended permit table, from the hand-written meaning of each command."""
    table = PermitTable()
    for c in cfg["commands"]:
        if c["action"] == "allow":
            until = _time(c.get("until"))
            change = ParsedCommand(action=Action.ALLOW, number=str(c["number"]), until=until)
            table.apply(change, confirm=lambda q: True)
    return table


def command_score(proposal: ParsedCommand | None, truth: dict) -> bool:
    """Whether Model C's proposal means what the owner meant (no change for off-topic)."""
    if truth["action"] != "allow":
        return proposal is None
    if proposal is None or proposal.action != Action.ALLOW:
        return False
    if proposal.number != str(truth["number"]):
        return False
    want = _time(truth.get("until"))
    got = proposal.until
    if want is None or got is None:
        return want is None and got is None
    return abs((got - want).total_seconds()) < 60


def run_commands(cfg: dict, pipe, table: PermitTable) -> pd.DataFrame:  # noqa: ANN001
    """Every commands.txt line through Model C; the proposals are accepted into `table`."""
    lines = read_commands(Path(cfg["commands_file"]))
    if len(lines) != len(cfg["commands"]):
        raise SystemExit("commands.txt and the config's intended commands do not match.")
    rows = []
    seen: list[ParsedCommand | None] = []

    def accept(question, change):  # noqa: ANN001, ANN202
        seen[-1] = change
        return change

    for (at, text), truth in zip(lines, cfg["commands"], strict=True):
        seen.append(None)
        reply = pipe.command(text, at, table, accept, OUT / "local" / "feedback.jsonl")
        proposal = seen[-1]
        rows.append({"time": at.strftime("%H:%M"), "command": text,
                     "Model C proposal": proposal.model_dump_json(exclude_none=True)
                     if proposal else "no change", "reply": reply,
                     "meaning right": command_score(proposal, truth)})  # fmt: skip
    return pd.DataFrame(rows)


def stay_rows(d: pd.DataFrame, cfg: dict, start: datetime, truth: PermitTable) -> pd.DataFrame:
    """Each true stay (per bay): the answer at its last parked frame against the right one."""
    from smart_parking.pipeline import clock

    rows = []
    for car in cfg["cars"]:
        for bay in ["left", "right"] if car["bay"] == "both" else [car["bay"]]:
            g = d[(d.bay == bay) & (d.t >= car["from"]) & (d.t < car["to"]) & ~d.blocked]
            last = g.iloc[-1] if len(g) else None
            at = start + timedelta(seconds=float(last.t if last is not None else car["to"]))
            right = true_status(True, car["plate"], at, truth)
            got = last.stay_status if last is not None else "EMPTY"
            occ = g[g.stay_occupied == 1]
            rows.append({
                "bay": bay, "true stay": f"{clock(car['from'])}-{clock(car['to'])}",
                "seconds": car["to"] - car["from"], "note": car.get("note", ""),
                "seen as occupied from": clock(occ.t.min()) if len(occ) else "never",
                "plate found": last.stay_plate if last is not None and last.stay_plate else "no",
                "right answer": right, "system answer": got, "right": got == right,
            })  # fmt: skip
    return pd.DataFrame(rows)


def measures(d: pd.DataFrame, stays: pd.DataFrame) -> pd.DataFrame:
    """Primary and secondary measures (all fixed before the run)."""
    long, short = stays[stays.seconds >= SHORT_S], stays[stays.seconds < SHORT_S]
    scored = d[~d.moving & ~d.blocked]
    cars, empty = scored[scored.truth_occupied == 1], scored[scored.truth_occupied == 0]
    blocked = d[d.blocked]
    authorized = d[d.true_status == "AUTHORIZED"]
    phantom = [
        f"{bay} {a:.0f}-{b:.0f} s"
        for bay, g in d.groupby("bay")
        for a, b, v in runs(g, "stay_occupied")
        if v and not g[(g.t >= a) & (g.t < b)].truth_occupied.any()
    ]
    plate_right = long[long["plate found"] != "no"]
    rows = [
        ("PRIMARY: stays of 30 s or more, answer right", f"{int(long.right.sum())} of {len(long)}"),
        ("stays under 30 s, answer right", f"{int(short.right.sum())} of {len(short)}"),
        ("stays of 30 s or more with a plate found", f"{len(plate_right)} of {len(long)}"),
        ("frames: per-stay answer right (not moving)",
         f"{(d[~d.moving].stay_status == d[~d.moving].true_status).mean():.0%}"),
        ("frames: occupancy right (Model A, not moving or blocked)",
         f"{(scored.occupied == scored.truth_occupied).mean():.0%}"),
        ("frames: empty bay called occupied (Model A)",
         f"{int((empty.occupied == 1).sum())} of {len(empty)}"),
        ("frames: parked car called empty (Model A)",
         f"{int((cars.occupied == 0).sum())} of {len(cars)}"),
        ("frames: plate read right (bays with a car, Model B)",
         f"{int((cars.plate.str.split().str[-1] == cars.true_plate).sum())} of {len(cars)}"),
        ("lens blocked: frames sent to a person",
         f"{int((blocked.stay_status == 'NEEDS_REVIEW').sum())} of {len(blocked)}"),
        ("false alerts: frames alerting on an allowed car",
         f"{int((authorized.stay_status == PU).sum())} of {len(authorized)}"),
        ("stays seen with no car there", f"{len(phantom)}" + (f" ({', '.join(phantom)})"
                                                               if phantom else "")),
        ("notifications to the owner, left + right",
         " + ".join(str(changes(g, "stay_status")) for _, g in d.groupby("bay"))),
    ]  # fmt: skip
    return pd.DataFrame(rows, columns=["measure", "result"])


def write_report(d: pd.DataFrame, cfg: dict, commands: pd.DataFrame, timing: pd.DataFrame) -> None:
    """Write `outputs/final_test/night_3.md` and `night_3.json`."""
    from smart_parking.pipeline import config_start

    start = config_start(cfg)
    stays = stay_rows(d, cfg, start, intended_table(cfg))
    m = measures(d, stays)
    by_slice = []
    for name, g in d[~d.moving].groupby("slice"):
        stay_ok, frame_ok = (g.stay_status == g.true_status), (g.status == g.true_status)
        by_slice.append({"frames": name, "bay checks": len(g),
                         "per-stay answer right": f"{stay_ok.mean():.0%}",
                         "frame-by-frame answer right": f"{frame_ok.mean():.0%}"})  # fmt: skip
    confusion = pd.crosstab(d[~d.moving].true_status, d[~d.moving].stay_status)
    confusion.insert(0, "truth \\ system", confusion.index)
    minutes = d.t.max() / 60
    (OUT / "night_3.md").write_text(
        "# Final test: the whole system on the sealed night video 3\n\n"
        + __doc__.split("\n\n", 1)[1].split("`just")[0].strip()
        + f"\n\nVideo: {minutes:.1f} minutes, {d.t.nunique()} frames, two bays; truth "
        f"**{cfg['truth_status']}**. One night, one spot, one run: indicative, not a "
        "benchmark.\n\n## Measures\n\n"
        + _md(m)
        + "\n\n## Owner commands (Model C)\n\n"
        + _md(commands)
        + "\n\n## Each true stay\n\n"
        + _md(stays)
        + "\n\n## Per slice (frames not moving)\n\n"
        + _md(pd.DataFrame(by_slice))
        + "\n\n## Truth against the system (per-stay answers, frames not moving)\n\n"
        + _md(confusion)
        + ("\n\n## Time per stage (this Mac)\n\n" + _md(timing) if len(timing) else "")
        + "\n"
    )
    long = stays[stays.seconds >= SHORT_S]
    (OUT / "night_3.json").write_text(json.dumps({
        "primary_right": int(long.right.sum()), "primary_stays": len(long),
        "commands_right": int(commands["meaning right"].sum()), "commands": len(commands),
    }, indent=2) + "\n")  # fmt: skip


def main() -> None:
    """Run the final test once (or rebuild its report with --report)."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", action="store_true", help="rebuild from saved results only")
    args = ap.parse_args()
    setup_logging(load_config().logging)
    cfg = yaml.safe_load(CONFIG.read_text())
    if not str(cfg.get("truth_status", "")).startswith("checked by the owner"):
        raise SystemExit("The truth must be checked by the owner before the test is run.")
    (OUT / "local").mkdir(parents=True, exist_ok=True)
    if args.report:
        d = pd.read_csv(FRAMES, keep_default_na=False)
        d["moving"], d["blocked"] = d.moving.astype(str) == "True", d.blocked.astype(str) == "True"
        commands = pd.read_csv(OUT / "local" / "night_3_commands.csv")
        timing = pd.read_csv(OUT / "local" / "night_3_timing.csv")
        write_report(d, cfg, commands, timing)
        logger.info("Final test report rebuilt -> {}", OUT / "night_3.md")
        return
    if FRAMES.exists():
        raise SystemExit("The final test has already been run once; use --report.")
    from smart_parking.pipeline import Pipeline, config_start, frame_table

    pipe = Pipeline(commands=True, deploy="adapted")
    table = PermitTable()
    commands = run_commands(cfg, pipe, table)
    frames, pipe = frame_table(cfg, pipe, table=table, true_table=intended_table(cfg))
    d = apply_stays(frames, config_start(cfg), table)
    d.to_csv(FRAMES, index=False)
    commands.to_csv(OUT / "local" / "night_3_commands.csv", index=False)
    timing = pipe.timing()
    timing.to_csv(OUT / "local" / "night_3_timing.csv", index=False)
    write_report(d, cfg, commands, timing)
    logger.info("Final test -> {}", OUT / "night_3.md")


if __name__ == "__main__":
    main()
