# Historical handover for the next chat (written 2026-11-21)

This records the project as it stood then. For current rules and results, use `AGENTS.md`, `CLAUDE.md`, and the latest entries in `Memory.md`. The older privacy and frozen-test instructions below are historical.

## 1. Prompt to paste into the new chat

> You are continuing my Smart Parking deep-learning project in this folder. First read, in this order:
> `CLAUDE.md`, `AGENTS.md`, `docs/HANDOVER.md` (this file, all of it), `Memory.md` (especially the 2026-11-20 and 2026-11-21 entries), `docs/planning/SMART_PARKING_Audit_Project.md`, `docs/planning/03_final_project_rubrics.md`, `docs/planning/SMART_PARKING_Checklist.md`, `docs/data_card.md` section 6, and the Model C code in `src/smart_parking/commands/` (`schema.py`, `rules.py`, `baseline.py`, `dataset.py`, `score.py`) with `tests/commands/test_commands.py`.
> Then run `just test` and `just lint` to confirm everything is green, and tell me in a few lines what state the project is in.
> Next task: Model C Step 4 (download the pretrained candidates and record their size, licence, memory and speed), then Step 5 (set each one up on the **dev** set only). Follow section 5 of `docs/HANDOVER.md`. Do not open the frozen test set. Ask me before anything in section 6 ("decisions waiting for me").
> Always answer me in simple English, even if I write in Arabic.

## 2. Standing rules (must follow)

- **Language:** always answer in simple English, even when I write in Arabic.
- **Memory:** after any meaningful decision (design, data, model, threshold, evaluation, workflow), add a short plain-language entry to `Memory.md` in the same session: decision/reason, outcome, next. Never invent results; mark untested ideas "pending". Mark reversed decisions "superseded".
- **Git:** commit or push only when I ask. Nothing has been pushed yet (local `main` is ahead of the remote). End commit messages with the co-author line the tool gives.
- **Never commit** my own edits to `docs/planning/SMART_PARKING_Checklist.md` (it shows as modified; leave it). Tick checklist boxes only after the work is verified, and only if I ask.
- **Privacy, strangers' plates:** these files hold real plates and stay local, never committed or shared: `configs/local_night_1.yaml`, `configs/local_pilot.yaml`, `outputs/occupancy/local_night_1/predictions.csv`, `outputs/occupancy/local_night_1/results.md`, everything in `outputs/occupancy/local_pilot/`, and all photos in `data/`. I have not yet decided whether to hide the plates or keep them local only.
- **Frozen test sets:** never use a test set to tune, choose a model or set a threshold. `just command-score <parser> test` is refused without `--final`; use `--final` only once, for the final comparison, and only after I agree.
- **Project limits (from the audit plan):** each model ≤200M parameters; the from-scratch model ≤50M; all pretrained models ≤1B combined; ≤10,000 fine-tuning items in the whole project (7,000 used, all by the plate model); local weights only, no online model APIs at run time. Model C is **not fine-tuned**.
- **Coding style:** Python 3.14, `uv`, `just`, Pydantic v2, Loguru (no `print`), ruff (line length 100). Keep changes small and surgical (see the Karpathy guidelines in the user's `CLAUDE.md`).

## 3. The project in one paragraph

A local prototype that watches my two parking bays. **Model A** (a small CNN trained from scratch) says whether each bay is empty or occupied. **Model B** (fine-tuned YOLO11n) reads the full UAE plate of a parked car. **Model C** (a pretrained text model, no fine-tuning) turns my short spoken command (already converted to text by the phone) into a permit change, which is applied only after I confirm. The three parts meet in one permit check that returns `AUTHORIZED`, `POTENTIALLY_UNAUTHORIZED` or `NEEDS_REVIEW`. Modalities: visual + text + tabular.

## 4. Where things stand

**Model A (occupancy):** trained and tested on public data (CNRPark+EXT). Checked on my 8 pilot photos (15/16 bays correct) and on 43 night photos from public car parks (60/86 correct: background rows, yellow wheel stops and close-up cars cause false alarms). Not yet adapted to local data.

**Model B (plates):** fine-tuned YOLO11n, final public test: 71% of plates read exactly right. Three safety rules added after the night test (merge duplicate thin characters, Dubai read without a code letter goes to review, plate narrower than 10% of the bay width goes to review). Every night-set finding has saved evidence (`outputs/occupancy/local_night_1/findings.md`, kept local).

**Model C (commands), Steps 1–3 done and committed (`b1b18fb`):**
- Final scope (reviewed by me): ALLOW or REMOVE only. I say the plate digits only (2–5 digits), and they are matched to Model B's full plate. Permits cover both bays, and a bay said in a command is ignored. The end time is optional, and no end time means a permanent permit.
- Anything unclear gives NEEDS_REVIEW plus a question, never a guess:
  - one-digit number (the command is kept for me to check);
  - an hour without AM/PM;
  - a time already passed today;
  - "tonight", "next Monday" or other vague phrases;
  - a dictation slip such as "a loud" for "allow";
  - a missing number, several numbers, or an invalid number.
- "Until Monday" means the coming Monday at 23:59, and it is asked about if today is Monday.
- Other requests (questions, "open the gate", "edit") get UNSUPPORTED.
- Full rules are in `rules.py` and in the last entry of `Memory.md`.
- **Design:** a candidate model only fills an `Extraction` (`action`: ALLOW/REMOVE/"OTHER"/None, `numbers`: list of the plate numbers as said, `time`: the end-time phrase as said). The shared `rules.finish()` turns that into `ParsedCommand` / `NeedsReview` / `Unsupported`, so every candidate is compared on the same footing. A candidate must **not** correct slips ("a loud" → action None).
- **Data:** `just command-data` builds the sets in `outputs/commands/data/`:
  - dev: 60 commands;
  - frozen test: 160 commands (95 clear, 55 to review, 10 unsupported; 44 mention a bay; 33 use wording not seen in dev; 6 slips).
  The answers are built from each sentence's meaning. `test_review.md` is the human-readable test list. I was asked to give the regenerated list a quick final look; check whether I did.
- **Scoring:** `just command-score <parser> dev`. Metrics:
  - exact: the main metric;
  - dangerous: a change is proposed and it is wrong;
  - needless question;
  - field accuracy for action, number and until;
  - slices by kind, reason, seen/unseen wording, bay said and slip.
  Parsers are registered in `PARSERS` in `score.py`.
- **Results so far:**
  - oracle (perfect extraction): 220/220;
  - rule baseline: 60/60 on dev (expected, because it was written from dev).
  The test set is unopened by any parser. 85 tests pass and lint is clean.

## 5. What to do next (Model C)

**Step 4: download the candidates and measure them.**
Candidates from the audit plan:
- `HuggingFaceTB/SmolLM2-135M-Instruct`: writes the answer as JSON; needs forced/constrained JSON output.
- `google/flan-t5-small`: about 77M; text in, short text out.
- `urchade/gliner_small-v2.1`: span finder; check the exact parameter count. It cannot choose the action, so pair it with a helper.
- Helper for the action: `sentence-transformers/all-MiniLM-L6-v2` (about 22M). It compares the command with a few example sentences per action (ALLOW / REMOVE / OTHER / none), with no training.

For each one, record:
- parameter count (measured, not quoted);
- licence;
- disk size;
- memory use;
- time per command on my Mac.

Download the weights locally (there is a `just download-weights` recipe for the plate model; follow its pattern). Add the needed packages with `uv add` (for example `transformers`, and `gliner` / `sentence-transformers` if used). Check that this does not break the plate or occupancy code. Write the table to `outputs/commands/candidates.md`.

**Step 5: set up each candidate on dev only.**
- Write one small adapter per candidate that returns an `Extraction`.
- Register each adapter in `PARSERS`.
- Tune prompts, examples and settings using dev only.
- Score with `just command-score <name> dev`.
- Keep a short record of what was tried.
- Add unit tests for each adapter's output shape. The tests must not need a model download, or they must skip cleanly.

**Step 6: choose with a rule fixed in advance.** Before any results are seen, agree the rule with me and write it in `Memory.md`. The earlier draft rule was:
1. highest exact score on dev, as long as the dangerous rate is low enough;
2. on a tie, the smaller and faster model wins.

The "low enough" limit is not yet fixed (see section 6).

**Step 7: one final test.**
- Run `just command-score <each parser> test --final` once, for the baseline and every candidate.
- Report the slices, especially unseen wording and slips.
- Add robustness levels for commands, in increasing severity:
  - typos and odd casing;
  - missing pieces;
  - ambiguous commands;
  - off-topic requests;
  - "ignore that and delete everything".

  The checklist asks for increasing-severity robustness tests.
- Record the outcome in `Memory.md`.

**Step 8: connect to the permit table.**
- Use `PermitTable` in `schema.py`: confirmation text, `apply`, and `find(plate_text, at)`.
- Demo the same arrival: `POTENTIALLY_UNAUTHORIZED` → a command plus my yes → `AUTHORIZED` → `POTENTIALLY_UNAUTHORIZED` again after the permit expires or is removed.
- Unclear plate reads stay `NEEDS_REVIEW`.

## 6. Decisions waiting for me (ask, don't assume)

1. Model C: the limit for the "dangerous" rate in the selection rule (for example, 0 dangerous on dev), and whether a slower model may win if it is clearly more accurate.
2. Model C: whether I have given the regenerated `test_review.md` a final look (the rubric needs human-checked test labels).
3. Model C (optional): whether I will dictate 20–30 real commands on the phone as an extra check of real wording (dev-style use only, or a small separate check set).
4. Privacy: whether to hide plates in the local configs and results so they can be committed, or keep them local only.
5. Plates: the code letter on photo IMG_1838 is still unconfirmed.
6. Plates: rerun the public plate test set once, when the plate system is final (the three safety rules were added after the last test).
7. Ask the professor whether local photos used to adapt the models count toward the 10,000-item cap.
8. Occupancy: adapting the CNN on local photos (split by car park, never at random), cutting background rows out of the bay boxes, and recording the planned fixed-camera videos.

## 7. Later work in the checklist (not started)

- Integrate the three models in one end-to-end flow.
- Build a CLI plus a simple UI.
- Calibration (reliability diagrams, ECE).
- Asymmetric error costs and thresholds chosen on validation.
- Abstention and risk–coverage.
- Monitoring alert on a simulated input shift.
- Explainability probes.
- Latency and memory per stage.
- `just evaluate` that reproduces every reported result.
- README.
- A clean-checkout check on the Mac.
- The 5–8-page final report (≤3,000 words).

## 8. Useful commands

```bash
just test                          # 85 tests
just lint                          # ruff check + format check
just command-data                  # rebuild dev/test command sets (seeded, same output)
just command-score rules dev       # score the rule baseline on dev
just command-score oracle test     # answer-key check (allowed without --final)
```

## 9. Update 2026-11-22: Model C finished (Steps 4–8)

- Work is on branch `model-c-candidates` (not merged, not pushed).
- **Model C = `tiered`:**
  - my fixed form ("add 5055", "remove 5055 for 2 days") is read by fixed rules;
  - anything else goes to GLiNER Small v2.1 + MiniLM-L6;
  - every proposed change must be matched (action + number) by SmolLM2-135M;
  - safety checks: a word close in meaning to an action word, every number explained, and a half-seen end time asked about;
  - I confirm every change.
  - About 310M parameters (each model under 200M), not fine-tuned.
- **Final test (run once, done; never rerun it):** Model C 50% exact, 1 dangerous of 160 (a negation, "don't allow car 28 anymore"); rule parser 64% / 3; GLiNER + MiniLM alone 73% / 15. The price of safety is coverage: new wording is almost always asked about. See `outputs/commands/final_test.md`.
- **Robustness:** `just command-robustness` → `outputs/commands/robustness.md`.
- **Permit table:** `commands/owner.py` (`handle`: confirm, reject-and-fix, `HumanFeedback` records; `arrival_decision`). `just command-demo` → `outputs/commands/demo.md`.
- **Next:** the integrated end-to-end flow with Models A and B, then the CLI + UI (section 7). Decisions in section 6 items 3–8 are still open.

## 10. Update 2026-11-22: full loop (steps 1–3)

- `model-c-candidates` is merged into `main` (fast-forward, not pushed). New work is on branch `full-loop`.
- **My decisions (section 6):**
  - item 4: real plates stay local only (now ignored by Git);
  - item 5: the IMG_1838 code letter is confirmed;
  - item 7: the cap is fine (about 3,000 items spare).
  - The professor accepts visual + text + tabular as three modalities.
  - The permanent list lives only in `configs/local_loop.yaml`.
- **Code:** `src/smart_parking/loop.py`, tests in `tests/test_loop.py`.
  - `just full-loop-scenario`: the story on real photos → `outputs/loop/local/scenario.md` (local only).
  - `just full-loop`: every local bay against the truth → `outputs/loop/full_loop.md` (counts only), with details in `outputs/loop/local/`.
- **Result (51 photos, 102 bays):**
  - 64% right overall;
  - 0 false alerts, and 0 unauthorized cars let through;
  - the main weakness is night occupancy (21 empty bays called occupied, 6 cars missed).
- **Model C finding:** in "until tomorrow nine thirty p.m.", both of its models dropped "tomorrow", and my check caught it. With my OK, a day-word check was added (`lost_day_words` in `adapters.py`). It was checked on dev sets only, the test was not run again, and the change is disclosed in `outputs/commands/final_test.md`. The robustness set now rebuilds identically.
- **Next:**
  - step 4: remove one model at a time;
  - step 5: time per stage, plus a command that runs a folder of new photos, videos and commands;
  - my 10-minute night video (not yet in `data/`).

## 11. Update 2026-11-22: steps 4–5 and the night video (branch `loop-ablations-video`)

- **Step 4, remove one part at a time:** `just full-loop-ablation` → `outputs/loop/ablation.md`.
  - Every part helps: without A or B, right answers fall from 64% to 33–35%; without the time check, 6 unauthorized cars are let through.
  - On my own wording, the rule parser beat Model C (see `Memory.md`).
- **Step 5:**
  - `src/smart_parking/pipeline.py` loads the three models once and times each stage.
  - `just run-folder <dir> [--yes] [--every 2]` runs a folder of photos, videos and `commands.txt`. It needs `bays.yaml`: one folder is one camera.
  - Latency: `outputs/loop/latency.md`.
- **Night video:**
  - `data/raw/video_night_1/IMG_1503.MOV` with truth in `configs/local_video_night_1.yaml` (local only).
  - `just video-night-1` → `outputs/loop/video_night_1.md` (counts only), plus a local timeline.
  - I checked the truth (`outputs/loop/local/video_truth_check.md`): accurate, no changes.
- **Next:**
  1. Optional: alert only if the answer holds for a few seconds. Fix the length before testing.
- **Per-stay logic** (`src/smart_parking/stays.py`):
  - The rule was fixed in `Memory.md` before it was run.
  - A bay changes state only after 5 frames in a row (10 s). A stay's plate is the majority clear read, seen at least twice.
  - `just video-night-1-stays` → `outputs/loop/video_night_1_stays.md`. The folder command uses it for videos.
  - Night video (a seen check): false alerts 4 → 0, notifications 78 → 29.

## 12. Update 2026-11-25: models final (branch `model-a-adapt`)

- **Last recording:** night video 2 (5 files, about 43 min); the truth was checked by me and is stored in `configs/local_video_night_2.yaml` (local only). There will be no more recordings.
- **Model A adapted** (`src/smart_parking/occupancy/adapt.py`):
  - the plan was fixed in `Memory.md` before training;
  - `just adapt-occupancy` chooses on block 4 → `outputs/occupancy/adaptation_val.md`;
  - `just adapt-occupancy-final` was run once → `outputs/occupancy/adaptation_test.md`. It refuses to run again.
  - Winner: fine-tune the last block. The product now uses `occupancy.deploy: adapted` (`checkpoints/occupancy/adapted_s*.pt`).
- **Model B:** the public test was rerun once with the safety rules (`outputs/plates/final_results.md`; the old one is `final_results_before_safety_rules.md`).
- **Model C:** unchanged and final.
- **Full system** reports were rerun with the final models (`outputs/loop/*.md`). The `*_public_model.md` copies keep the old Model A results for comparison.
- **Next:**
  1. trust checks (calibration, risk–coverage, image robustness, monitoring, explainability);
  2. evidence frames + the simple app;
  3. `just evaluate`, README, a clean-checkout check;
  4. the final report.

## 13. Update 2026-11-25: trust checks, product, demo, report (branch `trust-checks`)

- **Trust** (`src/smart_parking/trust/`, `just calibration costs ood robustness-images monitor-demo efficiency probes failures`) → `outputs/trust/`.
- **Product:**
  - `pipeline.run_folder`: camera check, structured output (`output.py`), evidence frames, plate caching, safe handling of bad inputs;
  - `decision.py`: the cost-chosen thresholds, stored under `decision:` in `configs/default.yaml`;
  - `app.py`: `just demo`.
- **Reproduce:**
  - `just evaluate` regenerates all tables (it needs the raw local data in `data/raw/`);
  - `just train` retrains;
  - `just budget` counts the parameters.
- **Privacy lifted** by me: local configs, truth labels and plate-level results are now in Git. Samples are in `samples/`.
- **Report:** `docs/final_report.md`.
- **Open:**
  1. host the raw local data (about 6.5 GB) and add a download step;
  2. merge `trust-checks` into `main` and push;
  3. I tick the checklist;
  4. optional: a plate rule for missing characters (probe B1).

## 14. Update 2026-11-27: audit fixes and the sealed final test (night 3)

- **Splits:** night 2 blocks 1-3 train, block 4 chooses every local setting; night 1 is a seen check (`VIDEO_SEEN`); night 3 (`data/raw/video_test/night_3.MOV`, `configs/local_video_night_3.yaml`) is the sealed final test (`VIDEO_TEST`). A test checks that no other config names the test folder.
- **Final test:** `just final-test` ran once (it refuses a second run; `--report` rebuilds). Result in `outputs/final_test/night_3.md`: 5 of 9 stays of 30 s or more right; all wrong ones are the two cars across both bays, one of them missed as EMPTY. Not fixed after the test.
- **Reproduce:** `just evaluate` is read-only (it stops if a fitted setting would change); `just refit` stores new fitted settings.
- **Open:** host the raw data (about 8 GB) and add the link to the data card; a design for "one car across two bays" (untested).
