"""Plate-level metrics: full-plate exact match, coverage, misreads and character errors."""

import numpy as np

from smart_parking.plates.reader import Box, PlateRead, iou

MATCH_IOU = 0.5
PLATE_METRICS = (
    "exact_match",
    "coverage",
    "answered_accuracy",
    "misread_rate",
    "plate_found",
    "emirate_accuracy",
    "cer",
)


def edit_distance(a: str, b: str) -> int:
    """Levenshtein distance between two strings."""
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def score_image(truth: PlateRead, reads: list[PlateRead]) -> dict:
    """Compare the main ground-truth plate with the best-overlapping predicted plate."""
    t = Box("plate", 1.0, *truth.box)
    best, best_iou = None, 0.0
    for r in reads:
        v = iou(t, Box("plate", 1.0, *r.box))
        if v > best_iou:
            best, best_iou = r, v
    if best is None or best_iou < MATCH_IOU:
        return {
            "found": False,
            "answered": False,
            "correct": False,
            "emirate_ok": False,
            "cer": 1.0,
            "pred_text": "",
            "pred_emirate": None,
            "reason": "plate_not_found",
        }
    correct = best.emirate == truth.emirate and best.text == truth.text
    return {
        "found": True,
        "answered": best.decision == "READ",
        "correct": best.decision == "READ" and correct,
        "emirate_ok": best.emirate == truth.emirate,
        "cer": edit_distance(best.text, truth.text) / max(1, len(truth.text)),
        "pred_text": best.text,
        "pred_emirate": best.emirate,
        "reason": best.reason,
    }


def summarise(rows: list[dict]) -> dict[str, float]:
    """Aggregate per-image scores. A review request counts as not correct."""
    found = np.array([r["found"] for r in rows])
    answered = np.array([r["answered"] for r in rows])
    correct = np.array([r["correct"] for r in rows])
    n = len(rows)
    return {
        "exact_match": float(correct.mean()),
        "coverage": float(answered.mean()),
        "answered_accuracy": float(correct[answered].mean()) if answered.any() else 0.0,
        "misread_rate": float((answered & ~correct).sum() / n),
        "plate_found": float(found.mean()),
        "emirate_accuracy": float(np.mean([r["emirate_ok"] for r in rows])),
        "cer": float(np.mean([r["cer"] for r in rows])),
    }
