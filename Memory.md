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
- **Next:** I approved this on 2026-11-07. Then baselines, then the occupancy CNN.

### 2026-11-06 | Own-site video data: budget, timing and recording plan

- **Decision / reason:** I record phone videos of the two real bays, because public data looks very different from the real site and has almost no night images. Data for the from-scratch occupancy model is outside the 10,000 fine-tuning cap; plate images from these videos used to fine-tune YOLO would count (superseded on 2026-11-07: videos will not be used for plate fine-tuning). Use frames sampled every few seconds, not every frame, since nearby frames are near-copies.
- **Plan:** 9 sessions of about 15 minutes with the same script (both empty → bay 1 parked → both parked → bay 1 leaves → bay 2 leaves), each with one extra event (plate test, passing car, partial entry, reverse-in, person walking, bad parking, headlight glare). Sessions 1–7 cover morning, noon, afternoon, dusk and night for training; sessions 8 (day) and 9 (night), on different days, are never trained on. I write down when each bay changes, so frames can be labelled from the times.
- **Outcome:** Pending. Recording runs in parallel with training on public data. Local data is added after the public-only model works, so the two can be compared.
- **Next:** Record. Confirm with the professor that further training our own scratch model on local data is not counted as fine-tuning.

### 2026-11-07 | Site check from a reference night photo

- **Decision / reason:** Checked whether the real site suits the project, using one night photo.
- **Outcome:** Suitable. The plate was readable at night under the street lights. Changes needed before recording: move the phone so the pole between the bays does not hide the bays or plates; use landscape; frame less sand and sky; mark bay corners in the first session (there are no painted lines); keep the camera fixed so bay crops stay valid. The view is low and from behind, very unlike the high public cameras, so the public-only model may transfer poorly. That makes local data essential and is the public-only vs local comparison the plan asks for.
- **Next:** I need to decide where the real camera will be mounted and record from as close to that spot as possible. Blur cars outside the two bays in saved evidence.

### 2026-11-07 | Occupancy baselines and training rules

- **Decision / reason:** Two baselines only: a texture threshold (inspection showed empty bays look flat, so this tests whether the CNN learns more than "flat = free") and HOG + logistic regression (the classical method named in the plan). mAlexNet was proposed as a third baseline and I rejected it. Image difference waits for my videos, since it needs a fixed camera and an empty reference frame. Metrics: F1, recall, precision, false positive rate and accuracy for "occupied", with confidence intervals and 3 seeds for the CNN. Validation data alone is used for model choice, settings and thresholds; all test sets stay untouched until the final comparison. Vertical flips are never used; horizontal flips only if a validation experiment supports them.
- **Outcome:** Done; results are in the next entry.
- **Next:** See next entry.

### 2026-11-07 | OccupancyCNN on public data: training choices and final comparison

- **Decision / reason:** Small CNN (about 294k parameters, far under the 50M limit) trained from scratch on the 40k balanced crops. Tested learning rate, augmentation (none / brightness-contrast-blur-shift / plus horizontal flips), regularization and input size (64 vs 96 px) on validation, one setting at a time. A new option had to beat the current one by more than 0.002 val F1.
- **Outcome:** The starting settings were kept (lr 0.001, brightness/contrast/blur/shift augmentation, light regularization, 64 px). All options were within about 0.003 val F1 of each other, so the CNN is not sensitive to these choices here; the differences are inconclusive. Horizontal flips did not help, so they are not used. 96 px took 2.3× longer with no gain, so 64 px stays. On the test sets (3 seeds), the CNN beats both baselines: F1 0.993 on same cameras, 0.988 on the unseen camera, 0.929 on the unseen site (HOG baseline: 0.946, 0.965, 0.854). Two lessons. (1) The baselines lost much more than the CNN between validation and test, mainly through false alarms; a threshold tuned on one class mix transfers poorly. (2) The unseen site is the clear weak point (about 8% false alarms), which supports the need for local video data.
- **Next:** I accepted this on 2026-11-07. Later: calibration, cost-based thresholds and robustness, then adapt and test on my videos.

### 2026-11-07 | Videos later; folder layout for submission

- **Decision / reason:** I will record videos (not photos) soon. Videos are needed for arrival timing, false-alert and missed-arrival metrics, and realistic night tests; photos would only help CNN training. Until then we work on parts that do not need them, starting with plate reading. The project was reorganized for submission: one folder per component (occupancy now, plates next) used the same way in `src/`, `tests/`, `outputs/`, `experiments/` and `checkpoints/`; planning documents in `docs/planning/`; datasets in `data/raw/` (untouched downloads) and `data/processed/` (built by our code); a data card in `docs/data_card.md`.
- **Outcome:** Worked. After the move, all data and result files were rebuilt and are identical to before; tests and lint pass.
- **Next:** Keep this layout for every new component. Next: audit the AddingUAE plate data.

### 2026-11-07 | AddingUAE plate data audit

- **Decision / reason:** Audit the plate data before fine-tuning YOLO11n, because its quality, leakage and coverage decide what results we can trust.
- **Outcome:** Mostly good data with fixable problems. File names carry the main plate's text, which gave a free label check: about 98% of named car photos match their labels exactly. Problems: the export's random split leaks 118 plate identities across splits; 359 plate-only images lack a `plate` box (training on them would teach the model to ignore visible plates); some photos are mock-ups with edited plates; Dubai dominates and new-style Sharjah plates are missing. YOLO11n (about 2.6M parameters) installs and runs on Python 3.14 (ultralytics, AGPL-3.0 license).
- **Next:** Superseded: the 4,500-image plan was replaced by the 7,000-image plan in the next entry.

### 2026-11-07 | Plate subset, split and fine-tuning budget (agreed)

- **Decision / reason:** My videos will focus on cars entering and leaving the two bays and will show only 2–3 different plates. That is far too few to teach plate reading, so YOLO11n will **not** be fine-tuned on video frames; those frames are only a real-site check (is the plate readable from the camera spot, and are my plates read correctly). This supersedes the earlier note that video plate images would be used for fine-tuning. The large reserve kept for video plates is no longer needed, so the plate set grows from 4,500 to **7,000 images: 5,000 train, 1,000 validation, 1,000 test**, leaving about 3,000 of the 10,000 cap in reserve (local occupancy crops if the professor counts them, test frames, safety margin).
- **Rules:** Car photos only (no plate-only or close-up images). Images whose labels exactly match the file name (verified), except that unverified RAK and UAQ car photos may be added to train only after a visual check, because so few are verified. Split by plate identity and image similarity, so the same plate or near-identical photos (including mock-ups) never cross splits. Include all plates from the smaller emirates and every image with X, Y or Z. Count every image (train, validation and test) in the ledger. A 2,500 vs 5,000 training-size comparison will serve as the quality-vs-cost study.
- **Outcome:** I approved this on 2026-11-07. Known gaps: new-style Sharjah plates are absent and UAQ is too small to test reliably; both go to `NEEDS_REVIEW` and are reported as limits.
- **Next:** Built the same day (`just prepare-plates`): exactly 5,000 / 1,000 / 1,000, no leakage, same result on every run. 95 of 114 unverified RAK / UAQ photos passed the visual check (19 rejected for wrong or incomplete characters, unclear plates, or a wrong emirate type). Because val and test keep each emirate's share, RAK has only 10 val and 10 test images and UAQ only 1 each, so their results will be indicative only. Pending my review before fine-tuning.

### 2026-11-07 | Umm Al Quwain and unknown-emirate plates go straight to human review

- **Decision / reason:** I decided that Umm Al Quwain plates (37 images) and plates with no emirate box (44 images) are too few to train or test on. They are removed from the plate subset, and the product will send them straight to `NEEDS_REVIEW`.
- **Outcome:** Done. The 81 freed places were refilled to keep 7,000 images (5,000 / 1,000 / 1,000). Every verified image from the other smaller emirates was already included, so the refill came from verified Dubai photos. No leakage; tests pass.
- **Next:** Superseded: the Dubai refill was replaced by checked non-Dubai photos (next entry).

### 2026-11-07 | Refill the 81 places with checked non-Dubai photos

- **Decision / reason:** Dubai already dominates, so I want the 81 freed places used for the smaller emirates, especially Ajman and Ras Al Khaimah. A check of all non-Dubai images left out found no more RAK car photos (only 29 plate close-ups, which break the car-photos-only rule). 86 unverified Ajman and Fujairah car photos were checked by eye: 72 approved (32 Ajman, 40 Fujairah), 14 rejected for wrong or extra digits, a missing code letter, a sideways photo, or unreadable plates. The last 9 places come from checked Sharjah photos. All of these go to train only, as agreed for unverified photos, so val and test keep only verified labels.
- **Outcome:** I approved this on 2026-11-07. Ajman train grows from 85 to about 117. Most new Fujairah photos are taxi plates from one fleet: a useful plate style, but little car variety.
- **Next:** Done the same day. A random sample of 16 Sharjah photos was checked (11 approved, first 9 used; 5 rejected). The split was rebuilt: still 7,000 (5,000 / 1,000 / 1,000), no leakage; train now has Ajman 117, Fujairah 273, Sharjah 278 and Dubai 3,563. Next: my approval of the fine-tuning plan.

### 2026-11-07 | YOLO11n fine-tuning plan

- **Plan:** Fine-tune pretrained YOLO11n (Ultralytics, about 2.6M parameters, pretrained on COCO, AGPL-3.0) to find the plate, each character and the emirate type in one pass. 48 classes (`plate`, 36 characters, 11 emirate types; the plan first said 49, a counting slip; `exp` and UAQ types removed). A fixed-rule assembler reads the characters in order and checks the format; UAQ, a missing emirate or an invalid format go to `NEEDS_REVIEW`. Primary metric: full-plate exact match; also character error rate, plate detection recall and precision, mAP, per-emirate accuracy and review rate. Baseline: YOLO11n trained from random weights on the same data. Validation-only experiments: image size 640 vs 960, head-only vs full fine-tuning, 2,500 vs 5,000 training images. Horizontal and vertical flips off (mirrored plates never occur). Final model: 3 seeds, test opened once at the end. Expected run time: half a day to a day in the background.
- **Outcome:** I approved this on 2026-11-07. Each run trains up to 30 epochs and stops early after 10 epochs without improvement on validation.
- **Next:** Running; results in the entries below.

### 2026-11-07 | Plate model: 960 px images instead of 640 px

- **Decision / reason:** First training-choice test, on validation only: image size 640 vs 960. The car photos are large (1440×1280), and the plate characters become very small when shrunk to 640.
- **Outcome:** 960 px won clearly and is now used for all later runs. Full-plate exact match rose from 35% to 70%, and the character error rate fell from 26% to 9%. Both sizes found the plate almost every time; the gap is in reading the small characters. The cost: training takes about twice as long (about 1.8 hours per run). Even at 960, about 28% of answered plates are still misread, which is too many for a gate.
- **Next:** Continue the planned tests (head-only vs full, 2,500 vs 5,000 images, the from-scratch baseline). Idea, untested and pending my decision: a second step that crops the found plate, enlarges it and reads the characters from the crop.

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
- **Next:** My review. Ideas, untested and pending: read characters from an enlarged plate crop; send low-confidence or wrong-length reads to `NEEDS_REVIEW` (tuned on validation only); check the reads on my own videos.

### 2026-11-20 | Occupancy CNN on my own photos (pilot check)

- **Decision / reason:** Before recording videos, check whether the CNN trained only on public data works on my own photos: 8 photos (4 late afternoon, 4 night), each with two bays, covering all four empty/occupied cases. Each bay was cropped by hand to where a car sits. The photos are a check only, never used for training or thresholds.
- **Outcome:** 15 of 16 bays correct; no parked car was missed. Night: 8 of 8. Day: 7 of 8. The one error was an empty bay called occupied. Small tests on that crop point to a large shadow across the empty bay as the main cause, plus part of the neighbouring car inside the box (removing the background cars did not help). Two other empty bays were close calls because the low camera angle puts cars from other rows or bays inside the crop; cutting them out made the answer clearly "empty". Much better than feared given the very different viewpoint, but 16 crops is far too few for firm conclusions, and the day photos came from four different spots.
- **Next:** Record the planned videos from one fixed camera spot. Draw tight bay boxes that avoid neighbouring cars; consider boxes that cover the lower part of each bay. Test shadow cases on purpose. Use the local data to adapt the model and measure false alarms properly.

### 2026-11-20 | Full loop on my photos: occupancy, then plate reading

- **Decision / reason:** Same 8 photos, now with the plate model added: when the occupancy model calls a bay occupied, the fine-tuned YOLO11n reads the plate inside that bay's area. Reading from the whole photo was tried as a comparison.
- **Outcome:** 13 of 16 bays fully right. Of the 7 real plates in occupied bays, 5 were read exactly right (all 4 new-style Dubai plates in normal light, day and night). The car with no plate fitted went to review, which is correct. Three problems: (1) the new white Sharjah plate went to review because that style is missing from the training data (safe, but no answer); (2) a night plate lit by a bright plate lamp lost its letters "AA", a confident-looking wrong read with low confidence (0.25); (3) the empty bay wrongly called occupied made the plate model read a background car's plate as if it were in the bay (dangerous chain). Reading the whole photo misread all 7 plates, because shrinking a tall phone photo makes plates too small, so reading from the bay area is the right design. The first version picked the most confident plate in the bay area; it chose a tiny background plate over the real one, so it now picks the largest plate (the closest car). Plates of cars in the bay were 27–29% of the bay width; background plates were 4–9%.
- **Next:** Ideas, pending my decision and to be set on validation or video data, not on these 8 photos: send reads whose plate is too small for a car in the bay to review; send low-confidence reads to review; add new Sharjah plates to the data if possible. Retest on the videos.

### 2026-11-20 | Local photos from many car parks; bay boxes per photo

- **Decision / reason:** I have no fixed camera yet, and his two home bays would only show 2–3 cars, too few to improve or test the models. So he photographed many pairs of bays in different car parks at night, standing the same way each time: 43 photos, 86 bays (46 empty, 40 occupied). In a real deployment there is one fixed camera and a one-time setup that marks the two bays; the code then crops every frame automatically, with no person or LLM involved. For this project, each photo is treated like its own fixed camera: the cropping code is the same, only the saved box coordinates differ. One shared pair of boxes is tried first (closest to the real system); per-photo boxes only where it does not fit.
- **Outcome:** I agreed. To report: hand-drawn boxes fit each photo perfectly, so results may be a little optimistic compared with a real camera that can shift; test this later by moving the boxes slightly. If photos are used both to improve and to test the models, split them by car park or area, never at random.
- **Next:** I copy the photos to `data/raw/local_night_1/`; then draw boxes, confirm labels with me, and run the full loop.

### 2026-11-20 | Full loop on 43 night photos from public car parks

- **Decision / reason:** A larger, harder check than the 8-photo pilot: 43 night photos, 86 bays (46 empty, 40 occupied), one shared pair of bay boxes for all photos like a fixed camera. Check only, nothing trained or tuned on it. Details in `outputs/occupancy/local_night_1/findings.md`.
- **Outcome:** Much worse than the pilot. Occupancy 60 of 86 right: 20 of 46 empty bays called occupied, 6 cars missed. Plates read exactly right for 19 of 34 cars. Controlled tests point to three occupancy causes: other rows of cars and buildings in the top of the box (cutting the top 30% gives 72 of 86), yellow wheel stops in empty bays (unseen in public training data), and close-up light cars that fill the box. The main plate cause: small code letters on the newest two-row Dubai plates fall below the confidence cut-off, so doubled or single code letters get lost, plus "Z" read as "2" and a thin "1" counted several times. A confidence rule would not help (wrong and right reads have similar confidence). Plate size again separates the parked car's plate (13–29% of bay width) from background plates (4–7%). Two rules fixed in advance (plate under 10% of bay width = review; Dubai read without a code letter = review, as no Dubai training label lacks one) would cut dangerous wrong outputs from 16 to 7 without losing a correct read. The public-data models do not transfer well to this kind of site.
- **Next:** Pending my decision: add the two rules and a better merge for thin characters (check on public validation first); draw real bay boxes without background rows; adapt the occupancy CNN on local photos split by car park, with a second session as the clean test; ask the professor about the 10,000 cap for local training.

### 2026-11-20 | Plate reader: three safety fixes after the night test

- **Decision / reason:** I asked to fix the plate step first. Three rules, each tied to a failure seen on the night photos and checked on the public validation set: merge duplicate boxes for one thin character (overlapping sideways by more than half), send a Dubai read without a code letter to review (no main Dubai plate in the training or validation labels lacks one), and send a plate narrower than 10% of the bay width to review (it belongs to a car further back).
- **Outcome:** Worked. Validation: exact match 69.7% → 71.9%, misreads 28.4% → 20.2%, at the cost of about 6% more plates going to review. Night set: dangerous wrong reads 16 → 6 (no more plates read in empty bays), correct reads 19 → 20. Pilot: dangerous outputs 2 → 0. A first merge cut-off of 70% missed a triple "1"; 50% was chosen on validation, not on the night photos. The 6 remaining misreads are doubled or swapped code letters, which these rules cannot catch.
- **Next:** Rerun the public plate test set once when the plate system is final. Later: better reading of small code letters (enlarged plate crop or more examples of the newest Dubai plates). Then start Model C (typed commands) and the permit table.

### 2026-11-21 | Evidence saved for every night-set finding

- **Decision / reason:** I asked whether each finding is justified. Some numbers came from one-off checks that were never saved, and some reasons were guesses. Each one now has a saved script or table, wheel stops are marked bay by bay in the set's config, and each finding is labelled "measured" or "hypothesis".
- **Outcome:** Validation before/after and the merge cut-off choice reproduced exactly. Four numbers changed when redone properly, with the same conclusions: wheel stops (15 of 26 bays with a stop gave false alarms vs 5 of 20 without; 10 of 11 remaining false alarms have one), brightness (92 vs 91, no difference), lost code letters (on 4 of 6 plates reviewed for a missing letter, the letter was found below the cut-off; on 2 it was not found), and the Dubai count (4,302 main plates, none without a letter; 98 of 500 smaller background plates lack one, often because they are only partly labelled). Untested reasons (training data lacking wheel stops, close-up cars, the white Sharjah plate) stay marked as hypotheses.
- **Next:** No change to the plan. The configs and per-bay results with real plates stay out of Git until I decide how to hide them.

### 2026-11-21 | Model C: simple scope for my own commands (partly superseded below)

- **Decision / reason:** Model C is for my personal use, so its scope is cut to what I will actually say. I speak; speech-to-text runs before Model C (the phone's dictation for now), so Model C reads text. Two actions only: allow (adds or replaces a permit) and remove. I say only the plate number; Model B already stores the full plate, and a spoken number matches a read plate by its digits. Cars sharing a number with a different code are out of scope. Bay (1 or 2) and end time are optional; no end time means no expiry. The system asks only when the action or number is missing or something is invalid. Every change still passes Pydantic checks and my confirmation. This replaces the earlier five actions (add, edit, extend, revoke, list).
- **How candidates are compared:** each candidate only picks out the action, number, bay and time words; the same fixed rules turn those into a checked command, so the comparison measures the model alone. Generated command sets (no training): dev (60) and a frozen test set (160, a third with wording not in dev). A rule parser written from dev wording is the baseline.
- **Outcome so far:** Steps 1–3 done. A perfect extraction gets all 220 answers right, so the answer key and fixed rules agree. The rule parser gets all 60 dev commands right, as expected since it was written from them; the test set is unopened.
- **Next:** I check the test answers by eye (they were generated with AI help, and the rubric needs human-checked test labels). Optionally, I dictate 20–30 real commands on the phone as an extra check of real wording. Then test the pretrained candidates on dev. If a local speech-to-text model is added later, it is a new decision (size limit, and whether it counts as another modality).

### 2026-11-21 | Model C: final scope after my review of the test answers

- **Decision / reason:** I reviewed the 160 test commands and set final rules. Main rule: only clear commands are accepted; anything unclear returns NEEDS_REVIEW and a question, never a guess. Changes from the entry above: (1) permits are no longer tied to a bay: allow covers both of my bays, remove revokes both, and a bay said in a command is ignored (Models A and B still find bays for monitoring); (2) a one-digit plate number goes to review with the command kept, so I check and confirm it; (3) an hour without AM/PM ("until 6") is asked, never guessed; (4) a clock time already passed today, with no date, is asked instead of moved to tomorrow; (5) "until tonight", "next Monday" and vague phrases are asked; "until Monday" means the coming Monday at 23:59 (asked if today is Monday); (6) a speech-to-text slip in the action ("a loud" for "allow") is asked, not corrected; (7) other requests (questions, "edit", "open the gate") get a clear "unsupported" reply. No end time still means a permanent permit, and the confirmation now says so. Model C only proposes; I confirm every change.
- **Outcome:** Contract, shared rules, rule parser, generator and tests updated; both sets regenerated (dev 60, test 160: 95 clear commands, 55 to review, 10 unsupported). A perfect extraction still reaches all 220 answers, and the rule parser gets all 60 dev commands right (written from dev, so expected). The test set is still unopened by any parser.
- **Next:** I give the regenerated test answers a quick final look. Then Step 4 (download candidates, note size and licence) and test them on dev only.

### 2026-11-21 | Model C: candidates downloaded and set up on dev (Steps 4–5)

- **Decision / reason:** Downloaded the three planned candidates at fixed versions as local files: SmolLM2-135M, FLAN-T5-Small, and GLiNER Small v2.1 paired with MiniLM-L6 for the action. All are Apache-2.0 (GLiNER's DeBERTa tokenizer files are MIT) and under 200M parameters each (counts and speed in `outputs/commands/candidates.md`). Each got a small adapter that fills the same extraction, tuned on dev only; the test set stays closed. Worked examples were written by hand in dev wording only, so the test's new wording stays a fair check.
- **Two safety choices in the adapters:** (1) the two text generators may only copy whole words from the command, so they cannot invent a plate number or a time, and an answer they cannot finish counts as no answer (the shared rules then ask). Without this, both invented numbers, and FLAN copied part of a number ("62" from "626"). (2) GLiNER's spans are trimmed and grown to the whole spoken number, because it often finds only part of a number said digit by digit.
- **Outcome (dev, inconclusive for the final choice):** GLiNER + MiniLM is best so far (73% exact, 10% dangerous), then SmolLM2 (58%, 28%), then FLAN-T5 (17%, 15%). All are far below the rule parser (100% on dev, but it was written from dev). The common dangerous errors: a dropped end time (becomes a permanent permit), allow and remove mixed up, and a command with no action word read as allow. SmolLM2 runs about 7× faster on the Mac GPU than on CPU (0.27 s vs 2.0 s per command), so the GPU is the default. What was tried is in `outputs/commands/dev_tuning.md`.
- **Next:** I fix the selection rule and the dangerous-rate limit before the final test (Step 6). Then the one final test run for all parsers.

### 2026-11-21 | Model C: selection rule fixed before the final test

- **Decision / reason:** I agreed to this before any test result is seen. A candidate qualifies only with **0 dangerous answers on dev**. Among those, the highest exact score on dev wins. A slower model may win if it is more accurate; size and speed only break ties. The rule applies to every candidate set up on dev, including any safety gate or combination added before the final test. A wrong change put to me is the worst error, so asking a needless question is the accepted price.
- **Outcome:** Pending. No candidate meets the rule yet (best: 10% dangerous on dev). 0 of 60 on dev still allows a true rate of up to about 5%, so the final test is the real check.
- **Next:** Add safety gates tuned on dev (see the plan given to me), then run the final test once.

### 2026-11-21 | Model C: a safe combination meets the rule on dev

- **Decision / reason:** To reach 0 dangerous answers on dev, three safety ideas were tried on dev only. (1) Each model's own confidence: rejected, because wrong answers were often as confident as right ones (the same lesson as the plate reader). (2) A second opinion: GLiNER + MiniLM gives the answer, and a change goes to me only if SmolLM2, reading the command on its own, reaches exactly the same change; otherwise the system says it is unsure and asks. Checking only the action and number was not enough (one dangerous answer). (3) A dropped end time turns into a permanent permit, so an allow with no end time is also asked about when GLiNER half-saw an end time. Its cut-off was set one step stricter than the minimum needed, to leave a margin.
- **Outcome:** The combination (`checked`) is the only option with 0 dangerous on dev, so it wins under the agreed rule: 60% exact, but 18 of 34 clear commands get a needless question. That is the price of safety, and I still confirms every change. Weak points: both models read a command with no action word as "allow", and one such case was stopped only because they disagreed on the time. 0 of 60 still allows a true rate of up to about 5%. About 0.15 s per command on the Mac GPU; the two models together have about 310M parameters, each under 200M.
- **Next:** One final test run (`--final`) for the rule baseline, the three candidates and `checked`; report the slices. Later (Step 8): a "reject, then fix the fields" confirmation screen that saves each accept or reject as a feedback record.

### 2026-11-22 | Model C: test answers checked by me

- **Decision / reason:** The rubric needs human-checked test labels. I reviewed the regenerated `test_review.md` (160 commands) and approved it with no changes.
- **Outcome:** The frozen test answers are final. The test set is still unopened by any parser.
- **Next:** Improve the safe combination on dev, build the robustness sets, then run the final test once.

### 2026-11-22 | Model C: improved for safety, then the one final test

- **Decision / reason:** I asked for the best model with 0 dangerous answers, within 2 hours. On dev only, plus extra command sets in dev wording: better MiniLM examples ("bay two" appeared only in a remove example and made both models read "add ... bay two" as remove), a lower GLiNER cut-off, SmolLM2 checks only the action and number, my fixed form read first by fixed rules, and two new checks: a change needs a word close in meaning to an action word, and every number in the command must be explained. Each fresh "confirm" set found a new rare failure (no action word, a question read as allow, a missed second car), so four were used in turn; the fourth, sealed until the design was final, gave 0 dangerous. Cut-offs: the gap midpoint for the action word, after "one grid step stricter" proved too small a margin.
- **Outcome (final test, run once):** Model C (`tiered`) put 1 wrong change to me out of 160 (0.6%, a negation: "don't allow car 28 anymore"), against 3 for the rule parser and 15 for GLiNER + MiniLM alone. The price is coverage: 50% exact, and only 38% of clear commands get the change without a question; commands in new wording are almost always asked about. GLiNER + MiniLM alone is the most accurate (73%) but unsafe (9.4% dangerous). Robustness (5 levels): typos make Model C ask much more (42% exact); missing pieces, ambiguity, off-topic and tricks are handled safely, with 2 rare failures. Details: `outputs/commands/final_test.md`, `robustness.md`, `dev_tuning.md`.
- **Next:** Connect Model C to the permit table with my confirmation (Step 8). For the report: safety bought with coverage, and the action-word check is the main cost on new wording.

### 2026-11-22 | My decisions before the full-loop tests

- **Decision / reason:** I chose to **keep real plates local only**. Local configs and plate-level results are now ignored by Git (`configs/local_*.yaml`, `outputs/loop/local/`, local occupancy results); shared reports show counts only. I gave the cars on the permanent list (stored only in `configs/local_loop.yaml`) and confirmed the uncertain code letter on IMG_1838. The professor accepts visual + text + tabular as three modalities. The 10,000-item cap has about 3,000 items to spare, so local photos fit even if counted. Model C work was merged into `main` (not pushed). My commands for testing are generated in my own (dev) wording, which I said matches how I speak.
- **Outcome:** Unblocked the full-loop tests (steps 1–3).
- **Next:** Steps 4–5 (remove one model at a time; time per stage and a folder command) and the night video.

### 2026-11-22 | Full loop: the three models together on my photos

- **Decision / reason:** Joined the models into one flow (`smart_parking.loop`): Model A says if a bay is occupied, Model B reads the plate in that bay, and the permit table (filled by Model C from my generated commands, each given simulated confirmation) is checked at the photo's time. Tested three ways: joining rules with stand-ins (unit tests), a step-by-step story on real photos, and every bay of the local photo sets (51 photos, 102 bays) against the truth. The photos stay check-only: nothing was tuned on them.
- **Outcome:** The story worked: the same visitor's car went from "potentially unauthorized" to "authorized" after a command, then back after the permit ended or was removed. In the measured run, 64% of bays got the right final answer, with **0 false alerts** and **0 unauthorized cars let through as authorized**. The cost is in occupancy: 21 empty bays were called occupied (sent to a person, mostly at night) and 6 parked cars were missed (5 of them unauthorized). The plate step sent 10 cars to a person, 7 because a Dubai code letter was missing. Of 33 commands, Model C got 24 right, asked about 8, and proposed 1 wrong end time ("until tomorrow nine thirty p.m." became today: both of its models cut "tomorrow" out of the time). My check caught it; without the check, 2 bays would have had false alerts.
- **Next:** Occupancy at night is the weakest stage; the night video and local adaptation are the main fixes. (The Model C time failure is handled in the next entry.)

### 2026-11-22 | Model C: a day said must be in the time read (change after the final test)

- **Decision / reason:** With my OK, Model C now asks again when the command says a day word (today, tonight, tomorrow, a weekday) that the time it read leaves out. This fixes the full-loop failure in which "tomorrow" was dropped. Because the final test was already used, the change was checked on dev sets only, the test was not run again, and the change is disclosed in `outputs/commands/final_test.md`.
- **Outcome:** Worked at no cost. Model C's scores on dev, check and confirm–confirm4 are unchanged (0 dangerous on all six). It also fixes one of the two known robustness failures (a typo command that lost "tomorrow"). In the full loop, that command is now asked about instead of being proposed wrong: 0 wrong proposals out of 33. While rerunning robustness, a reproducibility bug was found and fixed: the robustness set changed on every rebuild, because it avoided plate numbers from its own previous output. It now rebuilds identical to the saved set. The confirm reports saved in Git were from older designs; they have been refreshed.
- **Next:** Keep. The reported final-test numbers describe the version that was tested.

### 2026-11-22 | Full loop: what each part adds (remove one at a time)

- **Decision / reason:** To show each modality earns its place, the full loop was rerun on the same 102 local bays with one part removed at a time (`just full-loop-ablation` → `outputs/loop/ablation.md`).
- **Outcome:** Without Model A, every empty bay goes to a person (right answers 64% → 35%). Without Model B, no car can be identified (33%). Without the time check, 6 unauthorized cars are let through as authorized. Without any commands, 8 false alerts. With my check, Model C never causes a wrong answer; without it, 2 false alerts. **Surprise:** on these generated commands the plain rule parser did better than Model C (33 of 33 right, no questions, against Model C's 24 right and 9 questions). The commands use the same dev wording the rule parser was written from, so this favours it; on the test's new wording, the rule parser made 3 wrong proposals against Model C's 1. Reported as found.
- **Next:** In the report, present this as a trade: the rule parser is best on my own wording, and Model C is safer on new wording.

### 2026-11-22 | Night video and the folder command (step 5)

- **Decision / reason:** I recorded 10 minutes at night from a fixed spot; both of my cars arrive and leave several times. Claude marked the truth from frames; moving periods are not scored. Twice the BMW stands across both bays, so it counts as parked in both. I checked the truth list by hand and found it accurate, with no changes. The same per-frame code now serves a folder command for new inputs (photos, videos, typed commands) and times each stage.
- **Outcome (truth checked by me):** 0 false alerts on my cars in scored frames, and no parked car was missed. Plates were read right in 83% of normal frames. The weak point is again empty bays at night called occupied (78 of 243 checks), which go to a person, never to an alert. Single-frame false alerts appear while a car is moving (4 short episodes). Time: about 0.1 s per frame and about 0.1 s per command on the Mac GPU; about 10 s to load; about 2.2 GB of memory.
- **Next:** Per-stay logic (next entry). Idea, not yet tested: alert only when the same answer holds for a few seconds (the length to be fixed before looking at results, never tuned on this video).

### 2026-11-22 | Per-stay logic for video: rule fixed before running it

- **Decision / reason:** With video input, judging each frame alone gives a flickering answer (46 changes in 10 minutes in one bay) and one-frame false alerts while a car moves. I want one decision per car's stay. The rule below was **fixed and written here before it was run**, because the night video has already been seen. Its numbers come from reasoning, not from the video:
  - a bay changes between empty and occupied only after **5 frames in a row (10 s at one frame every 2 s)** agree, because a car needs several seconds to park or leave;
  - the stay's plate is the read that appears most often among the stay's clear reads (READ, not NEEDS_REVIEW), counting from the first frame of the arrival. It must appear **at least twice and in more than half of the clear reads**; otherwise the stay goes to a person. Two reads guard against a single misread;
  - the permit check is redone at every frame's time, so a permit that ends during a stay turns into an alert;
  - each change of a bay's answer counts as one notification to me.
- **Outcome (seen check, rule unchanged after running):** It worked on the main points. False alerts on my cars fell from 4 frames to 0, notifications fell from 78 to 29 over 10 minutes, and every real stay was found with the right answer at its end. The exception is the bay without the plate when the BMW stood across both bays, which goes to a person. Still weak: 5 "phantom" stays (a person standing in a bay, a car pulling up close and turning away), and empty bays at night called occupied (67 of 243 checks), so most remaining notifications are "please look" requests. With only a few reads early in a stay, the plate rule can flip once or twice before settling. The folder command now uses per-stay answers for videos (`outputs/loop/video_night_1_stays.md`).
- **Next:** A fresh video recorded later, not looked at first, is the clean test. The biggest remaining gain is night occupancy (adapting Model A on local photos, open item).

### 2026-11-25 | Last recording: night video 2 and the data split

- **Decision / reason:** I made the last recording: about 43 minutes on the night of 2026-11-24, from a fixed spot (phone on a stick), in 5 files that follow the checklist closely. Daytime recording is not possible (the site is too crowded), so local work is night only; daytime evidence comes from public data and 4 local day photos. Claude marked every arrival, departure, person and passing car; I checked the list and made 3 corrections (`configs/local_video_night_2.yaml`, local only). The waiting car counts as occupied, and a car across both bays counts in both. The camera did not move between files, but the view is closer than in video 1, so new bay boxes were drawn once from a frame with both cars parked.
- **Split (fixed before any training):** blocks 1–3 train Model A; block 4 chooses its settings; the first night video (a different night) is the final test, run once. Local photos and the public test set are extra checks that adapting did not break other car parks or daytime.
- **Next:** Write the adaptation plan here before training, then adapt Model A.

### 2026-11-25 | Model A adaptation plan (fixed before training)

- **Data:** bay crops (64 px, the same cut as the product) from night video 2, one frame every 2 s, moving periods left out, labels from truth I checked. Blocks 1–3 train; block 4 chooses. Hard cases are kept (a person in an empty bay = empty; the waiting car, the car across both bays and the crooked car = occupied). The first video is the final test, used once at the end.
- **Options:** (a) no training, only a new threshold chosen on block 4; (b) fine-tune the last conv block and the head; (c) fine-tune the whole model at a low learning rate (1e-4 and 3e-4 tried); (d) a wider CNN (channels 32-64-128-256, about 1.2M parameters, under the 50M limit) trained from scratch on public + local crops. Options b-d mix equal numbers of public and local crops in every epoch, so the model does not forget the public data. Each option is trained with seeds 42, 43, 44; the deployed model is the majority vote of the 3 seeds, as before.
- **Choosing (block 4 only):** for each run, the best epoch and the threshold are those with the best balanced accuracy (the average of the right rate on empty and on occupied bays) on block 4. The winning option has the best majority-vote balanced accuracy on block 4, provided that (1) it misses no more parked cars than the current model on block 4, and (2) its public validation F1 is at most 1 point below the current model's. Ties go to the smaller, simpler option (a, then b, c, d).
- **Final tests (once, results accepted):** the first video (frame by frame, then the full system per stay), the public test sets, and the local photos, each before and after.
- **Outcome (chosen on block 4, tested once):** Option b (fine-tune the last block, about 3 s per seed) won under the rule. Several options reached 100% on block 4 but forgot the public data (the 1-point limit caught them); b passed that limit only just. Final test on the first video (another night): in normal frames, empty bays called occupied fell from 78 to 2 with 0 parked cars missed (balanced accuracy 84% → 99.6%). But when the car stood across both bays, the bay holding only half of it was called empty 50 times (the old model got these right only because it called nearly everything occupied). The price is general skill: public test F1 0.994 → 0.988, unseen public site 0.932 → 0.857, and on other car parks' night photos more missed cars (6 → 16) but fewer false alarms (20 → 5). Full system on the first video: answers right on my cars 69% → 84% (98% in normal frames), notifications per stay 29 → 13, phantom stays 5 → 1, still 0 false alerts.
- **Decision:** The product uses the adapted model (`occupancy.deploy: adapted`), because the product is my fixed camera. The public-only model stays as the general model and as the baseline. Item count, counted conservatively: about 2,700 local crops (train, block 4 and the test video), so the project stays under the 10,000-item cap even if scratch-model data is counted.
- **Next:** Trust checks, the app, `just evaluate`, README and the report.

### 2026-11-25 | Plate reader: the one test rerun with the safety rules

- **Decision / reason:** The three plate safety rules were added after the plate reader's first test, so the public plate test was rerun once with the final system, as planned. The first result is kept in `outputs/plates/final_results_before_safety_rules.md`.
- **Outcome:** Safer and slightly more accurate: exact full-plate reads 70.6% → 72.8%, wrong reads 27.5% → 19.2%. The price is coverage: 98% → 92% of plates are answered; the rest go to a person.
- **Next:** Final. Never rerun.

### 2026-11-25 | Privacy lifted; project change explained (confirmed by me 2026-11-26)

- **Decision / reason:** I consider all captured data public (plates and faces included), so local photos, videos, their truth labels and plate-level results may go in the demo, the repository and the report. This supersedes the 2026-11-22 "keep plates local" decision. I also confirmed that the project was changed after the intermediate submission, with the professor's agreement, because the earlier project could not continue; the report says so and judges results against this project's own plan, not the old proposal.
- **Next:** Remove the privacy-only Git ignores, add sample inputs for the demo, and make the local results reproducible (large videos cannot go in Git; derived data or a download link is needed).

### 2026-11-25 | Trust checks, product hardening, demo and report

**Audit correction (2026-11-26):** the claims below that every report artifact is regenerated and that the local system has an untouched final test are superseded by the submission audit. Historical results are retained.

- **Decision / reason:** Finished the remaining rubric work on branch `trust-checks`. Each choice was made on validation (block 4, or public validation), with three choices informed by the test, each disclosed in its report: (1) Model A keeps its raw probability, because Platt scaling fitted on block 4 worsened calibration on the test night (ECE 0.065 vs 0.112), while Model B uses Platt scaling (0.139 → 0.036); (2) the feature-distance unfamiliar-input check is not used, because it flagged 13% of normal frames on the other night; (3) plate caching was adopted after the efficiency study measured it on the test night.
- **Cost model:** false alert 5, missed unauthorized car 10, review 1, with 70% of cars allowed. Model A's threshold became 0.86 (stable under every cost assumption). The plate gate was first chosen on public plates (0.7), but it sent 30% of my bays to a person, so it was re-chosen on block 4 (0.15).
- **Fixes found by the checks:** the sharpness check first flagged every frame 40% darker than usual, so it now uses a contrast-normalised frame. A probe found that covering a plate's last character gives a silent shorter read 58% of the time (not fixed: next step is a rule on how much of the plate width the characters span).
- **Product:**
  - camera check (blocked, unfamiliar view, blurred) before any model;
  - Pydantic output records with reason, guidance and evidence frames;
  - bad inputs returned as records, never a crash;
  - a folder without `bays.yaml` means my camera (adapted model); a folder with it means a new camera (public-data model);
  - plate caching after 3 matching reads (model time 38% of before);
  - Streamlit demo (`just demo`) with accept, reject or fix feedback.
- **Outcome:** On the test night, per stay: 85% of bay checks right, 0 false alerts, 13 notifications in 10 minutes, all four normal stays right. `just evaluate` regenerates every report table. Model C's frozen-test numbers replay exactly with `--as-tested`. A clean clone installs, passes 134 tests and runs the demo. The final report is `docs/final_report.md` (about 2,400 words).
- **Next:** Host the raw local videos and photos (about 6.5 GB, too big for Git) so `just evaluate` can be reproduced fully; merge and push when I say.

### 2026-11-26 | Submission audit: evidence boundary and safe fixes

- **Decision / reason:** Audit the saved evidence and use synthetic inputs for behavior checks; do not run frozen-test inference, retrain, choose settings or use `--final`. Keep larger changes for my approval.
- **Outcome:** The clean demo works and model/data limits pass. Full reproduction is incomplete, and earlier system choices used the seen test night. A synthetic blocked video loses its review warning in the displayed stay result. Small fixes cover missing terminal confirmation, folder quoting, logging, dependency declarations and inaccurate report claims. Details and all rubric checks are in `docs/submission_audit.md`.
- **Next:** My approval is needed for shared video logic, input validation, safe replay/data packaging and a genuinely fresh evaluation. Existing scores remain historical; no new performance result is claimed.

### 2026-11-26 | Privacy restored for submission work (superseded the same day: data stays public)

- **Decision / reason:** My instruction at the time keeps real plates and local photos private, superseding the earlier permission to publish them.
- **Outcome:** Current documentation and ignore rules now reflect that instruction. Private artifacts are already tracked, so ignore rules alone do not make the repository shareable. Nothing was committed, pushed, uploaded or removed from history.
- **Next:** Prepare an sanitized submission package I approve before sharing; keep original private evidence local.

### 2026-11-26 | Review of the Codex audit: data public, one sealed test video

- **Decision / reason:** An independent review of the Codex audit found that its "privacy restored" entry came from an outdated rule copied into the audit prompt, not from me. I confirmed that all plates, photos and videos are public, so the 2026-11-25 decision stands and the privacy edits were undone. The review also confirmed that night video 1 was looked at and used for three choices (Model A's confidence, the feature-distance check, plate caching), so it can no longer be a clean test.
- **New split:** public data unchanged. Night 2 blocks 1-3 train, block 4 chooses every local setting (including the three choices above, redone on block 4 only). Night 1 becomes a seen cross-night check. I will record **one new night video (at most 20 minutes, `docs/planning/test_video_checklist.md`)** as the only final system test: truth marked and checked before any model sees it, settings frozen and committed first, run once.
- **Next:** Fix the video safety bug (a blocked camera lost its review status), input checks and the evaluate recipe before the new video; then freeze and test once. Results pending.

### 2026-11-26 | Rules for redoing the three test-informed choices on block 4 (fixed before running)

- **Decision / reason:** The three choices once informed by night video 1 are made again on block 4 (validation) only, with these rules written down before any block-4 result is seen. Block 4 is split by time into a first and a second half; each rule uses one half to fit and the other to check, both ways.
- **Model A confidence:** use Platt scaling only if its mean held-out ECE is lower than the raw probability's on the same halves; otherwise (or a tie) keep the raw probability.
- **Feature-distance bay check:** use it only if its held-out false-alarm rate is at most 2% **and** it catches at least 5% of corrupted block-4 frames (blur, over-exposure, noise, moved camera, covered lens) that the blocked, view and sharpness checks miss.
- **Plate caching:** replay block 4 with and without caching; keep caching only if it answers at least as many stay ends right, per-stay answers on scored frames stay within 1 percentage point, and Model B runs fewer times.
- **Next:** Run `just validation-choices` and `just efficiency` on block 4, apply what the rules say, and record the outcome here.
- **Change before any result (same day):** the time halves failed at once: the second half of block 4 has only parked cars, so Platt scaling cannot be fitted on it. No score had been seen. Both checks now use two folds of alternating 60-second blocks instead of halves; the rules are otherwise unchanged.
- **Outcome:** All three rules give the same choice as before, now backed by block 4 alone: Model A keeps its raw probability (held-out ECE 0.011 raw vs 0.023 Platt); the bay check stays off (2.6% held-out false alarms, above the 2% limit, although it would catch about 13% of corrupted frames the other checks miss); plate caching stays (same stay answers, Model B time cut to about 13%). Details: `outputs/trust/validation_choices.md`, `outputs/trust/efficiency.md`. Night 1 is now only a seen check.

### 2026-11-26 | Fixes before the sealed test: video safety, input checks, read-only evaluate

- **Decision / reason:** Fixed the problems the audit review confirmed, before the new test video, so the test runs on the final design.
- **Video safety:** a frame the camera check refuses is now "unknown": it neither confirms nor ends a stay, and the bay shows NEEDS_REVIEW with the reason until the view is usable. Cached plate reads no longer count as new votes. One shared step now serves the CLI, the demo, the replays and the efficiency study (they disagreed before). Re-run on night 1 (seen check): per-stay answers 85% → 83%, notifications 13 → 28, because camera-check reviews that the old replay hid now reach I.
- **Input checks:** a bad `--every`, non-UTF-8 commands, an empty or broken `bays.yaml`, a missing snapshot and an empty or missing folder now return structured problems and always write `result.json`; a broken camera set-up never judges photos with my boxes. The demo validates my fixes.
- **Reproduction:** `just evaluate` is read-only: it rebuilds the training-choice and adaptation tables from logged runs and stops if calibration, thresholds or the camera check would change (only `just refit` stores them). Latency is now measured by a recipe (`just latency`): 21 ms per frame on average, 113 ms per command, 5 s to load, 2.6 GB.
- **Next:** Record the sealed test video; freeze and commit; mark truth before any model sees it; run once. Host the raw data and add the link.

### 2026-11-27 | Final test on night video 3: rules fixed before the run

- **What happened:** I recorded night video 3 alone (24 minutes, same spot as night 2) for the test only; it sits in `data/raw/video_test/`. Claude marked its truth from frames every 10 s and 2 s before any model saw it (`configs/local_video_night_3.yaml`). The commands file follows the checklist exactly (BMW always; Tesla until 9 minutes after the start, rounded down to 00:14; one off-topic line), not chosen after seeing the events. Bay boxes were drawn once from a frame with both cars parked, and the camera snapshot is the frame at 0:10, as on the earlier nights.
- **Rules (fixed now):** `just final-test` runs once and refuses to run again; it needs my truth check first. Model C reads the commands and its proposals are accepted as proposed, so its mistakes reach the bays. **Primary measure:** of the true stays of at least 30 s, the share whose answer at the stay's last parked frame is right. Secondary measures: stays under 30 s, plate found per stay, per-frame occupancy and plate reads, lens-blocked frames sent to a person, false alerts on allowed cars, stays seen with no car, notifications, commands understood. A car over the middle line counts in both bays; a lens blocked by a person must give NEEDS_REVIEW.
- **Night 3 also replaces night 1** as the test for Model A's adaptation, calibration, costs and the camera check (scored with the frozen models, nothing chosen). Monitoring and image robustness stay on night 1 (demonstrations, not tests). Fine-tuning items now count only what a model learned from or was chosen on (8,204 of 10,000); test items are listed apart.
- **My check and freeze:** I checked the truth on 2026-11-27 with no changes. Frozen before the run: commit 1a48211 plus the working tree (SHA-256 of src, configs, Justfile, pyproject and uv.lock: 6eb99bd16276f47f; deployed weights: c028975ff6848ff2). Not committed, on my time limit.
- **Outcome (run once, 2026-11-27):** 5 of 9 stays of 30 s or more answered right; the 22 s stay right too. Every normal stay was right (both my cars, the Tesla after its permit ended, the crooked Tesla, a person in front of a plate or in an empty bay, the lens blocked: 20 of 20 frames to a person). All four wrong stays are the two cars across both bays: the BMW went to NEEDS_REVIEW (safe), but the Tesla over the middle line was called EMPTY in both bays, so one car without a valid permit was missed. No false alert on an allowed car, no stay seen with no car there, 20 notifications in 24 minutes, Model C got all 3 commands right (the off-topic line got a question, not a refusal). `outputs/final_test/night_3.md`.
- **What it means:** the known weakness (a car across both bays) is the one that fails, and it can now fail unsafely (a miss), not only by review. Not fixed after the test: fixing it now would tune on the test. Next fix, untested: treat "one car over both bays" as its own event.
- **Other test-night findings (scored with frozen models, nothing chosen):** Model A on normal frames 0.999 balanced accuracy (public model 0.961), but across the whole night the adapted model costs more than the public one because of the cars across both bays. The camera check caught only 3% of simulated shifted-and-zoomed frames (98% on night 1), so a knocked camera is not reliably caught; blur, a covered lens and noise were all caught. The explainability probes now run on night 3 and partly support the half-car hypothesis (greying the left half of a car crop leaves 48% called occupied).

### 2026-11-27 | Fixes from the final Codex review (after the test)

- **Decision / reason:** A second review found real gaps; all were fixed without changing the test result. The night-3 start time is now pinned in its config, because a copied video can change its file time (a day's shift turned 5/9 into 4/9 on the same predictions). Commands typed during a video now apply from the next frame (before, only after the whole video); the final test was unaffected (its commands come before the video, and the one during it is off-topic). The 13 weight files `just evaluate` needs are now in Git. Evaluation stops if a fitted file is missing instead of creating it. The cost table now scores the real product rule (mean probability at 0.86), not the seeds' vote. Report timings are given as approximate, since they vary between runs.
- **Outcome:** `just final-test --report` gives the same report; tests pass.
- **Next:** Host the raw data and add the link; prepare the submission package.

## Decision log

For each **meaningful** new decision, add one short entry:

### YYYY-MM-DD | Decision title

- **Decision / reason:** What we chose or tested, and why.
- **Outcome:** Worked, failed, or inconclusive. Explain the practical lesson.
- **Next:** Keep, change, reject, or retest.

### 2026-11-27 | First-person submission narrative

- **Decision / reason:** I describe the parking problem, my work, and my decisions in my own voice across the authored project documents. The report opens directly with the problem; reproduction guidance belongs in the README.
- **Outcome:** I changed wording only. Saved measurements, model settings, code behavior, and historical result artifacts are unchanged.
- **Next:** Keep future submission writing in the same voice and preserve generated evidence as reproducible records.
