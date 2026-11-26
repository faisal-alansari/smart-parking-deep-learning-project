"""The sealed final test: scoring helpers, the run-once guard and the split boundary."""

from datetime import datetime
from pathlib import Path

import pytest
import yaml

from smart_parking import final_test as ft
from smart_parking.commands.schema import Action, ParsedCommand
from smart_parking.loop import TZ

CFG = {
    "commands": [
        {"action": "allow", "number": "66705"},
        {"action": "allow", "number": "33044", "until": "2026-11-26T22:09"},
        {"action": "none"},
    ]
}
AT = datetime(2026, 11, 26, 22, 0, tzinfo=TZ)


def test_commands_file_is_read_with_times(tmp_path):
    f = tmp_path / "commands.txt"
    f.write_text("# a comment\n2026-11-26 21:59 | allow car 66705\n\n2026-11-26 22:06 | hi\n")
    assert ft.read_commands(f) == [
        (datetime(2026, 11, 26, 21, 59, tzinfo=TZ), "allow car 66705"),
        (datetime(2026, 11, 26, 22, 6, tzinfo=TZ), "hi"),
    ]


def test_intended_table_expires_the_visitor():
    table = ft.intended_table(CFG)
    assert table.find("AA66705", AT.replace(hour=23))
    assert table.find("O33044", AT)
    assert not table.find("O33044", AT.replace(minute=10))


def test_command_score():
    until = datetime(2026, 11, 26, 22, 9, tzinfo=TZ)
    right = ParsedCommand(action=Action.ALLOW, number="33044", until=until)
    assert ft.command_score(right, CFG["commands"][1])
    assert not ft.command_score(right.model_copy(update={"until": None}), CFG["commands"][1])
    assert not ft.command_score(right, CFG["commands"][0])  # wrong number
    assert ft.command_score(None, CFG["commands"][2])  # off-topic: no change is right
    assert not ft.command_score(right, CFG["commands"][2])


def test_final_test_needs_the_owner_check(tmp_path, monkeypatch):
    cfg = tmp_path / "night_3.yaml"
    cfg.write_text(yaml.safe_dump({"truth_status": "pending the owner check"}))
    monkeypatch.setattr(ft, "CONFIG", cfg)
    monkeypatch.setattr("sys.argv", ["final_test"])
    with pytest.raises(SystemExit, match="checked by the owner"):
        ft.main()


def test_final_test_runs_only_once(tmp_path, monkeypatch):
    cfg = tmp_path / "night_3.yaml"
    cfg.write_text(yaml.safe_dump({"truth_status": "checked by the owner (today)"}))
    frames = tmp_path / "out" / "local" / "night_3_frames.csv"
    frames.parent.mkdir(parents=True)
    frames.write_text("t\n0\n")
    monkeypatch.setattr(ft, "CONFIG", cfg)
    monkeypatch.setattr(ft, "OUT", tmp_path / "out")
    monkeypatch.setattr(ft, "FRAMES", frames)
    monkeypatch.setattr("sys.argv", ["final_test"])
    with pytest.raises(SystemExit, match="already been run once"):
        ft.main()


def test_the_test_video_is_never_in_training_or_validation():
    """Only the night 3 config names the sealed test folder; the training config never does."""
    for config in Path("configs").glob("*.yaml"):
        text = config.read_text()
        if config.name != "local_video_night_3.yaml":
            assert "video_test" not in text, config
    train = yaml.safe_load(Path("configs/local_video_night_2.yaml").read_text())
    assert {f["split"] for f in train["files"]} == {"train", "validation"}
