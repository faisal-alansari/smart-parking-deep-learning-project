# Model C: oracle on test

Time per command: 0 ms mean, 0 ms p95.

| slice | n | exact | dangerous | needless question | action | number | until |
|---|---|---|---|---|---|---|---|
| all | 160 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 |
| kind=allow | 70 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 |
| kind=remove | 25 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 |
| kind=review | 49 | 1.000 | 0.000 | - | - | - | - |
| kind=single_digit | 6 | 1.000 | 0.000 | - | - | - | - |
| kind=unsupported | 10 | 1.000 | 0.000 | - | - | - | - |
| reason=ambiguous_time | 5 | 1.000 | 0.000 | - | - | - | - |
| reason=invalid_number | 5 | 1.000 | 0.000 | - | - | - | - |
| reason=missing_number | 8 | 1.000 | 0.000 | - | - | - | - |
| reason=multiple_numbers | 6 | 1.000 | 0.000 | - | - | - | - |
| reason=time_in_past | 5 | 1.000 | 0.000 | - | - | - | - |
| reason=unclear_action | 12 | 1.000 | 0.000 | - | - | - | - |
| reason=unclear_time | 8 | 1.000 | 0.000 | - | - | - | - |
| reason=unsupported | 10 | 1.000 | 0.000 | - | - | - | - |
| wording=seen | 74 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 |
| wording=unseen | 33 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 |
| bay said=False | 69 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 |
| bay said=True | 38 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 |
| slip=False | 154 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 |
| slip=True | 6 | 1.000 | 0.000 | - | - | - | - |

## Errors

None.
