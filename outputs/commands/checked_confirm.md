# Model C: checked on confirm

Time per command: 187 ms mean, 408 ms p95.

| slice | n | exact | dangerous | needless question | action | number | until |
|---|---|---|---|---|---|---|---|
| all | 120 | 0.700 | 0.025 | 0.338 | 0.662 | 0.662 | 0.647 |
| kind=allow | 52 | 0.538 | 0.019 | 0.442 | 0.558 | 0.558 | 0.538 |
| kind=remove | 16 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 |
| kind=review | 40 | 0.725 | 0.050 | - | - | - | - |
| kind=single_digit | 4 | 0.750 | 0.000 | - | - | - | - |
| kind=unsupported | 8 | 1.000 | 0.000 | - | - | - | - |
| reason=ambiguous_time | 6 | 0.833 | 0.000 | - | - | - | - |
| reason=invalid_number | 4 | 1.000 | 0.000 | - | - | - | - |
| reason=missing_number | 6 | 0.500 | 0.000 | - | - | - | - |
| reason=multiple_numbers | 4 | 0.750 | 0.000 | - | - | - | - |
| reason=time_in_past | 6 | 1.000 | 0.000 | - | - | - | - |
| reason=unclear_action | 8 | 0.625 | 0.250 | - | - | - | - |
| reason=unclear_time | 6 | 0.500 | 0.000 | - | - | - | - |
| reason=unsupported | 8 | 1.000 | 0.000 | - | - | - | - |
| wording=seen | 74 | 0.635 | 0.027 | 0.338 | 0.662 | 0.662 | 0.647 |
| bay said=False | 55 | 0.727 | 0.036 | 0.224 | 0.776 | 0.776 | 0.755 |
| bay said=True | 19 | 0.368 | 0.000 | 0.632 | 0.368 | 0.368 | 0.368 |
| slip=False | 118 | 0.712 | 0.017 | 0.338 | 0.662 | 0.662 | 0.647 |
| slip=True | 2 | 0.000 | 0.500 | - | - | - | - |

## Errors

- confirm-003: "add plate number forty one eighty seven for bay 2" expected PROPOSE ALLOW 4187, permanent; got NEEDS_REVIEW (unsure)
- confirm-006: "approve car fifty two thousand thirty for 45 minutes" expected PROPOSE ALLOW 52030, until Sat 28 Nov 07:30; got NEEDS_REVIEW (unsure)
- confirm-012: "Please let car number ninety six thousand seven hundred sixty three in for two hours." expected PROPOSE ALLOW 96763, until Mon 23 Nov 14:35; got NEEDS_REVIEW (unsure)
- confirm-014: "Let plate number 720 in until 8 PM." expected PROPOSE ALLOW 720, until Tue 01 Dec 20:00; got NEEDS_REVIEW (unsure)
- confirm-020: "Allow my brother's car." expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- confirm-021: "8 5 7 8 5 until tomorrow." expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 85785, until Tue 24 Nov 23:59
- confirm-027: "Add car number sixteen thousand seven hundred forty one for 2 days please." expected PROPOSE ALLOW 16741, until Wed 25 Nov 12:35; got NEEDS_REVIEW (unsure)
- confirm-028: "Add car 7093 for bay 1 for a week." expected PROPOSE ALLOW 7093, until Tue 08 Dec 19:30; got NEEDS_REVIEW (unclear_time)
- confirm-033: "please let number one one eight in until noon" expected PROPOSE ALLOW 118, until Sat 28 Nov 12:00; got NEEDS_REVIEW (unsure)
- confirm-037: "Add seven three four six three until tomorrow at 4:30 PM please." expected PROPOSE ALLOW 73463, until Tue 24 Nov 16:30; got PROPOSE ALLOW 73463, until Mon 23 Nov 16:30
- confirm-042: "let car number seventeen oh four in until tonight" expected NEEDS_REVIEW (unclear_time); got NEEDS_REVIEW (unclear_action)
- confirm-043: "allow car 9634 until 7:30 a.m. tomorrow" expected PROPOSE ALLOW 9634, until Tue 24 Nov 07:30; got NEEDS_REVIEW (time_in_past)
- confirm-047: "Okay let plate number 407 in for bay two till tomorrow." expected PROPOSE ALLOW 407, until Tue 24 Nov 23:59; got NEEDS_REVIEW (unclear_action)
- confirm-048: "okay let five zero five in for bay two" expected PROPOSE ALLOW 505, permanent; got NEEDS_REVIEW (unsure)
- confirm-050: "allow ninety five eighty three and six three four three" expected NEEDS_REVIEW (multiple_numbers); got NEEDS_REVIEW (unsure)
- confirm-059: "Let plate 5539 in till tomorrow." expected PROPOSE ALLOW 5539, until Wed 02 Dec 23:59; got NEEDS_REVIEW (unsure)
- confirm-060: "Hey add car number 36933 in bay two." expected PROPOSE ALLOW 36933, permanent; got NEEDS_REVIEW (unsure)
- confirm-062: "Please approve car number twenty thousand six hundred fifty seven." expected PROPOSE ALLOW 20657, permanent; got NEEDS_REVIEW (unsure)
- confirm-063: "Add plate 3603 until 21:30 bay 1 please." expected PROPOSE ALLOW 3603, until Sat 28 Nov 21:30; got NEEDS_REVIEW (unsure)
- confirm-066: "Please add plate number 92142 for bay two." expected PROPOSE ALLOW 92142, permanent; got NEEDS_REVIEW (unsure)
- confirm-077: "hey approve car 6 7 9 4 2 for bay two until 12 PM tomorrow" expected PROPOSE ALLOW 67942, until Wed 02 Dec 12:00; got NEEDS_REVIEW (missing_number)
- confirm-078: "Hey add plate 1 until tomorrow six p.m." expected NEEDS_REVIEW (single_digit_number): ALLOW 1, until Tue 24 Nov 18:00; got NEEDS_REVIEW (unsure)
- confirm-082: "Please and car 897 till tomorrow." expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 897, until Sun 29 Nov 23:59
- confirm-084: "Allow plate one four four until tomorrow." expected PROPOSE ALLOW 144, until Sun 29 Nov 23:59; got NEEDS_REVIEW (unsure)
- confirm-085: "hey let plate number six thousand one hundred fifty in" expected PROPOSE ALLOW 6150, permanent; got NEEDS_REVIEW (unsure)
- confirm-089: "Let 239 in until Saturday." expected NEEDS_REVIEW (unclear_time); got NEEDS_REVIEW (unclear_action)
- confirm-091: "let plate 5477 in for a while" expected NEEDS_REVIEW (unclear_time); got NEEDS_REVIEW (unsure)
- confirm-096: "allow the car" expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- confirm-097: "let car number 3828 in for bay one" expected PROPOSE ALLOW 3828, permanent; got NEEDS_REVIEW (unclear_action)
- confirm-104: "let car number 50925 in" expected PROPOSE ALLOW 50925, permanent; got NEEDS_REVIEW (unsure)
- confirm-108: "Okay allow car number 33734 for bay two." expected PROPOSE ALLOW 33734, permanent; got NEEDS_REVIEW (unsure)
- confirm-112: "add number 5 7 2 1 until tomorrow ten pm bay 2 please" expected PROPOSE ALLOW 5721, until Wed 02 Dec 22:00; got NEEDS_REVIEW (unsure)
- confirm-114: "Allow number 3 7 3 till tomorrow at 8." expected NEEDS_REVIEW (ambiguous_time); got NEEDS_REVIEW (unsure)
- confirm-115: "Hey and number nine six two nine for one day." expected NEEDS_REVIEW (unclear_action); got NEEDS_REVIEW (unsure)
- confirm-117: "Allow the car until 23:30." expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- confirm-120: "Add 36469 till tomorrow 1:15 pm bay one." expected PROPOSE ALLOW 36469, until Wed 02 Dec 13:15; got NEEDS_REVIEW (unsure)
