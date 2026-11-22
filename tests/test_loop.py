"""Full loop joining logic, with stand-ins for the three models (made-up plates only)."""

from datetime import datetime, timedelta
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pandas as pd

from smart_parking.commands.schema import Action, NeedsReview, ParsedCommand, PermitTable
from smart_parking.loop import (
    Command,
    bay_status,
    blame,
    judge,
    plan_commands,
    plate_read,
    run_commands,
    spoken_number,
    true_status,
)
from smart_parking.plates.reader import PlateRead

TZ = ZoneInfo("Asia/Dubai")
NOW = datetime(2026, 11, 22, 9, 30, tzinfo=TZ)
READ = PlateRead(emirate="Dubai", text="G12345", confidence=0.9, decision="READ", reason=None,
                 box=(0, 0, 1, 1))  # fmt: skip
ALLOW = ParsedCommand(action=Action.ALLOW, number="12345", until=NOW.replace(hour=18))
YES = lambda q: True  # noqa: E731


def test_an_empty_bay_is_never_checked_against_the_table():
    assert bay_status(False, READ, NOW, PermitTable()) == "EMPTY"


def test_the_same_arrival_follows_the_permit():
    table = PermitTable()
    assert bay_status(True, READ, NOW, table) == "POTENTIALLY_UNAUTHORIZED"
    table.apply(ALLOW, YES)
    assert bay_status(True, READ, NOW, table) == "AUTHORIZED"
    assert bay_status(True, READ, NOW.replace(hour=19), table) == "POTENTIALLY_UNAUTHORIZED"
    table.apply(ParsedCommand(action=Action.REMOVE, number="12345"), YES)
    assert bay_status(True, READ, NOW, table) == "POTENTIALLY_UNAUTHORIZED"


def test_unclear_or_missing_plates_go_to_a_person():
    unclear = READ.model_copy(update={"decision": "NEEDS_REVIEW"})
    assert bay_status(True, unclear, NOW, PermitTable()) == "NEEDS_REVIEW"
    assert bay_status(True, None, NOW, PermitTable()) == "NEEDS_REVIEW"
    assert true_status(True, "", NOW, PermitTable()) == "NEEDS_REVIEW"  # no plate fitted


def test_blame_goes_to_the_first_stage_that_went_wrong():
    assert blame(True, True, "AUTHORIZED", "AUTHORIZED") == ""
    assert blame(True, False, "POTENTIALLY_UNAUTHORIZED", "EMPTY") == "A occupancy"
    assert blame(False, True, "EMPTY", "POTENTIALLY_UNAUTHORIZED") == "A occupancy"
    assert blame(True, True, "AUTHORIZED", "POTENTIALLY_UNAUTHORIZED") == "B plate"


def test_spoken_number_drops_codes():
    assert spoken_number("G12345") == "12345"
    assert spoken_number("AB1234") == "1234"
    assert spoken_number("1012345") == "12345"  # numeric code 10


def test_planned_commands_are_fixed_by_the_seed_and_come_before_arrivals():
    arrivals = {str(n): NOW + timedelta(hours=n % 7) for n in range(10000, 10040)}
    a, b = plan_commands(["55555"], arrivals), plan_commands(["55555"], arrivals)
    assert [c.text for c in a] == [c.text for c in b]
    assert a[0].intended == ParsedCommand(action=Action.ALLOW, number="55555")
    assert all(c.at < arrivals[c.intended.number] for c in a[1:])
    assert {c.intended.action for c in a} == {Action.ALLOW, Action.REMOVE}


def test_the_owner_check_stops_a_wrong_change_from_reaching_the_table(tmp_path):
    wrong = ALLOW.model_copy(update={"number": "1234"})
    answers = iter([wrong, NeedsReview(reason="ambiguous_time"), ALLOW])
    cmds = [Command(NOW, "add car 12345 until 6 pm", ALLOW)] * 3
    tables = run_commands(cmds, lambda row, now: next(answers), tmp_path / "f.jsonl")
    assert list(tables.log["path"]) == ["fixed by owner", "asked", "accepted"]
    assert tables.confirmed.permits == tables.truth.permits == {"12345": tables.truth.permits[
        "12345"]}  # fmt: skip
    assert "1234" in tables.unchecked.permits  # Model C alone would have allowed car 1234


def _bay(truth: int, pred: int, true_plate: str, read: str) -> dict:
    return {"photo": "P1", "bay": "left", "at": NOW, "truth": truth, "pred": pred,
            "true_plate": true_plate, "bay_read": read, "bay_conf": 0.9 if read else "",
            "bay_decision": "READ" if read else ""}  # fmt: skip


def test_judge_joins_occupancy_plate_and_table():
    tables = SimpleNamespace(truth=PermitTable(), confirmed=PermitTable(), unchecked=PermitTable())
    for t in (tables.truth, tables.confirmed):
        t.apply(ALLOW, YES)
    res = pd.DataFrame([
        _bay(1, 1, "Dubai G12345", "Dubai G12345"),  # permitted car, read right
        _bay(1, 1, "Dubai G12345", "Dubai G12845"),  # misread: a false alert, Model B's fault
        _bay(1, 0, "Dubai H11111", ""),  # missed by Model A: an unauthorized car missed
        _bay(0, 0, "", ""),
    ])  # fmt: skip
    j = judge(res, tables)
    assert list(j["true_status"]) == ["AUTHORIZED", "AUTHORIZED", "POTENTIALLY_UNAUTHORIZED",
                                      "EMPTY"]  # fmt: skip
    assert list(j["status"]) == ["AUTHORIZED", "POTENTIALLY_UNAUTHORIZED", "EMPTY", "EMPTY"]
    assert list(j["blame"]) == ["", "B plate", "A occupancy", ""]
    assert list(j["status_no_owner_check"])[0] == "POTENTIALLY_UNAUTHORIZED"  # empty table
    assert plate_read(SimpleNamespace(**_bay(1, 1, "", "Abu Dhabi 1012345"))).emirate == "Abu Dhabi"
