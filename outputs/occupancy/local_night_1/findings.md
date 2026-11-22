# Findings: night car parks, 43 photos (2026-11-20)

Both models were trained on public data only. 43 owner photos at night, each showing a pair of bays in a public car park (several car parks): **86 bays, 46 empty, 40 occupied, 40 readable plates**. One shared pair of bay boxes for all photos, like a fixed camera set up once. Reproduce with `just local-night-1` (`results.md` and `probes.md` hold the numbers) and `just plate-rule-evidence` (`outputs/plates/rule_evidence.md`). Each finding below is marked **measured** (a saved number backs it) or **hypothesis** (a likely reason, not tested); see "Where each number comes from" at the end.

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

1. **Background inside the box (main cause).** From a low, standing viewpoint, the upper part of each bay box shows the next row of cars, buildings and lamps. Cutting the top 30% of every box raised accuracy from 60 to 72 of 86 and cut false alarms from 20 to 11. Growing the box to include more background raised false alarms to 37. *Measured.* Likely reason (*hypothesis*): the public training crops come from raised cameras looking down, so they rarely contain other rows of cars.
2. **Yellow concrete wheel stops in empty bays.** Wheel stops were marked by eye for every empty bay (26 of 46 have one inside the box). With the original box, 15 of 26 bays with a wheel stop were false alarms, against 5 of 20 without one. After cutting the background, 10 of the 11 false alarms left have a wheel stop. *Measured* (a link, not proof of cause). Likely reason (*hypothesis*): the public training bays rarely show wheel stops, and a bright horizontal block on dark ground looks like the back of a car.
3. **Close-up cars missed.** 6 of 40 cars were missed (*measured*). They come from the later photos, where the owner stood closer and a light car under orange street light fills the whole box. Likely reason (*hypothesis*, not tested): the model treats a smooth, plain surface as empty ground, because training crops show a whole car with ground around it.
4. **Not the cause:** overall brightness (false alarms and correct empty bays are equally bright, mean brightness 92 and 91 out of 255), and neighbouring cars at the sides of the box (trimming the sides changed 1 bay). *Measured.*
5. **Seed disagreement is a weak warning only.** When the 3 CNN seeds disagree, the answer is right 13 of 21 times. When they agree, it is right 47 of 65 times, so unanimous answers are still often wrong. *Measured.*

## Plate reading: why it failed

1. **Small code letters on the newest two-row Dubai plates are lost.** Of the 6 car plates sent to review for a missing code letter (after the reader fixes), the detector found a letter box below the 0.2 cut-off on 4 (confidence 0.14–0.19) and no letter box at all on 2. On 5 of the 6 misread plates, extra letter boxes at 0.05–0.15 were dropped while one letter was kept, so a doubled letter such as "GG" or "FF" becomes a single letter. A "B" also became "P". *Measured* (`probes.md`, last table). The cut-off was not lowered: that would be tuning on these photos.
2. **"Z" read as "2"** when the code letter sits in the top corner of the newest Dubai design.
3. **A thin digit "1" counted several times.** Overlapping boxes for the same thin "1" were not merged, because they overlapped too little for the old merge rule. The same pattern appeared in the public test set (for example a repeated last digit). **Fixed** by the merge rule below.
4. **The new white Sharjah plate goes to review (no emirate).** *Measured.* Likely reason (*hypothesis*, not checked in the labels): this plate style is missing from the training data. The outcome is safe, but gives no answer.
5. **A confidence rule would not help.** Misreads (confidence 0.26–0.89) and correct reads (0.25–0.91) overlap, because most misreads are a missing letter, and a missing letter cannot lower the confidence.
6. **Reading the whole photo fails** (0 of 34 right), as in the pilot. Reading from the bay area is the right design.

## What worked

- **Plate size separates parked cars from background cars, again.** Plates of cars in the bay were 13–29% of the bay width; plates seen through empty bays were 4–7% (pilot: 27–29% vs 4–9%).
- **The plate step already protects against most occupancy false alarms.** 17 of the 20 empty bays called occupied found no valid plate and went to review instead of a decision.
- **Common plates were read well.** All 19 correct reads were Dubai plates, read at night under orange light.

## Reader fixes applied (2026-11-20)

Three rules were added to the plate step, each tied to a failure seen here. They were checked on the public validation set first, and the occupancy model is unchanged.

- **Merge duplicate thin characters:** two character boxes in one row that overlap sideways by more than 50% of the narrower box are treated as one character. Only 36 of 81,622 real neighbouring pairs in the train/val labels overlap that much; on validation, 50% gave the best exact match among 70%, 60%, 50% and 40%. (A first try at 70% missed one triple "1" here.)
- **Dubai code letter required:** a Dubai read without a code letter goes to review (`missing_code`). None of the 4,302 main Dubai plates in the train/val labels (the plate named in the file) lacks one. 98 of 500 smaller background Dubai plates do, but many of those have only some characters labelled.
- **Plate size check:** a plate narrower than 10% of the bay width goes to review (`plate_too_small`), because it belongs to a car further back. This threshold was fixed from the 8-photo pilot before this test.

**Public validation set (1,000 plates, same detections; `outputs/plates/rule_evidence.md` also shows each rule alone):**

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
- **Answer key:** bay states came from the owner; plates were read by eye from the full-size photos. The one uncertain code letter (IMG_1838) was confirmed by the owner on 2026-11-22.
- **Light and framing:** all photos were taken at night under street lights. They are portrait, not landscape as planned, and the standing distance varied.

## Where each number comes from

| Finding | Source | Kind |
|---|---|---|
| Occupancy, plate and loop results | `results.md`, `predictions.csv` | measured |
| Box shapes (background cut, zoom, sides) | `probes.md` | measured (same photos) |
| Wheel stops | `wheel_stop` in the set's config (marked by eye), `probes.md` | measured link; cause is a hypothesis |
| Brightness, seed agreement | `probes.md` | measured |
| Plate size of parked vs background cars | `plate_width` in `predictions.csv` | measured |
| Lost code letters | `probes.md`, last table | measured |
| Merge cut-off, code-letter rule, validation before/after | `outputs/plates/rule_evidence.md` | measured (validation) |
| Why training data does not cover these cases | not checked | hypothesis |

`predictions.csv`, `results.md` and the set's config hold strangers' plate numbers, so they stay on this computer and are not in Git.
