"""Score a Model C candidate on a command set.

Every candidate only extracts pieces; the shared rules (`commands.rules.finish`) do the
rest, so all candidates are compared on the same footing.

- exact: the result matches exactly (status PROPOSED / NEEDS_REVIEW / UNSUPPORTED, the
  reason, and the proposed action, number and end time). Primary metric.
- dangerous: a permit change is put to the owner (proposed, or kept with a one-digit
  review) and the result is not the expected one; owner confirmation is the last guard.
- needless_question: NEEDS_REVIEW or UNSUPPORTED where a clear change was expected.
- field accuracy (action, number, until) where a change was expected and one was made.

Usage: `just command-score <parser> <split>`; the test split needs `--final` (except
for the oracle, which only checks the answer key and the shared rules).
"""

import argparse
import json
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

import pandas as pd
from loguru import logger

from smart_parking.commands import adapters, baseline, tiers
from smart_parking.commands.dataset import describe
from smart_parking.commands.rules import finish
from smart_parking.commands.schema import (
    Extraction,
    NeedsReview,
    ParsedCommand,
    Result,
    Unsupported,
)
from smart_parking.common.config import load_config

Parser = Callable[[dict], Extraction]
PARSERS: dict[str, Parser] = {
    "oracle": lambda row: Extraction(**row["oracle"]),  # perfect extraction: the ceiling
    "rules": lambda row: baseline.extract(row["text"]),
    "smollm2": adapters.Lazy(adapters.SmolLM),
    "flan-t5": adapters.Lazy(adapters.FlanT5),
    "gliner-minilm": adapters.Lazy(adapters.GlinerMiniLM),
    "checked": adapters.Lazy(adapters.Checked),  # GLiNER + MiniLM, every change checked
    "tiered": adapters.Lazy(tiers.Tiered),  # Model C as used: fixed form first, then checked
}
FIELDS = ("action", "number", "until")


def load_set(path: Path) -> list[dict]:
    """Read a JSONL command set, skipping blank lines."""
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _proposal(cmd: ParsedCommand | None) -> dict | None:
    if cmd is None:
        return None
    until = cmd.until.isoformat() if cmd.until else None
    return {"action": cmd.action.value, "number": cmd.number, "until": until}


def outcome(result: Result) -> dict:
    """A result in the answer-key format (see `dataset.outcome`)."""
    if isinstance(result, Unsupported):
        return {"status": "UNSUPPORTED", "reason": None, "proposal": None}
    if isinstance(result, NeedsReview):
        return {"status": "NEEDS_REVIEW", "reason": result.reason,
                "proposal": _proposal(result.proposal)}  # fmt: skip
    return {"status": "PROPOSED", "reason": None, "proposal": _proposal(result)}


def run(parser: Parser, rows: list[dict]) -> pd.DataFrame:
    """Run a parser on every command; one row per command with its checks and time."""
    out = []
    target = parser.load() if isinstance(parser, adapters.Lazy) else parser  # load not timed
    decide = getattr(target, "decide", None)  # parsers with their own safety checks
    for row in rows:
        now = datetime.fromisoformat(row["now"])
        start = time.perf_counter()
        result = decide(row, now) if decide else finish(parser(row), now)
        ms = (time.perf_counter() - start) * 1000
        got = outcome(result)
        want = row["expected"]
        wanted_change = want["status"] == "PROPOSED"
        made, wanted = got["proposal"], want["proposal"]
        out.append(
            {
                "id": row["id"],
                "text": row["text"],
                "expected": describe(want),
                "got": describe(got),
                "exact": got == want,
                "dangerous": made is not None and got != want,
                "needless_question": wanted_change and got["status"] != "PROPOSED",
                **{f"{f}_ok": bool(made and wanted and made[f] == wanted[f]) for f in FIELDS},
                "wanted_change": wanted_change,
                "ms": ms,
                **{f"tag_{k}": v for k, v in row["tags"].items()},
            }
        )
    return pd.DataFrame(out)


def summarise(d: pd.DataFrame) -> dict:
    """Share exact, dangerous and needless questions, and field accuracy on wanted changes."""
    cmd = d[d.wanted_change]
    return {
        "n": len(d),
        "exact": d.exact.mean(),
        "dangerous": d.dangerous.mean(),
        "needless_question": cmd.needless_question.mean() if len(cmd) else None,
        **{f"{f}_acc": cmd[f"{f}_ok"].mean() if len(cmd) else None for f in FIELDS},
    }


def report(d: pd.DataFrame) -> str:
    """Markdown table of the scores for all commands and each tag, plus the errors."""
    groups = {"all": d}
    tags = (("tag_kind", "kind"), ("tag_reason", "reason"), ("tag_wording", "wording"),
            ("tag_has_bay", "bay said"), ("tag_noisy", "slip"))  # fmt: skip
    for tag, label in tags:
        if tag in d:
            for value, g in d.groupby(tag, dropna=True):
                groups[f"{label}={value}"] = g
    rows = []
    for name, g in groups.items():
        s = summarise(g)
        cells = [s["exact"], s["dangerous"], s["needless_question"]]
        cells += [s[f"{f}_acc"] for f in FIELDS]
        shown = " | ".join("-" if c is None else f"{c:.3f}" for c in cells)
        rows.append(f"| {name} | {s['n']} | {shown} |")
    head = (
        "| slice | n | exact | dangerous | needless question | action | number | until |\n"
        "|---|---|---|---|---|---|---|---|\n"
    )
    wrong = d[~d.exact][["id", "text", "expected", "got"]]
    errors = "\n".join(f"- {r.id}: \"{r.text}\" expected {r.expected}; got {r.got}"
                       for r in wrong.itertuples())  # fmt: skip
    return head + "\n".join(rows) + "\n\n## Errors\n\n" + (errors or "None.") + "\n"


def main() -> None:
    """Run the documented entry point with contextual, rotating application logs."""
    from smart_parking.common.log import setup_logging

    setup_logging(load_config().logging)
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("parser", choices=sorted(PARSERS))
    ap.add_argument(
        "split", choices=["dev", "check", "confirm", "confirm2", "confirm3", "confirm4", "test"]
    )
    ap.add_argument("--final", action="store_true", help="allow the frozen test set")
    ap.add_argument("--as-tested", action="store_true",
                    help="the version run in the one final test (no day-word check), to "
                    "reproduce the reported test numbers")  # fmt: skip
    args = ap.parse_args()
    # The oracle only checks the answer key and shared rules, so it may read the test set.
    if args.split == "test" and not args.final and args.parser != "oracle":
        raise SystemExit("The test set is frozen: pass --final only for the final comparison.")
    cfg = load_config().commands
    if args.as_tested and isinstance(PARSERS[args.parser], adapters.Lazy):
        cfg = load_config().commands.model_copy(update={"day_word_check": False})
        PARSERS[args.parser].load(cfg)  # loaded once with the tested settings
    d = run(PARSERS[args.parser], load_set(cfg.data_dir / f"{args.split}.jsonl"))
    out = cfg.results_dir / f"{args.parser}_{args.split}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    speed = f"Time per command: {d.ms.mean():.0f} ms mean, {d.ms.quantile(0.95):.0f} ms p95.\n\n"
    out.write_text(f"# Model C: {args.parser} on {args.split}\n\n" + speed + report(d))
    logger.info("{} on {}: exact {:.3f}, dangerous {:.3f}, {:.0f} ms -> {}", args.parser,
                args.split, d.exact.mean(), d.dangerous.mean(), d.ms.mean(), out)  # fmt: skip


if __name__ == "__main__":
    main()
