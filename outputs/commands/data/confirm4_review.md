# Command set: confirm4 (120 commands)

| id | command (said at) | expected |
|---|---|---|
| confirm4-001 | car 9485 in bay 2 (Thu 26 Nov 11:20) | NEEDS_REVIEW (unclear_action) |
| confirm4-002 | Car 2099 in bay 2. (Thu 26 Nov 11:20) | NEEDS_REVIEW (unclear_action) |
| confirm4-003 | Approve 33994 until two pm. (Sat 05 Dec 21:50) | NEEDS_REVIEW (time_in_past) |
| confirm4-004 | hey approve 69795 till tomorrow please (Tue 01 Dec 07:35) | PROPOSE ALLOW 69795, until Wed 02 Dec 23:59 |
| confirm4-005 | Allow number 4517 until later. (Sat 05 Dec 21:50) | NEEDS_REVIEW (unclear_time) |
| confirm4-006 | Hey remove number 1985. (Sat 05 Dec 21:50) | PROPOSE REMOVE 1985 |
| confirm4-007 | let number 1788 in for a while (Thu 26 Nov 11:20) | NEEDS_REVIEW (unclear_time) |
| confirm4-008 | please delete car 5019 (Thu 26 Nov 11:20) | PROPOSE REMOVE 5019 |
| confirm4-009 | Add plate number 82118 until noon. (Tue 01 Dec 07:35) | PROPOSE ALLOW 82118, until Tue 01 Dec 12:00 |
| confirm4-010 | Allow 8013 for bay one. (Sat 05 Dec 21:50) | PROPOSE ALLOW 8013, permanent |
| confirm4-011 | add a car in bay 2 (Tue 01 Dec 07:35) | NEEDS_REVIEW (missing_number) |
| confirm4-012 | Okay let car 2053 in for today. (Sat 05 Dec 21:50) | PROPOSE ALLOW 2053, until Sat 05 Dec 23:59 |
| confirm4-013 | And 3 5 6 5 until 12 pm. (Tue 01 Dec 07:35) | NEEDS_REVIEW (unclear_action) |
| confirm4-014 | okay remove car number 8 6 3 0 please (Thu 26 Nov 11:20) | PROPOSE REMOVE 8630 |
| confirm4-015 | Add car 1635 and car 44511 until tomorrow. (Thu 26 Nov 11:20) | NEEDS_REVIEW (multiple_numbers) |
| confirm4-016 | approve plate 24007 till tomorrow at 11 (Thu 26 Nov 11:20) | NEEDS_REVIEW (ambiguous_time) |
| confirm4-017 | Allow plate number 245125 until tomorrow. (Thu 26 Nov 11:20) | NEEDS_REVIEW (invalid_number) |
| confirm4-018 | Extend the permit for car 27850. (Tue 01 Dec 07:35) | UNSUPPORTED |
| confirm4-019 | allow 727 and 3 5 8 5 5 (Thu 26 Nov 11:20) | NEEDS_REVIEW (multiple_numbers) |
| confirm4-020 | hey let number 27490 in for bay 2 please (Sat 05 Dec 21:50) | PROPOSE ALLOW 27490, permanent |
| confirm4-021 | hey add 4484 for a week (Sat 05 Dec 21:50) | PROPOSE ALLOW 4484, until Sat 12 Dec 21:50 |
| confirm4-022 | please take 5515 off the list (Sat 05 Dec 21:50) | PROPOSE REMOVE 5515 |
| confirm4-023 | is car 8 5 0 8 allowed (Tue 01 Dec 07:35) | UNSUPPORTED |
| confirm4-024 | Approve number 23704 until tonight. (Sat 05 Dec 21:50) | NEEDS_REVIEW (unclear_time) |
| confirm4-025 | hey approve number seventy one thousand twenty seven for one week please (Tue 01 Dec 07:35) | PROPOSE ALLOW 71027, until Tue 08 Dec 07:35 |
| confirm4-026 | Okay remove car number 1 from bay 1. (Tue 01 Dec 07:35) | NEEDS_REVIEW (single_digit_number): REMOVE 1 |
| confirm4-027 | Remove car number 48525. (Sat 05 Dec 21:50) | PROPOSE REMOVE 48525 |
| confirm4-028 | Approve number three zero nine till tomorrow please. (Thu 26 Nov 11:20) | PROPOSE ALLOW 309, until Fri 27 Nov 23:59 |
| confirm4-029 | let my friend in till 10 p.m. tonight (Sat 05 Dec 21:50) | NEEDS_REVIEW (missing_number) |
| confirm4-030 | okay add car 76175 for today (Tue 01 Dec 07:35) | PROPOSE ALLOW 76175, until Tue 01 Dec 23:59 |
| confirm4-031 | please remove car 5 from bay 2 (Tue 01 Dec 07:35) | NEEDS_REVIEW (single_digit_number): REMOVE 5 |
| confirm4-032 | what's the weather today (Sat 05 Dec 21:50) | UNSUPPORTED |
| confirm4-033 | add 7162 for one day (Sat 05 Dec 21:50) | PROPOSE ALLOW 7162, until Sun 06 Dec 21:50 |
| confirm4-034 | please allow car 265 (Tue 01 Dec 07:35) | PROPOSE ALLOW 265, permanent |
| confirm4-035 | Please allow plate seven six five four seven bay one. (Tue 01 Dec 07:35) | PROPOSE ALLOW 76547, permanent |
| confirm4-036 | Delete car seven six four nine six please. (Tue 01 Dec 07:35) | PROPOSE REMOVE 76496 |
| confirm4-037 | Approve 9 0 4 7 8 until 6a.m. (Thu 26 Nov 11:20) | NEEDS_REVIEW (time_in_past) |
| confirm4-038 | allow car number one eight six five seven (Sat 05 Dec 21:50) | PROPOSE ALLOW 18657, permanent |
| confirm4-039 | add car 94881 and car nine oh three seven one until tomorrow (Sat 05 Dec 21:50) | NEEDS_REVIEW (multiple_numbers) |
| confirm4-040 | allow the car for 2 hours (Tue 01 Dec 07:35) | NEEDS_REVIEW (missing_number) |
| confirm4-041 | Please add car 230 till tomorrow. (Thu 26 Nov 11:20) | PROPOSE ALLOW 230, until Fri 27 Nov 23:59 |
| confirm4-042 | okay remove plate 48 (Tue 01 Dec 07:35) | PROPOSE REMOVE 48 |
| confirm4-043 | let plate forty one thirty eight in until six (Sat 05 Dec 21:50) | NEEDS_REVIEW (ambiguous_time) |
| confirm4-044 | 73273 until tomorrow. (Thu 26 Nov 11:20) | NEEDS_REVIEW (unclear_action) |
| confirm4-045 | hey add forty six sixty three bay two (Sat 05 Dec 21:50) | PROPOSE ALLOW 4663, permanent |
| confirm4-046 | please allow car 3702 till tomorrow (Thu 26 Nov 11:20) | PROPOSE ALLOW 3702, until Fri 27 Nov 23:59 |
| confirm4-047 | add plate one eight eight four until tomorrow morning (Thu 26 Nov 11:20) | NEEDS_REVIEW (unclear_time) |
| confirm4-048 | approve car 2667 till tomorrow at 5 (Thu 26 Nov 11:20) | NEEDS_REVIEW (ambiguous_time) |
| confirm4-049 | let car number 556 in till 10 PM (Sat 05 Dec 21:50) | PROPOSE ALLOW 556, until Sat 05 Dec 22:00 |
| confirm4-050 | allow number 7 4 2 8 until tomorrow please (Sat 05 Dec 21:50) | PROPOSE ALLOW 7428, until Sun 06 Dec 23:59 |
| confirm4-051 | approve 66875 please (Thu 26 Nov 11:20) | PROPOSE ALLOW 66875, permanent |
| confirm4-052 | hey take plate number 9 off the list (Thu 26 Nov 11:20) | NEEDS_REVIEW (single_digit_number): REMOVE 9 |
| confirm4-053 | add 27168 (Tue 01 Dec 07:35) | PROPOSE ALLOW 27168, permanent |
| confirm4-054 | hey delete number seven thousand one hundred six from bay 2 please (Tue 01 Dec 07:35) | PROPOSE REMOVE 7106 |
| confirm4-055 | Approve plate number 63046 until twelve. (Tue 01 Dec 07:35) | NEEDS_REVIEW (ambiguous_time) |
| confirm4-056 | allow one zero eight three two and eight one five four (Sat 05 Dec 21:50) | NEEDS_REVIEW (multiple_numbers) |
| confirm4-057 | okay remove number 63054 from bay 1 (Tue 01 Dec 07:35) | PROPOSE REMOVE 63054 |
| confirm4-058 | Approve number 3270 in bay one until 9PM please. (Thu 26 Nov 11:20) | PROPOSE ALLOW 3270, until Thu 26 Nov 21:00 |
| confirm4-059 | hey approve plate number nine six oh five oh bay 1 (Thu 26 Nov 11:20) | PROPOSE ALLOW 96050, permanent |
| confirm4-060 | Hey remove four oh three nine please. (Thu 26 Nov 11:20) | PROPOSE REMOVE 4039 |
| confirm4-061 | approve 895 for a week (Sat 05 Dec 21:50) | PROPOSE ALLOW 895, until Sat 12 Dec 21:50 |
| confirm4-062 | let car 6 9 in for a week please (Tue 01 Dec 07:35) | PROPOSE ALLOW 69, until Tue 08 Dec 07:35 |
| confirm4-063 | Okay add plate number 142 until tomorrow at 2:30 PM. (Sat 05 Dec 21:50) | PROPOSE ALLOW 142, until Sun 06 Dec 14:30 |
| confirm4-064 | Allow plate 419 for 3 hours. (Tue 01 Dec 07:35) | PROPOSE ALLOW 419, until Tue 01 Dec 10:35 |
| confirm4-065 | Please take car 32700 off the list. (Tue 01 Dec 07:35) | PROPOSE REMOVE 32700 |
| confirm4-066 | let plate nine seven nine one in until tomorrow (Sat 05 Dec 21:50) | PROPOSE ALLOW 9791, until Sun 06 Dec 23:59 |
| confirm4-067 | Allow plate number 373016 for thirty minutes. (Sat 05 Dec 21:50) | NEEDS_REVIEW (invalid_number) |
| confirm4-068 | Add plate number 9236 in bay one. (Tue 01 Dec 07:35) | PROPOSE ALLOW 9236, permanent |
| confirm4-069 | approve plate five oh five seven until tomorrow please (Tue 01 Dec 07:35) | PROPOSE ALLOW 5057, until Wed 02 Dec 23:59 |
| confirm4-070 | hey allow car six till midnight (Sat 05 Dec 21:50) | NEEDS_REVIEW (single_digit_number): ALLOW 6, until Sun 06 Dec 00:00 |
| confirm4-071 | approve number three nine two seven one till tomorrow (Sat 05 Dec 21:50) | PROPOSE ALLOW 39271, until Sun 06 Dec 23:59 |
| confirm4-072 | is car 369 allowed (Tue 01 Dec 07:35) | UNSUPPORTED |
| confirm4-073 | approve car 698045 till tomorrow (Sat 05 Dec 21:50) | NEEDS_REVIEW (invalid_number) |
| confirm4-074 | remove the car (Sat 05 Dec 21:50) | NEEDS_REVIEW (missing_number) |
| confirm4-075 | please remove car number 5 4 4 4 2 (Sat 05 Dec 21:50) | PROPOSE REMOVE 54442 |
| confirm4-076 | add car number two four nine till one p.m. (Sat 05 Dec 21:50) | NEEDS_REVIEW (time_in_past) |
| confirm4-077 | Okay allow plate number 11868 until tomorrow. (Tue 01 Dec 07:35) | PROPOSE ALLOW 11868, until Wed 02 Dec 23:59 |
| confirm4-078 | okay approve plate 75752 bay 1 (Sat 05 Dec 21:50) | PROPOSE ALLOW 75752, permanent |
| confirm4-079 | Allow the car until 10pm. (Sat 05 Dec 21:50) | NEEDS_REVIEW (missing_number) |
| confirm4-080 | allow car number four six six two three bay two (Tue 01 Dec 07:35) | PROPOSE ALLOW 46623, permanent |
| confirm4-081 | Car number 39107. (Thu 26 Nov 11:20) | NEEDS_REVIEW (unclear_action) |
| confirm4-082 | Please add car number 8 8 1 9 2 for a week. (Thu 26 Nov 11:20) | PROPOSE ALLOW 88192, until Thu 03 Dec 11:20 |
| confirm4-083 | Let plate 8640 in bay 1 for 30 minutes. (Sat 05 Dec 21:50) | PROPOSE ALLOW 8640, until Sat 05 Dec 22:20 |
| confirm4-084 | allow plate 680 until tomorrow 3PM for bay 2 please (Tue 01 Dec 07:35) | PROPOSE ALLOW 680, until Wed 02 Dec 15:00 |
| confirm4-085 | Allow 20976 bay 1 till 11 pm tonight. (Thu 26 Nov 11:20) | PROPOSE ALLOW 20976, until Thu 26 Nov 23:00 |
| confirm4-086 | Is car 69380 allowed? (Sat 05 Dec 21:50) | UNSUPPORTED |
| confirm4-087 | Add 313029 till tomorrow. (Thu 26 Nov 11:20) | NEEDS_REVIEW (invalid_number) |
| confirm4-088 | Allow car 61993 bay one until tomorrow 12pm. (Sat 05 Dec 21:50) | PROPOSE ALLOW 61993, until Sun 06 Dec 12:00 |
| confirm4-089 | car number 737 (Tue 01 Dec 07:35) | NEEDS_REVIEW (unclear_action) |
| confirm4-090 | Let car number eight four eight three in till seven pm today. (Sat 05 Dec 21:50) | NEEDS_REVIEW (time_in_past) |
| confirm4-091 | hey approve car 9974 for bay 2 until today please (Tue 01 Dec 07:35) | PROPOSE ALLOW 9974, until Tue 01 Dec 23:59 |
| confirm4-092 | remove car number four seven eight six from bay 2 (Thu 26 Nov 11:20) | PROPOSE REMOVE 4786 |
| confirm4-093 | Add car number four thousand nine hundred forty in bay 2 please. (Thu 26 Nov 11:20) | PROPOSE ALLOW 4940, permanent |
| confirm4-094 | Approve number 5966 until 3:30. (Thu 26 Nov 11:20) | NEEDS_REVIEW (ambiguous_time) |
| confirm4-095 | And number 97531 till Saturday. (Tue 01 Dec 07:35) | NEEDS_REVIEW (unclear_action) |
| confirm4-096 | approve car number 5256 till 7:30 a.m. (Tue 01 Dec 07:35) | NEEDS_REVIEW (time_in_past) |
| confirm4-097 | Approve car number 33900 for bay two. (Thu 26 Nov 11:20) | PROPOSE ALLOW 33900, permanent |
| confirm4-098 | add 50291 until Monday in bay two please (Thu 26 Nov 11:20) | PROPOSE ALLOW 50291, until Mon 30 Nov 23:59 |
| confirm4-099 | approve plate 963 until 4:30 (Sat 05 Dec 21:50) | NEEDS_REVIEW (ambiguous_time) |
| confirm4-100 | allow plate five two seven two seven (Tue 01 Dec 07:35) | PROPOSE ALLOW 52727, permanent |
| confirm4-101 | Hey allow number nine four five until end of day. (Tue 01 Dec 07:35) | PROPOSE ALLOW 945, until Tue 01 Dec 23:59 |
| confirm4-102 | Show me the permits. (Thu 26 Nov 11:20) | UNSUPPORTED |
| confirm4-103 | Allow plate number 867 for bay 1 till 9:15 PM. (Tue 01 Dec 07:35) | PROPOSE ALLOW 867, until Tue 01 Dec 21:15 |
| confirm4-104 | How many cars are parked? (Sat 05 Dec 21:50) | UNSUPPORTED |
| confirm4-105 | 35243 until tomorrow (Sat 05 Dec 21:50) | NEEDS_REVIEW (unclear_action) |
| confirm4-106 | delete number 1 8 2 (Tue 01 Dec 07:35) | PROPOSE REMOVE 182 |
| confirm4-107 | delete 536 (Sat 05 Dec 21:50) | PROPOSE REMOVE 536 |
| confirm4-108 | Approve car four six seven seven until eleven am today. (Sat 05 Dec 21:50) | NEEDS_REVIEW (time_in_past) |
| confirm4-109 | Please let 4 8 2 in. (Tue 01 Dec 07:35) | PROPOSE ALLOW 482, permanent |
| confirm4-110 | let number 57865 in until tomorrow please (Thu 26 Nov 11:20) | PROPOSE ALLOW 57865, until Fri 27 Nov 23:59 |
| confirm4-111 | Hello. (Tue 01 Dec 07:35) | UNSUPPORTED |
| confirm4-112 | Allow car 9237 for a week. (Tue 01 Dec 07:35) | PROPOSE ALLOW 9237, until Tue 08 Dec 07:35 |
| confirm4-113 | Add number 6541 until 11 PM in bay 2 please. (Sat 05 Dec 21:50) | PROPOSE ALLOW 6541, until Sat 05 Dec 23:00 |
| confirm4-114 | approve 800 (Sat 05 Dec 21:50) | PROPOSE ALLOW 800, permanent |
| confirm4-115 | let number 3173 in until tonight (Tue 01 Dec 07:35) | NEEDS_REVIEW (unclear_time) |
| confirm4-116 | allow my brother's car (Thu 26 Nov 11:20) | NEEDS_REVIEW (missing_number) |
| confirm4-117 | allow 5 6 3 0 until Tuesday (Tue 01 Dec 07:35) | NEEDS_REVIEW (unclear_time) |
| confirm4-118 | Okay add plate 1791 until two pm for bay 1. (Tue 01 Dec 07:35) | PROPOSE ALLOW 1791, until Tue 01 Dec 14:00 |
| confirm4-119 | hey remove car 7417 (Sat 05 Dec 21:50) | PROPOSE REMOVE 7417 |
| confirm4-120 | hey add number five four one until tomorrow bay one (Tue 01 Dec 07:35) | PROPOSE ALLOW 541, until Wed 02 Dec 23:59 |
