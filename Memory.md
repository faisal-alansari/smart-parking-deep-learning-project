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
- **Next:** Done the same day. A random sample of 16 Sharjah photos was checked (11 approved, first 9 used; 5 rejected). The split was rebuilt: still 7,000 (5,000 / 1,000 / 1,000), no leakage; train now has Ajman 117, Fujairah 273, Sharjah 278 and Dubai 3,563. Next: owner approval of the fine-tuning plan.

### 2026-11-07 | YOLO11n fine-tuning plan

- **Plan:** Fine-tune pretrained YOLO11n (Ultralytics, about 2.6M parameters, pretrained on COCO, AGPL-3.0) to find the plate, each character and the emirate type in one pass. 48 classes (`plate`, 36 characters, 11 emirate types; the plan first said 49, a counting slip; `exp` and UAQ types removed). A fixed-rule assembler reads the characters in order and checks the format; UAQ, a missing emirate or an invalid format go to `NEEDS_REVIEW`. Primary metric: full-plate exact match; also character error rate, plate detection recall and precision, mAP, per-emirate accuracy and review rate. Baseline: YOLO11n trained from random weights on the same data. Validation-only experiments: image size 640 vs 960, head-only vs full fine-tuning, 2,500 vs 5,000 training images. Horizontal and vertical flips off (mirrored plates never occur). Final model: 3 seeds, test opened once at the end. Expected run time: half a day to a day in the background.
- **Outcome:** Approved by the owner on 2026-11-07. Each run trains up to 30 epochs and stops early after 10 epochs without improvement on validation.
- **Next:** Running; results in the entries below.

### 2026-11-07 | Plate model: 960 px images instead of 640 px

- **Decision / reason:** First training-choice test, on validation only: image size 640 vs 960. The car photos are large (1440×1280), and the plate characters become very small when shrunk to 640.
- **Outcome:** 960 px won clearly and is now used for all later runs. Full-plate exact match rose from 35% to 70%, and the character error rate fell from 26% to 9%. Both sizes found the plate almost every time; the gap is in reading the small characters. The cost: training takes about twice as long (about 1.8 hours per run). Even at 960, about 28% of answered plates are still misread, which is too many for a gate.
- **Next:** Continue the planned tests (head-only vs full, 2,500 vs 5,000 images, the from-scratch baseline). Idea, untested and pending owner decision: a second step that crops the found plate, enlarges it and reads the characters from the crop.

### 2026-11-07 | Plate model: full fine-tuning, not head-only

- **Decision / reason:** Second training-choice test on validation: train the whole network vs only the final detection layer (the rest frozen), which is cheaper and less likely to overfit.
- **Outcome:** Head-only failed badly: 4% full-plate exact match vs 70% with full fine-tuning. It still found the plate 99% of the time but could not tell the characters apart. Features learned from everyday COCO photos do not cover plate characters, so the whole network must adapt. Full fine-tuning is kept. Head-only saved only about 40% of the training time.
- **Next:** Keep full fine-tuning. Next test: 2,500 vs 5,000 training images.

### 2026-11-07 | Plate model: training size and from-scratch baseline (validation)

- **Decision / reason:** Last two validation tests. (1) Train on about half the images (2,500 vs 5,000) to see how much the extra data buys. (2) Train the same YOLO11n from random weights, with the same settings and 30 epochs, as the baseline for "does pretraining help?".
- **Outcome:** Halving the data cut full-plate exact match from 70% to 58% and saved about half the training time, so more data clearly helps and the full 5,000 are kept. More data might help further, but that would use the reserve. The from-scratch model learned to find plates (99.7%) but read almost none correctly (0.1% exact match). Starting from pretrained weights is essential with this much data and time. This is a fair same-budget comparison; a scratch model given far longer training would do better.
- **Next:** Final settings: 960 px, full fine-tuning, 5,000 images. Train seeds 43 and 44, then open the test set once.

### 2026-11-07 | Plate model: final test result

- **Decision / reason:** Trained the chosen setup (960 px, full fine-tuning, 5,000 images) with 3 seeds, then opened the test set once.
- **Outcome:** Fine-tuned YOLO11n reads the full plate exactly right on 71% of test images (3 seeds agree within 0.4 points), finds the plate 99.9% of the time and the emirate 97%. The from-scratch baseline reads 0%. Test matches validation (70%), so the choices did not overfit validation. Weak point: 28% of answered plates are misread, which is too many to act on alone. Most misreads are one character off: a dropped character (often the first one, the code letter or digit), an extra repeated character, or a swapped look-alike digit (8/6, 9/8). Abu Dhabi, Ajman and Ras Al Khaimah are weaker, but their test groups are small. About 12 ms per image.
- **Next:** Owner review. Ideas, untested and pending: read characters from an enlarged plate crop; send low-confidence or wrong-length reads to `NEEDS_REVIEW` (tuned on validation only); check the reads on the owner's own videos.

### 2026-11-20 | Occupancy CNN on the owner's own photos (pilot check)

- **Decision / reason:** Before recording videos, check whether the CNN trained only on public data works on the owner's own photos: 8 photos (4 late afternoon, 4 night), each with two bays, covering all four empty/occupied cases. Each bay was cropped by hand to where a car sits. The photos are a check only, never used for training or thresholds.
- **Outcome:** 15 of 16 bays correct; no parked car was missed. Night: 8 of 8. Day: 7 of 8. The one error was an empty bay called occupied. Small tests on that crop point to a large shadow across the empty bay as the main cause, plus part of the neighbouring car inside the box (removing the background cars did not help). Two other empty bays were close calls because the low camera angle puts cars from other rows or bays inside the crop; cutting them out made the answer clearly "empty". Much better than feared given the very different viewpoint, but 16 crops is far too few for firm conclusions, and the day photos came from four different spots.
- **Next:** Record the planned videos from one fixed camera spot. Draw tight bay boxes that avoid neighbouring cars; consider boxes that cover the lower part of each bay. Test shadow cases on purpose. Use the local data to adapt the model and measure false alarms properly.

### 2026-11-20 | Full loop on the owner's photos: occupancy, then plate reading

- **Decision / reason:** Same 8 photos, now with the plate model added: when the occupancy model calls a bay occupied, the fine-tuned YOLO11n reads the plate inside that bay's area. Reading from the whole photo was tried as a comparison.
- **Outcome:** 13 of 16 bays fully right. Of the 7 real plates in occupied bays, 5 were read exactly right (all 4 new-style Dubai plates in normal light, day and night). The car with no plate fitted went to review, which is correct. Three problems: (1) the new white Sharjah plate went to review because that style is missing from the training data (safe, but no answer); (2) a night plate lit by a bright plate lamp lost its letters "AA", a confident-looking wrong read with low confidence (0.25); (3) the empty bay wrongly called occupied made the plate model read a background car's plate as if it were in the bay (dangerous chain). Reading the whole photo misread all 7 plates, because shrinking a tall phone photo makes plates too small, so reading from the bay area is the right design. The first version picked the most confident plate in the bay area; it chose a tiny background plate over the real one, so it now picks the largest plate (the closest car). Plates of cars in the bay were 27–29% of the bay width; background plates were 4–9%.
- **Next:** Ideas, pending owner decision and to be set on validation or video data, not on these 8 photos: send reads whose plate is too small for a car in the bay to review; send low-confidence reads to review; add new Sharjah plates to the data if possible. Retest on the videos.

### 2026-11-20 | Local photos from many car parks; bay boxes per photo

- **Decision / reason:** The owner has no fixed camera yet, and his two home bays would only show 2–3 cars, too few to improve or test the models. So he photographed many pairs of bays in different car parks at night, standing the same way each time: 43 photos, 86 bays (46 empty, 40 occupied). In a real deployment there is one fixed camera and a one-time setup that marks the two bays; the code then crops every frame automatically, with no person or LLM involved. For this project, each photo is treated like its own fixed camera: the cropping code is the same, only the saved box coordinates differ. One shared pair of boxes is tried first (closest to the real system); per-photo boxes only where it does not fit.
- **Outcome:** Agreed by the owner. To report: hand-drawn boxes fit each photo perfectly, so results may be a little optimistic compared with a real camera that can shift; test this later by moving the boxes slightly. If photos are used both to improve and to test the models, split them by car park or area, never at random.
- **Next:** Owner copies the photos to `data/raw/local_night_1/`; then draw boxes, confirm labels with the owner, and run the full loop.

### 2026-11-20 | Full loop on 43 night photos from public car parks

- **Decision / reason:** A larger, harder check than the 8-photo pilot: 43 night photos, 86 bays (46 empty, 40 occupied), one shared pair of bay boxes for all photos like a fixed camera. Check only, nothing trained or tuned on it. Details in `outputs/occupancy/local_night_1/findings.md`.
- **Outcome:** Much worse than the pilot. Occupancy 60 of 86 right: 20 of 46 empty bays called occupied, 6 cars missed. Plates read exactly right for 19 of 34 cars. Controlled tests point to three occupancy causes: other rows of cars and buildings in the top of the box (cutting the top 30% gives 72 of 86), yellow wheel stops in empty bays (unseen in public training data), and close-up light cars that fill the box. The main plate cause: small code letters on the newest two-row Dubai plates fall below the confidence cut-off, so doubled or single code letters get lost, plus "Z" read as "2" and a thin "1" counted several times. A confidence rule would not help (wrong and right reads have similar confidence). Plate size again separates the parked car's plate (13–29% of bay width) from background plates (4–7%). Two rules fixed in advance (plate under 10% of bay width = review; Dubai read without a code letter = review, as no Dubai training label lacks one) would cut dangerous wrong outputs from 16 to 7 without losing a correct read. The public-data models do not transfer well to this kind of site.
- **Next:** Pending owner decision: add the two rules and a better merge for thin characters (check on public validation first); draw real bay boxes without background rows; adapt the occupancy CNN on local photos split by car park, with a second session as the clean test; ask the professor about the 10,000 cap for local training.

### 2026-11-20 | Plate reader: three safety fixes after the night test

- **Decision / reason:** The owner asked to fix the plate step first. Three rules, each tied to a failure seen on the night photos and checked on the public validation set: merge duplicate boxes for one thin character (overlapping sideways by more than half), send a Dubai read without a code letter to review (no main Dubai plate in the training or validation labels lacks one), and send a plate narrower than 10% of the bay width to review (it belongs to a car further back).
- **Outcome:** Worked. Validation: exact match 69.7% → 71.9%, misreads 28.4% → 20.2%, at the cost of about 6% more plates going to review. Night set: dangerous wrong reads 16 → 6 (no more plates read in empty bays), correct reads 19 → 20. Pilot: dangerous outputs 2 → 0. A first merge cut-off of 70% missed a triple "1"; 50% was chosen on validation, not on the night photos. The 6 remaining misreads are doubled or swapped code letters, which these rules cannot catch.
- **Next:** Rerun the public plate test set once when the plate system is final. Later: better reading of small code letters (enlarged plate crop or more examples of the newest Dubai plates). Then start Model C (typed commands) and the permit table.

### 2026-11-21 | Evidence saved for every night-set finding

- **Decision / reason:** The owner asked whether each finding is justified. Some numbers came from one-off checks that were never saved, and some reasons were guesses. Each one now has a saved script or table, wheel stops are marked bay by bay in the set's config, and each finding is labelled "measured" or "hypothesis".
- **Outcome:** Validation before/after and the merge cut-off choice reproduced exactly. Four numbers changed when redone properly, with the same conclusions: wheel stops (15 of 26 bays with a stop gave false alarms vs 5 of 20 without; 10 of 11 remaining false alarms have one), brightness (92 vs 91, no difference), lost code letters (on 4 of 6 plates reviewed for a missing letter, the letter was found below the cut-off; on 2 it was not found), and the Dubai count (4,302 main plates, none without a letter; 98 of 500 smaller background plates lack one, often because they are only partly labelled). Untested reasons (training data lacking wheel stops, close-up cars, the white Sharjah plate) stay marked as hypotheses.
- **Next:** No change to the plan. The configs and per-bay results with real plates stay out of Git until the owner decides how to hide them.

## Decision log

For each **meaningful** new decision, add one short entry:

### YYYY-MM-DD | Decision title

- **Decision / reason:** What we chose or tested, and why.
- **Outcome:** Worked, failed, or inconclusive. Explain the practical lesson.
- **Next:** Keep, change, reject, or retest.

