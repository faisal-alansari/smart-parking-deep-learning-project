"""Contract for owner commands and the one in-memory permit table (final scope 2026-11-21).

The owner speaks a short command; speech-to-text happens before Model C. A candidate
model only fills an `Extraction` (raw text pieces). Fixed rules (`commands.rules`)
turn it into one of three results:

- `ParsedCommand`: a clear permit change, proposed to the owner;
- `NeedsReview` (NEEDS_REVIEW): something essential is unclear, so ask; never guess;
- `Unsupported`: the owner asked for something other than allow or remove.

Model C only proposes. The permit table changes only after the owner confirms.

Scope: two actions (ALLOW adds or replaces a permit, REMOVE deletes it), the plate
number only (no emirate or code: Model B already stores the full plate), and an
optional end time (none means a permanent permit). Permits are not tied to a bay: an
allowed car may use either of the owner's two bays, and a bay said in a command is
ignored.
"""

from collections.abc import Callable, Iterable
from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Action(StrEnum):
    """A permit change: allow or remove a car."""

    ALLOW = "ALLOW"
    REMOVE = "REMOVE"


OTHER = "OTHER"  # a request Model C does not handle (a question, a status check, ...)


class Extraction(BaseModel):
    """What a candidate model finds in the command text, before any checks.

    `action` is None when no clear allow or remove is said, including a speech-to-text
    slip such as "a loud" for "allow": the candidate must not correct it.
    """

    model_config = ConfigDict(extra="forbid")

    action: Action | Literal["OTHER"] | None = None
    numbers: list[str] = []  # each spoken plate number, as said ("12345", "one two three")
    time: str | None = None  # the end-time phrase, as said ("until tomorrow", "for 2 hours")


class ParsedCommand(BaseModel):
    """A checked permit change, proposed to the owner (never applied without a yes)."""

    model_config = ConfigDict(frozen=True, extra="forbid")  # no bay: permits cover both

    action: Action
    number: str = Field(pattern=r"^[1-9]\d{0,4}$")
    until: datetime | None = None  # None: permanent

    @field_validator("until")
    @classmethod
    def _aware(cls, v: datetime | None) -> datetime | None:
        if v is not None and v.tzinfo is None:
            raise ValueError("until must carry a time zone")
        return v


Reason = Literal[
    "unclear_action",
    "missing_number",
    "multiple_numbers",
    "invalid_number",
    "single_digit_number",
    "unclear_time",
    "ambiguous_time",
    "time_in_past",
    "unsure",  # a safety check found the model unsure (Model C's own checks, not the rules)
]

QUESTIONS: dict[str, str] = {
    "unclear_action": "Do you want to allow or remove a car?",
    "missing_number": "Which car number?",
    "multiple_numbers": "Please give one car number at a time.",
    "invalid_number": "Plate numbers have 1 to 5 digits. Which number?",
    "single_digit_number": "Car {number} has a one-digit plate number. Please check it.",
    "unclear_time": "Until when? For example: until 6 PM, until tomorrow, for 2 hours.",
    "ambiguous_time": "Is that AM or PM?",
    "time_in_past": "That time has already passed today. Until when?",
    "unsure": "I am not sure I understood. Please say it again, for example: allow car 12345 "
    "until 6 PM.",
}


class NeedsReview(BaseModel):
    """NEEDS_REVIEW: essential information is unclear. Ask the owner; change nothing.

    For a one-digit plate number the full command is kept as `proposal`, so the owner
    can check the number and confirm it instead of saying it again.
    """

    model_config = ConfigDict(frozen=True)

    reason: Reason
    proposal: ParsedCommand | None = None

    @property
    def question(self) -> str:
        """The question for this reason, with the proposed number if there is one."""
        return QUESTIONS[self.reason].format(number=self.proposal.number if self.proposal else "")


class Unsupported(BaseModel):
    """The owner asked for something other than allowing or removing a car."""

    model_config = ConfigDict(frozen=True)

    @property
    def message(self) -> str:
        """The reply to a request other than allowing or removing a car."""
        return "I can only allow or remove a car. For example: allow car 12345 until 6 PM."


Result = ParsedCommand | NeedsReview | Unsupported


class Permit(BaseModel):
    """A car number allowed to park, until an end time or permanently."""

    number: str
    until: datetime | None = None  # None: permanent


def number_matches(number: str, plate_text: str) -> bool:
    """Whether a spoken plate number matches a plate read by Model B.

    Letter codes are dropped (Dubai "G12345" -> "12345"). Plates with a numeric code
    (for example Abu Dhabi "1028684" = code 10 + number 28684) also match when only a
    1-2 digit code is left in front. Different cars sharing a number are out of scope.
    """
    digits = "".join(ch for ch in plate_text if ch.isdigit())
    if digits == number:
        return True
    numeric_code = not any(ch.isalpha() for ch in plate_text)
    return numeric_code and digits.endswith(number) and 1 <= len(digits) - len(number) <= 2


class PermitTable:
    """The one permit table. Changes only after the owner confirms."""

    def __init__(self) -> None:
        self.permits: dict[str, Permit] = {}

    def confirmation(self, cmd: ParsedCommand, known_plates: Iterable[str] = ()) -> str:
        """The question shown to the owner before a change."""
        seen = [p for p in known_plates if number_matches(cmd.number, p.split()[-1])]
        car = f"car {cmd.number}" + (f" (seen before as {', '.join(seen)})" if seen else "")
        if cmd.action is Action.REMOVE:
            return f"Remove the permit for {car} (both bays)?"
        until = f"until {cmd.until:%a %d %b %H:%M}" if cmd.until else "permanently (no end time)"
        return f"Allow {car} in either bay {until}?"

    def apply(self, cmd: ParsedCommand, confirm: Callable[[str], bool]) -> bool:
        """Ask the owner; change the table only on a yes. Returns whether it changed."""
        if cmd.action is Action.REMOVE and cmd.number not in self.permits:
            return False
        if not confirm(self.confirmation(cmd)):
            return False
        if cmd.action is Action.REMOVE:
            del self.permits[cmd.number]
        else:
            self.permits[cmd.number] = Permit(number=cmd.number, until=cmd.until)
        return True

    def find(self, plate_text: str, at: datetime) -> Permit | None:
        """The valid permit for a car read by Model B at this time, in either bay."""
        for p in self.permits.values():
            if number_matches(p.number, plate_text) and (p.until is None or at <= p.until):
                return p
        return None
