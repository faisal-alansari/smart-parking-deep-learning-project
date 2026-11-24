# Smart Parking: two private bays, one camera

A homeowner in Dubai has two allocated parking bays that strangers often take. One fixed camera
watches the bays at night. The product says, for each car's stay, whether it is **AUTHORIZED**,
**POTENTIALLY_UNAUTHORIZED** (alert the owner) or **NEEDS_REVIEW** (a person must look, with the
reason and an evidence frame). The owner manages visitors by typing or dictating plain commands
("allow car 12345 until 6 pm"), which change the permit table only after the owner confirms.

Final report: [`docs/final_report.md`](docs/final_report.md). Data: [`docs/data_card.md`](docs/data_card.md).
Decision log: [`Memory.md`](Memory.md).

## How it works

```
camera frame ──> camera check (blocked / unfamiliar view / blurred?) ──> NEEDS_REVIEW + reason
     │ ok
     ├─> Model A  OccupancyCNN (from scratch, 0.29M)  ──> is each bay occupied?
     │        │ occupied
     │        └─> Model B  YOLO11n (fine-tuned, 2.6M) + reading rules ──> plate (emirate, code, number)
     │
owner command ─> Model C (pretrained, not fine-tuned: GLiNER + MiniLM, checked by SmolLM2)
     │            ──> proposed change ──> owner accepts / fixes / rejects ──> permit table
     │
     └─> permit table + time ──> one decision per stay (10 s to confirm, majority plate)
                                  AUTHORIZED / POTENTIALLY_UNAUTHORIZED / NEEDS_REVIEW
```

Three modalities: **images** (Models A and B), **text** (Model C) and **tabular** (the permit
table and its time limits). Every rule outside the models is tied to a failure seen during
development (see the report and `outputs/trust/failures.md`).

## Setup (macOS, from a clean checkout)

Requires [`uv`](https://docs.astral.sh/uv/) and [`just`](https://github.com/casey/just).
Python 3.14 is installed by `uv`.

```bash
just install                  # uv sync --frozen
just download-weights         # YOLO11n pretrained weights (only needed to retrain Model B)
just download-command-models  # Model C weights from Hugging Face (pinned revisions)
just test
```

Trained checkpoints for Models A and B are in `checkpoints/`. Model C runs from local weights
only (no runtime model APIs).

## Demo

```bash
just demo       # web app: owner commands (accept / reject / fix) and camera runs on samples/
just demo-cli   # the same samples on the command line -> outputs/runs/
```

`samples/owner_camera/` holds a clip of the owner's camera, photos (including a covered lens and
another car park, which the product refuses to judge) and `commands.txt`. `samples/new_camera/`
shows how a new camera is set up with `bays.yaml`.

## Run on new inputs

```bash
just run-folder path/to/folder --yes      # --every 2: seconds between video frames
```

The folder may hold photos (`.jpg .jpeg .png .heic`), videos (`.mov .mp4 .m4v`), a
`commands.txt` (`2026-11-22 09:05 | allow car 12345 until 6 pm`, one per line) and an optional
`bays.yaml` (`boxes: {left: [x0, y0, x1, y1], right: [...]}` as fractions of the frame). Without
`bays.yaml` the owner's camera is assumed. Results go to `outputs/runs/<folder>/`:
`result.json` (validated Pydantic records: status, confidence, reason, guidance, evidence frame),
`decisions.csv`, `summary.md` and `evidence/`. Bad or unsupported inputs are reported with
guidance, never a crash. Without `--yes`, each proposed permit change is asked in the terminal.

## Reproduce

```bash
just train      # public occupancy CNN, plate reader, Model A adaptation (seeds in configs/)
just evaluate   # regenerates every table and figure used in the report (no training)
```

Main recipes, each writing to `outputs/`:

| recipe | what it produces |
|---|---|
| `evaluate-occupancy`, `evaluate-plates` | Models A (public data) and B against baselines on their test splits |
| `adapt-occupancy` / `adapt-occupancy-report` | Model A adaptation: options chosen on validation; the one final test |
| `command-test`, `command-robustness` | Model C on its frozen test, as tested; robustness levels |
| `full-loop`, `full-loop-ablation`, `video-night-1`, `video-night-1-stays` | the joined system; one part removed at a time; the test night, frame by frame and per stay |
| `calibration`, `costs`, `ood`, `robustness-images`, `monitor-demo` | trust: reliability and ECE, cost-based thresholds, unfamiliar inputs, stress tests, monitoring |
| `efficiency`, `probes`, `failures`, `budget` | efficiency study, explainability probes, failure taxonomy, parameter budget |

**Data.** Public: CNRPark+EXT and AddingUAE (download links in the data card). The owner's
photos and videos (about 6.5 GB) go in `data/raw/` (`local_pilot/`, `local_night_1/`,
`video_night_1/`, `video_night_2/`); their truth labels are in `configs/local_*.yaml`. All
seeds are set in `configs/default.yaml` (42, 43, 44).

## Layout

| path | contents |
|---|---|
| `src/smart_parking/occupancy/` | Model A: data, baselines, CNN, training, adaptation |
| `src/smart_parking/plates/` | Model B: data, YOLO11n fine-tuning, reading rules |
| `src/smart_parking/commands/` | Model C: command sets, candidates, rules, owner flow |
| `src/smart_parking/` (`pipeline`, `loop`, `stays`, `decision`, `output`, `app`) | the joined product, per-stay logic, operating rules, output schema, demo app |
| `src/smart_parking/trust/` | calibration, costs, OOD, robustness, monitoring, probes, failures |
| `configs/` | all settings, seeds and truth labels |
| `checkpoints/`, `experiments/` | final models; training logs (TensorBoard, per-epoch history) |
| `outputs/` | every result table and figure |
| `samples/` | demo inputs |
| `tests/` | `just test` |

## Citations

- CNRPark+EXT: G. Amato et al., "Deep learning for decentralized parking lot occupancy
  detection", *Expert Systems with Applications*, 2017.
- AddingUAE plate dataset (Roboflow Universe, CC BY 4.0): https://universe.roboflow.com/addinguae/uae-zcfqj
- YOLO11: G. Jocher, J. Qiu, Ultralytics YOLO11, 2024 (AGPL-3.0).
- GLiNER: U. Zaratiana et al., "GLiNER: Generalist model for named entity recognition using
  bidirectional transformer", NAACL 2024; DeBERTa-v3: P. He et al., 2021.
- all-MiniLM-L6-v2: W. Wang et al., "MiniLM", NeurIPS 2020; N. Reimers, I. Gurevych,
  "Sentence-BERT", EMNLP 2019.
- SmolLM2: L. Ben Allal et al., "SmolLM2: When smol goes big", 2025.
- FLAN-T5 (a candidate, not used): H. W. Chung et al., "Scaling instruction-finetuned language
  models", 2022.
