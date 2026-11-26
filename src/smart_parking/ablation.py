"""Step 4: what each part adds to the full loop. Remove one at a time and rerun.

Same local bays, same truth and same owner commands as `just full-loop`:
- no Model A: every bay is treated as occupied, so a plate is read in every bay;
- no Model B: an occupied bay cannot be identified, so it always goes to a person;
- no Model C: the commands are read by the fixed rule parser instead, or not at all
  (an empty permit table);
- no time check (the tabular part): permits never end;
- Model C without the owner's check: every proposal is applied, questions are dropped.
Counts only (no plates): `outputs/loop/ablation.md`.
"""

import argparse
from pathlib import Path

import pandas as pd
import yaml
from loguru import logger

from smart_parking.commands import baseline
from smart_parking.commands.rules import finish
from smart_parking.commands.schema import Permit, PermitTable
from smart_parking.common.config import load_config
from smart_parking.common.log import setup_logging
from smart_parking.loop import (
    DEFAULT_CONFIG,
    OUT,
    Status,
    Tables,
    _md,
    bay_status,
    first_arrivals,
    judge,
    key_numbers,
    plan_commands,
    plate_read,
    run_commands,
    run_models,
)


def no_end_times(table: PermitTable) -> PermitTable:
    """The same permits with their end times dropped (no time check)."""
    out = PermitTable()
    out.permits = {n: Permit(number=n) for n in table.permits}
    return out


def statuses(res: pd.DataFrame, table: PermitTable, plates: bool = True) -> list[Status]:
    """System status of every bay; without plates, an occupied bay goes to a person."""
    if not plates:
        return ["NEEDS_REVIEW" if r.pred else "EMPTY" for r in res.itertuples()]
    return [bay_status(bool(r.pred), plate_read(r), r.at, table) for r in res.itertuples()]


def rules_decide(row: dict, now) -> object:  # noqa: ANN001
    """The fixed rule parser (Model C's baseline) in Model C's place."""
    return finish(baseline.extract(row["text"]), now)


def owner_effort(tables: Tables) -> str:
    """Owner effort as 'accepted / fixed by owner / asked' counts from the command log."""
    paths = tables.log["path"].value_counts()
    return " / ".join(f"{int(paths.get(p, 0))}" for p in ("accepted", "fixed by owner", "asked"))


def ablate(loop: dict, decide) -> str:  # noqa: ANN001
    """Key numbers for the full system and each variant with one part removed, as Markdown."""
    sets = loop["sets"]
    res = pd.concat([run_models(s) for s in sets], ignore_index=True)
    res_all = pd.concat([run_models(s, all_occupied=True) for s in sets], ignore_index=True)
    cmds = plan_commands(loop["permanent"], first_arrivals(res))
    scratch = OUT / "local" / "ablation_feedback.jsonl"
    scratch.parent.mkdir(parents=True, exist_ok=True)
    scratch.unlink(missing_ok=True)
    full = run_commands(cmds, decide, scratch)
    rules = run_commands(cmds, rules_decide, scratch)
    scratch.unlink(missing_ok=True)
    j = judge(res, full)  # truth and the full system
    variants = {
        "full system": j["status"],
        "no Model A (every bay occupied)": statuses(res_all, full.confirmed),
        "no Model B (no plate reading)": statuses(res, full.confirmed, plates=False),
        "no Model C: rule parser, owner checks": statuses(res, rules.confirmed),
        "no Model C: rule parser, no owner check": statuses(res, rules.unchecked),
        "no Model C: no commands (empty table)": statuses(res, PermitTable()),
        "Model C, no owner check": j["status_no_owner_check"],
        "no time check (permits never end)": statuses(res, no_end_times(full.confirmed)),
    }
    cols = {}
    for name, s in variants.items():
        v = j[["true_status"]].copy()
        v["status"] = list(s)
        cols[name] = key_numbers(v)
    table = pd.DataFrame(cols).T
    table.insert(0, "variant", table.index)
    effort = pd.DataFrame(
        [
            {"command reader": "Model C (tiered)", "accepted / fixed / asked": owner_effort(full)},
            {"command reader": "rule parser", "accepted / fixed / asked": owner_effort(rules)},
        ]
    )
    return (
        "# Full loop: remove one part at a time (step 4)\n\n"
        f"{res['photo'].nunique()} local photos, {len(res)} bays, {len(cmds)} generated owner "
        "commands; the same truth for every row (from the owner's intended permits). Counts "
        "only. Small sample: indicative only.\n\n"
        + _md(table)
        + "\n\n## Owner effort for the commands (of "
        + f"{len(cmds)})\n\n"
        + _md(effort)
        + "\n\n`asked`: the system asked a question, so the owner had to say the command again. "
        "With the owner's check, both readers end with the right table; the difference is the "
        "owner's effort and, without the check, wrong permits.\n\n"
        "Caution: the commands are generated in the dev wording, the same wording the rule "
        "parser was written from, so this favours the rule parser. On the frozen test's new "
        "wording, the rule parser put 3 wrong changes to the owner against Model C's 1 "
        "(`outputs/commands/final_test.md`).\n"
    )


def main() -> None:
    """Load Model C, run the ablation on the loop config and write `ablation.md`."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = ap.parse_args()
    project = load_config()
    setup_logging(project.logging)
    from smart_parking.commands.score import PARSERS  # loads Model C's libraries

    decide = PARSERS["tiered"].load(project.commands).decide
    out = OUT / "ablation.md"
    out.write_text(ablate(yaml.safe_load(args.config.read_text()), decide))
    logger.info("Ablation -> {}", out)


if __name__ == "__main__":
    main()
