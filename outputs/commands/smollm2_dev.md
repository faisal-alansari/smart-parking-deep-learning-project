# Model C: smollm2 on dev

Time per command: 267 ms mean, 381 ms p95.

| slice | n | exact | dangerous | needless question | action | number | until |
|---|---|---|---|---|---|---|---|
| all | 60 | 0.583 | 0.283 | 0.147 | 0.794 | 0.853 | 0.618 |
| kind=allow | 26 | 0.500 | 0.308 | 0.192 | 0.731 | 0.808 | 0.500 |
| kind=remove | 8 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 |
| kind=review | 20 | 0.450 | 0.450 | - | - | - | - |
| kind=single_digit | 2 | 1.000 | 0.000 | - | - | - | - |
| kind=unsupported | 4 | 0.750 | 0.000 | - | - | - | - |
| reason=ambiguous_time | 3 | 1.000 | 0.000 | - | - | - | - |
| reason=invalid_number | 2 | 1.000 | 0.000 | - | - | - | - |
| reason=missing_number | 3 | 0.333 | 0.333 | - | - | - | - |
| reason=multiple_numbers | 2 | 0.000 | 0.500 | - | - | - | - |
| reason=time_in_past | 3 | 0.667 | 0.333 | - | - | - | - |
| reason=unclear_action | 4 | 0.000 | 1.000 | - | - | - | - |
| reason=unclear_time | 3 | 0.333 | 0.667 | - | - | - | - |
| reason=unsupported | 4 | 0.750 | 0.000 | - | - | - | - |
| wording=seen | 37 | 0.622 | 0.243 | 0.147 | 0.794 | 0.853 | 0.618 |
| bay said=False | 26 | 0.654 | 0.231 | 0.125 | 0.833 | 0.875 | 0.625 |
| bay said=True | 11 | 0.545 | 0.273 | 0.200 | 0.700 | 0.800 | 0.600 |
| slip=False | 59 | 0.593 | 0.271 | 0.147 | 0.794 | 0.853 | 0.618 |
| slip=True | 1 | 0.000 | 1.000 | - | - | - | - |

## Errors

- dev-001: "Okay and car number 37080 bay one for one week." expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 37080, until Sat 28 Nov 09:30
- dev-007: "Please let plate 35 in for today." expected PROPOSE ALLOW 35, until Tue 24 Nov 23:59; got PROPOSE REMOVE 35
- dev-009: "okay let car 626 in till tomorrow" expected PROPOSE ALLOW 626, until Wed 25 Nov 23:59; got PROPOSE ALLOW 626, permanent
- dev-010: "930 until tomorrow." expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 930, permanent
- dev-011: "allow thirty nine thousand three hundred twenty two until tomorrow at 9 pm" expected PROPOSE ALLOW 39322, until Wed 25 Nov 21:00; got NEEDS_REVIEW (multiple_numbers)
- dev-014: "allow number 47 until Saturday" expected PROPOSE ALLOW 47, until Sat 28 Nov 23:59; got PROPOSE ALLOW 47, permanent
- dev-015: "Approve plate 3526 till midnight." expected PROPOSE ALLOW 3526, until Wed 25 Nov 00:00; got PROPOSE ALLOW 3526, permanent
- dev-022: "Let car number 9873 in bay two until tomorrow please." expected PROPOSE ALLOW 9873, until Wed 25 Nov 23:59; got PROPOSE REMOVE 9873
- dev-023: "please add nine one six five two until tomorrow at one thirty pm" expected PROPOSE ALLOW 91652, until Wed 25 Nov 13:30; got NEEDS_REVIEW (time_in_past)
- dev-025: "Remove the car." expected NEEDS_REVIEW (missing_number); got NEEDS_REVIEW (invalid_number)
- dev-026: "Hello." expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- dev-031: "Add car 62680 and car 46149 until tomorrow." expected NEEDS_REVIEW (multiple_numbers); got PROPOSE ALLOW 62680, until Sun 22 Nov 23:59
- dev-035: "Car number 98331." expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 98331, permanent
- dev-036: "add number one three eight zero six for today" expected PROPOSE ALLOW 13806, until Tue 24 Nov 23:59; got PROPOSE ALLOW 13806, permanent
- dev-039: "Let number 14649 in until 7am." expected NEEDS_REVIEW (time_in_past); got PROPOSE ALLOW 14649, permanent
- dev-040: "Allow car number 69375 for bay 1 until tomorrow." expected PROPOSE ALLOW 69375, until Sun 22 Nov 23:59; got PROPOSE ALLOW 69375, permanent
- dev-041: "Please let plate five thousand four hundred eleven in till tomorrow at one thirty pm." expected PROPOSE ALLOW 5411, until Wed 25 Nov 13:30; got NEEDS_REVIEW (time_in_past)
- dev-044: "Allow 18 and one two five eight seven." expected NEEDS_REVIEW (multiple_numbers); got NEEDS_REVIEW (unclear_time)
- dev-045: "car 6846 in bay 2" expected NEEDS_REVIEW (unclear_action); got PROPOSE REMOVE 6846
- dev-046: "Allow plate 9008 until 10 pm." expected PROPOSE ALLOW 9008, until Tue 24 Nov 22:00; got PROPOSE ALLOW 9008, permanent
- dev-047: "Add plate number 91586 until tonight." expected NEEDS_REVIEW (unclear_time); got PROPOSE ALLOW 91586, permanent
- dev-048: "Approve plate number 7 6 2 3 in bay two." expected PROPOSE ALLOW 7623, permanent; got NEEDS_REVIEW (missing_number)
- dev-051: "allow number 7565 for a while" expected NEEDS_REVIEW (unclear_time); got PROPOSE ALLOW 7565, permanent
- dev-052: "add a car in bay 2" expected NEEDS_REVIEW (missing_number); got NEEDS_REVIEW (single_digit_number): ALLOW 2, permanent
- dev-057: "Let car number nine hundred eleven in for an hour for bay 1." expected PROPOSE ALLOW 911, until Sat 21 Nov 10:30; got NEEDS_REVIEW (unclear_time)
