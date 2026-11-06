"""Loguru setup: stderr plus a rotating log file."""

import sys

from loguru import logger

from smart_parking.config import LoggingConfig


def setup_logging(cfg: LoggingConfig) -> None:
    """Replace default Loguru sinks with stderr and a rotating file."""
    logger.remove()
    logger.add(sys.stderr, level=cfg.level)
    cfg.file.parent.mkdir(parents=True, exist_ok=True)
    logger.add(cfg.file, level=cfg.level, rotation=cfg.rotation, retention=cfg.retention)
