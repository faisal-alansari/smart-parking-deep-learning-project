# Smart Parking Monitoring and Visitor Permits

## Final Rubric Implementation Reference

**Status:** Agreed project concept. This document defines the implementation and evidence needed for the **Final Project Rubric only**. Model C selection, plate-recognition method, supported plate layouts, and operating thresholds remain experimental. This reference is not the graded final report.

## 1. Problem, User, and Scope

I have **two adjacent, RTA-allocated parking bays** in Dubai. Unauthorized vehicles sometimes occupy them. I need a convenient way to detect arrivals, read plates, distinguish permitted residents and visitors, and review evidence. A vehicle outside the permanent list is not automatically unauthorized because visitors receive time-limited permission.

Build a **local academic prototype**, not a deployed enforcement service. No automatic fines, police/RTA submissions, legal violation claims, cloud inference, production database, or continuous multiweek recording. Start with **3–4 real permanently authorized vehicles** and add visitors through one editable **in-memory permit table**. Do not invent authorized identities to enlarge the project.

Five connected capabilities:

1. Detect empty/occupied status in each fixed bay.
2. Confirm arrivals and capture a useful evidence frame.
3. Read UAE plate identity when legible.
4. Add, edit, extend, revoke, and list permissions through typed **English commands**.
5. Match plate, bay, and event time against permissions; return evidence and a reviewable decision.

**Final decisions:** `AUTHORIZED`, `POTENTIALLY_UNAUTHORIZED`, or `NEEDS_REVIEW`. No case leads to an automatic penalty. A human can confirm or correct plate and decision fields.

## 2. Three Interacting Modalities


| Modality                                     | Role                                                                               |
| -------------------------------------------- | ---------------------------------------------------------------------------------- |
| **Visual:** video and still frames           | Detect occupancy and read the arriving car's plate.                                |
| **Text:** independent typed English commands | Change permanent or temporary visitor access.                                      |
| **Tabular:** one permit table                | Determines authorization from full plate identity, allowed bay, and validity time. |


Prove integration by showing the **same arrival** change from `POTENTIALLY_UNAUTHORIZED` to `AUTHORIZED` after a valid text command updates the table, and revert after expiry/revocation. Perform modality-removal ablations. Video frame sequences belong to the visual modality, not a separate vibration/sensor modality. **Confirm the visual + text + tabular interpretation with the professor.**

## 3. Models and Architecture


| Component              | Model or method                                                                       | Training role                                                               |
| ---------------------- | ------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| **A: occupancy**       | Small shared `OccupancyCNN`, two fixed bay ROIs                                       | **Train from random initialization**, target ~0.1–1M parameters, limit 50M. |
| **B: plate reading**   | **YOLO11n** (~2.6M reported parameters) plus deterministic character/layout assembler | **Fine-tune pretrained weights** on cleaned UAE plate annotations.          |
| **C: command parsing** | Select `SmolLM2-135M-Instruct`, `FLAN-T5-Small`, or `GLiNER Small v2.1` after testing | Use a **pretrained model without fine-tuning**.                             |
| Rules                  | ROI processing, event state machine, plate validation, permit/time checks             | Deterministic and separate from learned models.                             |


Model A predicts occupancy per bay. Smoothing, hysteresis, a validation-selected dwell time, and `UNCERTAIN` state prevent transient triggers. Confirmed arrivals initiate frame selection and Model B inference. Model B must extract the complete normalized `(emirate, code, number)`, not merely locate a plate. Prefer character detection plus geometric assembly; compare small OCR alternatives only if the labels or results justify them. Unsupported/blurred/obscured plates trigger review.

Model C proposes structured `ADD`, `EDIT`, `EXTEND`, `REVOKE`, or `LIST` actions. **Pydantic validation and my confirmation** precede any table mutation. Missing or ambiguous information prompts clarification; the model never directly executes commands.

Constraints: **each model ≤200M parameters**, scratch model **≤50M**, all pretrained/fine-tuned models **≤1B combined**, and **≤10,000 fine-tuning items across the project**. Measure and report actual parameter counts. Inference runs on local weights with **no runtime model APIs**.

## 4. Data and Feasibility


| Data source                                                                        | Intended use                                            | Key limitation                                                          |
| ---------------------------------------------------------------------------------- | ------------------------------------------------------- | ----------------------------------------------------------------------- |
| [CNRPark-EXT](https://cnrpark.it/) (~145k labeled crops)                           | Main occupancy training and unseen-camera tests         | Different viewpoints; night labels uncertain.                           |
| [PKLot](https://web.inf.ufpr.br/vri/databases/parking-lot-database/) (~696k crops) | Additional occupancy training and cross-site evaluation | No night images; repeated frames.                                       |
| [NDISPark](https://zenodo.org/records/6560823) (259 images)                        | Small day/night robustness test                         | Vehicle masks, not ready-made per-bay labels.                           |
| [AddingUAE](https://universe.roboflow.com/addinguae/uae-zcfqj)                     | Candidate plate/character annotation source             | Fable could not verify class map, count, or accessibility. Audit first. |
| [UAEPlates](https://universe.roboflow.com/uaeplates/uae-car-plates) (~730 images)  | Emirate/code/number region localization                 | Bounding boxes lack actual OCR text transcriptions.                     |
| My commands and permit table                                                    | Frozen NLP evaluation and integrated demo               | Small sample; design held-out commands and edge cases.                  |


Use approximately **20k–60k diverse, class-balanced public occupancy crops**, rather than all near-duplicates. Scratch-model data is outside the fine-tuning cap. For Model B, an **illustrative 4,500-item budget** leaves 5,500 headroom. Count distinct fine-tuning inputs conservatively across training, validation, and testing; exported augmented copies and separately trained crops count as inputs. Maintain an exact ledger.

**Own-camera alternative:** 8–10 sessions of 15–20 minutes, with fixed framing, empty/occupied states, partial entries, shadows, and daytime/nighttime variation. Collect short arrival/departure clips. Use early sessions for development and the last 2–3 as untouched local tests, including night. Expected ~400–800 labeled local crops and ~16–20 transitions are planning estimates; event confidence intervals will be wide. A smaller four-session day/night test is a weaker fallback.

**Go/no-go first:** At the actual camera position, measure plate character height and readability in both bays, day/night and nose-in/reverse-in, using consenting vehicles. If insufficient, test a narrower camera/crop or assisted human plate entry. Public images cannot establish deployment-camera accuracy.

Split occupancy data by camera/day/session and plates by **full plate identity**. Deduplicate across splits, audit annotations and class/emirate balance, and select thresholds only on validation data. Three-emirate support (Dubai, Abu Dhabi, Sharjah) is a reasonable **starting hypothesis**, not a verified capability. Abstain on unsupported layouts.

## 5. Core Workflow and Structured Output

1. I type: `Allow Dubai B 12345 in bay 2 on November 12 from 6 PM to 10 PM.`
2. Model C proposes typed fields. Validate plate, bay, Asia/Dubai timestamps, duplicates, and command intent. Show confirmation, then update **one** permit table.
3. Camera frames are cropped into two ROIs. Model A and temporal logic confirm arrival in bay 2.
4. Model B reads the full UAE plate, attaches confidence, and validates its layout.
5. Compare recognized plate, bay, and event timestamp with active permanent/temporary permits.
6. Return decision, reason, recognized fields, calibrated confidence, event time, bay, evidence image/crop, permit match, and `abstain_reason` where relevant.
7. Allow structured feedback: accepted decision, corrected plate/status, and optional note. Retain feedback as a local evaluation record, not a production database.

Use **Pydantic v2** schemas for `PlateIdentity`, `Permit`, `ParsedCommand`, `OccupancyEvent`, `EvidenceRecord`, and `HumanFeedback`. Invalid input returns a validated error or clarification without crashing or inventing plate data.

**Tiered safety:** Validate deterministic fields first, run the lightweight learned components only when needed, and escalate unreliable or unfamiliar results to human review. False accusation of an authorized visitor carries a higher assumed cost than a review request. Use consenting vehicles for staged data, limit camera framing to the two bays, blur unrelated identities, and store event evidence only as needed. Document retention and remaining privacy risks.

## 6. Final Evaluation and Evidence


| Final requirement           | Project-specific evidence                                                                                                                                                                                                               |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Metrics**                 | Occupancy F1/recall; plate full-identity exact match and character error; command intent/field accuracy; false alerts, missed arrivals, event latency, review rate, and task completion. Name a primary metric.                         |
| **Baselines**               | Classical image difference/HOG classifier vs scratch CNN; unadapted detector/OCR vs fine-tuned plate system; rule parser vs frozen NLP. Compare fairly on identical splits.                                                             |
| **Ablations**               | Remove/perturb each modality; public-only vs local-adapted occupancy; with/without temporal logic, augmentation, and table time/bay restrictions. State hypotheses and conclusions.                                                     |
| **Training choices**        | Logged optimizer/learning-rate, class balance, augmentation, regularization, and threshold experiments. Use validation data and report failed attempts.                                                                                 |
| **Uncertainty**             | Confidence intervals, multiple seeds or variance; separate day/night, camera, emirate, and difficult-input performance.                                                                                                                 |
| **Calibration/cost**        | Reliability diagrams and ECE with per-bin counts; compare before/after validation-fitted calibration if needed; asymmetric costs for false accusations, missed parking, and human review. Justify thresholds and test cost sensitivity. |
| **OOD/abstention**          | Unknown layouts, bad crops, unusual lighting, ambiguous text, and missing inputs yield `NEEDS_REVIEW` or clarification; show risk–coverage trade-off.                                                                                   |
| **Robustness**              | Increasing blur, glare, shadows, noise, occlusion, resolution loss, malformed commands, and missing fields; report degradation curves.                                                                                                  |
| **Monitoring**              | Simulated day-to-night/input shift; monitor confidence, review/error rates, image quality, and latency, with an alert and response.                                                                                                     |
| **Explainability/failures** | Controlled minimal pairs (permit expiry, wrong bay, lighting change), hypotheses, error categories with counts, root causes, and changes supported by before/after evidence.                                                            |
| **Efficiency**              | Per-stage and end-to-end latency, parameter/memory budget, and at least one measured quality-versus-cost optimization.                                                                                                                  |


Every deterministic rule in the final system should be traceable to an **observed failure**. Keep real measured results separate from goals and examples. No invented accuracy claims.

## 7. Final Deliverables and Reproducibility

- **Python 3.14**, `uv` and `uv.lock`, `just`, PyTorch, Pydantic v2, Loguru, fixed seeds, clean configuration, and organized `src/` modules. **No** `pip` **or** `uv pip`**.**
- A **CLI and simple UI** (Gradio/Streamlit acceptable) demonstrating an ordinary event, permit update, and abstention/review.
- `just install`, `just train`, `just evaluate`, `just demo`, `just test`, `just clean`, plus reproducible baseline, ablation, robustness, and batch-unseen-input commands.
- `just evaluate` reproduces **every reported figure and number**. Include data preparation, source/license records, checkpoints or download instructions, configuration, tests, and a clean Mac checkout test. Container operation remains local.
- Preserve **incremental Git history**, actual training/hyperparameter logs, experiment-tracker exports, evaluation artifacts, feedback, and failure records.
- Produce the **separate graded Final Report** in Markdown, **5–8 pages and ≤3,000 words** (rubric exclusions for tables/figures/captions apply). Follow the six final scoring areas: engineering; multimodal system; evaluations/ablations; trust; explainability/failures; reproducibility.
- Run valid structured inference on a folder of instructor-provided **unseen realistic inputs** without code modifications.



## 8. Implementation Priority and Open Decisions

1. **Verify feasibility:** plate-pixel pilot, dataset labels/licenses, local Mac/Python 3.14 compatibility, and professor approval of modalities.
2. **Build contracts/data:** one permit table, safe command validation, split/dedup pipelines, item ledger, realistic held-out samples.
3. **Train Model A and fine-tune Model B:** log runs, compare baselines, handle uncertainty and hard examples.
4. **Benchmark and choose frozen Model C:** compare structured command accuracy, invalid-action rate, latency, and memory.
5. **Integrate and verify full journey:** arrival → full plate → bay/time permit → decision/evidence/feedback, with permit-update before/after proof.
6. **Complete final evidence:** ablations, calibration, cost model, OOD, robustness, monitoring, probes, failure taxonomy, efficiency, reproducibility, report.

**Open:** final NLP candidate, OCR fallback, supported UAE plate layouts, thresholds, actual model performance, and professor acceptance of tabular modality. Do not expand scope without a new decision.

**Authoritative grading reference:** 03_final_project_rubrics.md