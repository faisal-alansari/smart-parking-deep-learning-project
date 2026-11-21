# Command set: test (160 commands)

| id | command (said at) | expected |
|---|---|---|
| test-001 | Whitelist number 64278 for some time. (Wed 02 Dec 14:40) | NEEDS_REVIEW (unclear_time) |
| test-002 | let the delivery guy in until tomorrow (Wed 02 Dec 14:40) | NEEDS_REVIEW (missing_number) |
| test-003 | please let car number 27677 in (Sun 29 Nov 21:10) | PROPOSE ALLOW 27677, permanent |
| test-004 | can you allow number 1 please (Thu 26 Nov 08:15) | NEEDS_REVIEW (single_digit_number): ALLOW 1, permanent |
| test-005 | Could you allow number one oh six in bay 2 until tomorrow. (Thu 26 Nov 08:15) | PROPOSE ALLOW 106, until Fri 27 Nov 23:59 |
| test-006 | Give access to the white car. (Sun 29 Nov 21:10) | NEEDS_REVIEW (missing_number) |
| test-007 | Let car six six one seven in. (Thu 26 Nov 08:15) | PROPOSE ALLOW 6617, permanent |
| test-008 | could you allow vehicle 73569 bay 3 (Wed 02 Dec 14:40) | PROPOSE ALLOW 73569, permanent |
| test-009 | Hey let number three eight four three in. (Sun 29 Nov 21:10) | PROPOSE ALLOW 3843, permanent |
| test-010 | and car number 94842 (Sun 29 Nov 21:10) | NEEDS_REVIEW (unclear_action) |
| test-011 | grant access to the car 69488 parking number two till tomorrow 12p.m. thanks (Thu 26 Nov 08:15) | PROPOSE ALLOW 69488, until Fri 27 Nov 12:00 |
| test-012 | remove number 1 from bay 1 (Wed 02 Dec 14:40) | NEEDS_REVIEW (single_digit_number): REMOVE 1 |
| test-013 | add plate 3296 until midnight thanks (Thu 26 Nov 08:15) | PROPOSE ALLOW 3296, until Fri 27 Nov 00:00 |
| test-014 | Allow cars 7 8 4 5 7 and four two eight. (Thu 26 Nov 08:15) | NEEDS_REVIEW (multiple_numbers) |
| test-015 | revoke 1 from bay 2 thanks (Wed 02 Dec 14:40) | NEEDS_REVIEW (single_digit_number): REMOVE 1 |
| test-016 | Give number 41830 access till nine. (Thu 26 Nov 08:15) | NEEDS_REVIEW (ambiguous_time) |
| test-017 | remove that car (Wed 02 Dec 14:40) | NEEDS_REVIEW (missing_number) |
| test-018 | Allow the car 441 please. (Sun 29 Nov 21:10) | PROPOSE ALLOW 441, permanent |
| test-019 | Allow plate number 245 for bay 1 thank you. (Sun 29 Nov 21:10) | PROPOSE ALLOW 245, permanent |
| test-020 | 7930 can park till tomorrow parking number 2 (Wed 02 Dec 14:40) | PROPOSE ALLOW 7930, until Thu 03 Dec 23:59 |
| test-021 | Um grant access to plate number fifty seven thousand seven hundred forty three. (Wed 02 Dec 14:40) | PROPOSE ALLOW 57743, permanent |
| test-022 | Take nine hundred five off the list please. (Sun 29 Nov 21:10) | PROPOSE REMOVE 905 |
| test-023 | allow the car in bay 2 for today (Wed 02 Dec 14:40) | NEEDS_REVIEW (missing_number) |
| test-024 | delete the visitor (Wed 02 Dec 14:40) | NEEDS_REVIEW (missing_number) |
| test-025 | list all permits (Sun 29 Nov 21:10) | UNSUPPORTED |
| test-026 | delete car number 243 please (Sun 29 Nov 21:10) | PROPOSE REMOVE 243 |
| test-027 | could you take vehicle forty eight thousand six hundred thirteen off the list thank you (Thu 26 Nov 08:15) | PROPOSE REMOVE 48613 |
| test-028 | Whitelist 822 until 3:30. (Wed 02 Dec 14:40) | NEEDS_REVIEW (ambiguous_time) |
| test-029 | let 48635 in until 7:30 pm tonight thanks (Wed 02 Dec 14:40) | PROPOSE ALLOW 48635, until Wed 02 Dec 19:30 |
| test-030 | car 187271 can park (Sun 29 Nov 21:10) | NEEDS_REVIEW (invalid_number) |
| test-031 | Hey allow car number seven four seven four until 7:15 pm tonight bay one. (Wed 02 Dec 14:40) | PROPOSE ALLOW 7474, until Wed 02 Dec 19:15 |
| test-032 | Permit number 1531 till 6 am. (Wed 02 Dec 14:40) | NEEDS_REVIEW (time_in_past) |
| test-033 | okay approve vehicle 6 till Saturday bay one thank you (Sun 29 Nov 21:10) | NEEDS_REVIEW (single_digit_number): ALLOW 6, until Sat 05 Dec 23:59 |
| test-034 | Add car number 726 for bay two until tomorrow. (Wed 02 Dec 14:40) | PROPOSE ALLOW 726, until Thu 03 Dec 23:59 |
| test-035 | Allow car number 8277 until next Monday. (Wed 02 Dec 14:40) | NEEDS_REVIEW (unclear_time) |
| test-036 | Give plate number 277 access please. (Thu 26 Nov 08:15) | PROPOSE ALLOW 277, permanent |
| test-037 | Number fifty nine for two hours. (Thu 26 Nov 08:15) | NEEDS_REVIEW (unclear_action) |
| test-038 | grant access to plate 39461 until tonight (Sun 29 Nov 21:10) | NEEDS_REVIEW (unclear_time) |
| test-039 | Approve 4942 thanks. (Sun 29 Nov 21:10) | PROPOSE ALLOW 4942, permanent |
| test-040 | can you aloud car 390 bay three until 9:15 AM thank you (Thu 26 Nov 08:15) | NEEDS_REVIEW (unclear_action) |
| test-041 | Could you add plate number six eight six seven seven. (Wed 02 Dec 14:40) | PROPOSE ALLOW 68677, permanent |
| test-042 | let plate number 63217 in until ten pm (Sun 29 Nov 21:10) | PROPOSE ALLOW 63217, until Sun 29 Nov 22:00 |
| test-043 | Allow car number 6744 for bay 2 till 9 p.m. tonight thank you. (Wed 02 Dec 14:40) | PROPOSE ALLOW 6744, until Wed 02 Dec 21:00 |
| test-044 | Okay delete vehicle seven eight two one. (Wed 02 Dec 14:40) | PROPOSE REMOVE 7821 |
| test-045 | delete car 3 2 3 please (Wed 02 Dec 14:40) | PROPOSE REMOVE 323 |
| test-046 | Grant access to eight hundred seven until 1:30. (Thu 26 Nov 08:15) | NEEDS_REVIEW (ambiguous_time) |
| test-047 | Allow the car four thousand five hundred forty seven please. (Thu 26 Nov 08:15) | PROPOSE ALLOW 4547, permanent |
| test-048 | Check car 39. (Wed 02 Dec 14:40) | UNSUPPORTED |
| test-049 | Good morning. (Thu 26 Nov 08:15) | UNSUPPORTED |
| test-050 | add car 9 5 5 9 9 till seven fifteen PM (Wed 02 Dec 14:40) | PROPOSE ALLOW 95599, until Wed 02 Dec 19:15 |
| test-051 | 13495 please (Thu 26 Nov 08:15) | NEEDS_REVIEW (unclear_action) |
| test-052 | add car 34434 until six thirty am today (Thu 26 Nov 08:15) | NEEDS_REVIEW (time_in_past) |
| test-053 | don't allow number 294 anymore (Wed 02 Dec 14:40) | PROPOSE REMOVE 294 |
| test-054 | allow number 6 5 till nine p.m. (Wed 02 Dec 14:40) | PROPOSE ALLOW 65, until Wed 02 Dec 21:00 |
| test-055 | um take number 421 off the list thank you (Wed 02 Dec 14:40) | PROPOSE REMOVE 421 |
| test-056 | Plate 9 6 5 1 3 9 can park until 3 PM. (Wed 02 Dec 14:40) | NEEDS_REVIEW (invalid_number) |
| test-057 | Remove three three seven three and nine thousand thirty one. (Wed 02 Dec 14:40) | NEEDS_REVIEW (multiple_numbers) |
| test-058 | Don't allow car two eight anymore thank you. (Sun 29 Nov 21:10) | PROPOSE REMOVE 28 |
| test-059 | Is eight thousand thirty seven still allowed? (Thu 26 Nov 08:15) | UNSUPPORTED |
| test-060 | Add my cousin's car in bay 1. (Thu 26 Nov 08:15) | NEEDS_REVIEW (missing_number) |
| test-061 | um grant access to seven one one six five until today (Sun 29 Nov 21:10) | PROPOSE ALLOW 71165, until Sun 29 Nov 23:59 |
| test-062 | Could you add plate number 16717. (Sun 29 Nov 21:10) | PROPOSE ALLOW 16717, permanent |
| test-063 | Approve car number seven eight seven four six thank you. (Sun 29 Nov 21:10) | PROPOSE ALLOW 78746, permanent |
| test-064 | What time is it? (Wed 02 Dec 14:40) | UNSUPPORTED |
| test-065 | could you cancel car number 69831 (Thu 26 Nov 08:15) | PROPOSE REMOVE 69831 |
| test-066 | remove plate 3663 thanks (Wed 02 Dec 14:40) | PROPOSE REMOVE 3663 |
| test-067 | Hey approve number 973 until tomorrow for bay three. (Thu 26 Nov 08:15) | PROPOSE ALLOW 973, until Fri 27 Nov 23:59 |
| test-068 | please approve number 2460 for two hours for bay 2 (Thu 26 Nov 08:15) | PROPOSE ALLOW 2460, until Thu 26 Nov 10:15 |
| test-069 | hey add number 95043 until 12p.m. tomorrow thank you (Thu 26 Nov 08:15) | PROPOSE ALLOW 95043, until Fri 27 Nov 12:00 |
| test-070 | Approve plate number 37376 till 8p.m. tomorrow thank you. (Thu 26 Nov 08:15) | PROPOSE ALLOW 37376, until Fri 27 Nov 20:00 |
| test-071 | Permit plate number 35212 until 11:15 AM. (Thu 26 Nov 08:15) | PROPOSE ALLOW 35212, until Thu 26 Nov 11:15 |
| test-072 | six eight three oh seven can park until Monday thanks (Wed 02 Dec 14:40) | PROPOSE ALLOW 68307, until Mon 07 Dec 23:59 |
| test-073 | Don't allow three three eight eight one anymore. (Thu 26 Nov 08:15) | PROPOSE REMOVE 33881 |
| test-074 | add vehicle 8 2 0 8 for six days in bay three please (Wed 02 Dec 14:40) | PROPOSE ALLOW 8208, until Tue 08 Dec 14:40 |
| test-075 | add the car 9173 for a week for bay one (Wed 02 Dec 14:40) | PROPOSE ALLOW 9173, until Wed 09 Dec 14:40 |
| test-076 | Add plate number 574763. (Thu 26 Nov 08:15) | NEEDS_REVIEW (invalid_number) |
| test-077 | Block plate number 76141 from bay 2. (Thu 26 Nov 08:15) | PROPOSE REMOVE 76141 |
| test-078 | 3574 can park until tomorrow. (Thu 26 Nov 08:15) | PROPOSE ALLOW 3574, until Fri 27 Nov 23:59 |
| test-079 | approve plate 9725 until 6:30 a.m. (Thu 26 Nov 08:15) | NEEDS_REVIEW (time_in_past) |
| test-080 | remove car 7 (Sun 29 Nov 21:10) | NEEDS_REVIEW (single_digit_number): REMOVE 7 |
| test-081 | hey aloud vehicle 20 till tomorrow in bay two (Thu 26 Nov 08:15) | NEEDS_REVIEW (unclear_action) |
| test-082 | Give plate 9007 access. (Wed 02 Dec 14:40) | PROPOSE ALLOW 9007, permanent |
| test-083 | take seven nine eight three off the list from bay 1 (Thu 26 Nov 08:15) | PROPOSE REMOVE 7983 |
| test-084 | Can you permit number 7. (Sun 29 Nov 21:10) | NEEDS_REVIEW (single_digit_number): ALLOW 7, permanent |
| test-085 | Please delete the car 6642 from bay 1. (Thu 26 Nov 08:15) | PROPOSE REMOVE 6642 |
| test-086 | the car 9799 tomorrow (Wed 02 Dec 14:40) | NEEDS_REVIEW (unclear_action) |
| test-087 | approve plate number 7 1 9 3 1 thank you (Wed 02 Dec 14:40) | PROPOSE ALLOW 71931, permanent |
| test-088 | please approve car number 4 4 8 for three days (Thu 26 Nov 08:15) | PROPOSE ALLOW 448, until Sun 29 Nov 08:15 |
| test-089 | please remove car number 59830 from bay 2 thanks (Thu 26 Nov 08:15) | PROPOSE REMOVE 59830 |
| test-090 | um allow plate number 9 3 8 in bay one until 4 p.m. thank you (Thu 26 Nov 08:15) | PROPOSE ALLOW 938, until Thu 26 Nov 16:00 |
| test-091 | Add car 7 2 1 for 2 days thanks. (Thu 26 Nov 08:15) | PROPOSE ALLOW 721, until Sat 28 Nov 08:15 |
| test-092 | let 6 3 3 4 and 8 6 2 4 in (Wed 02 Dec 14:40) | NEEDS_REVIEW (multiple_numbers) |
| test-093 | give 35087 access until end of day (Sun 29 Nov 21:10) | PROPOSE ALLOW 35087, until Sun 29 Nov 23:59 |
| test-094 | Cancel car 83438. (Sun 29 Nov 21:10) | PROPOSE REMOVE 83438 |
| test-095 | um give car 8 7 3 access in slot 2 thank you (Sun 29 Nov 21:10) | PROPOSE ALLOW 873, permanent |
| test-096 | Allow car 9757 until six pm. (Wed 02 Dec 14:40) | PROPOSE ALLOW 9757, until Wed 02 Dec 18:00 |
| test-097 | Edit car 15744. (Thu 26 Nov 08:15) | UNSUPPORTED |
| test-098 | hey let vehicle 8 4 8 7 in till tomorrow please (Sun 29 Nov 21:10) | PROPOSE ALLOW 8487, until Mon 30 Nov 23:59 |
| test-099 | approve car number 42281 until 1:30 (Thu 26 Nov 08:15) | NEEDS_REVIEW (ambiguous_time) |
| test-100 | allow number 35017 till 7 a.m. (Wed 02 Dec 14:40) | NEEDS_REVIEW (time_in_past) |
| test-101 | Car 3452 can park until he leaves. (Wed 02 Dec 14:40) | NEEDS_REVIEW (unclear_time) |
| test-102 | Add plate 85144 for forty five minutes for bay one. (Sun 29 Nov 21:10) | PROPOSE ALLOW 85144, until Sun 29 Nov 21:55 |
| test-103 | Whitelist plate four two seven five five for one week. (Sun 29 Nov 21:10) | PROPOSE ALLOW 42755, until Sun 06 Dec 21:10 |
| test-104 | can you take vehicle sixty two off the list thanks (Thu 26 Nov 08:15) | PROPOSE REMOVE 62 |
| test-105 | hey give number 4 0 3 access please (Wed 02 Dec 14:40) | PROPOSE ALLOW 403, permanent |
| test-106 | Approve plate number 5579677. (Sun 29 Nov 21:10) | NEEDS_REVIEW (invalid_number) |
| test-107 | approve the car 51 until 5 p.m. (Wed 02 Dec 14:40) | PROPOSE ALLOW 51, until Wed 02 Dec 17:00 |
| test-108 | Whitelist plate number three four seven eight two until next month. (Wed 02 Dec 14:40) | NEEDS_REVIEW (unclear_time) |
| test-109 | Okay give plate 955 access in parking 2 thank you. (Thu 26 Nov 08:15) | PROPOSE ALLOW 955, permanent |
| test-110 | Can you let number six one five zero six in for thirty minutes. (Wed 02 Dec 14:40) | PROPOSE ALLOW 61506, until Wed 02 Dec 15:10 |
| test-111 | Can you a loud plate 1 2 5 9 8 for bay 5 until end of day. (Thu 26 Nov 08:15) | NEEDS_REVIEW (unclear_action) |
| test-112 | Block the car five six from bay 2. (Thu 26 Nov 08:15) | PROPOSE REMOVE 56 |
| test-113 | Grant access to car 8006 spot two thank you. (Sun 29 Nov 21:10) | PROPOSE ALLOW 8006, permanent |
| test-114 | Give plate number 1522 access until tomorrow. (Thu 26 Nov 08:15) | PROPOSE ALLOW 1522, until Fri 27 Nov 23:59 |
| test-115 | Can you and the car seventy nine eighteen. (Wed 02 Dec 14:40) | NEEDS_REVIEW (unclear_action) |
| test-116 | Hey car 7754 can park till 5:30 pm in parking five. (Wed 02 Dec 14:40) | PROPOSE ALLOW 7754, until Wed 02 Dec 17:30 |
| test-117 | permit the guest (Wed 02 Dec 14:40) | NEEDS_REVIEW (missing_number) |
| test-118 | Please add plate number 7 1 9 3 for bay five thanks. (Thu 26 Nov 08:15) | PROPOSE ALLOW 7193, permanent |
| test-119 | Please permit plate number 4695 until tomorrow at 10:15 PM. (Wed 02 Dec 14:40) | PROPOSE ALLOW 4695, until Thu 03 Dec 22:15 |
| test-120 | permit plate 96906 till 10a.m. (Sun 29 Nov 21:10) | NEEDS_REVIEW (time_in_past) |
| test-121 | Could you aloud number 16182 until tomorrow. (Thu 26 Nov 08:15) | NEEDS_REVIEW (unclear_action) |
| test-122 | Remove car 4655 from bay 1 thank you. (Sun 29 Nov 21:10) | PROPOSE REMOVE 4655 |
| test-123 | Please allow number 80 in bay 3 thank you. (Thu 26 Nov 08:15) | PROPOSE ALLOW 80, permanent |
| test-124 | car 71734 in bay 1 (Thu 26 Nov 08:15) | NEEDS_REVIEW (unclear_action) |
| test-125 | Permit car eighty three thousand seven hundred twenty eight until Wednesday. (Wed 02 Dec 14:40) | NEEDS_REVIEW (unclear_time) |
| test-126 | Take car three four two one eight off the list. (Sun 29 Nov 21:10) | PROPOSE REMOVE 34218 |
| test-127 | Can you allow plate number 39429 in bay 2. (Wed 02 Dec 14:40) | PROPOSE ALLOW 39429, permanent |
| test-128 | Could you allow 7464 till Monday. (Wed 02 Dec 14:40) | PROPOSE ALLOW 7464, until Mon 07 Dec 23:59 |
| test-129 | approve 4845 in bay two please (Sun 29 Nov 21:10) | PROPOSE ALLOW 4845, permanent |
| test-130 | Remove six four one six four and 5380. (Wed 02 Dec 14:40) | NEEDS_REVIEW (multiple_numbers) |
| test-131 | approve 7525911 until eleven fifteen a.m. (Thu 26 Nov 08:15) | NEEDS_REVIEW (invalid_number) |
| test-132 | give plate 28424 access until tomorrow at eight am spot 2 thanks (Sun 29 Nov 21:10) | PROPOSE ALLOW 28424, until Mon 30 Nov 08:00 |
| test-133 | delete number 3 4 4 7 8 (Thu 26 Nov 08:15) | PROPOSE REMOVE 34478 |
| test-134 | please approve the car 58032 till 11 PM tonight (Wed 02 Dec 14:40) | PROPOSE ALLOW 58032, until Wed 02 Dec 23:00 |
| test-135 | Plate 66 till 8 pm. (Sun 29 Nov 21:10) | NEEDS_REVIEW (unclear_action) |
| test-136 | Can you grant access to plate 8860 thanks. (Thu 26 Nov 08:15) | PROPOSE ALLOW 8860, permanent |
| test-137 | um add plate number 7267 thank you (Wed 02 Dec 14:40) | PROPOSE ALLOW 7267, permanent |
| test-138 | um whitelist vehicle 23815 (Sun 29 Nov 21:10) | PROPOSE ALLOW 23815, permanent |
| test-139 | okay remove 3451 from bay 2 thank you (Thu 26 Nov 08:15) | PROPOSE REMOVE 3451 |
| test-140 | permit the guest till tomorrow (Wed 02 Dec 14:40) | NEEDS_REVIEW (missing_number) |
| test-141 | Could you revoke five four two six one from bay 1. (Sun 29 Nov 21:10) | PROPOSE REMOVE 54261 |
| test-142 | let number three four three in (Sun 29 Nov 21:10) | PROPOSE ALLOW 343, permanent |
| test-143 | Delete 3465. (Wed 02 Dec 14:40) | PROPOSE REMOVE 3465 |
| test-144 | Which bay is free? (Sun 29 Nov 21:10) | UNSUPPORTED |
| test-145 | permit number 79 until tomorrow afternoon (Sun 29 Nov 21:10) | NEEDS_REVIEW (unclear_time) |
| test-146 | Allow plate number eight hundred three until the weekend. (Wed 02 Dec 14:40) | NEEDS_REVIEW (unclear_time) |
| test-147 | Could you remove car number eighty four thousand two hundred forty four from bay 1 thank you. (Wed 02 Dec 14:40) | PROPOSE REMOVE 84244 |
| test-148 | Vehicle 796 in bay 2. (Wed 02 Dec 14:40) | NEEDS_REVIEW (unclear_action) |
| test-149 | change the time for four hundred fifty six (Thu 26 Nov 08:15) | UNSUPPORTED |
| test-150 | Could you grant access to vehicle 50874. (Wed 02 Dec 14:40) | PROPOSE ALLOW 50874, permanent |
| test-151 | okay approve the car 69582 until 10 pm tonight (Wed 02 Dec 14:40) | PROPOSE ALLOW 69582, until Wed 02 Dec 22:00 |
| test-152 | let plate five five one four in (Wed 02 Dec 14:40) | PROPOSE ALLOW 5514, permanent |
| test-153 | let seventy eight ninety eight and 36439 in (Wed 02 Dec 14:40) | NEEDS_REVIEW (multiple_numbers) |
| test-154 | allow cars 82205 and 6553 (Thu 26 Nov 08:15) | NEEDS_REVIEW (multiple_numbers) |
| test-155 | allow number 2 7 0 7 until 7 (Sun 29 Nov 21:10) | NEEDS_REVIEW (ambiguous_time) |
| test-156 | please permit the car four five two five oh (Sun 29 Nov 21:10) | PROPOSE ALLOW 45250, permanent |
| test-157 | who is parked in bay 1 (Thu 26 Nov 08:15) | UNSUPPORTED |
| test-158 | let 1 4 1 1 7 in thanks (Thu 26 Nov 08:15) | PROPOSE ALLOW 14117, permanent |
| test-159 | Let number eighty six thousand eight hundred thirty eight in thanks. (Thu 26 Nov 08:15) | PROPOSE ALLOW 86838, permanent |
| test-160 | Open the gate. (Thu 26 Nov 08:15) | UNSUPPORTED |
