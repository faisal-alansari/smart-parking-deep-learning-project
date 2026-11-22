# Smart Parking task runner. Run `just` to list recipes.

default:
    @just --list

# Install all dependencies from uv.lock
install:
    uv sync --frozen

# Build the occupancy manifest, inspection sheets, splits and sampled dataset
prepare-data:
    uv run python -m smart_parking.occupancy.data.prepare

# Fit the two occupancy baselines (train + validation only)
occupancy-baselines:
    uv run python -m smart_parking.occupancy.baselines

# Run the OccupancyCNN training-choice experiments (validation only)
occupancy-experiments:
    uv run python -m smart_parking.occupancy.experiments

# Train the selected OccupancyCNN once per seed
train-occupancy:
    uv run python -m smart_parking.occupancy.final --train

# Final comparison of baselines and OccupancyCNN on the test splits
evaluate-occupancy:
    uv run python -m smart_parking.occupancy.final --evaluate

# Check the public-data CNN on the owner's own bay photos (data/raw/local_pilot)
occupancy-local-pilot:
    uv run python -m smart_parking.occupancy.local_pilot --config configs/local_pilot.yaml

# Full loop on the night photo set (43 photos, shared bay boxes), then the error probes
local-night-1:
    uv run python -m smart_parking.occupancy.local_pilot --config configs/local_night_1.yaml
    uv run python -m smart_parking.occupancy.local_probes --config configs/local_night_1.yaml

# Evidence for the plate reader rules: label counts and validation scores (no test data)
plate-rule-evidence:
    uv run python -m smart_parking.plates.rule_evidence

# Audit the AddingUAE plate data: counts, label checks, duplicates, leakage
audit-plates:
    uv run python -m smart_parking.plates.data.audit

# Build the plate fine-tuning subset, leakage-safe splits, YOLO folders and item ledger
prepare-plates:
    uv run python -m smart_parking.plates.data.split

# Download the pretrained YOLO11n weights (Ultralytics release asset)
download-weights:
    YOLO_OFFLINE=1 uv run python -c "from ultralytics import YOLO; YOLO('checkpoints/plates/pretrained/yolo11n.pt')"

# YOLO11n training-choice experiments and from-scratch baseline (validation only)
plate-experiments:
    uv run python -m smart_parking.plates.experiments

# Train the selected YOLO11n settings once per seed
train-plates:
    uv run python -m smart_parking.plates.final --train

# Final comparison of fine-tuned YOLO11n and the from-scratch baseline on the test split
evaluate-plates:
    uv run python -m smart_parking.plates.final --evaluate

# Generate the owner-command sets for Model C (dev + frozen test; no training)
command-data:
    uv run python -m smart_parking.commands.dataset

# Download the pretrained Model C candidates (pinned revisions, local weights only)
download-command-models:
    uv run python -m smart_parking.commands.candidates --download

# Measure the Model C candidates: parameters, licence, disk, memory, time per command (dev)
command-candidates:
    HF_HUB_OFFLINE=1 uv run python -m smart_parking.commands.candidates --measure

# Score a Model C parser (oracle, rules, smollm2, flan-t5, gliner-minilm) on dev; test needs --final
command-score parser split="dev" *flags:
    HF_HUB_OFFLINE=1 uv run python -m smart_parking.commands.score {{parser}} {{split}} {{flags}}

# Model C robustness: 5 increasing levels of damaged or hostile commands (no tuning)
command-robustness:
    HF_HUB_OFFLINE=1 uv run python -m smart_parking.commands.robustness

# Model C demo: the same arrival before, during and after a permit, with owner confirmation
command-demo:
    HF_HUB_OFFLINE=1 uv run python -m smart_parking.commands.owner --demo

# Run tests
test:
    uv run pytest

# Lint and format check
lint:
    uv run ruff check .
    uv run ruff format --check .

# Remove caches and logs
clean:
    rm -rf .pytest_cache .ruff_cache logs
    find . -type d -name __pycache__ -prune -exec rm -rf {} +

# Full loop story on the owner's photos: all three models and the permit table (local only)
full-loop-scenario:
    HF_HUB_OFFLINE=1 uv run python -m smart_parking.loop --scenario

# Full loop on every local bay against the truth, with blame per stage (counts-only summary)
full-loop:
    HF_HUB_OFFLINE=1 uv run python -m smart_parking.loop --evaluate
