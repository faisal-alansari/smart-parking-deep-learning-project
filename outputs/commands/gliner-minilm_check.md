# Model C: gliner-minilm on check

Time per command: 24 ms mean, 33 ms p95.

| slice | n | exact | dangerous | needless question | action | number | until |
|---|---|---|---|---|---|---|---|
| all | 120 | 0.808 | 0.058 | 0.118 | 0.853 | 0.882 | 0.868 |
| kind=allow | 52 | 0.827 | 0.058 | 0.115 | 0.846 | 0.885 | 0.865 |
| kind=remove | 16 | 0.875 | 0.000 | 0.125 | 0.875 | 0.875 | 0.875 |
| kind=review | 40 | 0.725 | 0.100 | - | - | - | - |
| kind=single_digit | 4 | 1.000 | 0.000 | - | - | - | - |
| kind=unsupported | 8 | 0.875 | 0.000 | - | - | - | - |
| reason=ambiguous_time | 6 | 0.333 | 0.167 | - | - | - | - |
| reason=invalid_number | 4 | 1.000 | 0.000 | - | - | - | - |
| reason=missing_number | 6 | 0.500 | 0.000 | - | - | - | - |
| reason=multiple_numbers | 4 | 0.750 | 0.250 | - | - | - | - |
| reason=time_in_past | 6 | 1.000 | 0.000 | - | - | - | - |
| reason=unclear_action | 8 | 0.625 | 0.250 | - | - | - | - |
| reason=unclear_time | 6 | 1.000 | 0.000 | - | - | - | - |
| reason=unsupported | 8 | 0.875 | 0.000 | - | - | - | - |
| wording=seen | 74 | 0.824 | 0.068 | 0.118 | 0.853 | 0.882 | 0.868 |
| bay said=False | 56 | 0.821 | 0.089 | 0.100 | 0.860 | 0.900 | 0.880 |
| bay said=True | 18 | 0.833 | 0.000 | 0.167 | 0.833 | 0.833 | 0.833 |
| slip=False | 118 | 0.822 | 0.042 | 0.118 | 0.853 | 0.882 | 0.868 |
| slip=True | 2 | 0.000 | 1.000 | - | - | - | - |

## Errors

- check-002: "allow plate four thousand three hundred two till 2:30" expected NEEDS_REVIEW (ambiguous_time); got NEEDS_REVIEW (missing_number)
- check-004: "Allow the car until eight pm." expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- check-005: "allow my brother's car" expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- check-007: "Let plate 23745 in until today." expected PROPOSE ALLOW 23745, until Wed 25 Nov 23:59; got NEEDS_REVIEW (unclear_action)
- check-013: "Let car eleven thousand four hundred eighteen in till four." expected NEEDS_REVIEW (ambiguous_time); got UNSUPPORTED
- check-014: "Okay let plate 223 in for today." expected PROPOSE ALLOW 223, until Wed 25 Nov 23:59; got NEEDS_REVIEW (unclear_action)
- check-023: "Allow the car." expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- check-032: "Allow 3 3 and 3293." expected NEEDS_REVIEW (multiple_numbers); got PROPOSE ALLOW 3293, permanent
- check-041: "Approve car five two four seven three till 7." expected NEEDS_REVIEW (ambiguous_time); got PROPOSE ALLOW 52473, permanent
- check-042: "What's the weather today?" expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- check-046: "Hey let plate number 381 in till Wednesday." expected PROPOSE ALLOW 381, until Wed 02 Dec 23:59; got NEEDS_REVIEW (unclear_action)
- check-050: "Let plate number ninety three thousand one hundred ninety one in till tomorrow at 5." expected NEEDS_REVIEW (ambiguous_time); got NEEDS_REVIEW (missing_number)
- check-057: "let 1 9 2 9 in for a week" expected PROPOSE ALLOW 1929, until Wed 02 Dec 16:20; got PROPOSE ALLOW 1929, permanent
- check-075: "Car number fifty four thirty eight." expected NEEDS_REVIEW (unclear_action); got UNSUPPORTED
- check-080: "Take plate number 5 7 7 9 5 off the list from bay 1." expected PROPOSE REMOVE 57795; got NEEDS_REVIEW (unclear_action)
- check-081: "Please let number nine three two in." expected PROPOSE ALLOW 932, permanent; got PROPOSE REMOVE 932
- check-083: "let plate number 86422 in till 10:15 pm tonight" expected PROPOSE ALLOW 86422, until Wed 25 Nov 22:15; got NEEDS_REVIEW (unclear_action)
- check-087: "delete fifty seven thousand five hundred fifty five" expected PROPOSE REMOVE 57555; got NEEDS_REVIEW (missing_number)
- check-088: "Let plate 2 0 9 1 3 in for a week for bay 2 please." expected PROPOSE ALLOW 20913, until Wed 02 Dec 16:20; got NEEDS_REVIEW (unclear_time)
- check-095: "please and number 1 3 8" expected NEEDS_REVIEW (unclear_action); got PROPOSE REMOVE 138
- check-106: "let 193 in for one week in bay two please" expected PROPOSE ALLOW 193, until Sun 29 Nov 07:50; got NEEDS_REVIEW (unclear_action)
- check-111: "Hey and 5585 until tomorrow 9PM please." expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 5585, until Sat 28 Nov 21:00
- check-112: "Approve plate nine zero zero." expected PROPOSE ALLOW 900, permanent; got PROPOSE REMOVE 900
