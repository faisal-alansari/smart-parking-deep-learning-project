"""Model C as used: the owner's fixed form first, then the checked models, then the owner.

Tier 1: a command in the owner's fixed form ("add 5055", "remove 5055", "allow car 5055 for
2 days", "add 5055 until 6 pm") is read by a fixed pattern, with no model. It accepts only
allow / add / remove / delete, one plate number (digits or digit words), and an optional
time after "until", "till" or "for", so nothing else can match by accident; a bay word or
"and" sends the command on to tier 2.
Tier 2: anything else goes to the checked models (`adapters.Checked`).
Tier 3: the owner. Every change is shown for a yes, and unclear commands get a question.
"""

import re
from datetime import datetime

from smart_parking.commands.adapters import Checked
from smart_parking.commands.rules import NUMBER_WORDS, finish
from smart_parking.commands.schema import Action, Extraction, Result
from smart_parking.common.config import CommandsConfig

_NUM = r"(?:\d+|" + "|".join(sorted(NUMBER_WORDS, key=len, reverse=True)) + r")"
FIXED = re.compile(
    rf"(?:please |okay |hey )?(?P<verb>allow|add|remove|delete) (?:car |plate |number )?"
    rf"(?:number )?(?P<num>{_NUM}(?: {_NUM})*)(?: (?P<time>(?:until|till|for) [a-z0-9: ]+?))?"
    r"(?: please| thanks)?"
)


def fixed_form(text: str) -> Extraction | None:
    """The command's pieces if it is in the owner's fixed form, else None."""
    t = re.sub(r"[.!?,]+$", "", text.strip().lower())
    m = FIXED.fullmatch(t)
    if not m or "bay" in t or " and " in f" {m['num']} ":
        return None
    action = Action.REMOVE if m["verb"] in ("remove", "delete") else Action.ALLOW
    return Extraction(action=action, numbers=[m["num"]], time=m["time"])


class Tiered:
    """Tier 1 (fixed form) when it matches, else tier 2 (`Checked`)."""

    name = "tiered"

    def __init__(self, cfg: CommandsConfig) -> None:
        self.checked = Checked(cfg)
        self.models = self.checked.models
        self.last_tier = 0

    def decide(self, row: dict, now: datetime) -> Result:
        """Tier 1's result for a fixed-form command, else tier 2's checked decision."""
        ex = fixed_form(row["text"])
        self.last_tier = 1 if ex else 2
        return finish(ex, now) if ex else self.checked.decide(row, now)

    def __call__(self, row: dict) -> Extraction:
        """The fixed-form extraction, else tier 2's extraction."""
        return fixed_form(row["text"]) or self.checked(row)
