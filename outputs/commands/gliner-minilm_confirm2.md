# Model C: gliner-minilm on confirm2

Time per command: 26 ms mean, 35 ms p95.

| slice | n | exact | dangerous | needless question | action | number | until |
|---|---|---|---|---|---|---|---|
| all | 120 | 0.842 | 0.083 | 0.059 | 0.941 | 0.941 | 0.941 |
| kind=allow | 52 | 0.942 | 0.000 | 0.058 | 0.942 | 0.942 | 0.942 |
| kind=remove | 16 | 0.938 | 0.000 | 0.062 | 0.938 | 0.938 | 0.938 |
| kind=review | 40 | 0.650 | 0.225 | - | - | - | - |
| kind=single_digit | 4 | 1.000 | 0.000 | - | - | - | - |
| kind=unsupported | 8 | 0.875 | 0.125 | - | - | - | - |
| reason=ambiguous_time | 6 | 0.500 | 0.500 | - | - | - | - |
| reason=invalid_number | 4 | 1.000 | 0.000 | - | - | - | - |
| reason=missing_number | 6 | 0.667 | 0.000 | - | - | - | - |
| reason=multiple_numbers | 4 | 1.000 | 0.000 | - | - | - | - |
| reason=time_in_past | 6 | 0.833 | 0.000 | - | - | - | - |
| reason=unclear_action | 8 | 0.375 | 0.625 | - | - | - | - |
| reason=unclear_time | 6 | 0.500 | 0.167 | - | - | - | - |
| reason=unsupported | 8 | 0.875 | 0.125 | - | - | - | - |
| wording=seen | 74 | 0.919 | 0.027 | 0.059 | 0.941 | 0.941 | 0.941 |
| bay said=False | 46 | 0.913 | 0.043 | 0.049 | 0.951 | 0.951 | 0.951 |
| bay said=True | 28 | 0.929 | 0.000 | 0.074 | 0.926 | 0.926 | 0.926 |
| slip=False | 118 | 0.856 | 0.068 | 0.059 | 0.941 | 0.941 | 0.941 |
| slip=True | 2 | 0.000 | 1.000 | - | - | - | - |

## Errors

- confirm2-005: "Let car 65156 in for a while." expected NEEDS_REVIEW (unclear_time); got PROPOSE ALLOW 65156, permanent
- confirm2-007: "Add number 7369 until tomorrow at 8." expected NEEDS_REVIEW (ambiguous_time); got PROPOSE ALLOW 7369, until Wed 25 Nov 23:59
- confirm2-022: "4 6 1 3 0 until tomorrow" expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 46130, until Tue 01 Dec 23:59
- confirm2-027: "let plate 78329 in until tonight" expected NEEDS_REVIEW (unclear_time); got NEEDS_REVIEW (unclear_action)
- confirm2-035: "Please allow plate seven hundred nineteen in bay two." expected PROPOSE ALLOW 719, permanent; got NEEDS_REVIEW (unclear_action)
- confirm2-038: "Let plate number 1964 in." expected PROPOSE ALLOW 1964, permanent; got NEEDS_REVIEW (unclear_action)
- confirm2-054: "allow plate number 548 till ten" expected NEEDS_REVIEW (ambiguous_time); got PROPOSE ALLOW 548, permanent
- confirm2-060: "take 2 3 5 4 2 off the list" expected PROPOSE REMOVE 23542; got NEEDS_REVIEW (missing_number)
- confirm2-067: "okay and car number 342 for seven days" expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 342, until Thu 10 Dec 17:55
- confirm2-068: "Let number 96 in till 10:30 am." expected NEEDS_REVIEW (time_in_past); got NEEDS_REVIEW (unclear_action)
- confirm2-074: "car number 83083" expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 83083, permanent
- confirm2-080: "is car five eight nine two allowed" expected UNSUPPORTED; got PROPOSE ALLOW 5892, permanent
- confirm2-081: "let plate number 341 in until tonight" expected NEEDS_REVIEW (unclear_time); got NEEDS_REVIEW (unclear_action)
- confirm2-083: "allow my brother's car" expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- confirm2-090: "car number four eight six seven" expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 4867, permanent
- confirm2-098: "Please approve car two thousand one hundred seventy nine for a day in bay two." expected PROPOSE ALLOW 2179, until Tue 01 Dec 23:15; got NEEDS_REVIEW (unclear_time)
- confirm2-102: "Allow the car." expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- confirm2-108: "And car 1039 till nine pm please." expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 1039, until Tue 24 Nov 21:00
- confirm2-110: "Add 6 8 2 6 5 until eight." expected NEEDS_REVIEW (ambiguous_time); got PROPOSE ALLOW 68265, permanent
