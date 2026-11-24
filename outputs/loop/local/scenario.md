# Full-loop scenario (LOCAL ONLY: real plates)

Real photos and all three real models; the owner's answers are scripted (yes). Times are scenario times.

| time | input | system | right? |
|---|---|---|---|
| 08:00 | owner: "allow car 33044" | asks: Allow car 33044 in either bay permanently (no end time)? owner: yes. Done: Allow car 33044 in either bay permanently (no end time). | |
| 08:01 | owner: "please add 66705" | asks: Allow car 66705 in either bay permanently (no end time)? owner: yes. Done: Allow car 66705 in either bay permanently (no end time). | |
| 09:00 | camera IMG_1766 left bay | occupied, plate W48556 (READ) -> **POTENTIALLY_UNAUTHORIZED** | yes |
| 09:00 | camera IMG_1766 right bay | empty,  -> **EMPTY** | yes |
| 09:05 | owner: "let car 48556 in until 6 pm" | asks: Allow car 48556 in either bay until Sun 22 Nov 18:00? owner: yes. Done: Allow car 48556 in either bay until Sun 22 Nov 18:00. | |
| 09:10 | camera IMG_1766 left bay | occupied, plate W48556 (READ) -> **AUTHORIZED** | yes |
| 09:10 | camera IMG_1766 right bay | empty,  -> **EMPTY** | yes |
| 18:30 | camera IMG_1766 left bay | occupied, plate W48556 (READ) -> **POTENTIALLY_UNAUTHORIZED** | yes |
| 18:30 | camera IMG_1766 right bay | empty,  -> **EMPTY** | yes |
| 19:00 | owner: "allow plate number 48837 for 2 hours" | asks: Allow car 48837 in either bay until Sun 22 Nov 21:00? owner: yes. Done: Allow car 48837 in either bay until Sun 22 Nov 21:00. | |
| 19:30 | camera IMG_1771 left bay | empty,  -> **EMPTY** | yes |
| 19:30 | camera IMG_1771 right bay | occupied, plate O48837 (READ) -> **AUTHORIZED** | yes |
| 19:45 | owner: "remove car 48837" | asks: Remove the permit for car 48837 (both bays)? owner: yes. Done: Remove the permit for car 48837 (both bays). | |
| 19:50 | camera IMG_1771 left bay | empty,  -> **EMPTY** | yes |
| 19:50 | camera IMG_1771 right bay | occupied, plate O48837 (READ) -> **POTENTIALLY_UNAUTHORIZED** | yes |
| 21:00 | camera IMG_1820 left bay | occupied, plate O33044 (READ) -> **AUTHORIZED** | yes |
| 21:00 | camera IMG_1820 right bay | occupied, plate 66705 (NEEDS_REVIEW) -> **NEEDS_REVIEW** | no (AUTHORIZED) |
| 21:30 | camera IMG_1818 left bay | occupied, plate O33044 (READ) -> **AUTHORIZED** | yes |
| 21:30 | camera IMG_1818 right bay | empty,  -> **EMPTY** | yes |
| 22:00 | camera IMG_1601 left bay | occupied, plate 3269930 (NEEDS_REVIEW) -> **NEEDS_REVIEW** | no (POTENTIALLY_UNAUTHORIZED) |
| 22:00 | camera IMG_1601 right bay | occupied, plate 2710 (NEEDS_REVIEW) -> **NEEDS_REVIEW** | yes |
| 22:30 | camera IMG_1731 left bay | empty,  -> **EMPTY** | yes |
| 22:30 | camera IMG_1731 right bay | occupied, plate 88159 (NEEDS_REVIEW) -> **NEEDS_REVIEW** | no (EMPTY) |
