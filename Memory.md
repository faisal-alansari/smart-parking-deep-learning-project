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

### 2026-11-06 | Occupancy data: cleaning, splits and sampling (CNRPark+EXT)

- **Decision / reason:** Use CNRPark+EXT for the from-scratch occupancy model. Hold out camera C02 (closest view, 9 bays) and the CNRPark A/B site completely, to test unseen cameras and an unseen site. Split the other 8 cameras by the official day lists. Drop blank images, the 26 crops whose two label sources disagree, and crops too dark to check by eye. Remove near-copies of the same bay, then balance train to 20,000 free and 20,000 busy, spread evenly over cameras.
- **Outcome:** Worked. Labels look right on visual checks, and leakage checks pass. Train is 40,000 crops. Val and test keep their natural mix (val is only 35% free). Almost no night data, so night must come from our own videos and NDISPark. The 26 disagreeing crops looked empty, so the CSV label seems right, but they are dropped to be safe. Uses 0 of the 10,000 fine-tuning items.
- **Next:** Approved by the owner on 2026-11-07. Then baselines, then the occupancy CNN.

### 2026-11-06 | Own-site video data: budget, timing and recording plan

- **Decision / reason:** The owner records phone videos of the two real bays, because public data looks very different from the real site and has almost no night images. Data for the from-scratch occupancy model is outside the 10,000 fine-tuning cap; plate images from these videos used to fine-tune YOLO would count (superseded on 2026-11-07: videos will not be used for plate fine-tuning). Use frames sampled every few seconds, not every frame, since nearby frames are near-copies.
- **Plan:** 9 sessions of about 15 minutes with the same script (both empty → bay 1 parked → both parked → bay 1 leaves → bay 2 leaves), each with one extra event (plate test, passing car, partial entry, reverse-in, person walking, bad parking, headlight glare). Sessions 1–7 cover morning, noon, afternoon, dusk and night for training; sessions 8 (day) and 9 (night), on different days, are never trained on. The owner writes down when each bay changes, so frames can be labelled from the times.
- **Outcome:** Pending. Recording runs in parallel with training on public data. Local data is added after the public-only model works, so the two can be compared.
- **Next:** Record. Confirm with the professor that further training our own scratch model on local data is not counted as fine-tuning.

### 2026-11-07 | Site check from a reference night photo

- **Decision / reason:** Checked whether the real site suits the project, using one night photo.
- **Outcome:** Suitable. The plate was readable at night under the street lights. Changes needed before recording: move the phone so the pole between the bays does not hide the bays or plates; use landscape; frame less sand and sky; mark bay corners in the first session (there are no painted lines); keep the camera fixed so bay crops stay valid. The view is low and from behind, very unlike the high public cameras, so the public-only model may transfer poorly. That makes local data essential and is the public-only vs local comparison the plan asks for.
- **Next:** Owner to decide where the real camera will be mounted and record from as close to that spot as possible. Blur cars outside the two bays in saved evidence.

### 2026-11-07 | Occupancy baselines and training rules

- **Decision / reason:** Two baselines only: a texture threshold (inspection showed empty bays look flat, so this tests whether the CNN learns more than "flat = free") and HOG + logistic regression (the classical method named in the plan). mAlexNet was proposed as a third baseline and rejected by the owner. Image difference waits for the owner's videos, since it needs a fixed camera and an empty reference frame. Metrics: F1, recall, precision, false positive rate and accuracy for "occupied", with confidence intervals and 3 seeds for the CNN. Validation data alone is used for model choice, settings and thresholds; all test sets stay untouched until the final comparison. Vertical flips are never used; horizontal flips only if a validation experiment supports them.
- **Outcome:** Done; results are in the next entry.
- **Next:** See next entry.

### 2026-11-07 | OccupancyCNN on public data: training choices and final comparison

- **Decision / reason:** Small CNN (about 294k parameters, far under the 50M limit) trained from scratch on the 40k balanced crops. Tested learning rate, augmentation (none / brightness-contrast-blur-shift / plus horizontal flips), regularization and input size (64 vs 96 px) on validation, one setting at a time. A new option had to beat the current one by more than 0.002 val F1.
- **Outcome:** The starting settings were kept (lr 0.001, brightness/contrast/blur/shift augmentation, light regularization, 64 px). All options were within about 0.003 val F1 of each other, so the CNN is not sensitive to these choices here; the differences are inconclusive. Horizontal flips did not help, so they are not used. 96 px took 2.3× longer with no gain, so 64 px stays. On the test sets (3 seeds), the CNN beats both baselines: F1 0.993 on same cameras, 0.988 on the unseen camera, 0.929 on the unseen site (HOG baseline: 0.946, 0.965, 0.854). Two lessons. (1) The baselines lost much more than the CNN between validation and test, mainly through false alarms; a threshold tuned on one class mix transfers poorly. (2) The unseen site is the clear weak point (about 8% false alarms), which supports the need for local video data.
- **Next:** Accepted by the owner on 2026-11-07. Later: calibration, cost-based thresholds and robustness, then adapt and test on the owner's videos.

### 2026-11-07 | Videos later; folder layout for submission

- **Decision / reason:** The owner will record videos (not photos) soon. Videos are needed for arrival timing, false-alert and missed-arrival metrics, and realistic night tests; photos would only help CNN training. Until then we work on parts that do not need them, starting with plate reading. The project was reorganized for submission: one folder per component (occupancy now, plates next) used the same way in `src/`, `tests/`, `outputs/`, `experiments/` and `checkpoints/`; planning documents in `docs/planning/`; datasets in `data/raw/` (untouched downloads) and `data/processed/` (built by our code); a data card in `docs/data_card.md`.
- **Outcome:** Worked. After the move, all data and result files were rebuilt and are identical to before; tests and lint pass.
- **Next:** Keep this layout for every new component. Next: audit the AddingUAE plate data.

### 2026-11-07 | AddingUAE plate data audit

- **Decision / reason:** Audit the plate data before fine-tuning YOLO11n, because its quality, leakage and coverage decide what results we can trust.
- **Outcome:** Mostly good data with fixable problems. File names carry the main plate's text, which gave a free label check: about 98% of named car photos match their labels exactly. Problems: the export's random split leaks 118 plate identities across splits; 359 plate-only images lack a `plate` box (training on them would teach the model to ignore visible plates); some photos are mock-ups with edited plates; Dubai dominates and new-style Sharjah plates are missing. YOLO11n (about 2.6M parameters) installs and runs on Python 3.14 (ultralytics, AGPL-3.0 license).
- **Next:** Superseded: the 4,500-image plan was replaced by the 7,000-image plan in the next entry.

### 2026-11-07 | Plate subset, split and fine-tuning budget (agreed)

- **Decision / reason:** The owner's videos will focus on cars entering and leaving the two bays and will show only 2–3 different plates. That is far too few to teach plate reading, so YOLO11n will **not** be fine-tuned on video frames; those frames are only a real-site check (is the plate readable from the camera spot, and are the owner's plates read correctly). This supersedes the earlier note that video plate images would be used for fine-tuning. The large reserve kept for video plates is no longer needed, so the plate set grows from 4,500 to **7,000 images: 5,000 train, 1,000 validation, 1,000 test**, leaving about 3,000 of the 10,000 cap in reserve (local occupancy crops if the professor counts them, test frames, safety margin).
- **Rules:** Car photos only (no plate-only or close-up images). Images whose labels exactly match the file name (verified), except that unverified RAK and UAQ car photos may be added to train only after a visual check, because so few are verified. Split by plate identity and image similarity, so the same plate or near-identical photos (including mock-ups) never cross splits. Include all plates from the smaller emirates and every image with X, Y or Z. Count every image (train, validation and test) in the ledger. A 2,500 vs 5,000 training-size comparison will serve as the quality-vs-cost study.
- **Outcome:** Agreed by the owner on 2026-11-07. Known gaps: new-style Sharjah plates are absent and UAQ is too small to test reliably; both go to `NEEDS_REVIEW` and are reported as limits.
- **Next:** Built the same day (`just prepare-plates`): exactly 5,000 / 1,000 / 1,000, no leakage, same result on every run. 95 of 114 unverified RAK / UAQ photos passed the visual check (19 rejected for wrong or incomplete characters, unclear plates, or a wrong emirate type). Because val and test keep each emirate's share, RAK has only 10 val and 10 test images and UAQ only 1 each, so their results will be indicative only. Pending owner review before fine-tuning.

### 2026-11-07 | Umm Al Quwain and unknown-emirate plates go straight to human review

- **Decision / reason:** The owner decided that Umm Al Quwain plates (37 images) and plates with no emirate box (44 images) are too few to train or test on. They are removed from the plate subset, and the product will send them straight to `NEEDS_REVIEW`.
- **Outcome:** Done. The 81 freed places were refilled to keep 7,000 images (5,000 / 1,000 / 1,000). Every verified image from the other smaller emirates was already included, so the refill came from verified Dubai photos. No leakage; tests pass.
- **Next:** Superseded: the Dubai refill was replaced by checked non-Dubai photos (next entry).

### 2026-11-07 | Refill the 81 places with checked non-Dubai photos

- **Decision / reason:** Dubai already dominates, so the owner wants the 81 freed places used for the smaller emirates, especially Ajman and Ras Al Khaimah. A check of all non-Dubai images left out found no more RAK car photos (only 29 plate close-ups, which break the car-photos-only rule). 86 unverified Ajman and Fujairah car photos were checked by eye: 72 approved (32 Ajman, 40 Fujairah), 14 rejected for wrong or extra digits, a missing code letter, a sideways photo, or unreadable plates. The last 9 places come from checked Sharjah photos. All of these go to train only, as agreed for unverified photos, so val and test keep only verified labels.
- **Outcome:** Agreed by the owner on 2026-11-07. Ajman train grows from 85 to about 117. Most new Fujairah photos are taxi plates from one fleet: a useful plate style, but little car variety.
- **Next:** Check Sharjah photos, rebuild the split, then owner approval of the fine-tuning plan.

### 2026-11-07 | Proposed YOLO11n fine-tuning plan (pending approval)

- **Plan:** Fine-tune pretrained YOLO11n (Ultralytics, about 2.6M parameters, pretrained on COCO, AGPL-3.0) to find the plate, each character and the emirate type in one pass. 49 classes (`plate`, 36 characters, 12 emirate types; `exp` and UAQ types removed). A fixed-rule assembler reads the characters in order and checks the format; UAQ, a missing emirate or an invalid format go to `NEEDS_REVIEW`. Primary metric: full-plate exact match; also character error rate, plate detection recall and precision, mAP, per-emirate accuracy and review rate. Baseline: YOLO11n trained from random weights on the same data. Validation-only experiments: image size 640 vs 960, head-only vs full fine-tuning, 2,500 vs 5,000 training images. Horizontal and vertical flips off (mirrored plates never occur). Final model: 3 seeds, test opened once at the end. Expected run time: half a day to a day in the background.
- **Outcome:** Pending owner approval.
- **Next:** Approve or change, then fine-tune.

## Decision log

For each **meaningful** new decision, add one short entry:

### YYYY-MM-DD | Decision title

- **Decision / reason:** What we chose or tested, and why.
- **Outcome:** Worked, failed, or inconclusive. Explain the practical lesson.
- **Next:** Keep, change, reject, or retest.

