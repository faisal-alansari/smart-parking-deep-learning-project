# Model C: flan-t5 on dev

Time per command: 228 ms mean, 429 ms p95.

| slice | n | exact | dangerous | needless question | action | number | until |
|---|---|---|---|---|---|---|---|
| all | 60 | 0.167 | 0.150 | 0.794 | 0.118 | 0.206 | 0.147 |
| kind=allow | 26 | 0.000 | 0.154 | 0.885 | 0.000 | 0.115 | 0.038 |
| kind=remove | 8 | 0.500 | 0.000 | 0.500 | 0.500 | 0.500 | 0.500 |
| kind=review | 20 | 0.200 | 0.200 | - | - | - | - |
| kind=single_digit | 2 | 0.000 | 0.500 | - | - | - | - |
| kind=unsupported | 4 | 0.500 | 0.000 | - | - | - | - |
| reason=ambiguous_time | 3 | 0.000 | 0.333 | - | - | - | - |
| reason=invalid_number | 2 | 0.500 | 0.000 | - | - | - | - |
| reason=missing_number | 3 | 1.000 | 0.000 | - | - | - | - |
| reason=multiple_numbers | 2 | 0.000 | 0.000 | - | - | - | - |
| reason=time_in_past | 3 | 0.000 | 0.667 | - | - | - | - |
| reason=unclear_action | 4 | 0.000 | 0.250 | - | - | - | - |
| reason=unclear_time | 3 | 0.000 | 0.000 | - | - | - | - |
| reason=unsupported | 4 | 0.500 | 0.000 | - | - | - | - |
| wording=seen | 37 | 0.108 | 0.135 | 0.794 | 0.118 | 0.206 | 0.147 |
| bay said=False | 26 | 0.115 | 0.115 | 0.833 | 0.125 | 0.167 | 0.125 |
| bay said=True | 11 | 0.091 | 0.182 | 0.700 | 0.100 | 0.300 | 0.200 |
| slip=False | 59 | 0.169 | 0.153 | 0.794 | 0.118 | 0.206 | 0.147 |
| slip=True | 1 | 0.000 | 0.000 | - | - | - | - |

## Errors

- dev-001: "Okay and car number 37080 bay one for one week." expected NEEDS_REVIEW (unclear_action); got UNSUPPORTED
- dev-002: "please approve 6 4 3 1 9" expected PROPOSE ALLOW 64319, permanent; got UNSUPPORTED
- dev-003: "Hey remove plate four zero six zero nine please." expected PROPOSE REMOVE 40609; got NEEDS_REVIEW (missing_number)
- dev-005: "approve car eight oh nine until 4:30" expected NEEDS_REVIEW (ambiguous_time); got NEEDS_REVIEW (missing_number)
- dev-007: "Please let plate 35 in for today." expected PROPOSE ALLOW 35, until Tue 24 Nov 23:59; got UNSUPPORTED
- dev-009: "okay let car 626 in till tomorrow" expected PROPOSE ALLOW 626, until Wed 25 Nov 23:59; got UNSUPPORTED
- dev-010: "930 until tomorrow." expected NEEDS_REVIEW (unclear_action); got UNSUPPORTED
- dev-011: "allow thirty nine thousand three hundred twenty two until tomorrow at 9 pm" expected PROPOSE ALLOW 39322, until Wed 25 Nov 21:00; got UNSUPPORTED
- dev-012: "Add plate 61079 until 9AM." expected NEEDS_REVIEW (time_in_past); got PROPOSE REMOVE 61079
- dev-013: "allow number nine hundred four in bay 2 until seven thirty PM" expected PROPOSE ALLOW 904, until Sat 21 Nov 19:30; got UNSUPPORTED
- dev-014: "allow number 47 until Saturday" expected PROPOSE ALLOW 47, until Sat 28 Nov 23:59; got UNSUPPORTED
- dev-015: "Approve plate 3526 till midnight." expected PROPOSE ALLOW 3526, until Wed 25 Nov 00:00; got UNSUPPORTED
- dev-016: "okay add car eighty two thousand one hundred eighty eight" expected PROPOSE ALLOW 82188, permanent; got NEEDS_REVIEW (missing_number)
- dev-017: "please take eighty six fourteen off the list" expected PROPOSE REMOVE 8614; got NEEDS_REVIEW (missing_number)
- dev-018: "allow number nine one one seven please" expected PROPOSE ALLOW 9117, permanent; got UNSUPPORTED
- dev-019: "add 832 until tomorrow at 1" expected NEEDS_REVIEW (ambiguous_time); got UNSUPPORTED
- dev-020: "Add car 29422 until Tuesday." expected NEEDS_REVIEW (unclear_time); got NEEDS_REVIEW (missing_number)
- dev-021: "Add car number 95 please." expected PROPOSE ALLOW 95, permanent; got NEEDS_REVIEW (missing_number)
- dev-022: "Let car number 9873 in bay two until tomorrow please." expected PROPOSE ALLOW 9873, until Wed 25 Nov 23:59; got UNSUPPORTED
- dev-023: "please add nine one six five two until tomorrow at one thirty pm" expected PROPOSE ALLOW 91652, until Wed 25 Nov 13:30; got UNSUPPORTED
- dev-024: "Allow plate number one five eight nine five till 9:30." expected NEEDS_REVIEW (ambiguous_time); got PROPOSE REMOVE 930
- dev-027: "Approve plate number one oh two seven six until Wednesday." expected PROPOSE ALLOW 10276, until Wed 25 Nov 23:59; got NEEDS_REVIEW (single_digit_number): REMOVE 1
- dev-028: "approve seven five zero seven six bay 2 until Thursday" expected PROPOSE ALLOW 75076, until Thu 26 Nov 23:59; got UNSUPPORTED
- dev-029: "Let plate 4729886 in." expected NEEDS_REVIEW (invalid_number); got NEEDS_REVIEW (missing_number)
- dev-030: "How many cars are parked?" expected UNSUPPORTED; got NEEDS_REVIEW (missing_number)
- dev-031: "Add car 62680 and car 46149 until tomorrow." expected NEEDS_REVIEW (multiple_numbers); got NEEDS_REVIEW (missing_number)
- dev-032: "okay remove car 7 7 0 6 8" expected PROPOSE REMOVE 77068; got NEEDS_REVIEW (invalid_number)
- dev-034: "okay let one four eight four in for bay 2 until 21:00" expected PROPOSE ALLOW 1484, until Tue 24 Nov 21:00; got NEEDS_REVIEW (missing_number)
- dev-035: "Car number 98331." expected NEEDS_REVIEW (unclear_action); got UNSUPPORTED
- dev-036: "add number one three eight zero six for today" expected PROPOSE ALLOW 13806, until Tue 24 Nov 23:59; got NEEDS_REVIEW (missing_number)
- dev-038: "Please add 5134." expected PROPOSE ALLOW 5134, permanent; got UNSUPPORTED
- dev-039: "Let number 14649 in until 7am." expected NEEDS_REVIEW (time_in_past); got PROPOSE REMOVE 14649
- dev-040: "Allow car number 69375 for bay 1 until tomorrow." expected PROPOSE ALLOW 69375, until Sun 22 Nov 23:59; got PROPOSE REMOVE 69375
- dev-041: "Please let plate five thousand four hundred eleven in till tomorrow at one thirty pm." expected PROPOSE ALLOW 5411, until Wed 25 Nov 13:30; got UNSUPPORTED
- dev-042: "hey add plate three oh please" expected PROPOSE ALLOW 30, permanent; got UNSUPPORTED
- dev-043: "okay add car 15 bay one" expected PROPOSE ALLOW 15, permanent; got NEEDS_REVIEW (missing_number)
- dev-044: "Allow 18 and one two five eight seven." expected NEEDS_REVIEW (multiple_numbers); got UNSUPPORTED
- dev-045: "car 6846 in bay 2" expected NEEDS_REVIEW (unclear_action); got PROPOSE REMOVE 6846
- dev-046: "Allow plate 9008 until 10 pm." expected PROPOSE ALLOW 9008, until Tue 24 Nov 22:00; got PROPOSE REMOVE 9008
- dev-047: "Add plate number 91586 until tonight." expected NEEDS_REVIEW (unclear_time); got UNSUPPORTED
- dev-048: "Approve plate number 7 6 2 3 in bay two." expected PROPOSE ALLOW 7623, permanent; got PROPOSE REMOVE 7623
- dev-049: "Is car five zero oh two one allowed?" expected UNSUPPORTED; got NEEDS_REVIEW (missing_number)
- dev-051: "allow number 7565 for a while" expected NEEDS_REVIEW (unclear_time); got UNSUPPORTED
- dev-053: "okay approve 5 2 1 0 6 until Sunday" expected PROPOSE ALLOW 52106, until Sun 22 Nov 23:59; got UNSUPPORTED
- dev-054: "Allow number 8." expected NEEDS_REVIEW (single_digit_number): ALLOW 8, permanent; got NEEDS_REVIEW (single_digit_number): REMOVE 8
- dev-056: "Please approve number 4 for 2 hours." expected NEEDS_REVIEW (single_digit_number): ALLOW 4, until Tue 24 Nov 21:45; got UNSUPPORTED
- dev-057: "Let car number nine hundred eleven in for an hour for bay 1." expected PROPOSE ALLOW 911, until Sat 21 Nov 10:30; got NEEDS_REVIEW (missing_number)
- dev-058: "allow number 47645 until 8a.m. today" expected NEEDS_REVIEW (time_in_past); got UNSUPPORTED
- dev-059: "Please add plate number 48848 for bay 2 till 22:30." expected PROPOSE ALLOW 48848, until Sat 21 Nov 22:30; got UNSUPPORTED
- dev-060: "hey take one five three three five off the list" expected PROPOSE REMOVE 15335; got NEEDS_REVIEW (missing_number)
