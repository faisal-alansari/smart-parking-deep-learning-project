"""Generate the owner-command evaluation sets: a dev set and a frozen test set.

Short commands as a phone's speech-to-text would write them: lower case or dictation
style ("Allow car 12345 until 6 PM."), numbers as digits, spaced digits or words, a
few fillers, a few bay mentions (ignored: permits cover both bays) and a few
speech-to-text slips. Each example is built from its meaning first (action, number,
end time, or the reason it must be asked), so the expected answer is known by
construction and does not come from the rules or parser being tested.

Expected answers follow the final scope (2026-11-21): a clear command is PROPOSED;
anything unclear is NEEDS_REVIEW with a reason (never a guess); other requests are
UNSUPPORTED.

- dev: for designing prompts, rules and settings;
- check: 120 more commands in dev wording with new numbers and times. Meant only to confirm
  dev choices, it exposed two dangerous answers and was then used for development too;
- confirm: another 120 in dev wording; opened once, it showed two dangerous answers and was
  then used for development too;
- confirm2: the same again; opened once, it showed two dangerous answers (then development);
- confirm3: the same again; opened once, it showed one dangerous answer (then development);
- confirm4: another 120 in dev wording, opened once to confirm the final design before the test;
- test: frozen; opened once for the final comparison. About a third of its allow and
  remove commands use wording that never appears in dev ("unseen" tag).

Nothing here is used for training or fine-tuning. Run: `just command-data`.
"""

import json
import random
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from smart_parking.common.config import CommandsConfig, load_config

TZ = ZoneInfo("Asia/Dubai")
NOWS = {
    "dev": ["2026-11-21T09:30", "2026-11-24T19:45"],
    "test": ["2026-11-26T08:15", "2026-11-29T21:10", "2026-12-02T14:40"],
    "check": ["2026-11-22T07:50", "2026-11-25T16:20", "2026-11-27T22:05"],
    "confirm": ["2026-11-23T12:35", "2026-11-28T06:45", "2026-12-01T19:30"],
    "confirm2": ["2026-11-24T10:10", "2026-11-30T23:15", "2026-12-03T17:55"],
    "confirm3": ["2026-11-25T09:05", "2026-11-29T15:40", "2026-12-04T20:25"],
    "confirm4": ["2026-11-26T11:20", "2026-12-01T07:35", "2026-12-05T21:50"],
}
# Examples per set. allow/remove: clear commands (a permit change is proposed);
# single_digit: clear but a one-digit number (NEEDS_REVIEW with the proposal kept);
# unsupported: another request; the rest: NEEDS_REVIEW for that reason.
COUNTS = {
    "dev": {
        "allow": 26, "remove": 8, "single_digit": 2, "unclear_action": 4, "unsupported": 4,
        "missing_number": 3, "multiple_numbers": 2, "invalid_number": 2, "unclear_time": 3,
        "ambiguous_time": 3, "time_in_past": 3,
    },
    "check": {
        "allow": 52, "remove": 16, "single_digit": 4, "unclear_action": 8, "unsupported": 8,
        "missing_number": 6, "multiple_numbers": 4, "invalid_number": 4, "unclear_time": 6,
        "ambiguous_time": 6, "time_in_past": 6,
    },
    "confirm4": {
        "allow": 52, "remove": 16, "single_digit": 4, "unclear_action": 8, "unsupported": 8,
        "missing_number": 6, "multiple_numbers": 4, "invalid_number": 4, "unclear_time": 6,
        "ambiguous_time": 6, "time_in_past": 6,
    },
    "confirm3": {
        "allow": 52, "remove": 16, "single_digit": 4, "unclear_action": 8, "unsupported": 8,
        "missing_number": 6, "multiple_numbers": 4, "invalid_number": 4, "unclear_time": 6,
        "ambiguous_time": 6, "time_in_past": 6,
    },
    "confirm2": {
        "allow": 52, "remove": 16, "single_digit": 4, "unclear_action": 8, "unsupported": 8,
        "missing_number": 6, "multiple_numbers": 4, "invalid_number": 4, "unclear_time": 6,
        "ambiguous_time": 6, "time_in_past": 6,
    },
    "confirm": {
        "allow": 52, "remove": 16, "single_digit": 4, "unclear_action": 8, "unsupported": 8,
        "missing_number": 6, "multiple_numbers": 4, "invalid_number": 4, "unclear_time": 6,
        "ambiguous_time": 6, "time_in_past": 6,
    },
    "test": {
        "allow": 70, "remove": 25, "single_digit": 6, "unclear_action": 12, "unsupported": 10,
        "missing_number": 8, "multiple_numbers": 6, "invalid_number": 5, "unclear_time": 8,
        "ambiguous_time": 5, "time_in_past": 5,
    },
}  # fmt: skip
UNSEEN_SHARE = 0.33  # test only
SLIPS = {
    "dev": 1,
    "test": 6,
    "check": 2,
    "confirm": 2,
    "confirm2": 2,
    "confirm3": 2,
    "confirm4": 2,
}  # unclear_action examples that are speech-to-text slips

SEEN = {
    "allow": ["allow {obj}", "add {obj}", "let {obj} in", "approve {obj}"],
    "remove": ["remove {obj}", "delete {obj}", "take {obj} off the list"],
    "bay": ["in bay {b}", "bay {b}", "for bay {b}"],
}
UNSEEN = {
    "allow": [
        "give {obj} access", "permit {obj}", "{obj} can park", "whitelist {obj}",
        "grant access to {obj}",
    ],
    "remove": [
        "cancel {obj}", "revoke {obj}", "block {obj}", "{obj} is not allowed anymore",
        "cancel the permit for {obj}", "don't allow {obj} anymore",
    ],
    "bay": ["in parking {b}", "spot {b}", "in slot {b}", "parking number {b}"],
}  # fmt: skip
BAY_NUMBERS = {"dev": [1, 2], "test": [1, 2, 1, 2, 3, 5]}  # any bay said is ignored
# Speech-to-text slips: the action word is misheard, so it must be asked, not corrected.
SLIP_TEMPLATES = {
    "dev": ["and {obj}"],  # "add"
    "test": ["a loud {obj}", "aloud {obj}", "and {obj}", "we move {obj}"],  # allow/add/remove
}
OBJECTS = ["{n}", "car {n}", "car number {n}", "number {n}", "plate {n}", "plate number {n}"]
OBJECTS_TEST = OBJECTS + ["the car {n}", "vehicle {n}"]
PREFIX = {
    "dev": ["", "", "", "", "please ", "hey ", "okay "],
    "test": ["", "", "", "", "please ", "hey ", "okay ", "um ", "can you ", "could you "],
}
SUFFIX = {"dev": ["", "", "", " please"], "test": ["", "", "", " please", " thanks", " thank you"]}
CLARIFY = {
    "dev": {
        "missing_number": [
            "allow the car{t}", "add a car in bay 2", "remove the car", "let my friend in{t}",
            "allow my brother's car",
        ],
        "no_verb": ["car {n} in bay 2", "{n} until tomorrow", "car number {n}"],
        "unsupported": [
            "what's the weather today", "how many cars are parked", "is car {n} allowed",
            "hello", "show me the permits", "extend the permit for car {n}",
        ],
        "unclear": ["until tonight", "until {today}", "for a while", "until tomorrow morning",
                    "until later"],  # used in this order
        "multiple": ["allow {n} and {m}", "add car {n} and car {m} until tomorrow"],
    },
    "test": {
        "missing_number": [
            "give access to the white car", "delete the visitor", "permit the guest{t}",
            "add my cousin's car in bay 1", "remove that car", "let the delivery guy in{t}",
            "allow the car in bay 2{t}",
        ],
        "no_verb": [
            "car {n} in bay 1", "plate {n} till 8 pm", "number {n} for two hours", "{n} please",
            "the car {n} tomorrow", "vehicle {n} in bay 2",
        ],
        "unsupported": [
            "check car {n}", "which bay is free", "list all permits", "good morning",
            "is {n} still allowed", "who is parked in bay 1", "what time is it", "open the gate",
            "edit car {n}", "change the time for {n}",
        ],
        "unclear": [  # used in this order: the owner's named cases first
            "until tonight", "until next month", "until he leaves", "until next Monday",
            "until {today}", "until the weekend", "until tomorrow afternoon", "for some time",
            "until after lunch",
        ],
        "multiple": ["allow cars {n} and {m}", "remove {n} and {m}", "let {n} and {m} in"],
    },
}  # fmt: skip

ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
TEENS = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
         "seventeen", "eighteen", "nineteen"]  # fmt: skip
TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def words(n: int) -> str:
    """Cardinal words: 12345 -> 'twelve thousand three hundred forty five'."""
    if n < 10:
        return ONES[n]
    if n < 20:
        return TEENS[n - 10]
    if n < 100:
        return TENS[n // 10] + (f" {ONES[n % 10]}" if n % 10 else "")
    if n < 1000:
        return f"{ONES[n // 100]} hundred" + (f" {words(n % 100)}" if n % 100 else "")
    return f"{words(n // 1000)} thousand" + (f" {words(n % 1000)}" if n % 1000 else "")


def say_number(rng: random.Random, n: str) -> tuple[str, str]:
    """A plate number as speech-to-text might write it, and the style used."""
    styles = ["digits"] * 11 + ["spaced"] * 3 + ["digit_words"] * 3
    if len(n) <= 5:
        styles += ["cardinal"] * 2
    if len(n) == 4 and n[2:] != "00":
        styles.append("pairs")
    style = rng.choice(styles)
    if style == "spaced":
        return " ".join(n), style
    if style == "digit_words":
        return " ".join(rng.choice(["zero", "oh"]) if d == "0" else ONES[int(d)] for d in n), style
    if style == "cardinal":
        return words(int(n)), style
    if style == "pairs":  # "1234" -> "twelve thirty four", "1205" -> "twelve oh five"
        second = f"oh {ONES[int(n[3])]}" if n[2] == "0" else words(int(n[2:]))
        return f"{words(int(n[:2]))} {second}", style
    return n, style


def plate_number(rng: random.Random, used: set[str], digits: int | None = None) -> str:
    """A new plate number (2-5 digits unless `digits` is given). Numbers never repeat
    across the two sets, except one-digit numbers (only nine exist)."""
    while True:
        k = digits or rng.choices([2, 3, 4, 5], weights=[7, 15, 30, 45])[0]
        n = str(rng.randint(10 ** (k - 1), 10**k - 1))
        if k == 1:
            return n
        if n not in used:
            used.add(n)
            return n


def _at(day: datetime, h: int, m: int) -> datetime:
    return day.replace(hour=h, minute=m, second=0, microsecond=0)


def _later_today(rng: random.Random, now: datetime, hours: range) -> tuple[int, int] | None:
    """A clock time later today (none if the day is nearly over)."""
    options = [(h, m) for h in hours for m in (0, 0, 0, 30, 15) if _at(now, h, m) > now]
    return rng.choice(options) if options else None


def _clock(rng: random.Random, h24: int, m: int) -> str:
    """A clock time with AM/PM, as dictation might write it."""
    h, half = h24 % 12 or 12, "am" if h24 < 12 else "pm"
    half = rng.choice([half, half, half.upper(), f"{half[0]}.m."])
    if m == 0:
        return rng.choice(
            [f"{h} {half}", f"{h}{half}", f"{ONES[h] if h < 10 else words(h)} {half}"]
        )
    return rng.choice([f"{h}:{m:02d} {half}", f"{words(h)} {words(m)} {half}"])


def say_time(rng: random.Random, now: datetime) -> tuple[str, datetime]:
    """A clear time phrase and the end time it means (always in the future)."""
    until = rng.choice(["until", "until", "till"])
    kind = rng.choices(
        ["tomorrow", "today", "clock", "clock_day", "duration", "weekday", "noon", "24h"],
        weights=[5, 3, 6, 4, 6, 2, 1, 1],
    )[0]
    tomorrow = now + timedelta(days=1)
    later = _later_today(rng, now, range(7, 24))
    if kind in ("clock", "24h") and later is None:
        kind = "clock_day"
    if kind == "tomorrow":
        return f"{until} tomorrow", _at(tomorrow, 23, 59)
    if kind == "today":
        return rng.choice(["until today", "for today", "until end of day"]), _at(now, 23, 59)
    if kind == "clock":
        h, m = later
        if h >= 18 and rng.random() < 0.3:
            return f"{until} {_clock(rng, h, m)} tonight", _at(now, h, m)
        return f"{until} {_clock(rng, h, m)}", _at(now, h, m)
    if kind == "clock_day":
        h, m = rng.randint(7, 22), rng.choice([0, 0, 0, 30, 15])
        clock = _clock(rng, h, m)
        phrase = rng.choice([f"{until} tomorrow {clock}", f"{until} tomorrow at {clock}",
                             f"{until} {clock} tomorrow"])  # fmt: skip
        return phrase, _at(tomorrow, h, m)
    if kind == "duration":
        unit, n = rng.choice([("hour", rng.randint(1, 5)), ("minute", rng.choice([15, 30, 45])),
                              ("day", rng.randint(1, 7)), ("week", 1)])  # fmt: skip
        amount = (
            rng.choice(["a" if unit != "hour" else "an", "one"])
            if n == 1
            else (rng.choice([str(n), words(n)]))
        )
        return f"for {amount} {unit}{'s' if n > 1 else ''}", now + timedelta(**{unit + "s": n})
    if kind == "weekday":  # never today's own weekday (that one is asked)
        ahead = rng.randint(1, 6)
        return f"{until} {WEEKDAYS[(now.weekday() + ahead) % 7]}", _at(
            now + timedelta(days=ahead), 23, 59
        )
    if kind == "noon":
        if now.hour < 12 and rng.random() < 0.5:
            return f"{until} noon", _at(now, 12, 0)
        return f"{until} midnight", _at(tomorrow, 0, 0)
    h, m = later
    if h < 13:
        return f"{until} {_clock(rng, h, m)}", _at(now, h, m)
    return f"{until} {h}:{m:02d}", _at(now, h, m)


def ambiguous_time(rng: random.Random) -> str:
    """An hour without AM or PM: always asked."""
    h = rng.randint(1, 12)
    until = rng.choice(["until", "till"])
    return rng.choice([f"{until} {h}", f"{until} {words(h)}", f"{until} {h}:30",
                       f"{until} tomorrow at {h}"])  # fmt: skip


def past_time(rng: random.Random, now: datetime) -> str:
    """A clock time earlier today, said without a date: always asked."""
    options = [(h, m) for h in range(6, now.hour + 1) for m in (0, 30) if _at(now, h, m) < now]
    h, m = rng.choice(options)
    if h == 12 and m == 0 and rng.random() < 0.5:
        return "until noon"
    phrase = f"{rng.choice(['until', 'till'])} {_clock(rng, h, m)}"
    return phrase + (" today" if rng.random() < 0.2 else "")


QUESTIONS = ("is ", "what", "how ", "which ", "who ")


def _dictation(rng: random.Random, text: str) -> str:
    """Half the commands in dictation style: capital first letter and a full stop."""
    text = text.replace(" in in ", " in ")  # "let car 5 in" + "in bay 2"
    if rng.random() < 0.5:
        return text
    end = "?" if text.startswith(QUESTIONS) else "" if text.endswith(".") else "."
    return text[0].upper() + text[1:] + end


def _wrap(rng: random.Random, split: str, body: str, verb_first: bool) -> str:
    prefix, suffix = rng.choice(PREFIX[split]), rng.choice(SUFFIX[split])
    if not verb_first and prefix.strip() in ("can you", "could you"):
        prefix = ""
    if prefix.strip() == suffix.strip() == "please":
        suffix = ""
    return _dictation(rng, f"{prefix}{body}{suffix}")


def outcome(status: str, reason: str | None = None, proposal: dict | None = None) -> dict:
    """The expected result: status PROPOSED, NEEDS_REVIEW or UNSUPPORTED."""
    return {"status": status, "reason": reason, "proposal": proposal}


def proposal(action: str, number: str, until: datetime | None = None) -> dict:
    """An expected proposal as a dict, with the end time in ISO form."""
    return {"action": action, "number": number, "until": until.isoformat() if until else None}


def _example(text: str, now: datetime, expected: dict, oracle: dict, **tags) -> dict:
    """`oracle`: the exact pieces used to build the text (a perfect extraction). It is
    never shown to a candidate; it checks that the shared rules can reach `expected`."""
    return {
        "text": text, "now": now.isoformat(), "expected": expected, "oracle": oracle, "tags": tags,
    }  # fmt: skip


def _command(rng, split, now, used, kind: str, wording: str = "seen", slip: bool = False) -> dict:
    """A clear allow or remove (kind allow, remove, single_digit), or one whose action
    word is a speech-to-text slip (slip=True: NEEDS_REVIEW, unclear_action)."""
    action = rng.choice(["allow", "remove"]) if kind == "single_digit" else kind
    if slip:
        action = "allow"
    pools = UNSEEN if wording == "unseen" else SEEN
    template = rng.choice(SLIP_TEMPLATES[split] if slip else pools[action])
    n = plate_number(rng, used, digits=1 if kind == "single_digit" else None)
    said, style = say_number(rng, n)
    obj = rng.choice(OBJECTS_TEST if split == "test" else OBJECTS).format(n=said)
    parts, until, bay = [template.format(obj=obj)], None, False
    oracle = {"action": None if slip else action.upper(), "numbers": [said], "time": None}
    if action == "allow":
        if rng.random() < 0.35:
            bay = True
            b = rng.choice(BAY_NUMBERS[split])
            parts.append(rng.choice(pools["bay"]).format(b=rng.choice([str(b), ONES[b]])))
        if rng.random() < 0.6:
            phrase, until = say_time(rng, now)
            parts.append(phrase)
            oracle["time"] = phrase
        if len(parts) == 3 and rng.random() < 0.5:
            parts[1], parts[2] = parts[2], parts[1]
    elif "anymore" not in template and rng.random() < 0.2:
        bay = True
        parts.append(f"from bay {rng.choice([1, 2])}")
    cmd = proposal(action.upper(), n, until)
    if slip:
        expected = outcome("NEEDS_REVIEW", "unclear_action")
    elif kind == "single_digit":
        expected = outcome("NEEDS_REVIEW", "single_digit_number", cmd)
    else:
        expected = outcome("PROPOSED", proposal=cmd)
    text = _wrap(rng, split, " ".join(parts), not template.startswith(("{obj}", "don't")))
    tags = {"kind": "review", "reason": "unclear_action"} if slip else {"kind": kind}
    return _example(
        text, now, expected, oracle, **tags, wording=wording, number_style=style,
        has_bay=bay, has_time=until is not None, noisy=slip,
    )  # fmt: skip


def _clarify(rng, split, now, used, reason: str, i: int = 0) -> dict:
    """A command that must be asked about (NEEDS_REVIEW) or is another request."""
    pools = CLARIFY[split]
    n, m = plate_number(rng, used), plate_number(rng, used)
    said_n, said_m = say_number(rng, n)[0], say_number(rng, m)[0]
    oracle = {"action": "ALLOW", "numbers": [], "time": None}
    if reason in ("missing_number", "unclear_action", "multiple_numbers", "unsupported"):
        key = {"multiple_numbers": "multiple", "unclear_action": "no_verb"}.get(reason, reason)
        template = pools[key][i % len(pools[key])]  # every template appears in turn
        t = " " + say_time(rng, now)[0] if "{t}" in template and rng.random() < 0.6 else ""
        body = template.format(n=said_n, m=said_m, t=t)
        if reason in ("unclear_action", "unsupported"):
            oracle["action"] = "OTHER" if reason == "unsupported" else None
            oracle["numbers"] = [said_n] if "{n}" in template else []
        if reason == "multiple_numbers":
            oracle["numbers"] = [said_n, said_m]
        if template.startswith(("remove", "delete")):
            oracle["action"] = "REMOVE"
    else:
        verb = rng.choice(SEEN["allow"] if split == "dev" else SEEN["allow"] + UNSEEN["allow"])
        if reason == "invalid_number":
            n = plate_number(rng, used, digits=rng.choice([6, 7]))
        said_n = say_number(rng, n)[0]
        body = verb.format(obj=rng.choice(OBJECTS).format(n=said_n))
        oracle["numbers"] = [said_n]
        if reason == "unclear_time":
            phrase = pools["unclear"][i % len(pools["unclear"])]
            oracle["time"] = phrase.format(today=WEEKDAYS[now.weekday()])
        elif reason == "ambiguous_time":
            oracle["time"] = ambiguous_time(rng)
        elif reason == "time_in_past":
            oracle["time"] = past_time(rng, now)
        elif rng.random() < 0.4:  # invalid_number, with or without a time
            oracle["time"] = say_time(rng, now)[0]
        if oracle["time"]:
            body += " " + oracle["time"]
    text = _dictation(rng, body)
    if reason == "unsupported":
        expected = outcome("UNSUPPORTED")
    else:
        expected = outcome("NEEDS_REVIEW", reason)
    return _example(
        text, now, expected, oracle, kind="unsupported" if reason == "unsupported" else "review",
        reason=reason, noisy=False,
    )  # fmt: skip


def build(split: str, seed: int, used: set[str], style: str | None = None) -> list[dict]:
    """`style`: whose wording to use (the check set uses dev wording with new numbers/times)."""
    style = style or split
    rng = random.Random(seed)
    nows = [datetime.fromisoformat(t).replace(tzinfo=TZ) for t in NOWS[split]]
    rows: list[dict] = []
    texts: set[str] = set()
    plan = []
    for kind, count in COUNTS[split].items():
        for i in range(count):
            plan.append((kind, i))
    for kind, i in plan:
        for attempt in range(100):  # redraw on a repeated sentence
            now = rng.choice(nows)
            if kind in ("allow", "remove", "single_digit"):
                unseen = split == "test" and i < round(COUNTS[split][kind] * UNSEEN_SHARE)
                row = _command(rng, style, now, used, kind, "unseen" if unseen else "seen")
            elif kind == "unclear_action" and i < SLIPS[split]:
                row = _command(rng, style, now, used, "allow", slip=True)
            else:
                row = _clarify(rng, style, now, used, kind, i + attempt)
            key = re.sub(r"[^a-z0-9 ]", "", row["text"].lower())
            if key not in texts:
                texts.add(key)
                break
        rows.append(row)
    rng.shuffle(rows)
    for k, row in enumerate(rows, 1):
        row["id"] = f"{split}-{k:03d}"
    return [{"id": r.pop("id"), **r} for r in rows]


def describe(expected: dict) -> str:
    """An expected result in plain words, for the review tables and score reports."""

    def change(p: dict) -> str:
        until = p["until"]
        when = f"until {datetime.fromisoformat(until):%a %d %b %H:%M}" if until else "permanent"
        return f"{p['action']} {p['number']}" + (f", {when}" if p["action"] == "ALLOW" else "")

    if expected["status"] == "PROPOSED":
        return f"PROPOSE {change(expected['proposal'])}"
    if expected["status"] == "UNSUPPORTED":
        return "UNSUPPORTED"
    out = f"NEEDS_REVIEW ({expected['reason']})"
    return out + (f": {change(expected['proposal'])}" if expected["proposal"] else "")


def _review(rows: list[dict]) -> str:
    """A table for a human to check every expected answer."""
    lines = ["| id | command (said at) | expected |", "|---|---|---|"]
    for r in rows:
        now = datetime.fromisoformat(r["now"])
        lines.append(
            f"| {r['id']} | {r['text']} ({now:%a %d %b %H:%M}) | {describe(r['expected'])} |"
        )
    return "\n".join(lines) + "\n"


def main(cfg: CommandsConfig | None = None) -> None:
    """Run the documented entry point with contextual, rotating application logs."""
    from smart_parking.common.log import setup_logging

    setup_logging(load_config().logging)
    cfg = cfg or load_config().commands
    cfg.data_dir.mkdir(parents=True, exist_ok=True)
    used: set[str] = set()  # plate numbers never repeat across the sets
    # The check and confirm sets (dev wording, new numbers and times) are built last so dev
    # and test stay exactly as before.
    sets = [("dev", cfg.dev_seed, "dev"), ("test", cfg.test_seed, "test")]
    sets += [(name, getattr(cfg, f"{name}_seed"), "dev")
             for name in ("check", "confirm", "confirm2", "confirm3", "confirm4")]  # fmt: skip
    for split, seed, style in sets:
        rows = build(split, seed, used, style)
        with (cfg.data_dir / f"{split}.jsonl").open("w") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")
        (cfg.data_dir / f"{split}_review.md").write_text(
            f"# Command set: {split} ({len(rows)} commands)\n\n" + _review(rows)
        )


if __name__ == "__main__":
    main()
