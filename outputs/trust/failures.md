# Failure analysis

Sources (all produced by other `just` recipes; nothing is picked by hand):
1. the full system on the owner's camera, the sealed test night 3
   (outputs/final_test/local/night_3_frames.csv, scored frames): every bay whose frame-by-frame
   answer differs from the truth;
2. the full system on other car parks' photos (outputs/loop/local/bays.csv);
3. Model B on the public plate test (data/processed/trust/plate_reads_test.csv);
4. Model C on its frozen test (outputs/commands/tiered_test.md, counts per slice).
Then the fixes made during the project, each tied to a failure it was built for, with its
before/after evidence, and the failure modes that remain.

## 1. Owner's camera, the sealed test night 3 (1162 scored bay checks; errors: 225)

| cause | bay checks | share of errors |
|---|---|---|
| B: plate not in this bay (car across both bays) | 97 | 43% |
| A: bay holding half of a car called empty | 95 | 42% |
| B: plate misread | 13 | 6% |
| B: plate unclear, sent to a person (plate_too_small) | 13 | 6% |
| A: parked car missed | 5 | 2% |
| B: no plate found | 1 | 0% |
| A: empty bay called occupied | 1 | 0% |

## 2. Other car parks' photos (102 bays; errors: 27)

| cause | bays |
|---|---|
| A: parked car missed | 15 |
| A: empty bay called occupied | 5 |
| B: plate unclear, sent to a person (missing_code) | 4 |
| B: plate unclear, sent to a person (no_emirate) | 2 |
| B: plate unclear, sent to a person (invalid_length) | 1 |

## 3. Model B, public plate test (all outcomes)

| outcome | images |
|---|---|
| right | 726 |
| misread | 187 |
| sent to a person (missing_code) | 67 |
| sent to a person (no_emirate) | 14 |
| sent to a person (invalid_length) | 5 |
| plate not found | 1 |

## 4. Model C, frozen test (160 commands)

| cause | commands |
|---|---|
| a clear command asked about again (needless question) | 58 |
|   of which: new wording (action-word check) | 32 |
| a wrong change put to the owner (dangerous) | 1 |
| an unclear command answered with the wrong question or reason | 11 |
| another request not recognised as unsupported | 7 |

## Fixes made, each tied to an observed failure

| failure seen | fix | evidence (before -> after) |
|---|---|---|
| Plate reader read one thin '1' as '111' | rule: merge sideways-overlapping boxes | outputs/plates/rule_evidence.md; final_results_before_safety_rules.md -> final_results.md: wrong reads 27.5% -> 19.2% |
| A Dubai plate read without its code letter | rule: Dubai reads need a code, else ask | same as above |
| A plate of a car further back read as the parked car's | rule: a plate narrower than 10% of the bay goes to a person | outputs/occupancy/local_night_1/findings.md |
| Empty bays at night called occupied (78 of 243 on night 1) | adapt Model A on the owner's camera (night video 2) | outputs/occupancy/adaptation_test.md: 78 -> 2 |
| One-frame alerts while a car moves; 78 notifications in 10 min | one decision per stay (10 s to confirm, majority plate) | outputs/loop/video_night_1_stays.md (night 1): false alerts 4 -> 0, notifications 78 -> 28 (public model frame by frame -> adapted model per stay) |
| Model C dropped 'tomorrow' from a time | check: a day said must be in the time read | outputs/commands/final_test.md (change after the test): 0 wrong proposals in the full loop |
| Model C's two models agreed on wrong changes | a second model must agree; action-word and loose-number checks | outputs/commands/dev_tuning.md, final_test.md: 1 dangerous of 160 |
| The camera check flagged every frame 40% darker than usual | measure sharpness on a contrast-normalised frame | outputs/trust/robustness_images.md: 100% -> 2.5% of frames flagged at brightness x0.6 |
| A plate gate tuned on public photos sent 30% of the owner's bays to a person | re-choose the gate on the owner's camera (block 4) | outputs/trust/costs.md; full system right answers 67% -> 84% on night 1 |
| Platt scaling made Model A's confidence worse on held-out data | keep Model A's raw probability (chosen on block 4 alone) | outputs/trust/validation_choices.md: held-out ECE 0.011 raw vs 0.023 Platt |

## Failure modes that remain

- A car standing across both bays: the bay holding half of it is called empty, and on the test night a car centred on the middle line was called EMPTY in both bays, so a car without a valid permit was missed (outputs/final_test/night_3.md).
- Model A is a specialist: worse on other car parks and on the unseen public site than the public-only model; a new camera needs a new set-up and new adaptation.
- Over-exposure and strong glare: the camera check catches only part of it (23-36%).
- Model C asks again about most commands in new wording (the action-word check), and one negation ('don't allow ... anymore') was read as a change.
- The plate reader cannot read about 8% of public test plates and misreads some codes at night.
- Evidence is small: one sealed test night of 24 minutes with two cars (and one seen night of 10 minutes); no daytime test on the owner's camera.
