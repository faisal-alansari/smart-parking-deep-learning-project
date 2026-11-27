# Model A adaptation: choosing on block 4 (validation)

Plan fixed before training (2026-11-25). Local crops from the owner's night video 2: blocks 1-3 train, block 4 chooses; moving periods left out. Each option is the majority vote of seeds 42, 43, 44. Allowed: no more parked cars missed than the current model (0) and public validation F1 at least 0.9843.

## Crops

| split | empty | occupied |
|---|---|---|
| train | 913 | 691 |
| validation | 227 | 373 |

## Options (block 4)

| option | balanced accuracy | parked cars missed | empty bays called occupied | F1 | public val F1 | allowed |
|---|---|---|---|---|---|---|
| current model (public data only) | 0.9097 | 0.0 | 41.0 | 0.9479 | 0.9943 | True |
| a_threshold | 0.9898 | 1.0 | 4.0 | 0.9933 | 0.9884 | False |
| b_last_block | 0.9956 | 0.0 | 2.0 | 0.9973 | 0.9846 | True |
| c_full_lr1e-4 | 0.9912 | 0.0 | 4.0 | 0.9947 | 0.9921 | True |
| c_full_lr3e-4 | 1.0 | 0.0 | 0.0 | 1.0 | 0.9836 | False |
| d_wide_scratch | 1.0 | 0.0 | 0.0 | 1.0 | 0.964 | False |

**Chosen: b_last_block**

## Each run

| run | best_epoch | threshold | block4_balanced | public_val_f1 | train_seconds |
|---|---|---|---|---|---|
| b_last_block_s42 | 8 | 0.9429 | 0.9916 | 0.9827 | 2.8 |
| b_last_block_s43 | 8 | 0.9518 | 0.9934 | 0.9815 | 2.3 |
| b_last_block_s44 | 6 | 0.942 | 1.0 | 0.984 | 2.4 |
| c_full_lr1e-4_s42 | 3 | 0.5 | 0.9912 | 0.9916 | 4.9 |
| c_full_lr1e-4_s43 | 7 | 0.5 | 0.9912 | 0.9925 | 4.2 |
| c_full_lr1e-4_s44 | 8 | 0.9205 | 1.0 | 0.9877 | 4.2 |
| c_full_lr3e-4_s42 | 4 | 0.7873 | 1.0 | 0.9902 | 4.2 |
| c_full_lr3e-4_s43 | 5 | 0.9725 | 1.0 | 0.9688 | 4.2 |
| c_full_lr3e-4_s44 | 2 | 0.9784 | 1.0 | 0.9798 | 4.2 |
| d_wide_scratch_s42 | 1 | 0.9844 | 1.0 | 0.9557 | 252.0 |
| d_wide_scratch_s43 | 1 | 0.1724 | 1.0 | 0.9745 | 243.1 |
| d_wide_scratch_s44 | 1 | 0.9957 | 1.0 | 0.9436 | 239.3 |
