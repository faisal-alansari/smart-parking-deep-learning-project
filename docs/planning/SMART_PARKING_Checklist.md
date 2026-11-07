# Smart Parking — Final Rubric Checklist

Based on `Final rubrics.txt` and the updated `SMART_PARKING_Audit_Project.md`.
Approved modalities: **Visual + Text + Tabular**. Local prototype for two parking bays, a 3–4-car permanent whitelist, and temporary visitor permits. No automated fines or production deployment.

## 1. Foundation & Models

- [x] Set up Python 3.14, `uv`, `just`, Pydantic, Loguru, configs, and seeds.
- [ ] Audit datasets, clean labels, prevent split leakage, and track the 10,000-item fine-tuning cap.
- [ ] Train the two-bay occupancy CNN **from scratch**.
- [ ] Fine-tune pretrained **YOLO11n** for complete UAE plate identity.
- [ ] Benchmark and select a **pretrained NLP model without fine-tuning**.
- [ ] Verify model parameter limits, local weights, and actual camera/plate feasibility.

## 2. Integrated Product

- [ ] Detect bay occupancy, confirm arrivals, and capture evidence frames.
- [ ] Parse English visitor commands and update one in-memory permit table **after confirmation**.
- [ ] Match full plate, bay, and time to return `AUTHORIZED`, `POTENTIALLY_UNAUTHORIZED`, or `NEEDS_REVIEW`.
- [ ] Integrate all **three approved modalities** in one end-to-end workflow.
- [ ] Build CLI + simple UI, structured outputs, user feedback, and safe error/review handling.

## 3. Experimental Evidence

- [ ] Define the primary metric, 2–3 ML metrics, and 2 practical metrics.
- [ ] Compare fair baselines for occupancy, plate recognition, and NLP parsing.
- [ ] Run modality/component ablations and logged training-choice experiments.
- [ ] Measure uncertainty, unseen-input generalization, latency, memory, and efficiency.
- [ ] Report test results against targets with reproducible tables and figures.

## 4. Trust & Investigation

- [ ] Measure calibration with reliability diagrams and ECE.
- [ ] Build an asymmetric error-cost model and validation-selected thresholds.
- [ ] Evaluate OOD detection, abstention, human review, and risk–coverage trade-offs.
- [ ] Run increasing-severity robustness tests for images and commands.
- [ ] Demonstrate monitoring alerts on a simulated input shift.
- [ ] Run controlled explainability probes and counted failure analysis with fixes.

## 5. Final Delivery

- [ ] Automate install, train, evaluate, demo, test, clean, ablations, robustness, and batch inference via `just`.
- [ ] Make `just evaluate` reproduce **every reported result**.
- [ ] Preserve incremental Git history, checkpoints, logs, and experiment exports.
- [ ] Complete README, code tests, citations, and clean-checkout Mac verification.
- [ ] Submit the **5–8-page, ≤3,000-word Markdown final report** with results, limitations, and risks.
