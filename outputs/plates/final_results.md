# Plate reading: final comparison on the test split

1000 test images, one plate identity each. Thresholds chosen on validation. Fine-tuned = mean over seeds [42, 43, 44] (± std). Brackets = 95% bootstrap CI over images. A review request counts as not correct.

| Metric | Fine-tuned YOLO11n | From-scratch baseline |
|---|---|---|
| Full-plate exact match | 0.7063 ± 0.0037 [0.680, 0.731] | 0.0000 [0.000, 0.000] |
| Coverage (answered) | 0.9817 ± 0.0017 [0.974, 0.988] | 0.9020 [0.883, 0.921] |
| Accuracy when answered | 0.7195 ± 0.0025 [0.695, 0.744] | 0.0000 [0.000, 0.000] |
| Misread rate | 0.2753 ± 0.0021 [0.252, 0.299] | 0.9020 [0.883, 0.921] |
| Plate found | 0.9990 ± 0.0000 [0.997, 1.000] | 0.9960 [0.992, 1.000] |
| Emirate correct | 0.9687 ± 0.0019 [0.959, 0.977] | 0.7280 [0.701, 0.756] |
| Character error rate | 0.0857 ± 0.0015 [0.076, 0.096] | 0.6789 [0.666, 0.691] |
| Detection mAP50 | 0.8561 | 0.1836 |
| Detection mAP50-95 | 0.6540 | 0.1164 |
| Milliseconds per image | 12 | 11 |

## Fine-tuned model by emirate

| Emirate | Test images | Exact match | Misread rate |
|---|---|---|---|
| Dubai | 735 | 0.7333 | 0.2553 |
| Abu Dhabi | 135 | 0.6025 | 0.3679 |
| Sharjah | 55 | 0.7455 | 0.2364 |
| Fujairah | 48 | 0.6875 | 0.2917 |
| Ajman | 17 | 0.4902 | 0.3725 |
| Ras Al Khaimah | 10 | 0.3667 | 0.4667 |
