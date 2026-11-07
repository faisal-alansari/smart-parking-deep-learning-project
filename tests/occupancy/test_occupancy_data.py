import pandas as pd
import pytest

from smart_parking.occupancy.data.sample import balance_train, mark_near_copies
from smart_parking.occupancy.data.split import assign_splits, check_no_leakage, quality_flags


def _manifest() -> pd.DataFrame:
    rows = []
    for cam in ["C01", "C02", "C03"]:
        for day in ["2015-11-12", "2015-11-13", "2015-11-14"]:
            for slot in range(4):
                rows.append(
                    {
                        "crop_id": f"{cam}_{slot}_{day}",
                        "camera": cam,
                        "source": "CNR-EXT",
                        "slot_id": slot,
                        "date": day,
                        "timestamp": f"{day} 08:00",
                        "label": slot % 2,
                        "md5": f"{cam}{slot}{day}",
                        "dhash": f"{slot:016x}",
                        "brightness": 100.0,
                        "contrast": 20.0,
                        "label_agrees": True,
                    }
                )
    rows.append({**rows[0], "crop_id": "A_1", "camera": "A", "source": "CNRPark", "md5": "a"})
    return pd.DataFrame(rows)


DAYS = {"train": {"2015-11-12"}, "val": {"2015-11-13"}, "test": {"2015-11-14"}}


def test_held_out_camera_and_site_never_in_train():
    m = _manifest()
    m["split"] = assign_splits(m, DAYS, ["C02"], ["CNRPark"])
    assert set(m.loc[m["camera"] == "C02", "split"]) == {"test_unseen_camera"}
    assert set(m.loc[m["source"] == "CNRPark", "split"]) == {"test_unseen_site"}
    check_no_leakage(m)


def test_leakage_check_catches_shared_file():
    m = _manifest()
    m["split"] = assign_splits(m, DAYS, ["C02"], ["CNRPark"])
    m.loc[m.index[:2], "md5"] = "same"
    m.loc[m.index[0], "split"], m.loc[m.index[1], "split"] = "train", "val"
    with pytest.raises(ValueError):
        check_no_leakage(m)


def test_quality_flags():
    m = _manifest()
    m.loc[0, "contrast"] = 0.0
    m.loc[1, "brightness"] = 5.0
    m.loc[2, "label_agrees"] = False
    flags = quality_flags(m, dark_threshold=15)
    assert list(flags[:4]) == ["blank_image", "too_dark_to_verify", "label_conflict", ""]


def test_near_copies_keep_label_changes():
    m = pd.DataFrame(
        {
            "camera": "C01",
            "slot_id": 1,
            "timestamp": ["t1", "t2", "t3", "t4"],
            "dhash": ["0" * 16, "0" * 15 + "1", "f" * 16, "f" * 16],
            "label": [0, 0, 0, 1],
        }
    )
    assert mark_near_copies(m, max_distance=4).tolist() == [False, True, False, False]


def test_balance_gives_equal_classes():
    m = _manifest()
    idx = balance_train(m, target_per_class=10, seed=0)
    counts = m.loc[idx, "label"].value_counts()
    assert counts[0] == counts[1] == 10
