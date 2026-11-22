# Full loop on the owner's night video (fixed camera)

One 10-minute night video of the owner's two bays, one frame every 2 s (301 frames). The owner's two cars arrive and leave several times. 58 frames while a car is moving in or out are not scored. Twice the owner's car stands across both bays; it then counts as parked in both (its own column). Truth: marked from the video by Claude, **checked by the owner (2026-11-22), no changes**. Each car is scored twice: as the owner's car (on the permanent list, so the right answer is AUTHORIZED) and as a visitor (empty table, so the right answer is POTENTIALLY_UNAUTHORIZED). Counts only. One night, one spot: indicative only.

| measure | all | car across both bays | normal |
|---|---|---|---|
| bay checks (frames x bays) | 486 | 124 | 362 |
| occupancy right | 84% | 100% | 78% |
| empty bay called occupied | 78 of 243 | 0 of 0 | 78 of 243 |
| parked car called empty | 0 of 243 | 0 of 124 | 0 of 119 |
| plate read right (bays with a car) | 140 of 243 | 41 of 124 | 99 of 119 |
| owner's cars: final answer right | 69% | 45% | 77% |
| owner's cars: false alerts | 0 | 0 | 0 |
| as visitors: final answer right | 69% | 45% | 77% |
| as visitors: alerted / to a person / missed | 169 / 74 / 0 | 56 / 68 / 0 | 113 / 6 / 0 |

## Owner's cars: truth against the system (scored frames)

| truth \ system | AUTHORIZED | EMPTY | NEEDS_REVIEW |
|---|---|---|---|
| AUTHORIZED | 169 | 0 | 74 |
| EMPTY | 0 | 165 | 78 |

## Over time (all frames, moving ones included)

| bay | status changes | false-alert episodes (owner's cars) |
|---|---|---|
| left | 32 | 1 |
| right | 46 | 3 |

## Time per stage (Mac, Apple GPU)

| stage | calls | mean ms | p95 ms |
|---|---|---|---|
| A occupancy (one frame, both bays) | 301 | 8.2 | 8.8 |
| B plate read (one occupied bay) | 399 | 54.3 | 59.6 |
| permit table check (one bay) | 602 | 0.0 | 0.0 |
