import pandas as pd

from smart_parking.plates.data.audit import (
    _multiset,
    _order_characters,
    assemble_plates,
    describe_images,
    match_filenames,
)


def _box(image, cls, cx, cy, w, h, source="K-123"):
    return {
        "split": "train",
        "image": image,
        "source": source,
        "cls": cls,
        "cx": cx,
        "cy": cy,
        "w": w,
        "h": h,
    }


def test_one_row_plate_reads_left_to_right():
    chars = pd.DataFrame(
        [
            {"cls": "3", "cx": 0.30, "cy": 0.5, "h": 0.02},
            {"cls": "K", "cx": 0.10, "cy": 0.5, "h": 0.02},
            {"cls": "1", "cx": 0.20, "cy": 0.5, "h": 0.02},
        ]
    )
    assert _order_characters(chars) == "K13"


def test_two_row_plate_reads_top_then_bottom():
    chars = pd.DataFrame(
        [
            {"cls": "5", "cx": 0.2, "cy": 0.60, "h": 0.02},
            {"cls": "A", "cx": 0.1, "cy": 0.50, "h": 0.02},
            {"cls": "4", "cx": 0.1, "cy": 0.60, "h": 0.02},
        ]
    )
    assert _order_characters(chars) == "A/45"


def test_assemble_matches_file_name_and_counts_orphans():
    boxes = pd.DataFrame(
        [
            _box("a.jpg", "plate", 0.5, 0.5, 0.2, 0.1),
            _box("a.jpg", "K", 0.45, 0.5, 0.02, 0.05),
            _box("a.jpg", "1", 0.50, 0.5, 0.02, 0.05),
            _box("a.jpg", "2", 0.53, 0.5, 0.02, 0.05),
            _box("a.jpg", "3", 0.56, 0.5, 0.02, 0.05),
            _box("a.jpg", "old_DUBAI", 0.42, 0.5, 0.03, 0.05),
            _box("a.jpg", "9", 0.9, 0.9, 0.02, 0.05),
        ]
    )
    plates, orphans = assemble_plates(boxes)
    assert orphans == 1
    assert plates.iloc[0]["text"] == "K123"
    assert plates.iloc[0]["plate_type"] == "old_DUBAI"
    images = match_filenames(plates, describe_images(boxes, plates))
    assert images.iloc[0]["match"] == "exact"
    assert images.iloc[0]["identity"] == "name:K-123"


def test_multiset_ignores_separators():
    assert _multiset("K-123") == _multiset("K123") == "123K"
