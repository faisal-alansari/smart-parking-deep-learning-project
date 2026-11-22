# Model C: what was tried on dev (Step 5)

Dev set only (60 commands). The frozen test set was not opened. Every candidate fills the
same `Extraction`; the shared rules do the rest. Worked examples and class examples were
written by hand in the dev set's wording only (allow / add / let ... in / approve; remove /
delete / take ... off) and avoid the test set's unseen wording. Field checks below compare a
candidate's pieces with the dev answer pieces ("oracle"), out of 60.

## Shared decoding choice (SmolLM2, FLAN-T5)

| try | result | kept? |
|---|---|---|
| Free generation | Both models invent numbers ("441, 442, 443 ...") and copy the examples | no |
| Copy-only decoding: fixed answer shape, every value copied from the command | No invented values; on 3 of 4 spot-checked commands SmolLM2 gave the same answer as when free (the 4th was an invented number, now blocked) | yes |
| Copies may be any substring | FLAN copied part of a number ("62" from "626"), proposing the wrong car | no |
| Copies must be whole words; an answer that cannot finish counts as no answer | Part-numbers gone | yes |

## SmolLM2-135M-Instruct

| try | dev | kept? |
|---|---|---|
| One JSON answer (action, numbers, time), greedy | exact 0.367, dangerous 0.550; says ALLOW for nearly everything | no |
| Action scored inside the JSON prompt | action 45/60 | no |
| Action as its own question, no examples | action 26/60 | no |
| Action as its own question, 11 worked examples | action 51/60 | yes |
| Same, lower-cased | action 50/60 | no (no gain) |
| Numbers + time JSON, prefill ending in `[` | numbers 6/60: the model writes ` ["` as one token, so a fill ending mid-token broke it | no |
| Numbers + time JSON, prefill stops before ` ["` | numbers 50/60, time 42/60 | yes |
| Time as its own question | time 40/60 | no |
| 4 more worked examples with end times | time 27/60 (copies stray words) | no |
| **Final** (action question + numbers/time JSON) | **exact 0.583, dangerous 0.283** | |

## FLAN-T5-Small

| try | dev | kept? |
|---|---|---|
| Action: "allow, remove, other or unclear?" | action 5/60 (says "other") | no |
| Action: OPTIONS list "allow a car / remove a car / something else / unclear" | action 11/60 | yes (best, still poor) |
| Action: allow / remove / neither | 9/60 | no |
| Action: verbs listed in the question | 9/60 | no |
| Number: "What is the car plate number? Copy it, or answer none." | 22/60 | yes |
| Number: two other wordings | 20/60, 15/60 | no |
| Time: "Until when ...?" | 4/60 | no |
| Time: "Until what time or for how long? Answer none if no time is given." | 13/60 | yes |
| Time: "What is the end time ...?" | 11/60 | no |
| **Final** | **exact 0.167, dangerous 0.150** (often REMOVE for an allow command) | |

## GLiNER Small v2.1 + all-MiniLM-L6-v2

| try | dev | kept? |
|---|---|---|
| First version (nearest example, similarity cut-off 0.5; spans as found) | exact 0.300, dangerous 0.217 | no |
| MiniLM action: nearest single example | action 35/60 (confuses allow and remove) | no |
| MiniLM action: class descriptions only | 15–20/60 | no |
| MiniLM action: numbers masked | no gain | no |
| MiniLM action: average of 4–8 hand-written examples per action | action 53/60 | yes |
| GLiNER spans cut to the number words and grown to the whole spoken number | numbers 34 → 55/60 | yes |
| GLiNER label sets (5) × thresholds 0.2 / 0.3 / 0.4 | within ±2 of the default; inconclusive | kept default labels, 0.3 |
| **Final** | **exact 0.733, dangerous 0.100** | |

## Device

SmolLM2 on CPU spends most of its time reading its two long prompts: about 2.0 s per command,
against about 0.27 s on the Mac GPU (MPS), so `device: mps` is the default. Times for both are in
`candidates.md`.

## Reaching 0 dangerous on dev (selection rule fixed first, 2026-11-21)

Rule agreed with the owner before any test result: 0 dangerous on dev, then the highest exact
score; a slower model may win.

| try | dev | kept? |
|---|---|---|
| Each model's own confidence (decoding probability; MiniLM lead; GLiNER span scores) | Wrong and right answers overlap: 3 of GLiNER + MiniLM's 6 dangerous answers have a bigger action lead than most correct ones. A cut-off would block nearly every correct change | no |
| GLiNER + MiniLM answers; every change must be matched exactly by SmolLM2, else "unsure" | exact 36/60, dangerous 2 (both a dropped end time that both models missed) | yes |
| SmolLM2 checks the action and number only | exact 40/60, dangerous 1 ("930 until tomorrow" read as allow by both) | no: fails the rule |
| SmolLM2 checks the action only | exact 40/60, dangerous 1 | no: fails the rule |
| All three models must agree (adding FLAN-T5) | exact 6/60, dangerous 0 | no: far lower exact |
| Plus: an allow with no end time is "unsure" if GLiNER half-saw an end time (score ≥ cut-off, below 0.3) | cut-offs 0.2 / 0.1: 1 dangerous; 0.08 / 0.05 / 0.03: 0 dangerous, exact 36/60 | yes, 0.05 |

The cut-off 0.05 is one step stricter than the loosest one that gives 0 dangerous (0.08), as
planned, to leave a margin. **Final safe parser (`checked`): exact 0.600, dangerous 0.000;**
18 of 34 clear commands get a needless question, mostly because SmolLM2 misses end times.
Two cautions: "930 until tomorrow" is stopped only because the two models disagreed on the end
time (both read a command with no action word as allow), and 0 of 60 still allows a true
dangerous rate of up to about 5%.

## Improving the safe parser within 2 hours (2026-11-22, owner's request)

Goal: highest exact score with 0 dangerous. New command sets in dev wording (new numbers and
times): **check** (120), then **confirm**, **confirm2**, **confirm3**, **confirm4** (120 each),
each sealed until opened once. A confirm set that showed a failure became development data,
and the next one was sealed. Numbers below are exact / dangerous.

| try | dev (60) | check (120) | kept? |
|---|---|---|---|
| Starting point (`checked`, all fields) | 36 / 0 | 71 / 2 ("add plate ... in bay two" read as remove by both models) | – |
| MiniLM: allow and no-action examples with "bay two", "extend ..." as other (v2) | 39 / 0 | 70 / 0 | yes |
| Same, SmolLM2 checks action + number only | 44 / 0 | 74 / 0 | yes |
| Also change SmolLM2's examples (insert one, v1) | SmolLM2 alone 35 → 25 | – | no |
| Move "bay two" between SmolLM2's examples (v3) | 44 / 0 | 71 / 1 | no |
| Fixed form first (tier 1) | 47 / 0 | 77 / 0 | yes |
| Remove bay phrases before both models (v4) | 47 / 1 (a slip read as allow) | 82 / 0 | no |
| GLiNER cut-off 0.3 → 0.2 (v5) | 50 / 0 | 81 / 0 | yes |
| GLiNER cut-off 0.15 (v6) | 50 / 0 | 83 / 0 | no (gain within noise) |

**confirm (opened once): 87 / 2** — "8 5 7 8 5 until tomorrow" and the slip "Please and car
897 till tomorrow" read as allow by both models. GLiNER cannot point at verbs (tried 4 labels).
Added: a change needs a word close in meaning (MiniLM) to an action word. Cut-offs 0.40–0.65
all gave 0 dangerous on dev, check and confirm; 0.45 chosen (one step stricter than 0.40).

**confirm2 (opened once): 84 / 2** — the slip "okay and car number 342 for seven days" ("for"
scored 0.464, just above 0.45) and "is car five eight nine two allowed" read as allow. Changed:
the cut-off to the middle of the gap between the highest no-action word (0.536) and the lowest
action word (0.694), so 0.6; "is car 4410 allowed" added to MiniLM's other-request examples.

**confirm3 (opened once): 88 / 1** — "Add car 3875 and car 5 6 2 1 until tomorrow": both models
found only the first car. Added: every number in the command must be explained by a found span
(plate, time or bay), else "unsure". No loss in exact on any set.

**confirm4 (sealed until the design was final): 93 / 0 (77.5% exact).** Stopped improving.

Final design (`tiered`): dev 49 / 0, check 81 / 0, confirm 85 / 0, confirm2 84 / 0, confirm3
88 / 0, confirm4 93 / 0. These sets use dev wording only, so they overstate performance on new
wording; see `final_test.md`.
