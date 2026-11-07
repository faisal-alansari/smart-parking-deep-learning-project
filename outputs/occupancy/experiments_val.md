# OccupancyCNN training-choice experiments (validation split, seed 42)

An option replaces the current choice only if val F1 rises by > 0.002.

| Stage | Option | Val F1 | Recall | Precision | FPR | Accuracy | Best epoch | Seconds | Chosen |
|---|---|---|---|---|---|---|---|---|---|
| learning_rate | lr-0.0003 | 0.9908 | 0.9889 | 0.9928 | 0.0131 | 0.9882 | 15 | 69.7 |  |
| learning_rate | lr-0.001 | 0.9934 | 0.9915 | 0.9954 | 0.0084 | 0.9915 | 13 | 68.4 | yes |
| learning_rate | lr-0.003 | 0.9946 | 0.9918 | 0.9973 | 0.0049 | 0.9930 | 15 | 68.5 |  |
| augmentation | augment-none | 0.9918 | 0.9913 | 0.9922 | 0.0142 | 0.9894 | 14 | 65.5 |  |
| augmentation | augment-photo | 0.9934 | 0.9915 | 0.9954 | 0.0084 | 0.9915 | 13 | 68.4 | yes |
| augmentation | augment-photo_hflip | 0.9920 | 0.9909 | 0.9932 | 0.0124 | 0.9897 | 15 | 69.1 |  |
| regularization | weight_decay-0.0_dropout-0.0 | 0.9941 | 0.9922 | 0.9961 | 0.0071 | 0.9924 | 15 | 71.3 |  |
| regularization | weight_decay-0.0001_dropout-0.3 | 0.9934 | 0.9915 | 0.9954 | 0.0084 | 0.9915 | 13 | 68.4 | yes |
| regularization | weight_decay-0.001_dropout-0.5 | 0.9938 | 0.9918 | 0.9957 | 0.0078 | 0.9920 | 15 | 67.2 |  |
| input_size | input_size-64 | 0.9934 | 0.9915 | 0.9954 | 0.0084 | 0.9915 | 13 | 68.4 | yes |
| input_size | input_size-96 | 0.9924 | 0.9905 | 0.9944 | 0.0102 | 0.9902 | 15 | 155.3 |  |

Selected settings: `{'lr': 0.001, 'augment': 'photo', 'weight_decay': 0.0001, 'dropout': 0.3, 'input_size': 64}`
