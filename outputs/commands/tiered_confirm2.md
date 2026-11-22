# Model C: tiered on confirm2

Time per command: 147 ms mean, 429 ms p95.

| slice | n | exact | dangerous | needless question | action | number | until |
|---|---|---|---|---|---|---|---|
| all | 120 | 0.700 | 0.000 | 0.397 | 0.603 | 0.603 | 0.603 |
| kind=allow | 52 | 0.500 | 0.000 | 0.500 | 0.500 | 0.500 | 0.500 |
| kind=remove | 16 | 0.938 | 0.000 | 0.062 | 0.938 | 0.938 | 0.938 |
| kind=review | 40 | 0.825 | 0.000 | - | - | - | - |
| kind=single_digit | 4 | 0.750 | 0.000 | - | - | - | - |
| kind=unsupported | 8 | 0.875 | 0.000 | - | - | - | - |
| reason=ambiguous_time | 6 | 0.833 | 0.000 | - | - | - | - |
| reason=invalid_number | 4 | 1.000 | 0.000 | - | - | - | - |
| reason=missing_number | 6 | 0.667 | 0.000 | - | - | - | - |
| reason=multiple_numbers | 4 | 1.000 | 0.000 | - | - | - | - |
| reason=time_in_past | 6 | 0.833 | 0.000 | - | - | - | - |
| reason=unclear_action | 8 | 1.000 | 0.000 | - | - | - | - |
| reason=unclear_time | 6 | 0.500 | 0.000 | - | - | - | - |
| reason=unsupported | 8 | 0.875 | 0.000 | - | - | - | - |
| wording=seen | 74 | 0.622 | 0.000 | 0.397 | 0.603 | 0.603 | 0.603 |
| bay said=False | 46 | 0.783 | 0.000 | 0.244 | 0.756 | 0.756 | 0.756 |
| bay said=True | 28 | 0.357 | 0.000 | 0.630 | 0.370 | 0.370 | 0.370 |
| slip=False | 118 | 0.695 | 0.000 | 0.397 | 0.603 | 0.603 | 0.603 |
| slip=True | 2 | 1.000 | 0.000 | - | - | - | - |

## Errors

- confirm2-005: "Let car 65156 in for a while." expected NEEDS_REVIEW (unclear_time); got NEEDS_REVIEW (unsure)
- confirm2-006: "Please let 4931 in for bay 1." expected PROPOSE ALLOW 4931, permanent; got NEEDS_REVIEW (unsure)
- confirm2-011: "please add car 6020 bay 2 till tomorrow at 10am" expected PROPOSE ALLOW 6020, until Tue 01 Dec 10:00; got NEEDS_REVIEW (unsure)
- confirm2-016: "let car 28118 in" expected PROPOSE ALLOW 28118, permanent; got UNSUPPORTED
- confirm2-020: "Approve car 7 0 4 2 3 please." expected PROPOSE ALLOW 70423, permanent; got NEEDS_REVIEW (unsure)
- confirm2-021: "Allow car 6 2 5 4 1 until five fifteen pm bay one." expected PROPOSE ALLOW 62541, until Tue 24 Nov 17:15; got NEEDS_REVIEW (unsure)
- confirm2-024: "approve car number 1322 until tomorrow" expected PROPOSE ALLOW 1322, until Tue 01 Dec 23:59; got NEEDS_REVIEW (unsure)
- confirm2-027: "let plate 78329 in until tonight" expected NEEDS_REVIEW (unclear_time); got NEEDS_REVIEW (unclear_action)
- confirm2-030: "what's the weather today" expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- confirm2-031: "Let nine five four six three in." expected PROPOSE ALLOW 95463, permanent; got NEEDS_REVIEW (unsure)
- confirm2-032: "allow plate 2 5 5 1 2 in bay two please" expected PROPOSE ALLOW 25512, permanent; got NEEDS_REVIEW (unsure)
- confirm2-035: "Please allow plate seven hundred nineteen in bay two." expected PROPOSE ALLOW 719, permanent; got NEEDS_REVIEW (unclear_action)
- confirm2-038: "Let plate number 1964 in." expected PROPOSE ALLOW 1964, permanent; got NEEDS_REVIEW (unclear_action)
- confirm2-039: "hey let car number 9 6 5 in for bay one" expected PROPOSE ALLOW 965, permanent; got NEEDS_REVIEW (unsure)
- confirm2-046: "add plate five zero three one nine bay 2 please" expected PROPOSE ALLOW 50319, permanent; got NEEDS_REVIEW (unsure)
- confirm2-047: "Let car number sixty five oh seven in until 1:15 pm please." expected PROPOSE ALLOW 6507, until Tue 24 Nov 13:15; got NEEDS_REVIEW (unsure)
- confirm2-048: "Allow 3 until today bay 2." expected NEEDS_REVIEW (single_digit_number): ALLOW 3, until Tue 24 Nov 23:59; got NEEDS_REVIEW (unsure)
- confirm2-051: "add plate number five zero five four one in bay 2" expected PROPOSE ALLOW 50541, permanent; got NEEDS_REVIEW (unsure)
- confirm2-055: "Hey add plate number two zero nine eight zero until 11:30 p.m." expected PROPOSE ALLOW 20980, until Mon 30 Nov 23:30; got NEEDS_REVIEW (unsure)
- confirm2-057: "let car 36388 in till 4" expected NEEDS_REVIEW (ambiguous_time); got UNSUPPORTED
- confirm2-060: "take 2 3 5 4 2 off the list" expected PROPOSE REMOVE 23542; got NEEDS_REVIEW (missing_number)
- confirm2-064: "please let car one two six four two in bay 1" expected PROPOSE ALLOW 12642, permanent; got NEEDS_REVIEW (unsure)
- confirm2-065: "hey allow plate 95733 for bay 1 please" expected PROPOSE ALLOW 95733, permanent; got NEEDS_REVIEW (unsure)
- confirm2-066: "please approve four one nine one two in bay two till 23:15" expected PROPOSE ALLOW 41912, until Tue 24 Nov 23:15; got NEEDS_REVIEW (unsure)
- confirm2-068: "Let number 96 in till 10:30 am." expected NEEDS_REVIEW (time_in_past); got NEEDS_REVIEW (unclear_action)
- confirm2-075: "approve 63761 until tomorrow in bay 2" expected PROPOSE ALLOW 63761, until Wed 25 Nov 23:59; got NEEDS_REVIEW (unsure)
- confirm2-076: "please approve number 3400 until tomorrow at 5pm" expected PROPOSE ALLOW 3400, until Tue 01 Dec 17:00; got NEEDS_REVIEW (unsure)
- confirm2-081: "let plate number 341 in until tonight" expected NEEDS_REVIEW (unclear_time); got NEEDS_REVIEW (unclear_action)
- confirm2-083: "allow my brother's car" expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- confirm2-094: "let number 55 in for six days please" expected PROPOSE ALLOW 55, until Wed 09 Dec 17:55; got NEEDS_REVIEW (unsure)
- confirm2-097: "okay add number 91 in bay 1 please" expected PROPOSE ALLOW 91, permanent; got NEEDS_REVIEW (unsure)
- confirm2-098: "Please approve car two thousand one hundred seventy nine for a day in bay two." expected PROPOSE ALLOW 2179, until Tue 01 Dec 23:15; got NEEDS_REVIEW (unclear_time)
- confirm2-099: "Add car one five four eight six in bay one." expected PROPOSE ALLOW 15486, permanent; got NEEDS_REVIEW (unsure)
- confirm2-102: "Allow the car." expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- confirm2-114: "add 6 4 1 2 till tomorrow for bay 1 please" expected PROPOSE ALLOW 6412, until Tue 01 Dec 23:59; got NEEDS_REVIEW (unsure)
- confirm2-120: "Add plate 71559 in bay two please." expected PROPOSE ALLOW 71559, permanent; got NEEDS_REVIEW (unsure)
