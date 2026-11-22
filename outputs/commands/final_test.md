# Model C: the one final test (2026-11-22)

Frozen test set, 160 commands (95 clear changes, 55 to ask about, 10 other requests; 33 in
wording never seen in dev; 6 dictation slips). Each parser was run once with `--final`, after
the design was fixed on dev, check and the confirm sets and the owner approved the test
answers. Nothing was changed after this run. Full per-command reports: `<parser>_test.md`.

Selection rule (fixed before the test): 0 dangerous on dev, then the highest exact score.
Chosen Model C: **tiered** (the owner's fixed form first, then GLiNER + MiniLM with every
change checked by SmolLM2 and the safety checks). The test does not change that choice.

## Risk and coverage

"Dangerous" = a wrong change put to the owner. "Coverage" = clear commands answered with the
right change.

| parser | exact | changes proposed | right changes | wrong changes (dangerous) | clear commands answered (coverage) | needless questions | ms/command |
|---|---|---|---|---|---|---|---|
| rules | 103/160 (64%) | 67 | 64 | 3 (1.9%) | 64/95 (67%) | 28/95 | 0 |
| flan-t5 | 19/160 (12%) | 28 | 6 | 22 (13.8%) | 6/95 (6%) | 80/95 | 242 |
| smollm2 | 80/160 (50%) | 99 | 53 | 46 (28.7%) | 53/95 (56%) | 15/95 | 295 |
| gliner-minilm | 117/160 (73%) | 90 | 75 | 15 (9.4%) | 75/95 (79%) | 14/95 | 27 |
| checked | 78/160 (49%) | 36 | 35 | 1 (0.6%) | 35/95 (37%) | 59/95 | 142 |
| tiered | 80/160 (50%) | 37 | 36 | 1 (0.6%) | 36/95 (38%) | 58/95 | 123 |

## By slice (exact / dangerous)

| slice | n | rules | GLiNER + MiniLM | tiered (Model C) |
|---|---|---|---|---|
| wording seen in dev | 74 | 1.00 / 0.000 | 0.84 / 0.041 | 0.58 / 0.000 |
| wording never seen | 33 | 0.00 / 0.091 | 0.64 / 0.152 | 0.00 / 0.030 |
| bay said | 38 | 0.71 / 0.000 | 0.79 / 0.053 | 0.34 / 0.000 |
| dictation slip | 6 | 1.00 / 0.000 | 0.33 / 0.333 | 0.67 / 0.000 |
| to ask about | 49 | 0.67 / 0.000 | 0.67 / 0.122 | 0.78 / 0.000 |
| other request | 10 | 0.20 / 0.000 | 0.30 / 0.300 | 0.30 / 0.000 |

## What it means

- **Safety goal met on test, almost:** Model C put 1 wrong change to the owner out of 160
  (0.6%): "Don't allow car two eight anymore" was read as allow (a negation; both models and
  the rule parser fail on it). The rule parser made 3 such errors, GLiNER + MiniLM alone 15.
- **The price is coverage:** Model C answers only 38% of clear commands with a change; the rest
  get a question. On wording never seen in dev it answers none: the action-word check (set on
  dev wording) treats new verbs as unclear, so they are asked about. Safe, but the models'
  main strength (GLiNER + MiniLM alone answers 64% of new wording) is mostly given up.
- **Best accuracy, unsafe:** GLiNER + MiniLM alone is the most accurate (73% exact) but puts a
  wrong change to the owner 9.4% of the time.
- Dev and the confirm sets overstated Model C (dev 82%, confirm sets 70-78% exact), because
  they use dev wording only.
