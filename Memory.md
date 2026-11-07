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

- **Decision / reason:** The owner records phone videos of the two real bays, because public data looks very different from the real site and has almost no night images. Data for the from-scratch occupancy model is outside the 10,000 fine-tuning cap; plate images from these videos used to fine-tune YOLO do count. Use frames sampled every few seconds, not every frame, since nearby frames are near-copies.
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
- **Next:** Owner review. Later: calibration, cost-based thresholds and robustness, then adapt and test on the owner's videos.

## Decision log

For each **meaningful** new decision, add one short entry:

### YYYY-MM-DD | Decision title

- **Decision / reason:** What we chose or tested, and why.
- **Outcome:** Worked, failed, or inconclusive. Explain the practical lesson.
- **Next:** Keep, change, reject, or retest.

