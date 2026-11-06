"""Global seeding for reproducible runs."""

import os
import random

import numpy as np
import torch
from loguru import logger


def set_seed(seed: int) -> None:
    """Seed Python, NumPy, and PyTorch."""
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    logger.bind(seed=seed).info("Seeds set")
