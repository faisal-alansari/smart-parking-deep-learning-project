# Occupancy data report (CNRPark+EXT)

Total crops: 157549

| Status | Crops |
|---|---|
| kept | 86294 |
| near_copy | 37062 |
| not_sampled | 33424 |
| too_dark_to_verify | 704 |
| blank_image | 39 |
| label_conflict | 26 |

| Split | Crops | Free | Busy | Free share | Cameras | Days |
|---|---|---|---|---|---|---|
| train | 40000 | 20000 | 20000 | 50% | C01, C03, C04, C05, C06, C07, C08, C09 | 15 |
| val | 12714 | 4507 | 8207 | 35% | C01, C03, C04, C05, C06, C07, C08, C09 | 3 |
| test | 23589 | 11938 | 11651 | 51% | C01, C03, C04, C05, C06, C07, C08, C09 | 5 |
| test_unseen_camera | 2902 | 1183 | 1719 | 41% | C02 | 23 |
| test_unseen_site | 7089 | 3129 | 3960 | 44% | A, B | 2 |

Fine-tuning items used: 0 (Occupancy model is trained from scratch; its data is outside the cap.)
