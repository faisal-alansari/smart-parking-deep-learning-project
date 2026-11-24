"""The product's operating rules, chosen by expected cost on validation (`just costs`).

- Model A: a bay is occupied when the mean probability of the deployed seeds reaches
  `occupancy_threshold`; within `occupancy_review_band` of it the bay is unsure and goes to a
  person. (The values are set for the adapted model, `occupancy.deploy: adapted`.)
- Model B: a plate read's confidence is calibrated with Platt scaling (fitted on validation,
  `just calibration`); a clear read below `plate_min_confidence` goes to a person
  ("low_confidence").
"""

import numpy as np

from smart_parking.common.config import DecisionConfig
from smart_parking.plates.reader import PlateRead


def occupancy_decision(
    probs: list[np.ndarray], d: DecisionConfig
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(mean probability, occupied, unsure) for each bay crop."""
    p = np.mean(probs, axis=0)
    unsure = np.abs(p - d.occupancy_threshold) < d.occupancy_review_band
    return p, (p >= d.occupancy_threshold) & ~unsure, unsure


def calibrated(confidence: float, d: DecisionConfig) -> float:
    z = np.log(max(confidence, 1e-6) / max(1 - confidence, 1e-6))
    return float(1 / (1 + np.exp(-(d.plate_platt_a * z + d.plate_platt_b))))


def gate_plate(read: PlateRead | None, d: DecisionConfig) -> PlateRead | None:
    """Calibrate the read's confidence; a clear read below the gate goes to a person."""
    if read is None:
        return None
    conf = calibrated(read.confidence, d)
    if read.decision == "READ" and conf < d.plate_min_confidence:
        return read.model_copy(
            update={"confidence": conf, "decision": "NEEDS_REVIEW", "reason": "low_confidence"}
        )
    return read.model_copy(update={"confidence": conf})
