# Model C: gliner-minilm on confirm3

Time per command: 25 ms mean, 37 ms p95.

| slice | n | exact | dangerous | needless question | action | number | until |
|---|---|---|---|---|---|---|---|
| all | 120 | 0.792 | 0.058 | 0.147 | 0.838 | 0.853 | 0.853 |
| kind=allow | 52 | 0.808 | 0.000 | 0.192 | 0.808 | 0.808 | 0.808 |
| kind=remove | 16 | 0.938 | 0.062 | 0.000 | 0.938 | 1.000 | 1.000 |
| kind=review | 40 | 0.700 | 0.150 | - | - | - | - |
| kind=single_digit | 4 | 0.750 | 0.000 | - | - | - | - |
| kind=unsupported | 8 | 0.875 | 0.000 | - | - | - | - |
| reason=ambiguous_time | 6 | 0.333 | 0.333 | - | - | - | - |
| reason=invalid_number | 4 | 1.000 | 0.000 | - | - | - | - |
| reason=missing_number | 6 | 0.500 | 0.000 | - | - | - | - |
| reason=multiple_numbers | 4 | 0.750 | 0.250 | - | - | - | - |
| reason=time_in_past | 6 | 1.000 | 0.000 | - | - | - | - |
| reason=unclear_action | 8 | 0.750 | 0.250 | - | - | - | - |
| reason=unclear_time | 6 | 0.667 | 0.167 | - | - | - | - |
| reason=unsupported | 8 | 0.875 | 0.000 | - | - | - | - |
| wording=seen | 74 | 0.811 | 0.041 | 0.147 | 0.838 | 0.853 | 0.853 |
| bay said=False | 58 | 0.862 | 0.034 | 0.096 | 0.904 | 0.904 | 0.904 |
| bay said=True | 16 | 0.625 | 0.062 | 0.312 | 0.625 | 0.688 | 0.688 |
| slip=False | 118 | 0.805 | 0.042 | 0.147 | 0.838 | 0.853 | 0.853 |
| slip=True | 2 | 0.000 | 1.000 | - | - | - | - |

## Errors

- confirm3-004: "Let car one hundred forty six in." expected PROPOSE ALLOW 146, permanent; got UNSUPPORTED
- confirm3-005: "approve number 3993 till 1" expected NEEDS_REVIEW (ambiguous_time); got PROPOSE ALLOW 3993, permanent
- confirm3-007: "Add 45 for a while." expected NEEDS_REVIEW (unclear_time); got PROPOSE ALLOW 45, permanent
- confirm3-010: "Allow car 9742 for today please." expected PROPOSE ALLOW 9742, until Wed 25 Nov 23:59; got UNSUPPORTED
- confirm3-012: "Okay allow plate 912 until today bay two." expected PROPOSE ALLOW 912, until Sun 29 Nov 23:59; got NEEDS_REVIEW (unclear_action)
- confirm3-014: "Allow car number 83104 for a week." expected PROPOSE ALLOW 83104, until Wed 02 Dec 09:05; got UNSUPPORTED
- confirm3-020: "and 9376 for 30 minutes" expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 9376, until Sun 29 Nov 16:10
- confirm3-021: "Let car five three zero eight in till 2:30." expected NEEDS_REVIEW (ambiguous_time); got NEEDS_REVIEW (missing_number)
- confirm3-023: "Add car 3875 and car 5 6 2 1 until tomorrow." expected NEEDS_REVIEW (multiple_numbers); got PROPOSE ALLOW 3875, until Mon 30 Nov 23:59
- confirm3-030: "Hey allow car 8 until noon." expected NEEDS_REVIEW (single_digit_number): ALLOW 8, until Wed 25 Nov 12:00; got UNSUPPORTED
- confirm3-034: "and plate number 87013 please" expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 87013, permanent
- confirm3-039: "allow car forty thousand five hundred until later" expected NEEDS_REVIEW (unclear_time); got UNSUPPORTED
- confirm3-053: "Let number 89960 in bay one." expected PROPOSE ALLOW 89960, permanent; got NEEDS_REVIEW (unclear_action)
- confirm3-055: "please approve car thirty two sixty two" expected PROPOSE ALLOW 3262, permanent; got UNSUPPORTED
- confirm3-070: "allow number 941 bay two for a week" expected PROPOSE ALLOW 941, until Fri 11 Dec 20:25; got NEEDS_REVIEW (unclear_time)
- confirm3-076: "allow car 5125 in bay 2" expected PROPOSE ALLOW 5125, permanent; got UNSUPPORTED
- confirm3-082: "what's the weather today" expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- confirm3-087: "Add six seven three five until tomorrow at 3." expected NEEDS_REVIEW (ambiguous_time); got NEEDS_REVIEW (multiple_numbers)
- confirm3-088: "allow plate number 93734 until tomorrow 5 p.m. in bay 1" expected PROPOSE ALLOW 93734, until Sat 05 Dec 17:00; got NEEDS_REVIEW (unclear_action)
- confirm3-089: "Take number one six five five off the list from bay 2." expected PROPOSE REMOVE 1655; got PROPOSE ALLOW 1655, permanent
- confirm3-093: "allow number 93 until tomorrow" expected PROPOSE ALLOW 93, until Mon 30 Nov 23:59; got NEEDS_REVIEW (unclear_action)
- confirm3-097: "Allow my brother's car." expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- confirm3-101: "Allow the car until 11PM tonight." expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- confirm3-112: "Let plate number 72102 in until tomorrow at 6." expected NEEDS_REVIEW (ambiguous_time); got PROPOSE ALLOW 72102, until Thu 26 Nov 23:59
- confirm3-114: "Allow the car." expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
