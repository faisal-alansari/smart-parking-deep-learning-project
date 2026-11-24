# Efficiency study (quality against cost)

Two ideas, measured on the other night (the saved per-frame results, one frame every 2 s):
1. **frame rate:** one frame every 2, 4 or 8 s, keeping the same 10 s to confirm a stay;
2. **plate caching:** once a stay's plate has been read the same way 3 times, stop running
   Model B on that bay until the car leaves (today it re-reads the same parked car every frame).
Quality: the answer at the end of each true stay (as the owner's car and as a visitor), per-stay
answers right on scored frames, notifications, and how late an arrival is confirmed. Cost: model
time per minute of video, from the measured time per call (outputs/loop/video_night_1.md).

Measured time per call: Model A 6.6 ms per frame (both bays), Model B 54.2 ms per occupied bay. The first row is today's product.

| frame every (s) | plate caching | frames | A calls | B calls | stay-end answers right (of 12) | per-stay answers right (scored) | notifications | mean arrival delay (s) | model time per minute of video (ms) | cost vs today |
|---|---|---|---|---|---|---|---|---|---|---|
| 2 | off | 301 | 301 | 246 | 8 | 82% | 17 | 0.0 | 1527 | 100% |
| 2 | after 3 reads | 301 | 301 | 53 | 8 | 85% | 13 | 0.0 | 484 | 32% |
| 4 | off | 151 | 151 | 123 | 8 | 85% | 15 | 1.0 | 764 | 50% |
| 4 | after 3 reads | 151 | 151 | 29 | 8 | 86% | 11 | 1.0 | 256 | 17% |
| 8 | off | 76 | 76 | 63 | 8 | 84% | 17 | 3.0 | 390 | 26% |
| 8 | after 3 reads | 76 | 76 | 23 | 8 | 84% | 15 | 3.0 | 174 | 11% |
