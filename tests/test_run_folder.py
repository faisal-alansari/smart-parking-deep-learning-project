"""The folder command never crashes on bad input: each problem comes back structured."""

from smart_parking.output import BayDecision, guidance
from smart_parking.pipeline import _boxes_ok, run_folder


def test_not_a_folder_and_empty_folder(tmp_path):
    r = run_folder(tmp_path / "missing", 2, True)
    assert [p.reason for p in r.problems] == ["empty_folder"]
    r = run_folder(tmp_path, 2, True)
    assert [p.reason for p in r.problems] == ["empty_folder"] and r.decisions == []


def test_bad_files_are_reported_with_guidance(tmp_path):
    (tmp_path / "notes.pdf").write_text("x")
    (tmp_path / "broken.jpg").write_bytes(b"not an image")
    (tmp_path / "commands.txt").write_text("allow car 12345\n# a comment\n\n")
    (tmp_path / "bays.yaml").write_text("boxes: {left: [0.5, 0.2, 0.1, 0.9]}\n")
    reasons = sorted(p.reason for p in run_folder(tmp_path, 2, True).problems)
    assert reasons == ["bad_bays_file", "bad_command_line", "empty_folder", "unreadable_file",
                       "unsupported_file"]  # fmt: skip


def test_boxes_and_guidance():
    assert _boxes_ok({"left": [0.0, 0.4, 0.5, 0.6]})
    assert not _boxes_ok({"left": [0.6, 0.4, 0.5, 0.6]}) and not _boxes_ok(None)
    assert guidance("EMPTY", None) is None and guidance("AUTHORIZED", None) is None
    assert "permit" in guidance("POTENTIALLY_UNAUTHORIZED", None)
    assert "plate" in guidance("NEEDS_REVIEW", "missing_code")
    assert "camera" in guidance("NEEDS_REVIEW", "unfamiliar_view")
    BayDecision(source="a.jpg", time="2026-11-25T21:00:00+04:00", bay="left", status="EMPTY",
                stay_status="EMPTY", occupied=False, occupancy_confidence=0.1)  # fmt: skip
