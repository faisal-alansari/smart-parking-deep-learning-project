# Night video: one decision per stay

The rule was fixed before it was run (2026-11-22): a bay changes state only after 5 frames in a row agree (10 s), and the stay's plate must be the most frequent clear read, seen at least 2 times and in more than half of the clear reads. Same per-frame model outputs as `video_night_1.md`. **This video had already been seen, so this is a seen check, not a clean test.** Counts and times only. `(scored)`: frames while a car moves in or out are left out; `(all)`: every frame.

| measure | frame by frame | per stay |
|---|---|---|
| occupancy right (scored) | 84% | 84% |
| empty bay called occupied (scored) | 78 of 243 | 67 of 243 |
| owner's cars: answer right (scored) | 69% | 69% |
| as visitors: answer right (scored) | 69% | 69% |
| owner's cars: frames with a false alert (all) | 4 | 0 |
| notifications to the owner, left + right (all) | 32 + 46 | 12 + 17 |

## Each true stay

| bay | true stay | across both bays | seen as occupied from | plate found | answer at the end (owner's car) | answer at the end (as a visitor) |
|---|---|---|---|---|---|---|
| left | 0:00-0:28 | yes | 0:08 | yes | AUTHORIZED | POTENTIALLY_UNAUTHORIZED |
| right | 0:00-0:28 | yes | 0:08 | no | NEEDS_REVIEW | NEEDS_REVIEW |
| right | 1:54-3:54 |  | 1:54 | yes | AUTHORIZED | POTENTIALLY_UNAUTHORIZED |
| left | 2:56-5:12 |  | 2:56 | yes | AUTHORIZED | POTENTIALLY_UNAUTHORIZED |
| left | 8:26-10:01 | yes | 8:32 | yes | AUTHORIZED | POTENTIALLY_UNAUTHORIZED |
| right | 8:26-10:01 | yes | 8:26 | no | NEEDS_REVIEW | NEEDS_REVIEW |

Stays seen with no car there: 5 (left 1:58-2:16, left 6:12-6:32, left 8:02-8:12, right 6:08-6:40, right 7:02-7:32).
