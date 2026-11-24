# Model A adaptation: the one final test (chosen option: b_last_block)

Run once, after the choice on block 4; results accepted as they are. `before` = the model trained on public data only; `after` = the adapted model. Counts only.

## 1. The first night video (the final test; a different night)

| model | frames | bay checks | balanced accuracy | parked cars missed | empty bays called occupied | F1 |
|---|---|---|---|---|---|---|
| before | all | 486 | 0.8395 | 0 | 78 | 0.8617 |
| before | car across both bays | 124 | 0.5 | 0 | 0 | 1.0 |
| before | normal | 362 | 0.8395 | 0 | 78 | 0.7532 |
| after | all | 486 | 0.893 | 50 | 2 | 0.8813 |
| after | car across both bays | 124 | 0.2984 | 50 | 0 | 0.7475 |
| after | normal | 362 | 0.9959 | 0 | 2 | 0.9917 |

## 2. Public test sets

| split | model | F1 | accuracy |
|---|---|---|---|
| test | before | 0.9937 | 0.9938 |
| test | after | 0.9877 | 0.988 |
| test_unseen_camera | before | 0.989 | 0.9869 |
| test_unseen_camera | after | 0.9853 | 0.9828 |
| test_unseen_site | before | 0.9323 | 0.925 |
| test_unseen_site | after | 0.8571 | 0.8588 |

## 3. Local photos (other car parks; check only)

| photos | model | bays | balanced accuracy | parked cars missed | empty bays called occupied | F1 |
|---|---|---|---|---|---|---|
| pilot | before | 16 | 0.9375 | 0 | 1 | 0.9412 |
| pilot | after | 16 | 1.0 | 0 | 0 | 1.0 |
| night_1 | before | 86 | 0.7076 | 6 | 20 | 0.7234 |
| night_1 | after | 86 | 0.7457 | 16 | 5 | 0.6957 |
