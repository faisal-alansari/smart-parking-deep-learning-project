"""Model A adaptation helpers (no video or model needed)."""

import numpy as np

from smart_parking.occupancy.adapt import (
    balanced,
    best_balanced_threshold,
    summary_row,
    truth,
    video_files,
    vote,
)


def test_balanced_accuracy_weighs_both_classes_equally():
    y = np.array([1, 1, 1, 1, 0])
    assert balanced(y, np.ones(5, bool)) == 0.5  # all "occupied": empty bay always wrong
    assert balanced(y, y.astype(bool)) == 1.0


def test_threshold_and_vote():
    y = np.array([0, 0, 1, 1])
    t, score = best_balanced_threshold(y, np.array([0.1, 0.2, 0.7, 0.9]))
    assert score == 1.0 and 0.2 < t <= 0.7
    probs = [np.array([0.9, 0.1]), np.array([0.6, 0.4]), np.array([0.2, 0.8])]
    assert list(vote(probs, [0.5, 0.5, 0.5])) == [True, False]  # two of three


def test_truth_counts_a_car_across_both_bays_in_both():
    cars = [{"bay": "both", "from": 0, "to": 10}, {"bay": "right", "from": 20, "to": 30}]
    assert (truth(cars, "left", 5), truth(cars, "right", 5)) == (1, 1)
    assert (truth(cars, "left", 25), truth(cars, "right", 25), truth(cars, "right", 30)) == (
        0,
        1,
        0,
    )
    row = summary_row(np.array([1, 0, 1]), np.array([False, True, True]))
    assert (row["parked cars missed"], row["empty bays called occupied"]) == (1, 1)


def test_both_video_config_formats():
    single = {"video": "v.MOV", "cars": [], "moving": [[1, 2]], "straddle": [[3, 4]]}
    files = video_files(single)
    assert files[0]["split"] == "test" and files[0]["slices"]["car across both bays"] == [[3, 4]]
    assert video_files({"files": [{"video": "a"}]}) == [{"video": "a"}]
