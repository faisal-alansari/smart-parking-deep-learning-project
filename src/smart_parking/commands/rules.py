"""Fixed rules shared by every Model C candidate: spoken numbers, time phrases, checks.

A candidate only extracts text pieces; these rules are the same for all candidates, so
the comparison measures the extraction alone.

Only clear commands are accepted; anything unclear returns NEEDS_REVIEW (never a guess).

Time phrases (final rules, 2026-11-21):
- none: a permanent permit (the confirmation says so);
- "today", "for today", "end of day": today at 23:59; "tomorrow": tomorrow at 23:59;
- a weekday ("until Monday"): 23:59 on the next day with that name, within 6 days;
  today's own weekday and "next Monday" are unclear (which week?), so they are asked;
- a clock time with AM/PM or in 24-hour form ("6 PM", "6:30pm", "18:00", "six thirty
  pm", "noon", "midnight"), optionally with "today" or "tomorrow". Without a day it means
  today; if that time has already passed, ask (never move it to tomorrow). "Midnight"
  is the coming midnight. "Tonight" only goes with a PM time ("until 10 pm tonight");
- a duration: "for 2 hours", "for an hour", "for 30 minutes", "for 3 days", "for a week".

Asked instead: an hour without AM/PM ("until 6", "until tomorrow at 7"); "until tonight"
alone; vague phrases ("until next month", "until he leaves", "for a while").
"""

import re
from datetime import datetime, timedelta
from typing import Literal

from smart_parking.commands.schema import (
    OTHER,
    Action,
    Extraction,
    NeedsReview,
    ParsedCommand,
    Result,
    Unsupported,
)

UNITS = {
    "zero": 0, "oh": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
}  # fmt: skip
TEENS = {
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
}  # fmt: skip
TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
}  # fmt: skip
SCALES = {"hundred": 100, "thousand": 1000}
NUMBER_WORDS = UNITS | TEENS | TENS
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
FILLERS = r"please|thanks|thank you|okay|ok|uh|um"
END_OF_DAY = (23, 59)


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z]+|\d+", text.lower().replace("-", " "))


def _cardinal(tokens: list[str]) -> str | None:
    total = current = 0
    for t in tokens:
        if t == "and":
            continue
        if t.isdigit():
            current += int(t)
        elif t in NUMBER_WORDS:
            current += NUMBER_WORDS[t]
        elif t == "hundred":
            current *= 100
        elif t == "thousand":
            total += current * 1000
            current = 0
        else:
            return None
    return str(total + current)


def spoken_digits(text: str) -> str | None:
    """Digits of a spoken number, or None if it is not one.

    "12345", "1 2 3 4 5", "one two three four five", "twelve thirty four five"
    (said in pairs) and "twelve thousand three hundred forty five" all give "12345".
    """
    tokens = _tokens(text)
    if not tokens:
        return None
    if any(t in SCALES for t in tokens):
        return _cardinal(tokens)
    out, i = [], 0
    while i < len(tokens):
        t = tokens[i]
        if t.isdigit():
            out.append(t)
        elif t in TENS and i + 1 < len(tokens) and UNITS.get(tokens[i + 1], 0) > 0:
            out.append(str(TENS[t] + UNITS[tokens[i + 1]]))
            i += 1
        elif t in NUMBER_WORDS:
            out.append(str(NUMBER_WORDS[t]))
        else:
            return None
        i += 1
    return "".join(out)


def _clean_time(phrase: str) -> str:
    p = phrase.lower()
    p = re.sub(r"(?<![a-z])([ap])\.?\s?m\b\.?", r"\1m", p)  # "p.m.", "6p.m." -> "pm"
    p = re.sub(r"(\d)(am|pm)\b", r"\1 \2", p)
    p = re.sub(r"[^a-z0-9: ]", " ", p)
    p = re.sub(r"\bend of (the )?day\b", "today", p)
    p = re.sub(r"\bhalf (an )?hour\b", "30 minutes", p)
    p = re.sub(r"\b(a|an)\b(?= (minute|hour|day|week)\b)", "1", p)
    p = re.sub(
        rf"\b(until|till|til|up to|through|by|for|the|at|o clock|oclock|{FILLERS})\b", " ", p
    )
    words = p.split()
    out, i = [], 0
    while i < len(words):  # number words -> digits, keeping "six thirty" as 6 30
        w = words[i]
        if w in TENS and i + 1 < len(words) and UNITS.get(words[i + 1], 0) > 0:
            out.append(str(TENS[w] + UNITS[words[i + 1]]))
            i += 1
        elif w in NUMBER_WORDS and w != "oh":
            out.append(str(NUMBER_WORDS[w]))
        else:
            out.append(w)
        i += 1
    return " ".join(out)


def _at(day: datetime, hour: int, minute: int) -> datetime:
    return day.replace(hour=hour, minute=minute, second=0, microsecond=0)


TimeProblem = Literal["unclear_time", "ambiguous_time"]


def resolve_time(phrase: str, now: datetime) -> datetime | TimeProblem:
    """End time for a spoken time phrase, or why it must be asked about.

    A past result is possible ("until 2 PM" said at 9 PM); `finish` asks about it.
    """
    p = _clean_time(phrase)
    m = re.fullmatch(r"(\d+) (minute|min|hour|hr|day|week)s?", p)
    if m:
        unit = {"min": "minutes", "hr": "hours"}.get(m[2], m[2] + "s")
        return now + timedelta(**{unit: int(m[1])})
    words = p.split()
    days = [w for w in words if w in ("today", "tonight", "tomorrow")]
    rest = " ".join(w for w in words if w not in ("today", "tonight", "tomorrow"))
    if len(days) > 1:
        return "unclear_time"
    day = days[0] if days else None
    base = now + timedelta(days=1) if day == "tomorrow" else now
    if rest in WEEKDAYS and day is None:
        ahead = (WEEKDAYS.index(rest) - now.weekday()) % 7
        return _at(now + timedelta(days=ahead), *END_OF_DAY) if ahead else "unclear_time"
    if rest == "":
        return _at(base, *END_OF_DAY) if day in ("today", "tomorrow") else "unclear_time"
    if rest == "midnight":
        return _at(now + timedelta(days=1), 0, 0) if day != "tomorrow" else "unclear_time"
    if rest == "noon":
        return _at(base, 12, 0) if day != "tonight" else "unclear_time"
    m = re.fullmatch(r"(\d{1,2})(?:[: ](\d{2}))? ?(am|pm)?", rest)
    if not m or int(m[2] or 0) > 59:
        return "unclear_time"
    hour, minute, half = int(m[1]), int(m[2] or 0), m[3]
    if half:
        if not 1 <= hour <= 12 or (day == "tonight" and half == "am"):
            return "unclear_time"
        hour = hour % 12 + (0 if half == "am" else 12)
    elif 1 <= hour <= 12:
        return "ambiguous_time"  # never assume AM or PM
    elif not (13 <= hour <= 23 or (hour == 0 and m[2])):
        return "unclear_time"
    if day == "tonight" and hour < 12:
        return "unclear_time"
    return _at(base, hour, minute)


def finish(ex: Extraction, now: datetime) -> Result:
    """Check a candidate's extraction. Anything unclear is NEEDS_REVIEW; never guess."""
    if ex.action == OTHER:
        return Unsupported()
    if ex.action is None:
        return NeedsReview(reason="unclear_action")
    if not ex.numbers:
        return NeedsReview(reason="missing_number")
    if len(ex.numbers) > 1:
        return NeedsReview(reason="multiple_numbers")
    number = spoken_digits(ex.numbers[0])
    if not number or not re.fullmatch(r"[1-9]\d{0,4}", number):
        return NeedsReview(reason="invalid_number")
    until = None
    if ex.action == Action.ALLOW and ex.time:  # REMOVE ends the permit now; a time is ignored
        until = resolve_time(ex.time, now)
        if isinstance(until, str):
            return NeedsReview(reason=until)
        if until <= now:
            return NeedsReview(reason="time_in_past")
    cmd = ParsedCommand(action=Action(ex.action), number=number, until=until)
    if len(number) == 1:  # rare and easy to mishear: the owner checks it
        return NeedsReview(reason="single_digit_number", proposal=cmd)
    return cmd
