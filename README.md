# Smart Parking Monitoring and Visitor Permits

Local academic prototype for two RTA-allocated parking bays in Dubai. A camera watches the bays, a from-scratch CNN detects occupancy, a fine-tuned YOLO11n reads UAE plates, and typed English commands manage a visitor permit table. Each arrival gets a reviewable decision: `AUTHORIZED`, `POTENTIALLY_UNAUTHORIZED` or `NEEDS_REVIEW`.

Project plan and rubric: `docs/planning/`. Data sources and splits: `docs/data_card.md`. Decision log: `Memory.md`.

## Setup

Requires `uv` and `just` on macOS (Python 3.14 is installed by `uv`).

```bash
just install
just test
```

Download the datasets as described in `docs/data_card.md`.

## Reproduce the occupancy results

```bash
just prepare-data          # manifest, inspection sheets, splits, sampling
just occupancy-baselines   # texture threshold and HOG + logistic regression
just occupancy-experiments # training-choice experiments (validation only)
just train-occupancy       # final OccupancyCNN, one run per seed
just evaluate-occupancy    # one-time comparison on the test splits
```

## Layout

| Path | Contents |
|---|---|
| `src/smart_parking/common/` | Config, logging, seeding |
| `src/smart_parking/occupancy/` | Occupancy data preparation, baselines, CNN, training, evaluation |
| `tests/` | Tests per component (`just test`) |
| `configs/default.yaml` | All settings and seeds |
| `experiments/occupancy/` | Training logs (TensorBoard and per-epoch history) |
| `checkpoints/occupancy/` | Final models and baselines |
| `outputs/occupancy/` | Data report, inspection sheets, result tables |
| `docs/` | Data card, planning documents, final report |
| `data/` | Datasets (not in Git) |
