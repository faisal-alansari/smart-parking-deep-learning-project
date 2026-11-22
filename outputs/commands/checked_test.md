# Model C: checked on test

Time per command: 142 ms mean, 407 ms p95.

| slice | n | exact | dangerous | needless question | action | number | until |
|---|---|---|---|---|---|---|---|
| all | 160 | 0.487 | 0.006 | 0.621 | 0.368 | 0.379 | 0.379 |
| kind=allow | 70 | 0.300 | 0.000 | 0.700 | 0.300 | 0.300 | 0.300 |
| kind=remove | 25 | 0.560 | 0.040 | 0.400 | 0.560 | 0.600 | 0.600 |
| kind=review | 49 | 0.755 | 0.000 | - | - | - | - |
| kind=single_digit | 6 | 0.500 | 0.000 | - | - | - | - |
| kind=unsupported | 10 | 0.300 | 0.000 | - | - | - | - |
| reason=ambiguous_time | 5 | 0.800 | 0.000 | - | - | - | - |
| reason=invalid_number | 5 | 0.800 | 0.000 | - | - | - | - |
| reason=missing_number | 8 | 0.625 | 0.000 | - | - | - | - |
| reason=multiple_numbers | 6 | 0.667 | 0.000 | - | - | - | - |
| reason=time_in_past | 5 | 1.000 | 0.000 | - | - | - | - |
| reason=unclear_action | 12 | 0.833 | 0.000 | - | - | - | - |
| reason=unclear_time | 8 | 0.625 | 0.000 | - | - | - | - |
| reason=unsupported | 10 | 0.300 | 0.000 | - | - | - | - |
| wording=seen | 74 | 0.568 | 0.000 | 0.453 | 0.547 | 0.547 | 0.547 |
| wording=unseen | 33 | 0.000 | 0.030 | 0.968 | 0.000 | 0.032 | 0.032 |
| bay said=False | 69 | 0.420 | 0.014 | 0.587 | 0.397 | 0.413 | 0.413 |
| bay said=True | 38 | 0.342 | 0.000 | 0.688 | 0.312 | 0.312 | 0.312 |
| slip=False | 154 | 0.481 | 0.006 | 0.621 | 0.368 | 0.379 | 0.379 |
| slip=True | 6 | 0.667 | 0.000 | - | - | - | - |

## Errors

- test-001: "Whitelist number 64278 for some time." expected NEEDS_REVIEW (unclear_time); got NEEDS_REVIEW (unclear_action)
- test-003: "please let car number 27677 in" expected PROPOSE ALLOW 27677, permanent; got NEEDS_REVIEW (unsure)
- test-005: "Could you allow number one oh six in bay 2 until tomorrow." expected PROPOSE ALLOW 106, until Fri 27 Nov 23:59; got NEEDS_REVIEW (unsure)
- test-006: "Give access to the white car." expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- test-007: "Let car six six one seven in." expected PROPOSE ALLOW 6617, permanent; got NEEDS_REVIEW (unsure)
- test-008: "could you allow vehicle 73569 bay 3" expected PROPOSE ALLOW 73569, permanent; got NEEDS_REVIEW (unsure)
- test-009: "Hey let number three eight four three in." expected PROPOSE ALLOW 3843, permanent; got NEEDS_REVIEW (unsure)
- test-011: "grant access to the car 69488 parking number two till tomorrow 12p.m. thanks" expected PROPOSE ALLOW 69488, until Fri 27 Nov 12:00; got NEEDS_REVIEW (unclear_action)
- test-013: "add plate 3296 until midnight thanks" expected PROPOSE ALLOW 3296, until Fri 27 Nov 00:00; got NEEDS_REVIEW (unsure)
- test-014: "Allow cars 7 8 4 5 7 and four two eight." expected NEEDS_REVIEW (multiple_numbers); got UNSUPPORTED
- test-015: "revoke 1 from bay 2 thanks" expected NEEDS_REVIEW (single_digit_number): REMOVE 1; got NEEDS_REVIEW (unclear_action)
- test-018: "Allow the car 441 please." expected PROPOSE ALLOW 441, permanent; got UNSUPPORTED
- test-020: "7930 can park till tomorrow parking number 2" expected PROPOSE ALLOW 7930, until Thu 03 Dec 23:59; got NEEDS_REVIEW (unclear_action)
- test-021: "Um grant access to plate number fifty seven thousand seven hundred forty three." expected PROPOSE ALLOW 57743, permanent; got NEEDS_REVIEW (unclear_action)
- test-030: "car 187271 can park" expected NEEDS_REVIEW (invalid_number); got UNSUPPORTED
- test-031: "Hey allow car number seven four seven four until 7:15 pm tonight bay one." expected PROPOSE ALLOW 7474, until Wed 02 Dec 19:15; got NEEDS_REVIEW (unsure)
- test-033: "okay approve vehicle 6 till Saturday bay one thank you" expected NEEDS_REVIEW (single_digit_number): ALLOW 6, until Sat 05 Dec 23:59; got NEEDS_REVIEW (unsure)
- test-036: "Give plate number 277 access please." expected PROPOSE ALLOW 277, permanent; got NEEDS_REVIEW (unclear_action)
- test-040: "can you aloud car 390 bay three until 9:15 AM thank you" expected NEEDS_REVIEW (unclear_action); got NEEDS_REVIEW (missing_number)
- test-041: "Could you add plate number six eight six seven seven." expected PROPOSE ALLOW 68677, permanent; got NEEDS_REVIEW (unsure)
- test-042: "let plate number 63217 in until ten pm" expected PROPOSE ALLOW 63217, until Sun 29 Nov 22:00; got NEEDS_REVIEW (unsure)
- test-053: "don't allow number 294 anymore" expected PROPOSE REMOVE 294; got NEEDS_REVIEW (unsure)
- test-058: "Don't allow car two eight anymore thank you." expected PROPOSE REMOVE 28; got PROPOSE ALLOW 28, permanent
- test-059: "Is eight thousand thirty seven still allowed?" expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- test-061: "um grant access to seven one one six five until today" expected PROPOSE ALLOW 71165, until Sun 29 Nov 23:59; got NEEDS_REVIEW (unclear_action)
- test-062: "Could you add plate number 16717." expected PROPOSE ALLOW 16717, permanent; got NEEDS_REVIEW (unsure)
- test-063: "Approve car number seven eight seven four six thank you." expected PROPOSE ALLOW 78746, permanent; got NEEDS_REVIEW (unsure)
- test-064: "What time is it?" expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- test-065: "could you cancel car number 69831" expected PROPOSE REMOVE 69831; got NEEDS_REVIEW (unclear_action)
- test-068: "please approve number 2460 for two hours for bay 2" expected PROPOSE ALLOW 2460, until Thu 26 Nov 10:15; got NEEDS_REVIEW (unsure)
- test-071: "Permit plate number 35212 until 11:15 AM." expected PROPOSE ALLOW 35212, until Thu 26 Nov 11:15; got NEEDS_REVIEW (unclear_action)
- test-072: "six eight three oh seven can park until Monday thanks" expected PROPOSE ALLOW 68307, until Mon 07 Dec 23:59; got NEEDS_REVIEW (unclear_action)
- test-073: "Don't allow three three eight eight one anymore." expected PROPOSE REMOVE 33881; got NEEDS_REVIEW (unsure)
- test-074: "add vehicle 8 2 0 8 for six days in bay three please" expected PROPOSE ALLOW 8208, until Tue 08 Dec 14:40; got NEEDS_REVIEW (unsure)
- test-075: "add the car 9173 for a week for bay one" expected PROPOSE ALLOW 9173, until Wed 09 Dec 14:40; got NEEDS_REVIEW (unclear_time)
- test-077: "Block plate number 76141 from bay 2." expected PROPOSE REMOVE 76141; got NEEDS_REVIEW (unclear_action)
- test-078: "3574 can park until tomorrow." expected PROPOSE ALLOW 3574, until Fri 27 Nov 23:59; got NEEDS_REVIEW (unclear_action)
- test-082: "Give plate 9007 access." expected PROPOSE ALLOW 9007, permanent; got NEEDS_REVIEW (unclear_action)
- test-084: "Can you permit number 7." expected NEEDS_REVIEW (single_digit_number): ALLOW 7, permanent; got NEEDS_REVIEW (unclear_action)
- test-093: "give 35087 access until end of day" expected PROPOSE ALLOW 35087, until Sun 29 Nov 23:59; got NEEDS_REVIEW (unclear_action)
- test-094: "Cancel car 83438." expected PROPOSE REMOVE 83438; got NEEDS_REVIEW (unclear_action)
- test-095: "um give car 8 7 3 access in slot 2 thank you" expected PROPOSE ALLOW 873, permanent; got NEEDS_REVIEW (unclear_action)
- test-097: "Edit car 15744." expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- test-101: "Car 3452 can park until he leaves." expected NEEDS_REVIEW (unclear_time); got UNSUPPORTED
- test-102: "Add plate 85144 for forty five minutes for bay one." expected PROPOSE ALLOW 85144, until Sun 29 Nov 21:55; got NEEDS_REVIEW (unsure)
- test-103: "Whitelist plate four two seven five five for one week." expected PROPOSE ALLOW 42755, until Sun 06 Dec 21:10; got NEEDS_REVIEW (unclear_action)
- test-104: "can you take vehicle sixty two off the list thanks" expected PROPOSE REMOVE 62; got UNSUPPORTED
- test-105: "hey give number 4 0 3 access please" expected PROPOSE ALLOW 403, permanent; got NEEDS_REVIEW (unclear_action)
- test-107: "approve the car 51 until 5 p.m." expected PROPOSE ALLOW 51, until Wed 02 Dec 17:00; got UNSUPPORTED
- test-109: "Okay give plate 955 access in parking 2 thank you." expected PROPOSE ALLOW 955, permanent; got NEEDS_REVIEW (unclear_action)
- test-112: "Block the car five six from bay 2." expected PROPOSE REMOVE 56; got NEEDS_REVIEW (unclear_action)
- test-113: "Grant access to car 8006 spot two thank you." expected PROPOSE ALLOW 8006, permanent; got NEEDS_REVIEW (multiple_numbers)
- test-114: "Give plate number 1522 access until tomorrow." expected PROPOSE ALLOW 1522, until Fri 27 Nov 23:59; got NEEDS_REVIEW (unclear_action)
- test-115: "Can you and the car seventy nine eighteen." expected NEEDS_REVIEW (unclear_action); got UNSUPPORTED
- test-116: "Hey car 7754 can park till 5:30 pm in parking five." expected PROPOSE ALLOW 7754, until Wed 02 Dec 17:30; got NEEDS_REVIEW (unclear_action)
- test-117: "permit the guest" expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- test-118: "Please add plate number 7 1 9 3 for bay five thanks." expected PROPOSE ALLOW 7193, permanent; got NEEDS_REVIEW (unsure)
- test-119: "Please permit plate number 4695 until tomorrow at 10:15 PM." expected PROPOSE ALLOW 4695, until Thu 03 Dec 22:15; got NEEDS_REVIEW (unclear_action)
- test-123: "Please allow number 80 in bay 3 thank you." expected PROPOSE ALLOW 80, permanent; got NEEDS_REVIEW (unclear_action)
- test-125: "Permit car eighty three thousand seven hundred twenty eight until Wednesday." expected NEEDS_REVIEW (unclear_time); got UNSUPPORTED
- test-126: "Take car three four two one eight off the list." expected PROPOSE REMOVE 34218; got UNSUPPORTED
- test-127: "Can you allow plate number 39429 in bay 2." expected PROPOSE ALLOW 39429, permanent; got NEEDS_REVIEW (unsure)
- test-128: "Could you allow 7464 till Monday." expected PROPOSE ALLOW 7464, until Mon 07 Dec 23:59; got NEEDS_REVIEW (unsure)
- test-129: "approve 4845 in bay two please" expected PROPOSE ALLOW 4845, permanent; got NEEDS_REVIEW (unsure)
- test-132: "give plate 28424 access until tomorrow at eight am spot 2 thanks" expected PROPOSE ALLOW 28424, until Mon 30 Nov 08:00; got NEEDS_REVIEW (unclear_action)
- test-134: "please approve the car 58032 till 11 PM tonight" expected PROPOSE ALLOW 58032, until Wed 02 Dec 23:00; got NEEDS_REVIEW (unsure)
- test-136: "Can you grant access to plate 8860 thanks." expected PROPOSE ALLOW 8860, permanent; got NEEDS_REVIEW (unclear_action)
- test-138: "um whitelist vehicle 23815" expected PROPOSE ALLOW 23815, permanent; got UNSUPPORTED
- test-140: "permit the guest till tomorrow" expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- test-141: "Could you revoke five four two six one from bay 1." expected PROPOSE REMOVE 54261; got NEEDS_REVIEW (unclear_action)
- test-142: "let number three four three in" expected PROPOSE ALLOW 343, permanent; got NEEDS_REVIEW (unsure)
- test-144: "Which bay is free?" expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- test-147: "Could you remove car number eighty four thousand two hundred forty four from bay 1 thank you." expected PROPOSE REMOVE 84244; got NEEDS_REVIEW (missing_number)
- test-149: "change the time for four hundred fifty six" expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- test-150: "Could you grant access to vehicle 50874." expected PROPOSE ALLOW 50874, permanent; got UNSUPPORTED
- test-152: "let plate five five one four in" expected PROPOSE ALLOW 5514, permanent; got NEEDS_REVIEW (unsure)
- test-154: "allow cars 82205 and 6553" expected NEEDS_REVIEW (multiple_numbers); got UNSUPPORTED
- test-155: "allow number 2 7 0 7 until 7" expected NEEDS_REVIEW (ambiguous_time); got NEEDS_REVIEW (unsure)
- test-156: "please permit the car four five two five oh" expected PROPOSE ALLOW 45250, permanent; got UNSUPPORTED
- test-157: "who is parked in bay 1" expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- test-158: "let 1 4 1 1 7 in thanks" expected PROPOSE ALLOW 14117, permanent; got NEEDS_REVIEW (unsure)
- test-160: "Open the gate." expected UNSUPPORTED; got NEEDS_REVIEW (missing_number)
