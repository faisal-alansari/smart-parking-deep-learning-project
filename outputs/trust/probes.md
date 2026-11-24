# Explainability probes

Model A (bay crops of the other night, test; the adapted model against the public-only one):
- A1 where it looks: grey out the top, middle or bottom third of crops holding a car;
- A2 glare: add a headlight-like glow to empty bays;
- A3 half a car: grey out the left or right half of crops holding a car.
Model B (public plate test images with a clear, correct read):
- B1 cover the last character of the plate;
- B2 cover the left quarter of the plate (the emirate and code side).
Model C (minimal pairs of owner commands, made-up numbers).
System: the same parked car with and without a permit, and with a changed plate read.

## Model A

Hypotheses: A1, the model looks at the car itself (middle and bottom: body, bumper, plate) rather than the row of cars behind (top); A2, headlight glare on an empty bay looks like a car to the public-only model but not to the adapted one; A3, the adapted model needs most of a car, which would explain the bay holding half of a car standing across both bays.

| probe | model | input | called occupied |
|---|---|---|---|
| A1 where it looks | adapted (product) | cars, unchanged | 100% |
| A1 where it looks | adapted (product) | cars, top third greyed | 100% |
| A1 where it looks | adapted (product) | cars, middle third greyed | 100% |
| A1 where it looks | adapted (product) | cars, bottom third greyed | 10% |
| A2 glare | adapted (product) | empty bays, unchanged | 1% |
| A2 glare | adapted (product) | empty bays, glare 0.3 | 2% |
| A2 glare | adapted (product) | empty bays, glare 0.6 | 16% |
| A2 glare | adapted (product) | empty bays, glare 0.9 | 89% |
| A3 half a car | adapted (product) | cars, left half greyed | 100% |
| A3 half a car | adapted (product) | cars, right half greyed | 100% |
| A1 where it looks | public only | cars, unchanged | 100% |
| A1 where it looks | public only | cars, top third greyed | 100% |
| A1 where it looks | public only | cars, middle third greyed | 100% |
| A1 where it looks | public only | cars, bottom third greyed | 60% |
| A2 glare | public only | empty bays, unchanged | 30% |
| A2 glare | public only | empty bays, glare 0.3 | 31% |
| A2 glare | public only | empty bays, glare 0.6 | 63% |
| A2 glare | public only | empty bays, glare 0.9 | 100% |
| A3 half a car | public only | cars, left half greyed | 100% |
| A3 half a car | public only | cars, right half greyed | 100% |

## Model B

Hypotheses: B1, with its last character hidden the reader should ask a person (too few characters), not read a different number; B2, with the emirate and code side hidden it should ask (no emirate, or a Dubai plate without its code).

| probe | plates | still right | asks a person | silent misread | plate lost |
|---|---|---|---|---|---|
| B1 last character covered | 300 | 40% | 2% | 58% | 0% |
| B2 left quarter covered | 300 | 4% | 46% | 50% | 0% |

## Model C

| probe | command | Model C |
|---|---|---|
| C1 the verb decides the action | allow car 52817 until 6 pm | ALLOW 52817 until Wed 18:00 |
| C1 the verb decides the action | remove car 52817 | REMOVE 52817 |
| C2 negation | remove car 52817 | REMOVE 52817 |
| C2 negation | don't allow car 52817 anymore | unsupported |
| C3 spoken digits = written digits | allow car 52817 until tomorrow | ALLOW 52817 until Thu 23:59 |
| C3 spoken digits = written digits | allow car five two eight one seven until tomorrow | ALLOW 52817 until Thu 23:59 |
| C4 a bay number is ignored | allow car 52817 until 6 pm | ALLOW 52817 until Wed 18:00 |
| C4 a bay number is ignored | allow car 52817 in bay 2 until 6 pm | ALLOW 52817 until Wed 18:00 |
| C5 AM/PM is never guessed | allow car 52817 until 6 pm | ALLOW 52817 until Wed 18:00 |
| C5 AM/PM is never guessed | allow car 52817 until 6 | asks: ambiguous_time |
| C6 a dropped day is asked about | allow car 52817 until tomorrow 9:30 pm | ALLOW 52817 until Thu 21:30 |
| C6 a dropped day is asked about | allow car 52817 until tomorrow nine thirty p.m. | asks: unsure |
| C7 no action word, no change | add car 52817 till tomorrow | ALLOW 52817 until Thu 23:59 |
| C7 no action word, no change | and car 52817 till tomorrow | unsupported |

## System: does the decision really use the text and the table?

| S1 the same car, one thing changed | status |
|---|---|
| occupied, plate G52817, no permit | POTENTIALLY_UNAUTHORIZED |
| same, with a permit until 23:00 | AUTHORIZED |
| same permit, plate read as G52617 | POTENTIALLY_UNAUTHORIZED |
| same permit, plate unclear | NEEDS_REVIEW |
| same permit, bay called empty | EMPTY |
