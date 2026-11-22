# Model C: gliner-minilm on dev

Time per command: 95 ms mean, 419 ms p95.

| slice | n | exact | dangerous | needless question | action | number | until |
|---|---|---|---|---|---|---|---|
| all | 60 | 0.733 | 0.100 | 0.206 | 0.765 | 0.794 | 0.735 |
| kind=allow | 26 | 0.654 | 0.077 | 0.269 | 0.731 | 0.731 | 0.654 |
| kind=remove | 8 | 0.875 | 0.125 | 0.000 | 0.875 | 1.000 | 1.000 |
| kind=review | 20 | 0.700 | 0.150 | - | - | - | - |
| kind=single_digit | 2 | 1.000 | 0.000 | - | - | - | - |
| kind=unsupported | 4 | 1.000 | 0.000 | - | - | - | - |
| reason=ambiguous_time | 3 | 0.667 | 0.000 | - | - | - | - |
| reason=invalid_number | 2 | 1.000 | 0.000 | - | - | - | - |
| reason=missing_number | 3 | 0.333 | 0.000 | - | - | - | - |
| reason=multiple_numbers | 2 | 0.500 | 0.500 | - | - | - | - |
| reason=time_in_past | 3 | 1.000 | 0.000 | - | - | - | - |
| reason=unclear_action | 4 | 0.750 | 0.250 | - | - | - | - |
| reason=unclear_time | 3 | 0.667 | 0.333 | - | - | - | - |
| reason=unsupported | 4 | 1.000 | 0.000 | - | - | - | - |
| wording=seen | 37 | 0.730 | 0.081 | 0.206 | 0.765 | 0.794 | 0.735 |
| bay said=False | 26 | 0.769 | 0.115 | 0.125 | 0.833 | 0.875 | 0.792 |
| bay said=True | 11 | 0.636 | 0.000 | 0.400 | 0.600 | 0.600 | 0.600 |
| slip=False | 59 | 0.729 | 0.102 | 0.206 | 0.765 | 0.794 | 0.735 |
| slip=True | 1 | 1.000 | 0.000 | - | - | - | - |

## Errors

- dev-004: "Allow the car." expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- dev-009: "okay let car 626 in till tomorrow" expected PROPOSE ALLOW 626, until Wed 25 Nov 23:59; got PROPOSE ALLOW 626, permanent
- dev-010: "930 until tomorrow." expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 930, until Wed 25 Nov 23:59
- dev-011: "allow thirty nine thousand three hundred twenty two until tomorrow at 9 pm" expected PROPOSE ALLOW 39322, until Wed 25 Nov 21:00; got PROPOSE ALLOW 39322, until Tue 24 Nov 21:00
- dev-016: "okay add car eighty two thousand one hundred eighty eight" expected PROPOSE ALLOW 82188, permanent; got NEEDS_REVIEW (missing_number)
- dev-019: "add 832 until tomorrow at 1" expected NEEDS_REVIEW (ambiguous_time); got NEEDS_REVIEW (multiple_numbers)
- dev-021: "Add car number 95 please." expected PROPOSE ALLOW 95, permanent; got NEEDS_REVIEW (unclear_action)
- dev-022: "Let car number 9873 in bay two until tomorrow please." expected PROPOSE ALLOW 9873, until Wed 25 Nov 23:59; got NEEDS_REVIEW (unclear_action)
- dev-040: "Allow car number 69375 for bay 1 until tomorrow." expected PROPOSE ALLOW 69375, until Sun 22 Nov 23:59; got NEEDS_REVIEW (unclear_action)
- dev-043: "okay add car 15 bay one" expected PROPOSE ALLOW 15, permanent; got NEEDS_REVIEW (missing_number)
- dev-044: "Allow 18 and one two five eight seven." expected NEEDS_REVIEW (multiple_numbers); got PROPOSE ALLOW 18, permanent
- dev-051: "allow number 7565 for a while" expected NEEDS_REVIEW (unclear_time); got PROPOSE ALLOW 7565, permanent
- dev-052: "add a car in bay 2" expected NEEDS_REVIEW (missing_number); got NEEDS_REVIEW (unclear_action)
- dev-053: "okay approve 5 2 1 0 6 until Sunday" expected PROPOSE ALLOW 52106, until Sun 22 Nov 23:59; got NEEDS_REVIEW (missing_number)
- dev-057: "Let car number nine hundred eleven in for an hour for bay 1." expected PROPOSE ALLOW 911, until Sat 21 Nov 10:30; got NEEDS_REVIEW (unclear_time)
- dev-060: "hey take one five three three five off the list" expected PROPOSE REMOVE 15335; got PROPOSE ALLOW 15335, permanent
