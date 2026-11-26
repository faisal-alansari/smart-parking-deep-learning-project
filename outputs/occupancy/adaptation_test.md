# Model A adaptation: the one final test (chosen option: b_last_block)

Run once, after the choice on block 4; results accepted as they are. `before` = the model trained on public data only; `after` = the adapted model. Counts only.

## 1. Night video 3 (the sealed final test; a different night)

| model | frames | bay checks | balanced accuracy | parked cars missed | empty bays called occupied | F1 |
|---|---|---|---|---|---|---|
| before | all | 1142 | 0.9116 | 0 | 84 | 0.9408 |
| before | car just outside the right bay | 124 | 0.9111 | 0 | 16 | 0.8095 |
| before | normal | 620 | 0.9614 | 0 | 25 | 0.9595 |
| before | person in front of the plate | 30 | 0.5 | 0 | 0 | 1.0 |
| before | person in an empty bay | 34 | 0.5882 | 0 | 14 | 0.7083 |
| before | car across both bays | 192 | 0.5 | 0 | 0 | 1.0 |
| before | short stay (22 s) | 22 | 1.0 | 0 | 0 | 1.0 |
| before | crooked car | 66 | 0.5606 | 0 | 29 | 0.6947 |
| before | headlights on | 54 | 0.5 | 0 | 0 | 1.0 |
| after | all | 1142 | 0.8888 | 147 | 1 | 0.8754 |
| after | car just outside the right bay | 124 | 1.0 | 0 | 0 | 1.0 |
| after | normal | 620 | 0.9985 | 0 | 1 | 0.9983 |
| after | person in front of the plate | 30 | 0.5 | 0 | 0 | 1.0 |
| after | person in an empty bay | 34 | 1.0 | 0 | 0 | 1.0 |
| after | car across both bays | 192 | 0.1302 | 142 | 0 | 0.4132 |
| after | short stay (22 s) | 22 | 1.0 | 0 | 0 | 1.0 |
| after | crooked car | 66 | 0.9242 | 5 | 0 | 0.918 |
| after | headlights on | 54 | 0.5 | 0 | 0 | 1.0 |

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
