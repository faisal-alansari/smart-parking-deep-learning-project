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
