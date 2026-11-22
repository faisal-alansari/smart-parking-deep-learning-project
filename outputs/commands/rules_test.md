# Model C: rules on test

Time per command: 0 ms mean, 0 ms p95.

| slice | n | exact | dangerous | needless question | action | number | until |
|---|---|---|---|---|---|---|---|
| all | 160 | 0.644 | 0.019 | 0.295 | 0.674 | 0.705 | 0.705 |
| kind=allow | 70 | 0.671 | 0.000 | 0.329 | 0.671 | 0.671 | 0.671 |
| kind=remove | 25 | 0.680 | 0.120 | 0.200 | 0.680 | 0.800 | 0.800 |
| kind=review | 49 | 0.673 | 0.000 | - | - | - | - |
| kind=single_digit | 6 | 0.667 | 0.000 | - | - | - | - |
| kind=unsupported | 10 | 0.200 | 0.000 | - | - | - | - |
| reason=ambiguous_time | 5 | 0.400 | 0.000 | - | - | - | - |
| reason=invalid_number | 5 | 0.600 | 0.000 | - | - | - | - |
| reason=missing_number | 8 | 0.625 | 0.000 | - | - | - | - |
| reason=multiple_numbers | 6 | 1.000 | 0.000 | - | - | - | - |
| reason=time_in_past | 5 | 0.600 | 0.000 | - | - | - | - |
| reason=unclear_action | 12 | 1.000 | 0.000 | - | - | - | - |
| reason=unclear_time | 8 | 0.250 | 0.000 | - | - | - | - |
| reason=unsupported | 10 | 0.200 | 0.000 | - | - | - | - |
| wording=seen | 74 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 |
| wording=unseen | 33 | 0.000 | 0.091 | 0.903 | 0.000 | 0.097 | 0.097 |
| bay said=False | 69 | 0.681 | 0.043 | 0.286 | 0.667 | 0.714 | 0.714 |
| bay said=True | 38 | 0.711 | 0.000 | 0.312 | 0.688 | 0.688 | 0.688 |
| slip=False | 154 | 0.630 | 0.019 | 0.295 | 0.674 | 0.705 | 0.705 |
| slip=True | 6 | 1.000 | 0.000 | - | - | - | - |

## Errors

- test-001: "Whitelist number 64278 for some time." expected NEEDS_REVIEW (unclear_time); got NEEDS_REVIEW (unclear_action)
- test-006: "Give access to the white car." expected NEEDS_REVIEW (missing_number); got NEEDS_REVIEW (unclear_action)
- test-011: "grant access to the car 69488 parking number two till tomorrow 12p.m. thanks" expected PROPOSE ALLOW 69488, until Fri 27 Nov 12:00; got NEEDS_REVIEW (unclear_action)
- test-015: "revoke 1 from bay 2 thanks" expected NEEDS_REVIEW (single_digit_number): REMOVE 1; got NEEDS_REVIEW (unclear_action)
- test-016: "Give number 41830 access till nine." expected NEEDS_REVIEW (ambiguous_time); got NEEDS_REVIEW (unclear_action)
- test-020: "7930 can park till tomorrow parking number 2" expected PROPOSE ALLOW 7930, until Thu 03 Dec 23:59; got NEEDS_REVIEW (unclear_action)
- test-021: "Um grant access to plate number fifty seven thousand seven hundred forty three." expected PROPOSE ALLOW 57743, permanent; got NEEDS_REVIEW (unclear_action)
- test-025: "list all permits" expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- test-028: "Whitelist 822 until 3:30." expected NEEDS_REVIEW (ambiguous_time); got NEEDS_REVIEW (unclear_action)
- test-030: "car 187271 can park" expected NEEDS_REVIEW (invalid_number); got NEEDS_REVIEW (unclear_action)
- test-032: "Permit number 1531 till 6 am." expected NEEDS_REVIEW (time_in_past); got NEEDS_REVIEW (unclear_action)
- test-036: "Give plate number 277 access please." expected PROPOSE ALLOW 277, permanent; got NEEDS_REVIEW (unclear_action)
- test-038: "grant access to plate 39461 until tonight" expected NEEDS_REVIEW (unclear_time); got NEEDS_REVIEW (unclear_action)
- test-046: "Grant access to eight hundred seven until 1:30." expected NEEDS_REVIEW (ambiguous_time); got NEEDS_REVIEW (unclear_action)
- test-048: "Check car 39." expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- test-049: "Good morning." expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- test-053: "don't allow number 294 anymore" expected PROPOSE REMOVE 294; got PROPOSE ALLOW 294, permanent
- test-056: "Plate 9 6 5 1 3 9 can park until 3 PM." expected NEEDS_REVIEW (invalid_number); got NEEDS_REVIEW (unclear_action)
- test-058: "Don't allow car two eight anymore thank you." expected PROPOSE REMOVE 28; got PROPOSE ALLOW 28, permanent
- test-061: "um grant access to seven one one six five until today" expected PROPOSE ALLOW 71165, until Sun 29 Nov 23:59; got NEEDS_REVIEW (unclear_action)
- test-065: "could you cancel car number 69831" expected PROPOSE REMOVE 69831; got NEEDS_REVIEW (unclear_action)
- test-071: "Permit plate number 35212 until 11:15 AM." expected PROPOSE ALLOW 35212, until Thu 26 Nov 11:15; got NEEDS_REVIEW (unclear_action)
- test-072: "six eight three oh seven can park until Monday thanks" expected PROPOSE ALLOW 68307, until Mon 07 Dec 23:59; got NEEDS_REVIEW (unclear_action)
- test-073: "Don't allow three three eight eight one anymore." expected PROPOSE REMOVE 33881; got PROPOSE ALLOW 33881, permanent
- test-077: "Block plate number 76141 from bay 2." expected PROPOSE REMOVE 76141; got NEEDS_REVIEW (unclear_action)
- test-078: "3574 can park until tomorrow." expected PROPOSE ALLOW 3574, until Fri 27 Nov 23:59; got NEEDS_REVIEW (unclear_action)
- test-082: "Give plate 9007 access." expected PROPOSE ALLOW 9007, permanent; got NEEDS_REVIEW (unclear_action)
- test-084: "Can you permit number 7." expected NEEDS_REVIEW (single_digit_number): ALLOW 7, permanent; got NEEDS_REVIEW (unclear_action)
- test-093: "give 35087 access until end of day" expected PROPOSE ALLOW 35087, until Sun 29 Nov 23:59; got NEEDS_REVIEW (unclear_action)
- test-094: "Cancel car 83438." expected PROPOSE REMOVE 83438; got NEEDS_REVIEW (unclear_action)
- test-095: "um give car 8 7 3 access in slot 2 thank you" expected PROPOSE ALLOW 873, permanent; got NEEDS_REVIEW (unclear_action)
- test-097: "Edit car 15744." expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- test-101: "Car 3452 can park until he leaves." expected NEEDS_REVIEW (unclear_time); got NEEDS_REVIEW (unclear_action)
- test-103: "Whitelist plate four two seven five five for one week." expected PROPOSE ALLOW 42755, until Sun 06 Dec 21:10; got NEEDS_REVIEW (unclear_action)
- test-105: "hey give number 4 0 3 access please" expected PROPOSE ALLOW 403, permanent; got NEEDS_REVIEW (unclear_action)
- test-108: "Whitelist plate number three four seven eight two until next month." expected NEEDS_REVIEW (unclear_time); got NEEDS_REVIEW (unclear_action)
- test-109: "Okay give plate 955 access in parking 2 thank you." expected PROPOSE ALLOW 955, permanent; got NEEDS_REVIEW (unclear_action)
- test-112: "Block the car five six from bay 2." expected PROPOSE REMOVE 56; got NEEDS_REVIEW (unclear_action)
- test-113: "Grant access to car 8006 spot two thank you." expected PROPOSE ALLOW 8006, permanent; got NEEDS_REVIEW (unclear_action)
- test-114: "Give plate number 1522 access until tomorrow." expected PROPOSE ALLOW 1522, until Fri 27 Nov 23:59; got NEEDS_REVIEW (unclear_action)
- test-116: "Hey car 7754 can park till 5:30 pm in parking five." expected PROPOSE ALLOW 7754, until Wed 02 Dec 17:30; got NEEDS_REVIEW (unclear_action)
- test-117: "permit the guest" expected NEEDS_REVIEW (missing_number); got NEEDS_REVIEW (unclear_action)
- test-119: "Please permit plate number 4695 until tomorrow at 10:15 PM." expected PROPOSE ALLOW 4695, until Thu 03 Dec 22:15; got NEEDS_REVIEW (unclear_action)
- test-120: "permit plate 96906 till 10a.m." expected NEEDS_REVIEW (time_in_past); got NEEDS_REVIEW (unclear_action)
- test-125: "Permit car eighty three thousand seven hundred twenty eight until Wednesday." expected NEEDS_REVIEW (unclear_time); got NEEDS_REVIEW (unclear_action)
- test-132: "give plate 28424 access until tomorrow at eight am spot 2 thanks" expected PROPOSE ALLOW 28424, until Mon 30 Nov 08:00; got NEEDS_REVIEW (unclear_action)
- test-136: "Can you grant access to plate 8860 thanks." expected PROPOSE ALLOW 8860, permanent; got NEEDS_REVIEW (unclear_action)
- test-138: "um whitelist vehicle 23815" expected PROPOSE ALLOW 23815, permanent; got NEEDS_REVIEW (unclear_action)
- test-140: "permit the guest till tomorrow" expected NEEDS_REVIEW (missing_number); got NEEDS_REVIEW (unclear_action)
- test-141: "Could you revoke five four two six one from bay 1." expected PROPOSE REMOVE 54261; got NEEDS_REVIEW (unclear_action)
- test-144: "Which bay is free?" expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- test-145: "permit number 79 until tomorrow afternoon" expected NEEDS_REVIEW (unclear_time); got NEEDS_REVIEW (unclear_action)
- test-149: "change the time for four hundred fifty six" expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- test-150: "Could you grant access to vehicle 50874." expected PROPOSE ALLOW 50874, permanent; got NEEDS_REVIEW (unclear_action)
- test-156: "please permit the car four five two five oh" expected PROPOSE ALLOW 45250, permanent; got NEEDS_REVIEW (unclear_action)
- test-157: "who is parked in bay 1" expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- test-160: "Open the gate." expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
