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


class ProjectConfig(BaseModel):
    """Top-level project configuration."""

    model_config = ConfigDict(extra="forbid")

    seed: int = 42
    timezone: str = "Asia/Dubai"
    logging: LoggingConfig = LoggingConfig()


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> ProjectConfig:
    """Load and validate a YAML config file."""
    with Path(path).open() as f:
        return ProjectConfig.model_validate(yaml.safe_load(f) or {})
