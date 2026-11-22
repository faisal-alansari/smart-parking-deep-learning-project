"""Full loop: the three models working together, as the product runs them.

For each photo of the owner's two bays:
1. Model A (OccupancyCNN, majority of 3 seeds) says whether each bay is occupied;
2. Model B (YOLO11n + reading rules) reads the plate inside each occupied bay;
3. the permit table, filled from the owner's spoken commands by Model C (tiered) and
   confirmed by the owner, is checked at the photo's time.
Each bay ends as EMPTY, AUTHORIZED, POTENTIALLY_UNAUTHORIZED or NEEDS_REVIEW.

`--scenario`: one story on real photos (steps in configs/local_loop.yaml).
`--evaluate`: every bay of the local photo sets against the truth, with blame per stage.
The owner's commands are generated in the owner's own (dev) wording.
Real plates stay on this Mac: details go to outputs/loop/local/ (ignored by Git); the
shared summary, outputs/loop/full_loop.md, holds counts only.
"""

import argparse
import random
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo

import pandas as pd
import yaml
from loguru import logger
from PIL import Image

from smart_parking.commands.dataset import OBJECTS, SEEN, _wrap, say_number, say_time
from smart_parking.commands.owner import arrival_decision, handle
from smart_parking.commands.schema import Action, ParsedCommand, PermitTable, Result
from smart_parking.common.config import load_config
from smart_parking.common.log import setup_logging
from smart_parking.plates.reader import PlateRead

Status = Literal["EMPTY", "AUTHORIZED", "POTENTIALLY_UNAUTHORIZED", "NEEDS_REVIEW"]
STATUSES: list[Status] = ["EMPTY", "AUTHORIZED", "POTENTIALLY_UNAUTHORIZED", "NEEDS_REVIEW"]
TZ = ZoneInfo("Asia/Dubai")
DEFAULT_CONFIG = Path("configs/local_loop.yaml")
OUT = Path("outputs/loop")
SEED = 21
PERMIT_SHARE = 0.4  # visitors the owner gives a timed permit before they arrive
REMOVED_SHARE = 0.1  # visitors given a permit that the owner removes again before they arrive
Decide = Callable[[dict, datetime], Result]


def bay_status(occupied: bool, read: PlateRead | None, at: datetime, table: PermitTable) -> Status:
    """What the system says about one bay: Model A first, then Model B and the table."""
    return arrival_decision(read, at, table) if occupied else "EMPTY"


def true_status(occupied: bool, plate: str, at: datetime, table: PermitTable) -> Status:
    """The right answer for one bay, from the truth labels and the owner's intended table.
    A car with no plate fitted cannot be checked, so the right answer is NEEDS_REVIEW."""
    if not occupied:
        return "EMPTY"
    if not plate:
        return "NEEDS_REVIEW"
    return "AUTHORIZED" if table.find(plate, at) else "POTENTIALLY_UNAUTHORIZED"


def blame(truth_occupied: bool, pred_occupied: bool, truth: Status, system: Status) -> str:
    """The first stage that went wrong: occupancy (A), else the plate (B). Model C cannot be
    blamed here because the owner confirms every change; see `run_commands`."""
    if truth == system:
        return ""
    return "A occupancy" if truth_occupied != pred_occupied else "B plate"


def spoken_number(plate_text: str) -> str:
    """The number the owner says for a plate: its digits without the letter code. Plates with
    a numeric code keep their last five digits (plate numbers have at most five)."""
    return "".join(c for c in plate_text if c.isdigit())[-5:]


def say_command(
    rng: random.Random, action: str, number: str, now: datetime, timed: bool
) -> tuple[str, datetime | None]:
    """An owner command in the owner's own (dev) wording, and the end time it means."""
    template = rng.choice(SEEN[action])
    parts = [template.format(obj=rng.choice(OBJECTS).format(n=say_number(rng, number)[0]))]
    until = None
    if action == "allow" and rng.random() < 0.3:  # a bay is sometimes said (and ignored)
        parts.append(rng.choice(SEEN["bay"]).format(b=rng.choice(["1", "2", "one", "two"])))
    if action == "allow" and timed:
        phrase, until = say_time(rng, now)
        parts.append(phrase)
    return _wrap(rng, "dev", " ".join(parts), not template.startswith("{obj}")), until


@dataclass
class Command:
    at: datetime
    text: str
    intended: ParsedCommand  # what the owner meant


def plan_commands(permanent: list[str], arrivals: dict[str, datetime], seed: int = SEED
                  ) -> list[Command]:  # fmt: skip
    """The owner's commands: the permanent list first, then for some visitors a timed permit
    said 15 minutes to 30 hours before their first arrival (so some end before it), or a
    permit removed again before they arrive."""
    rng = random.Random(seed)
    start = min(arrivals.values()) - timedelta(days=2)
    cmds = []
    for n in permanent:
        text, _ = say_command(rng, "allow", n, start, timed=False)
        cmds.append(Command(start, text, ParsedCommand(action=Action.ALLOW, number=n)))
    for n, first in sorted(arrivals.items()):
        r = rng.random()
        if n in permanent or r >= PERMIT_SHARE + REMOVED_SHARE:
            continue
        at = (first - timedelta(minutes=rng.randint(15, 30 * 60))).replace(second=0)
        timed = r < PERMIT_SHARE
        text, until = say_command(rng, "allow", n, at, timed)
        cmds.append(Command(at, text, ParsedCommand(action=Action.ALLOW, number=n, until=until)))
        if not timed:
            gone = (at + (first - at) / 2).replace(second=0, microsecond=0)
            text, _ = say_command(rng, "remove", n, gone, timed=False)
            cmds.append(Command(gone, text, ParsedCommand(action=Action.REMOVE, number=n)))
    return sorted(cmds, key=lambda c: c.at)


@dataclass
class Tables:
    truth: PermitTable  # what the owner meant
    confirmed: PermitTable  # the product: Model C proposes, the owner confirms or fixes
    unchecked: PermitTable  # Model C alone: every proposal applied, questions dropped
    log: pd.DataFrame


def run_commands(cmds: list[Command], decide: Decide, feedback: Path) -> Tables:
    """Send each command through Model C. The simulated owner accepts a right proposal,
    fixes a wrong one, and says the command again when asked a question."""
    truth, confirmed, unchecked = PermitTable(), PermitTable(), PermitTable()
    rows = []
    for c in cmds:
        truth.apply(c.intended, confirm=lambda q: True)
        result = decide({"text": c.text}, c.at)
        if isinstance(result, ParsedCommand):
            unchecked.apply(result, confirm=lambda q: True)
        shown: list[ParsedCommand] = []

        def owner(question: str, proposal: ParsedCommand, c: Command = c,
                  shown: list = shown) -> ParsedCommand:  # fmt: skip
            shown.append(proposal)
            return c.intended

        def model_c(row: dict, now: datetime, result: Result = result) -> Result:
            return result  # already decided above

        reply = handle(c.text, c.at, model_c, confirmed, owner, feedback)
        if not shown:  # asked a question (or "unsupported"): the owner says it again clearly
            confirmed.apply(c.intended, confirm=lambda q: True)
        path = ("accepted" if shown[0] == c.intended else "fixed by owner") if shown else "asked"
        rows.append({"at": c.at, "command": c.text, "path": path, "reply": reply,
                     "model_c": type(result).__name__})  # fmt: skip
    return Tables(truth, confirmed, unchecked, pd.DataFrame(rows))


# --- Photos through Models A and B -------------------------------------------------------


def photo_time(path: Path, fallback: str) -> datetime:
    """When the photo was taken (EXIF), else the set's fallback time."""
    stamp = Image.open(path).getexif().get(306)
    when = datetime.strptime(stamp, "%Y:%m:%d %H:%M:%S") if stamp else None
    return (when or datetime.fromisoformat(fallback)).replace(tzinfo=TZ)


def run_models(photo_set: dict) -> pd.DataFrame:
    """Models A and B on every bay of one photo set (the local-pilot pipeline)."""
    from smart_parking.occupancy import local_pilot as lp  # loads YOLO; import when needed

    project = load_config()
    pilot = yaml.safe_load(Path(photo_set["config"]).read_text())
    lp.prepare_photos(Path(pilot["raw_dir"]), Path(pilot["photo_dir"]))
    images, rows, _ = lp.crop_bays(pilot, project.occupancy.input_size)
    res = lp.read_bay_plates(pilot, project.plates, lp.score(project.occupancy, images, rows))
    res["set"] = Path(photo_set["config"]).stem
    times = [photo_time(Path(pilot["photo_dir"]) / f"{p}.jpg", photo_set["fallback_time"])
             for p in res["photo"]]  # fmt: skip
    res["at"] = pd.Series(times, index=res.index, dtype=object)  # plain datetimes
    return res


def plate_read(row) -> PlateRead | None:  # noqa: ANN001  (a DataFrame row)
    """Model B's read for one bay, rebuilt from the pipeline's columns."""
    if not row.pred or row.bay_read in ("", "none"):
        return None
    emirate, text = row.bay_read.rsplit(" ", 1)
    return PlateRead(
        emirate=None if emirate == "None" else emirate, text=text,
        confidence=float(row.bay_conf or 0), box=(0, 0, 0, 0), reason=None,
        decision="READ" if row.bay_decision == "READ" else "NEEDS_REVIEW",
    )  # fmt: skip


def plate_text(true_plate: str) -> str:
    return true_plate.rsplit(" ", 1)[-1] if true_plate else ""


def judge(res: pd.DataFrame, tables: Tables) -> pd.DataFrame:
    """Truth and system status of every bay, with the confirmed and the unchecked table."""
    out = res.copy()
    truth, system, alone, who = [], [], [], []
    for r in res.itertuples():
        read = plate_read(r)
        t = true_status(bool(r.truth), plate_text(r.true_plate), r.at, tables.truth)
        s = bay_status(bool(r.pred), read, r.at, tables.confirmed)
        a = bay_status(bool(r.pred), read, r.at, tables.unchecked)
        truth.append(t)
        system.append(s)
        alone.append(a)
        who.append(blame(bool(r.truth), bool(r.pred), t, s))
    out["true_status"], out["status"], out["status_no_owner_check"] = truth, system, alone
    out["blame"] = who
    return out


# --- Reports ----------------------------------------------------------------------------


def _md(df: pd.DataFrame) -> str:
    lines = ["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)]
    lines += ["| " + " | ".join(str(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join(lines)


def key_numbers(j: pd.DataFrame, col: str = "status") -> dict[str, str]:
    """The numbers that matter to the owner, for one status column."""
    pu, t = "POTENTIALLY_UNAUTHORIZED", j["true_status"]
    s = j[col]
    unauth = s[t == pu]
    return {
        "bays": str(len(j)),
        "right": f"{int((s == t).sum())} ({(s == t).mean():.0%})",
        "false alerts (alert on a car that is not unauthorized)": str(
            int(((s == pu) & (t != pu)).sum())
        ),
        "unauthorized cars": str(len(unauth)),
        "  alerted": str(int((unauth == pu).sum())),
        "  sent to a person": str(int((unauth == "NEEDS_REVIEW").sum())),
        "  missed (bay called empty)": str(int((unauth == "EMPTY").sum())),
        "  let through as AUTHORIZED": str(int((unauth == "AUTHORIZED").sum())),
        "sent to a person (NEEDS_REVIEW)": str(int((s == "NEEDS_REVIEW").sum())),
        "  of which not needed": str(int(((s == "NEEDS_REVIEW") & (t != "NEEDS_REVIEW")).sum())),
    }


def summary(j: pd.DataFrame, tables: Tables) -> str:
    """Counts only (no plates): safe to share."""
    groups = [("all", j)] + [(f"{k[0]}, {k[1]}", g) for k, g in j.groupby(["set", "light"])]
    keys = pd.DataFrame({name: key_numbers(g) for name, g in groups})
    keys.insert(0, "measure", keys.index)
    matrix = pd.crosstab(j["true_status"], j["status"]).reindex(
        index=STATUSES, columns=STATUSES, fill_value=0
    )
    matrix.insert(0, "truth \\ system", matrix.index)
    blames = j.loc[j["blame"] != "", "blame"].value_counts()
    paths = tables.log["path"].value_counts()
    alone = pd.DataFrame(
        {
            "with owner check": key_numbers(j),
            "Model C alone (no owner check)": key_numbers(j, "status_no_owner_check"),
        }
    )
    alone.insert(0, "measure", alone.index)
    c_only = int(((j["status"] == j["true_status"])
                  & (j["status_no_owner_check"] != j["true_status"])).sum())  # fmt: skip
    return (
        "# Full loop on the owner's photos (Models A + B + C)\n\n"
        f"{j['photo'].nunique()} photos, {len(j)} bays ({', '.join(sorted(j['set'].unique()))}). "
        "Each photo is treated as an arrival at the owner's two bays, at the time it was taken. "
        f"The permit table comes from {len(tables.log)} owner commands, generated in the "
        "owner's own wording and sent through Model C (tiered); the simulated owner accepts a "
        "right proposal, fixes a wrong one and repeats a command when asked. Plates stay "
        "local, so this page shows counts only. Small sample: indicative only.\n\n"
        "## Key numbers\n\n" + _md(keys) + "\n\n"
        "## Truth against the system (all bays)\n\n" + _md(matrix) + "\n\n"
        "## Which stage caused each wrong answer\n\n"
        + (_md(blames.rename_axis("stage").reset_index(name="bays")) if len(blames) else "None.")
        + "\n\nModel C cannot cause a wrong answer here: the owner checks every change.\n\n"
        "## Model C and the owner's check\n\n"
        + _md(paths.rename_axis("command path").reset_index(name="commands"))
        + "\n\n"
        + _md(alone)
        + "\n\n"
        f"Bays the owner's check saved (wrong without it, right with it): {c_only}.\n"
    )


def details(j: pd.DataFrame, tables: Tables) -> str:
    """Every bay and command, with real plates: local only."""
    cols = ["set", "photo", "light", "bay", "at", "truth", "pred", "true_plate", "bay_read",
            "bay_decision", "true_status", "status", "status_no_owner_check", "blame"]  # fmt: skip
    wrong = j[j["status"] != j["true_status"]]
    return (
        "# Full loop details (LOCAL ONLY: real plates)\n\n## Wrong bays\n\n"
        + _md(wrong[cols])
        + "\n\n## Owner commands\n\n"
        + _md(tables.log)
        + "\n"
    )


def evaluate(loop: dict, decide: Decide) -> None:
    res = pd.concat([run_models(s) for s in loop["sets"]], ignore_index=True)
    arrivals: dict[str, datetime] = {}
    for r in res[res["true_plate"] != ""].itertuples():
        n = spoken_number(plate_text(r.true_plate))
        arrivals[n] = min(arrivals.get(n, r.at), r.at)
    (OUT / "local").mkdir(parents=True, exist_ok=True)
    feedback = OUT / "local" / "feedback.jsonl"
    feedback.unlink(missing_ok=True)
    tables = run_commands(plan_commands(loop["permanent"], arrivals), decide, feedback)
    j = judge(res, tables)
    j.to_csv(OUT / "local" / "bays.csv", index=False)
    (OUT / "local" / "details.md").write_text(details(j, tables))
    (OUT / "full_loop.md").write_text(summary(j, tables))
    logger.info("Full loop: {} of {} bays right -> {}", int((j.status == j.true_status).sum()),
                len(j), OUT / "full_loop.md")  # fmt: skip


def scenario(loop: dict, decide: Decide) -> None:
    """The step-by-step story: commands change the table, photos are checked against it."""
    res = pd.concat([run_models(s) for s in loop["sets"]], ignore_index=True)
    table = PermitTable()
    (OUT / "local").mkdir(parents=True, exist_ok=True)
    feedback = OUT / "local" / "feedback_scenario.jsonl"
    feedback.unlink(missing_ok=True)
    lines = ["# Full-loop scenario (LOCAL ONLY: real plates)", "",
             "Real photos and all three real models; the owner's answers are scripted (yes). "
             "Times are scenario times.", "",
             "| time | input | system | right? |", "|---|---|---|---|"]  # fmt: skip
    for step in loop["scenario"]:
        at = datetime.fromisoformat(step["at"]).replace(tzinfo=TZ)
        if "say" in step:
            asked: list[str] = []
            reply = handle(step["say"], at, decide, table,
                           lambda q, c, asked=asked: asked.append(q) or c, feedback)  # fmt: skip
            said = f"asks: {asked[0]} owner: yes. " if asked else ""
            lines.append(f'| {at:%H:%M} | owner: "{step["say"]}" | {said}{reply} | |')
            continue
        for r in res[res["photo"] == step["photo"]].itertuples():
            read = plate_read(r)
            s = bay_status(bool(r.pred), read, at, table)
            t = true_status(bool(r.truth), plate_text(r.true_plate), at, table)
            seen = f"plate {read.text} ({read.decision})" if read else "no plate read"
            occ = "occupied" if r.pred else "empty"
            right = "yes" if s == t else f"no ({t})"
            lines.append(f"| {at:%H:%M} | camera {r.photo} {r.bay} bay | {occ}"
                         f"{', ' + seen if r.pred else ''} -> **{s}** | {right} |")  # fmt: skip
    (OUT / "local" / "scenario.md").write_text("\n".join(lines) + "\n")
    logger.info("Scenario -> {}", OUT / "local" / "scenario.md")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    ap.add_argument("--scenario", action="store_true")
    ap.add_argument("--evaluate", action="store_true")
    args = ap.parse_args()
    project = load_config()
    setup_logging(project.logging)
    loop = yaml.safe_load(args.config.read_text())
    from smart_parking.commands.score import PARSERS  # loads Model C's libraries

    decide = PARSERS["tiered"].load(project.commands).decide
    if args.scenario:
        scenario(loop, decide)
    if args.evaluate:
        evaluate(loop, decide)


if __name__ == "__main__":
    main()
