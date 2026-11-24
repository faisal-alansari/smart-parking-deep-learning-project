# Unfamiliar inputs (OOD) and abstention

Model A is adapted to the owner's camera, so the product must notice frames that do not look
like it. Three tiers, cheapest first:
1. **blocked camera** (fixed rule): a nearly black or white frame;
2. **view check**: the background of the frame (everything outside the two bay boxes, small and
   grey) is compared with a snapshot taken when the camera was set up (Pearson correlation).
   Cars come and go inside the bays, but another car park, a moved camera, a blurred or noisy
   lens all change the background;
   **sharpness check**: the frame's sharpness against the snapshot's (a blurred lens);
3. **bay check** (evaluated, not used): the Mahalanobis distance of each bay crop's Model A
   features (the pooled last conv layer of the first deployed seed) from the training crops
   (night video 2, blocks 1-3).
Cut-offs come from block 4 (validation, in-distribution): the view check flags the lowest 1% of
its similarities, the bay check the highest 1% of its distances. Evaluated on frames of the other
night (in-distribution, test) against other car parks, a moved camera, a camera set up again
without a new snapshot, and corrupted frames. An unfamiliar frame returns NEEDS_REVIEW for both
bays with the reason (`camera_blocked`, `unfamiliar_view` or `blurred_view`): the product never
guesses on a view it does not know.

After the first run the bay check flagged 13% of normal frames on the other night (1% on block 4): its cut-off is tuned to the training night, the same lesson as calibration. The product therefore uses the blocked, view and sharpness checks; the bay check is reported but not used (a choice informed by the test). The sharpness check (frame sharpness divided by the snapshot's) was added after the first run showed that heavy blur passes the view check.

Cut-offs: view similarity below 0.725, sharpness ratio below 0.629, bay distance above 18.31; blocked: mean pixel value below 12 or above 243. One frame every 10 s. AUROC: how well each check separates these frames from the in-distribution test frames (1 = perfectly).

| frames | n | blocked | view check | sharpness check | product (blocked, view or sharpness) | bay check (not used) | view AUROC | sharpness AUROC | bay AUROC |
|---|---|---|---|---|---|---|---|---|---|
| in: night 2, block 4 (validation) | 74 | 0% | 1% | 1% | 3% | 1% |  |  |  |
| in: night 1 (test, its own snapshot) | 61 | 0% | 2% | 3% | 5% | 13% |  |  |  |
| out: other car parks (51 photos) | 51 | 0% | 90% | 18% | 92% | 18% | 0.995 | 0.341 | 0.658 |
| out: camera set up again, old snapshot (night 2 vs night 1) | 25 | 0% | 88% | 0% | 88% | 8% | 0.991 | 0.146 | 0.632 |
| out: night 1, camera moved (shifted and zoomed) | 61 | 0% | 98% | 2% | 98% | 13% | 0.999 | 0.347 | 0.46 |
| out: night 1, heavy blur | 61 | 0% | 2% | 100% | 100% | 13% | 0.538 | 1.0 | 0.659 |
| out: night 1, over-exposed (x3) | 61 | 2% | 13% | 11% | 23% | 34% | 0.821 | 0.22 | 0.711 |
| out: night 1, lens almost covered | 61 | 100% | 2% | 100% | 100% | 100% | 0.636 | 1.0 | 1.0 |
| out: night 1, pure noise | 61 | 0% | 100% | 0% | 100% | 100% | 1.0 | 0.066 | 1.0 |
