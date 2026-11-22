# Model C: gliner-minilm on test

Time per command: 27 ms mean, 38 ms p95.

| slice | n | exact | dangerous | needless question | action | number | until |
|---|---|---|---|---|---|---|---|
| all | 160 | 0.731 | 0.094 | 0.147 | 0.800 | 0.853 | 0.842 |
| kind=allow | 70 | 0.829 | 0.029 | 0.143 | 0.843 | 0.857 | 0.843 |
| kind=remove | 25 | 0.680 | 0.160 | 0.160 | 0.680 | 0.840 | 0.840 |
| kind=review | 49 | 0.673 | 0.122 | - | - | - | - |
| kind=single_digit | 6 | 1.000 | 0.000 | - | - | - | - |
| kind=unsupported | 10 | 0.300 | 0.300 | - | - | - | - |
| reason=ambiguous_time | 5 | 0.800 | 0.200 | - | - | - | - |
| reason=invalid_number | 5 | 0.800 | 0.000 | - | - | - | - |
| reason=missing_number | 8 | 0.625 | 0.000 | - | - | - | - |
| reason=multiple_numbers | 6 | 0.667 | 0.000 | - | - | - | - |
| reason=time_in_past | 5 | 1.000 | 0.000 | - | - | - | - |
| reason=unclear_action | 12 | 0.500 | 0.333 | - | - | - | - |
| reason=unclear_time | 8 | 0.625 | 0.125 | - | - | - | - |
| reason=unsupported | 10 | 0.300 | 0.300 | - | - | - | - |
| wording=seen | 74 | 0.838 | 0.041 | 0.109 | 0.875 | 0.891 | 0.891 |
| wording=unseen | 33 | 0.636 | 0.152 | 0.226 | 0.645 | 0.774 | 0.742 |
| bay said=False | 69 | 0.768 | 0.087 | 0.143 | 0.794 | 0.857 | 0.841 |
| bay said=True | 38 | 0.789 | 0.053 | 0.156 | 0.812 | 0.844 | 0.844 |
| slip=False | 154 | 0.747 | 0.084 | 0.147 | 0.800 | 0.853 | 0.842 |
| slip=True | 6 | 0.333 | 0.333 | - | - | - | - |

## Errors

- test-001: "Whitelist number 64278 for some time." expected NEEDS_REVIEW (unclear_time); got PROPOSE REMOVE 64278
- test-006: "Give access to the white car." expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- test-009: "Hey let number three eight four three in." expected PROPOSE ALLOW 3843, permanent; got PROPOSE REMOVE 3843
- test-014: "Allow cars 7 8 4 5 7 and four two eight." expected NEEDS_REVIEW (multiple_numbers); got UNSUPPORTED
- test-018: "Allow the car 441 please." expected PROPOSE ALLOW 441, permanent; got UNSUPPORTED
- test-030: "car 187271 can park" expected NEEDS_REVIEW (invalid_number); got UNSUPPORTED
- test-037: "Number fifty nine for two hours." expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 59, until Thu 26 Nov 10:15
- test-040: "can you aloud car 390 bay three until 9:15 AM thank you" expected NEEDS_REVIEW (unclear_action); got NEEDS_REVIEW (missing_number)
- test-051: "13495 please" expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 13495, permanent
- test-053: "don't allow number 294 anymore" expected PROPOSE REMOVE 294; got PROPOSE ALLOW 294, permanent
- test-058: "Don't allow car two eight anymore thank you." expected PROPOSE REMOVE 28; got PROPOSE ALLOW 28, permanent
- test-059: "Is eight thousand thirty seven still allowed?" expected UNSUPPORTED; got PROPOSE ALLOW 8037, permanent
- test-064: "What time is it?" expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- test-065: "could you cancel car number 69831" expected PROPOSE REMOVE 69831; got PROPOSE ALLOW 69831, permanent
- test-071: "Permit plate number 35212 until 11:15 AM." expected PROPOSE ALLOW 35212, until Thu 26 Nov 11:15; got NEEDS_REVIEW (unclear_action)
- test-075: "add the car 9173 for a week for bay one" expected PROPOSE ALLOW 9173, until Wed 09 Dec 14:40; got NEEDS_REVIEW (unclear_time)
- test-077: "Block plate number 76141 from bay 2." expected PROPOSE REMOVE 76141; got NEEDS_REVIEW (unclear_action)
- test-078: "3574 can park until tomorrow." expected PROPOSE ALLOW 3574, until Fri 27 Nov 23:59; got NEEDS_REVIEW (unclear_action)
- test-097: "Edit car 15744." expected UNSUPPORTED; got PROPOSE ALLOW 15744, permanent
- test-101: "Car 3452 can park until he leaves." expected NEEDS_REVIEW (unclear_time); got UNSUPPORTED
- test-104: "can you take vehicle sixty two off the list thanks" expected PROPOSE REMOVE 62; got UNSUPPORTED
- test-107: "approve the car 51 until 5 p.m." expected PROPOSE ALLOW 51, until Wed 02 Dec 17:00; got UNSUPPORTED
- test-111: "Can you a loud plate 1 2 5 9 8 for bay 5 until end of day." expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 12598, until Thu 26 Nov 23:59
- test-112: "Block the car five six from bay 2." expected PROPOSE REMOVE 56; got PROPOSE ALLOW 56, permanent
- test-113: "Grant access to car 8006 spot two thank you." expected PROPOSE ALLOW 8006, permanent; got NEEDS_REVIEW (multiple_numbers)
- test-115: "Can you and the car seventy nine eighteen." expected NEEDS_REVIEW (unclear_action); got UNSUPPORTED
- test-117: "permit the guest" expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- test-119: "Please permit plate number 4695 until tomorrow at 10:15 PM." expected PROPOSE ALLOW 4695, until Thu 03 Dec 22:15; got PROPOSE ALLOW 4695, until Wed 02 Dec 22:15
- test-121: "Could you aloud number 16182 until tomorrow." expected NEEDS_REVIEW (unclear_action); got PROPOSE ALLOW 16182, until Fri 27 Nov 23:59
- test-123: "Please allow number 80 in bay 3 thank you." expected PROPOSE ALLOW 80, permanent; got NEEDS_REVIEW (unclear_action)
- test-125: "Permit car eighty three thousand seven hundred twenty eight until Wednesday." expected NEEDS_REVIEW (unclear_time); got UNSUPPORTED
- test-126: "Take car three four two one eight off the list." expected PROPOSE REMOVE 34218; got UNSUPPORTED
- test-138: "um whitelist vehicle 23815" expected PROPOSE ALLOW 23815, permanent; got UNSUPPORTED
- test-140: "permit the guest till tomorrow" expected NEEDS_REVIEW (missing_number); got UNSUPPORTED
- test-144: "Which bay is free?" expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- test-147: "Could you remove car number eighty four thousand two hundred forty four from bay 1 thank you." expected PROPOSE REMOVE 84244; got NEEDS_REVIEW (missing_number)
- test-149: "change the time for four hundred fifty six" expected UNSUPPORTED; got PROPOSE ALLOW 456, permanent
- test-150: "Could you grant access to vehicle 50874." expected PROPOSE ALLOW 50874, permanent; got UNSUPPORTED
- test-154: "allow cars 82205 and 6553" expected NEEDS_REVIEW (multiple_numbers); got UNSUPPORTED
- test-155: "allow number 2 7 0 7 until 7" expected NEEDS_REVIEW (ambiguous_time); got PROPOSE ALLOW 2707, permanent
- test-156: "please permit the car four five two five oh" expected PROPOSE ALLOW 45250, permanent; got UNSUPPORTED
- test-157: "who is parked in bay 1" expected UNSUPPORTED; got NEEDS_REVIEW (unclear_action)
- test-160: "Open the gate." expected UNSUPPORTED; got NEEDS_REVIEW (missing_number)
