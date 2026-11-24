# Full loop: remove one part at a time (step 4)

51 local photos, 102 bays, 33 generated owner commands; the same truth for every row (from the owner's intended permits). Counts only. Small sample: indicative only.

| variant | bays | right | false alerts (alert on a car that is not unauthorized) | unauthorized cars |   alerted |   sent to a person |   missed (bay called empty) |   let through as AUTHORIZED | sent to a person (NEEDS_REVIEW) |   of which not needed |
|---|---|---|---|---|---|---|---|---|---|---|
| full system | 102 | 74 (73%) | 0 | 35 | 16 | 6 | 13 | 0 | 13 | 12 |
| no Model A (every bay occupied) | 102 | 36 (35%) | 0 | 35 | 27 | 8 | 0 | 0 | 67 | 66 |
| no Model B (no plate reading) | 102 | 50 (49%) | 0 | 35 | 0 | 22 | 13 | 0 | 37 | 36 |
| no Model C: rule parser, owner checks | 102 | 74 (73%) | 0 | 35 | 16 | 6 | 13 | 0 | 13 | 12 |
| no Model C: rule parser, no owner check | 102 | 74 (73%) | 0 | 35 | 16 | 6 | 13 | 0 | 13 | 12 |
| no Model C: no commands (empty table) | 102 | 66 (65%) | 8 | 35 | 16 | 6 | 13 | 0 | 13 | 12 |
| Model C, no owner check | 102 | 72 (71%) | 2 | 35 | 16 | 6 | 13 | 0 | 13 | 12 |
| no time check (permits never end) | 102 | 69 (68%) | 0 | 35 | 11 | 6 | 13 | 5 | 13 | 12 |

## Owner effort for the commands (of 33)

| command reader | accepted / fixed / asked |
|---|---|
| Model C (tiered) | 24 / 0 / 9 |
| rule parser | 33 / 0 / 0 |

`asked`: the system asked a question, so the owner had to say the command again. With the owner's check, both readers end with the right table; the difference is the owner's effort and, without the check, wrong permits.

Caution: the commands are generated in the dev wording, the same wording the rule parser was written from, so this favours the rule parser. On the frozen test's new wording, the rule parser put 3 wrong changes to the owner against Model C's 1 (`outputs/commands/final_test.md`).
