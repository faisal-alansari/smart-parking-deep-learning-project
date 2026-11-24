# Run on folder `samples/new_camera`

Camera: set up from bays.yaml; occupancy model: final. 1 commands, 4 bay decisions, 0 input problems. Everything: `result.json`.

## Commands

| time | command | reply |
|---|---|---|
| 2026-01-01 08:00:00+04:00 | please add 33044 | Done: Allow car 33044 in either bay permanently (no end time). |

## Answers (one per stay for videos)

| source | bay | AUTHORIZED | EMPTY | POTENTIALLY_UNAUTHORIZED |
|---|---|---|---|---|
| IMG_1818.jpg | left | 1 | 0 | 0 |
| IMG_1818.jpg | right | 0 | 1 | 0 |
| IMG_1820.jpg | left | 1 | 0 | 0 |
| IMG_1820.jpg | right | 0 | 0 | 1 |

## Evidence frames (each notification)

| source | clock | bay | stay_status | plate | reason | evidence |
|---|---|---|---|---|---|---|
| IMG_1818.jpg |  | left | AUTHORIZED | Dubai O33044 |  | outputs/runs/new_camera/evidence/IMG_1818_left.jpg |
| IMG_1820.jpg |  | left | AUTHORIZED | Dubai O33044 |  | outputs/runs/new_camera/evidence/IMG_1820_left.jpg |
| IMG_1820.jpg |  | right | POTENTIALLY_UNAUTHORIZED | Dubai A66705 |  | outputs/runs/new_camera/evidence/IMG_1820_right.jpg |

## Time per stage

| stage | calls | mean ms | p95 ms |
|---|---|---|---|
| C command (one command) | 1 | 0.5 | 0.5 |
| camera check (one frame) | 2 | 7.0 | 7.2 |
| A occupancy (one frame, both bays) | 2 | 19.2 | 30.6 |
| B plate read (one occupied bay) | 3 | 59.4 | 72.5 |
| permit table check (one bay) | 4 | 0.0 | 0.0 |
