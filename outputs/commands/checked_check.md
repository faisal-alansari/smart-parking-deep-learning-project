# Model C: checked on check

Time per command: 161 ms mean, 377 ms p95.

| slice | n | exact | dangerous | needless question | action | number | until |
|---|---|---|---|---|---|---|---|
| all | 120 | 0.658 | 0.000 | 0.412 | 0.588 | 0.588 | 0.588 |
| kind=allow | 52 | 0.500 | 0.000 | 0.500 | 0.500 | 0.500 | 0.500 |
| kind=remove | 16 | 0.875 | 0.000 | 0.125 | 0.875 | 0.875 | 0.875 |
| kind=review | 40 | 0.750 | 0.000 | - | - | - | - |
| kind=single_digit | 4 | 0.750 | 0.000 | - | - | - | - |
| kind=unsupported | 8 | 0.750 | 0.000 | - | - | - | - |
| reason=ambiguous_time | 6 | 0.333 | 0.000 | - | - | - | - |
| reason=invalid_number | 4 | 1.000 | 0.000 | - | - | - | - |
| reason=missing_number | 6 | 0.500 | 0.000 | - | - | - | - |
| reason=multiple_numbers | 4 | 0.750 | 0.000 | - | - | - | - |
| reason=time_in_past | 6 | 1.000 | 0.000 | - | - | - | - |
| reason=unclear_action | 8 | 0.750 | 0.000 | - | - | - | - |
| reason=unclear_time | 6 | 1.000 | 0.000 | - | - | - | - |
| reason=unsupported | 8 | 0.750 | 0.000 | - | - | - | - |
| wording=seen | 74 | 0.608 | 0.000 | 0.412 | 0.588 | 0.588 | 0.588 |
| bay said=False | 56 | 0.750 | 0.000 | 0.260 | 0.740 | 0.740 | 0.740 |
| bay said=True | 18 | 0.167 | 0.000 | 0.833 | 0.167 | 0.167 | 0.167 |
| slip=False | 118 | 0.653 | 0.000 | 0.412 | 0.588 | 0.588 | 0.588 |
| slip=True | 2 | 1.000 | 0.000 | - | - | - | - |

## Errors

- check-002: "allow plate four thousand three hundred two till 2:30" expected NEEDS_REVIEW (ambiguous_time); got NEEDS_REVIEW (missing_number)
- check-004: "Allow the car until eight pm." expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- check-005: "allow my brother's car" expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- check-007: "Let plate 23745 in until today." expected PROPOSE ALLOW 23745, until Wed 25 Nov 23:59; got NEEDS_REVIEW (unclear_action)
- check-009: "please allow car number 90237 until tomorrow 12 PM in bay two" expected PROPOSE ALLOW 90237, until Thu 26 Nov 12:00; got NEEDS_REVIEW (unsure)
- check-013: "Let car eleven thousand four hundred eighteen in till four." expected NEEDS_REVIEW (ambiguous_time); got UNSUPPORTED
- check-014: "Okay let plate 223 in for today." expected PROPOSE ALLOW 223, until Wed 25 Nov 23:59; got NEEDS_REVIEW (unclear_action)
- check-017: "Okay allow plate one five eight zero eight in bay 2 until tomorrow." expected PROPOSE ALLOW 15808, until Sat 28 Nov 23:59; got NEEDS_REVIEW (unsure)
- check-018: "hey add twenty four fifty three until noon for bay 1" expected PROPOSE ALLOW 2453, until Sun 22 Nov 12:00; got NEEDS_REVIEW (unsure)
- check-023: "Allow the car." expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- check-025: "please let number 3 2 6 6 in till Monday" expected PROPOSE ALLOW 3266, until Mon 23 Nov 23:59; got NEEDS_REVIEW (unsure)
- check-027: "Car number 44." expected NEEDS_REVIEW (unclear_action); got UNSUPPORTED
- check-031: "Okay approve plate twenty six thousand eight hundred thirty nine until Monday in bay 2 please." expected PROPOSE ALLOW 26839, until Mon 30 Nov 23:59; got NEEDS_REVIEW (unsure)
- check-032: "Allow 3 3 and 3293." expected NEEDS_REVIEW (multiple_numbers); got NEEDS_REVIEW (unsure)
- check-033: "Let two oh three nine in bay 1 for one hour." expected PROPOSE ALLOW 2039, until Sun 22 Nov 08:50; got NEEDS_REVIEW (unsure)
- check-035: "hello" expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- check-040: "allow plate two one two eight eight until nine thirty PM" expected PROPOSE ALLOW 21288, until Wed 25 Nov 21:30; got NEEDS_REVIEW (unsure)
- check-041: "Approve car five two four seven three till 7." expected NEEDS_REVIEW (ambiguous_time); got NEEDS_REVIEW (unsure)
- check-042: "What's the weather today?" expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- check-046: "Hey let plate number 381 in till Wednesday." expected PROPOSE ALLOW 381, until Wed 02 Dec 23:59; got NEEDS_REVIEW (unclear_action)
- check-050: "Let plate number ninety three thousand one hundred ninety one in till tomorrow at 5." expected NEEDS_REVIEW (ambiguous_time); got NEEDS_REVIEW (missing_number)
- check-057: "let 1 9 2 9 in for a week" expected PROPOSE ALLOW 1929, until Wed 02 Dec 16:20; got NEEDS_REVIEW (unsure)
- check-068: "approve plate number 5 1 2 8 0 until tomorrow nine thirty am" expected PROPOSE ALLOW 51280, until Sat 28 Nov 09:30; got NEEDS_REVIEW (unsure)
- check-074: "add number nine six three eight in bay 2" expected PROPOSE ALLOW 9638, permanent; got NEEDS_REVIEW (unsure)
- check-075: "Car number fifty four thirty eight." expected NEEDS_REVIEW (unclear_action); got UNSUPPORTED
- check-080: "Take plate number 5 7 7 9 5 off the list from bay 1." expected PROPOSE REMOVE 57795; got NEEDS_REVIEW (unclear_action)
- check-081: "Please let number nine three two in." expected PROPOSE ALLOW 932, permanent; got NEEDS_REVIEW (unsure)
- check-082: "add plate 67336 in bay two" expected PROPOSE ALLOW 67336, permanent; got NEEDS_REVIEW (unsure)
- check-083: "let plate number 86422 in till 10:15 pm tonight" expected PROPOSE ALLOW 86422, until Wed 25 Nov 22:15; got NEEDS_REVIEW (unclear_action)
- check-087: "delete fifty seven thousand five hundred fifty five" expected PROPOSE REMOVE 57555; got NEEDS_REVIEW (missing_number)
- check-088: "Let plate 2 0 9 1 3 in for a week for bay 2 please." expected PROPOSE ALLOW 20913, until Wed 02 Dec 16:20; got NEEDS_REVIEW (unclear_time)
- check-090: "please let number 56077 in bay two until tomorrow" expected PROPOSE ALLOW 56077, until Thu 26 Nov 23:59; got NEEDS_REVIEW (unsure)
- check-099: "okay approve number two thousand one hundred thirteen till seven pm bay 2" expected PROPOSE ALLOW 2113, until Wed 25 Nov 19:00; got NEEDS_REVIEW (unsure)
- check-102: "Approve 6 4 6 7 until one pm in bay two." expected PROPOSE ALLOW 6467, until Sun 22 Nov 13:00; got NEEDS_REVIEW (unsure)
- check-106: "let 193 in for one week in bay two please" expected PROPOSE ALLOW 193, until Sun 29 Nov 07:50; got NEEDS_REVIEW (unclear_action)
- check-109: "Hey add car number seven until tomorrow." expected NEEDS_REVIEW (single_digit_number): ALLOW 7, until Sat 28 Nov 23:59; got NEEDS_REVIEW (unsure)
- check-112: "Approve plate nine zero zero." expected PROPOSE ALLOW 900, permanent; got NEEDS_REVIEW (unsure)
- check-115: "Okay add number 869 bay 1." expected PROPOSE ALLOW 869, permanent; got NEEDS_REVIEW (unsure)
- check-117: "allow plate 59838 bay two please" expected PROPOSE ALLOW 59838, permanent; got NEEDS_REVIEW (unsure)
- check-119: "Please approve car number 34393 till ten fifteen PM." expected PROPOSE ALLOW 34393, until Fri 27 Nov 22:15; got NEEDS_REVIEW (unsure)
- check-120: "Please approve car number 102 until tomorrow at one pm." expected PROPOSE ALLOW 102, until Thu 26 Nov 13:00; got NEEDS_REVIEW (unsure)
