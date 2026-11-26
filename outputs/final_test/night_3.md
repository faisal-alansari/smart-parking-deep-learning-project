# Final test: the whole system on the sealed night video 3

Night video 3 was recorded for this test only (docs/planning/test_video_checklist.md) and never
used for training, validation or any choice. Its truth (configs/local_video_night_3.yaml) was
marked from the frames and checked by the owner before any model saw the video. The rules and
the primary measure were fixed in Memory.md (2026-11-27) before the run.

1. The owner's typed commands (`commands.txt` beside the video) go through Model C as in the
   product. Each proposal is accepted as proposed, so a Model C mistake reaches the bays. The
   intended permit table is built by hand from the same lines (`commands` in the config).
2. Every frame (one every 2 s) goes through the camera check, Model A and Model B against the
   table Model C built.
3. The per-stay rule (`smart_parking.stays`, with plate caching) gives one answer per stay.

**Primary measure:** of the true stays of at least 30 s, the share whose answer at the stay's
last parked frame is right (owner's table). Stays under 30 s are reported on their own.
The models run once; `--report` rebuilds the report from the saved per-frame results.

Video: 23.9 minutes, 719 frames, two bays; truth **checked by the owner (2026-11-27), no changes**. One night, one spot, one run: indicative, not a benchmark.

## Measures

| measure | result |
|---|---|
| PRIMARY: stays of 30 s or more, answer right | 5 of 9 |
| stays under 30 s, answer right | 1 of 1 |
| stays of 30 s or more with a plate found | 5 of 9 |
| frames: per-stay answer right (not moving) | 82% |
| frames: occupancy right (Model A, not moving or blocked) | 91% |
| frames: empty bay called occupied (Model A) | 1 of 475 |
| frames: parked car called empty (Model A) | 100 of 667 |
| frames: plate read right (bays with a car, Model B) | 441 of 667 |
| lens blocked: frames sent to a person | 20 of 20 |
| false alerts: frames alerting on an allowed car | 0 of 455 |
| stays seen with no car there | 0 |
| notifications to the owner, left + right | 8 + 12 |

## Owner commands (Model C)

| time | command | Model C proposal | reply | meaning right |
|---|---|---|---|---|
| 00:04 | allow car 66705 | {"action":"ALLOW","number":"66705"} | Done: Allow car 66705 in either bay permanently (no end time). | True |
| 00:04 | allow car 33044 until 00:14 | {"action":"ALLOW","number":"33044","until":"2026-11-27T00:14:00+04:00"} | Done: Allow car 33044 in either bay until Fri 27 Nov 00:14. | True |
| 00:11 | what's the weather today | no change | Do you want to allow or remove a car? | True |

## Each true stay

| bay | true stay | seconds | note | seen as occupied from | plate found | right answer | system answer | right |
|---|---|---|---|---|---|---|---|---|
| left | 1:26-5:46 | 260 | BMW reverses in | 1:26 | AA66705 | AUTHORIZED | AUTHORIZED | True |
| right | 3:40-7:46 | 246 | Tesla nose-in | 3:44 | O33044 | AUTHORIZED | AUTHORIZED | True |
| left | 9:16-10:52 | 96 | BMW across both bays | 9:18 | no | AUTHORIZED | NEEDS_REVIEW | False |
| right | 9:16-10:52 | 96 | BMW across both bays | 9:20 | no | AUTHORIZED | NEEDS_REVIEW | False |
| right | 12:06-12:28 | 22 | quick in-and-out | 12:10 | O33044 | POTENTIALLY_UNAUTHORIZED | POTENTIALLY_UNAUTHORIZED | True |
| left | 13:10-14:46 | 96 | Tesla crooked over the middle line | never | no | POTENTIALLY_UNAUTHORIZED | EMPTY | False |
| right | 13:10-14:46 | 96 | Tesla crooked over the middle line | never | no | POTENTIALLY_UNAUTHORIZED | EMPTY | False |
| right | 15:06-16:54 | 108 | Tesla crooked | 15:06 | O33044 | POTENTIALLY_UNAUTHORIZED | POTENTIALLY_UNAUTHORIZED | True |
| right | 17:12-21:08 | 236 | Tesla parked again | 17:18 | O33044 | POTENTIALLY_UNAUTHORIZED | POTENTIALLY_UNAUTHORIZED | True |
| left | 18:05-21:58 | 233 | BMW nose-in | 18:12 | AA66705 | AUTHORIZED | AUTHORIZED | True |

## Per slice (frames not moving)

| frames | bay checks | per-stay answer right | frame-by-frame answer right |
|---|---|---|---|
| camera blocked | 20 | 100% | 100% |
| car across both bays | 192 | 0% | 0% |
| car just outside the right bay | 124 | 100% | 95% |
| crooked car | 66 | 100% | 94% |
| headlights on | 54 | 94% | 100% |
| normal | 620 | 99% | 99% |
| person in an empty bay | 34 | 100% | 100% |
| person in front of the plate | 30 | 100% | 50% |
| short stay (22 s) | 22 | 91% | 100% |

## Truth against the system (per-stay answers, frames not moving)

| truth \ system | AUTHORIZED | EMPTY | NEEDS_REVIEW | POTENTIALLY_UNAUTHORIZED |
|---|---|---|---|---|
| AUTHORIZED | 327 | 8 | 93 | 0 |
| EMPTY | 2 | 473 | 0 | 0 |
| NEEDS_REVIEW | 0 | 0 | 20 | 0 |
| POTENTIALLY_UNAUTHORIZED | 0 | 101 | 0 | 138 |

## Time per stage (this Mac)

| stage | calls | mean ms | p95 ms |
|---|---|---|---|
| C command (one command) | 3 | 36.2 | 96.9 |
| camera check (one frame) | 719 | 5.2 | 5.8 |
| A occupancy (one frame, both bays) | 709 | 6.8 | 8.6 |
| permit table check (one bay) | 1418 | 0.0 | 0.0 |
| B plate read (one occupied bay) | 664 | 56.9 | 62.3 |
