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

## Fine-tuning items (cap 10,000)

| items | count |
|---|---|
| plate images used to fine-tune YOLO11n (train, validation and test) | 7000 |
| local bay crops used to adapt Model A (night 2) and test it (night 1); scratch-model data, counted here to be safe | 2690 |
| total | 9690 |
