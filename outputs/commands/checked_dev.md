# Model C: checked on dev

Time per command: 148 ms mean, 362 ms p95.

| slice | n | exact | dangerous | needless question | action | number | until |
|---|---|---|---|---|---|---|---|
| all | 60 | 0.600 | 0.000 | 0.529 | 0.471 | 0.471 | 0.471 |
| kind=allow | 26 | 0.346 | 0.000 | 0.654 | 0.346 | 0.346 | 0.346 |
| kind=remove | 8 | 0.875 | 0.000 | 0.125 | 0.875 | 0.875 | 0.875 |
| kind=review | 20 | 0.700 | 0.000 | - | - | - | - |
| kind=single_digit | 2 | 1.000 | 0.000 | - | - | - | - |
| kind=unsupported | 4 | 1.000 | 0.000 | - | - | - | - |
| reason=ambiguous_time | 3 | 0.667 | 0.000 | - | - | - | - |
| reason=invalid_number | 2 | 1.000 | 0.000 | - | - | - | - |
| reason=missing_number | 3 | 0.333 | 0.000 | - | - | - | - |
| reason=multiple_numbers | 2 | 0.500 | 0.000 | - | - | - | - |
| reason=time_in_past | 3 | 1.000 | 0.000 | - | - | - | - |
| reason=unclear_action | 4 | 0.750 | 0.000 | - | - | - | - |
| reason=unclear_time | 3 | 0.667 | 0.000 | - | - | - | - |
| reason=unsupported | 4 | 1.000 | 0.000 | - | - | - | - |
| wording=seen | 37 | 0.514 | 0.000 | 0.529 | 0.471 | 0.471 | 0.471 |
| bay said=False | 26 | 0.500 | 0.000 | 0.542 | 0.458 | 0.458 | 0.458 |
| bay said=True | 11 | 0.545 | 0.000 | 0.500 | 0.500 | 0.500 | 0.500 |
| slip=False | 59 | 0.593 | 0.000 | 0.529 | 0.471 | 0.471 | 0.471 |
| slip=True | 1 | 1.000 | 0.000 | - | - | - | - |

## Errors

- dev-004: "Allow the car." expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- dev-007: "Please let plate 35 in for today." expected PROPOSE ALLOW 35, until Tue 24 Nov 23:59; got NEEDS_REVIEW (unsure)
- dev-009: "okay let car 626 in till tomorrow" expected PROPOSE ALLOW 626, until Wed 25 Nov 23:59; got NEEDS_REVIEW (unsure)
- dev-010: "930 until tomorrow." expected NEEDS_REVIEW (unclear_action); got NEEDS_REVIEW (unsure)
- dev-011: "allow thirty nine thousand three hundred twenty two until tomorrow at 9 pm" expected PROPOSE ALLOW 39322, until Wed 25 Nov 21:00; got NEEDS_REVIEW (unsure)
- dev-014: "allow number 47 until Saturday" expected PROPOSE ALLOW 47, until Sat 28 Nov 23:59; got NEEDS_REVIEW (unsure)
- dev-015: "Approve plate 3526 till midnight." expected PROPOSE ALLOW 3526, until Wed 25 Nov 00:00; got NEEDS_REVIEW (unsure)
- dev-016: "okay add car eighty two thousand one hundred eighty eight" expected PROPOSE ALLOW 82188, permanent; got NEEDS_REVIEW (missing_number)
- dev-019: "add 832 until tomorrow at 1" expected NEEDS_REVIEW (ambiguous_time); got NEEDS_REVIEW (multiple_numbers)
- dev-021: "Add car number 95 please." expected PROPOSE ALLOW 95, permanent; got NEEDS_REVIEW (unclear_action)
- dev-022: "Let car number 9873 in bay two until tomorrow please." expected PROPOSE ALLOW 9873, until Wed 25 Nov 23:59; got NEEDS_REVIEW (unclear_action)
- dev-023: "please add nine one six five two until tomorrow at one thirty pm" expected PROPOSE ALLOW 91652, until Wed 25 Nov 13:30; got NEEDS_REVIEW (unsure)
- dev-036: "add number one three eight zero six for today" expected PROPOSE ALLOW 13806, until Tue 24 Nov 23:59; got NEEDS_REVIEW (unsure)
- dev-040: "Allow car number 69375 for bay 1 until tomorrow." expected PROPOSE ALLOW 69375, until Sun 22 Nov 23:59; got NEEDS_REVIEW (unclear_action)
- dev-041: "Please let plate five thousand four hundred eleven in till tomorrow at one thirty pm." expected PROPOSE ALLOW 5411, until Wed 25 Nov 13:30; got NEEDS_REVIEW (unsure)
- dev-043: "okay add car 15 bay one" expected PROPOSE ALLOW 15, permanent; got NEEDS_REVIEW (missing_number)
- dev-044: "Allow 18 and one two five eight seven." expected NEEDS_REVIEW (multiple_numbers); got NEEDS_REVIEW (unsure)
- dev-046: "Allow plate 9008 until 10 pm." expected PROPOSE ALLOW 9008, until Tue 24 Nov 22:00; got NEEDS_REVIEW (unsure)
- dev-048: "Approve plate number 7 6 2 3 in bay two." expected PROPOSE ALLOW 7623, permanent; got NEEDS_REVIEW (unsure)
- dev-051: "allow number 7565 for a while" expected NEEDS_REVIEW (unclear_time); got NEEDS_REVIEW (unsure)
- dev-052: "add a car in bay 2" expected NEEDS_REVIEW (missing_number); got NEEDS_REVIEW (unclear_action)
- dev-053: "okay approve 5 2 1 0 6 until Sunday" expected PROPOSE ALLOW 52106, until Sun 22 Nov 23:59; got NEEDS_REVIEW (missing_number)
- dev-057: "Let car number nine hundred eleven in for an hour for bay 1." expected PROPOSE ALLOW 911, until Sat 21 Nov 10:30; got NEEDS_REVIEW (unclear_time)
- dev-060: "hey take one five three three five off the list" expected PROPOSE REMOVE 15335; got NEEDS_REVIEW (unsure)
