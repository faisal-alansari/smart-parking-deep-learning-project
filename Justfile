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

# Rebuild the training-choice tables from the logged runs (no training)
occupancy-experiments-report:
    uv run python -m smart_parking.occupancy.experiments --report

plate-experiments-report:
    uv run python -m smart_parking.plates.experiments --report

# Rebuild the Model A adaptation choice table from the saved runs (no training)
adapt-occupancy-choice-report:
    uv run python -m smart_parking.occupancy.adapt --report-choice

# Model A confidence and the bay check, chosen again on block 4 only (rules in Memory.md)
validation-choices:
    uv run python -m smart_parking.trust.validation_choices

# Compute and latency budget on the sample clip and dev commands (outputs/loop/latency.md)
latency:
    HF_HUB_OFFLINE=1 uv run python -m smart_parking.latency

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

# Build the submission zip from Git: code, full history, weights, logs and outputs (no raw
# data, downloaded models or caches; uncommitted changes are left out)
package:
    rm -rf dist && mkdir -p dist
    git clone --quiet . dist/smart-parking
    git -C dist/smart-parking remote set-url origin "$(git remote get-url origin)"
    cd dist && zip -qr smart-parking-submission.zip smart-parking
    @du -h dist/smart-parking-submission.zip

# Full loop story on the owner's photos: all three models and the permit table (local only)
full-loop-scenario:
    HF_HUB_OFFLINE=1 uv run python -m smart_parking.loop --scenario

# Full loop on every local bay against the truth, with blame per stage (counts-only summary)
full-loop:
    HF_HUB_OFFLINE=1 uv run python -m smart_parking.loop --evaluate

# Remove one part of the full loop at a time (no Model A, B, C, time check, owner check)
full-loop-ablation:
    HF_HUB_OFFLINE=1 uv run python -m smart_parking.ablation

# Run the full system on a folder of new photos, videos and commands.txt (see pipeline.py)
run-folder dir *flags:
    HF_HUB_OFFLINE=1 uv run python -m smart_parking.pipeline --folder {{quote(dir)}} {{flags}}

# Full loop on the owner's night video against its truth (local only; counts-only summary)
video-night-1:
    HF_HUB_OFFLINE=1 uv run python -m smart_parking.pipeline --video-eval configs/local_video_night_1.yaml

# The one final test: the whole system on the sealed night video 3 (runs the models once;
# `just final-test --report` rebuilds the report from the saved results)
final-test *flags:
    HF_HUB_OFFLINE=1 uv run python -m smart_parking.final_test {{flags}}

# One decision per car's stay on the night video (uses the saved per-frame results)
video-night-1-stays:
    uv run python -m smart_parking.stays

# Adapt Model A to the owner's camera: train options on video 2 blocks 1-3, choose on block 4
adapt-occupancy:
    uv run python -m smart_parking.occupancy.adapt

# The one final test of the adapted Model A (first night video, public tests, local photos)
adapt-occupancy-final:
    uv run python -m smart_parking.occupancy.adapt --final

# Regenerate the adapted Model A's final test tables (nothing is chosen again)
adapt-occupancy-report:
    uv run python -m smart_parking.occupancy.adapt --reproduce

# Calibration: reliability diagrams, ECE and Platt scaling for Models A and B (outputs/trust/)
calibration:
    uv run python -m smart_parking.trust.calibration

# Error-cost model: thresholds chosen on validation, test cost, sensitivity, risk-coverage
costs:
    uv run python -m smart_parking.trust.costs

# Unfamiliar-input (OOD) detector for the camera: fit, cut-off on block 4, evaluation
ood:
    uv run python -m smart_parking.trust.ood

# Image robustness at increasing severity (Model A + camera check, Model B)
robustness-images:
    uv run python -m smart_parking.trust.robustness

# Monitoring demo: the other night replayed with a dimming light and a knocked camera
monitor-demo:
    uv run python -m smart_parking.trust.monitor

# Explainability probes for Models A, B, C and the joined decision
probes:
    HF_HUB_OFFLINE=1 uv run python -m smart_parking.trust.probes

# Failure analysis: every error sorted into causes, fixes and what remains
failures:
    uv run python -m smart_parking.trust.failures

# Efficiency study: frame rate and plate caching, quality against model time
efficiency:
    uv run python -m smart_parking.trust.efficiency

# Demo web app (Streamlit): owner commands with accept/reject/fix, camera runs on samples/
demo:
    HF_HUB_OFFLINE=1 uv run streamlit run src/smart_parking/app.py --server.headless true --server.address 127.0.0.1 --browser.gatherUsageStats false

# Demo on the command line: both sample folders through the full system (outputs/runs/)
demo-cli:
    HF_HUB_OFFLINE=1 uv run python -m smart_parking.pipeline --folder samples/owner_camera --yes
    HF_HUB_OFFLINE=1 uv run python -m smart_parking.pipeline --folder samples/new_camera --yes

# Parameter budget counted from the loaded models, and fine-tuning items against the cap
budget:
    HF_HUB_OFFLINE=1 uv run python -m smart_parking.budget

# Check the report word limit without evaluating or choosing any model
report-check:
    uv run python -m smart_parking.report_check

# Train every learned part in order (public occupancy CNN, plate reader, Model A adaptation)
train: train-occupancy train-plates adapt-occupancy

# Model C on its frozen test exactly as tested (reproduces the reported test numbers)
# Replay the one frozen Model C test comparison exactly as tested (fixed parsers; nothing is chosen)
command-test:
    for p in oracle rules smollm2 flan-t5 gliner-minilm checked tiered; do HF_HUB_OFFLINE=1 uv run python -m smart_parking.commands.score $p test --final --as-tested; done

# Regenerate every table and figure in the report from saved models and logged runs. Read-only:
# it never trains and never changes a fitted setting (a mismatch stops it; see `just refit`).
evaluate:
    just occupancy-experiments-report
    just plate-experiments-report
    just adapt-occupancy-choice-report
    just evaluate-occupancy
    just evaluate-plates
    just adapt-occupancy-report
    just validation-choices
    just calibration
    just costs
    just ood
    just command-test
    just command-robustness
    just command-demo
    just full-loop
    just full-loop-ablation
    just full-loop-scenario
    just video-night-1
    just video-night-1-stays
    just final-test --report
    just robustness-images
    just monitor-demo
    just latency
    just efficiency
    just probes
    just failures
    just budget
    just report-check
    just demo-cli

# Re-fit the validation-only settings (calibration, cost thresholds, camera check) and store them
refit:
    uv run python -m smart_parking.trust.calibration --refit
    uv run python -m smart_parking.trust.costs --refit
    uv run python -m smart_parking.trust.ood --refit

