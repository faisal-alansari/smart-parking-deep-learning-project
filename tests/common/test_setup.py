import random

import numpy as np
import torch

from smart_parking.common.config import load_config
from smart_parking.common.seed import set_seed


def test_default_config_loads():
    cfg = load_config()
    assert cfg.seed == 42
    assert cfg.timezone == "Asia/Dubai"


def test_set_seed_is_reproducible():
    set_seed(7)
    a = (random.random(), np.random.rand(), torch.rand(1).item())
    set_seed(7)
    b = (random.random(), np.random.rand(), torch.rand(1).item())
    assert a == b
