# Efficiency study (quality against cost)

Two ideas, chosen on block 4 of night video 2 (validation; one frame every 2 s through the
product), then shown on night video 1 as a seen check:
1. **frame rate:** one frame every 2, 4 or 8 s, keeping the same 10 s to confirm a stay;
2. **plate caching:** once a stay's plate has been read the same way 3 times, stop running
   Model B on that bay until the car leaves.
Quality: the answer at the end of each true stay (as the owner's car and as a visitor), per-stay
answers right on scored frames, notifications, and how late an arrival is confirmed. Cost: model
time per minute of video, from the measured time per call (`outputs/loop/latency.md`).
Caching is kept only if, on block 4, it answers at least as many stay ends right, per-stay
answers stay within 1 point and Model B runs fewer times (rule fixed first; report Appendix A).

Measured time per call: Model A 6.6 ms per frame (both bays), Model B 56.6 ms per occupied bay.

## Block 4 (validation): the choice

| frame every (s) | plate caching | frames | A calls | B calls | stay-end answers right | per-stay answers right (scored) | notifications | mean arrival delay (s) | model time per minute of video (ms) | cost vs no caching |
|---|---|---|---|---|---|---|---|---|---|---|
| 2 | off | 366 | 366 | 396 | 4 of 6 | 96% | 36 | 2.7 | 2035 | 100% |
| 2 | after 3 reads | 366 | 366 | 15 | 4 of 6 | 96% | 36 | 2.7 | 268 | 13% |
| 4 | off | 183 | 183 | 198 | 4 of 6 | 96% | 19 | 2.0 | 1018 | 50% |
| 4 | after 3 reads | 183 | 183 | 11 | 4 of 6 | 96% | 19 | 2.0 | 150 | 7% |
| 8 | off | 92 | 92 | 99 | 4 of 6 | 96% | 16 | 4.7 | 509 | 25% |
| 8 | after 3 reads | 92 | 92 | 10 | 4 of 6 | 96% | 16 | 4.7 | 96 | 5% |

**Plate caching: kept** under the rule.

## Night video 1 (seen check, not used to choose)

| frame every (s) | plate caching | frames | A calls | B calls | stay-end answers right | per-stay answers right (scored) | notifications | mean arrival delay (s) | model time per minute of video (ms) | cost vs no caching |
|---|---|---|---|---|---|---|---|---|---|---|
| 2 | off | 301 | 301 | 235 | 8 of 12 | 79% | 30 | 0.0 | 1524 | 100% |
| 2 | after 3 reads | 301 | 301 | 53 | 8 of 12 | 83% | 28 | 0.0 | 497 | 33% |
| 4 | off | 151 | 151 | 116 | 8 of 12 | 82% | 30 | 1.0 | 754 | 49% |
| 4 | after 3 reads | 151 | 151 | 30 | 8 of 12 | 83% | 26 | 1.0 | 269 | 18% |
| 8 | off | 76 | 76 | 61 | 8 of 12 | 81% | 25 | 3.0 | 394 | 26% |
| 8 | after 3 reads | 76 | 76 | 23 | 8 of 12 | 82% | 23 | 3.0 | 180 | 12% |
