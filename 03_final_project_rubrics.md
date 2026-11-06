# Final Project Grading Rubrics

# Overview & General Expectations

The final submission is the complete case for yourproject. The standard throughout the course is simple: you must show not only that the product works, but **why it works, when it fails, how you know, and why its design is appropriate for the setting in which it will be used**.

Grading is based on reading the submitted code, the written report, and the evidence of how the project was developed (logs, experiment-tracker exports, git history), together with running the system. The instructor may also run your system on **realistic common and edge-case inputs that you have not seen**. These will not be synthetically generated adversarial examples. They will look like the inputs your real users would send.

At this stage, I expect:

- a **complete, multimodal, end-to-end product** (three or more interacting modalities, three to five connected capabilities) that runs from a CLI and a simple demo interface
- **experimentally justified design decisions**: baselines, meaningful ablations, and logged evidence for choices about optimization, augmentation, regularization, class weighting, freezing/adaptation strategy and operating thresholds
- **calibrated, honest confidence**: reliability diagrams and Expected Calibration Error (ECE), connected to a domain-specific asymmetric cost model, with out-of-distribution detection and an explicit abstention/escalation path
- **robustness, monitoring, efficiency and generalization evidence** that answers real questions about your domain
- **explainability treated as an investigation** (controlled probes) together with a systematic failure analysis
- **preserved development evidence** and a full reproducibility package

Everything required at the intermediate stage must also be present in the final submission. All members of a team receive the same score.

## General Constraints (applies to all sections)

- Code must run in **Python 3.14 via uv**. No pip usage. The project must run on a Mac from a clean checkout using only `uv` and `just`.
- All random seeds must be set and documented. Results must be reproducible.
- The product must run locally on downloaded model weights. No runtime LLM APIs. Network access is limited to model/data downloads (e.g., Hugging Face Hub).
- Model constraints from the proposal guidelines still apply: no model above **200M** parameters; pretrained and fine-tuned models together within **1B**; the from-scratch model within **50M**; no more than **10,000** fine-tuning items across the entire project.
- Your report must be a concise Markdown document of **5-8 pages and at most 3,000 words**. Tables, figures and their captions do not count toward the page or word limit. Do **NOT** write long essays. Short, precise paragraphs, tables and figures are preferred. Other formats and longer documnts will be penalized.
- LLM assistance for code and debugging is allowed, but analysis and design decisions must be your own.
- Every number in the report must be reproducible by running the provided `just` recipes.

# Grading Summary

| Section | Points |
|---|---|
| 1. Engineering Tooling & Project Setup | 10 |
| 2. System, Multimodal Integration & Technical Soundness | 20 |
| 3. Evaluation, Ablations & Experimental Justification | 20 |
| 4. Trust & Safety: Calibration, Abstention, Robustness & Monitoring | 20 |
| 5. Explainability, Failure Analysis & Practical Insight | 15 |
| 6. Reproducibility, Development Evidence & Professionalism | 15 |
| **Total** | **100** |

# Section 0: Recommended Project Structure and Report Outline

This section just gives some ideas. You can customize it to your requirements.

**Repository**

- `pyproject.toml`, `uv.lock`, `Justfile`, `README.md`
- `src/` (subpackages such as `data/`, `models/`, `evaluation/`, `pipeline/`, `monitoring/`, `utils/`)
- `configs/`
- `data/` (or download scripts and a data card if the data is large)
- `experiments/` (training and hyper-parameter logs, W&B/TensorBoard exports)
- `outputs/` (metrics, reliability diagrams, ablation tables, robustness curves, probe results)
- `checkpoints/` (or a script to obtain them), `logs/`, `tests/`
- `samples/` (example inputs for the demo)
- `docs/` (including `final_report.md`)

**Report outline (suggested)**

1. Venture and user recap (one paragraph)
2. System design and parameter budget
3. Data and splits
4. Results: baselines, ablations, training-choice experiments
5. Trust: calibration, cost-based thresholds, OOD/abstention, robustness, monitoring
6. Efficiency and generalization
7. Explainability probes and failure analysis
8. Insights, limitations and risks

# Section 1: Engineering Tooling & Project Setup (10 points)

Please refer to the intermediate report rubric for full details on the tooling requirements.

## 1a. uv Project Setup

- Valid `pyproject.toml` with metadata and `requires-python` set for Python 3.14
- All runtime dependencies declared with version constraints; dev dependencies separated
- `uv.lock` committed; project installs cleanly with `uv sync` on a Mac. No pip or `uv pip` usage anywhere.

## 1b. Justfile Automation

All recipes must work end-to-end without manual steps.

- Recipes carried over from the intermediate stage: `just install`, `just train` (or documented `train-*` variants), `just evaluate`, `just demo`, `just test`, `just clean`
- Additional final recipes, for example:
  - one to run the baseline(s) and the final system side by side
  - one to run the ablations
  - one to run the robustness suite and monitoring demonstration
  - one that accepts a directory of new inputs and returns structured outputs (used for instructor evaluation)
- `just evaluate` regenerates every table and figure used in the report

## 1c. Pydantic Schemas & Loguru Logging

- Pydantic (v2 or later) used for structured data contracts throughout, including the final output schema with confidence, abstention/escalation decision and reason, and user-feedback records
- Loguru replaces all `print()` statements in `src/`, with logs written to stderr and a rotating file, and contextual logging (e.g., `logger.bind()`)
- Key events are logged: data loading, training, metrics, abstention/escalation decisions, monitoring alerts

# Section 2: System, Multimodal Integration & Technical Soundness (20 points)

This section is evaluated by reading the code, running the product, and reading the report's description of the system.

## 2a. Product Concept & Workflow

- A specific user and concrete problem, with the product's place in the user's existing workflow made clear
- A coherent user journey from input or onboarding to a useful result, including what happens on failure or escalation
- A plausible operational or commercial reason for the product to exist
- Scope is stated: what is delivered and what is deliberately out of scope

## 2b. Model Composition & Parameter Budget

- At least one model **trained from scratch** (randomly initialized, ≤50M) and at least one pretrained model **fine-tuned** for your task, plus any unmodified pretrained models with a clear role
- No model exceeds 200M parameters; pretrained and fine-tuned models total ≤1B
- **Parameter budget table** in the report listing every model, its role, and its parameter count, verified programmatically
- The budget is distributed meaningfully across modalities and pipeline stages rather than concentrated in one model
- Each architecture choice is justified for its modality and role
- The boundary between learned components and deterministic logic is justified

## 2c. Multimodal Integration

- At least **three distinct modalities** are genuinely used, and they interact meaningfully within one pipeline (not three disconnected demonstrations)
- Three to five connected capabilities are implemented, and the flow of information among models and rule-based components is clearly described (a system diagram is recommended)
- Each modality demonstrably contributes to the result. This is supported by evidence in Section 3c (e.g., a modality-removal ablation).

## 2d. End-to-End Pipeline & Structured Outputs

- The pipeline runs from raw input to a validated, structured output without crashing
- Learned components are loaded from local checkpoints or weights; no runtime LLM API calls
- Deterministic rules are clearly separated from learned components, and **each final rule is traceable to a failure actually observed during development** (documented in the report or logs)
- Inference is near real-time, or any slower design is justified and approved by the instructor
- Malformed, empty, incomplete or unsupported inputs produce a sensible structured response with guidance, not a crash

## 2e. Demo Interface & Feedback Mechanism

- A CLI and a simple demo interface (e.g., Streamlit or Gradio) are both provided and launched via `just demo`, using sample inputs included in the repository
- The demo walks through the complete user journey, including an abstention/escalation case
- A user-feedback mechanism (corrections, overrides or accept/reject) is implemented and stores structured feedback records. Retraining from the feedback may be simulated, but the report must explain how the feedback would be used.

# Section 3: Evaluation, Ablations & Experimental Justification (20 points)

This section is evaluated by reading the code, the experiment logs, and the report. The metric values reported must match what is produced by `just evaluate`. Include a few concise paragraphs on: (a) what you are measuring, (b) how you are measuring it, and (c) what the results say.

## 3a. Data Quality & Splits

- Data sources and provenance documented (data card), including any data you curated, labelled or synthesized yourselves
- Splits are fixed by seed and respect the structure of the problem (e.g., by customer, document, site or time); no leakage (duplicates checked across splits, preprocessing fit on train only)
- Data issues are addressed and reported: cleaning, annotation quality, deduplication, class imbalance, coverage gaps
- Final **fine-tuning item count** is reported against the 10,000-item project cap
- The data supports the claims made in the report

## 3b. Metrics, Baselines & Reporting

- At least 2-3 ML metrics and at least 2 business/practical metrics, with a designated primary metric that matches the success criteria in your proposal
- Evaluation runs strictly on the held-out test split; all model and threshold selection uses the validation split
- At least one **fair, meaningful baseline** (e.g., a heuristic, a classical ML model, or the pretrained model without fine-tuning), compared on the same test split and metrics in a single results table
- Results include confidence intervals, standard deviations, or multiple-seed averages
- Final results are shown against the targets set in the proposal, with an honest status (met, partially met, not met) and an interpretation of what this means for the product

## 3c. Ablations

- Meaningful ablations chosen to answer real questions about your design, for example: removing or weakening a modality, scratch model vs. pretrained alternative, removing a pipeline component, deterministic rules on/off, fine-tuned vs. frozen pretrained model
- Each ablation states its hypothesis, shows results in a table or figure, and draws a conclusion
- The ablations show that each major component and modality earns its place, and honestly report components that do not

## 3d. Justified Training Choices

- Experimentally justified choices about the relevant subset of: optimizer and learning rate, augmentation, regularization, class weighting or loss design, freezing/adaptation strategy (full, frozen, parameter-efficient), and operating thresholds
- Choices are supported by logged runs (learning curves, hyper-parameter comparison tables), not asserted
- All tuning uses the validation split, and the search effort is described honestly (what was tried, including what did not help)

## 3e. Efficiency & Generalization

- A **compute and latency budget**: parameters, memory, and per-stage and end-to-end latency on the target machine
- An **efficiency study** that looks for a genuine quality-cost improvement (e.g., preserving quality while reducing latency, memory or parameter count via a smaller backbone, distillation, quantization, pruning, or caching), reported as a quality-vs-cost comparison
- Generalization is examined on realistic hard examples or previously unseen inputs, and the gap between in-distribution and harder inputs is reported
- Behavior on the instructor's unseen realistic inputs is sensible (see Section 6c)

# Section 4: Trust & Safety (20 points)

The product must recognize the limits of its competence. This section is evaluated on both the code and the report.

## 4a. Calibration

- Reliability diagrams and Expected Calibration Error (ECE) reported on the held-out test split for the models that produce the confidence used in decisions
- Binning scheme and per-bin sample counts are documented, and accuracy and confidence are shown together
- Calibration is improved where needed (e.g., temperature scaling fit on validation data), with before/after results and a short interpretation of where the model is over- or under-confident
- For non-classification tasks, an appropriate confidence measure is used and justified (e.g., interval coverage, score distributions)

## 4b. Asymmetric Cost Model & Operating Thresholds

- A **domain-specific asymmetric cost model** that reflects the real consequences of different errors (including the cost of escalating to a human), with the assumptions justified
- Thresholds and escalation decisions are chosen on the validation split by minimizing expected cost, and are stored in config
- Test-split cost is reported against the baseline and the naive alternatives
- Sensitivity of the chosen thresholds to the cost assumptions is examined

## 4c. OOD Detection, Abstention & Tiered Escalation

- An OOD or unfamiliar-input detection method is implemented and evaluated with in-distribution and out-of-distribution examples relevant to your domain
- An explicit abstention/escalation path returns a structured result with a reason (low confidence, OOD, failed validation, unsupported input) and never silently guesses
- A tiered response (e.g., deterministic check, small model, larger model, human review) is used where appropriate, with a defensible escalation rule
- The trade-off between coverage and accuracy or risk is shown (e.g., selective accuracy vs. abstention rate) and connected to the cost model in 4b

## 4d. Robustness Testing

- Stress tests arise from the risks of your chosen domain (e.g., blur, noise, dialect variation, code-switching, missing fields, corrupted inputs, or a weakened or missing modality)
- Performance degradation is shown across increasing stress levels (tables or curves), not a single point
- The report states which stresses matter most for the user and how the system responds (degrades gracefully, abstains, or fails)

## 4e. Monitoring

- A monitoring layer tracks signals relevant to your setting: confidence distribution, error or feedback rates, input characteristics, latency
- It is demonstrated on a simulated stream of inputs that includes a shift or degradation, and shows the monitor detecting it
- Alert conditions and what a maintainer would do in response are described

# Section 5: Explainability, Failure Analysis & Practical Insights (15 points)

This section is evaluated primarily on the report. The goal is to make the system's behavior visible and to translate technical outputs into plain-English insights connected to concrete actions.

## 5a. Explainability Investigation

- Explainability is treated as an investigation: **controlled probes**, minimal pairs, targeted perturbations, counterfactual examples, or synthetic edge cases that isolate what a model has learned
- Each probe states a hypothesis and what the result would mean
- The analysis assesses whether the system truly uses each modality as intended, and interprets what the evidence supports and where it is ambiguous
- Saliency maps, SHAP plots or other canned visualizations may support the analysis but are not sufficient by themselves

## 5b. Systematic Failure Analysis

- Errors are collected systematically and categorized into a taxonomy with counts (not hand-picked anecdotes)
- Root causes are identified for the main categories (data, model, threshold, rule, input quality)
- Findings are linked to actions taken (new rule, data fix, threshold change, escalation policy) with before/after evidence where possible
- Remaining known failure modes are stated clearly

## 5c. Practical Interpretation & Limitations

- Insights are specific and non-obvious, not restatements of accuracy numbers
- Findings are connected to the original user problem, with a couple of paragraphs on concrete actions they support (deployment decisions, human-review policy, staffing or cost implications, and why the design fits the setting)
- Awareness of limitations, risks, and ethical implications, including who is harmed when the system is wrong and how the design limits that harm

# Section 6: Reproducibility, Development Evidence & Professionalism (15 points)

A project that cannot be understood, run, and verified by a reviewer scores poorly regardless of technical sophistication.

## 6a. Reproducibility Package

- Running `just evaluate` reproduces every number, table and figure in the report
- All random seeds are set and documented; configs are complete and versioned
- Data download or preparation scripts, instructions to obtain model weights or checkpoints, and pinned dependencies are provided
- The project runs from a clean checkout on a Mac using `uv` and `just`, with no manual edits

## 6b. Development Evidence

- Training and hyper-parameter logs are preserved for the runs behind the reported results
- Experiment-tracker exports (e.g., W&B or TensorBoard) are included and consistent with the report
- The git history is **incremental** and shows the development of the work over time. One large final commit or a polished retrospective without the underlying evidence does not demonstrate ownership of the work.

## 6c. Instructor Evaluation Readiness

- The system can be run on a folder of new inputs through a documented command, without code changes
- Outputs remain valid and structured for unfamiliar inputs, and the system answers when it should and abstains when it should
- Performance on the instructor's realistic common and edge-case inputs is judged on sensible behavior, not only accuracy

## 6d. Code Quality & Documentation

- `README.md` covers the project goal, architecture overview, setup (`just install` to `just demo`), and how to reproduce the report's results
- Code is organized in `src/` with no monolithic scripts; Ruff or an equivalent linter passes; docstrings on public functions and classes; no dead code; tests run via `just test`
- Proper citations for datasets and pretrained models; consistent naming and professional polish
