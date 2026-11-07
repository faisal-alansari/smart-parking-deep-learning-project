# Smart Parking task runner. Run `just` to list recipes.

default:
    @just --list

# Install all dependencies from uv.lock
install:
    uv sync --frozen

# Build the occupancy manifest, inspection sheets, splits and sampled dataset
prepare-data:
    uv run python -m smart_parking.data.prepare

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
