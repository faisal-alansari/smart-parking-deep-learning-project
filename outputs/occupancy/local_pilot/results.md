# Full loop: local_pilot

8 photos, 16 bays. Both models trained on public data only. Small sample: indicative only.

## 1. Occupancy (majority vote of the 3 final CNN seeds)

| light | bays | correct | accuracy | false_alarms | missed_cars |
|---|---|---|---|---|---|
| all | 16 | 15 | 0.938 | 1 of 8 empty | 0 of 8 occupied |
| day | 8 | 7 | 0.875 | 1 of 4 empty | 0 of 4 occupied |
| night | 8 | 8 | 1.0 | 0 of 4 empty | 0 of 4 occupied |

| photo | light | bay | truth | p_s42 | p_s43 | p_s44 | pred | correct |
|---|---|---|---|---|---|---|---|---|
| IMG_1601 | day | left | 1 | 0.997 | 0.999 | 1.0 | 1 | True |
| IMG_1601 | day | right | 1 | 0.962 | 0.987 | 0.977 | 1 | True |
| IMG_1731 | day | left | 0 | 0.063 | 0.891 | 0.109 | 0 | True |
| IMG_1731 | day | right | 0 | 0.908 | 0.975 | 0.053 | 1 | False |
| IMG_1766 | day | left | 1 | 0.997 | 1.0 | 1.0 | 1 | True |
| IMG_1766 | day | right | 0 | 0.001 | 0.01 | 0.001 | 0 | True |
| IMG_1771 | day | left | 0 | 0.003 | 0.199 | 0.023 | 0 | True |
| IMG_1771 | day | right | 1 | 1.0 | 0.999 | 0.999 | 1 | True |
| IMG_1817 | night | left | 0 | 0.563 | 0.084 | 0.348 | 0 | True |
| IMG_1817 | night | right | 1 | 0.999 | 1.0 | 1.0 | 1 | True |
| IMG_1818 | night | left | 1 | 0.991 | 0.999 | 0.998 | 1 | True |
| IMG_1818 | night | right | 0 | 0.01 | 0.255 | 0.077 | 0 | True |
| IMG_1819 | night | left | 0 | 0.015 | 0.1 | 0.002 | 0 | True |
| IMG_1819 | night | right | 0 | 0.008 | 0.074 | 0.035 | 0 | True |
| IMG_1820 | night | left | 1 | 0.993 | 0.999 | 0.999 | 1 | True |
| IMG_1820 | night | right | 1 | 1.0 | 1.0 | 1.0 | 1 | True |

## 2. Plate reading in bays called occupied (YOLO11n final seed 42)

`bay` = read from the bay area (the product loop); `photo` = read from the whole photo (comparison). `plate_width` = plate width as a share of the bay width.

| photo | light | bay | truth | pred | true_plate | bay_read | bay_decision | bay_conf | plate_width | bay_outcome | photo_read | photo_outcome |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| IMG_1601 | day | left | 1 | 1 | Sharjah 269030 | None 3269930 | NEEDS_REVIEW (no_emirate) | 0.33 | 0.28 | review | Dubai K6 | misread |
| IMG_1601 | day | right | 1 | 1 |  | None 2710 | NEEDS_REVIEW (plate_too_small) | 0.21 | 0.08 | correct_review_no_plate | none | correct_no_plate |
| IMG_1731 | day | right | 0 | 1 |  | Dubai 88159 | NEEDS_REVIEW (plate_too_small) | 0.3 | 0.09 | empty_bay_review | None  | empty_bay_review |
| IMG_1766 | day | left | 1 | 1 | Dubai W48556 | Dubai W48556 | READ | 0.82 | 0.29 | correct | Dubai W48558 | misread |
| IMG_1771 | day | right | 1 | 1 | Dubai O48837 | Dubai O48837 | READ | 0.83 | 0.27 | correct | Dubai 499 | review |
| IMG_1817 | night | right | 1 | 1 | Dubai AA66705 | Dubai AA66705 | READ | 0.47 | 0.29 | correct | Dubai 9965 | review |
| IMG_1818 | night | left | 1 | 1 | Dubai O33044 | Dubai O33044 | READ | 0.83 | 0.28 | correct | Dubai 524 | review |
| IMG_1820 | night | left | 1 | 1 | Dubai O33044 | Dubai O33044 | READ | 0.9 | 0.28 | correct | Dubai 9044 | review |
| IMG_1820 | night | right | 1 | 1 | Dubai AA66705 | Dubai 66705 | NEEDS_REVIEW (missing_code) | 0.73 | 0.29 | review | Dubai 556 | review |

## 3. End to end

Bays fully right (occupancy right and, if occupied, the plate read right or a missing plate sent to review): 13 of 16.
