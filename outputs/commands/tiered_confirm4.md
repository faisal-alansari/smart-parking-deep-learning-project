# Model C: tiered on confirm4

Time per command: 97 ms mean, 347 ms p95.

| slice | n | exact | dangerous | needless question | action | number | until |
|---|---|---|---|---|---|---|---|
| all | 120 | 0.775 | 0.000 | 0.294 | 0.706 | 0.706 | 0.706 |
| kind=allow | 52 | 0.635 | 0.000 | 0.365 | 0.635 | 0.635 | 0.635 |
| kind=remove | 16 | 0.938 | 0.000 | 0.062 | 0.938 | 0.938 | 0.938 |
| kind=review | 40 | 0.850 | 0.000 | - | - | - | - |
| kind=single_digit | 4 | 1.000 | 0.000 | - | - | - | - |
| kind=unsupported | 8 | 0.875 | 0.000 | - | - | - | - |
| reason=ambiguous_time | 6 | 0.833 | 0.000 | - | - | - | - |
| reason=invalid_number | 4 | 1.000 | 0.000 | - | - | - | - |
| reason=missing_number | 6 | 0.500 | 0.000 | - | - | - | - |
| reason=multiple_numbers | 4 | 1.000 | 0.000 | - | - | - | - |
| reason=time_in_past | 6 | 1.000 | 0.000 | - | - | - | - |
| reason=unclear_action | 8 | 0.875 | 0.000 | - | - | - | - |
| reason=unclear_time | 6 | 0.833 | 0.000 | - | - | - | - |
| reason=unsupported | 8 | 0.875 | 0.000 | - | - | - | - |
| wording=seen | 74 | 0.716 | 0.000 | 0.294 | 0.706 | 0.706 | 0.706 |
| bay said=False | 48 | 0.812 | 0.000 | 0.182 | 0.818 | 0.818 | 0.818 |
| bay said=True | 26 | 0.538 | 0.000 | 0.500 | 0.500 | 0.500 | 0.500 |
| slip=False | 118 | 0.780 | 0.000 | 0.294 | 0.706 | 0.706 | 0.706 |
| slip=True | 2 | 0.500 | 0.000 | - | - | - | - |

## Errors

- confirm4-004: "hey approve 69795 till tomorrow please" expected PROPOSE ALLOW 69795, until Wed 02 Dec 23:59; got NEEDS_REVIEW (unsure)
- confirm4-007: "let number 1788 in for a while" expected NEEDS_REVIEW (unclear_time); got NEEDS_REVIEW (unclear_action)
- confirm4-013: "And 3 5 6 5 until 12 pm." expected NEEDS_REVIEW (unclear_action); got NEEDS_REVIEW (missing_number)
- confirm4-020: "hey let number 27490 in for bay 2 please" expected PROPOSE ALLOW 27490, permanent; got NEEDS_REVIEW (unsure)
- confirm4-025: "hey approve number seventy one thousand twenty seven for one week please" expected PROPOSE ALLOW 71027, until Tue 08 Dec 07:35; got NEEDS_REVIEW (unsure)
- confirm4-032: "what's the weather today" expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- confirm4-035: "Please allow plate seven six five four seven bay one." expected PROPOSE ALLOW 76547, permanent; got NEEDS_REVIEW (unsure)
- confirm4-040: "allow the car for 2 hours" expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- confirm4-045: "hey add forty six sixty three bay two" expected PROPOSE ALLOW 4663, permanent; got NEEDS_REVIEW (unsure)
- confirm4-048: "approve car 2667 till tomorrow at 5" expected NEEDS_REVIEW (ambiguous_time); got NEEDS_REVIEW (unsure)
- confirm4-049: "let car number 556 in till 10 PM" expected PROPOSE ALLOW 556, until Sat 05 Dec 22:00; got NEEDS_REVIEW (unsure)
- confirm4-061: "approve 895 for a week" expected PROPOSE ALLOW 895, until Sat 12 Dec 21:50; got NEEDS_REVIEW (unsure)
- confirm4-062: "let car 6 9 in for a week please" expected PROPOSE ALLOW 69, until Tue 08 Dec 07:35; got NEEDS_REVIEW (unsure)
- confirm4-065: "Please take car 32700 off the list." expected PROPOSE REMOVE 32700; got UNSUPPORTED
- confirm4-068: "Add plate number 9236 in bay one." expected PROPOSE ALLOW 9236, permanent; got NEEDS_REVIEW (unclear_action)
- confirm4-079: "Allow the car until 10pm." expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- confirm4-080: "allow car number four six six two three bay two" expected PROPOSE ALLOW 46623, permanent; got NEEDS_REVIEW (unsure)
- confirm4-083: "Let plate 8640 in bay 1 for 30 minutes." expected PROPOSE ALLOW 8640, until Sat 05 Dec 22:20; got NEEDS_REVIEW (unclear_action)
- confirm4-084: "allow plate 680 until tomorrow 3PM for bay 2 please" expected PROPOSE ALLOW 680, until Wed 02 Dec 15:00; got NEEDS_REVIEW (unsure)
- confirm4-085: "Allow 20976 bay 1 till 11 pm tonight." expected PROPOSE ALLOW 20976, until Thu 26 Nov 23:00; got NEEDS_REVIEW (multiple_numbers)
- confirm4-093: "Add car number four thousand nine hundred forty in bay 2 please." expected PROPOSE ALLOW 4940, permanent; got NEEDS_REVIEW (unsure)
- confirm4-098: "add 50291 until Monday in bay two please" expected PROPOSE ALLOW 50291, until Mon 30 Nov 23:59; got NEEDS_REVIEW (unsure)
- confirm4-109: "Please let 4 8 2 in." expected PROPOSE ALLOW 482, permanent; got NEEDS_REVIEW (unsure)
- confirm4-110: "let number 57865 in until tomorrow please" expected PROPOSE ALLOW 57865, until Fri 27 Nov 23:59; got NEEDS_REVIEW (unsure)
- confirm4-113: "Add number 6541 until 11 PM in bay 2 please." expected PROPOSE ALLOW 6541, until Sat 05 Dec 23:00; got NEEDS_REVIEW (unsure)
- confirm4-116: "allow my brother's car" expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- confirm4-118: "Okay add plate 1791 until two pm for bay 1." expected PROPOSE ALLOW 1791, until Tue 01 Dec 14:00; got NEEDS_REVIEW (unsure)
