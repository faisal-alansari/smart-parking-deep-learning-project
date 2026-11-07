from pathlib import Path

import numpy as np
import pytest
import torch

from smart_parking.occupancy.images import load_split
from smart_parking.occupancy.metrics import best_threshold, binary_metrics, cluster_bootstrap_ci
from smart_parking.occupancy.model import OccupancyCNN, count_parameters
from smart_parking.occupancy.train import MAX_SCRATCH_PARAMS, augment


def test_binary_metrics_known_values():
    y = np.array([1, 1, 1, 0, 0, 0, 0, 0])
    p = np.array([1, 1, 0, 1, 0, 0, 0, 0])
    m = binary_metrics(y, p)
    assert m["precision"] == pytest.approx(2 / 3)
    assert m["recall"] == pytest.approx(2 / 3)
    assert m["fpr"] == pytest.approx(1 / 5)
    assert m["accuracy"] == pytest.approx(6 / 8)


def test_best_threshold_separates_clean_scores():
    y = np.array([0] * 50 + [1] * 50)
    score = np.concatenate([np.linspace(0, 0.4, 50), np.linspace(0.6, 1, 50)])
    t = best_threshold(y, score)
    assert binary_metrics(y, score >= t)["f1"] == 1.0


def test_cluster_bootstrap_ci_contains_point_estimate():
    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, 400)
    p = np.where(rng.random(400) < 0.9, y, 1 - y)
    clusters = np.repeat(np.arange(40), 10)
    ci = cluster_bootstrap_ci(y, [p], clusters, n_boot=200)
    f1 = binary_metrics(y, p)["f1"]
    assert ci["f1"][0] <= f1 <= ci["f1"][1]


def test_model_output_and_size():
    model = OccupancyCNN([16, 32, 64, 128], dropout=0.3)
    assert model(torch.zeros(2, 3, 64, 64)).shape == (2,)
    assert count_parameters(model) < MAX_SCRATCH_PARAMS


def test_augment_keeps_shape_and_range():
    gen = torch.Generator().manual_seed(0)
    x = torch.rand(8, 3, 64, 64)
    for mode in ("none", "photo", "photo_hflip"):
        out = augment(x, mode, gen)
        assert out.shape == x.shape
        assert out.min() >= 0 and out.max() <= 1
    assert torch.equal(augment(x, "none", gen), x)


def test_test_splits_are_locked_without_flag():
    with pytest.raises(PermissionError):
        load_split("test_unseen_camera", 64, Path("x.csv"), Path("."), Path("."))
