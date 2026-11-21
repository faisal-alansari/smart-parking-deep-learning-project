# Findings: night car parks, 43 photos (2026-11-20)

Both models were trained on public data only. 43 owner photos at night, each showing a pair of bays in a public car park (several car parks): **86 bays, 46 empty, 40 occupied, 40 readable plates**. One shared pair of bay boxes for all photos, like a fixed camera set up once. Reproduce with `just local-night-1` (`results.md` and `probes.md` hold the numbers).

These photos were used only to check the system. Nothing was trained or tuned on them. The probes explain the same photos, so their gains are indicative and must be confirmed on a new photo set.

## Headline

| | Result |
|---|---|
| Occupancy correct | 60 of 86 (70%) |
| False alarms (empty bay called occupied) | 20 of 46 empty bays |
| Missed cars | 6 of 40 |
| Plates read exactly right (cars reaching the plate step) | 19 of 34 (20 after the reader fixes) |
| Full loop fully right | 45 of 86 (46 after the reader fixes) |
| Dangerous outputs (wrong plate given as a valid read) | 16 at first; 6 after the reader fixes |

This is much worse than the 8-photo pilot (15 of 16). The pilot's empty bays were mostly plain paving, while these car parks have features the public training data never shows.

## Occupancy: why it failed

1. **Background inside the box (main cause).** From a low, standing viewpoint, the upper part of each bay box shows the next row of cars, buildings and lamps. Cutting the top 30% of every box raised accuracy from 60 to 72 of 86 and cut false alarms from 20 to 11. Growing the box to include more background raised false alarms to 37. The public training crops come from high cameras looking down, so they never contain other rows of cars.
2. **Yellow concrete wheel stops in empty bays.** 8 of the 11 false alarms left after cutting the background contain a bright yellow wheel stop on dark brick paving. Across all empty bays, about 16 of 28 with a wheel stop were false alarms, against 4 of 18 without one. The public training bays are plain asphalt with no wheel stops, and a bright horizontal block on dark ground looks like the back of a car.
3. **Close-up cars missed.** In the later photos the owner stood closer. A white or light car under orange street light then fills the whole box as one smooth, bright surface. The model treats "smooth and plain" as empty ground, because training crops always show a whole car with ground around it.
4. **Not the cause:** overall brightness (false alarms and correct empty bays are equally bright, means 98 and 100), and neighbouring cars at the sides of the box (trimming the sides changed 1 bay).
5. **Seed disagreement is a weak warning only.** When the 3 CNN seeds disagree, the answer is right 13 of 21 times. When they agree, it is right 47 of 65 times, so unanimous answers are still often wrong.

## Plate reading: why it failed

1. **Small code letters on the newest two-row Dubai plates are lost.** The model sees them, but with low confidence (for example 0.15–0.39), and the 0.2 cut-off drops them. As a result, a doubled letter such as "GG" or "FF" becomes a single letter, the code letter can be dropped entirely, and a "B" becomes "P".
2. **"Z" read as "2"** when the code letter sits in the top corner of the newest Dubai design.
3. **A thin digit "1" counted several times.** Overlapping boxes for the same thin "1" are not merged, because they overlap too little for the current merge rule. The same pattern appeared in the public test set (for example a repeated last digit).
4. **The new white Sharjah plate goes to review (no emirate).** This plate style is missing from the training data; the outcome is safe, but gives no answer.
5. **A confidence rule would not help.** Misreads (confidence 0.26–0.89) and correct reads (0.25–0.91) overlap, because most misreads are a missing letter, and a missing letter cannot lower the confidence.
6. **Reading the whole photo fails** (0 of 34 right), as in the pilot. Reading from the bay area is the right design.

## What worked

- **Plate size separates parked cars from background cars, again.** Plates of cars in the bay were 13–29% of the bay width; plates seen through empty bays were 4–7% (pilot: 27–29% vs 4–9%).
- **The plate step already protects against most occupancy false alarms.** 17 of the 20 empty bays called occupied found no valid plate and went to review instead of a decision.
- **Common plates were read well.** All 19 correct reads were Dubai plates, read at night under orange light.

## Reader fixes applied (2026-11-20)

Three rules were added to the plate step, each tied to a failure seen here. They were checked on the public validation set first, and the occupancy model is unchanged.

- **Merge duplicate thin characters:** two character boxes in one row that overlap sideways by more than 50% of the narrower box are treated as one character. Only 36 of 81,622 real neighbouring pairs in the train/val labels overlap that much; on validation, 50% gave the best exact match among 70%, 60%, 50% and 40%. (A first try at 70% missed one triple "1" here.)
- **Dubai code letter required:** a Dubai read without a code letter goes to review (`missing_code`). None of the 4,298 Dubai train/val labels lacks one.
- **Plate size check:** a plate narrower than 10% of the bay width goes to review (`plate_too_small`), because it belongs to a car further back. This threshold was fixed from the 8-photo pilot before this test.

**Public validation set (1,000 plates, same detections):**

| | Before | After |
|---|---|---|
| Exact match | 69.7% | **71.9%** |
| Misread (wrong answer given) | 28.4% | **20.2%** |
| Answered (not sent to review) | 98.1% | 92.1% |
| Accuracy when answered | 71.0% | **78.1%** |

**This night set:**

| Outcome | Before | After |
|---|---|---|
| WRONG: misread plate | 13 | **6** |
| WRONG: plate read in an empty bay | 3 | **0** |
| Plate right | 19 | **20** |
| Car sent to review | 2 | 8 |
| Empty bay called occupied, then sent to review | 17 | 20 |

**8-photo pilot:** dangerous outputs fell from 2 to 0, and correct reads stayed at 5.

**Remaining misreads (6):** a doubled code letter read as one ("GG" → "G", "FF" → "F"), a letter swapped for another ("P" → "F", "B" → "P"), and an "8" read as "9". The code letter is still found, so the code-letter rule cannot catch these. Fixing them needs a better reader for small code letters, such as reading from an enlarged plate crop or using more training examples of the newest Dubai plates.

The public test set has not been rerun with the new rules. It should be opened once more only when the plate system is final.

## Recommended next steps

1. ~~Add the two safety rules and fix the merge rule~~: done (see above).
2. **Rerun the public plate test set once** when the plate system is final, and report it as the final system's result.
3. **Bay boxes in the real system:** draw them over the bay surface and the car body height only, without the background rows. Confirm on a new photo set, since the 72-of-86 figure comes from these same photos.
4. **Adapt the occupancy CNN with local photos:** night, wheel stops, low viewpoint, close-up cars. Split by car park: tune on one set, test on a new one. A second session at different car parks (ideally including daytime shadows) would be the clean test. Ask the professor whether local training counts toward the 10,000-item cap.
5. **Plates:** collect some newest-style Dubai two-row plates and new white Sharjah plates; consider a plate-crop second reading step for small code letters.

## Notes on the data

- **Repeat cars:** a few cars appear in two photos (the same car in a different bay pair), so there are 36 distinct plates.
- **Answer key:** bay states came from the owner; plates were read by eye from the full-size photos. One code letter (IMG_1838) is uncertain.
- **Light and framing:** all photos were taken at night under street lights. They are portrait, not landscape as planned, and the standing distance varied.
