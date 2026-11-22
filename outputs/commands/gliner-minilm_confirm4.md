# Model C: gliner-minilm on confirm4

Time per command: 24 ms mean, 33 ms p95.

| slice | n | exact | dangerous | needless question | action | number | until |
|---|---|---|---|---|---|---|---|
| all | 120 | 0.833 | 0.042 | 0.118 | 0.882 | 0.882 | 0.824 |
| kind=allow | 52 | 0.788 | 0.077 | 0.135 | 0.865 | 0.865 | 0.788 |
| kind=remove | 16 | 0.938 | 0.000 | 0.062 | 0.938 | 0.938 | 0.938 |
| kind=review | 40 | 0.825 | 0.025 | - | - | - | - |
| kind=single_digit | 4 | 1.000 | 0.000 | - | - | - | - |
| kind=unsupported | 8 | 0.875 | 0.000 | - | - | - | - |
| reason=ambiguous_time | 6 | 0.833 | 0.167 | - | - | - | - |
| reason=invalid_number | 4 | 1.000 | 0.000 | - | - | - | - |
| reason=missing_number | 6 | 0.500 | 0.000 | - | - | - | - |
| reason=multiple_numbers | 4 | 1.000 | 0.000 | - | - | - | - |
| reason=time_in_past | 6 | 1.000 | 0.000 | - | - | - | - |
| reason=unclear_action | 8 | 0.875 | 0.000 | - | - | - | - |
| reason=unclear_time | 6 | 0.667 | 0.000 | - | - | - | - |
| reason=unsupported | 8 | 0.875 | 0.000 | - | - | - | - |
| wording=seen | 74 | 0.824 | 0.054 | 0.118 | 0.882 | 0.882 | 0.824 |
| bay said=False | 48 | 0.792 | 0.083 | 0.114 | 0.886 | 0.886 | 0.795 |
| bay said=True | 26 | 0.885 | 0.000 | 0.125 | 0.875 | 0.875 | 0.875 |
| slip=False | 118 | 0.839 | 0.042 | 0.118 | 0.882 | 0.882 | 0.824 |
| slip=True | 2 | 0.500 | 0.000 | - | - | - | - |

## Errors

- confirm4-007: "let number 1788 in for a while" expected NEEDS_REVIEW (unclear_time); got NEEDS_REVIEW (unclear_action)
- confirm4-013: "And 3 5 6 5 until 12 pm." expected NEEDS_REVIEW (unclear_action); got NEEDS_REVIEW (missing_number)
- confirm4-021: "hey add 4484 for a week" expected PROPOSE ALLOW 4484, until Sat 12 Dec 21:50; got PROPOSE ALLOW 4484, permanent
- confirm4-032: "what's the weather today" expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- confirm4-033: "add 7162 for one day" expected PROPOSE ALLOW 7162, until Sun 06 Dec 21:50; got PROPOSE ALLOW 7162, permanent
- confirm4-034: "please allow car 265" expected PROPOSE ALLOW 265, permanent; got UNSUPPORTED
- confirm4-040: "allow the car for 2 hours" expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- confirm4-046: "please allow car 3702 till tomorrow" expected PROPOSE ALLOW 3702, until Fri 27 Nov 23:59; got UNSUPPORTED
- confirm4-048: "approve car 2667 till tomorrow at 5" expected NEEDS_REVIEW (ambiguous_time); got PROPOSE ALLOW 2667, until Fri 27 Nov 23:59
- confirm4-061: "approve 895 for a week" expected PROPOSE ALLOW 895, until Sat 12 Dec 21:50; got PROPOSE ALLOW 895, permanent
- confirm4-062: "let car 6 9 in for a week please" expected PROPOSE ALLOW 69, until Tue 08 Dec 07:35; got PROPOSE ALLOW 69, permanent
- confirm4-065: "Please take car 32700 off the list." expected PROPOSE REMOVE 32700; got UNSUPPORTED
- confirm4-068: "Add plate number 9236 in bay one." expected PROPOSE ALLOW 9236, permanent; got NEEDS_REVIEW (unclear_action)
- confirm4-079: "Allow the car until 10pm." expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- confirm4-082: "Please add car number 8 8 1 9 2 for a week." expected PROPOSE ALLOW 88192, until Thu 03 Dec 11:20; got NEEDS_REVIEW (unclear_time)
- confirm4-083: "Let plate 8640 in bay 1 for 30 minutes." expected PROPOSE ALLOW 8640, until Sat 05 Dec 22:20; got NEEDS_REVIEW (unclear_action)
- confirm4-085: "Allow 20976 bay 1 till 11 pm tonight." expected PROPOSE ALLOW 20976, until Thu 26 Nov 23:00; got NEEDS_REVIEW (multiple_numbers)
- confirm4-112: "Allow car 9237 for a week." expected PROPOSE ALLOW 9237, until Tue 08 Dec 07:35; got UNSUPPORTED
- confirm4-116: "allow my brother's car" expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- confirm4-117: "allow 5 6 3 0 until Tuesday" expected NEEDS_REVIEW (unclear_time); got NEEDS_REVIEW (missing_number)
