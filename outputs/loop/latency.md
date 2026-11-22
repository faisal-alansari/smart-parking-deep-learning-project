# Time and memory per stage (step 5)

Measured on the owner's Mac (Apple GPU, "MPS") on 2026-11-22, using `smart_parking.pipeline`
with all three models loaded once. Sources: the night video (301 frames, one every 2 s) and a
mixed folder (`just run-folder`: 6 iPhone photos, the video at one frame every 10 s, and the 60
dev commands).

| stage | what one call does | mean | p95 |
|---|---|---|---|
| A occupancy | both bays of one frame, 3 CNN seeds | 8 ms | 8–13 ms |
| B plate read | YOLO11n + reading rules on one occupied bay | 51 ms | 55–73 ms |
| permit table check | one bay | under 0.1 ms | under 0.1 ms |
| C command | one typed command through Model C (tiered) | 117 ms | 365 ms |

- **One camera frame** (both bays occupied, the slowest case): about 8 + 2 × 51 ≈ 110 ms, so
  roughly 9 frames per second. One frame every 1–2 seconds is plenty for parking.
- **One owner command:** about 0.1 s on average, at most about 0.4 s for 95% of commands. Most of
  this is the two command models (GLiNER + MiniLM, then the SmolLM2 check).
- **Loading:** about 10 s once at start (all models); peak memory about 2.2 GB.
- Model C on the CPU only is about 6× slower (0.7 s per command; `outputs/commands/candidates.md`).
