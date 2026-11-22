# Model C: smollm2 on test

Time per command: 295 ms mean, 414 ms p95.

| slice | n | exact | dangerous | needless question | action | number | until |
|---|---|---|---|---|---|---|---|
| all | 160 | 0.500 | 0.287 | 0.158 | 0.653 | 0.832 | 0.674 |
| kind=allow | 70 | 0.457 | 0.371 | 0.171 | 0.586 | 0.814 | 0.600 |
| kind=remove | 25 | 0.840 | 0.040 | 0.120 | 0.840 | 0.880 | 0.880 |
| kind=review | 49 | 0.367 | 0.347 | - | - | - | - |
| kind=single_digit | 6 | 0.833 | 0.000 | - | - | - | - |
| kind=unsupported | 10 | 0.400 | 0.200 | - | - | - | - |
| reason=ambiguous_time | 5 | 0.800 | 0.000 | - | - | - | - |
| reason=invalid_number | 5 | 1.000 | 0.000 | - | - | - | - |
| reason=missing_number | 8 | 0.000 | 0.125 | - | - | - | - |
| reason=multiple_numbers | 6 | 0.167 | 0.333 | - | - | - | - |
| reason=time_in_past | 5 | 1.000 | 0.000 | - | - | - | - |
| reason=unclear_action | 12 | 0.000 | 0.750 | - | - | - | - |
| reason=unclear_time | 8 | 0.375 | 0.625 | - | - | - | - |
| reason=unsupported | 10 | 0.400 | 0.200 | - | - | - | - |
| wording=seen | 74 | 0.527 | 0.297 | 0.156 | 0.641 | 0.844 | 0.672 |
| wording=unseen | 33 | 0.576 | 0.273 | 0.161 | 0.677 | 0.806 | 0.677 |
| bay said=False | 69 | 0.623 | 0.275 | 0.095 | 0.730 | 0.889 | 0.746 |
| bay said=True | 38 | 0.395 | 0.316 | 0.281 | 0.500 | 0.719 | 0.531 |
| slip=False | 154 | 0.519 | 0.273 | 0.158 | 0.653 | 0.832 | 0.674 |
| slip=True | 6 | 0.000 | 0.667 | - | - | - | - |

## Errors

- test-001: "Whitelist number 64278 for some time." expected NEEDS_REVIEW (unclear_time); got PROPOSE ALLOW 64278, permanent
- test-002: "let the delivery guy in until tomorrow" expected NEEDS_REVIEW (missing_number); got NEEDS_REVIEW (invalid_number)
- test-003: "please let car number 27677 in" expected PROPOSE ALLOW 27677, permanent; got PROPOSE REMOVE 27677
- test-005: "Could you allow number one oh six in bay 2 until tomorrow." expected PROPOSE ALLOW 106, until Fri 27 Nov 23:59; got PROPOSE REMOVE 106
- test-006: "Give access to the white car." expected NEEDS_REVIEW (missing_number); got NEEDS_REVIEW (invalid_number)
- test-007: "Let car six six one seven in." expected PROPOSE ALLOW 6617, permanent; got NEEDS_REVIEW (unclear_time)
- test-008: "could you allow vehicle 73569 bay 3" expected PROPOSE ALLOW 73569, permanent; got PROPOSE REMOVE 73569
- test-010: "and car number 94842" expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 94842, permanent
- test-011: "grant access to the car 69488 parking number two till tomorrow 12p.m. thanks" expected PROPOSE ALLOW 69488, until Fri 27 Nov 12:00; got PROPOSE ALLOW 69488, until Thu 26 Nov 12:00
- test-013: "add plate 3296 until midnight thanks" expected PROPOSE ALLOW 3296, until Fri 27 Nov 00:00; got PROPOSE REMOVE 3296
- test-014: "Allow cars 7 8 4 5 7 and four two eight." expected NEEDS_REVIEW (multiple_numbers); got NEEDS_REVIEW (unclear_time)
- test-017: "remove that car" expected NEEDS_REVIEW (missing_number); got NEEDS_REVIEW (invalid_number)
- test-020: "7930 can park till tomorrow parking number 2" expected PROPOSE ALLOW 7930, until Thu 03 Dec 23:59; got PROPOSE REMOVE 7930
- test-023: "allow the car in bay 2 for today" expected NEEDS_REVIEW (missing_number); got NEEDS_REVIEW (multiple_numbers)
- test-024: "delete the visitor" expected NEEDS_REVIEW (missing_number); got NEEDS_REVIEW (multiple_numbers)
- test-031: "Hey allow car number seven four seven four until 7:15 pm tonight bay one." expected PROPOSE ALLOW 7474, until Wed 02 Dec 19:15; got NEEDS_REVIEW (missing_number)
- test-033: "okay approve vehicle 6 till Saturday bay one thank you" expected NEEDS_REVIEW (single_digit_number): ALLOW 6, until Sat 05 Dec 23:59; got NEEDS_REVIEW (multiple_numbers)
- test-034: "Add car number 726 for bay two until tomorrow." expected PROPOSE ALLOW 726, until Thu 03 Dec 23:59; got PROPOSE ALLOW 726, permanent
- test-035: "Allow car number 8277 until next Monday." expected NEEDS_REVIEW (unclear_time); got PROPOSE ALLOW 8277, permanent
- test-036: "Give plate number 277 access please." expected PROPOSE ALLOW 277, permanent; got PROPOSE REMOVE 277
- test-037: "Number fifty nine for two hours." expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 59, until Thu 26 Nov 10:15
- test-038: "grant access to plate 39461 until tonight" expected NEEDS_REVIEW (unclear_time); got PROPOSE REMOVE 39461
- test-040: "can you aloud car 390 bay three until 9:15 AM thank you" expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 390, until Thu 26 Nov 09:15
- test-041: "Could you add plate number six eight six seven seven." expected PROPOSE ALLOW 68677, permanent; got PROPOSE REMOVE 68677
- test-042: "let plate number 63217 in until ten pm" expected PROPOSE ALLOW 63217, until Sun 29 Nov 22:00; got PROPOSE REMOVE 63217
- test-046: "Grant access to eight hundred seven until 1:30." expected NEEDS_REVIEW (ambiguous_time); got NEEDS_REVIEW (multiple_numbers)
- test-048: "Check car 39." expected UNSUPPORTED; got PROPOSE REMOVE 39
- test-049: "Good morning." expected UNSUPPORTED; got NEEDS_REVIEW (invalid_number)
- test-051: "13495 please" expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 13495, permanent
- test-057: "Remove three three seven three and nine thousand thirty one." expected NEEDS_REVIEW (multiple_numbers); got PROPOSE REMOVE 3373
- test-058: "Don't allow car two eight anymore thank you." expected PROPOSE REMOVE 28; got PROPOSE ALLOW 28, permanent
- test-060: "Add my cousin's car in bay 1." expected NEEDS_REVIEW (missing_number); got NEEDS_REVIEW (single_digit_number): ALLOW 1, permanent
- test-062: "Could you add plate number 16717." expected PROPOSE ALLOW 16717, permanent; got PROPOSE REMOVE 16717
- test-063: "Approve car number seven eight seven four six thank you." expected PROPOSE ALLOW 78746, permanent; got NEEDS_REVIEW (multiple_numbers)
- test-064: "What time is it?" expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- test-067: "Hey approve number 973 until tomorrow for bay three." expected PROPOSE ALLOW 973, until Fri 27 Nov 23:59; got PROPOSE ALLOW 973, permanent
- test-068: "please approve number 2460 for two hours for bay 2" expected PROPOSE ALLOW 2460, until Thu 26 Nov 10:15; got PROPOSE REMOVE 2460
- test-073: "Don't allow three three eight eight one anymore." expected PROPOSE REMOVE 33881; got NEEDS_REVIEW (multiple_numbers)
- test-074: "add vehicle 8 2 0 8 for six days in bay three please" expected PROPOSE ALLOW 8208, until Tue 08 Dec 14:40; got NEEDS_REVIEW (unclear_time)
- test-075: "add the car 9173 for a week for bay one" expected PROPOSE ALLOW 9173, until Wed 09 Dec 14:40; got NEEDS_REVIEW (unclear_time)
- test-078: "3574 can park until tomorrow." expected PROPOSE ALLOW 3574, until Fri 27 Nov 23:59; got PROPOSE ALLOW 3574, permanent
- test-081: "hey aloud vehicle 20 till tomorrow in bay two" expected NEEDS_REVIEW (unclear_action); got NEEDS_REVIEW (unclear_time)
- test-086: "the car 9799 tomorrow" expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 9799, permanent
- test-088: "please approve car number 4 4 8 for three days" expected PROPOSE ALLOW 448, until Sun 29 Nov 08:15; got PROPOSE ALLOW 448, permanent
- test-092: "let 6 3 3 4 and 8 6 2 4 in" expected NEEDS_REVIEW (multiple_numbers); got NEEDS_REVIEW (unclear_time)
- test-095: "um give car 8 7 3 access in slot 2 thank you" expected PROPOSE ALLOW 873, permanent; got NEEDS_REVIEW (ambiguous_time)
- test-096: "Allow car 9757 until six pm." expected PROPOSE ALLOW 9757, until Wed 02 Dec 18:00; got PROPOSE ALLOW 9757, permanent
- test-097: "Edit car 15744." expected UNSUPPORTED; got PROPOSE ALLOW 15744, permanent
- test-102: "Add plate 85144 for forty five minutes for bay one." expected PROPOSE ALLOW 85144, until Sun 29 Nov 21:55; got NEEDS_REVIEW (unclear_time)
- test-103: "Whitelist plate four two seven five five for one week." expected PROPOSE ALLOW 42755, until Sun 06 Dec 21:10; got PROPOSE ALLOW 4275, until Sun 06 Dec 21:10
- test-107: "approve the car 51 until 5 p.m." expected PROPOSE ALLOW 51, until Wed 02 Dec 17:00; got PROPOSE ALLOW 51, permanent
- test-111: "Can you a loud plate 1 2 5 9 8 for bay 5 until end of day." expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 12598, until Thu 26 Nov 23:59
- test-114: "Give plate number 1522 access until tomorrow." expected PROPOSE ALLOW 1522, until Fri 27 Nov 23:59; got PROPOSE REMOVE 1522
- test-115: "Can you and the car seventy nine eighteen." expected NEEDS_REVIEW (unclear_action); got NEEDS_REVIEW (missing_number)
- test-116: "Hey car 7754 can park till 5:30 pm in parking five." expected PROPOSE ALLOW 7754, until Wed 02 Dec 17:30; got NEEDS_REVIEW (unclear_time)
- test-117: "permit the guest" expected NEEDS_REVIEW (missing_number); got NEEDS_REVIEW (invalid_number)
- test-118: "Please add plate number 7 1 9 3 for bay five thanks." expected PROPOSE ALLOW 7193, permanent; got PROPOSE REMOVE 7193
- test-119: "Please permit plate number 4695 until tomorrow at 10:15 PM." expected PROPOSE ALLOW 4695, until Thu 03 Dec 22:15; got PROPOSE ALLOW 4695, until Wed 02 Dec 22:15
- test-121: "Could you aloud number 16182 until tomorrow." expected NEEDS_REVIEW (unclear_action); got PROPOSE REMOVE 16182
- test-123: "Please allow number 80 in bay 3 thank you." expected PROPOSE ALLOW 80, permanent; got PROPOSE REMOVE 80
- test-124: "car 71734 in bay 1" expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 71734, permanent
- test-127: "Can you allow plate number 39429 in bay 2." expected PROPOSE ALLOW 39429, permanent; got PROPOSE REMOVE 39429
- test-128: "Could you allow 7464 till Monday." expected PROPOSE ALLOW 7464, until Mon 07 Dec 23:59; got PROPOSE REMOVE 7464
- test-130: "Remove six four one six four and 5380." expected NEEDS_REVIEW (multiple_numbers); got PROPOSE REMOVE 5380
- test-132: "give plate 28424 access until tomorrow at eight am spot 2 thanks" expected PROPOSE ALLOW 28424, until Mon 30 Nov 08:00; got NEEDS_REVIEW (unclear_time)
- test-134: "please approve the car 58032 till 11 PM tonight" expected PROPOSE ALLOW 58032, until Wed 02 Dec 23:00; got PROPOSE REMOVE 58032
- test-135: "Plate 66 till 8 pm." expected NEEDS_REVIEW (unclear_action); got NEEDS_REVIEW (time_in_past)
- test-140: "permit the guest till tomorrow" expected NEEDS_REVIEW (missing_number); got NEEDS_REVIEW (multiple_numbers)
- test-141: "Could you revoke five four two six one from bay 1." expected PROPOSE REMOVE 54261; got NEEDS_REVIEW (missing_number)
- test-142: "let number three four three in" expected PROPOSE ALLOW 343, permanent; got NEEDS_REVIEW (unclear_time)
- test-145: "permit number 79 until tomorrow afternoon" expected NEEDS_REVIEW (unclear_time); got PROPOSE ALLOW 79, permanent
- test-146: "Allow plate number eight hundred three until the weekend." expected NEEDS_REVIEW (unclear_time); got PROPOSE ALLOW 803, permanent
- test-147: "Could you remove car number eighty four thousand two hundred forty four from bay 1 thank you." expected PROPOSE REMOVE 84244; got NEEDS_REVIEW (multiple_numbers)
- test-148: "Vehicle 796 in bay 2." expected NEEDS_REVIEW (unclear_action); got PROPOSE REMOVE 796
- test-149: "change the time for four hundred fifty six" expected UNSUPPORTED; got NEEDS_REVIEW (unclear_time)
- test-150: "Could you grant access to vehicle 50874." expected PROPOSE ALLOW 50874, permanent; got PROPOSE REMOVE 50874
- test-152: "let plate five five one four in" expected PROPOSE ALLOW 5514, permanent; got NEEDS_REVIEW (unclear_time)
- test-153: "let seventy eight ninety eight and 36439 in" expected NEEDS_REVIEW (multiple_numbers); got NEEDS_REVIEW (missing_number)
- test-158: "let 1 4 1 1 7 in thanks" expected PROPOSE ALLOW 14117, permanent; got NEEDS_REVIEW (unclear_time)
- test-160: "Open the gate." expected UNSUPPORTED; got NEEDS_REVIEW (invalid_number)
