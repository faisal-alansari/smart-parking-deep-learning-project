# AddingUAE plate data audit

Images: 9985. Boxes: 86294. Exact duplicate images: 0.

| Split | Images | Plate boxes | Plates with characters |
|---|---|---|---|
| train | 6990 | 8705 | 7742 |
| valid | 1997 | 2518 | 2263 |
| test | 998 | 1245 | 1101 |

## Image kinds

| Kind | Images |
|---|---|
| car_photo | 9442 |
| plate_only_no_plate_box | 359 |
| plate_closeup | 184 |

## Label check against file names (file name = main plate text)

Plate-style file names: 9135. exact: 8619 (94.4%), no_chars: 331 (3.6%), partial: 185 (2.0%)

Character or type boxes outside any plate box: 2404. Plate boxes without characters: 1362. Plate boxes without an emirate/type box: 1921.

## Leakage between the export's splits

- Plate identities: 9688; with several images: 272; in several splits: 118 (254 images).
- Near-duplicate image pairs: 2047; across splits: 859; of which car photos: 42.

## Plate types (emirate and style)

| Type | Plates |
|---|---|
| old_DUBAI | 5036 |
| new_DUBAI | 2840 |
| old_abudabi | 888 |
| old_sharka | 642 |
| old_fujira | 424 |
| new_abudabi | 258 |
| old_ajman | 130 |
| old_RAK | 111 |
| old_am | 68 |
| new_RAK | 66 |
| new_ajman | 45 |
| new_am | 27 |
| new_fujairah | 11 |
| exp | 1 |

Rare classes (< 100 boxes): {'exp': 3, 'Z': 7, 'Y': 15, 'new_fujairah': 17, 'new_am': 29, 'new_ajman': 50, 'X': 67, 'new_RAK': 74}

Character height in pixels (quantiles): {'0.05': 16.0, '0.25': 27.0, '0.5': 34.0, '0.75': 41.5, '0.95': 55.5}
