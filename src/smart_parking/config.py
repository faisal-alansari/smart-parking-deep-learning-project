"""Typed project configuration loaded from YAML."""

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict

DEFAULT_CONFIG_PATH = Path("configs/default.yaml")


class LoggingConfig(BaseModel):
    """Loguru settings."""

    model_config = ConfigDict(extra="forbid")

    level: str = "INFO"
    file: Path = Path("logs/smart_parking.log")
    rotation: str = "10 MB"
    retention: int = 5


class OccupancyDataConfig(BaseModel):
    """Paths and rules for preparing the occupancy (CNRPark+EXT) data."""

    model_config = ConfigDict(extra="forbid")

    raw_root: Path = Path("data/CNN-training")
    processed_dir: Path = Path("data/processed")
    report_dir: Path = Path("outputs/data")
    workers: int = 8
    # Splitting
    unseen_cameras: list[str] = []
    unseen_site_sources: list[str] = ["CNRPark"]
    # Quality filter: crops darker than this mean brightness cannot be checked by eye
    dark_threshold: float = 15.0
    # Near-copy removal and balancing
    near_copy_max_distance: int = 4
    train_target_per_class: int = 20000


class OccupancyTrainConfig(BaseModel):
    """Baselines, OccupancyCNN training and evaluation settings."""

    model_config = ConfigDict(extra="forbid")

    dataset_csv: Path = Path("data/processed/occupancy_dataset.csv")
    raw_root: Path = Path("data/CNN-training")
    cache_dir: Path = Path("data/processed/cache")
    run_dir: Path = Path("experiments/occupancy")
    checkpoint_dir: Path = Path("checkpoints/occupancy")
    results_dir: Path = Path("outputs/occupancy")
    # OccupancyCNN
    input_size: int = 64
    channels: list[int] = [16, 32, 64, 128]
    dropout: float = 0.3
    augment: Literal["none", "photo", "photo_hflip"] = "photo"
    batch_size: int = 256
    epochs: int = 15
    lr: float = 1e-3
    weight_decay: float = 1e-4
    seeds: list[int] = [42, 43, 44]
    # An option replaces the current choice only if validation F1 rises by more than this
    min_val_gain: float = 0.002
    # Baselines
    baseline_size: int = 64
    hog_c_grid: list[float] = [0.001, 0.003, 0.01, 0.1, 1.0]
    # Evaluation
    bootstrap_samples: int = 1000


class ProjectConfig(BaseModel):
    """Top-level project configuration."""

    model_config = ConfigDict(extra="forbid")

    seed: int = 42
    timezone: str = "Asia/Dubai"
    logging: LoggingConfig = LoggingConfig()
    occupancy_data: OccupancyDataConfig = OccupancyDataConfig()
    occupancy: OccupancyTrainConfig = OccupancyTrainConfig()


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> ProjectConfig:
    """Load and validate a YAML config file."""
    with Path(path).open() as f:
        return ProjectConfig.model_validate(yaml.safe_load(f) or {})
