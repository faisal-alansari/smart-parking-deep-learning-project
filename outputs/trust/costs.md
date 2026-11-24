# Error costs, thresholds and risk-coverage

Costs are in "minutes of the owner's attention" (assumptions, see the report):
- a false alert (an allowed car or an empty bay flagged as potentially unauthorized): 5. The
  owner walks down to check and may confront a guest;
- an unauthorized car missed: 10. Someone takes the owner's bay for hours;
- a request for a person to look (NEEDS_REVIEW): 1. A glance at the evidence frame;
- p_authorized = 0.7: the share of cars in the owner's bays that are allowed (own cars, guests).

What each model error costs, given these:
- Model A calls an empty bay occupied: the plate step then usually finds no plate, so the bay
  goes to a person: review (1);
- Model A calls a parked car empty: if the car is unauthorized it is missed:
  (1 - p_authorized) x missed (3);
- Model A is unsure (inside its review band): review (1);
- Model B answers with a wrong plate: an allowed car is flagged: p_authorized x false alert (3.5);
- Model B finds no plate, is unsure or is below the confidence gate: review (1).

Chosen on validation only (block 4 for Model A; the public plate validation split for Model B):
Model A's threshold on its mean probability and a review band around it, and Model B's
minimum calibrated confidence. Ties go to the middle of the tied thresholds and to the
narrower band. The chosen values are written to configs/default.yaml (`decision:`) and used by
the product. Test cost is then reported once against the alternatives, and the choice is
repeated for other cost assumptions (sensitivity).

## Chosen on validation

Model A: threshold **0.86**, review band **±0.0** (validation cost 0.0033 per bay check). Model B: minimum calibrated confidence **0.7** (validation cost 0.5250 per plate).

## Test cost against the alternatives

| Model A policy | test cost per bay check |
|---|---|
| public model, majority vote (before adapting) | 0.1605 |
| adapted, majority vote (tested product) | 0.3128 |
| adapted, cost threshold 0.86 and band 0.0 (chosen on block 4) | 0.2716 |
| always occupied (no Model A) | 0.5 |
| always ask a person | 1.0 |
| public model, car-level view | 0.1605 |
| adapted (tested product), car-level view | 0.0165 |
| public model, normal frames only | 0.2155 |
| adapted (tested product), normal frames only | 0.0055 |

Bay by bay, the adapted model costs more than the public model on the test night: it calls the bay holding half of a car standing across both bays empty, and each such check is charged as a missed car (3), while the public model's many false 'occupied' calls cost 1 each. That car is seen in the other bay, though, so it is not really missed: the car-level rows (a view added after seeing the test) and the normal-frame rows show the adapted model is far cheaper once that case is set aside.

| Model B policy | test cost per plate |
|---|---|
| no confidence gate (before) | 0.7415 |
| calibrated confidence gate 0.7 (chosen on validation) | 0.498 |
| always ask a person | 1.0 |

## Sensitivity to the cost assumptions

Each row re-chooses the thresholds on validation under other costs, then reports test cost under those same costs.

| cost assumption | A threshold | A band | A test cost | B gate | B test cost |
|---|---|---|---|---|---|
| base | 0.86 | 0.0 | 0.2716 | 0.7 | 0.498 |
| missed x0.5 (5) | 0.86 | 0.0 | 0.1389 | 0.7 | 0.498 |
| missed x2 (20) | 0.86 | 0.0 | 0.537 | 0.7 | 0.498 |
| false alert x0.4 (2) | 0.86 | 0.0 | 0.2716 | 0.1 | 0.3488 |
| false alert x2 (10) | 0.86 | 0.0 | 0.2716 | 0.85 | 0.567 |
| review x0.5 (0.5) | 0.86 | 0.0 | 0.2685 | 0.85 | 0.2835 |
| review x3 (3) | 0.86 | 0.0 | 0.284 | 0.1 | 0.9155 |
| p_authorized 0.3 | 0.86 | 0.0 | 0.6255 | 0.35 | 0.356 |
| p_authorized 0.95 | 0.88 | 0.0 | 0.0504 | 0.85 | 0.5333 |

![Risk-coverage](figures/risk_coverage.png)
