# Command set: confirm2 (120 commands)

| id | command (said at) | expected |
|---|---|---|
| confirm2-001 | delete number 20981 please (Tue 24 Nov 10:10) | PROPOSE REMOVE 20981 |
| confirm2-002 | Approve number 240714. (Thu 03 Dec 17:55) | NEEDS_REVIEW (invalid_number) |
| confirm2-003 | extend the permit for car 67493 (Thu 03 Dec 17:55) | UNSUPPORTED |
| confirm2-004 | allow 8 8 8 0 till Saturday (Tue 24 Nov 10:10) | PROPOSE ALLOW 8880, until Sat 28 Nov 23:59 |
| confirm2-005 | Let car 65156 in for a while. (Mon 30 Nov 23:15) | NEEDS_REVIEW (unclear_time) |
| confirm2-006 | Please let 4931 in for bay 1. (Mon 30 Nov 23:15) | PROPOSE ALLOW 4931, permanent |
| confirm2-007 | Add number 7369 until tomorrow at 8. (Tue 24 Nov 10:10) | NEEDS_REVIEW (ambiguous_time) |
| confirm2-008 | Hello. (Tue 24 Nov 10:10) | UNSUPPORTED |
| confirm2-009 | Let car 7 3 4 4 8 in till eight thirty am. (Tue 24 Nov 10:10) | NEEDS_REVIEW (time_in_past) |
| confirm2-010 | allow number six one four one four five two till 18:15 (Thu 03 Dec 17:55) | NEEDS_REVIEW (invalid_number) |
| confirm2-011 | please add car 6020 bay 2 till tomorrow at 10am (Mon 30 Nov 23:15) | PROPOSE ALLOW 6020, until Tue 01 Dec 10:00 |
| confirm2-012 | approve five seven four seven six until today (Thu 03 Dec 17:55) | PROPOSE ALLOW 57476, until Thu 03 Dec 23:59 |
| confirm2-013 | allow 53 and 7693 (Mon 30 Nov 23:15) | NEEDS_REVIEW (multiple_numbers) |
| confirm2-014 | Remove plate number 4896. (Tue 24 Nov 10:10) | PROPOSE REMOVE 4896 |
| confirm2-015 | allow car five three five until eleven thirty am (Thu 03 Dec 17:55) | NEEDS_REVIEW (time_in_past) |
| confirm2-016 | let car 28118 in (Thu 03 Dec 17:55) | PROPOSE ALLOW 28118, permanent |
| confirm2-017 | Allow car number seven six seven six. (Tue 24 Nov 10:10) | PROPOSE ALLOW 7676, permanent |
| confirm2-018 | Okay add 492 for today. (Tue 24 Nov 10:10) | PROPOSE ALLOW 492, until Tue 24 Nov 23:59 |
| confirm2-019 | approve plate eight hundred ninety nine till 3 pm tomorrow (Thu 03 Dec 17:55) | PROPOSE ALLOW 899, until Fri 04 Dec 15:00 |
| confirm2-020 | Approve car 7 0 4 2 3 please. (Mon 30 Nov 23:15) | PROPOSE ALLOW 70423, permanent |
| confirm2-021 | Allow car 6 2 5 4 1 until five fifteen pm bay one. (Tue 24 Nov 10:10) | PROPOSE ALLOW 62541, until Tue 24 Nov 17:15 |
| confirm2-022 | 4 6 1 3 0 until tomorrow (Mon 30 Nov 23:15) | NEEDS_REVIEW (unclear_action) |
| confirm2-023 | Okay take car 1 off the list please. (Thu 03 Dec 17:55) | NEEDS_REVIEW (single_digit_number): REMOVE 1 |
| confirm2-024 | approve car number 1322 until tomorrow (Mon 30 Nov 23:15) | PROPOSE ALLOW 1322, until Tue 01 Dec 23:59 |
| confirm2-025 | Add a car in bay 2. (Thu 03 Dec 17:55) | NEEDS_REVIEW (missing_number) |
| confirm2-026 | Approve number nine three nine eight six till 9 AM. (Thu 03 Dec 17:55) | NEEDS_REVIEW (time_in_past) |
| confirm2-027 | let plate 78329 in until tonight (Thu 03 Dec 17:55) | NEEDS_REVIEW (unclear_time) |
| confirm2-028 | Add plate one one five one seven until eleven thirty PM. (Mon 30 Nov 23:15) | PROPOSE ALLOW 11517, until Mon 30 Nov 23:30 |
| confirm2-029 | Let my friend in until today. (Mon 30 Nov 23:15) | NEEDS_REVIEW (missing_number) |
| confirm2-030 | what's the weather today (Tue 24 Nov 10:10) | UNSUPPORTED |
| confirm2-031 | Let nine five four six three in. (Thu 03 Dec 17:55) | PROPOSE ALLOW 95463, permanent |
| confirm2-032 | allow plate 2 5 5 1 2 in bay two please (Mon 30 Nov 23:15) | PROPOSE ALLOW 25512, permanent |
| confirm2-033 | allow car number three seven three nine six till six am (Tue 24 Nov 10:10) | NEEDS_REVIEW (time_in_past) |
| confirm2-034 | add car 2 2 and car 76371 until tomorrow (Tue 24 Nov 10:10) | NEEDS_REVIEW (multiple_numbers) |
| confirm2-035 | Please allow plate seven hundred nineteen in bay two. (Mon 30 Nov 23:15) | PROPOSE ALLOW 719, permanent |
| confirm2-036 | is car 165 allowed (Thu 03 Dec 17:55) | UNSUPPORTED |
| confirm2-037 | take 72483 off the list from bay 1 (Tue 24 Nov 10:10) | PROPOSE REMOVE 72483 |
| confirm2-038 | Let plate number 1964 in. (Mon 30 Nov 23:15) | PROPOSE ALLOW 1964, permanent |
| confirm2-039 | hey let car number 9 6 5 in for bay one (Mon 30 Nov 23:15) | PROPOSE ALLOW 965, permanent |
| confirm2-040 | 592 until tomorrow. (Thu 03 Dec 17:55) | NEEDS_REVIEW (unclear_action) |
| confirm2-041 | add car 19932 and car 2683 until tomorrow (Mon 30 Nov 23:15) | NEEDS_REVIEW (multiple_numbers) |
| confirm2-042 | Hey approve plate six two three one one. (Thu 03 Dec 17:55) | PROPOSE ALLOW 62311, permanent |
| confirm2-043 | Approve car number 3101 until Monday. (Mon 30 Nov 23:15) | NEEDS_REVIEW (unclear_time) |
| confirm2-044 | allow car number 96979 please (Mon 30 Nov 23:15) | PROPOSE ALLOW 96979, permanent |
| confirm2-045 | Delete car number one oh three please. (Thu 03 Dec 17:55) | PROPOSE REMOVE 103 |
| confirm2-046 | add plate five zero three one nine bay 2 please (Mon 30 Nov 23:15) | PROPOSE ALLOW 50319, permanent |
| confirm2-047 | Let car number sixty five oh seven in until 1:15 pm please. (Tue 24 Nov 10:10) | PROPOSE ALLOW 6507, until Tue 24 Nov 13:15 |
| confirm2-048 | Allow 3 until today bay 2. (Tue 24 Nov 10:10) | NEEDS_REVIEW (single_digit_number): ALLOW 3, until Tue 24 Nov 23:59 |
| confirm2-049 | Please let plate 6 4 9 3 2 in until tomorrow. (Mon 30 Nov 23:15) | PROPOSE ALLOW 64932, until Tue 01 Dec 23:59 |
| confirm2-050 | add car five six four three please (Thu 03 Dec 17:55) | PROPOSE ALLOW 5643, permanent |
| confirm2-051 | add plate number five zero five four one in bay 2 (Thu 03 Dec 17:55) | PROPOSE ALLOW 50541, permanent |
| confirm2-052 | how many cars are parked (Thu 03 Dec 17:55) | UNSUPPORTED |
| confirm2-053 | Okay take plate number eight five three six two off the list. (Mon 30 Nov 23:15) | PROPOSE REMOVE 85362 |
| confirm2-054 | allow plate number 548 till ten (Tue 24 Nov 10:10) | NEEDS_REVIEW (ambiguous_time) |
| confirm2-055 | Hey add plate number two zero nine eight zero until 11:30 p.m. (Mon 30 Nov 23:15) | PROPOSE ALLOW 20980, until Mon 30 Nov 23:30 |
| confirm2-056 | Allow plate 1 0 5 2 bay 2 till five fifteen pm tomorrow. (Mon 30 Nov 23:15) | PROPOSE ALLOW 1052, until Tue 01 Dec 17:15 |
| confirm2-057 | let car 36388 in till 4 (Mon 30 Nov 23:15) | NEEDS_REVIEW (ambiguous_time) |
| confirm2-058 | add car 992 (Mon 30 Nov 23:15) | PROPOSE ALLOW 992, permanent |
| confirm2-059 | Let car number nine nine seven five seven seven in. (Thu 03 Dec 17:55) | NEEDS_REVIEW (invalid_number) |
| confirm2-060 | take 2 3 5 4 2 off the list (Thu 03 Dec 17:55) | PROPOSE REMOVE 23542 |
| confirm2-061 | is car 37179 allowed (Tue 24 Nov 10:10) | UNSUPPORTED |
| confirm2-062 | Okay add plate number 1 please. (Thu 03 Dec 17:55) | NEEDS_REVIEW (single_digit_number): ALLOW 1, permanent |
| confirm2-063 | Remove the car. (Thu 03 Dec 17:55) | NEEDS_REVIEW (missing_number) |
| confirm2-064 | please let car one two six four two in bay 1 (Mon 30 Nov 23:15) | PROPOSE ALLOW 12642, permanent |
| confirm2-065 | hey allow plate 95733 for bay 1 please (Thu 03 Dec 17:55) | PROPOSE ALLOW 95733, permanent |
| confirm2-066 | please approve four one nine one two in bay two till 23:15 (Tue 24 Nov 10:10) | PROPOSE ALLOW 41912, until Tue 24 Nov 23:15 |
| confirm2-067 | okay and car number 342 for seven days (Thu 03 Dec 17:55) | NEEDS_REVIEW (unclear_action) |
| confirm2-068 | Let number 96 in till 10:30 am. (Thu 03 Dec 17:55) | NEEDS_REVIEW (time_in_past) |
| confirm2-069 | add car number 6 until 23:30 please (Mon 30 Nov 23:15) | NEEDS_REVIEW (single_digit_number): ALLOW 6, until Mon 30 Nov 23:30 |
| confirm2-070 | Let three seven three seven five five five in until 10am tomorrow. (Tue 24 Nov 10:10) | NEEDS_REVIEW (invalid_number) |
| confirm2-071 | Allow plate number twenty one thousand one hundred seventy three for bay one until eight pm tonight. (Thu 03 Dec 17:55) | PROPOSE ALLOW 21173, until Thu 03 Dec 20:00 |
| confirm2-072 | please remove car 522 (Tue 24 Nov 10:10) | PROPOSE REMOVE 522 |
| confirm2-073 | hey let car number three four one seven nine in bay 2 until midnight (Thu 03 Dec 17:55) | PROPOSE ALLOW 34179, until Fri 04 Dec 00:00 |
| confirm2-074 | car number 83083 (Thu 03 Dec 17:55) | NEEDS_REVIEW (unclear_action) |
| confirm2-075 | approve 63761 until tomorrow in bay 2 (Tue 24 Nov 10:10) | PROPOSE ALLOW 63761, until Wed 25 Nov 23:59 |
| confirm2-076 | please approve number 3400 until tomorrow at 5pm (Mon 30 Nov 23:15) | PROPOSE ALLOW 3400, until Tue 01 Dec 17:00 |
| confirm2-077 | Allow 127 and 80928. (Tue 24 Nov 10:10) | NEEDS_REVIEW (multiple_numbers) |
| confirm2-078 | Approve car number 21951 until twelve fifteen PM. (Tue 24 Nov 10:10) | PROPOSE ALLOW 21951, until Tue 24 Nov 12:15 |
| confirm2-079 | allow the car until tomorrow at 7 pm (Tue 24 Nov 10:10) | NEEDS_REVIEW (missing_number) |
| confirm2-080 | is car five eight nine two allowed (Mon 30 Nov 23:15) | UNSUPPORTED |
| confirm2-081 | let plate number 341 in until tonight (Tue 24 Nov 10:10) | NEEDS_REVIEW (unclear_time) |
| confirm2-082 | Okay allow car thirty nine sixty four bay one until today. (Thu 03 Dec 17:55) | PROPOSE ALLOW 3964, until Thu 03 Dec 23:59 |
| confirm2-083 | allow my brother's car (Tue 24 Nov 10:10) | NEEDS_REVIEW (missing_number) |
| confirm2-084 | Allow 1 0 1 5 bay one until ten fifteen p.m. (Tue 24 Nov 10:10) | PROPOSE ALLOW 1015, until Tue 24 Nov 22:15 |
| confirm2-085 | approve plate number 76493 until later (Tue 24 Nov 10:10) | NEEDS_REVIEW (unclear_time) |
| confirm2-086 | Let plate 5 0 3 9 in bay 1 until Thursday. (Tue 24 Nov 10:10) | PROPOSE ALLOW 5039, until Thu 26 Nov 23:59 |
| confirm2-087 | Hey add number nine two eight six eight. (Tue 24 Nov 10:10) | PROPOSE ALLOW 92868, permanent |
| confirm2-088 | Approve car five three eight two two until midnight. (Thu 03 Dec 17:55) | PROPOSE ALLOW 53822, until Fri 04 Dec 00:00 |
| confirm2-089 | car eighty one thousand seven hundred seventy in bay 2 (Mon 30 Nov 23:15) | NEEDS_REVIEW (unclear_action) |
| confirm2-090 | car number four eight six seven (Mon 30 Nov 23:15) | NEEDS_REVIEW (unclear_action) |
| confirm2-091 | please take car three nine one eight off the list (Tue 24 Nov 10:10) | PROPOSE REMOVE 3918 |
| confirm2-092 | allow plate number 9 3 3 in bay 1 until 7pm tonight (Thu 03 Dec 17:55) | PROPOSE ALLOW 933, until Thu 03 Dec 19:00 |
| confirm2-093 | approve car number 339 until one fifteen pm tomorrow please (Thu 03 Dec 17:55) | PROPOSE ALLOW 339, until Fri 04 Dec 13:15 |
| confirm2-094 | let number 55 in for six days please (Thu 03 Dec 17:55) | PROPOSE ALLOW 55, until Wed 09 Dec 17:55 |
| confirm2-095 | allow plate 2 3 8 1 for 2 hours (Tue 24 Nov 10:10) | PROPOSE ALLOW 2381, until Tue 24 Nov 12:10 |
| confirm2-096 | please delete number 5003 (Mon 30 Nov 23:15) | PROPOSE REMOVE 5003 |
| confirm2-097 | okay add number 91 in bay 1 please (Mon 30 Nov 23:15) | PROPOSE ALLOW 91, permanent |
| confirm2-098 | Please approve car two thousand one hundred seventy nine for a day in bay two. (Mon 30 Nov 23:15) | PROPOSE ALLOW 2179, until Tue 01 Dec 23:15 |
| confirm2-099 | Add car one five four eight six in bay one. (Thu 03 Dec 17:55) | PROPOSE ALLOW 15486, permanent |
| confirm2-100 | Take 59023 off the list. (Tue 24 Nov 10:10) | PROPOSE REMOVE 59023 |
| confirm2-101 | Let 40724 in. (Tue 24 Nov 10:10) | PROPOSE ALLOW 40724, permanent |
| confirm2-102 | Allow the car. (Thu 03 Dec 17:55) | NEEDS_REVIEW (missing_number) |
| confirm2-103 | Car one two eight zero four in bay 2. (Mon 30 Nov 23:15) | NEEDS_REVIEW (unclear_action) |
| confirm2-104 | Add car number 24569 until 12 pm tomorrow please. (Tue 24 Nov 10:10) | PROPOSE ALLOW 24569, until Wed 25 Nov 12:00 |
| confirm2-105 | Show me the permits. (Mon 30 Nov 23:15) | UNSUPPORTED |
| confirm2-106 | okay take three seven three six zero off the list please (Thu 03 Dec 17:55) | PROPOSE REMOVE 37360 |
| confirm2-107 | Hey remove number 83842 from bay 1. (Tue 24 Nov 10:10) | PROPOSE REMOVE 83842 |
| confirm2-108 | And car 1039 till nine pm please. (Tue 24 Nov 10:10) | NEEDS_REVIEW (unclear_action) |
| confirm2-109 | add number 4 2 9 8 till eleven (Mon 30 Nov 23:15) | NEEDS_REVIEW (ambiguous_time) |
| confirm2-110 | Add 6 8 2 6 5 until eight. (Thu 03 Dec 17:55) | NEEDS_REVIEW (ambiguous_time) |
| confirm2-111 | Allow plate number fifty seven thousand six hundred thirty five. (Mon 30 Nov 23:15) | PROPOSE ALLOW 57635, permanent |
| confirm2-112 | Approve plate 6 3 9 3 until 1pm. (Thu 03 Dec 17:55) | NEEDS_REVIEW (time_in_past) |
| confirm2-113 | Delete twenty one thousand six hundred thirteen. (Mon 30 Nov 23:15) | PROPOSE REMOVE 21613 |
| confirm2-114 | add 6 4 1 2 till tomorrow for bay 1 please (Mon 30 Nov 23:15) | PROPOSE ALLOW 6412, until Tue 01 Dec 23:59 |
| confirm2-115 | delete number three thousand nine hundred forty seven (Thu 03 Dec 17:55) | PROPOSE REMOVE 3947 |
| confirm2-116 | take car number two nine one four off the list (Thu 03 Dec 17:55) | PROPOSE REMOVE 2914 |
| confirm2-117 | allow number seventeen fifty six until 6:30 (Thu 03 Dec 17:55) | NEEDS_REVIEW (ambiguous_time) |
| confirm2-118 | Allow seven one until tomorrow morning. (Thu 03 Dec 17:55) | NEEDS_REVIEW (unclear_time) |
| confirm2-119 | Hey delete car number 631 from bay 2 please. (Tue 24 Nov 10:10) | PROPOSE REMOVE 631 |
| confirm2-120 | Add plate 71559 in bay two please. (Thu 03 Dec 17:55) | PROPOSE ALLOW 71559, permanent |
