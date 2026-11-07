# Data Card

The `data/` folder is not stored in Git. This card explains where each dataset comes from, where it goes, and how it is used.

## Layout

| Path | Contents |
|---|---|
| `data/raw/cnrpark/` | CNRPark+EXT download (patch zips, CSV, official splits) |
| `data/raw/adding_uae/` | AddingUAE plate dataset (YOLO format) |
| `data/raw/local_videos/` | Owner's own recordings of the two bays (planned) |
| `data/processed/occupancy/` | Built by `just prepare-data`: manifest, dataset with splits, image cache |
| `data/processed/plates/` | Built by `just audit-plates` and `just prepare-plates`: box tables, YOLO folders for the subset |

## 1. CNRPark+EXT (occupancy model, trained from scratch)

- **Source:** http://cnrpark.it/ (files: `CNR-EXT-Patches-150x150.zip`, `CNRPark-Patches-150x150.zip`, `CNRPark+EXT.csv`, `splits.zip`). Unzip into `data/raw/cnrpark/`.
- **Citation:** G. Amato, F. Carrara, F. Falchi, C. Gennaro, C. Meghini, C. Vairo, "Deep learning for decentralized parking lot occupancy detection", *Expert Systems with Applications*, 2017. G. Amato et al., "Car parking occupancy detection using smart camera networks and deep learning", *IEEE ISCC*, 2016.
- **License:** A third-party mirror lists ODbL v1.0. Not yet confirmed on the official site.
- **Contents:** 157,549 labelled crops of single parking spaces (free / busy) from 11 cameras: CNR-EXT (9 cameras, Nov 2015 – Feb 2016) and CNRPark A/B (July 2015). Captured 07:00–18:00; almost no night images.
- **Cleaning:** 39 blank images, 26 crops whose CSV label disagrees with the official label file, and 704 crops too dark to check by eye are excluded. 37,062 near-copies (same bay looking the same as its last kept snapshot) are removed.
- **Splits:** camera C02 and the CNRPark A/B site are held out completely (unseen camera and unseen site tests). The other 8 cameras are split by the official day lists, so no day is shared. Train is balanced to 20,000 free + 20,000 busy, spread over cameras; validation and test keep their natural class mix. Full counts: `outputs/occupancy/data/data_report.md`.
- **Fine-tuning cap:** not counted. This data trains a model from random initialization.

## 2. AddingUAE (plate reading, fine-tuning YOLO11n)

- **Source:** https://universe.roboflow.com/addinguae/uae-zcfqj (Roboflow export "UAE v1", YOLOv11 format). Unzip into `data/raw/adding_uae/`.
- **License:** CC BY 4.0 (from the Roboflow page).
- **Contents (from the dataset page):** about 10,000 images; 51 classes: `plate`, digits 0–9, letters A–Z, `exp`, and new/old plate types for the seven emirates. The downloaded export is split 70/20/10 at random: 6,990 train, 1,997 validation, 998 test images.
- **Audit (`just audit-plates`, report in `outputs/plates/data/audit_report.md`):** 86,294 boxes, no exact duplicate images, no augmentation. File names usually carry the main plate's text (e.g. `K-67810`); among plate-style names, 8,619 labels match the name exactly, 185 partly (about half label mistakes, a quarter name mistakes, the rest hidden or cut-off plates). 359 plate-only images have character boxes but no `plate` box. 184 images are plate close-ups. Some car photos are mock-ups (the same car with different plates edited in). Plate types are mostly Dubai (old 5,036, new 2,840); new-style Sharjah plates are missing. Rare classes: Y (15), Z (7), `exp` (3).
- **Leakage in the export split:** 118 plate identities (254 images) appear in more than one split, and 42 near-identical car photos cross splits. A re-split by plate identity and image similarity is needed.
- **Fine-tuning subset (`just prepare-plates`):** 7,000 car photos, 5,000 train / 1,000 val / 1,000 test, re-split from scratch (the export's split is not used). 6,905 are verified (labels exactly match the file name). 95 RAK / UAQ car photos without a plate-style name were checked by eye and added to train only; 19 were rejected (`configs/plates_manual_review.yaml`). The same plate identity or near-identical photos never cross splits. All plates from the smaller emirates and all images with X, Y or Z are included; Dubai fills the rest. Val and test keep each emirate's share. Per-emirate counts: `outputs/plates/data/finetune_ledger.md`; full list: `finetune_ledger.csv`.
- **Coverage limits:** RAK has only 10 val and 10 test images, UAQ only 1 each, and new-style Sharjah plates are absent, so results for these are not reliable.
- **Fine-tuning cap:** all 7,000 selected images count (train, val and test).

## 3. Owner's local videos (planned)

Nine 15-minute sessions of the two real bays, with session notes giving when each bay changes state. Sessions 8 (day) and 9 (night) are never trained on. Videos stay local because they show real plates.

## Fine-tuning item ledger (10,000 cap)

| Dataset | Items used for fine-tuning |
|---|---|
| CNRPark+EXT | 0 (from-scratch model) |
| AddingUAE | 7,000 (5,000 train, 1,000 val, 1,000 test) |
| Local videos | 0 planned for plate fine-tuning (2–3 plates; real-site check only) |
| **Total** | **7,000 of 10,000** (3,000 left) |
