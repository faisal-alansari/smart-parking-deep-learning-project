from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from smart_parking.commands import baseline
from smart_parking.commands.dataset import build
from smart_parking.commands.rules import finish, resolve_time, spoken_digits
from smart_parking.commands.schema import (
    OTHER,
    Action,
    Extraction,
    NeedsReview,
    ParsedCommand,
    PermitTable,
    Unsupported,
    number_matches,
)
from smart_parking.commands.score import outcome

TZ = ZoneInfo("Asia/Dubai")
NOW = datetime(2026, 11, 21, 9, 30, tzinfo=TZ)  # Saturday morning


def at(day: int, h: int, m: int = 0) -> datetime:
    return datetime(2026, 11, day, h, m, tzinfo=TZ)


@pytest.mark.parametrize(
    "said",
    ["12345", "1 2 3 4 5", "one two three four five", "twelve thousand three hundred forty five"],
)
def test_spoken_numbers(said):
    assert spoken_digits(said) == "12345"


def test_spoken_numbers_in_pairs_and_with_oh():
    assert spoken_digits("twelve thirty four") == "1234"
    assert spoken_digits("one oh five") == "105"
    assert spoken_digits("my friend") is None


@pytest.mark.parametrize(
    ("phrase", "expected"),
    [
        ("until tomorrow", at(22, 23, 59)),
        ("until today", at(21, 23, 59)),
        ("until end of day", at(21, 23, 59)),
        ("until 6 PM", at(21, 18)),
        ("till 6p.m.", at(21, 18)),
        ("until 18:00", at(21, 18)),
        ("until tomorrow at 7:30 am", at(22, 7, 30)),
        ("until six thirty pm", at(21, 18, 30)),
        ("until 10 pm tonight", at(21, 22)),
        ("for two hours", at(21, 11, 30)),
        ("for an hour", at(21, 10, 30)),
        ("until Friday", at(27, 23, 59)),  # the next Friday, end of day
        ("till Monday", at(23, 23, 59)),
        ("until midnight", at(22, 0)),
        ("until 8 am", at(21, 8)),  # today: already passed, so `finish` asks
    ],
)
def test_time_phrases(phrase, expected):
    assert resolve_time(phrase, NOW) == expected


@pytest.mark.parametrize(
    ("phrase", "problem"),
    [
        ("until 6", "ambiguous_time"),  # never assume AM or PM
        ("till seven", "ambiguous_time"),
        ("until 6:30", "ambiguous_time"),
        ("until tomorrow at 7", "ambiguous_time"),
        ("until tonight", "unclear_time"),
        ("until next month", "unclear_time"),
        ("until he leaves", "unclear_time"),
        ("until tomorrow morning", "unclear_time"),
        ("until next Monday", "unclear_time"),  # which week?
        ("until Saturday", "unclear_time"),  # said on a Saturday: today or next week?
        ("until 7 am tonight", "unclear_time"),
    ],
)
def test_unclear_time_phrases_are_asked(phrase, problem):
    assert resolve_time(phrase, NOW) == problem


def test_finish_builds_a_checked_command():
    ex = Extraction(action=Action.ALLOW, numbers=["one two three"], time="for 2 hours")
    assert finish(ex, NOW) == ParsedCommand(action=Action.ALLOW, number="123", until=at(21, 11, 30))
    assert finish(Extraction(action=Action.ALLOW, numbers=["44"]), NOW).until is None  # permanent


@pytest.mark.parametrize(
    ("ex", "reason"),
    [
        (Extraction(numbers=["123"]), "unclear_action"),
        (Extraction(action=Action.ALLOW), "missing_number"),
        (Extraction(action=Action.ALLOW, numbers=["12", "34"]), "multiple_numbers"),
        (Extraction(action=Action.ALLOW, numbers=["123456"]), "invalid_number"),
        (Extraction(action=Action.ALLOW, numbers=["55"], time="until later"), "unclear_time"),
        (Extraction(action=Action.ALLOW, numbers=["55"], time="until 6"), "ambiguous_time"),
        (Extraction(action=Action.ALLOW, numbers=["55"], time="until 8 am"), "time_in_past"),
    ],
)
def test_finish_asks_when_anything_essential_is_unclear(ex, reason):
    assert finish(ex, NOW) == NeedsReview(reason=reason)


def test_single_digit_number_is_kept_for_the_owner_to_check():
    result = finish(Extraction(action=Action.ALLOW, numbers=["seven"]), NOW)
    assert result == NeedsReview(
        reason="single_digit_number", proposal=ParsedCommand(action=Action.ALLOW, number="7")
    )
    assert "Car 7" in result.question


def test_other_requests_are_unsupported():
    assert finish(Extraction(action=OTHER, numbers=["123"]), NOW) == Unsupported()


def test_remove_ignores_time():
    ex = Extraction(action=Action.REMOVE, numbers=["77"], time="nonsense")
    assert finish(ex, NOW) == ParsedCommand(action=Action.REMOVE, number="77")


def test_command_contract_rejects_bad_values():
    with pytest.raises(ValidationError):
        ParsedCommand(action=Action.ALLOW, number="123456")
    with pytest.raises(ValidationError):
        ParsedCommand(action=Action.ALLOW, number="05")
    with pytest.raises(ValidationError):
        ParsedCommand(action=Action.ALLOW, number="5", until=datetime(2026, 11, 21, 18))
    with pytest.raises(ValidationError):
        ParsedCommand(action=Action.ALLOW, number="5", bay=2)  # permits have no bay


def test_spoken_number_matches_the_plate_read_by_model_b():
    assert number_matches("12345", "G12345")
    assert not number_matches("345", "G12345")
    assert number_matches("28684", "1028684")  # Abu Dhabi: numeric code 10
    assert not number_matches("8684", "1028684")


def test_permit_table_changes_only_after_confirmation():
    table = PermitTable()
    cmd = ParsedCommand(action=Action.ALLOW, number="12345", until=at(21, 18))
    assert not table.apply(cmd, confirm=lambda question: False)
    assert table.permits == {}
    questions = []
    assert table.apply(cmd, confirm=lambda q: questions.append(q) or True)
    assert questions == ["Allow car 12345 in either bay until Sat 21 Nov 18:00?"]
    assert table.find("G12345", at=at(21, 17)) is not None  # either bay
    assert table.find("G12345", at=at(21, 19)) is None  # expired
    remove = ParsedCommand(action=Action.REMOVE, number="12345")
    assert table.apply(remove, confirm=lambda q: True) and table.permits == {}


def test_confirmation_names_the_known_plate_and_says_permanent():
    cmd = ParsedCommand(action=Action.ALLOW, number="12345")
    text = PermitTable().confirmation(cmd, known_plates=["Dubai G12345", "Sharjah 3 777"])
    assert text == (
        "Allow car 12345 (seen before as Dubai G12345) in either bay permanently (no end time)?"
    )


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "Allow car number 12345 until 6 PM.",
            Extraction(action="ALLOW", numbers=["12345"], time="until 6 pm"),
        ),
        ("let 4 5 in in bay two", Extraction(action="ALLOW", numbers=["4 5"])),
        ("Take 36846 off the list from bay 1.", Extraction(action="REMOVE", numbers=["36846"])),
        ("Is car 441 allowed?", Extraction(action=OTHER)),
        ("and car 441", Extraction(numbers=["441"])),  # a slip is not corrected
    ],
)  # fmt: skip
def test_rule_baseline(text, expected):
    assert baseline.extract(text) == expected


def test_command_sets_are_reproducible_and_their_answers_reachable():
    dev, test = build("dev", 1, set()), build("test", 2, set())
    assert build("dev", 1, set()) == dev
    used: set[str] = set()
    dev, test = build("dev", 1, used), build("test", 2, used)
    numbers = [
        {r["expected"]["proposal"]["number"] for r in s if r["expected"]["proposal"]}
        for s in (dev, test)
    ]
    assert not {n for n in numbers[0] & numbers[1] if len(n) > 1}  # one-digit may repeat
    for row in dev + test:  # a perfect extraction reaches every expected answer
        got = finish(Extraction(**row["oracle"]), datetime.fromisoformat(row["now"]))
        assert outcome(got) == row["expected"], row["text"]
