# Run on folder `samples/owner_camera`

Camera: the owner's camera (default boxes and snapshot); occupancy model: adapted. 3 commands, 246 bay decisions, 0 input problems. Everything: `result.json`.

## Commands

| time | command | reply |
|---|---|---|
| 2026-01-01 08:00:00+04:00 | allow car 66705 | Done: Allow car 66705 in either bay permanently (no end time). |
| 2026-01-01 08:01:00+04:00 | what's the weather today | Do you want to allow or remove a car? |
| 2026-01-01 08:02:00+04:00 | add 12345 until 6 | Is that AM or PM? |

## Answers (one per stay for videos)

| source | bay | AUTHORIZED | EMPTY | NEEDS_REVIEW | POTENTIALLY_UNAUTHORIZED |
|---|---|---|---|---|---|
| both_parked.jpg | left | 1 | 0 | 0 | 0 |
| both_parked.jpg | right | 0 | 0 | 0 | 1 |
| covered_lens.jpg | left | 0 | 0 | 1 | 0 |
| covered_lens.jpg | right | 0 | 0 | 1 | 0 |
| night_clip.mp4 | left | 14 | 96 | 10 | 0 |
| night_clip.mp4 | right | 20 | 35 | 10 | 55 |
| other_car_park.jpg | left | 0 | 0 | 1 | 0 |
| other_car_park.jpg | right | 0 | 0 | 1 | 0 |

## Timeline: night_clip.mp4 (one decision per stay)

| bay | from | to | frames | status |
|---|---|---|---|---|
| left | 0:00 | 0:06 | 4 | EMPTY |
| left | 0:08 | 0:10 | 2 | NEEDS_REVIEW |
| left | 0:12 | 0:30 | 10 | EMPTY |
| left | 0:32 | 0:32 | 1 | NEEDS_REVIEW |
| left | 0:34 | 0:36 | 2 | EMPTY |
| left | 0:38 | 0:38 | 1 | NEEDS_REVIEW |
| left | 0:40 | 0:42 | 2 | EMPTY |
| left | 0:44 | 0:54 | 6 | NEEDS_REVIEW |
| left | 0:56 | 3:30 | 78 | EMPTY |
| left | 3:32 | 3:58 | 14 | AUTHORIZED |
| right | 0:00 | 0:06 | 4 | EMPTY |
| right | 0:08 | 0:10 | 2 | NEEDS_REVIEW |
| right | 0:12 | 0:30 | 10 | AUTHORIZED |
| right | 0:32 | 0:32 | 1 | NEEDS_REVIEW |
| right | 0:34 | 0:36 | 2 | AUTHORIZED |
| right | 0:38 | 0:38 | 1 | NEEDS_REVIEW |
| right | 0:40 | 0:42 | 2 | AUTHORIZED |
| right | 0:44 | 0:54 | 6 | NEEDS_REVIEW |
| right | 0:56 | 1:06 | 6 | AUTHORIZED |
| right | 1:08 | 2:08 | 31 | EMPTY |
| right | 2:10 | 3:58 | 55 | POTENTIALLY_UNAUTHORIZED |

## Evidence frames (each notification)

| source | clock | bay | stay_status | plate | reason | evidence |
|---|---|---|---|---|---|---|
| other_car_park.jpg |  | left | NEEDS_REVIEW |  | unfamiliar_view | outputs/runs/owner_camera/evidence/other_car_park_left.jpg |
| other_car_park.jpg |  | right | NEEDS_REVIEW |  | unfamiliar_view | outputs/runs/owner_camera/evidence/other_car_park_right.jpg |
| night_clip.mp4 | 0:08 | left | NEEDS_REVIEW |  | blurred_view | outputs/runs/owner_camera/evidence/night_clip_left_0-08.jpg |
| night_clip.mp4 | 0:08 | right | NEEDS_REVIEW |  | blurred_view | outputs/runs/owner_camera/evidence/night_clip_right_0-08.jpg |
| night_clip.mp4 | 0:12 | right | AUTHORIZED | Dubai AA66705 |  | outputs/runs/owner_camera/evidence/night_clip_right_0-12.jpg |
| night_clip.mp4 | 0:32 | left | NEEDS_REVIEW |  | unfamiliar_view | outputs/runs/owner_camera/evidence/night_clip_left_0-32.jpg |
| night_clip.mp4 | 0:32 | right | NEEDS_REVIEW |  | unfamiliar_view | outputs/runs/owner_camera/evidence/night_clip_right_0-32.jpg |
| night_clip.mp4 | 0:34 | right | AUTHORIZED | Dubai AA66705 |  | outputs/runs/owner_camera/evidence/night_clip_right_0-34.jpg |
| night_clip.mp4 | 0:38 | left | NEEDS_REVIEW |  | unfamiliar_view | outputs/runs/owner_camera/evidence/night_clip_left_0-38.jpg |
| night_clip.mp4 | 0:38 | right | NEEDS_REVIEW |  | unfamiliar_view | outputs/runs/owner_camera/evidence/night_clip_right_0-38.jpg |
| night_clip.mp4 | 0:40 | right | AUTHORIZED | Dubai AA66705 |  | outputs/runs/owner_camera/evidence/night_clip_right_0-40.jpg |
| night_clip.mp4 | 0:44 | left | NEEDS_REVIEW |  | blurred_view | outputs/runs/owner_camera/evidence/night_clip_left_0-44.jpg |
| night_clip.mp4 | 0:44 | right | NEEDS_REVIEW |  | blurred_view | outputs/runs/owner_camera/evidence/night_clip_right_0-44.jpg |
| night_clip.mp4 | 0:56 | right | AUTHORIZED | Dubai AA66705 |  | outputs/runs/owner_camera/evidence/night_clip_right_0-56.jpg |
| night_clip.mp4 | 2:10 | right | POTENTIALLY_UNAUTHORIZED | Dubai O33044 |  | outputs/runs/owner_camera/evidence/night_clip_right_2-10.jpg |
| night_clip.mp4 | 3:32 | left | AUTHORIZED | Dubai AA66705 |  | outputs/runs/owner_camera/evidence/night_clip_left_3-32.jpg |
| both_parked.jpg |  | left | AUTHORIZED | Dubai AA66705 |  | outputs/runs/owner_camera/evidence/both_parked_left.jpg |
| both_parked.jpg |  | right | POTENTIALLY_UNAUTHORIZED | Dubai O33044 |  | outputs/runs/owner_camera/evidence/both_parked_right.jpg |
| covered_lens.jpg |  | left | NEEDS_REVIEW |  | camera_blocked | outputs/runs/owner_camera/evidence/covered_lens_left.jpg |
| covered_lens.jpg |  | right | NEEDS_REVIEW |  | camera_blocked | outputs/runs/owner_camera/evidence/covered_lens_right.jpg |

## Time per stage

| stage | calls | mean ms | p95 ms |
|---|---|---|---|
| C command (one command) | 3 | 31.7 | 84.8 |
| camera check (one frame) | 123 | 5.0 | 5.4 |
| A occupancy (one frame, both bays) | 111 | 6.8 | 7.2 |
| permit table check (one bay) | 222 | 0.0 | 0.0 |
| B plate read (one occupied bay) | 19 | 60.0 | 79.0 |
