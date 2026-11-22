# Command set: check (120 commands)

| id | command (said at) | expected |
|---|---|---|
| check-001 | Car 598 in bay 2. (Sun 22 Nov 07:50) | NEEDS_REVIEW (unclear_action) |
| check-002 | allow plate four thousand three hundred two till 2:30 (Fri 27 Nov 22:05) | NEEDS_REVIEW (ambiguous_time) |
| check-003 | 94794 until tomorrow. (Wed 25 Nov 16:20) | NEEDS_REVIEW (unclear_action) |
| check-004 | Allow the car until eight pm. (Sun 22 Nov 07:50) | NEEDS_REVIEW (missing_number) |
| check-005 | allow my brother's car (Wed 25 Nov 16:20) | NEEDS_REVIEW (missing_number) |
| check-006 | let plate number 8467 in until six AM (Fri 27 Nov 22:05) | NEEDS_REVIEW (time_in_past) |
| check-007 | Let plate 23745 in until today. (Wed 25 Nov 16:20) | PROPOSE ALLOW 23745, until Wed 25 Nov 23:59 |
| check-008 | Okay allow car number 1 2 7 8 5 till 5pm. (Sun 22 Nov 07:50) | PROPOSE ALLOW 12785, until Sun 22 Nov 17:00 |
| check-009 | please allow car number 90237 until tomorrow 12 PM in bay two (Wed 25 Nov 16:20) | PROPOSE ALLOW 90237, until Thu 26 Nov 12:00 |
| check-010 | Hey remove 1. (Wed 25 Nov 16:20) | NEEDS_REVIEW (single_digit_number): REMOVE 1 |
| check-011 | Allow plate eight three eight seven seven till tomorrow. (Sun 22 Nov 07:50) | PROPOSE ALLOW 83877, until Mon 23 Nov 23:59 |
| check-012 | Allow car number 8025659 until midnight. (Fri 27 Nov 22:05) | NEEDS_REVIEW (invalid_number) |
| check-013 | Let car eleven thousand four hundred eighteen in till four. (Fri 27 Nov 22:05) | NEEDS_REVIEW (ambiguous_time) |
| check-014 | Okay let plate 223 in for today. (Wed 25 Nov 16:20) | PROPOSE ALLOW 223, until Wed 25 Nov 23:59 |
| check-015 | Approve car number 673. (Fri 27 Nov 22:05) | PROPOSE ALLOW 673, permanent |
| check-016 | Please add number 90. (Fri 27 Nov 22:05) | PROPOSE ALLOW 90, permanent |
| check-017 | Okay allow plate one five eight zero eight in bay 2 until tomorrow. (Fri 27 Nov 22:05) | PROPOSE ALLOW 15808, until Sat 28 Nov 23:59 |
| check-018 | hey add twenty four fifty three until noon for bay 1 (Sun 22 Nov 07:50) | PROPOSE ALLOW 2453, until Sun 22 Nov 12:00 |
| check-019 | delete 14583 from bay 1 (Wed 25 Nov 16:20) | PROPOSE REMOVE 14583 |
| check-020 | Let 5729 in until 6 am. (Sun 22 Nov 07:50) | NEEDS_REVIEW (time_in_past) |
| check-021 | take car number 9 off the list (Wed 25 Nov 16:20) | NEEDS_REVIEW (single_digit_number): REMOVE 9 |
| check-022 | remove the car (Wed 25 Nov 16:20) | NEEDS_REVIEW (missing_number) |
| check-023 | Allow the car. (Wed 25 Nov 16:20) | NEEDS_REVIEW (missing_number) |
| check-024 | Add car number 87476 please. (Sun 22 Nov 07:50) | PROPOSE ALLOW 87476, permanent |
| check-025 | please let number 3 2 6 6 in till Monday (Sun 22 Nov 07:50) | PROPOSE ALLOW 3266, until Mon 23 Nov 23:59 |
| check-026 | let twenty three in (Sun 22 Nov 07:50) | PROPOSE ALLOW 23, permanent |
| check-027 | Car number 44. (Fri 27 Nov 22:05) | NEEDS_REVIEW (unclear_action) |
| check-028 | Okay allow 55035 until 10:30 p.m. (Fri 27 Nov 22:05) | PROPOSE ALLOW 55035, until Fri 27 Nov 22:30 |
| check-029 | Add car 4 1 1 1 and car 21119 until tomorrow. (Wed 25 Nov 16:20) | NEEDS_REVIEW (multiple_numbers) |
| check-030 | Allow plate four thousand three hundred ninety eight until 7 am. (Sun 22 Nov 07:50) | NEEDS_REVIEW (time_in_past) |
| check-031 | Okay approve plate twenty six thousand eight hundred thirty nine until Monday in bay 2 please. (Fri 27 Nov 22:05) | PROPOSE ALLOW 26839, until Mon 30 Nov 23:59 |
| check-032 | Allow 3 3 and 3293. (Wed 25 Nov 16:20) | NEEDS_REVIEW (multiple_numbers) |
| check-033 | Let two oh three nine in bay 1 for one hour. (Sun 22 Nov 07:50) | PROPOSE ALLOW 2039, until Sun 22 Nov 08:50 |
| check-034 | please approve 3889 (Wed 25 Nov 16:20) | PROPOSE ALLOW 3889, permanent |
| check-035 | hello (Sun 22 Nov 07:50) | UNSUPPORTED |
| check-036 | let number two eight nine zero six in until tonight (Wed 25 Nov 16:20) | NEEDS_REVIEW (unclear_time) |
| check-037 | Please delete car number 8300. (Fri 27 Nov 22:05) | PROPOSE REMOVE 8300 |
| check-038 | remove plate number 15316 please (Fri 27 Nov 22:05) | PROPOSE REMOVE 15316 |
| check-039 | Add 6 3 7 0 till seven thirty am. (Sun 22 Nov 07:50) | NEEDS_REVIEW (time_in_past) |
| check-040 | allow plate two one two eight eight until nine thirty PM (Wed 25 Nov 16:20) | PROPOSE ALLOW 21288, until Wed 25 Nov 21:30 |
| check-041 | Approve car five two four seven three till 7. (Wed 25 Nov 16:20) | NEEDS_REVIEW (ambiguous_time) |
| check-042 | What's the weather today? (Sun 22 Nov 07:50) | UNSUPPORTED |
| check-043 | allow 2978 and seven one nine seven (Sun 22 Nov 07:50) | NEEDS_REVIEW (multiple_numbers) |
| check-044 | add a car in bay 2 (Wed 25 Nov 16:20) | NEEDS_REVIEW (missing_number) |
| check-045 | allow car number six one four eight until 7:30 (Sun 22 Nov 07:50) | NEEDS_REVIEW (ambiguous_time) |
| check-046 | Hey let plate number 381 in till Wednesday. (Fri 27 Nov 22:05) | PROPOSE ALLOW 381, until Wed 02 Dec 23:59 |
| check-047 | allow six eight zero three zero for one week (Sun 22 Nov 07:50) | PROPOSE ALLOW 68030, until Sun 29 Nov 07:50 |
| check-048 | Let number six two eight two three one zero in until Thursday. (Sun 22 Nov 07:50) | NEEDS_REVIEW (invalid_number) |
| check-049 | Please remove plate 4420. (Sun 22 Nov 07:50) | PROPOSE REMOVE 4420 |
| check-050 | Let plate number ninety three thousand one hundred ninety one in till tomorrow at 5. (Sun 22 Nov 07:50) | NEEDS_REVIEW (ambiguous_time) |
| check-051 | please take car number 9 7 7 7 off the list (Fri 27 Nov 22:05) | PROPOSE REMOVE 9777 |
| check-052 | Approve 8044 until seven a.m. today. (Fri 27 Nov 22:05) | NEEDS_REVIEW (time_in_past) |
| check-053 | Add eight thousand seven hundred sixty six. (Sun 22 Nov 07:50) | PROPOSE ALLOW 8766, permanent |
| check-054 | Hey approve plate number eight two oh four one until Thursday. (Sun 22 Nov 07:50) | PROPOSE ALLOW 82041, until Thu 26 Nov 23:59 |
| check-055 | is car 55090 allowed (Fri 27 Nov 22:05) | UNSUPPORTED |
| check-056 | Please approve car 8 2 5 2 6 until 11:30 PM. (Fri 27 Nov 22:05) | PROPOSE ALLOW 82526, until Fri 27 Nov 23:30 |
| check-057 | let 1 9 2 9 in for a week (Wed 25 Nov 16:20) | PROPOSE ALLOW 1929, until Wed 02 Dec 16:20 |
| check-058 | Take car 7 1 4 4 off the list please. (Wed 25 Nov 16:20) | PROPOSE REMOVE 7144 |
| check-059 | let car number 891436 in (Sun 22 Nov 07:50) | NEEDS_REVIEW (invalid_number) |
| check-060 | add car 43898 (Wed 25 Nov 16:20) | PROPOSE ALLOW 43898, permanent |
| check-061 | take car number two six nine three off the list (Wed 25 Nov 16:20) | PROPOSE REMOVE 2693 |
| check-062 | allow car seven thousand one hundred thirty four until tomorrow morning (Fri 27 Nov 22:05) | NEEDS_REVIEW (unclear_time) |
| check-063 | Please allow plate number 89405. (Fri 27 Nov 22:05) | PROPOSE ALLOW 89405, permanent |
| check-064 | Okay add car number six eight. (Fri 27 Nov 22:05) | PROPOSE ALLOW 68, permanent |
| check-065 | Approve number thirty eight thousand two hundred thirty five for a while. (Wed 25 Nov 16:20) | NEEDS_REVIEW (unclear_time) |
| check-066 | approve car number 440 till ten thirty PM (Wed 25 Nov 16:20) | PROPOSE ALLOW 440, until Wed 25 Nov 22:30 |
| check-067 | add car 96486 and car 5701 until tomorrow (Wed 25 Nov 16:20) | NEEDS_REVIEW (multiple_numbers) |
| check-068 | approve plate number 5 1 2 8 0 until tomorrow nine thirty am (Fri 27 Nov 22:05) | PROPOSE ALLOW 51280, until Sat 28 Nov 09:30 |
| check-069 | Allow number 7. (Fri 27 Nov 22:05) | NEEDS_REVIEW (single_digit_number): ALLOW 7, permanent |
| check-070 | Is car 7284 allowed? (Sun 22 Nov 07:50) | UNSUPPORTED |
| check-071 | Allow plate number 15908 until tomorrow at ten pm. (Wed 25 Nov 16:20) | PROPOSE ALLOW 15908, until Thu 26 Nov 22:00 |
| check-072 | is car forty six thousand sixty two allowed (Fri 27 Nov 22:05) | UNSUPPORTED |
| check-073 | remove plate number 70840 (Sun 22 Nov 07:50) | PROPOSE REMOVE 70840 |
| check-074 | add number nine six three eight in bay 2 (Wed 25 Nov 16:20) | PROPOSE ALLOW 9638, permanent |
| check-075 | Car number fifty four thirty eight. (Wed 25 Nov 16:20) | NEEDS_REVIEW (unclear_action) |
| check-076 | okay let number 3236 in till nine p.m. (Wed 25 Nov 16:20) | PROPOSE ALLOW 3236, until Wed 25 Nov 21:00 |
| check-077 | approve plate 54591 until Sunday (Sun 22 Nov 07:50) | NEEDS_REVIEW (unclear_time) |
| check-078 | hey remove car number two two two nine six please (Wed 25 Nov 16:20) | PROPOSE REMOVE 22296 |
| check-079 | Remove 5725. (Fri 27 Nov 22:05) | PROPOSE REMOVE 5725 |
| check-080 | Take plate number 5 7 7 9 5 off the list from bay 1. (Sun 22 Nov 07:50) | PROPOSE REMOVE 57795 |
| check-081 | Please let number nine three two in. (Fri 27 Nov 22:05) | PROPOSE ALLOW 932, permanent |
| check-082 | add plate 67336 in bay two (Fri 27 Nov 22:05) | PROPOSE ALLOW 67336, permanent |
| check-083 | let plate number 86422 in till 10:15 pm tonight (Wed 25 Nov 16:20) | PROPOSE ALLOW 86422, until Wed 25 Nov 22:15 |
| check-084 | let my friend in until five pm (Sun 22 Nov 07:50) | NEEDS_REVIEW (missing_number) |
| check-085 | Hey remove plate number 508 please. (Wed 25 Nov 16:20) | PROPOSE REMOVE 508 |
| check-086 | Approve number 5 7 7 5 1 1 4. (Sun 22 Nov 07:50) | NEEDS_REVIEW (invalid_number) |
| check-087 | delete fifty seven thousand five hundred fifty five (Wed 25 Nov 16:20) | PROPOSE REMOVE 57555 |
| check-088 | Let plate 2 0 9 1 3 in for a week for bay 2 please. (Wed 25 Nov 16:20) | PROPOSE ALLOW 20913, until Wed 02 Dec 16:20 |
| check-089 | show me the permits (Fri 27 Nov 22:05) | UNSUPPORTED |
| check-090 | please let number 56077 in bay two until tomorrow (Wed 25 Nov 16:20) | PROPOSE ALLOW 56077, until Thu 26 Nov 23:59 |
| check-091 | Approve 39082 until later. (Wed 25 Nov 16:20) | NEEDS_REVIEW (unclear_time) |
| check-092 | how many cars are parked (Wed 25 Nov 16:20) | UNSUPPORTED |
| check-093 | hey approve car number 5351 for 6 days (Wed 25 Nov 16:20) | PROPOSE ALLOW 5351, until Tue 01 Dec 16:20 |
| check-094 | Remove car 9779. (Fri 27 Nov 22:05) | PROPOSE REMOVE 9779 |
| check-095 | please and number 1 3 8 (Sun 22 Nov 07:50) | NEEDS_REVIEW (unclear_action) |
| check-096 | Delete car number 8192. (Sun 22 Nov 07:50) | PROPOSE REMOVE 8192 |
| check-097 | allow number 3945 (Sun 22 Nov 07:50) | PROPOSE ALLOW 3945, permanent |
| check-098 | please allow car 7270 for forty five minutes (Wed 25 Nov 16:20) | PROPOSE ALLOW 7270, until Wed 25 Nov 17:05 |
| check-099 | okay approve number two thousand one hundred thirteen till seven pm bay 2 (Wed 25 Nov 16:20) | PROPOSE ALLOW 2113, until Wed 25 Nov 19:00 |
| check-100 | Car three five six in bay 2. (Sun 22 Nov 07:50) | NEEDS_REVIEW (unclear_action) |
| check-101 | add car number 17470 until tonight (Fri 27 Nov 22:05) | NEEDS_REVIEW (unclear_time) |
| check-102 | Approve 6 4 6 7 until one pm in bay two. (Sun 22 Nov 07:50) | PROPOSE ALLOW 6467, until Sun 22 Nov 13:00 |
| check-103 | Approve car number 8284 bay 1 till eight thirty p.m. (Wed 25 Nov 16:20) | PROPOSE ALLOW 8284, until Wed 25 Nov 20:30 |
| check-104 | let 36150 in until 12 (Fri 27 Nov 22:05) | NEEDS_REVIEW (ambiguous_time) |
| check-105 | Add plate 2632. (Sun 22 Nov 07:50) | PROPOSE ALLOW 2632, permanent |
| check-106 | let 193 in for one week in bay two please (Sun 22 Nov 07:50) | PROPOSE ALLOW 193, until Sun 29 Nov 07:50 |
| check-107 | 638 until tomorrow. (Fri 27 Nov 22:05) | NEEDS_REVIEW (unclear_action) |
| check-108 | extend the permit for car 7290 (Sun 22 Nov 07:50) | UNSUPPORTED |
| check-109 | Hey add car number seven until tomorrow. (Fri 27 Nov 22:05) | NEEDS_REVIEW (single_digit_number): ALLOW 7, until Sat 28 Nov 23:59 |
| check-110 | Okay add number 9493 until Friday bay two please. (Wed 25 Nov 16:20) | PROPOSE ALLOW 9493, until Fri 27 Nov 23:59 |
| check-111 | Hey and 5585 until tomorrow 9PM please. (Fri 27 Nov 22:05) | NEEDS_REVIEW (unclear_action) |
| check-112 | Approve plate nine zero zero. (Fri 27 Nov 22:05) | PROPOSE ALLOW 900, permanent |
| check-113 | Approve plate 2881 till eight a.m. (Wed 25 Nov 16:20) | NEEDS_REVIEW (time_in_past) |
| check-114 | Hey allow plate number 429 until tomorrow. (Fri 27 Nov 22:05) | PROPOSE ALLOW 429, until Sat 28 Nov 23:59 |
| check-115 | Okay add number 869 bay 1. (Sun 22 Nov 07:50) | PROPOSE ALLOW 869, permanent |
| check-116 | okay remove 2296 (Fri 27 Nov 22:05) | PROPOSE REMOVE 2296 |
| check-117 | allow plate 59838 bay two please (Sun 22 Nov 07:50) | PROPOSE ALLOW 59838, permanent |
| check-118 | Hey allow number 62463. (Fri 27 Nov 22:05) | PROPOSE ALLOW 62463, permanent |
| check-119 | Please approve car number 34393 till ten fifteen PM. (Fri 27 Nov 22:05) | PROPOSE ALLOW 34393, until Fri 27 Nov 22:15 |
| check-120 | Please approve car number 102 until tomorrow at one pm. (Wed 25 Nov 16:20) | PROPOSE ALLOW 102, until Thu 26 Nov 13:00 |
