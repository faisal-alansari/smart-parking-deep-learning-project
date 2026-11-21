# Probes: night car parks, 43 photos (2026-11-20)

Indicative only: these probes explain the same photos they look at.

## Occupancy: same bays, different box shapes

| box | correct | false_alarms | missed_cars |
|---|---|---|---|
| original | 60 of 86 | 20 of 46 | 6 of 40 |
| background_cut | 72 of 86 | 11 of 46 | 3 of 40 |
| floor_only | 69 of 86 | 10 of 46 | 7 of 40 |
| sides_trimmed | 61 of 86 | 19 of 46 | 6 of 40 |
| zoomed_out | 40 of 86 | 37 of 46 | 9 of 40 |

## Occupancy: false alarms and wheel stops

Wheel stops were marked by eye on the empty bays (`wheel_stop` in the config).

| box | false_alarms_with_wheel_stop | false_alarms_without | share_of_false_alarms_with_a_stop |
|---|---|---|---|
| original | 15 of 26 | 5 of 20 | 15 of 20 |
| background_cut | 10 of 26 | 1 of 20 | 10 of 11 |

## Occupancy: brightness of empty bays

| empty_bays | n | mean_brightness |
|---|---|---|
| false alarm | 20 | 92 |
| correct | 26 | 91 |

## Occupancy: do the 3 seeds agree?

| seeds | right |
|---|---|
| all 3 agree | 47 of 65 |
| split 2-1 | 13 of 21 |

## Plates: letter boxes on misread or reviewed plates

Confidence of each letter box the detector found on the plate (kept: at or above the reading threshold; dropped: below it, down to 0.05).

| photo | bay | outcome | decision | letters_kept | letters_dropped |
|---|---|---|---|---|---|
| IMG_1837 | right | review | NEEDS_REVIEW (missing_code) | - | - |
| IMG_1843 | left | review | NEEDS_REVIEW (missing_code) | - | - |
| IMG_1845 | right | review | NEEDS_REVIEW (invalid_length) | - | - |
| IMG_1846 | left | review | NEEDS_REVIEW (missing_code) | - | 0.15 |
| IMG_1851 | right | misread | READ | 0.39 | 0.08, 0.06 |
| IMG_1853 | left | review | NEEDS_REVIEW (no_emirate) | - | - |
| IMG_1853 | right | review | NEEDS_REVIEW (missing_code) | - | 0.14 |
| IMG_1854 | left | misread | READ | 0.74 | 0.11, 0.07 |
| IMG_1856 | right | misread | READ | 0.60 | 0.10 |
| IMG_1858 | right | review | NEEDS_REVIEW (missing_code) | - | 0.19 |
| IMG_1859 | left | misread | READ | 0.57 | 0.14 |
| IMG_1859 | right | review | NEEDS_REVIEW (missing_code) | - | 0.16, 0.15 |
| IMG_1863 | left | misread | READ | 0.29, 0.27 | - |
| IMG_1864 | left | misread | READ | 0.26 | 0.15, 0.13, 0.08, 0.06, 0.05 |
