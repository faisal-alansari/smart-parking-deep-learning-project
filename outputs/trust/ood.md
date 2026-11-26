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

The product uses the blocked, view and sharpness checks. The feature-distance bay check is reported but not used: on block 4 alone its held-out false-alarm rate was above the 2% limit (`validation_choices.md`). The sharpness check (frame sharpness divided by the snapshot's) was added after an earlier run on night 1 showed that heavy blur passes the view check. Night 3 is the sealed test: nothing here was chosen on it.

Cut-offs: view similarity below 0.725, sharpness ratio below 0.666, bay distance above 18.31; blocked: mean pixel value below 12 or above 243. One frame every 10 s. AUROC: how well each check separates these frames from the in-distribution test frames (1 = perfectly).

| frames | n | blocked | view check | sharpness check | product (blocked, view or sharpness) | bay check (not used) | view AUROC | sharpness AUROC | bay AUROC |
|---|---|---|---|---|---|---|---|---|---|
| in: night 2, block 4 (validation) | 74 | 0% | 1% | 1% | 3% | 1% |  |  |  |
| in: night 3 (test, its own snapshot) | 144 | 0% | 1% | 1% | 1% | 2% |  |  |  |
| out: other car parks (51 photos) | 51 | 0% | 90% | 31% | 94% | 18% | 0.996 | 0.552 | 0.79 |
| out: camera set up again, old snapshot (night 2 frames vs night 3 snapshot) | 25 | 0% | 8% | 8% | 8% | 0% | 0.965 | 0.7 | 0.569 |
| out: night 3, camera moved (shifted and zoomed) | 144 | 0% | 3% | 1% | 3% | 1% | 0.986 | 0.348 | 0.456 |
| out: night 3, heavy blur | 144 | 0% | 1% | 100% | 100% | 4% | 0.56 | 1.0 | 0.493 |
| out: night 3, over-exposed (x3) | 144 | 0% | 1% | 24% | 24% | 51% | 0.822 | 0.766 | 0.882 |
| out: night 3, lens almost covered | 144 | 100% | 1% | 1% | 100% | 100% | 0.766 | 0.023 | 0.999 |
| out: night 3, pure noise | 144 | 0% | 100% | 0% | 100% | 100% | 1.0 | 0.0 | 1.0 |
