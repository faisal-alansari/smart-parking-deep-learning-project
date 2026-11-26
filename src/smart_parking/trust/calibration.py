"""Calibration of the confidences the product shows: reliability diagrams, ECE, Platt scaling.

Model A: P(occupied) = the mean probability of the three deployed seeds, per bay crop.
Model B: the plate read's confidence (the lowest box confidence in the read) against whether
an answered read is exactly right. Model C gives no single confidence: it proposes a change only
when its checks agree, so its trust is measured by coverage and dangerous answers instead
(outputs/commands/final_test.md).

Binning: 10 equal-width bins of the confidence; each bin shows its mean confidence, its observed
rate and its count. ECE = the count-weighted mean gap between them. Calibration is improved with
Platt scaling (a logistic fit on the logit of the confidence), fitted on validation only
(block 4 for Model A, the public plate validation split for Model B), then shown on test.
The fitted parameters are saved to outputs/trust/calibration.json and used in the product.
`just calibration`.
"""

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from loguru import logger  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402

from smart_parking.common.config import load_config  # noqa: E402
from smart_parking.common.log import setup_logging  # noqa: E402
from smart_parking.trust.common import (  # noqa: E402
    FITTED_CHANGED,
    OUT,
    md,
    occupancy_models,
    occupancy_scores,
    occupancy_sets,
    plate_rows,
    refit_flag,
    same_numbers,
)

BINS = 10
EPS = 1e-6


def logit(p: np.ndarray) -> np.ndarray:
    """Log-odds of p, clipped away from 0 and 1."""
    p = np.clip(p, EPS, 1 - EPS)
    return np.log(p / (1 - p))


def reliability(y: np.ndarray, p: np.ndarray, bins: int = BINS) -> pd.DataFrame:
    """Per bin: confidence range, count, mean confidence and observed rate."""
    edges = np.linspace(0, 1, bins + 1)
    idx = np.clip(np.digitize(p, edges[1:-1]), 0, bins - 1)
    rows = []
    for b in range(bins):
        m = idx == b
        rows.append({"bin": f"{edges[b]:.1f}-{edges[b + 1]:.1f}", "count": int(m.sum()),
                     "mean confidence": round(float(p[m].mean()), 3) if m.any() else "",
                     "observed rate": round(float(y[m].mean()), 3) if m.any() else ""})  # fmt: skip
    return pd.DataFrame(rows)


def ece(y: np.ndarray, p: np.ndarray, bins: int = BINS) -> float:
    """Expected calibration error over equal-width bins."""
    edges = np.linspace(0, 1, bins + 1)
    idx = np.clip(np.digitize(p, edges[1:-1]), 0, bins - 1)
    return float(sum((idx == b).mean() * abs(p[idx == b].mean() - y[idx == b].mean())
                     for b in range(bins) if (idx == b).any()))  # fmt: skip


def platt(y: np.ndarray, p: np.ndarray) -> tuple[float, float]:
    """(a, b) so that sigmoid(a * logit(p) + b) is calibrated on these (validation) rows."""
    lr = LogisticRegression(C=1e6).fit(logit(p).reshape(-1, 1), y.astype(int))
    return float(lr.coef_[0, 0]), float(lr.intercept_[0])


def apply_platt(p: np.ndarray, ab: tuple[float, float]) -> np.ndarray:
    """Apply Platt parameters (a, b) to probabilities."""
    return 1 / (1 + np.exp(-(ab[0] * logit(p) + ab[1])))


def _panel(ax, y: np.ndarray, p: np.ndarray, title: str) -> None:  # noqa: ANN001
    r = reliability(y, p)
    have = r["count"] > 0
    centers = (np.arange(BINS) + 0.5) / BINS
    ax.plot([0, 1], [0, 1], "--", color="grey", lw=1)
    ax.bar(centers[have], r.loc[have, "observed rate"].astype(float), width=0.09, alpha=0.6,
           label="observed rate")  # fmt: skip
    conf, rate = r.loc[have, "mean confidence"], r.loc[have, "observed rate"]
    ax.plot(conf.astype(float), rate.astype(float), "o-", color="black", ms=3)
    for c, n in zip(centers[have], r.loc[have, "count"], strict=True):
        ax.text(c, 0.02, str(n), ha="center", fontsize=6, rotation=90)
    ax.set(xlim=(0, 1), ylim=(0, 1), title=f"{title}\nECE {ece(y, p):.3f}", xlabel="confidence",
           ylabel="observed rate")  # fmt: skip
    ax.title.set_fontsize(8)


def run(refit: bool = False) -> None:
    """Fit Platt scaling for Models A and B, compare ECE on test, write `calibration.md`."""
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "figures").mkdir(exist_ok=True)
    sets, models = occupancy_sets(), occupancy_models()
    a = {k: (occupancy_scores(x, models)[0], m["label"].to_numpy()) for k, (x, m) in sets.items()}
    ab_a = platt(a["validation"][1], a["validation"][0])
    val_b, test_b = plate_rows("val"), plate_rows("test")
    val_b, test_b = val_b[val_b.answered.astype(bool)], test_b[test_b.answered.astype(bool)]
    yb_v, pb_v = val_b.correct.astype(bool).to_numpy(), val_b.confidence.astype(float).to_numpy()
    yb_t, pb_t = test_b.correct.astype(bool).to_numpy(), test_b.confidence.astype(float).to_numpy()
    ab_b = platt(yb_v, pb_v)
    pa_t, ya_t = a["test"]
    rows = [
        {"model": "A occupancy", "split": "validation (block 4)", "items": len(a["validation"][1]),
         "ECE before": ece(a["validation"][1], a["validation"][0]),
         "ECE after": ece(a["validation"][1], apply_platt(a["validation"][0], ab_a))},
        {"model": "A occupancy", "split": "test (night video 3)", "items": len(ya_t),
         "ECE before": ece(ya_t, pa_t), "ECE after": ece(ya_t, apply_platt(pa_t, ab_a))},
        {"model": "B plate read", "split": "validation (public)", "items": len(yb_v),
         "ECE before": ece(yb_v, pb_v), "ECE after": ece(yb_v, apply_platt(pb_v, ab_b))},
        {"model": "B plate read", "split": "test (public)", "items": len(yb_t),
         "ECE before": ece(yb_t, pb_t), "ECE after": ece(yb_t, apply_platt(pb_t, ab_b))},
    ]  # fmt: skip
    table = pd.DataFrame(rows).round(4)
    fig, axes = plt.subplots(1, 4, figsize=(13, 3.4))
    _panel(axes[0], ya_t, pa_t, "A occupancy, test, raw")
    _panel(axes[1], ya_t, apply_platt(pa_t, ab_a), "A occupancy, test, Platt (fit on block 4)")
    _panel(axes[2], yb_t, pb_t, "B plate read, test, raw")
    _panel(axes[3], yb_t, apply_platt(pb_t, ab_b), "B plate read, test, Platt (fit on val)")
    fig.tight_layout()
    fig.savefig(OUT / "figures" / "reliability.png", dpi=150)
    # Used by the product: Platt for Model B; Model A keeps its raw probability (see below)
    params = {"occupancy": {"method": "raw", "platt_a": ab_a[0], "platt_b": ab_a[1]},
              "plate": {"method": "platt", "a": ab_b[0], "b": ab_b[1]}}  # fmt: skip
    saved = OUT / "calibration.json"
    if refit or not saved.exists():
        saved.write_text(json.dumps(params, indent=2))
    elif not same_numbers(json.loads(saved.read_text()), params):
        raise SystemExit(FITTED_CHANGED.format("Calibration"))
    bins = []
    for name, y, p in (("A raw", ya_t, pa_t), ("A Platt", ya_t, apply_platt(pa_t, ab_a)),
                       ("B raw", yb_t, pb_t),
                       ("B Platt", yb_t, apply_platt(pb_t, ab_b))):  # fmt: skip
        bins.append(f"### {name} (test)\n\n" + md(reliability(y, p)))
    (OUT / "calibration.md").write_text(
        "# Calibration (test split)\n\n"
        + __doc__.split("\n\n", 1)[1].split("`just")[0].strip()
        + "\n\n"
        + md(table)
        + "\n\n![Reliability diagrams](figures/reliability.png)\n\n"
        "## What this says\n\n"
        "- **Model B is under-confident:** its reads are right more often than its confidence "
        "says (bins below). Platt scaling fitted on validation fixes this on test, so the "
        "product shows Model B's calibrated confidence.\n"
        "- **Model A keeps its raw probability.** The choice was made on block 4 alone: with "
        "each of two folds of block 4 held out in turn, Platt scaling had a higher calibration "
        "error than the raw probability (`validation_choices.md`). The test night only reports how "
        "both behave; nothing was chosen on it.\n\n"
        "## Bins (test)\n\n" + "\n\n".join(bins) + "\n"
    )
    logger.info("Calibration -> {}", OUT / "calibration.md")


def main() -> None:
    """Set up logging and run the calibration (`--refit` stores the new fit)."""
    setup_logging(load_config().logging)
    run(refit_flag())


if __name__ == "__main__":
    main()
