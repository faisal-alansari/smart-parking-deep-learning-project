# Time and memory per stage

Measured on the sample night clip (`samples/owner_camera`, one frame every 2 s) and the Model C
dev commands, never on test data. Writes `outputs/loop/latency.md`.

Machine: arm64 macOS 15.7.9, device mps. Models loaded once in **5.0 s**; peak memory of the process **2.7 GB**.

| stage | calls | mean ms | p95 ms |
|---|---|---|---|
| C command (one command) | 63 | 114.4 | 376.8 |
| camera check (one frame) | 123 | 5.1 | 5.6 |
| A occupancy (one frame, both bays) | 111 | 6.6 | 7.0 |
| permit table check (one bay) | 222 | 0.0 | 0.0 |
| B plate read (one occupied bay) | 19 | 56.6 | 61.7 |
| one frame end to end (camera check + A + B + permits) | 123 | 19.8 | 67.4 |

At one frame every 2 s, a frame that takes well under a second keeps up in real time; a command answers in well under a second.
