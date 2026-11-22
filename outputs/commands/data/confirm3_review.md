# Command set: confirm3 (120 commands)

| id | command (said at) | expected |
|---|---|---|
| confirm3-001 | Approve plate number 93851 until 18:00 please. (Sun 29 Nov 15:40) | PROPOSE ALLOW 93851, until Sun 29 Nov 18:00 |
| confirm3-002 | allow number four one five six until tomorrow morning (Wed 25 Nov 09:05) | NEEDS_REVIEW (unclear_time) |
| confirm3-003 | Car 24559 in bay 2. (Sun 29 Nov 15:40) | NEEDS_REVIEW (unclear_action) |
| confirm3-004 | Let car one hundred forty six in. (Fri 04 Dec 20:25) | PROPOSE ALLOW 146, permanent |
| confirm3-005 | approve number 3993 till 1 (Wed 25 Nov 09:05) | NEEDS_REVIEW (ambiguous_time) |
| confirm3-006 | okay allow plate 90138 (Wed 25 Nov 09:05) | PROPOSE ALLOW 90138, permanent |
| confirm3-007 | Add 45 for a while. (Sun 29 Nov 15:40) | NEEDS_REVIEW (unclear_time) |
| confirm3-008 | take plate 6183 off the list (Wed 25 Nov 09:05) | PROPOSE REMOVE 6183 |
| confirm3-009 | Extend the permit for car 5027. (Wed 25 Nov 09:05) | UNSUPPORTED |
| confirm3-010 | Allow car 9742 for today please. (Wed 25 Nov 09:05) | PROPOSE ALLOW 9742, until Wed 25 Nov 23:59 |
| confirm3-011 | add car six five five three two and car 6 9 6 5 until tomorrow (Wed 25 Nov 09:05) | NEEDS_REVIEW (multiple_numbers) |
| confirm3-012 | Okay allow plate 912 until today bay two. (Sun 29 Nov 15:40) | PROPOSE ALLOW 912, until Sun 29 Nov 23:59 |
| confirm3-013 | Approve 8939 till 9 am. (Fri 04 Dec 20:25) | NEEDS_REVIEW (time_in_past) |
| confirm3-014 | Allow car number 83104 for a week. (Wed 25 Nov 09:05) | PROPOSE ALLOW 83104, until Wed 02 Dec 09:05 |
| confirm3-015 | take plate 89382 off the list (Fri 04 Dec 20:25) | PROPOSE REMOVE 89382 |
| confirm3-016 | okay approve number fifty three thousand eighty two (Wed 25 Nov 09:05) | PROPOSE ALLOW 53082, permanent |
| confirm3-017 | Add plate number ninety four thousand five hundred sixty. (Fri 04 Dec 20:25) | PROPOSE ALLOW 94560, permanent |
| confirm3-018 | Add plate 4777782 for 3 days. (Sun 29 Nov 15:40) | NEEDS_REVIEW (invalid_number) |
| confirm3-019 | add a car in bay 2 (Sun 29 Nov 15:40) | NEEDS_REVIEW (missing_number) |
| confirm3-020 | and 9376 for 30 minutes (Sun 29 Nov 15:40) | NEEDS_REVIEW (unclear_action) |
| confirm3-021 | Let car five three zero eight in till 2:30. (Sun 29 Nov 15:40) | NEEDS_REVIEW (ambiguous_time) |
| confirm3-022 | 1020 until tomorrow. (Sun 29 Nov 15:40) | NEEDS_REVIEW (unclear_action) |
| confirm3-023 | Add car 3875 and car 5 6 2 1 until tomorrow. (Sun 29 Nov 15:40) | NEEDS_REVIEW (multiple_numbers) |
| confirm3-024 | add plate number 934 until tonight (Fri 04 Dec 20:25) | NEEDS_REVIEW (unclear_time) |
| confirm3-025 | approve car 7068 (Sun 29 Nov 15:40) | PROPOSE ALLOW 7068, permanent |
| confirm3-026 | Remove 8 0 6 4. (Wed 25 Nov 09:05) | PROPOSE REMOVE 8064 |
| confirm3-027 | please allow car number 6915 for today (Wed 25 Nov 09:05) | PROPOSE ALLOW 6915, until Wed 25 Nov 23:59 |
| confirm3-028 | Hey take plate number 3129 off the list. (Wed 25 Nov 09:05) | PROPOSE REMOVE 3129 |
| confirm3-029 | allow number twelve thousand three hundred twelve until 8:30 AM (Sun 29 Nov 15:40) | NEEDS_REVIEW (time_in_past) |
| confirm3-030 | Hey allow car 8 until noon. (Wed 25 Nov 09:05) | NEEDS_REVIEW (single_digit_number): ALLOW 8, until Wed 25 Nov 12:00 |
| confirm3-031 | Allow car 58956 until seven fifteen pm. (Wed 25 Nov 09:05) | PROPOSE ALLOW 58956, until Wed 25 Nov 19:15 |
| confirm3-032 | okay allow plate number four seven oh eight four in bay 2 please (Fri 04 Dec 20:25) | PROPOSE ALLOW 47084, permanent |
| confirm3-033 | Let my friend in. (Sun 29 Nov 15:40) | NEEDS_REVIEW (missing_number) |
| confirm3-034 | and plate number 87013 please (Wed 25 Nov 09:05) | NEEDS_REVIEW (unclear_action) |
| confirm3-035 | let car four five oh one oh eight in (Sun 29 Nov 15:40) | NEEDS_REVIEW (invalid_number) |
| confirm3-036 | Add car number ninety nine sixty one for today bay 1 please. (Sun 29 Nov 15:40) | PROPOSE ALLOW 9961, until Sun 29 Nov 23:59 |
| confirm3-037 | please allow number 5 8 6 1 5 until tomorrow (Fri 04 Dec 20:25) | PROPOSE ALLOW 58615, until Sat 05 Dec 23:59 |
| confirm3-038 | Delete 1122 please. (Fri 04 Dec 20:25) | PROPOSE REMOVE 1122 |
| confirm3-039 | allow car forty thousand five hundred until later (Wed 25 Nov 09:05) | NEEDS_REVIEW (unclear_time) |
| confirm3-040 | Hey remove car seven six three five please. (Wed 25 Nov 09:05) | PROPOSE REMOVE 7635 |
| confirm3-041 | car number 82165 (Wed 25 Nov 09:05) | NEEDS_REVIEW (unclear_action) |
| confirm3-042 | Hey approve car number seven one eight four for five days please. (Sun 29 Nov 15:40) | PROPOSE ALLOW 7184, until Fri 04 Dec 15:40 |
| confirm3-043 | okay delete plate 8 3 1 3 (Fri 04 Dec 20:25) | PROPOSE REMOVE 8313 |
| confirm3-044 | Take number 818 off the list. (Fri 04 Dec 20:25) | PROPOSE REMOVE 818 |
| confirm3-045 | remove the car (Sun 29 Nov 15:40) | NEEDS_REVIEW (missing_number) |
| confirm3-046 | Please take number 75299 off the list. (Fri 04 Dec 20:25) | PROPOSE REMOVE 75299 |
| confirm3-047 | okay approve number 112 till tomorrow 8am (Wed 25 Nov 09:05) | PROPOSE ALLOW 112, until Thu 26 Nov 08:00 |
| confirm3-048 | take plate 41770 off the list (Fri 04 Dec 20:25) | PROPOSE REMOVE 41770 |
| confirm3-049 | Let plate number 65563 in until six am. (Wed 25 Nov 09:05) | NEEDS_REVIEW (time_in_past) |
| confirm3-050 | allow plate 9789 please (Sun 29 Nov 15:40) | PROPOSE ALLOW 9789, permanent |
| confirm3-051 | Let plate 4 in until 10:15 PM please. (Fri 04 Dec 20:25) | NEEDS_REVIEW (single_digit_number): ALLOW 4, until Fri 04 Dec 22:15 |
| confirm3-052 | Please add plate 2 4 9 4 6 for bay 2 until tomorrow at 12:15 pm. (Wed 25 Nov 09:05) | PROPOSE ALLOW 24946, until Thu 26 Nov 12:15 |
| confirm3-053 | Let number 89960 in bay one. (Fri 04 Dec 20:25) | PROPOSE ALLOW 89960, permanent |
| confirm3-054 | okay let car 71664 in until tomorrow (Sun 29 Nov 15:40) | PROPOSE ALLOW 71664, until Mon 30 Nov 23:59 |
| confirm3-055 | please approve car thirty two sixty two (Wed 25 Nov 09:05) | PROPOSE ALLOW 3262, permanent |
| confirm3-056 | let plate number 5 4 6 4 3 in until tomorrow please (Wed 25 Nov 09:05) | PROPOSE ALLOW 54643, until Thu 26 Nov 23:59 |
| confirm3-057 | Approve plate number 2130. (Wed 25 Nov 09:05) | PROPOSE ALLOW 2130, permanent |
| confirm3-058 | Okay add plate number 2 9 3 0 7. (Sun 29 Nov 15:40) | PROPOSE ALLOW 29307, permanent |
| confirm3-059 | Add car 3673 till five fifteen p.m. please. (Wed 25 Nov 09:05) | PROPOSE ALLOW 3673, until Wed 25 Nov 17:15 |
| confirm3-060 | Let car number three eight six seven in bay 1. (Wed 25 Nov 09:05) | PROPOSE ALLOW 3867, permanent |
| confirm3-061 | remove number six five five five eight from bay 2 (Fri 04 Dec 20:25) | PROPOSE REMOVE 65558 |
| confirm3-062 | Okay add number 21694. (Fri 04 Dec 20:25) | PROPOSE ALLOW 21694, permanent |
| confirm3-063 | Hey delete car number 1. (Wed 25 Nov 09:05) | NEEDS_REVIEW (single_digit_number): REMOVE 1 |
| confirm3-064 | Allow car number 5518 until tomorrow. (Wed 25 Nov 09:05) | PROPOSE ALLOW 5518, until Thu 26 Nov 23:59 |
| confirm3-065 | show me the permits (Sun 29 Nov 15:40) | UNSUPPORTED |
| confirm3-066 | please allow plate nine thousand one hundred fifteen bay 1 (Fri 04 Dec 20:25) | PROPOSE ALLOW 9115, permanent |
| confirm3-067 | allow 942 and three six three one two (Fri 04 Dec 20:25) | NEEDS_REVIEW (multiple_numbers) |
| confirm3-068 | allow car 90767 till eleven thirty p.m. for bay 2 (Sun 29 Nov 15:40) | PROPOSE ALLOW 90767, until Sun 29 Nov 23:30 |
| confirm3-069 | how many cars are parked (Sun 29 Nov 15:40) | UNSUPPORTED |
| confirm3-070 | allow number 941 bay two for a week (Fri 04 Dec 20:25) | PROPOSE ALLOW 941, until Fri 11 Dec 20:25 |
| confirm3-071 | Add 6 7 6 2 till seven AM. (Wed 25 Nov 09:05) | NEEDS_REVIEW (time_in_past) |
| confirm3-072 | Is car 8 4 8 8 2 allowed? (Fri 04 Dec 20:25) | UNSUPPORTED |
| confirm3-073 | Add 8736 until tomorrow at 5p.m. (Fri 04 Dec 20:25) | PROPOSE ALLOW 8736, until Sat 05 Dec 17:00 |
| confirm3-074 | Remove car number 8 3 1 2 please. (Fri 04 Dec 20:25) | PROPOSE REMOVE 8312 |
| confirm3-075 | please allow car 5 9 5 7 until tomorrow (Sun 29 Nov 15:40) | PROPOSE ALLOW 5957, until Mon 30 Nov 23:59 |
| confirm3-076 | allow car 5125 in bay 2 (Sun 29 Nov 15:40) | PROPOSE ALLOW 5125, permanent |
| confirm3-077 | Hey delete car 7694. (Sun 29 Nov 15:40) | PROPOSE REMOVE 7694 |
| confirm3-078 | approve car 4224091 (Wed 25 Nov 09:05) | NEEDS_REVIEW (invalid_number) |
| confirm3-079 | hey add plate number 1523 please (Wed 25 Nov 09:05) | PROPOSE ALLOW 1523, permanent |
| confirm3-080 | 4960 until tomorrow. (Wed 25 Nov 09:05) | NEEDS_REVIEW (unclear_action) |
| confirm3-081 | please allow car number 4 2 0 9 8 till Saturday (Fri 04 Dec 20:25) | PROPOSE ALLOW 42098, until Sat 05 Dec 23:59 |
| confirm3-082 | what's the weather today (Wed 25 Nov 09:05) | UNSUPPORTED |
| confirm3-083 | let car number 6 7 1 5 3 in (Sun 29 Nov 15:40) | PROPOSE ALLOW 67153, permanent |
| confirm3-084 | Add forty eight thousand one hundred fourteen. (Fri 04 Dec 20:25) | PROPOSE ALLOW 48114, permanent |
| confirm3-085 | Hey add car number four thousand two hundred sixteen. (Fri 04 Dec 20:25) | PROPOSE ALLOW 4216, permanent |
| confirm3-086 | hey allow car number 7 (Wed 25 Nov 09:05) | NEEDS_REVIEW (single_digit_number): ALLOW 7, permanent |
| confirm3-087 | Add six seven three five until tomorrow at 3. (Wed 25 Nov 09:05) | NEEDS_REVIEW (ambiguous_time) |
| confirm3-088 | allow plate number 93734 until tomorrow 5 p.m. in bay 1 (Fri 04 Dec 20:25) | PROPOSE ALLOW 93734, until Sat 05 Dec 17:00 |
| confirm3-089 | Take number one six five five off the list from bay 2. (Wed 25 Nov 09:05) | PROPOSE REMOVE 1655 |
| confirm3-090 | Approve plate 64828 until Wednesday. (Wed 25 Nov 09:05) | NEEDS_REVIEW (unclear_time) |
| confirm3-091 | allow number eight three five six till 12:30 (Fri 04 Dec 20:25) | NEEDS_REVIEW (ambiguous_time) |
| confirm3-092 | Hey allow plate number 446 for today please. (Fri 04 Dec 20:25) | PROPOSE ALLOW 446, until Fri 04 Dec 23:59 |
| confirm3-093 | allow number 93 until tomorrow (Sun 29 Nov 15:40) | PROPOSE ALLOW 93, until Mon 30 Nov 23:59 |
| confirm3-094 | Let plate four five eight two two in. (Sun 29 Nov 15:40) | PROPOSE ALLOW 45822, permanent |
| confirm3-095 | approve plate 7226 until midnight please (Wed 25 Nov 09:05) | PROPOSE ALLOW 7226, until Thu 26 Nov 00:00 |
| confirm3-096 | Allow 98916 and 90674. (Wed 25 Nov 09:05) | NEEDS_REVIEW (multiple_numbers) |
| confirm3-097 | Allow my brother's car. (Wed 25 Nov 09:05) | NEEDS_REVIEW (missing_number) |
| confirm3-098 | allow plate three four three nine five until tonight (Fri 04 Dec 20:25) | NEEDS_REVIEW (unclear_time) |
| confirm3-099 | delete 4679 from bay 2 (Fri 04 Dec 20:25) | PROPOSE REMOVE 4679 |
| confirm3-100 | Allow seven seven seven. (Wed 25 Nov 09:05) | PROPOSE ALLOW 777, permanent |
| confirm3-101 | Allow the car until 11PM tonight. (Fri 04 Dec 20:25) | NEEDS_REVIEW (missing_number) |
| confirm3-102 | Car number 2857. (Fri 04 Dec 20:25) | NEEDS_REVIEW (unclear_action) |
| confirm3-103 | Is car 3364 allowed? (Wed 25 Nov 09:05) | UNSUPPORTED |
| confirm3-104 | add plate number 84165 till tomorrow at 11 (Sun 29 Nov 15:40) | NEEDS_REVIEW (ambiguous_time) |
| confirm3-105 | Approve car number 337 until today. (Fri 04 Dec 20:25) | PROPOSE ALLOW 337, until Fri 04 Dec 23:59 |
| confirm3-106 | Car forty nine thousand three hundred fifty three in bay 2. (Fri 04 Dec 20:25) | NEEDS_REVIEW (unclear_action) |
| confirm3-107 | Approve number 47621 for five hours bay 1. (Wed 25 Nov 09:05) | PROPOSE ALLOW 47621, until Wed 25 Nov 14:05 |
| confirm3-108 | Let number seventy two thousand three hundred twelve in. (Fri 04 Dec 20:25) | PROPOSE ALLOW 72312, permanent |
| confirm3-109 | okay allow 85505 till 10 p.m. please (Sun 29 Nov 15:40) | PROPOSE ALLOW 85505, until Sun 29 Nov 22:00 |
| confirm3-110 | remove plate number three six nine two five (Wed 25 Nov 09:05) | PROPOSE REMOVE 36925 |
| confirm3-111 | Hello. (Wed 25 Nov 09:05) | UNSUPPORTED |
| confirm3-112 | Let plate number 72102 in until tomorrow at 6. (Wed 25 Nov 09:05) | NEEDS_REVIEW (ambiguous_time) |
| confirm3-113 | please allow 5286 for bay two until end of day (Fri 04 Dec 20:25) | PROPOSE ALLOW 5286, until Fri 04 Dec 23:59 |
| confirm3-114 | Allow the car. (Fri 04 Dec 20:25) | NEEDS_REVIEW (missing_number) |
| confirm3-115 | okay let number 6916 in till nine fifteen pm (Fri 04 Dec 20:25) | PROPOSE ALLOW 6916, until Fri 04 Dec 21:15 |
| confirm3-116 | approve car 1332 until 7pm (Sun 29 Nov 15:40) | PROPOSE ALLOW 1332, until Sun 29 Nov 19:00 |
| confirm3-117 | Add number 98321 until 7 AM today. (Wed 25 Nov 09:05) | NEEDS_REVIEW (time_in_past) |
| confirm3-118 | Is car 8969 allowed? (Fri 04 Dec 20:25) | UNSUPPORTED |
| confirm3-119 | add three three zero six nine until 8am today (Wed 25 Nov 09:05) | NEEDS_REVIEW (time_in_past) |
| confirm3-120 | Add 3569532 until 10:30 pm. (Fri 04 Dec 20:25) | NEEDS_REVIEW (invalid_number) |
