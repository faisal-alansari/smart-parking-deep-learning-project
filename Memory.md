# Project Memory

Concise decisions and lessons for the Smart Parking project. This is **not** a technical experiment log.

## Confirmed decisions

### 2026-11-06 | Three modalities

- **Decision:** Use Visual (camera), Text (visitor commands), and Tabular (permit table).
- **Outcome:** Approved. No separate vibration/event sensor is planned.
- **Next:** Prove their interaction in the integrated demo and ablations.

### 2026-11-06 | Project setup

- **Decision / reason:** Python 3.14 with `uv` and `just`. One YAML config file checked by Pydantic, Loguru logging to screen and a rotating file, and one seed (42) for Python, NumPy, and PyTorch.
- **Outcome:** Worked. Install, tests, and lint pass on the Mac. PyTorch runs on Python 3.14 and can use the Mac GPU (MPS).
- **Next:** Keep. Add new settings to the same config file as each model is built.

## Decision log

For each **meaningful** new decision, add one short entry:

### YYYY-MM-DD | Decision title

- **Decision / reason:** What we chose or tested, and why.
- **Outcome:** Worked, failed, or inconclusive. Explain the practical lesson.
- **Next:** Keep, change, reject, or retest.

