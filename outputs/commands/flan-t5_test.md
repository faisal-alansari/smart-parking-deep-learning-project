# Model C: flan-t5 on test

Time per command: 232 ms mean, 450 ms p95.

| slice | n | exact | dangerous | needless question | action | number | until |
|---|---|---|---|---|---|---|---|
| all | 160 | 0.119 | 0.138 | 0.842 | 0.063 | 0.147 | 0.074 |
| kind=allow | 70 | 0.000 | 0.143 | 0.871 | 0.000 | 0.114 | 0.014 |
| kind=remove | 25 | 0.240 | 0.000 | 0.760 | 0.240 | 0.240 | 0.240 |
| kind=review | 49 | 0.122 | 0.204 | - | - | - | - |
| kind=single_digit | 6 | 0.000 | 0.167 | - | - | - | - |
| kind=unsupported | 10 | 0.700 | 0.100 | - | - | - | - |
| reason=ambiguous_time | 5 | 0.000 | 0.400 | - | - | - | - |
| reason=invalid_number | 5 | 0.400 | 0.200 | - | - | - | - |
| reason=missing_number | 8 | 0.500 | 0.000 | - | - | - | - |
| reason=multiple_numbers | 6 | 0.000 | 0.167 | - | - | - | - |
| reason=time_in_past | 5 | 0.000 | 0.000 | - | - | - | - |
| reason=unclear_action | 12 | 0.000 | 0.167 | - | - | - | - |
| reason=unclear_time | 8 | 0.000 | 0.500 | - | - | - | - |
| reason=unsupported | 10 | 0.700 | 0.100 | - | - | - | - |
| wording=seen | 74 | 0.054 | 0.108 | 0.844 | 0.062 | 0.141 | 0.078 |
| wording=unseen | 33 | 0.061 | 0.121 | 0.839 | 0.065 | 0.161 | 0.065 |
| bay said=False | 69 | 0.058 | 0.130 | 0.841 | 0.063 | 0.143 | 0.079 |
| bay said=True | 38 | 0.053 | 0.079 | 0.844 | 0.062 | 0.156 | 0.062 |
| slip=False | 154 | 0.123 | 0.136 | 0.842 | 0.063 | 0.147 | 0.074 |
| slip=True | 6 | 0.000 | 0.167 | - | - | - | - |

## Errors

- test-001: "Whitelist number 64278 for some time." expected NEEDS_REVIEW (unclear_time); got PROPOSE REMOVE 64278
- test-002: "let the delivery guy in until tomorrow" expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- test-003: "please let car number 27677 in" expected PROPOSE ALLOW 27677, permanent; got PROPOSE REMOVE 27677
- test-004: "can you allow number 1 please" expected NEEDS_REVIEW (single_digit_number): ALLOW 1, permanent; got UNSUPPORTED
- test-005: "Could you allow number one oh six in bay 2 until tomorrow." expected PROPOSE ALLOW 106, until Fri 27 Nov 23:59; got UNSUPPORTED
- test-007: "Let car six six one seven in." expected PROPOSE ALLOW 6617, permanent; got NEEDS_REVIEW (missing_number)
- test-008: "could you allow vehicle 73569 bay 3" expected PROPOSE ALLOW 73569, permanent; got NEEDS_REVIEW (missing_number)
- test-009: "Hey let number three eight four three in." expected PROPOSE ALLOW 3843, permanent; got UNSUPPORTED
- test-010: "and car number 94842" expected NEEDS_REVIEW (unclear_action); got PROPOSE REMOVE 94842
- test-011: "grant access to the car 69488 parking number two till tomorrow 12p.m. thanks" expected PROPOSE ALLOW 69488, until Fri 27 Nov 12:00; got PROPOSE REMOVE 69488
- test-012: "remove number 1 from bay 1" expected NEEDS_REVIEW (single_digit_number): REMOVE 1; got UNSUPPORTED
- test-013: "add plate 3296 until midnight thanks" expected PROPOSE ALLOW 3296, until Fri 27 Nov 00:00; got UNSUPPORTED
- test-014: "Allow cars 7 8 4 5 7 and four two eight." expected NEEDS_REVIEW (multiple_numbers); got NEEDS_REVIEW (missing_number)
- test-015: "revoke 1 from bay 2 thanks" expected NEEDS_REVIEW (single_digit_number): REMOVE 1; got UNSUPPORTED
- test-016: "Give number 41830 access till nine." expected NEEDS_REVIEW (ambiguous_time); got UNSUPPORTED
- test-018: "Allow the car 441 please." expected PROPOSE ALLOW 441, permanent; got NEEDS_REVIEW (missing_number)
- test-019: "Allow plate number 245 for bay 1 thank you." expected PROPOSE ALLOW 245, permanent; got UNSUPPORTED
- test-020: "7930 can park till tomorrow parking number 2" expected PROPOSE ALLOW 7930, until Thu 03 Dec 23:59; got UNSUPPORTED
- test-021: "Um grant access to plate number fifty seven thousand seven hundred forty three." expected PROPOSE ALLOW 57743, permanent; got UNSUPPORTED
- test-022: "Take nine hundred five off the list please." expected PROPOSE REMOVE 905; got UNSUPPORTED
- test-024: "delete the visitor" expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- test-025: "list all permits" expected UNSUPPORTED; got NEEDS_REVIEW (missing_number)
- test-027: "could you take vehicle forty eight thousand six hundred thirteen off the list thank you" expected PROPOSE REMOVE 48613; got NEEDS_REVIEW (missing_number)
- test-028: "Whitelist 822 until 3:30." expected NEEDS_REVIEW (ambiguous_time); got PROPOSE REMOVE 330
- test-029: "let 48635 in until 7:30 pm tonight thanks" expected PROPOSE ALLOW 48635, until Wed 02 Dec 19:30; got UNSUPPORTED
- test-030: "car 187271 can park" expected NEEDS_REVIEW (invalid_number); got UNSUPPORTED
- test-031: "Hey allow car number seven four seven four until 7:15 pm tonight bay one." expected PROPOSE ALLOW 7474, until Wed 02 Dec 19:15; got UNSUPPORTED
- test-032: "Permit number 1531 till 6 am." expected NEEDS_REVIEW (time_in_past); got UNSUPPORTED
- test-033: "okay approve vehicle 6 till Saturday bay one thank you" expected NEEDS_REVIEW (single_digit_number): ALLOW 6, until Sat 05 Dec 23:59; got UNSUPPORTED
- test-034: "Add car number 726 for bay two until tomorrow." expected PROPOSE ALLOW 726, until Thu 03 Dec 23:59; got PROPOSE REMOVE 726
- test-035: "Allow car number 8277 until next Monday." expected NEEDS_REVIEW (unclear_time); got PROPOSE REMOVE 8277
- test-036: "Give plate number 277 access please." expected PROPOSE ALLOW 277, permanent; got UNSUPPORTED
- test-037: "Number fifty nine for two hours." expected NEEDS_REVIEW (unclear_action); got UNSUPPORTED
- test-038: "grant access to plate 39461 until tonight" expected NEEDS_REVIEW (unclear_time); got UNSUPPORTED
- test-039: "Approve 4942 thanks." expected PROPOSE ALLOW 4942, permanent; got UNSUPPORTED
- test-040: "can you aloud car 390 bay three until 9:15 AM thank you" expected NEEDS_REVIEW (unclear_action); got NEEDS_REVIEW (missing_number)
- test-041: "Could you add plate number six eight six seven seven." expected PROPOSE ALLOW 68677, permanent; got UNSUPPORTED
- test-042: "let plate number 63217 in until ten pm" expected PROPOSE ALLOW 63217, until Sun 29 Nov 22:00; got NEEDS_REVIEW (missing_number)
- test-043: "Allow car number 6744 for bay 2 till 9 p.m. tonight thank you." expected PROPOSE ALLOW 6744, until Wed 02 Dec 21:00; got UNSUPPORTED
- test-044: "Okay delete vehicle seven eight two one." expected PROPOSE REMOVE 7821; got NEEDS_REVIEW (missing_number)
- test-045: "delete car 3 2 3 please" expected PROPOSE REMOVE 323; got NEEDS_REVIEW (missing_number)
- test-046: "Grant access to eight hundred seven until 1:30." expected NEEDS_REVIEW (ambiguous_time); got UNSUPPORTED
- test-047: "Allow the car four thousand five hundred forty seven please." expected PROPOSE ALLOW 4547, permanent; got NEEDS_REVIEW (missing_number)
- test-048: "Check car 39." expected UNSUPPORTED; got NEEDS_REVIEW (missing_number)
- test-050: "add car 9 5 5 9 9 till seven fifteen PM" expected PROPOSE ALLOW 95599, until Wed 02 Dec 19:15; got NEEDS_REVIEW (missing_number)
- test-051: "13495 please" expected NEEDS_REVIEW (unclear_action); got UNSUPPORTED
- test-052: "add car 34434 until six thirty am today" expected NEEDS_REVIEW (time_in_past); got NEEDS_REVIEW (missing_number)
- test-053: "don't allow number 294 anymore" expected PROPOSE REMOVE 294; got UNSUPPORTED
- test-054: "allow number 6 5 till nine p.m." expected PROPOSE ALLOW 65, until Wed 02 Dec 21:00; got UNSUPPORTED
- test-055: "um take number 421 off the list thank you" expected PROPOSE REMOVE 421; got UNSUPPORTED
- test-056: "Plate 9 6 5 1 3 9 can park until 3 PM." expected NEEDS_REVIEW (invalid_number); got NEEDS_REVIEW (single_digit_number): REMOVE 9
- test-057: "Remove three three seven three and nine thousand thirty one." expected NEEDS_REVIEW (multiple_numbers); got NEEDS_REVIEW (missing_number)
- test-058: "Don't allow car two eight anymore thank you." expected PROPOSE REMOVE 28; got UNSUPPORTED
- test-061: "um grant access to seven one one six five until today" expected PROPOSE ALLOW 71165, until Sun 29 Nov 23:59; got UNSUPPORTED
- test-062: "Could you add plate number 16717." expected PROPOSE ALLOW 16717, permanent; got UNSUPPORTED
- test-063: "Approve car number seven eight seven four six thank you." expected PROPOSE ALLOW 78746, permanent; got NEEDS_REVIEW (missing_number)
- test-066: "remove plate 3663 thanks" expected PROPOSE REMOVE 3663; got UNSUPPORTED
- test-067: "Hey approve number 973 until tomorrow for bay three." expected PROPOSE ALLOW 973, until Fri 27 Nov 23:59; got UNSUPPORTED
- test-068: "please approve number 2460 for two hours for bay 2" expected PROPOSE ALLOW 2460, until Thu 26 Nov 10:15; got UNSUPPORTED
- test-069: "hey add number 95043 until 12p.m. tomorrow thank you" expected PROPOSE ALLOW 95043, until Fri 27 Nov 12:00; got UNSUPPORTED
- test-070: "Approve plate number 37376 till 8p.m. tomorrow thank you." expected PROPOSE ALLOW 37376, until Fri 27 Nov 20:00; got UNSUPPORTED
- test-071: "Permit plate number 35212 until 11:15 AM." expected PROPOSE ALLOW 35212, until Thu 26 Nov 11:15; got PROPOSE REMOVE 35212
- test-072: "six eight three oh seven can park until Monday thanks" expected PROPOSE ALLOW 68307, until Mon 07 Dec 23:59; got UNSUPPORTED
- test-073: "Don't allow three three eight eight one anymore." expected PROPOSE REMOVE 33881; got UNSUPPORTED
- test-074: "add vehicle 8 2 0 8 for six days in bay three please" expected PROPOSE ALLOW 8208, until Tue 08 Dec 14:40; got NEEDS_REVIEW (invalid_number)
- test-075: "add the car 9173 for a week for bay one" expected PROPOSE ALLOW 9173, until Wed 09 Dec 14:40; got PROPOSE REMOVE 9173
- test-077: "Block plate number 76141 from bay 2." expected PROPOSE REMOVE 76141; got UNSUPPORTED
- test-078: "3574 can park until tomorrow." expected PROPOSE ALLOW 3574, until Fri 27 Nov 23:59; got UNSUPPORTED
- test-079: "approve plate 9725 until 6:30 a.m." expected NEEDS_REVIEW (time_in_past); got UNSUPPORTED
- test-080: "remove car 7" expected NEEDS_REVIEW (single_digit_number): REMOVE 7; got UNSUPPORTED
- test-081: "hey aloud vehicle 20 till tomorrow in bay two" expected NEEDS_REVIEW (unclear_action); got UNSUPPORTED
- test-082: "Give plate 9007 access." expected PROPOSE ALLOW 9007, permanent; got UNSUPPORTED
- test-083: "take seven nine eight three off the list from bay 1" expected PROPOSE REMOVE 7983; got UNSUPPORTED
- test-084: "Can you permit number 7." expected NEEDS_REVIEW (single_digit_number): ALLOW 7, permanent; got NEEDS_REVIEW (single_digit_number): REMOVE 7
- test-086: "the car 9799 tomorrow" expected NEEDS_REVIEW (unclear_action); got UNSUPPORTED
- test-087: "approve plate number 7 1 9 3 1 thank you" expected PROPOSE ALLOW 71931, permanent; got UNSUPPORTED
- test-088: "please approve car number 4 4 8 for three days" expected PROPOSE ALLOW 448, until Sun 29 Nov 08:15; got PROPOSE REMOVE 48
- test-090: "um allow plate number 9 3 8 in bay one until 4 p.m. thank you" expected PROPOSE ALLOW 938, until Thu 26 Nov 16:00; got UNSUPPORTED
- test-091: "Add car 7 2 1 for 2 days thanks." expected PROPOSE ALLOW 721, until Sat 28 Nov 08:15; got UNSUPPORTED
- test-092: "let 6 3 3 4 and 8 6 2 4 in" expected NEEDS_REVIEW (multiple_numbers); got NEEDS_REVIEW (missing_number)
- test-093: "give 35087 access until end of day" expected PROPOSE ALLOW 35087, until Sun 29 Nov 23:59; got UNSUPPORTED
- test-095: "um give car 8 7 3 access in slot 2 thank you" expected PROPOSE ALLOW 873, permanent; got NEEDS_REVIEW (missing_number)
- test-096: "Allow car 9757 until six pm." expected PROPOSE ALLOW 9757, until Wed 02 Dec 18:00; got PROPOSE REMOVE 9757
- test-097: "Edit car 15744." expected UNSUPPORTED; got PROPOSE REMOVE 15744
- test-098: "hey let vehicle 8 4 8 7 in till tomorrow please" expected PROPOSE ALLOW 8487, until Mon 30 Nov 23:59; got UNSUPPORTED
- test-099: "approve car number 42281 until 1:30" expected NEEDS_REVIEW (ambiguous_time); got PROPOSE REMOVE 42281
- test-100: "allow number 35017 till 7 a.m." expected NEEDS_REVIEW (time_in_past); got UNSUPPORTED
- test-101: "Car 3452 can park until he leaves." expected NEEDS_REVIEW (unclear_time); got NEEDS_REVIEW (missing_number)
- test-102: "Add plate 85144 for forty five minutes for bay one." expected PROPOSE ALLOW 85144, until Sun 29 Nov 21:55; got UNSUPPORTED
- test-103: "Whitelist plate four two seven five five for one week." expected PROPOSE ALLOW 42755, until Sun 06 Dec 21:10; got NEEDS_REVIEW (missing_number)
- test-104: "can you take vehicle sixty two off the list thanks" expected PROPOSE REMOVE 62; got NEEDS_REVIEW (missing_number)
- test-105: "hey give number 4 0 3 access please" expected PROPOSE ALLOW 403, permanent; got UNSUPPORTED
- test-107: "approve the car 51 until 5 p.m." expected PROPOSE ALLOW 51, until Wed 02 Dec 17:00; got NEEDS_REVIEW (missing_number)
- test-108: "Whitelist plate number three four seven eight two until next month." expected NEEDS_REVIEW (unclear_time); got PROPOSE REMOVE 34782
- test-109: "Okay give plate 955 access in parking 2 thank you." expected PROPOSE ALLOW 955, permanent; got UNSUPPORTED
- test-110: "Can you let number six one five zero six in for thirty minutes." expected PROPOSE ALLOW 61506, until Wed 02 Dec 15:10; got NEEDS_REVIEW (single_digit_number): REMOVE 6
- test-111: "Can you a loud plate 1 2 5 9 8 for bay 5 until end of day." expected NEEDS_REVIEW (unclear_action); got UNSUPPORTED
- test-112: "Block the car five six from bay 2." expected PROPOSE REMOVE 56; got NEEDS_REVIEW (missing_number)
- test-113: "Grant access to car 8006 spot two thank you." expected PROPOSE ALLOW 8006, permanent; got UNSUPPORTED
- test-114: "Give plate number 1522 access until tomorrow." expected PROPOSE ALLOW 1522, until Fri 27 Nov 23:59; got UNSUPPORTED
- test-115: "Can you and the car seventy nine eighteen." expected NEEDS_REVIEW (unclear_action); got NEEDS_REVIEW (missing_number)
- test-116: "Hey car 7754 can park till 5:30 pm in parking five." expected PROPOSE ALLOW 7754, until Wed 02 Dec 17:30; got UNSUPPORTED
- test-117: "permit the guest" expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- test-118: "Please add plate number 7 1 9 3 for bay five thanks." expected PROPOSE ALLOW 7193, permanent; got UNSUPPORTED
- test-119: "Please permit plate number 4695 until tomorrow at 10:15 PM." expected PROPOSE ALLOW 4695, until Thu 03 Dec 22:15; got PROPOSE REMOVE 4695
- test-120: "permit plate 96906 till 10a.m." expected NEEDS_REVIEW (time_in_past); got UNSUPPORTED
- test-121: "Could you aloud number 16182 until tomorrow." expected NEEDS_REVIEW (unclear_action); got UNSUPPORTED
- test-122: "Remove car 4655 from bay 1 thank you." expected PROPOSE REMOVE 4655; got NEEDS_REVIEW (missing_number)
- test-123: "Please allow number 80 in bay 3 thank you." expected PROPOSE ALLOW 80, permanent; got UNSUPPORTED
- test-124: "car 71734 in bay 1" expected NEEDS_REVIEW (unclear_action); got PROPOSE REMOVE 71734
- test-125: "Permit car eighty three thousand seven hundred twenty eight until Wednesday." expected NEEDS_REVIEW (unclear_time); got NEEDS_REVIEW (missing_number)
- test-126: "Take car three four two one eight off the list." expected PROPOSE REMOVE 34218; got NEEDS_REVIEW (missing_number)
- test-127: "Can you allow plate number 39429 in bay 2." expected PROPOSE ALLOW 39429, permanent; got UNSUPPORTED
- test-128: "Could you allow 7464 till Monday." expected PROPOSE ALLOW 7464, until Mon 07 Dec 23:59; got UNSUPPORTED
- test-129: "approve 4845 in bay two please" expected PROPOSE ALLOW 4845, permanent; got UNSUPPORTED
- test-130: "Remove six four one six four and 5380." expected NEEDS_REVIEW (multiple_numbers); got NEEDS_REVIEW (missing_number)
- test-131: "approve 7525911 until eleven fifteen a.m." expected NEEDS_REVIEW (invalid_number); got UNSUPPORTED
- test-132: "give plate 28424 access until tomorrow at eight am spot 2 thanks" expected PROPOSE ALLOW 28424, until Mon 30 Nov 08:00; got UNSUPPORTED
- test-133: "delete number 3 4 4 7 8" expected PROPOSE REMOVE 34478; got NEEDS_REVIEW (missing_number)
- test-134: "please approve the car 58032 till 11 PM tonight" expected PROPOSE ALLOW 58032, until Wed 02 Dec 23:00; got UNSUPPORTED
- test-135: "Plate 66 till 8 pm." expected NEEDS_REVIEW (unclear_action); got UNSUPPORTED
- test-136: "Can you grant access to plate 8860 thanks." expected PROPOSE ALLOW 8860, permanent; got UNSUPPORTED
- test-137: "um add plate number 7267 thank you" expected PROPOSE ALLOW 7267, permanent; got UNSUPPORTED
- test-138: "um whitelist vehicle 23815" expected PROPOSE ALLOW 23815, permanent; got NEEDS_REVIEW (missing_number)
- test-139: "okay remove 3451 from bay 2 thank you" expected PROPOSE REMOVE 3451; got NEEDS_REVIEW (missing_number)
- test-140: "permit the guest till tomorrow" expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- test-141: "Could you revoke five four two six one from bay 1." expected PROPOSE REMOVE 54261; got UNSUPPORTED
- test-142: "let number three four three in" expected PROPOSE ALLOW 343, permanent; got NEEDS_REVIEW (missing_number)
- test-145: "permit number 79 until tomorrow afternoon" expected NEEDS_REVIEW (unclear_time); got UNSUPPORTED
- test-146: "Allow plate number eight hundred three until the weekend." expected NEEDS_REVIEW (unclear_time); got PROPOSE REMOVE 803
- test-147: "Could you remove car number eighty four thousand two hundred forty four from bay 1 thank you." expected PROPOSE REMOVE 84244; got NEEDS_REVIEW (missing_number)
- test-148: "Vehicle 796 in bay 2." expected NEEDS_REVIEW (unclear_action); got NEEDS_REVIEW (missing_number)
- test-150: "Could you grant access to vehicle 50874." expected PROPOSE ALLOW 50874, permanent; got UNSUPPORTED
- test-151: "okay approve the car 69582 until 10 pm tonight" expected PROPOSE ALLOW 69582, until Wed 02 Dec 22:00; got PROPOSE REMOVE 69582
- test-152: "let plate five five one four in" expected PROPOSE ALLOW 5514, permanent; got NEEDS_REVIEW (missing_number)
- test-153: "let seventy eight ninety eight and 36439 in" expected NEEDS_REVIEW (multiple_numbers); got UNSUPPORTED
- test-154: "allow cars 82205 and 6553" expected NEEDS_REVIEW (multiple_numbers); got PROPOSE REMOVE 82205
- test-155: "allow number 2 7 0 7 until 7" expected NEEDS_REVIEW (ambiguous_time); got NEEDS_REVIEW (invalid_number)
- test-156: "please permit the car four five two five oh" expected PROPOSE ALLOW 45250, permanent; got NEEDS_REVIEW (invalid_number)
- test-158: "let 1 4 1 1 7 in thanks" expected PROPOSE ALLOW 14117, permanent; got UNSUPPORTED
- test-159: "Let number eighty six thousand eight hundred thirty eight in thanks." expected PROPOSE ALLOW 86838, permanent; got UNSUPPORTED
