# Data Card

I keep `data/` outside Git. This card explains where each dataset comes from, where I put it, and how I use it.

## Layout

| Path | Contents |
|---|---|
| `data/raw/cnrpark/` | CNRPark+EXT download (patch zips, CSV, official splits) |
| `data/raw/adding_uae/` | AddingUAE plate dataset (YOLO format) |
| `data/raw/video_night_1/`, `video_night_2/`, `video_test/` | My recordings of the two bays |
| `data/processed/occupancy/` | Built by `just prepare-data`: manifest, dataset with splits, image cache |
| `data/processed/plates/` | Built by `just audit-plates` and `just prepare-plates`: box tables, YOLO folders for the subset |

## 1. CNRPark+EXT (occupancy model, trained from scratch)

- **Source:** http://cnrpark.it/ (files: `CNR-EXT-Patches-150x150.zip`, `CNRPark-Patches-150x150.zip`, `CNRPark+EXT.csv`, `splits.zip`). Unzip into `data/raw/cnrpark/`.
- **Citation:** G. Amato, F. Carrara, F. Falchi, C. Gennaro, C. Meghini, C. Vairo, "Deep learning for decentralized parking lot occupancy detection", *Expert Systems with Applications*, 2017. G. Amato et al., "Car parking occupancy detection using smart camera networks and deep learning", *IEEE ISCC*, 2016.
- **License:** Open Data Commons Open Database License (ODbL) v1.0, as listed for the [official dataset](https://cnrpark.it/).
- **Contents:** 157,549 labelled crops of single parking spaces (free / busy) from 11 cameras: CNR-EXT (9 cameras, Nov 2015 – Feb 2016) and CNRPark A/B (July 2015). Captured 07:00–18:00; almost no night images.
- **Cleaning:** 39 blank images, 26 crops whose CSV label disagrees with the official label file, and 704 crops too dark to check by eye are excluded. 37,062 near-copies (same bay looking the same as its last kept snapshot) are removed.
- **Splits:** I held out camera C02 and the CNRPark A/B site completely (unseen camera and unseen site tests). I split the other 8 cameras by the official day lists, so no day is shared. Train is balanced to 20,000 free + 20,000 busy, spread over cameras; validation and test keep their natural class mix. Full counts: `outputs/occupancy/data/data_report.md`.
- **Fine-tuning cap:** not counted. This data trains a model from random initialization.

## 2. AddingUAE (plate reading, fine-tuning YOLO11n)

- **Source:** https://universe.roboflow.com/addinguae/uae-zcfqj (Roboflow export "UAE v1", YOLOv11 format). Unzip into `data/raw/adding_uae/`.
- **License:** CC BY 4.0 (from the Roboflow page).
- **Contents (from the dataset page):** about 10,000 images; 51 classes: `plate`, digits 0–9, letters A–Z, `exp`, and new/old plate types for the seven emirates. The downloaded export is split 70/20/10 at random: 6,990 train, 1,997 validation, 998 test images.
- **Audit (`just audit-plates`, report in `outputs/plates/data/audit_report.md`):** 86,294 boxes, no exact duplicate images, no augmentation. File names usually carry the main plate's text (e.g. `K-67810`); among plate-style names, 8,619 labels match the name exactly, 185 partly (about half label mistakes, a quarter name mistakes, the rest hidden or cut-off plates). 359 plate-only images have character boxes but no `plate` box. 184 images are plate close-ups. Some car photos are mock-ups (the same car with different plates edited in). Plate types are mostly Dubai (old 5,036, new 2,840); new-style Sharjah plates are missing. Rare classes: Y (15), Z (7), `exp` (3).
- **Leakage in the export split:** 118 plate identities (254 images) appear in more than one split, and 42 near-identical car photos cross splits. A re-split by plate identity and image similarity is needed.
- **Fine-tuning subset (`just prepare-plates`):** I re-split 7,000 car photos into 5,000 train / 1,000 val / 1,000 test (the export's split is not used). 6,852 are verified (labels exactly match the file name). I checked 148 unverified car photos by eye and added them to train only: 67 RAK, 32 Ajman, 40 Fujairah and 9 Sharjah; I rejected 38. Decisions and reasons: `configs/plates_manual_review.yaml`. The same plate identity or near-identical photos never cross splits. I included all verified plates from the smaller emirates and all images with X, Y or Z; Dubai fills the rest. Val and test keep each emirate's share. Per-emirate counts: `outputs/plates/data/finetune_ledger.md`; full list: `finetune_ledger.csv`.
- **Left out on purpose:** Umm Al Quwain plates and plates without an emirate box (too few examples); the product sends them to human review.
- **Coverage limits:** RAK and Ajman have only 10 and 17 val/test images each, and new-style Sharjah plates are absent, so results for these are not reliable.
- **Fine-tuning cap:** the 6,000 train and val images count; the 1,000 test images are never learned from and are listed apart (`outputs/budget.md`).

## 3. My videos (fixed camera, night)

I recorded three nights at my two bays with a phone fixed on a stick (portrait, 1080x1920, 30 fps). My two cars arrive, leave, park across both bays and park crookedly; I also stand in front of a bay, while other people and cars pass behind. I could not record during the day because the site is too crowded.

- **Night 1** (16 Nov 2026, `IMG_1503.MOV`, 10 min): a **cross-night check** of the adapted Model A and of the full system. Never used for training. It was seen during development and first informed three choices (Model A's raw confidence, no feature-distance check, plate caching); those were made again on block 4 alone (`outputs/trust/validation_choices.md`), so night 1 is reported as a seen check, not a test. Truth: `configs/local_video_night_1.yaml`.
- **Night 3** (27 Nov 2026, `data/raw/video_test/night_3.MOV`, 24 min, which I recorded alone): the **final system test**, recorded after I froze the design. Truth (`configs/local_video_night_3.yaml`) was marked before any model saw the video; I checked it and made no changes. My `commands.txt` sits beside the video. I ran the test once (`just final-test`, `outputs/final_test/night_3.md`). I never used it for training, validation or any choice.
- **Night 2** (24 Nov 2026, five files, about 43 min, recorded to a checklist): blocks 1-3 (about 31 min) **train** Model A's adaptation; block 4 (12 min) **chooses** its settings, thresholds and gates. Truth: `configs/local_video_night_2.yaml`.

Claude marked truth for all three from frames every 10 s and every 2 s; **I checked the labels** and corrected three entries on night 2. I do not score moving periods. I count a car across both bays as parked in both, and a car waiting in a bay as occupied. The camera did not move within a night, but its view differs across nights, so I drew each night's bay boxes once from a single frame. Bay crops: one frame every 2 s, 64 px: night 2 gives 1,604 training crops (913 empty, 691 occupied) and 600 validation crops; night 1 gives 486 check crops and night 3 1,142 test crops (a blocked lens is left out, like moving cars).

## 4. My local pilot photos

I took 8 phone photos (4 late afternoon, 4 night) on 19–20 November 2026, covering all four bay states (both empty, either one occupied, both occupied). The night photos come from one fixed spot at my site; the day photos come from four spots, one at another car park. I read the truth from the photos by eye and drew bay boxes by hand in `configs/local_pilot.yaml`. I used these only to check the full loop (occupancy CNN, then plate reading in occupied bays; `just occupancy-local-pilot`), never for training, model choice or thresholds. I read the true plates of the 8 parked cars by eye from the full-size photos.

## 5. My night photo set 1

I took 43 phone photos on 20 November 2026 at night in several public car parks, each showing one pair of bays from a standing position: 86 bays (46 empty, 40 occupied), 40 readable plates (36 distinct cars). I used one shared pair of bay boxes for every photo (`configs/local_night_1.yaml`), like a fixed camera. I labelled bay states and read plates by eye from the full-size photos. I used them only to check the full loop and probe its errors (`just local-night-1`); failures informed plate safety rules. I did not use them for gradient training. I confirmed the code letter on IMG_1838.

**Privacy (2026-11-25, confirmed 2026-11-26):** I consider all captured photos and videos public, plates and faces included, so truth labels and plate-level results are in Git and short samples are in `samples/`. The raw videos are too large for Git (about 8 GB). **Download:** all raw data, my photos and videos plus copies of the two public datasets, is hosted at https://huggingface.co/datasets/faisal-alansari/smart-parking-data (about 11 GB). `just download-data` downloads a pinned version into `data/raw/` and unpacks it.

## 6. My command sets (Model C)

I generated 220 short commands, as my phone's speech-to-text would write them, using `just command-data` (seeded, reproducible) into `outputs/commands/data/`: **dev** (60) for designing prompts and rules, and a frozen **test** set (160), opened once for the final comparison. Expected answers follow the scope I set on 2026-11-21: a clear allow or remove is PROPOSED (plate number, optional end time; permits cover both bays, so any bay said is ignored); anything unclear is NEEDS_REVIEW with a reason (unclear action including speech-to-text slips, missing, several or invalid numbers, a one-digit number, unclear time, an hour without AM/PM, a time already passed); other requests are UNSUPPORTED. Test make-up: 95 clear commands, 55 to review, 10 unsupported; 44 mention a bay, spot or slot; about a third of the allow and remove commands (33) use wording that never appears in dev; 6 contain a speech-to-text slip ("a loud", "aloud", "and"). I built each expected answer from the command's meaning, not from the rules or parser being tested; a perfect extraction reaches all 220 (`just command-score oracle test`). I used AI help and checked the labels myself (`test_review.md`). Plate numbers are random. I did not use these commands for training or fine-tuning.

Extra sets in dev wording (new numbers and times, `just command-data`, seeds in the config): **check** (120) and **confirm**, **confirm2**, **confirm3**, **confirm4** (120 each). Each confirm set stayed sealed until opened once; one that showed a failure became development data and the next was sealed, so only **confirm4** is a clean check of the final design. A **robustness** set (`just command-robustness`, 140) damages 40 fresh clear commands in five increasing levels (typos and casing, missing pieces, ambiguity, off-topic, tricks); it is never used to tune. None of these is used for training or fine-tuning.

## Fine-tuning item ledger (10,000 cap)

| Dataset | Items used for fine-tuning |
|---|---|
| CNRPark+EXT | 0 (from-scratch model) |
| AddingUAE | 6,000 counted (5,000 train, 1,000 val); the 1,000 test images are never learned from and are not counted |
| Local videos (bay crops, Model A) | 2,204 counted to be safe (1,604 train, 600 validation; Model A is a from-scratch model). Test crops (486 night 1, 1,142 night 3) are not counted |
| Local pilot photos | 0 (check only; no training or tuning) |
| Night photo set 1 | 0 (check only; no training or tuning) |
| My command sets | 0 (evaluation only; Model C is not fine-tuned) |
| **Total** | **8,204 of 10,000** (`outputs/budget.md`) |
