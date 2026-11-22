"""Per-stay logic for video (made-up plates)."""

from smart_parking.stays import CONFIRM_FRAMES, BayTracker, stay_plate


def test_stay_plate_needs_two_reads_and_a_majority():
    assert stay_plate([]) is None
    assert stay_plate(["G12345"]) is None  # one read could be a misread
    assert stay_plate(["G12345", "G12345", "G12845"]) == "G12345"
    assert stay_plate(["G12345", "G12345", "G12845", "G12845"]) is None  # a tie
    assert stay_plate(["G12345", "G12345", "A1", "B2", "C3"]) is None  # not more than half


def test_a_bay_changes_only_after_enough_frames_in_a_row():
    bay = BayTracker()
    for _ in range(CONFIRM_FRAMES - 1):
        assert bay.update(True, "G12345") == (False, None)  # still arriving
    assert bay.update(True, "G12345") == (True, "G12345")  # reads from the arrival count
    assert bay.update(False, None) == (True, "G12345")  # one empty frame: still parked
    assert bay.update(True, None)[0]
    for _ in range(CONFIRM_FRAMES - 1):
        assert bay.update(False, None)[0]
    assert bay.update(False, None) == (False, None)  # left
    assert bay.reads == []


def test_a_short_flicker_never_becomes_a_stay():
    bay = BayTracker()
    for occupied in [True, True, False, True, False, True, True, True, False]:
        assert bay.update(occupied, "G12345") == (False, None)
