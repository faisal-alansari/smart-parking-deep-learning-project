# Model C: checked on confirm3

Time per command: 174 ms mean, 408 ms p95.

| slice | n | exact | dangerous | needless question | action | number | until |
|---|---|---|---|---|---|---|---|
| all | 120 | 0.667 | 0.008 | 0.397 | 0.603 | 0.603 | 0.603 |
| kind=allow | 52 | 0.519 | 0.000 | 0.481 | 0.519 | 0.519 | 0.519 |
| kind=remove | 16 | 0.875 | 0.000 | 0.125 | 0.875 | 0.875 | 0.875 |
| kind=review | 40 | 0.750 | 0.025 | - | - | - | - |
| kind=single_digit | 4 | 0.500 | 0.000 | - | - | - | - |
| kind=unsupported | 8 | 0.875 | 0.000 | - | - | - | - |
| reason=ambiguous_time | 6 | 0.333 | 0.000 | - | - | - | - |
| reason=invalid_number | 4 | 1.000 | 0.000 | - | - | - | - |
| reason=missing_number | 6 | 0.500 | 0.000 | - | - | - | - |
| reason=multiple_numbers | 4 | 0.750 | 0.250 | - | - | - | - |
| reason=time_in_past | 6 | 1.000 | 0.000 | - | - | - | - |
| reason=unclear_action | 8 | 1.000 | 0.000 | - | - | - | - |
| reason=unclear_time | 6 | 0.667 | 0.000 | - | - | - | - |
| reason=unsupported | 8 | 0.875 | 0.000 | - | - | - | - |
| wording=seen | 74 | 0.608 | 0.000 | 0.397 | 0.603 | 0.603 | 0.603 |
| bay said=False | 58 | 0.707 | 0.000 | 0.288 | 0.712 | 0.712 | 0.712 |
| bay said=True | 16 | 0.250 | 0.000 | 0.750 | 0.250 | 0.250 | 0.250 |
| slip=False | 118 | 0.661 | 0.008 | 0.397 | 0.603 | 0.603 | 0.603 |
| slip=True | 2 | 1.000 | 0.000 | - | - | - | - |

## Errors

- confirm3-004: "Let car one hundred forty six in." expected PROPOSE ALLOW 146, permanent; got UNSUPPORTED
- confirm3-005: "approve number 3993 till 1" expected NEEDS_REVIEW (ambiguous_time); got NEEDS_REVIEW (unsure)
- confirm3-007: "Add 45 for a while." expected NEEDS_REVIEW (unclear_time); got NEEDS_REVIEW (unsure)
- confirm3-010: "Allow car 9742 for today please." expected PROPOSE ALLOW 9742, until Wed 25 Nov 23:59; got UNSUPPORTED
- confirm3-012: "Okay allow plate 912 until today bay two." expected PROPOSE ALLOW 912, until Sun 29 Nov 23:59; got NEEDS_REVIEW (unclear_action)
- confirm3-014: "Allow car number 83104 for a week." expected PROPOSE ALLOW 83104, until Wed 02 Dec 09:05; got UNSUPPORTED
- confirm3-021: "Let car five three zero eight in till 2:30." expected NEEDS_REVIEW (ambiguous_time); got NEEDS_REVIEW (missing_number)
- confirm3-023: "Add car 3875 and car 5 6 2 1 until tomorrow." expected NEEDS_REVIEW (multiple_numbers); got PROPOSE ALLOW 3875, until Mon 30 Nov 23:59
- confirm3-030: "Hey allow car 8 until noon." expected NEEDS_REVIEW (single_digit_number): ALLOW 8, until Wed 25 Nov 12:00; got UNSUPPORTED
- confirm3-032: "okay allow plate number four seven oh eight four in bay 2 please" expected PROPOSE ALLOW 47084, permanent; got NEEDS_REVIEW (unsure)
- confirm3-039: "allow car forty thousand five hundred until later" expected NEEDS_REVIEW (unclear_time); got UNSUPPORTED
- confirm3-047: "okay approve number 112 till tomorrow 8am" expected PROPOSE ALLOW 112, until Thu 26 Nov 08:00; got NEEDS_REVIEW (unsure)
- confirm3-050: "allow plate 9789 please" expected PROPOSE ALLOW 9789, permanent; got NEEDS_REVIEW (unsure)
- confirm3-051: "Let plate 4 in until 10:15 PM please." expected NEEDS_REVIEW (single_digit_number): ALLOW 4, until Fri 04 Dec 22:15; got NEEDS_REVIEW (unsure)
- confirm3-053: "Let number 89960 in bay one." expected PROPOSE ALLOW 89960, permanent; got NEEDS_REVIEW (unclear_action)
- confirm3-055: "please approve car thirty two sixty two" expected PROPOSE ALLOW 3262, permanent; got UNSUPPORTED
- confirm3-056: "let plate number 5 4 6 4 3 in until tomorrow please" expected PROPOSE ALLOW 54643, until Thu 26 Nov 23:59; got NEEDS_REVIEW (unsure)
- confirm3-060: "Let car number three eight six seven in bay 1." expected PROPOSE ALLOW 3867, permanent; got NEEDS_REVIEW (unsure)
- confirm3-061: "remove number six five five five eight from bay 2" expected PROPOSE REMOVE 65558; got NEEDS_REVIEW (unsure)
- confirm3-066: "please allow plate nine thousand one hundred fifteen bay 1" expected PROPOSE ALLOW 9115, permanent; got NEEDS_REVIEW (unsure)
- confirm3-068: "allow car 90767 till eleven thirty p.m. for bay 2" expected PROPOSE ALLOW 90767, until Sun 29 Nov 23:30; got NEEDS_REVIEW (unsure)
- confirm3-070: "allow number 941 bay two for a week" expected PROPOSE ALLOW 941, until Fri 11 Dec 20:25; got NEEDS_REVIEW (unclear_time)
- confirm3-073: "Add 8736 until tomorrow at 5p.m." expected PROPOSE ALLOW 8736, until Sat 05 Dec 17:00; got NEEDS_REVIEW (unsure)
- confirm3-076: "allow car 5125 in bay 2" expected PROPOSE ALLOW 5125, permanent; got UNSUPPORTED
- confirm3-079: "hey add plate number 1523 please" expected PROPOSE ALLOW 1523, permanent; got NEEDS_REVIEW (unsure)
- confirm3-082: "what's the weather today" expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- confirm3-083: "let car number 6 7 1 5 3 in" expected PROPOSE ALLOW 67153, permanent; got NEEDS_REVIEW (unsure)
- confirm3-085: "Hey add car number four thousand two hundred sixteen." expected PROPOSE ALLOW 4216, permanent; got NEEDS_REVIEW (unsure)
- confirm3-087: "Add six seven three five until tomorrow at 3." expected NEEDS_REVIEW (ambiguous_time); got NEEDS_REVIEW (multiple_numbers)
- confirm3-088: "allow plate number 93734 until tomorrow 5 p.m. in bay 1" expected PROPOSE ALLOW 93734, until Sat 05 Dec 17:00; got NEEDS_REVIEW (unclear_action)
- confirm3-089: "Take number one six five five off the list from bay 2." expected PROPOSE REMOVE 1655; got NEEDS_REVIEW (unsure)
- confirm3-093: "allow number 93 until tomorrow" expected PROPOSE ALLOW 93, until Mon 30 Nov 23:59; got NEEDS_REVIEW (unclear_action)
- confirm3-094: "Let plate four five eight two two in." expected PROPOSE ALLOW 45822, permanent; got NEEDS_REVIEW (unsure)
- confirm3-097: "Allow my brother's car." expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- confirm3-101: "Allow the car until 11PM tonight." expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- confirm3-107: "Approve number 47621 for five hours bay 1." expected PROPOSE ALLOW 47621, until Wed 25 Nov 14:05; got NEEDS_REVIEW (unsure)
- confirm3-108: "Let number seventy two thousand three hundred twelve in." expected PROPOSE ALLOW 72312, permanent; got NEEDS_REVIEW (unsure)
- confirm3-112: "Let plate number 72102 in until tomorrow at 6." expected NEEDS_REVIEW (ambiguous_time); got NEEDS_REVIEW (unsure)
- confirm3-114: "Allow the car." expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- confirm3-115: "okay let number 6916 in till nine fifteen pm" expected PROPOSE ALLOW 6916, until Fri 04 Dec 21:15; got NEEDS_REVIEW (unsure)
