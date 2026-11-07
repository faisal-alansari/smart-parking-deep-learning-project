"""Typed project configuration loaded from YAML."""

from pathlib import Path

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


class ProjectConfig(BaseModel):
    """Top-level project configuration."""

    model_config = ConfigDict(extra="forbid")

    seed: int = 42
    timezone: str = "Asia/Dubai"
    logging: LoggingConfig = LoggingConfig()
    occupancy_data: OccupancyDataConfig = OccupancyDataConfig()


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> ProjectConfig:
    """Load and validate a YAML config file."""
    with Path(path).open() as f:
        return ProjectConfig.model_validate(yaml.safe_load(f) or {})
