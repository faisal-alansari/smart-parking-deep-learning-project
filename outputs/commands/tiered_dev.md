# Model C: tiered on dev

Time per command: 111 ms mean, 347 ms p95.

| slice | n | exact | dangerous | needless question | action | number | until |
|---|---|---|---|---|---|---|---|
| all | 60 | 0.817 | 0.000 | 0.206 | 0.794 | 0.794 | 0.794 |
| kind=allow | 26 | 0.731 | 0.000 | 0.269 | 0.731 | 0.731 | 0.731 |
| kind=remove | 8 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 |
| kind=review | 20 | 0.850 | 0.000 | - | - | - | - |
| kind=single_digit | 2 | 1.000 | 0.000 | - | - | - | - |
| kind=unsupported | 4 | 0.750 | 0.000 | - | - | - | - |
| reason=ambiguous_time | 3 | 1.000 | 0.000 | - | - | - | - |
| reason=invalid_number | 2 | 0.500 | 0.000 | - | - | - | - |
| reason=missing_number | 3 | 0.667 | 0.000 | - | - | - | - |
| reason=multiple_numbers | 2 | 0.500 | 0.000 | - | - | - | - |
| reason=time_in_past | 3 | 1.000 | 0.000 | - | - | - | - |
| reason=unclear_action | 4 | 1.000 | 0.000 | - | - | - | - |
| reason=unclear_time | 3 | 1.000 | 0.000 | - | - | - | - |
| reason=unsupported | 4 | 0.750 | 0.000 | - | - | - | - |
| wording=seen | 37 | 0.811 | 0.000 | 0.206 | 0.794 | 0.794 | 0.794 |
| bay said=False | 26 | 0.885 | 0.000 | 0.125 | 0.875 | 0.875 | 0.875 |
| bay said=True | 11 | 0.636 | 0.000 | 0.400 | 0.600 | 0.600 | 0.600 |
| slip=False | 59 | 0.814 | 0.000 | 0.206 | 0.794 | 0.794 | 0.794 |
| slip=True | 1 | 1.000 | 0.000 | - | - | - | - |

## Errors

- dev-004: "Allow the car." expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- dev-007: "Please let plate 35 in for today." expected PROPOSE ALLOW 35, until Tue 24 Nov 23:59; got NEEDS_REVIEW (unsure)
- dev-008: "what's the weather today" expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- dev-011: "allow thirty nine thousand three hundred twenty two until tomorrow at 9 pm" expected PROPOSE ALLOW 39322, until Wed 25 Nov 21:00; got NEEDS_REVIEW (unsure)
- dev-022: "Let car number 9873 in bay two until tomorrow please." expected PROPOSE ALLOW 9873, until Wed 25 Nov 23:59; got NEEDS_REVIEW (unsure)
- dev-029: "Let plate 4729886 in." expected NEEDS_REVIEW (invalid_number); got NEEDS_REVIEW (unclear_action)
- dev-041: "Please let plate five thousand four hundred eleven in till tomorrow at one thirty pm." expected PROPOSE ALLOW 5411, until Wed 25 Nov 13:30; got NEEDS_REVIEW (unsure)
- dev-043: "okay add car 15 bay one" expected PROPOSE ALLOW 15, permanent; got NEEDS_REVIEW (missing_number)
- dev-044: "Allow 18 and one two five eight seven." expected NEEDS_REVIEW (multiple_numbers); got NEEDS_REVIEW (unsure)
- dev-048: "Approve plate number 7 6 2 3 in bay two." expected PROPOSE ALLOW 7623, permanent; got NEEDS_REVIEW (unsure)
- dev-057: "Let car number nine hundred eleven in for an hour for bay 1." expected PROPOSE ALLOW 911, until Sat 21 Nov 10:30; got NEEDS_REVIEW (unclear_time)
