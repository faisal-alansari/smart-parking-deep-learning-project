"""Model C candidate adapters: the answer-shape helpers (no model needed) and, when the local
weights are present, one command through each adapter."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from smart_parking.commands import adapters as A
from smart_parking.commands.schema import Action, Extraction, NeedsReview, ParsedCommand
from smart_parking.commands.tiers import fixed_form
from smart_parking.common.config import load_config

TEXT = "allow car 626 until 6 pm"


def test_copies_must_be_whole_words():
    assert A.is_copy("626", TEXT, closed=True)
    assert not A.is_copy("62", TEXT, closed=True)  # part of a number is not a copy
    assert A.is_copy("62", TEXT, closed=False)  # ...but may still grow into one
    assert not A.is_copy("12345", TEXT, closed=False)  # never invented
    assert A.is_copy("until 6 pm", TEXT, closed=True)


def test_json_answer_shape_and_copies():
    assert A.smol_state(' ["626"], "time": "until 6 pm"}', TEXT) == "done"
    assert A.smol_state(' ["62', TEXT) == "partial"
    assert A.smol_state(' ["62"], "time": null}', TEXT) == "bad"  # not a whole number
    assert A.smol_state(' ["999"]', TEXT) == "bad"  # not in the command
    assert A.smol_state(' "626"', TEXT) == "bad"  # wrong shape
    assert A.parse_smol(' ["626"], "time": null}') == (["626"], None)
    assert A.parse_smol("") == ([], None)  # no answer: the shared rules ask


def test_option_and_copy_answers():
    assert A.option_state("ALL", list(A.ACTIONS)) == "partial"
    assert A.option_state("ALLOW", list(A.ACTIONS)) == "done"
    assert A.option_state("ADD", list(A.ACTIONS)) == "bad"
    assert A.copy_state(" none", TEXT) == "done"
    assert A.copy_state(" 62", TEXT) == "partial"
    assert A.copy_state(" 626", TEXT) == "done"
    assert A.copy_state(" 12", TEXT) == "bad"


def test_raw_answers_become_extractions():
    assert A.to_extraction("NONE", ["626 "], "") == Extraction(numbers=["626"])
    assert A.to_extraction("REMOVE", [], None) == Extraction(action=Action.REMOVE)
    assert A.split_numbers("12 and 87") == ["12", "87"]
    assert A.split_numbers("12 and car 87") == ["12", "87"]


def test_spans_are_cut_and_grown_to_whole_spoken_numbers():
    text = "remove plate four zero six zero nine in bay two"
    spans = [  # GLiNER found "plate four" and "six", and the bay
        {"start": 7, "end": 17, "label": "plate number"},
        {"start": 23, "end": 26, "label": "plate number"},
        {"start": 40, "end": 47, "label": "parking bay"},
    ]
    assert A.number_runs(spans, text) == ["four zero six zero nine"]
    two = "add car 62680 and car 46149"
    spans = [{"start": 4, "end": 13, "label": "plate number"},
             {"start": 18, "end": 27, "label": "plate number"}]  # fmt: skip
    assert A.number_runs(spans, two) == ["62680", "46149"]
    times = [
        {"start": 0, "end": 8, "label": "end time"},
        {"start": 9, "end": 13, "label": "end time"},
    ]
    assert A.merge_spans(times, "tomorrow 9 pm", "end time") == ["tomorrow 9 pm"]


CFG = load_config().commands


@pytest.mark.parametrize(
    ("name", "folders"),
    [("smollm2", ["smollm2-135m"]), ("flan-t5", ["flan-t5-small"]),
     ("gliner-minilm", ["gliner-small-v2.1", "deberta-v3-small", "minilm-l6-v2"])],
)  # fmt: skip
def test_each_adapter_returns_an_extraction(name, folders):
    if not A.weights_present(CFG, folders):
        pytest.skip("weights not downloaded (just download-command-models)")
    from smart_parking.commands.score import PARSERS

    cfg = CFG.model_copy(update={"device": "cpu"})
    parser = PARSERS[name].load(cfg)
    out = parser({"text": "Allow car number 12345 until 6 PM."})
    assert isinstance(out, Extraction)
    assert all(n in "Allow car number 12345 until 6 PM." for n in out.numbers)  # copied only


class _Fake:
    def __init__(self, ex: Extraction, **sure: float) -> None:
        self.ex = ex
        self.sure = {"time_near_miss": 0.0, "action_word": 1.0, "loose_numbers": 0} | sure

    def extract(self, row):
        return self.ex, self.sure

    def __call__(self, row):
        return self.ex


def _checked(main: _Fake, check: _Fake) -> A.Checked:
    c = A.Checked.__new__(A.Checked)  # stand-in models, no download
    c.cfg, c.main, c.check = CFG, main, check
    return c


ROW = {"text": "allow car 626 until 6 pm"}
NOW = datetime(2026, 11, 21, 9, 30, tzinfo=ZoneInfo("Asia/Dubai"))
ALLOW = Extraction(action=Action.ALLOW, numbers=["626"], time="until 6 pm")


def test_checked_proposes_only_when_both_models_agree_on_action_and_number():
    assert isinstance(_checked(_Fake(ALLOW), _Fake(ALLOW)).decide(ROW, NOW), ParsedCommand)
    no_time = Extraction(action=Action.ALLOW, numbers=["626"])  # SmolLM2 missed the time only
    assert isinstance(_checked(_Fake(ALLOW), _Fake(no_time)).decide(ROW, NOW), ParsedCommand)
    remove = Extraction(action=Action.REMOVE, numbers=["626"])
    assert _checked(_Fake(ALLOW), _Fake(remove)).decide(ROW, NOW) == NeedsReview(reason="unsure")
    other = Extraction(action=Action.ALLOW, numbers=["62"])
    assert _checked(_Fake(ALLOW), _Fake(other)).decide(ROW, NOW) == NeedsReview(reason="unsure")


def test_checked_asks_without_an_action_word_or_with_an_unexplained_number():
    weak = _Fake(ALLOW, action_word=CFG.action_word_min - 0.01)  # e.g. "and car 626"
    assert _checked(weak, _Fake(ALLOW)).decide(ROW, NOW) == NeedsReview(reason="unclear_action")
    loose = _Fake(ALLOW, loose_numbers=1)  # e.g. a second car that was not found
    assert _checked(loose, _Fake(ALLOW)).decide(ROW, NOW) == NeedsReview(reason="unsure")


def test_checked_asks_when_the_time_leaves_out_a_day_that_was_said():
    assert not A.lost_day_words("allow car 626 until tomorrow 6 pm", "until tomorrow 6 pm")
    assert not A.lost_day_words("Allow car 626 for 2 hours.", "for 2 hours")
    assert A.lost_day_words("allow 626 until tomorrow nine thirty p.m.", "nine thirty p.m")
    assert A.lost_day_words("allow 626 till Friday", None)
    said = {"text": "allow 626 until tomorrow nine thirty p.m."}
    cut = _Fake(Extraction(action=Action.ALLOW, numbers=["626"], time="nine thirty p.m"))
    assert _checked(cut, cut).decide(said, NOW) == NeedsReview(reason="unsure")


def test_checked_keeps_questions_and_asks_about_a_half_seen_end_time():
    question = _checked(_Fake(Extraction(numbers=["626"])), _Fake(ALLOW)).decide(ROW, NOW)
    assert question == NeedsReview(reason="unclear_action")
    no_time = Extraction(action=Action.ALLOW, numbers=["626"])
    seen = _Fake(no_time, time_near_miss=CFG.time_near_miss)  # GLiNER half-saw a time
    assert _checked(seen, _Fake(no_time)).decide(ROW, NOW) == NeedsReview(reason="unsure")
    assert "not sure" in NeedsReview(reason="unsure").question


def test_unexplained_numbers_are_counted():
    text = "add car 3875 and car 5 6 2 1 until tomorrow"
    plate = [{"start": 8, "end": 12, "label": "plate number"}]
    assert A.loose_numbers(plate, text) == 1  # "5 6 2 1" is explained by nothing
    both = plate + [{"start": 21, "end": 28, "label": "plate number"}]
    assert A.loose_numbers(both, text) == 0


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("add 5055", Extraction(action=Action.ALLOW, numbers=["5055"])),
        ("Remove car 5055.", Extraction(action=Action.REMOVE, numbers=["5055"])),
        ("add 5055 for 2 days",
         Extraction(action=Action.ALLOW, numbers=["5055"], time="for 2 days")),
        ("please allow plate number five zero five five until 6 pm thanks",
         Extraction(action=Action.ALLOW, numbers=["five zero five five"], time="until 6 pm")),
    ],
)  # fmt: skip
def test_fixed_form_reads_the_owners_short_commands(text, expected):
    assert fixed_form(text) == expected


@pytest.mark.parametrize(
    "text",
    ["and car 5055", "let 5055 in", "add 5055 in bay 2", "add 12 and 87", "5055 until tomorrow",
     "is car 5055 allowed"],
)  # fmt: skip
def test_anything_else_goes_to_the_models(text):
    assert fixed_form(text) is None
