# Model C: oracle on confirm3

Time per command: 0 ms mean, 0 ms p95.

| slice | n | exact | dangerous | needless question | action | number | until |
|---|---|---|---|---|---|---|---|
| all | 120 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 |
| kind=allow | 52 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 |
| kind=remove | 16 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 |
| kind=review | 40 | 1.000 | 0.000 | - | - | - | - |
| kind=single_digit | 4 | 1.000 | 0.000 | - | - | - | - |
| kind=unsupported | 8 | 1.000 | 0.000 | - | - | - | - |
| reason=ambiguous_time | 6 | 1.000 | 0.000 | - | - | - | - |
| reason=invalid_number | 4 | 1.000 | 0.000 | - | - | - | - |
| reason=missing_number | 6 | 1.000 | 0.000 | - | - | - | - |
| reason=multiple_numbers | 4 | 1.000 | 0.000 | - | - | - | - |
| reason=time_in_past | 6 | 1.000 | 0.000 | - | - | - | - |
| reason=unclear_action | 8 | 1.000 | 0.000 | - | - | - | - |
| reason=unclear_time | 6 | 1.000 | 0.000 | - | - | - | - |
| reason=unsupported | 8 | 1.000 | 0.000 | - | - | - | - |
| wording=seen | 74 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 |
| bay said=False | 58 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 |
| bay said=True | 16 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 |
| slip=False | 118 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 |
| slip=True | 2 | 1.000 | 0.000 | - | - | - | - |

## Errors

None.
