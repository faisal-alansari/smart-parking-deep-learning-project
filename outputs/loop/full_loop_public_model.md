# Full loop on the owner's photos (Models A + B + C)

51 photos, 102 bays (local_night_1, local_pilot). Each photo is treated as an arrival at the owner's two bays, at the time it was taken. The permit table comes from 33 owner commands, generated in the owner's own wording and sent through Model C (tiered); the simulated owner accepts a right proposal, fixes a wrong one and repeats a command when asked. Plates stay local, so this page shows counts only. Small sample: indicative only.

## Key numbers

| measure | all | local_night_1, night | local_pilot, day | local_pilot, night |
|---|---|---|---|---|
| bays | 102 | 86 | 8 | 8 |
| right | 65 (64%) | 52 (60%) | 6 (75%) | 7 (88%) |
| false alerts (alert on a car that is not unauthorized) | 0 | 0 | 0 | 0 |
| unauthorized cars | 35 | 32 | 3 | 0 |
|   alerted | 23 | 21 | 2 | 0 |
|   sent to a person | 7 | 6 | 1 | 0 |
|   missed (bay called empty) | 5 | 5 | 0 | 0 |
|   let through as AUTHORIZED | 0 | 0 | 0 | 0 |
| sent to a person (NEEDS_REVIEW) | 32 | 28 | 3 | 1 |
|   of which not needed | 31 | 28 | 2 | 1 |

## Truth against the system (all bays)

| truth \ system | EMPTY | AUTHORIZED | POTENTIALLY_UNAUTHORIZED | NEEDS_REVIEW |
|---|---|---|---|---|
| EMPTY | 33 | 0 | 0 | 21 |
| AUTHORIZED | 1 | 8 | 0 | 3 |
| POTENTIALLY_UNAUTHORIZED | 5 | 0 | 23 | 7 |
| NEEDS_REVIEW | 0 | 0 | 0 | 1 |

## Which stage caused each wrong answer

| stage | bays |
|---|---|
| A occupancy | 27 |
| B plate | 10 |

Model C cannot cause a wrong answer here: the owner checks every change.

## Model C and the owner's check

| command path | commands |
|---|---|
| accepted | 24 |
| asked | 9 |

| measure | with owner check | Model C alone (no owner check) |
|---|---|---|
| bays | 102 | 102 |
| right | 65 (64%) | 63 (62%) |
| false alerts (alert on a car that is not unauthorized) | 0 | 2 |
| unauthorized cars | 35 | 35 |
|   alerted | 23 | 23 |
|   sent to a person | 7 | 7 |
|   missed (bay called empty) | 5 | 5 |
|   let through as AUTHORIZED | 0 | 0 |
| sent to a person (NEEDS_REVIEW) | 32 | 32 |
|   of which not needed | 31 | 31 |

Bays the owner's check saved (wrong without it, right with it): 2.
