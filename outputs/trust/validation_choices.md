# Choices made on block 4 (validation) only

Block 4 of night video 2 is split into two folds of alternating 60-second blocks (time halves
would leave one fold with parked cars only); each check fits on one fold and is measured on the
other, both ways. Rules fixed before running (report Appendix A, 2026-11-26):
1. **Model A confidence:** Platt scaling only if its mean held-out ECE is lower than the raw
   probability's; otherwise (or a tie) the raw probability.
2. **Feature-distance bay check:** used only if its held-out false-alarm rate is at most 2% and
   it catches at least 5% of corrupted block-4 frames that the blocked, view and sharpness checks
   miss.
No test data is read. Plate caching, the third choice, is decided in

## 1. Model A confidence

| held-out fold | crops | ECE raw | ECE Platt (fit on the other fold) |
|---|---|---|---|
| even minutes | 294 | 0.006 | 0.0393 |
| odd minutes | 306 | 0.016 | 0.0073 |

**Chosen: raw.**

## 2. Feature-distance bay check

| held-out fold | normal frames | bay check false alarms | corrupted frames | caught only by the bay check |
|---|---|---|---|---|
| even minutes | 38 | 5.3% | 190 | 12.6% |
| odd minutes | 36 | 0.0% | 180 | 12.8% |

**Bay check: not used.**
