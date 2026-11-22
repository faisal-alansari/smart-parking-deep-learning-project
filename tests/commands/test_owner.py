"""Model C connected to the permit table: confirmation, correction, feedback, arrival check."""

import json
from datetime import datetime
from zoneinfo import ZoneInfo

from smart_parking.commands.owner import HumanFeedback, arrival_decision, handle
from smart_parking.commands.schema import Action, NeedsReview, ParsedCommand, PermitTable
from smart_parking.plates.reader import PlateRead

TZ = ZoneInfo("Asia/Dubai")
NOW = datetime(2026, 11, 22, 9, 30, tzinfo=TZ)
ALLOW = ParsedCommand(
    action=Action.ALLOW, number="12345", until=datetime(2026, 11, 22, 18, tzinfo=TZ)
)
READ = PlateRead(emirate="Dubai", text="G12345", confidence=0.9, decision="READ", reason=None,
                 box=(0, 0, 1, 1))  # fmt: skip


def _model(result):
    return lambda row, now: result


def test_a_change_is_applied_only_after_the_owner_accepts(tmp_path):
    table, log = PermitTable(), tmp_path / "feedback.jsonl"
    asked = []
    reply = handle("allow car 12345 until 6 pm", NOW, _model(ALLOW), table,
                   lambda q, c: asked.append(q) or None, log)  # fmt: skip
    assert reply.startswith("Rejected") and table.permits == {}
    assert asked == ["Allow car 12345 in either bay until Sun 22 Nov 18:00?"]
    handle("allow car 12345 until 6 pm", NOW, _model(ALLOW), table, lambda q, c: c, log)
    assert arrival_decision(READ, NOW, table) == "AUTHORIZED"
    records = [HumanFeedback(**json.loads(x)) for x in log.read_text().splitlines()]
    assert [r.accepted for r in records] == [False, True]


def test_the_owner_can_reject_and_fix_the_fields(tmp_path):
    table, log = PermitTable(), tmp_path / "feedback.jsonl"
    wrong = ALLOW.model_copy(update={"number": "1234"})
    fixed = lambda q, c: c.model_copy(update={"number": "12345"})  # noqa: E731
    handle("add car 1234 until 6 pm", NOW, _model(wrong), table, fixed, log)
    assert "12345" in table.permits
    record = HumanFeedback(**json.loads(log.read_text()))
    assert not record.accepted and record.corrected.number == "12345"


def test_questions_change_nothing(tmp_path):
    table, log = PermitTable(), tmp_path / "feedback.jsonl"
    reply = handle("add 12345 until 6", NOW, _model(NeedsReview(reason="ambiguous_time")), table,
                   lambda q, c: c, log)  # fmt: skip
    assert reply == "Is that AM or PM?" and table.permits == {} and not log.exists()


def test_arrival_decision_follows_the_permit_and_the_plate_read():
    table = PermitTable()
    assert arrival_decision(READ, NOW, table) == "POTENTIALLY_UNAUTHORIZED"
    table.apply(ALLOW, confirm=lambda q: True)
    assert arrival_decision(READ, NOW, table) == "AUTHORIZED"
    assert arrival_decision(READ, NOW.replace(hour=19), table) == "POTENTIALLY_UNAUTHORIZED"
    unclear = READ.model_copy(update={"decision": "NEEDS_REVIEW", "reason": "low_confidence"})
    assert arrival_decision(unclear, NOW, table) == "NEEDS_REVIEW"
    assert arrival_decision(None, NOW, table) == "NEEDS_REVIEW"
