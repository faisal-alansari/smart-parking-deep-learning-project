# Night video: one decision per stay

The rule was fixed before it was run (2026-11-22): a bay changes state only after 5 frames in a row agree (10 s), and the stay's plate must be the most frequent clear read, seen at least 2 times and in more than half of the clear reads. Same per-frame model outputs as `video_night_1.md`. **This video had already been seen, so this is a seen check, not a clean test.** Counts and times only. `(scored)`: frames while a car moves in or out are left out; `(all)`: every frame.

| measure | frame by frame | per stay |
|---|---|---|
| occupancy right (scored) | 88% | 88% |
| empty bay called occupied (scored) | 3 of 243 | 6 of 243 |
| owner's cars: answer right (scored) | 82% | 83% |
| as visitors: answer right (scored) | 82% | 83% |
| owner's cars: frames with a false alert (all) | 1 | 0 |
| notifications to the owner, left + right (all) | 29 + 35 | 13 + 15 |

## Each true stay

| bay | true stay | across both bays | seen as occupied from | plate found | answer at the end (owner's car) | answer at the end (as a visitor) |
|---|---|---|---|---|---|---|
| left | 0:00-0:28 | yes | 0:08 | yes | AUTHORIZED | POTENTIALLY_UNAUTHORIZED |
| right | 0:00-0:28 | yes | never | no | EMPTY | EMPTY |
| right | 1:54-3:54 |  | 1:54 | yes | AUTHORIZED | POTENTIALLY_UNAUTHORIZED |
| left | 2:56-5:12 |  | 2:56 | yes | AUTHORIZED | POTENTIALLY_UNAUTHORIZED |
| left | 8:26-10:01 | yes | 8:32 | yes | AUTHORIZED | POTENTIALLY_UNAUTHORIZED |
| right | 8:26-10:01 | yes | 8:32 | no | EMPTY | EMPTY |

Stays seen with no car there: 1 (right 7:10-7:20).
