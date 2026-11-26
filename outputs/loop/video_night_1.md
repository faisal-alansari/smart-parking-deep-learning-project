# Full loop on the owner's night video (fixed camera)

One 10-minute night video of the owner's two bays, one frame every 2 s (301 frames). The owner's two cars arrive and leave several times. 58 frames while a car is moving in or out are not scored. Twice the owner's car stands across both bays; it then counts as parked in both (its own column). Truth: marked from the video by Claude, **checked by the owner (2026-11-22), no changes**. Each car is scored twice: as the owner's car (on the permanent list, so the right answer is AUTHORIZED) and as a visitor (empty table, so the right answer is POTENTIALLY_UNAUTHORIZED). Counts only. One night, one spot: indicative only.

| measure | all | car across both bays | normal |
|---|---|---|---|
| bay checks (frames x bays) | 486 | 124 | 362 |
| occupancy right | 88% | 65% | 96% |
| empty bay called occupied | 3 of 243 | 0 of 0 | 3 of 243 |
| parked car called empty | 43 of 243 | 43 of 124 | 0 of 119 |
| plate read right (bays with a car) | 130 of 243 | 41 of 124 | 89 of 119 |
| owner's cars: final answer right | 82% | 45% | 95% |
| owner's cars: false alerts | 0 | 0 | 0 |
| as visitors: final answer right | 82% | 45% | 95% |
| as visitors: alerted / to a person / missed | 159 / 41 / 43 | 56 / 25 / 43 | 103 / 16 / 0 |

## Owner's cars: truth against the system (scored frames)

| truth \ system | AUTHORIZED | EMPTY | NEEDS_REVIEW |
|---|---|---|---|
| AUTHORIZED | 159 | 43 | 41 |
| EMPTY | 0 | 240 | 3 |

## Over time (all frames, moving ones included)

| bay | status changes | false-alert episodes (owner's cars) |
|---|---|---|
| left | 29 | 0 |
| right | 35 | 1 |

## Time per stage (Mac, Apple GPU)

| stage | calls | mean ms | p95 ms |
|---|---|---|---|
| camera check (one frame) | 301 | 4.9 | 5.5 |
| A occupancy (one frame, both bays) | 292 | 6.7 | 7.7 |
| B plate read (one occupied bay) | 235 | 47.1 | 54.1 |
| permit table check (one bay) | 584 | 0.0 | 0.0 |
