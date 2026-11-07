from smart_parking.plates.metrics import edit_distance, score_image, summarise
from smart_parking.plates.reader import Box, check_text, read_plates


def _plate(chars, emirate_type="old_DUBAI", conf=0.9):
    boxes = [Box("plate", conf, 0, 0, 100, 40)]
    for i, ch in enumerate(chars):
        boxes.append(Box(ch, conf, 10 + i * 12, 10, 20 + i * 12, 30))
    if emirate_type:
        boxes.append(Box(emirate_type, conf, 2, 30, 8, 38))
    return boxes


def test_reads_plate_text_and_emirate():
    (r,) = read_plates(_plate("K12345"), min_conf=0.25)
    assert (r.emirate, r.text, r.decision) == ("Dubai", "K12345", "READ")


def test_missing_emirate_goes_to_review():
    (r,) = read_plates(_plate("K12345", emirate_type=None), min_conf=0.25)
    assert r.decision == "NEEDS_REVIEW" and r.reason == "no_emirate"


def test_low_confidence_boxes_are_ignored():
    assert read_plates(_plate("K12345", conf=0.1), min_conf=0.25) == []


def test_duplicate_character_boxes_keep_the_most_confident():
    boxes = _plate("K1")
    boxes.append(Box("7", 0.5, 22, 10, 32, 30))  # overlaps the "1"
    (r,) = read_plates(boxes, min_conf=0.25)
    assert r.text == "K1"


def test_check_text_rules():
    assert check_text("K12345") is None
    assert check_text("ABC12") == "too_many_letters"
    assert check_text("K") == "invalid_length"


def test_metrics_count_misreads_and_reviews():
    truth = read_plates(_plate("K12345"), 0.25)[0]
    good = score_image(truth, read_plates(_plate("K12345"), 0.25))
    bad = score_image(truth, read_plates(_plate("K12346"), 0.25))
    review = score_image(truth, read_plates(_plate("K12345", emirate_type=None), 0.25))
    s = summarise([good, bad, review])
    assert s["exact_match"] == 1 / 3
    assert s["misread_rate"] == 1 / 3
    assert s["coverage"] == 2 / 3
    assert edit_distance("K12345", "K12346") == 1


def test_ci_over_seeds_brackets_the_mean():
    from smart_parking.plates.final import _ci_over_seeds

    row_ok = {"found": True, "answered": True, "correct": True, "emirate_ok": True, "cer": 0.0}
    row_bad = {**row_ok, "correct": False, "cer": 0.5}
    a = [row_ok] * 8 + [row_bad] * 2
    b = [row_ok] * 9 + [row_bad] * 1
    ci = _ci_over_seeds([a, b], n_boot=200)
    assert ci["exact_match"][0] <= 0.85 <= ci["exact_match"][1]
