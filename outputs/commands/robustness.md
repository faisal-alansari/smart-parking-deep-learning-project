# Model C robustness (5 increasing levels)

Built from 40 fresh clear commands in dev wording (never the frozen test set). The expected
answer of every changed command is built from its meaning, as in `dataset`:

| parser | level | n | exact | dangerous | changes proposed |
|---|---|---|---|---|---|
| rules | 1. typos and odd casing | 40 | 0.90 | 0 | 36 |
| rules | 2. missing pieces | 40 | 1.00 | 0 | 0 |
| rules | 3. ambiguous | 40 | 0.78 | 0 | 0 |
| rules | 4. off-topic | 10 | 0.30 | 0 | 0 |
| rules | 5. tricks | 10 | - | 1 | 0 |
|  | dangerous: "approve plate minus five" -> NEEDS_REVIEW (single_digit_number): ALLOW 5, permanent |  |  |  |  |
| gliner-minilm | 1. typos and odd casing | 40 | 0.85 | 5 | 38 |
| gliner-minilm | 2. missing pieces | 40 | 0.93 | 2 | 1 |
| gliner-minilm | 3. ambiguous | 40 | 0.62 | 10 | 10 |
| gliner-minilm | 4. off-topic | 10 | 0.30 | 0 | 0 |
| gliner-minilm | 5. tricks | 10 | - | 1 | 0 |
|  | dangerous: "approve plate 4111 until 7" -> PROPOSE ALLOW 4111, permanent |  |  |  |  |
|  | dangerous: "APPROVE CAR 12 BAY ONE PELASE" -> NEEDS_REVIEW (single_digit_number): ALLOW 1, permanent |  |  |  |  |
|  | dangerous: "approve car bay one please" -> NEEDS_REVIEW (single_digit_number): ALLOW 1, permanent |  |  |  |  |
|  | dangerous: "allow plate number 72 until 7" -> PROPOSE ALLOW 72, permanent |  |  |  |  |
|  | dangerous: "Please let plate 14396 in till 7pm. and car 4821" -> PROPOSE ALLOW 14396, until Thu 26 Nov 19:00 |  |  |  |  |
|  | dangerous: "let numebr 8754 in until tomorrow 7:15 pm." -> PROPOSE ALLOW 8754, until Sun 22 Nov 19:15 |  |  |  |  |
|  | dangerous: "approve car numebr nine six five two four for seven days" -> PROPOSE ALLOW 96524, permanent |  |  |  |  |
|  | dangerous: "Add number 36252 for 30 minutes in bay 2. and car 4821" -> PROPOSE ALLOW 36252, until Thu 26 Nov 18:40 |  |  |  |  |
|  | dangerous: "Approve Nine One Eight Nine Oh Till Tomorrow" -> PROPOSE ALLOW 91890, permanent |  |  |  |  |
|  | dangerous: "approve nine one eight nine oh until 7" -> PROPOSE ALLOW 91890, permanent |  |  |  |  |
|  | dangerous: "please number 4225" -> PROPOSE ALLOW 4225, permanent |  |  |  |  |
|  | dangerous: "PLESAE LET 1465 IN TILL 11:30 P.M." -> PROPOSE ALLOW 1465, permanent |  |  |  |  |
|  | dangerous: "Approve plate 648 in bay 2 until tomorrow 10:30 am please. and car 4821" -> PROPOSE ALLOW 648, until Fri 27 Nov 10:30 |  |  |  |  |
|  | dangerous: "Remove plate number 345 from bay 2 please. and car 4821" -> PROPOSE REMOVE 345 |  |  |  |  |
|  | dangerous: "okay take number 26515 off the list and car 4821" -> PROPOSE REMOVE 26515 |  |  |  |  |
|  | dangerous: "okay take plate number 163 off the list and car 4821" -> PROPOSE REMOVE 163 |  |  |  |  |
|  | dangerous: "Please take plate 9 2 4 9 4 off the list. and car 4821" -> PROPOSE REMOVE 92494 |  |  |  |  |
|  | dangerous: "approve plate minus five" -> NEEDS_REVIEW (single_digit_number): ALLOW 5, permanent |  |  |  |  |
| checked | 1. typos and odd casing | 40 | 0.42 | 1 | 18 |
| checked | 2. missing pieces | 40 | 0.95 | 0 | 0 |
| checked | 3. ambiguous | 40 | 0.62 | 0 | 0 |
| checked | 4. off-topic | 10 | 0.30 | 0 | 0 |
| checked | 5. tricks | 10 | - | 1 | 0 |
|  | dangerous: "let numebr 8754 in until tomorrow 7:15 pm." -> PROPOSE ALLOW 8754, until Sun 22 Nov 19:15 |  |  |  |  |
|  | dangerous: "approve plate minus five" -> NEEDS_REVIEW (single_digit_number): ALLOW 5, permanent |  |  |  |  |
| tiered | 1. typos and odd casing | 40 | 0.42 | 1 | 18 |
| tiered | 2. missing pieces | 40 | 0.95 | 0 | 0 |
| tiered | 3. ambiguous | 40 | 0.65 | 0 | 0 |
| tiered | 4. off-topic | 10 | 0.30 | 0 | 0 |
| tiered | 5. tricks | 10 | - | 1 | 0 |
|  | dangerous: "let numebr 8754 in until tomorrow 7:15 pm." -> PROPOSE ALLOW 8754, until Sun 22 Nov 19:15 |  |  |  |  |
|  | dangerous: "approve plate minus five" -> NEEDS_REVIEW (single_digit_number): ALLOW 5, permanent |  |  |  |  |
