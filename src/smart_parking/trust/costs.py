"""Asymmetric error costs, cost-based thresholds, abstention and risk-coverage.

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
repeated for other cost assumptions (sensitivity). `just costs`.
"""

import json
from dataclasses import dataclass, replace

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from loguru import logger  # noqa: E402

from smart_parking.common.config import load_config  # noqa: E402
from smart_parking.common.log import setup_logging  # noqa: E402
from smart_parking.trust.calibration import apply_platt  # noqa: E402
from smart_parking.trust.common import (  # noqa: E402
    OUT,
    md,
    occupancy_models,
    occupancy_scores,
    occupancy_sets,
    plate_rows,
)

THRESHOLDS = np.round(np.linspace(0.02, 0.98, 49), 2)
BANDS = [0.0, 0.05, 0.1, 0.2, 0.3]
GATES = np.round(np.linspace(0.0, 0.95, 20), 2)


@dataclass(frozen=True)
class Costs:
    false_alert: float = 5.0
    missed_unauthorized: float = 10.0
    review: float = 1.0
    p_authorized: float = 0.7

    @property
    def a_empty_called_occupied(self) -> float:
        return self.review

    @property
    def a_car_called_empty(self) -> float:
        return (1 - self.p_authorized) * self.missed_unauthorized

    @property
    def b_wrong_plate(self) -> float:
        return self.p_authorized * self.false_alert


def occupancy_cost(y: np.ndarray, p: np.ndarray, t: float, band: float, c: Costs) -> float:
    """Mean cost per bay check: occupied if p >= t + band, empty if p < t - band, else review."""
    occ, empty = p >= t + band, p < t - band
    review = ~occ & ~empty
    cost = (occ & (y == 0)) * c.a_empty_called_occupied + (empty & (y == 1)) * c.a_car_called_empty
    return float((cost + review * c.review).mean())


def plate_cost(rows: pd.DataFrame, gate: float, c: Costs) -> float:
    """Mean cost per plate: answered and right 0, answered and wrong, or review."""
    answered = rows["answered"].astype(bool) & (rows["calibrated"] >= gate)
    wrong = answered & ~rows["correct"].astype(bool)
    return float((wrong * c.b_wrong_plate + ~answered * c.review).mean())


def _middle(values: list[float]) -> float:
    return float(values[len(values) // 2])


def choose_occupancy(y: np.ndarray, p: np.ndarray, c: Costs) -> tuple[float, float, float]:
    """(threshold, band, validation cost) with the lowest cost. A wider band must lower the
    cost to be chosen; tied thresholds give their middle one."""
    chosen = None
    for band in BANDS:  # narrowest first
        costs = {t: occupancy_cost(y, p, t, band, c) for t in THRESHOLDS}
        best = min(costs.values())
        if chosen is None or best < chosen[2] - 1e-9:
            chosen = (_middle([t for t, v in costs.items() if v <= best + 1e-9]), band, best)
    return chosen


def choose_gate(rows: pd.DataFrame, c: Costs) -> tuple[float, float]:
    costs = {g: plate_cost(rows, g, c) for g in GATES}
    best = min(costs.values())
    return _middle([g for g, v in costs.items() if v <= best + 1e-9]), best


def _risk_coverage(ax, y: np.ndarray, p: np.ndarray, t: float, label: str) -> None:  # noqa: ANN001
    """Model A: abstain on the bays closest to the threshold; error rate among the rest."""
    margin = np.abs(p - t)
    order = np.argsort(-margin)  # most certain first
    wrong = ((p >= t) != y.astype(bool))[order]
    n = np.arange(1, len(y) + 1)
    ax.plot(n / len(y), np.cumsum(wrong) / n, label=label)


def run() -> None:
    project = load_config()
    c = Costs()
    sets, models = occupancy_sets(), occupancy_models()
    (xv, mv), (xt, mt) = sets["validation"], sets["test"]
    pv, _ = occupancy_scores(xv, models)
    pt, vote_t = occupancy_scores(xt, models)
    yv, yt = mv["label"].to_numpy(), mt["label"].to_numpy()
    t_a, band, val_cost_a = choose_occupancy(yv, pv, c)
    from smart_parking.occupancy.train import load_checkpoint, pick_device

    cfg = project.occupancy
    public = [
        load_checkpoint(cfg.checkpoint_dir / f"final_s{s}.pt", pick_device()) for s in cfg.seeds
    ]
    _, vote_public = occupancy_scores(xt, public)

    def decided_cost(y: np.ndarray, occ: np.ndarray) -> float:
        return float(((occ & (y == 0)) * c.a_empty_called_occupied
                      + (~occ & (y == 1)) * c.a_car_called_empty).mean())  # fmt: skip

    rows_a = [
        {"Model A policy": "public model, majority vote (before adapting)",
         "test cost per bay check": decided_cost(yt, vote_public)},
        {"Model A policy": "adapted, majority vote (tested product)",
         "test cost per bay check": decided_cost(yt, vote_t)},
        {"Model A policy": f"adapted, cost threshold {t_a} and band {band} (chosen on block 4)",
         "test cost per bay check": occupancy_cost(yt, pt, t_a, band, c)},
        {"Model A policy": "always occupied (no Model A)",
         "test cost per bay check": decided_cost(yt, np.ones(len(yt), bool))},
        {"Model A policy": "always ask a person",
         "test cost per bay check": c.review},
    ]  # fmt: skip
    # Car-level view (added after seeing the test): a bay called empty is not a missed car when
    # the same car is seen in the other bay at the same moment (a car across both bays).
    other = mt.assign(occ=vote_t, occ_public=vote_public).set_index(["t", "bay"])

    def car_level(col: str, occ: np.ndarray) -> float:
        seen_other = np.array([bool(other.loc[(r.t, "right" if r.bay == "left" else "left"), col])
                               for r in mt.itertuples()])  # fmt: skip
        straddle = (mt["slice"] == "car across both bays").to_numpy()
        missed = ~occ & (yt == 1) & ~(straddle & seen_other)
        return float(((occ & (yt == 0)) * c.a_empty_called_occupied
                      + missed * c.a_car_called_empty).mean())  # fmt: skip

    normal = (mt["slice"] == "normal").to_numpy()
    rows_a += [
        {"Model A policy": "public model, car-level view",
         "test cost per bay check": car_level("occ_public", vote_public)},
        {"Model A policy": "adapted (tested product), car-level view",
         "test cost per bay check": car_level("occ", vote_t)},
        {"Model A policy": "public model, normal frames only",
         "test cost per bay check": decided_cost(yt[normal], vote_public[normal])},
        {"Model A policy": "adapted (tested product), normal frames only",
         "test cost per bay check": decided_cost(yt[normal], vote_t[normal])},
    ]  # fmt: skip
    calib = json.loads((OUT / "calibration.json").read_text())["plate"]
    plates = {}
    for split in ("val", "test"):
        r = plate_rows(split)
        r["calibrated"] = apply_platt(
            r["confidence"].astype(float).to_numpy(), (calib["a"], calib["b"])
        )
        plates[split] = r
    gate, val_cost_b = choose_gate(plates["val"], c)
    always_review = c.review
    rows_b = [
        {"Model B policy": "no confidence gate (before)",
         "test cost per plate": plate_cost(plates["test"], 0.0, c)},
        {"Model B policy": f"calibrated confidence gate {gate} (chosen on validation)",
         "test cost per plate": plate_cost(plates["test"], gate, c)},
        {"Model B policy": "always ask a person", "test cost per plate": always_review},
    ]  # fmt: skip
    sens = []
    for name, cc in [
        ("base", c),
        ("missed x0.5 (5)", replace(c, missed_unauthorized=5)),
        ("missed x2 (20)", replace(c, missed_unauthorized=20)),
        ("false alert x0.4 (2)", replace(c, false_alert=2)),
        ("false alert x2 (10)", replace(c, false_alert=10)),
        ("review x0.5 (0.5)", replace(c, review=0.5)),
        ("review x3 (3)", replace(c, review=3)),
        ("p_authorized 0.3", replace(c, p_authorized=0.3)),
        ("p_authorized 0.95", replace(c, p_authorized=0.95)),
    ]:
        ta, ba, _ = choose_occupancy(yv, pv, cc)
        g, _ = choose_gate(plates["val"], cc)
        sens.append({"cost assumption": name, "A threshold": ta, "A band": ba,
                     "A test cost": round(occupancy_cost(yt, pt, ta, ba, cc), 4),
                     "B gate": g,
                     "B test cost": round(plate_cost(plates["test"], g, cc), 4)})  # fmt: skip
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4))
    _risk_coverage(axes[0], yv, pv, t_a, "validation (block 4)")
    _risk_coverage(axes[0], yt, pt, t_a, "test (first video)")
    axes[0].set(title="Model A: abstain on the least certain bays", xlabel="coverage (answered)",
                ylabel="error rate among answered")  # fmt: skip
    for split, r in plates.items():
        cov, risk = [], []
        for g in np.linspace(0, 0.99, 100):
            ans = r["answered"].astype(bool) & (r["calibrated"] >= g)
            cov.append(ans.mean())
            risk.append((ans & ~r["correct"].astype(bool)).sum() / max(ans.sum(), 1))
        axes[1].plot(cov, risk, label=split)
        a = r["answered"].astype(bool) & (r["calibrated"] >= gate)
        axes[1].plot(a.mean(), (a & ~r["correct"].astype(bool)).sum() / max(a.sum(), 1), "ko")
    axes[1].set(title=f"Model B: confidence gate (dot = chosen {gate})",
                xlabel="coverage (answered)",
                ylabel="wrong reads among answered")  # fmt: skip
    for ax in axes:
        ax.legend(fontsize=7)
        ax.title.set_fontsize(9)
    fig.tight_layout()
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "figures" / "risk_coverage.png", dpi=150)
    _write_config(t_a, band, gate, c)
    (OUT / "costs.md").write_text(
        "# Error costs, thresholds and risk-coverage\n\n"
        + __doc__.split("\n\n", 1)[1].split("`just")[0].strip()
        + f"\n\n## Chosen on validation\n\nModel A: threshold **{t_a}**, review band **±{band}** "
        f"(validation cost {val_cost_a:.4f} per bay check). Model B: minimum calibrated "
        f"confidence **{gate}** (validation cost {val_cost_b:.4f} per plate).\n\n"
        "## Test cost against the alternatives\n\n"
        + md(pd.DataFrame(rows_a).round(4))
        + "\n\nBay by bay, the adapted model costs more than the public model on the test "
        "night: it calls the bay holding half of a car standing across both bays empty, and "
        "each such check is charged as a missed car (3), while the public model's many false "
        "'occupied' calls cost 1 each. That car is seen in the other bay, though, so it is not "
        "really missed: the car-level rows (a view added after seeing the test) and the "
        "normal-frame rows show the adapted model is far cheaper once that case is set aside.\n\n"
        + md(pd.DataFrame(rows_b).round(4))
        + "\n\n## Sensitivity to the cost assumptions\n\n"
        "Each row re-chooses the thresholds on validation under other costs, then reports test "
        "cost under those same costs.\n\n"
        + md(pd.DataFrame(sens))
        + "\n\n![Risk-coverage](figures/risk_coverage.png)\n"
    )
    logger.info("Costs: A threshold {} band {}, B gate {} -> {}", t_a, band, gate, OUT / "costs.md")


def _write_config(t_a: float, band: float, gate: float, c: Costs) -> None:
    """Store the chosen values in configs/default.yaml (`decision:`), replacing old ones."""
    from pathlib import Path

    platt = json.loads((OUT / "calibration.json").read_text())["plate"]
    path = Path("configs/default.yaml")
    text = path.read_text().split("\n# Decision thresholds chosen by expected cost")[0].rstrip()
    block = (
        "\n\n# Decision thresholds chosen by expected cost on validation (`just costs`,\n"
        "# outputs/trust/costs.md). Costs in minutes of the owner's attention.\n"
        "decision:\n"
        f"  occupancy_threshold: {t_a}\n  occupancy_review_band: {band}\n"
        f"  plate_min_confidence: {gate}\n"
        f"  plate_platt_a: {platt['a']}\n  plate_platt_b: {platt['b']}\n"
        f"  cost_false_alert: {c.false_alert}\n"
        f"  cost_missed_unauthorized: {c.missed_unauthorized}\n"
        f"  cost_review: {c.review}\n  p_authorized: {c.p_authorized}\n"
    )
    path.write_text(text + block)


def main() -> None:
    setup_logging(load_config().logging)
    run()


if __name__ == "__main__":
    main()
