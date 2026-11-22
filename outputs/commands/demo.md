# Model C demo: owner commands and the permit table

Made-up plate Dubai G12345; the owner's answers are scripted.

| step | owner / camera | system |
|---|---|---|
| 1 | camera 09:30 | car in bay 1, plate G12345 -> **POTENTIALLY_UNAUTHORIZED** |
| 2 | owner says | "allow car 12345 until 6 pm" |
| 3 | system asks | Allow car 12345 in either bay until Sun 22 Nov 18:00? |
| 4 | system | Done: Allow car 12345 in either bay until Sun 22 Nov 18:00. |
| 5 | camera 09:35 | car in bay 1, plate G12345 -> **AUTHORIZED** |
| 6 | camera 18:30 | car in bay 1, plate G12345 -> **POTENTIALLY_UNAUTHORIZED** |
| 7 | owner says | "please let car number 12345 in until tomorrow" |
| 8 | system | I am not sure I understood. Please say it again, for example: allow car 12345 until 6 PM. |
| 9 | owner says | "okay let car 12345 in till 9 pm" |
| 10 | system asks | Allow car 12345 in either bay until Sun 22 Nov 21:00? |
| 11 | system | Done: Allow car 12345 in either bay until Sun 22 Nov 21:00. |
| 12 | camera 18:40 | car in bay 1, plate G12345 -> **AUTHORIZED** |
| 13 | owner says | "remove car 12345" |
| 14 | system asks | Remove the permit for car 12345 (both bays)? |
| 15 | system | Done: Remove the permit for car 12345 (both bays). |
| 16 | camera 19:05 | car in bay 1, plate G12345 -> **POTENTIALLY_UNAUTHORIZED** |
| 17 | owner says | "add car 1234 till tomorrow" |
| 18 | system asks | Allow car 1234 in either bay until Mon 23 Nov 23:59? |
| 19 | owner | No: the number is 12345 |
| 20 | system | Done: Allow car 12345 in either bay until Mon 23 Nov 23:59. |
| 21 | camera 19:15 | car in bay 1, plate unclear -> **NEEDS_REVIEW** |
| 22 | owner says | "add 12345 until 6" |
| 23 | system | Is that AM or PM? |
| 24 | owner says | "what's the weather today" |
| 25 | system | Do you want to allow or remove a car? |

Feedback records saved: 4 (`outputs/commands/feedback_demo.jsonl`).
