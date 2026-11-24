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

    raw_root: Path = Path("data/raw/cnrpark")
    processed_dir: Path = Path("data/processed/occupancy")
    report_dir: Path = Path("outputs/occupancy/data")
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

    dataset_csv: Path = Path("data/processed/occupancy/occupancy_dataset.csv")
    raw_root: Path = Path("data/raw/cnrpark")
    cache_dir: Path = Path("data/processed/occupancy/cache")
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
    # Checkpoints the product uses: "final" (public data only) or "adapted" (owner's camera)
    deploy: str = "final"
    # An option replaces the current choice only if validation F1 rises by more than this
    min_val_gain: float = 0.002
    # Baselines
    baseline_size: int = 64
    hog_c_grid: list[float] = [0.001, 0.003, 0.01, 0.1, 1.0]
    # Evaluation
    bootstrap_samples: int = 1000


class PlateDataConfig(BaseModel):
    """Paths and rules for auditing and preparing the AddingUAE plate data."""

    model_config = ConfigDict(extra="forbid")

    raw_root: Path = Path("data/raw/adding_uae")
    processed_dir: Path = Path("data/processed/plates")
    report_dir: Path = Path("outputs/plates/data")
    workers: int = 8
    near_duplicate_max_distance: int = 4
    # Fine-tuning subset (agreed 2026-11-07)
    subset_total: int = 7000
    val_size: int = 1000
    test_size: int = 1000
    finetune_cap: int = 10000
    manual_review_file: Path = Path("configs/plates_manual_review.yaml")
    # Too few examples to train or test; the product sends these to human review.
    review_only_emirates: list[str] = ["Umm Al Quwain", "unknown"]


class PlateTrainConfig(BaseModel):
    """YOLO11n fine-tuning, plate reading thresholds and evaluation settings."""

    model_config = ConfigDict(extra="forbid")

    yolo_dir: Path = Path("data/processed/plates/yolo")
    ledger_csv: Path = Path("outputs/plates/data/finetune_ledger.csv")
    pretrained_weights: Path = Path("checkpoints/plates/pretrained/yolo11n.pt")
    run_dir: Path = Path("experiments/plates")
    checkpoint_dir: Path = Path("checkpoints/plates")
    results_dir: Path = Path("outputs/plates")
    device: str = "mps"
    workers: int = 4
    batch: int = 16
    epochs: int = 30
    patience: int = 10
    imgsz: int = 640
    # None = full fine-tuning; 23 = freeze layers 0-22 (train the detection head only)
    freeze: int | None = None
    train_size: int = 5000
    seeds: list[int] = [42, 43, 44]
    conf_grid: list[float] = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    min_val_gain: float = 0.005
    bootstrap_samples: int = 1000


class CommandsConfig(BaseModel):
    """Model C (owner commands): evaluation command sets and results."""

    model_config = ConfigDict(extra="forbid")

    data_dir: Path = Path("outputs/commands/data")
    results_dir: Path = Path("outputs/commands")
    dev_seed: int = 1
    test_seed: int = 2
    check_seed: int = 3  # extra set in dev wording (became a second dev set)
    confirm_seed: int = 4  # opened once to confirm; it then showed 2 dangerous (became dev)
    confirm2_seed: int = 5  # opened once; it showed 2 dangerous answers (became dev)
    confirm3_seed: int = 6  # opened once; it showed 1 dangerous answer (became dev)
    confirm4_seed: int = 7  # opened once, only to confirm the final design before the test
    # Pretrained candidates (local weights only, no fine-tuning)
    weights_dir: Path = Path("checkpoints/commands/pretrained")
    device: str = "cpu"
    threads: int = 4
    # GLiNER + MiniLM candidate (set on dev only)
    gliner_threshold: float = 0.2
    # Safe combination (`checked`): an allow without an end time is asked about when GLiNER
    # half-saw an end time scoring at least this (set on dev)
    time_near_miss: float = 0.05
    # A change needs a word this close in meaning to an action word (MiniLM; set on dev)
    action_word_min: float = 0.6


class DecisionConfig(BaseModel):
    """Operating thresholds chosen by expected cost on validation (`just costs`)."""

    model_config = ConfigDict(extra="forbid")

    occupancy_threshold: float = 0.5  # on the mean probability of the Model A seeds
    occupancy_review_band: float = 0.0  # unsure (ask a person) within this distance of it
    plate_min_confidence: float = 0.0  # calibrated plate confidence below this: ask a person
    plate_platt_a: float = 1.0  # Platt scaling of the plate confidence (`just calibration`)
    plate_platt_b: float = 0.0
    cost_false_alert: float = 5.0
    cost_missed_unauthorized: float = 10.0
    cost_review: float = 1.0
    p_authorized: float = 0.7


class ProjectConfig(BaseModel):
    """Top-level project configuration."""

    model_config = ConfigDict(extra="forbid")

    seed: int = 42
    timezone: str = "Asia/Dubai"
    logging: LoggingConfig = LoggingConfig()
    occupancy_data: OccupancyDataConfig = OccupancyDataConfig()
    occupancy: OccupancyTrainConfig = OccupancyTrainConfig()
    plate_data: PlateDataConfig = PlateDataConfig()
    plates: PlateTrainConfig = PlateTrainConfig()
    commands: CommandsConfig = CommandsConfig()
    decision: DecisionConfig = DecisionConfig()


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> ProjectConfig:
    """Load and validate a YAML config file."""
    with Path(path).open() as f:
        return ProjectConfig.model_validate(yaml.safe_load(f) or {})
