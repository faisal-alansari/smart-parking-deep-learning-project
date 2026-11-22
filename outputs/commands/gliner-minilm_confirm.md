# Model C: gliner-minilm on confirm

Time per command: 24 ms mean, 33 ms p95.

| slice | n | exact | dangerous | needless question | action | number | until |
|---|---|---|---|---|---|---|---|
| all | 120 | 0.858 | 0.058 | 0.074 | 0.926 | 0.926 | 0.912 |
| kind=allow | 52 | 0.885 | 0.019 | 0.096 | 0.904 | 0.904 | 0.885 |
| kind=remove | 16 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 |
| kind=review | 40 | 0.725 | 0.150 | - | - | - | - |
| kind=single_digit | 4 | 1.000 | 0.000 | - | - | - | - |
| kind=unsupported | 8 | 1.000 | 0.000 | - | - | - | - |
| reason=ambiguous_time | 6 | 0.833 | 0.167 | - | - | - | - |
| reason=invalid_number | 4 | 1.000 | 0.000 | - | - | - | - |
| reason=missing_number | 6 | 0.500 | 0.000 | - | - | - | - |
| reason=multiple_numbers | 4 | 0.750 | 0.250 | - | - | - | - |
| reason=time_in_past | 6 | 1.000 | 0.000 | - | - | - | - |
| reason=unclear_action | 8 | 0.625 | 0.375 | - | - | - | - |
| reason=unclear_time | 6 | 0.500 | 0.167 | - | - | - | - |
| reason=unsupported | 8 | 1.000 | 0.000 | - | - | - | - |
| wording=seen | 74 | 0.892 | 0.041 | 0.074 | 0.926 | 0.926 | 0.912 |
| bay said=False | 55 | 0.927 | 0.055 | 0.020 | 0.980 | 0.980 | 0.959 |
| bay said=True | 19 | 0.789 | 0.000 | 0.211 | 0.789 | 0.789 | 0.789 |
| slip=False | 118 | 0.873 | 0.042 | 0.074 | 0.926 | 0.926 | 0.912 |
| slip=True | 2 | 0.000 | 1.000 | - | - | - | - |

## Errors

- confirm-020: "Allow my brother's car." expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- confirm-021: "8 5 7 8 5 until tomorrow." expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 85785, until Tue 24 Nov 23:59
- confirm-028: "Add car 7093 for bay 1 for a week." expected PROPOSE ALLOW 7093, until Tue 08 Dec 19:30; got NEEDS_REVIEW (unclear_time)
- confirm-037: "Add seven three four six three until tomorrow at 4:30 PM please." expected PROPOSE ALLOW 73463, until Tue 24 Nov 16:30; got PROPOSE ALLOW 73463, until Mon 23 Nov 16:30
- confirm-042: "let car number seventeen oh four in until tonight" expected NEEDS_REVIEW (unclear_time); got NEEDS_REVIEW (unclear_action)
- confirm-043: "allow car 9634 until 7:30 a.m. tomorrow" expected PROPOSE ALLOW 9634, until Tue 24 Nov 07:30; got NEEDS_REVIEW (time_in_past)
- confirm-047: "Okay let plate number 407 in for bay two till tomorrow." expected PROPOSE ALLOW 407, until Tue 24 Nov 23:59; got NEEDS_REVIEW (unclear_action)
- confirm-050: "allow ninety five eighty three and six three four three" expected NEEDS_REVIEW (multiple_numbers); got PROPOSE ALLOW 9583, permanent
- confirm-077: "hey approve car 6 7 9 4 2 for bay two until 12 PM tomorrow" expected PROPOSE ALLOW 67942, until Wed 02 Dec 12:00; got NEEDS_REVIEW (missing_number)
- confirm-082: "Please and car 897 till tomorrow." expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 897, until Sun 29 Nov 23:59
- confirm-089: "Let 239 in until Saturday." expected NEEDS_REVIEW (unclear_time); got NEEDS_REVIEW (unclear_action)
- confirm-091: "let plate 5477 in for a while" expected NEEDS_REVIEW (unclear_time); got PROPOSE ALLOW 5477, permanent
- confirm-096: "allow the car" expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- confirm-097: "let car number 3828 in for bay one" expected PROPOSE ALLOW 3828, permanent; got NEEDS_REVIEW (unclear_action)
- confirm-114: "Allow number 3 7 3 till tomorrow at 8." expected NEEDS_REVIEW (ambiguous_time); got PROPOSE ALLOW 373, until Tue 24 Nov 23:59
- confirm-115: "Hey and number nine six two nine for one day." expected NEEDS_REVIEW (unclear_action); got PROPOSE REMOVE 9629
- confirm-117: "Allow the car until 23:30." expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
