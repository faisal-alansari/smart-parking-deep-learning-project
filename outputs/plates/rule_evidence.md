# Evidence for the plate reader rules

Reproduce with `just plate-rule-evidence`. Validation only; test not used.

## Labels (train + val)

- Same-row character pairs inside a plate: 81,622.
- Pairs whose sideways overlap is more than a share of the narrower box: > 70%: 16 | > 60%: 22 | > 50%: 36 | > 40%: 178.
- Dubai main plates (the plate named in the file): 4,302; without a code letter: 0.
- Other Dubai plates (smaller, in the background): 500; without a code letter: 98. Many of these have only some characters labelled.

## Validation (final seed 42, its threshold, same detections for every row)

| setting | exact match | answered | accuracy when answered | misread |
|---|---|---|---|---|
| rules off (before) | 0.697 | 0.981 | 0.710 | 0.284 |
| merge only, cut-off 70% | 0.709 | 0.983 | 0.721 | 0.274 |
| merge only, cut-off 60% | 0.714 | 0.983 | 0.726 | 0.269 |
| merge only, cut-off 50% | 0.719 | 0.983 | 0.731 | 0.264 |
| merge only, cut-off 40% | 0.718 | 0.983 | 0.730 | 0.265 |
| code-letter rule only | 0.697 | 0.919 | 0.758 | 0.222 |
| both rules, cut-off 50% (after) | 0.719 | 0.921 | 0.781 | 0.202 |
