# Command set: dev (60 commands)

| id | command (said at) | expected |
|---|---|---|
| dev-001 | Okay and car number 37080 bay one for one week. (Sat 21 Nov 09:30) | NEEDS_REVIEW (unclear_action) |
| dev-002 | please approve 6 4 3 1 9 (Tue 24 Nov 19:45) | PROPOSE ALLOW 64319, permanent |
| dev-003 | Hey remove plate four zero six zero nine please. (Tue 24 Nov 19:45) | PROPOSE REMOVE 40609 |
| dev-004 | Allow the car. (Tue 24 Nov 19:45) | NEEDS_REVIEW (missing_number) |
| dev-005 | approve car eight oh nine until 4:30 (Tue 24 Nov 19:45) | NEEDS_REVIEW (ambiguous_time) |
| dev-006 | Please remove plate number 8845. (Sat 21 Nov 09:30) | PROPOSE REMOVE 8845 |
| dev-007 | Please let plate 35 in for today. (Tue 24 Nov 19:45) | PROPOSE ALLOW 35, until Tue 24 Nov 23:59 |
| dev-008 | what's the weather today (Tue 24 Nov 19:45) | UNSUPPORTED |
| dev-009 | okay let car 626 in till tomorrow (Tue 24 Nov 19:45) | PROPOSE ALLOW 626, until Wed 25 Nov 23:59 |
| dev-010 | 930 until tomorrow. (Tue 24 Nov 19:45) | NEEDS_REVIEW (unclear_action) |
| dev-011 | allow thirty nine thousand three hundred twenty two until tomorrow at 9 pm (Tue 24 Nov 19:45) | PROPOSE ALLOW 39322, until Wed 25 Nov 21:00 |
| dev-012 | Add plate 61079 until 9AM. (Sat 21 Nov 09:30) | NEEDS_REVIEW (time_in_past) |
| dev-013 | allow number nine hundred four in bay 2 until seven thirty PM (Sat 21 Nov 09:30) | PROPOSE ALLOW 904, until Sat 21 Nov 19:30 |
| dev-014 | allow number 47 until Saturday (Tue 24 Nov 19:45) | PROPOSE ALLOW 47, until Sat 28 Nov 23:59 |
| dev-015 | Approve plate 3526 till midnight. (Tue 24 Nov 19:45) | PROPOSE ALLOW 3526, until Wed 25 Nov 00:00 |
| dev-016 | okay add car eighty two thousand one hundred eighty eight (Sat 21 Nov 09:30) | PROPOSE ALLOW 82188, permanent |
| dev-017 | please take eighty six fourteen off the list (Tue 24 Nov 19:45) | PROPOSE REMOVE 8614 |
| dev-018 | allow number nine one one seven please (Sat 21 Nov 09:30) | PROPOSE ALLOW 9117, permanent |
| dev-019 | add 832 until tomorrow at 1 (Tue 24 Nov 19:45) | NEEDS_REVIEW (ambiguous_time) |
| dev-020 | Add car 29422 until Tuesday. (Tue 24 Nov 19:45) | NEEDS_REVIEW (unclear_time) |
| dev-021 | Add car number 95 please. (Tue 24 Nov 19:45) | PROPOSE ALLOW 95, permanent |
| dev-022 | Let car number 9873 in bay two until tomorrow please. (Tue 24 Nov 19:45) | PROPOSE ALLOW 9873, until Wed 25 Nov 23:59 |
| dev-023 | please add nine one six five two until tomorrow at one thirty pm (Tue 24 Nov 19:45) | PROPOSE ALLOW 91652, until Wed 25 Nov 13:30 |
| dev-024 | Allow plate number one five eight nine five till 9:30. (Sat 21 Nov 09:30) | NEEDS_REVIEW (ambiguous_time) |
| dev-025 | Remove the car. (Tue 24 Nov 19:45) | NEEDS_REVIEW (missing_number) |
| dev-026 | Hello. (Tue 24 Nov 19:45) | UNSUPPORTED |
| dev-027 | Approve plate number one oh two seven six until Wednesday. (Tue 24 Nov 19:45) | PROPOSE ALLOW 10276, until Wed 25 Nov 23:59 |
| dev-028 | approve seven five zero seven six bay 2 until Thursday (Tue 24 Nov 19:45) | PROPOSE ALLOW 75076, until Thu 26 Nov 23:59 |
| dev-029 | Let plate 4729886 in. (Tue 24 Nov 19:45) | NEEDS_REVIEW (invalid_number) |
| dev-030 | How many cars are parked? (Sat 21 Nov 09:30) | UNSUPPORTED |
| dev-031 | Add car 62680 and car 46149 until tomorrow. (Sat 21 Nov 09:30) | NEEDS_REVIEW (multiple_numbers) |
| dev-032 | okay remove car 7 7 0 6 8 (Sat 21 Nov 09:30) | PROPOSE REMOVE 77068 |
| dev-033 | hey delete number 683 (Tue 24 Nov 19:45) | PROPOSE REMOVE 683 |
| dev-034 | okay let one four eight four in for bay 2 until 21:00 (Tue 24 Nov 19:45) | PROPOSE ALLOW 1484, until Tue 24 Nov 21:00 |
| dev-035 | Car number 98331. (Sat 21 Nov 09:30) | NEEDS_REVIEW (unclear_action) |
| dev-036 | add number one three eight zero six for today (Tue 24 Nov 19:45) | PROPOSE ALLOW 13806, until Tue 24 Nov 23:59 |
| dev-037 | Approve plate number 276741. (Sat 21 Nov 09:30) | NEEDS_REVIEW (invalid_number) |
| dev-038 | Please add 5134. (Tue 24 Nov 19:45) | PROPOSE ALLOW 5134, permanent |
| dev-039 | Let number 14649 in until 7am. (Tue 24 Nov 19:45) | NEEDS_REVIEW (time_in_past) |
| dev-040 | Allow car number 69375 for bay 1 until tomorrow. (Sat 21 Nov 09:30) | PROPOSE ALLOW 69375, until Sun 22 Nov 23:59 |
| dev-041 | Please let plate five thousand four hundred eleven in till tomorrow at one thirty pm. (Tue 24 Nov 19:45) | PROPOSE ALLOW 5411, until Wed 25 Nov 13:30 |
| dev-042 | hey add plate three oh please (Tue 24 Nov 19:45) | PROPOSE ALLOW 30, permanent |
| dev-043 | okay add car 15 bay one (Tue 24 Nov 19:45) | PROPOSE ALLOW 15, permanent |
| dev-044 | Allow 18 and one two five eight seven. (Tue 24 Nov 19:45) | NEEDS_REVIEW (multiple_numbers) |
| dev-045 | car 6846 in bay 2 (Tue 24 Nov 19:45) | NEEDS_REVIEW (unclear_action) |
| dev-046 | Allow plate 9008 until 10 pm. (Tue 24 Nov 19:45) | PROPOSE ALLOW 9008, until Tue 24 Nov 22:00 |
| dev-047 | Add plate number 91586 until tonight. (Sat 21 Nov 09:30) | NEEDS_REVIEW (unclear_time) |
| dev-048 | Approve plate number 7 6 2 3 in bay two. (Sat 21 Nov 09:30) | PROPOSE ALLOW 7623, permanent |
| dev-049 | Is car five zero oh two one allowed? (Tue 24 Nov 19:45) | UNSUPPORTED |
| dev-050 | okay remove plate 86031 from bay 2 (Sat 21 Nov 09:30) | PROPOSE REMOVE 86031 |
| dev-051 | allow number 7565 for a while (Tue 24 Nov 19:45) | NEEDS_REVIEW (unclear_time) |
| dev-052 | add a car in bay 2 (Sat 21 Nov 09:30) | NEEDS_REVIEW (missing_number) |
| dev-053 | okay approve 5 2 1 0 6 until Sunday (Sat 21 Nov 09:30) | PROPOSE ALLOW 52106, until Sun 22 Nov 23:59 |
| dev-054 | Allow number 8. (Sat 21 Nov 09:30) | NEEDS_REVIEW (single_digit_number): ALLOW 8, permanent |
| dev-055 | Take car 7483 off the list please. (Tue 24 Nov 19:45) | PROPOSE REMOVE 7483 |
| dev-056 | Please approve number 4 for 2 hours. (Tue 24 Nov 19:45) | NEEDS_REVIEW (single_digit_number): ALLOW 4, until Tue 24 Nov 21:45 |
| dev-057 | Let car number nine hundred eleven in for an hour for bay 1. (Sat 21 Nov 09:30) | PROPOSE ALLOW 911, until Sat 21 Nov 10:30 |
| dev-058 | allow number 47645 until 8a.m. today (Tue 24 Nov 19:45) | NEEDS_REVIEW (time_in_past) |
| dev-059 | Please add plate number 48848 for bay 2 till 22:30. (Sat 21 Nov 09:30) | PROPOSE ALLOW 48848, until Sat 21 Nov 22:30 |
| dev-060 | hey take one five three three five off the list (Sat 21 Nov 09:30) | PROPOSE REMOVE 15335 |
