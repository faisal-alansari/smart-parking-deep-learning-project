# Plate reading: final comparison on the test split

1000 test images, one plate identity each. Thresholds chosen on validation. Fine-tuned = mean over seeds [42, 43, 44] (± std). Brackets = 95% bootstrap CI over images. A review request counts as not correct.

| Metric | Fine-tuned YOLO11n | From-scratch baseline |
|---|---|---|
| Full-plate exact match | 0.7283 ± 0.0021 [0.702, 0.752] | 0.0000 [0.000, 0.000] |
| Coverage (answered) | 0.9207 ± 0.0058 [0.906, 0.935] | 0.1360 [0.114, 0.158] |
| Accuracy when answered | 0.7911 ± 0.0029 [0.767, 0.813] | 0.0000 [0.000, 0.000] |
| Misread rate | 0.1923 ± 0.0039 [0.172, 0.214] | 0.1360 [0.114, 0.158] |
| Plate found | 0.9990 ± 0.0000 [0.997, 1.000] | 0.9960 [0.992, 1.000] |
| Emirate correct | 0.9687 ± 0.0019 [0.959, 0.977] | 0.7280 [0.701, 0.756] |
| Character error rate | 0.0803 ± 0.0013 [0.071, 0.091] | 0.6722 [0.659, 0.685] |
| Detection mAP50 | 0.8561 | 0.1836 |
| Detection mAP50-95 | 0.6540 | 0.1164 |
| Milliseconds per image | 12 | 12 |

## Fine-tuned model by emirate

| Emirate | Test images | Exact match | Misread rate |
|---|---|---|---|
| Dubai | 735 | 0.7551 | 0.1578 |
| Abu Dhabi | 135 | 0.6296 | 0.3383 |
| Sharjah | 55 | 0.7758 | 0.1939 |
| Fujairah | 48 | 0.7014 | 0.2222 |
| Ajman | 17 | 0.4902 | 0.3137 |
| Ras Al Khaimah | 10 | 0.3667 | 0.4000 |
