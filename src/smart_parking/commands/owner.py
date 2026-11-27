"""Model C connected to the permit table: the owner's command, confirmation and feedback.

`handle` sends a command through Model C. A proposed change is shown to the owner as a
question; the owner accepts it, rejects it and fixes the fields, or rejects it. Only then does
the permit table change, and every decision is saved as a `HumanFeedback` record (the
feedback records, and a measure of Model C on real commands). Unclear commands get
a question; other requests get the "unsupported" reply. Nothing changes without the owner.

`arrival_decision` joins the three modalities: a plate read by Model B (visual), the permit
table filled through Model C (text) and the time (tabular check).

Demo (made-up plate, scripted owner answers): `just command-demo`.
"""

import argparse
from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo

from loguru import logger
from pydantic import BaseModel

from smart_parking.commands.schema import NeedsReview, ParsedCommand, PermitTable, Result
from smart_parking.common.config import load_config
from smart_parking.plates.reader import PlateRead

# The owner sees the question and the proposed change, and answers with the change to apply:
# the same one (accept), a fixed one (reject and correct), or None (reject).
Review = Callable[[str, ParsedCommand], ParsedCommand | None]
Decision = Literal["AUTHORIZED", "POTENTIALLY_UNAUTHORIZED", "NEEDS_REVIEW"]


class HumanFeedback(BaseModel):
    """One owner decision on a change Model C proposed."""

    at: datetime
    command: str
    proposed: ParsedCommand
    accepted: bool
    corrected: ParsedCommand | None = None  # the owner's fixed version, if rejected and fixed


def handle(
    text: str, now: datetime, decide: Callable[[dict, datetime], Result], table: PermitTable,
    review: Review, feedback: Path,
) -> str:  # fmt: skip
    """Run one command end to end and say what happened, in plain words."""
    result = decide({"text": text}, now)
    proposal = result if isinstance(result, ParsedCommand) else None
    question = table.confirmation(result) if proposal else ""
    if isinstance(result, NeedsReview) and result.proposal:  # a one-digit number: check it
        proposal, question = result.proposal, result.question
    if proposal is None:
        reply = result.question if isinstance(result, NeedsReview) else result.message
        logger.bind(command=text).info("No change; reply: {}", reply)
        return reply
    change = review(question, proposal)
    fixed = change if change not in (None, proposal) else None
    record = HumanFeedback(
        at=now, command=text, proposed=proposal, accepted=change == proposal, corrected=fixed
    )
    feedback.parent.mkdir(parents=True, exist_ok=True)
    with feedback.open("a") as f:
        f.write(record.model_dump_json() + "\n")
    if change is None:
        logger.bind(command=text).info("Owner rejected: no change")
        return "Rejected: nothing changed."
    changed = table.apply(change, confirm=lambda q: True)  # the owner has just answered
    logger.bind(command=text).info("Applied {} (changed: {})", change, changed)
    return f"Done: {table.confirmation(change).rstrip('?')}." if changed else "Nothing to change."


def arrival_decision(read: PlateRead | None, at: datetime, table: PermitTable) -> Decision:
    """The permit check for a car in one of the owner's bays."""
    if read is None or read.decision == "NEEDS_REVIEW":
        return "NEEDS_REVIEW"  # no clear plate: a person looks, nothing is claimed
    return "AUTHORIZED" if table.find(read.text, at) else "POTENTIALLY_UNAUTHORIZED"


def demo() -> str:
    """The same arrival before, during and after a permit, and the other owner paths."""
    from smart_parking.commands.score import PARSERS

    cfg = load_config().commands
    model_c = PARSERS["tiered"].load(cfg)
    tz = ZoneInfo("Asia/Dubai")
    now = datetime(2026, 11, 22, 9, 30, tzinfo=tz)
    feedback = cfg.results_dir / "feedback_demo.jsonl"
    feedback.unlink(missing_ok=True)
    table = PermitTable()
    read = PlateRead(emirate="Dubai", text="G12345", confidence=0.9, decision="READ",
                     reason=None, box=(0, 0, 1, 1))  # made-up plate  # fmt: skip
    unclear = read.model_copy(update={"decision": "NEEDS_REVIEW", "reason": "low_confidence"})
    lines = ["# Model C demo: owner commands and the permit table", "",
             "Made-up plate Dubai G12345; the owner's answers are scripted.", "",
             "| step | owner / camera | system |", "|---|---|---|"]  # fmt: skip

    def step(who: str, what: str) -> None:
        lines.append(f"| {len(lines) - 5} | {who} | {what} |")

    def yes(question: str, change: ParsedCommand) -> ParsedCommand:
        step("system asks", question)
        return change

    def fix_number(question: str, change: ParsedCommand) -> ParsedCommand:
        step("system asks", question)
        fixed = change.model_copy(update={"number": "12345"})
        step("owner", f"No: the number is {fixed.number}")
        return fixed

    def run(text: str, at: datetime, review: Review = yes) -> None:
        step("owner says", f'"{text}"')
        step("system", handle(text, at, model_c.decide, table, review, feedback))

    def arrive(at: datetime, plate: PlateRead = read) -> None:
        shown = f"plate {plate.text}" if plate.decision == "READ" else "plate unclear"
        step(f"camera {at:%H:%M}", f"car in bay 1, {shown} -> "
             f"**{arrival_decision(plate, at, table)}**")  # fmt: skip

    arrive(now)
    run("allow car 12345 until 6 pm", now)  # the owner's fixed form (tier 1)
    arrive(now + timedelta(minutes=5))
    arrive(now.replace(hour=18, minute=30))  # the permit has expired
    run("please let car number 12345 in until tomorrow", now.replace(hour=18, minute=35))
    run("okay let car 12345 in till 9 pm", now.replace(hour=18, minute=36))  # models (tier 2)
    arrive(now.replace(hour=18, minute=40))
    run("remove car 12345", now.replace(hour=19))
    arrive(now.replace(hour=19, minute=5))
    run("add car 1234 till tomorrow", now.replace(hour=19, minute=10), review=fix_number)
    arrive(now.replace(hour=19, minute=15), unclear)  # an unclear read stays for review
    run("add 12345 until 6", now.replace(hour=19, minute=20))  # AM or PM? asked, not guessed
    run("what's the weather today", now.replace(hour=19, minute=25))
    records = feedback.read_text().splitlines() if feedback.exists() else []
    lines += ["", f"Feedback records saved: {len(records)} (`{feedback}`)."]
    return "\n".join(lines) + "\n"


def main() -> None:
    """Run the documented entry point with contextual, rotating application logs."""
    from smart_parking.common.config import load_config
    from smart_parking.common.log import setup_logging

    setup_logging(load_config().logging)
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()
    if args.demo:
        out = load_config().commands.results_dir / "demo.md"
        out.write_text(demo())
        logger.info("Demo -> {}", out)


if __name__ == "__main__":
    main()
