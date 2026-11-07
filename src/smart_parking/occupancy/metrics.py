"""Binary metrics for "occupied" (positive class = 1), thresholds and bootstrap CIs."""

import numpy as np

METRICS = ("f1", "recall", "precision", "fpr", "accuracy")


def binary_metrics(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    """F1, recall, precision, false positive rate and accuracy for label 1."""
    y, pred = np.asarray(y).astype(bool), np.asarray(pred).astype(bool)
    tp = float(np.sum(y & pred))
    fp = float(np.sum(~y & pred))
    fn = float(np.sum(y & ~pred))
    tn = float(np.sum(~y & ~pred))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "f1": f1,
        "recall": recall,
        "precision": precision,
        "fpr": fp / (fp + tn) if fp + tn else 0.0,
        "accuracy": (tp + tn) / len(y),
    }


def best_threshold(y: np.ndarray, score: np.ndarray) -> float:
    """Threshold on `score` (higher = occupied) that maximises F1. Use on validation only."""
    candidates = np.unique(np.quantile(score, np.linspace(0.001, 0.999, 999)))
    f1s = [binary_metrics(y, score >= t)["f1"] for t in candidates]
    return float(candidates[int(np.argmax(f1s))])


def cluster_bootstrap_ci(
    y: np.ndarray,
    preds: list[np.ndarray],
    clusters: np.ndarray,
    n_boot: int = 1000,
    seed: int = 0,
) -> dict[str, tuple[float, float]]:
    """95% CI of each metric, averaged over `preds` (e.g. seeds).

    Resamples whole clusters (one parking bay seen over time), because crops of the
    same bay are not independent. Plain per-crop resampling would give CIs that
    are too narrow.
    """
    rng = np.random.default_rng(seed)
    ids, inverse = np.unique(clusters, return_inverse=True)
    members = [np.flatnonzero(inverse == i) for i in range(len(ids))]
    draws = {m: [] for m in METRICS}
    for _ in range(n_boot):
        idx = np.concatenate([members[i] for i in rng.integers(0, len(ids), len(ids))])
        per_pred = [binary_metrics(y[idx], p[idx]) for p in preds]
        for m in METRICS:
            draws[m].append(np.mean([r[m] for r in per_pred]))
    return {
        m: (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))) for m, v in draws.items()
    }
