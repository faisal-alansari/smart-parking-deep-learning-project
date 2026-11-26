"""The folder command never crashes on bad input: each problem comes back structured."""

from smart_parking.output import BayDecision, guidance
from smart_parking.pipeline import _boxes_ok, run_folder


def _out(tmp_path):  # noqa: ANN001, ANN202
    """Results go beside the input folder, never inside it."""
    return tmp_path.parent / f"{tmp_path.name}_runs"


def test_confirmation_without_stdin_never_accepts(monkeypatch):
    from smart_parking.commands.schema import Action, ParsedCommand
    from smart_parking.pipeline import ask_owner

    def closed_stdin(prompt):
        raise EOFError

    monkeypatch.setattr("builtins.input", closed_stdin)
    change = ParsedCommand(action=Action.ALLOW, number="12345")
    assert ask_owner("Confirm?", change) is None


def test_not_a_folder_and_empty_folder(tmp_path):
    r = run_folder(tmp_path / "missing", 2, True, _out(tmp_path))
    assert [p.reason for p in r.problems] == ["empty_folder"]
    r = run_folder(tmp_path, 2, True, _out(tmp_path))
    assert [p.reason for p in r.problems] == ["empty_folder"] and r.decisions == []


def test_bad_files_are_reported_with_guidance(tmp_path):
    (tmp_path / "notes.pdf").write_text("x")
    (tmp_path / "broken.jpg").write_bytes(b"not an image")
    (tmp_path / "commands.txt").write_text("allow car 12345\n# a comment\n\n")
    (tmp_path / "bays.yaml").write_text("boxes: {left: [0.5, 0.2, 0.1, 0.9]}\n")
    reasons = sorted(p.reason for p in run_folder(tmp_path, 2, True, _out(tmp_path)).problems)
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


def test_invalid_options_and_missing_folders_still_write_a_result(tmp_path):
    for every in (0, -2, float("nan")):
        r = run_folder(tmp_path, every, True, _out(tmp_path))
        assert [p.reason for p in r.problems] == ["bad_option"]
    r = run_folder(tmp_path / "missing", 2, True, _out(tmp_path))
    assert (_out(tmp_path) / "missing" / "result.json").exists()
    empty = tmp_path / "empty"
    empty.mkdir()
    run_folder(empty, 2, True, _out(tmp_path))
    assert (_out(tmp_path) / "empty" / "result.json").exists()


def test_commands_that_are_not_utf8_are_reported(tmp_path):
    (tmp_path / "commands.txt").write_bytes(b"\xff\xfe 2026-11-22 09:05 | allow car 12\x00")
    r = run_folder(tmp_path, 2, True, _out(tmp_path))
    assert {p.reason for p in r.problems} == {"unreadable_file", "empty_folder"}


def test_a_broken_camera_setup_never_judges_photos(tmp_path):
    from PIL import Image

    Image.new("RGB", (64, 48)).save(tmp_path / "a.jpg")
    for bays in ("boxes: {}\n", "boxes: {left: [0.1, 0.1, 0.9, 0.9]}\nsnapshot: gone.jpg\n"):
        (tmp_path / "bays.yaml").write_text(bays)
        r = run_folder(tmp_path, 2, True, _out(tmp_path))
        assert r.decisions == []
        assert {p.reason for p in r.problems} == {"bad_bays_file", "camera_not_set_up"}


def test_owner_fixes_in_the_demo_are_validated():
    from smart_parking.app import corrected
    from smart_parking.commands.schema import Action, ParsedCommand

    proposal = ParsedCommand(action=Action.ALLOW, number="12345")
    assert corrected(proposal, "54321", "").number == "54321"
    assert corrected(proposal, "54321", "2026-11-26 18:00").until.tzinfo is not None
    assert corrected(proposal, "12a45", "") is None
    assert corrected(proposal, "12345", "tomorrow at six") is None
