# Command set: confirm (120 commands)

| id | command (said at) | expected |
|---|---|---|
| confirm-001 | Allow 47829 and seventy six thousand one hundred fifty two. (Sat 28 Nov 06:45) | NEEDS_REVIEW (multiple_numbers) |
| confirm-002 | hey remove plate 5 4 6 6 0 please (Tue 01 Dec 19:30) | PROPOSE REMOVE 54660 |
| confirm-003 | add plate number forty one eighty seven for bay 2 (Sat 28 Nov 06:45) | PROPOSE ALLOW 4187, permanent |
| confirm-004 | Hey allow car number 84732 please. (Tue 01 Dec 19:30) | PROPOSE ALLOW 84732, permanent |
| confirm-005 | approve plate number 282005 (Mon 23 Nov 12:35) | NEEDS_REVIEW (invalid_number) |
| confirm-006 | approve car fifty two thousand thirty for 45 minutes (Sat 28 Nov 06:45) | PROPOSE ALLOW 52030, until Sat 28 Nov 07:30 |
| confirm-007 | add car 9 9 4 8 till 6 am (Sat 28 Nov 06:45) | NEEDS_REVIEW (time_in_past) |
| confirm-008 | Car 5565 in bay 2. (Tue 01 Dec 19:30) | NEEDS_REVIEW (unclear_action) |
| confirm-009 | delete plate 5 5 9 (Mon 23 Nov 12:35) | PROPOSE REMOVE 559 |
| confirm-010 | approve number 304 till 10:30 pm (Tue 01 Dec 19:30) | PROPOSE ALLOW 304, until Tue 01 Dec 22:30 |
| confirm-011 | take number seven off the list (Tue 01 Dec 19:30) | NEEDS_REVIEW (single_digit_number): REMOVE 7 |
| confirm-012 | Please let car number ninety six thousand seven hundred sixty three in for two hours. (Mon 23 Nov 12:35) | PROPOSE ALLOW 96763, until Mon 23 Nov 14:35 |
| confirm-013 | show me the permits (Mon 23 Nov 12:35) | UNSUPPORTED |
| confirm-014 | Let plate number 720 in until 8 PM. (Tue 01 Dec 19:30) | PROPOSE ALLOW 720, until Tue 01 Dec 20:00 |
| confirm-015 | Is car 28108 allowed? (Sat 28 Nov 06:45) | UNSUPPORTED |
| confirm-016 | How many cars are parked? (Tue 01 Dec 19:30) | UNSUPPORTED |
| confirm-017 | add car four seven zero two seven in bay 2 for one hour (Sat 28 Nov 06:45) | PROPOSE ALLOW 47027, until Sat 28 Nov 07:45 |
| confirm-018 | Add plate 5900 until tonight. (Mon 23 Nov 12:35) | NEEDS_REVIEW (unclear_time) |
| confirm-019 | Allow plate number 2353 until 2:15 p.m. (Mon 23 Nov 12:35) | PROPOSE ALLOW 2353, until Mon 23 Nov 14:15 |
| confirm-020 | Allow my brother's car. (Sat 28 Nov 06:45) | NEEDS_REVIEW (missing_number) |
| confirm-021 | 8 5 7 8 5 until tomorrow. (Mon 23 Nov 12:35) | NEEDS_REVIEW (unclear_action) |
| confirm-022 | Okay take 7 off the list. (Mon 23 Nov 12:35) | NEEDS_REVIEW (single_digit_number): REMOVE 7 |
| confirm-023 | approve 67624 bay one (Sat 28 Nov 06:45) | PROPOSE ALLOW 67624, permanent |
| confirm-024 | please remove car number 30291 (Mon 23 Nov 12:35) | PROPOSE REMOVE 30291 |
| confirm-025 | let plate number 8 1 0 9 in until tomorrow 8pm (Tue 01 Dec 19:30) | PROPOSE ALLOW 8109, until Wed 02 Dec 20:00 |
| confirm-026 | hey remove plate 59015 (Tue 01 Dec 19:30) | PROPOSE REMOVE 59015 |
| confirm-027 | Add car number sixteen thousand seven hundred forty one for 2 days please. (Mon 23 Nov 12:35) | PROPOSE ALLOW 16741, until Wed 25 Nov 12:35 |
| confirm-028 | Add car 7093 for bay 1 for a week. (Tue 01 Dec 19:30) | PROPOSE ALLOW 7093, until Tue 08 Dec 19:30 |
| confirm-029 | Please take number 90499 off the list. (Tue 01 Dec 19:30) | PROPOSE REMOVE 90499 |
| confirm-030 | Hey add plate number 75436 for bay 2 until ten AM tomorrow. (Sat 28 Nov 06:45) | PROPOSE ALLOW 75436, until Sun 29 Nov 10:00 |
| confirm-031 | Allow car fifty seven thousand nine hundred forty eight. (Sat 28 Nov 06:45) | PROPOSE ALLOW 57948, permanent |
| confirm-032 | car three four seven four one in bay 2 (Mon 23 Nov 12:35) | NEEDS_REVIEW (unclear_action) |
| confirm-033 | please let number one one eight in until noon (Sat 28 Nov 06:45) | PROPOSE ALLOW 118, until Sat 28 Nov 12:00 |
| confirm-034 | Add car 338 and car 88431 until tomorrow. (Sat 28 Nov 06:45) | NEEDS_REVIEW (multiple_numbers) |
| confirm-035 | Add plate number 4 3 0 3 0 3. (Tue 01 Dec 19:30) | NEEDS_REVIEW (invalid_number) |
| confirm-036 | Allow car four nine seven one until tomorrow. (Mon 23 Nov 12:35) | PROPOSE ALLOW 4971, until Tue 24 Nov 23:59 |
| confirm-037 | Add seven three four six three until tomorrow at 4:30 PM please. (Mon 23 Nov 12:35) | PROPOSE ALLOW 73463, until Tue 24 Nov 16:30 |
| confirm-038 | Please allow car 2 5 2 2 until eleven fifteen PM. (Sat 28 Nov 06:45) | PROPOSE ALLOW 2522, until Sat 28 Nov 23:15 |
| confirm-039 | Let 5 in till tomorrow. (Tue 01 Dec 19:30) | NEEDS_REVIEW (single_digit_number): ALLOW 5, until Wed 02 Dec 23:59 |
| confirm-040 | Okay let seven four two five in for 2 days. (Tue 01 Dec 19:30) | PROPOSE ALLOW 7425, until Thu 03 Dec 19:30 |
| confirm-041 | Approve ninety six thousand six hundred forty eight until four. (Mon 23 Nov 12:35) | NEEDS_REVIEW (ambiguous_time) |
| confirm-042 | let car number seventeen oh four in until tonight (Tue 01 Dec 19:30) | NEEDS_REVIEW (unclear_time) |
| confirm-043 | allow car 9634 until 7:30 a.m. tomorrow (Mon 23 Nov 12:35) | PROPOSE ALLOW 9634, until Tue 24 Nov 07:30 |
| confirm-044 | allow plate 38 (Mon 23 Nov 12:35) | PROPOSE ALLOW 38, permanent |
| confirm-045 | hello (Tue 01 Dec 19:30) | UNSUPPORTED |
| confirm-046 | Let car 1215 in till 7:30 pm tomorrow please. (Sat 28 Nov 06:45) | PROPOSE ALLOW 1215, until Sun 29 Nov 19:30 |
| confirm-047 | Okay let plate number 407 in for bay two till tomorrow. (Mon 23 Nov 12:35) | PROPOSE ALLOW 407, until Tue 24 Nov 23:59 |
| confirm-048 | okay let five zero five in for bay two (Mon 23 Nov 12:35) | PROPOSE ALLOW 505, permanent |
| confirm-049 | Please add car number 25. (Tue 01 Dec 19:30) | PROPOSE ALLOW 25, permanent |
| confirm-050 | allow ninety five eighty three and six three four three (Tue 01 Dec 19:30) | NEEDS_REVIEW (multiple_numbers) |
| confirm-051 | Take plate number 9328 off the list. (Sat 28 Nov 06:45) | PROPOSE REMOVE 9328 |
| confirm-052 | Add car 9413 until eight. (Mon 23 Nov 12:35) | NEEDS_REVIEW (ambiguous_time) |
| confirm-053 | add a car in bay 2 (Tue 01 Dec 19:30) | NEEDS_REVIEW (missing_number) |
| confirm-054 | Allow car seven thousand thirty four until 10. (Sat 28 Nov 06:45) | NEEDS_REVIEW (ambiguous_time) |
| confirm-055 | is car 483 allowed (Sat 28 Nov 06:45) | UNSUPPORTED |
| confirm-056 | hey delete car 6 1 5 7 1 please (Mon 23 Nov 12:35) | PROPOSE REMOVE 61571 |
| confirm-057 | allow 7978 till six thirty a.m. today (Sat 28 Nov 06:45) | NEEDS_REVIEW (time_in_past) |
| confirm-058 | Approve plate number 940 until 6AM today. (Sat 28 Nov 06:45) | NEEDS_REVIEW (time_in_past) |
| confirm-059 | Let plate 5539 in till tomorrow. (Tue 01 Dec 19:30) | PROPOSE ALLOW 5539, until Wed 02 Dec 23:59 |
| confirm-060 | Hey add car number 36933 in bay two. (Mon 23 Nov 12:35) | PROPOSE ALLOW 36933, permanent |
| confirm-061 | Is car 30062 allowed? (Tue 01 Dec 19:30) | UNSUPPORTED |
| confirm-062 | Please approve car number twenty thousand six hundred fifty seven. (Tue 01 Dec 19:30) | PROPOSE ALLOW 20657, permanent |
| confirm-063 | Add plate 3603 until 21:30 bay 1 please. (Sat 28 Nov 06:45) | PROPOSE ALLOW 3603, until Sat 28 Nov 21:30 |
| confirm-064 | allow car 3498 in bay 1 until Monday please (Sat 28 Nov 06:45) | PROPOSE ALLOW 3498, until Mon 30 Nov 23:59 |
| confirm-065 | please allow number 1768 (Mon 23 Nov 12:35) | PROPOSE ALLOW 1768, permanent |
| confirm-066 | Please add plate number 92142 for bay two. (Sat 28 Nov 06:45) | PROPOSE ALLOW 92142, permanent |
| confirm-067 | add car number 7 8 5 5 until tomorrow at 12 (Mon 23 Nov 12:35) | NEEDS_REVIEW (ambiguous_time) |
| confirm-068 | Remove the car. (Mon 23 Nov 12:35) | NEEDS_REVIEW (missing_number) |
| confirm-069 | Let 10639 in until ten pm please. (Sat 28 Nov 06:45) | PROPOSE ALLOW 10639, until Sat 28 Nov 22:00 |
| confirm-070 | Approve car number four eight four until 5:30 pm. (Sat 28 Nov 06:45) | PROPOSE ALLOW 484, until Sat 28 Nov 17:30 |
| confirm-071 | Approve 61176 in bay one until Sunday. (Sat 28 Nov 06:45) | PROPOSE ALLOW 61176, until Sun 29 Nov 23:59 |
| confirm-072 | Add car 16489. (Mon 23 Nov 12:35) | PROPOSE ALLOW 16489, permanent |
| confirm-073 | let plate six eight three five oh five in (Tue 01 Dec 19:30) | NEEDS_REVIEW (invalid_number) |
| confirm-074 | Approve plate one seven eight nine oh until later. (Sat 28 Nov 06:45) | NEEDS_REVIEW (unclear_time) |
| confirm-075 | Please remove number 85079. (Sat 28 Nov 06:45) | PROPOSE REMOVE 85079 |
| confirm-076 | let plate number 6 5 1 5 6 2 0 in (Mon 23 Nov 12:35) | NEEDS_REVIEW (invalid_number) |
| confirm-077 | hey approve car 6 7 9 4 2 for bay two until 12 PM tomorrow (Tue 01 Dec 19:30) | PROPOSE ALLOW 67942, until Wed 02 Dec 12:00 |
| confirm-078 | Hey add plate 1 until tomorrow six p.m. (Mon 23 Nov 12:35) | NEEDS_REVIEW (single_digit_number): ALLOW 1, until Tue 24 Nov 18:00 |
| confirm-079 | delete 22599 (Mon 23 Nov 12:35) | PROPOSE REMOVE 22599 |
| confirm-080 | add number 6523 till 2:30 PM (Tue 01 Dec 19:30) | NEEDS_REVIEW (time_in_past) |
| confirm-081 | add car 47114 and car two eight two zero one until tomorrow (Mon 23 Nov 12:35) | NEEDS_REVIEW (multiple_numbers) |
| confirm-082 | Please and car 897 till tomorrow. (Sat 28 Nov 06:45) | NEEDS_REVIEW (unclear_action) |
| confirm-083 | hey remove 80254 (Tue 01 Dec 19:30) | PROPOSE REMOVE 80254 |
| confirm-084 | Allow plate one four four until tomorrow. (Sat 28 Nov 06:45) | PROPOSE ALLOW 144, until Sun 29 Nov 23:59 |
| confirm-085 | hey let plate number six thousand one hundred fifty in (Tue 01 Dec 19:30) | PROPOSE ALLOW 6150, permanent |
| confirm-086 | approve number 1604 (Mon 23 Nov 12:35) | PROPOSE ALLOW 1604, permanent |
| confirm-087 | allow plate 31 until tomorrow for bay 2 (Mon 23 Nov 12:35) | PROPOSE ALLOW 31, until Tue 24 Nov 23:59 |
| confirm-088 | allow 6683 for one week (Tue 01 Dec 19:30) | PROPOSE ALLOW 6683, until Tue 08 Dec 19:30 |
| confirm-089 | Let 239 in until Saturday. (Sat 28 Nov 06:45) | NEEDS_REVIEW (unclear_time) |
| confirm-090 | allow number 1438 until four (Sat 28 Nov 06:45) | NEEDS_REVIEW (ambiguous_time) |
| confirm-091 | let plate 5477 in for a while (Sat 28 Nov 06:45) | NEEDS_REVIEW (unclear_time) |
| confirm-092 | car number 88788 (Mon 23 Nov 12:35) | NEEDS_REVIEW (unclear_action) |
| confirm-093 | Please allow plate number 43 until tomorrow. (Tue 01 Dec 19:30) | PROPOSE ALLOW 43, until Wed 02 Dec 23:59 |
| confirm-094 | Okay add number 6651 until one fifteen PM. (Mon 23 Nov 12:35) | PROPOSE ALLOW 6651, until Mon 23 Nov 13:15 |
| confirm-095 | allow car number one seven five five eight until tomorrow morning (Tue 01 Dec 19:30) | NEEDS_REVIEW (unclear_time) |
| confirm-096 | allow the car (Sat 28 Nov 06:45) | NEEDS_REVIEW (missing_number) |
| confirm-097 | let car number 3828 in for bay one (Tue 01 Dec 19:30) | PROPOSE ALLOW 3828, permanent |
| confirm-098 | Please take car 854 off the list. (Mon 23 Nov 12:35) | PROPOSE REMOVE 854 |
| confirm-099 | Delete number 85476. (Tue 01 Dec 19:30) | PROPOSE REMOVE 85476 |
| confirm-100 | what's the weather today (Tue 01 Dec 19:30) | UNSUPPORTED |
| confirm-101 | Approve car 8 7 7 0 7 until 22:15 please. (Tue 01 Dec 19:30) | PROPOSE ALLOW 87707, until Tue 01 Dec 22:15 |
| confirm-102 | Let plate number eight four six four four in till nine thirty am. (Mon 23 Nov 12:35) | NEEDS_REVIEW (time_in_past) |
| confirm-103 | 9650 until tomorrow (Tue 01 Dec 19:30) | NEEDS_REVIEW (unclear_action) |
| confirm-104 | let car number 50925 in (Tue 01 Dec 19:30) | PROPOSE ALLOW 50925, permanent |
| confirm-105 | hey delete car number three zero three oh (Sat 28 Nov 06:45) | PROPOSE REMOVE 3030 |
| confirm-106 | Add car number 7 3 4. (Mon 23 Nov 12:35) | PROPOSE ALLOW 734, permanent |
| confirm-107 | hey remove plate 6081 from bay 1 (Mon 23 Nov 12:35) | PROPOSE REMOVE 6081 |
| confirm-108 | Okay allow car number 33734 for bay two. (Mon 23 Nov 12:35) | PROPOSE ALLOW 33734, permanent |
| confirm-109 | Car number 19345. (Mon 23 Nov 12:35) | NEEDS_REVIEW (unclear_action) |
| confirm-110 | Delete plate number six hundred fifty four. (Sat 28 Nov 06:45) | PROPOSE REMOVE 654 |
| confirm-111 | Let number nine hundred fourteen in until six thirty AM. (Sat 28 Nov 06:45) | NEEDS_REVIEW (time_in_past) |
| confirm-112 | add number 5 7 2 1 until tomorrow ten pm bay 2 please (Tue 01 Dec 19:30) | PROPOSE ALLOW 5721, until Wed 02 Dec 22:00 |
| confirm-113 | Remove car number 6 7 2 5 please. (Mon 23 Nov 12:35) | PROPOSE REMOVE 6725 |
| confirm-114 | Allow number 3 7 3 till tomorrow at 8. (Mon 23 Nov 12:35) | NEEDS_REVIEW (ambiguous_time) |
| confirm-115 | Hey and number nine six two nine for one day. (Mon 23 Nov 12:35) | NEEDS_REVIEW (unclear_action) |
| confirm-116 | Let my friend in until today. (Mon 23 Nov 12:35) | NEEDS_REVIEW (missing_number) |
| confirm-117 | Allow the car until 23:30. (Mon 23 Nov 12:35) | NEEDS_REVIEW (missing_number) |
| confirm-118 | Okay add plate number 96542 for six days please. (Tue 01 Dec 19:30) | PROPOSE ALLOW 96542, until Mon 07 Dec 19:30 |
| confirm-119 | extend the permit for car 14769 (Mon 23 Nov 12:35) | UNSUPPORTED |
| confirm-120 | Add 36469 till tomorrow 1:15 pm bay one. (Tue 01 Dec 19:30) | PROPOSE ALLOW 36469, until Wed 02 Dec 13:15 |
