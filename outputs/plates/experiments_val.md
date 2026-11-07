# YOLO11n training-choice experiments (validation split, seed 42)

An option replaces the current choice only if val exact match rises by more than 0.005.
Exact match counts a review request as not correct.

| Stage | Option | Exact match | Coverage | Answered acc. | Misread rate | CER | mAP50 | Conf | Epochs | Minutes | Chosen |
|---|---|---|---|---|---|---|---|---|---|---|---|
| image_size | {'imgsz': 640} | 0.3480 | 0.9650 | 0.3606 | 0.6170 | 0.2586 | 0.6132 | 0.1 | 30 | 57 |  |
| image_size | {'imgsz': 960} | 0.6970 | 0.9810 | 0.7105 | 0.2840 | 0.0905 | 0.8379 | 0.2 | 30 | 110 | yes |
| adaptation | {'freeze': None} | 0.6970 | 0.9810 | 0.7105 | 0.2840 | 0.0905 | 0.8379 | 0.2 | 30 | 110 | yes |
| adaptation | {'freeze': 23} | 0.0380 | 0.7940 | 0.0479 | 0.7560 | 0.5436 | 0.3226 | 0.1 | 30 | 62 |  |
| train_size | {'train_size': 5000} | 0.6970 | 0.9810 | 0.7105 | 0.2840 | 0.0905 | 0.8379 | 0.2 | 30 | 110 | yes |
| train_size | {'train_size': 2500} | 0.5760 | 0.9780 | 0.5890 | 0.4020 | 0.1296 | 0.7233 | 0.1 | 30 | 57 |  |
| baseline_from_scratch | random init | 0.0010 | 0.9170 | 0.0011 | 0.9160 | 0.6762 | 0.1725 | 0.1 | 30 | 108 |  |

Selected: `{'imgsz': 960, 'freeze': None, 'train_size': 5000, 'seed42_run': 'exp_img960_full_n5000', 'baseline_run': 'exp_img960_full_n5000_scratch'}`
