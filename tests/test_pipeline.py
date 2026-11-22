"""Helpers of the folder/video pipeline and the ablation (no models needed; made-up plates)."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

from smart_parking.ablation import no_end_times, statuses
from smart_parking.commands.schema import Action, ParsedCommand, PermitTable
from smart_parking.pipeline import _alerts, clock, in_any, timeline, video_truth

NOW = datetime(2026, 11, 22, 9, 30, tzinfo=ZoneInfo("Asia/Dubai"))
CFG = {"boxes": {"left": [], "right": []},
       "cars": [{"bay": "right", "from": 10, "to": 20, "plate": "G12345"},
                {"bay": "both", "from": 30, "to": 40, "plate": "H54321"}]}  # fmt: skip


def test_video_truth_follows_the_car_intervals():
    assert video_truth(CFG, 5) == {"left": "", "right": ""}
    assert video_truth(CFG, 10) == {"left": "", "right": "G12345"}
    assert video_truth(CFG, 20) == {"left": "", "right": ""}  # end is not included
    assert video_truth(CFG, 35) == {"left": "H54321", "right": "H54321"}  # across both bays
    assert in_any(29.9, [[28, 48]]) and not in_any(48, [[28, 48]])
    assert clock(125) == "2:05"


def test_timeline_and_alert_episodes():
    g = pd.DataFrame({"bay": "left", "t": range(6), "clock": [clock(t) for t in range(6)],
                      "status": ["EMPTY", "POTENTIALLY_UNAUTHORIZED", "POTENTIALLY_UNAUTHORIZED",
                                 "EMPTY", "POTENTIALLY_UNAUTHORIZED", "EMPTY"]})  # fmt: skip
    runs = timeline(g)
    assert list(runs["frames"]) == [1, 2, 1, 1, 1]
    assert (runs.iloc[1]["from"], runs.iloc[1]["to"]) == ("0:01", "0:02")
    assert _alerts(g, "status") == 2  # two separate alert episodes


def test_ablation_variants():
    table = PermitTable()
    table.apply(ParsedCommand(action=Action.ALLOW, number="12345", until=NOW), lambda q: True)
    assert no_end_times(table).find("G12345", NOW.replace(hour=23)) is not None
    assert table.find("G12345", NOW.replace(hour=23)) is None
    res = pd.DataFrame([{"pred": 1}, {"pred": 0}])
    assert statuses(res, table, plates=False) == ["NEEDS_REVIEW", "EMPTY"]
