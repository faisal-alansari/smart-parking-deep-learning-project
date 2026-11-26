"""Video safety: a blocked camera stays visible; cached reads are not new evidence."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from smart_parking.commands.schema import Action, ParsedCommand, PermitTable
from smart_parking.pipeline import run_folder
from smart_parking.plates.reader import PlateRead
from smart_parking.stays import (
    CONFIRM_FRAMES,
    SETTLE_READS,
    UNKNOWN,
    BayTracker,
    apply_stays,
    stay_status,
    stay_update,
)

AT = datetime(2026, 11, 26, 21, 0, tzinfo=ZoneInfo("Asia/Dubai"))


def _table(until: datetime | None = None) -> PermitTable:
    table = PermitTable()
    change = ParsedCommand(action=Action.ALLOW, number="12345", until=until)
    table.apply(change, confirm=lambda q: True)
    return table


def _parked(tracker: BayTracker) -> None:
    for _ in range(CONFIRM_FRAMES):
        stay_update(tracker, 1, "G12345")


def test_blocked_camera_on_an_empty_bay_goes_to_a_person():
    occ, plate, judged = stay_update(BayTracker(), UNKNOWN, None)
    assert (occ, plate, judged) == (False, None, False)
    assert stay_status(occ, plate, AT, PermitTable(), judged) == "NEEDS_REVIEW"


def test_blocked_camera_keeps_the_stay_and_recovers():
    tracker = BayTracker(settle_after=SETTLE_READS)
    _parked(tracker)
    for _ in range(CONFIRM_FRAMES * 2):  # far longer than it takes to end a stay
        occ, plate, judged = stay_update(tracker, UNKNOWN, None)
        assert stay_status(occ, plate, AT, _table(), judged) == "NEEDS_REVIEW"
    occ, plate, judged = stay_update(tracker, 1, None)  # view is back; the car never left
    assert stay_status(occ, plate, AT, _table(), judged) == "AUTHORIZED"


def test_unknown_frames_neither_confirm_nor_cancel_an_arrival():
    tracker = BayTracker()
    for occupied in [1, 1, UNKNOWN, UNKNOWN, 1, 1]:
        occ, _, _ = stay_update(tracker, occupied, "G12345")
    assert not occ  # four judged frames so far
    assert stay_update(tracker, 1, "G12345")[0]  # the fifth judged frame confirms it


def test_cached_reads_and_a_hidden_plate_do_not_change_the_stay():
    tracker = BayTracker(settle_after=SETTLE_READS)
    _parked(tracker)
    assert not tracker.needs_read
    reads = list(tracker.reads)
    for _ in range(10):  # cached (None) or a person standing in front of the plate
        occ, plate, judged = stay_update(tracker, 1, None)
    assert tracker.reads == reads and plate == "G12345" and judged


def test_a_permit_that_expires_during_a_stay_changes_the_answer():
    table = _table(until=AT + timedelta(minutes=5))
    assert stay_status(True, "G12345", AT, table) == "AUTHORIZED"
    assert stay_status(True, "G12345", AT + timedelta(minutes=6), table) == (
        "POTENTIALLY_UNAUTHORIZED"
    )


def test_replay_marks_blocked_frames_for_review():
    rows = [{"t": 2.0 * i, "bay": "left", "occupied": 1, "plate": "Dubai G12345",
             "plate_decision": "READ"} for i in range(CONFIRM_FRAMES + 2)]  # fmt: skip
    rows += [{"t": 2.0 * (CONFIRM_FRAMES + 2 + i), "bay": "left", "occupied": UNKNOWN,
              "plate": "", "plate_decision": ""} for i in range(8)]  # fmt: skip
    out = apply_stays(pd.DataFrame(rows), AT, _table())
    assert out.stay_status.iloc[CONFIRM_FRAMES] == "AUTHORIZED"
    assert (out.stay_status.iloc[-8:] == "NEEDS_REVIEW").all()
    assert (out.stay_status_visitor.iloc[-8:] == "NEEDS_REVIEW").all()


class _FakePipe:
    """Stands in for the models: a scripted occupancy per frame for one bay."""

    def __init__(self, script: list[int]) -> None:
        self.script, self.i, self.cached_seen = script, 0, 0

    def frame(self, im, boxes, at, table, guard=None, cached=None):  # noqa: ANN001, ANN201
        occupied = self.script[min(self.i, len(self.script) - 1)]
        self.i += 1
        cached = cached or {}
        self.cached_seen += "left" in cached
        if occupied == UNKNOWN:
            return [{"bay": "left", "occupied": UNKNOWN, "occupancy_p": None,
                     "status": "NEEDS_REVIEW", "reason": "camera_blocked", "plate": "",
                     "plate_decision": "", "read": None}]  # fmt: skip
        read = cached.get("left") or PlateRead(
            emirate="Dubai", text="G12345", confidence=0.9, decision="READ", reason=None,
            box=(0.1, 0.1, 0.2, 0.2),
        )  # fmt: skip
        return [{"bay": "left", "occupied": occupied, "occupancy_p": 0.95, "status": "AUTHORIZED",
                 "reason": "", "plate": "Dubai G12345", "plate_decision": "READ",
                 "read": read if occupied else None}]  # fmt: skip

    def timing(self) -> pd.DataFrame:
        return pd.DataFrame()


def _video(path, frames: int) -> None:  # noqa: ANN001
    import cv2

    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), 1, (64, 48))
    for _ in range(frames):
        writer.write(np.full((48, 64, 3), 90, np.uint8))
    writer.release()


def test_folder_run_keeps_a_blocked_camera_visible(tmp_path):
    folder = tmp_path / "cam"
    folder.mkdir()
    (folder / "bays.yaml").write_text("boxes: {left: [0.1, 0.1, 0.9, 0.9]}\n")
    script = [1] * 8 + [UNKNOWN] * 4 + [1] * 3
    _video(folder / "clip.mp4", len(script))
    pipe = _FakePipe(script)
    result = run_folder(folder, 1, True, tmp_path / "runs", _table(), {"final": pipe})
    stays = [d.stay_status for d in result.decisions]
    assert stays[CONFIRM_FRAMES - 1] == "AUTHORIZED"
    assert stays[8:12] == ["NEEDS_REVIEW"] * 4  # never shown as EMPTY or AUTHORIZED
    assert all("camera" in d.guidance for d in result.decisions[8:12])
    assert result.decisions[8].evidence  # the change to review is notified with a frame
    assert stays[-1] == "AUTHORIZED"  # the view came back and the car never left
    assert pipe.cached_seen > 0  # the settled plate was reused, not re-read
    assert (tmp_path / "runs" / "cam" / "result.json").exists()
