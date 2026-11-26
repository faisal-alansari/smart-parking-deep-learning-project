# Parameter budget and fine-tuning items

Counted from the loaded models.

| model | role | training | parameters | limit | within limit |
|---|---|---|---|---|---|
| A occupancy (OccupancyCNN) | camera: is each bay occupied | trained from scratch | 294,129 | 50M | True |
| B plate reader (YOLO11n) | camera: plate, characters and emirate in the bay | pretrained (COCO), fine-tuned | 2,616,304 | 200M | True |
| C1 GLiNER small v2.1 (DeBERTa-v3-small) | text: plate number and end time in a command | pretrained, not fine-tuned | 152,648,704 | 200M | True |
| C2 all-MiniLM-L6-v2 | text: allow, remove or other (closest examples) | pretrained, not fine-tuned | 22,713,216 | 200M | True |
| C3 SmolLM2-135M-Instruct | text: second opinion on action and number | pretrained, not fine-tuned | 134,515,008 | 200M | True |

Pretrained and fine-tuned models together: 312,493,232 parameters (limit 1,000,000,000): within the limit.

## Evaluated but not deployed, and the deployed ensemble

| model | role | parameters |
|---|---|---|
| A as deployed: majority vote of 3 seeds | 3 copies of Model A in memory | 882,387 |
| A option d: wider OccupancyCNN (32-64-128-256) | adaptation candidate, rejected | 1,173,473 |
| B baseline: YOLO11n from random weights | from-scratch plate baseline | 2,616,304 |
| C candidate: FLAN-T5-small | Model C candidate, rejected on dev | 76,961,152 |

## Fine-tuning items (cap 10,000)

| items | count | counted |
|---|---|---|
| plate images used to fine-tune YOLO11n (train and validation) | 6000 | yes |
| local bay crops used to adapt Model A (night 2, train and validation); scratch-model data, counted here to be safe | 2204 | yes |
| total counted against the cap | 8204 |  |
| test only, never learned from: plate test images | 1000 | no |
| test only, never learned from: local bay crops (nights 1 and 3) | 1628 | no |
