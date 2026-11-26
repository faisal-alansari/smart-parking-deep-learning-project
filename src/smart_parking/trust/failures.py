"""Systematic failure analysis: every error collected, sorted into causes, counted.

Sources (all produced by other `just` recipes; nothing is picked by hand):
1. the full system on the owner's camera, the sealed test night 3
   (outputs/final_test/local/night_3_frames.csv, scored frames): every bay whose frame-by-frame
   answer differs from the truth;
2. the full system on other car parks' photos (outputs/loop/local/bays.csv);
3. Model B on the public plate test (data/processed/trust/plate_reads_test.csv);
4. Model C on its frozen test (outputs/commands/tiered_test.md, counts per slice).
Then the fixes made during the project, each tied to a failure it was built for, with its
before/after evidence, and the failure modes that remain. `just failures`.
"""

import re
from pathlib import Path

import pandas as pd
from loguru import logger

from smart_parking.common.config import load_config
from smart_parking.common.log import setup_logging
from smart_parking.trust.common import OUT, md, plate_rows


def _camera_cause(r) -> str:  # noqa: ANN001
    if r.occupied == -1:
        return "camera check asked a person (frame looked unfamiliar)"
    straddle = r.slice == "car across both bays"
    if r.truth_occupied and not r.occupied:
        return "A: bay holding half of a car called empty" if straddle else "A: parked car missed"
    if not r.truth_occupied and r.occupied:
        return "A: empty bay called occupied"
    if r.status == "NEEDS_REVIEW":
        if straddle:
            return "B: plate not in this bay (car across both bays)"
        if r.reason in ("", "no_plate_found"):
            return "B: no plate found"
        return f"B: plate unclear, sent to a person ({r.reason})"
    if r.plate.split(" ")[-1] != r.true_plate:
        return "B: plate misread"
    return "other"


def camera() -> tuple[pd.DataFrame, int]:
    """Test-night errors by cause (moving frames left out), and the number of scored checks."""
    d = pd.read_csv("outputs/final_test/local/night_3_frames.csv", keep_default_na=False)
    d = d[~d["moving"].astype(str).eq("True")]
    wrong = d[d["status"] != d["true_status"]]
    causes = wrong.apply(_camera_cause, axis=1).value_counts()
    out = causes.rename_axis("cause").reset_index(name="bay checks")
    out["share of errors"] = (out["bay checks"] / len(wrong)).map("{:.0%}".format)
    return out, len(d)


def photos() -> tuple[pd.DataFrame, int]:
    """Errors on the local photos by cause, and the number of bays."""
    d = pd.read_csv("outputs/loop/local/bays.csv", keep_default_na=False)
    wrong = d[d["status"] != d["true_status"]]

    def cause(r) -> str:  # noqa: ANN001
        if int(r.truth) and not int(r.pred):
            return "A: parked car missed"
        if not int(r.truth) and int(r.pred):
            return "A: empty bay called occupied"
        reason = re.search(r"\((\w+)\)", r.bay_decision)
        if r.bay_read in ("", "none"):
            return "B: no plate found"
        if reason:
            return f"B: plate unclear, sent to a person ({reason.group(1)})"
        return "B: plate misread"

    out = wrong.apply(cause, axis=1).value_counts().rename_axis("cause").reset_index(name="bays")
    return out, len(d)


def plates() -> pd.DataFrame:
    """Model B's outcomes on the public plate test."""
    d = plate_rows("test")
    cause = d.apply(
        lambda r: (
            "right"
            if r.correct == "True" or r.correct is True
            else "plate not found"
            if r.reason == "plate_not_found"
            else f"sent to a person ({r.reason})"
            if r.reason
            else "misread"
        ),
        axis=1,
    )
    return cause.value_counts().rename_axis("outcome").reset_index(name="images")


def commands() -> pd.DataFrame:
    """Model C's frozen-test errors by cause, counted from `tiered_test.md`."""
    text = Path("outputs/commands/tiered_test.md").read_text()
    rows = {
        m.group(1): (
            int(m.group(2)),
            [float(x) if x != "-" else None for x in m.group(3).split(" | ")],
        )
        for m in re.finditer(r"^\| (\S+) \| (\d+) \| (.+) \|$", text, re.M)
    }
    n_all, (exact, dangerous, needless, *_) = rows["all"]
    clear = rows["kind=allow"][0] + rows["kind=remove"][0]
    return pd.DataFrame(
        [
            {
                "cause": "a clear command asked about again (needless question)",
                "commands": round(needless * clear),
            },
            {
                "cause": "  of which: new wording (action-word check)",
                "commands": round(rows["wording=unseen"][1][2] * rows["wording=unseen"][0]),
            },
            {
                "cause": "a wrong change put to the owner (dangerous)",
                "commands": round(dangerous * n_all),
            },
            {
                "cause": "an unclear command answered with the wrong question or reason",
                "commands": round((1 - rows["kind=review"][1][0]) * rows["kind=review"][0]),
            },
            {
                "cause": "another request not recognised as unsupported",
                "commands": round(
                    (1 - rows["kind=unsupported"][1][0]) * rows["kind=unsupported"][0]
                ),
            },
        ]
    )


FIXES = [
    (
        "Plate reader read one thin '1' as '111'",
        "rule: merge sideways-overlapping boxes",
        "outputs/plates/rule_evidence.md; final_results_before_safety_rules.md -> "
        "final_results.md: "
        "wrong reads 27.5% -> 19.2%",
    ),
    (
        "A Dubai plate read without its code letter",
        "rule: Dubai reads need a code, else ask",
        "same as above",
    ),
    (
        "A plate of a car further back read as the parked car's",
        "rule: a plate narrower than 10% of the bay goes to a person",
        "outputs/occupancy/local_night_1/findings.md",
    ),
    (
        "Empty bays at night called occupied (78 of 243 on night 1)",
        "adapt Model A on the owner's camera (night video 2)",
        "outputs/occupancy/adaptation_test.md: 78 -> 2",
    ),
    (
        "One-frame alerts while a car moves; 78 notifications in 10 min",
        "one decision per stay (10 s to confirm, majority plate)",
        "outputs/loop/video_night_1_stays.md (night 1): false alerts 4 -> 0, notifications "
        "78 -> 28 (public model frame by frame -> adapted model per stay)",
    ),
    (
        "Model C dropped 'tomorrow' from a time",
        "check: a day said must be in the time read",
        "outputs/commands/final_test.md (change after the test): 0 wrong proposals in the "
        "full loop",
    ),
    (
        "Model C's two models agreed on wrong changes",
        "a second model must agree; action-word and loose-number checks",
        "outputs/commands/dev_tuning.md, final_test.md: 1 dangerous of 160",
    ),
    (
        "The camera check flagged every frame 40% darker than usual",
        "measure sharpness on a contrast-normalised frame",
        "outputs/trust/robustness_images.md: 100% -> 2.5% of frames flagged at brightness x0.6",
    ),
    (
        "A plate gate tuned on public photos sent 30% of the owner's bays to a person",
        "re-choose the gate on the owner's camera (block 4)",
        "outputs/trust/costs.md; full system right answers 67% -> 84% on night 1",
    ),
    (
        "Platt scaling made Model A's confidence worse on held-out data",
        "keep Model A's raw probability (chosen on block 4 alone)",
        "outputs/trust/validation_choices.md: held-out ECE 0.011 raw vs 0.023 Platt",
    ),
]
REMAINING = [
    "A car standing across both bays: the bay holding half of it is called empty, and on the "
    "test night a car centred on the middle line was called EMPTY in both bays, so a car "
    "without a valid permit was missed (outputs/final_test/night_3.md).",
    "Model A is a specialist: worse on other car parks and on the unseen public site than the "
    "public-only model; a new camera needs a new set-up and new adaptation.",
    "Over-exposure and strong glare: the camera check catches only part of it (23-36%).",
    "Model C asks again about most commands in new wording (the action-word check), and one "
    "negation ('don't allow ... anymore') was read as a change.",
    "The plate reader cannot read about 8% of public test plates and misreads some codes at night.",
    "Evidence is small: one sealed test night of 24 minutes with two cars (and one seen night "
    "of 10 minutes); no daytime test on the owner's camera.",
]


def run() -> None:
    """Write the failure analysis to `failures.md`."""
    cam, n_cam = camera()
    pho, n_pho = photos()
    (OUT / "failures.md").write_text(
        "# Failure analysis\n\n"
        + __doc__.split("\n\n", 1)[1].rsplit("`just failures`", 1)[0].strip()
        + f"\n\n## 1. Owner's camera, the sealed test night 3 ({n_cam} scored bay checks; errors: "
        f"{int(cam['bay checks'].sum())})\n\n"
        + md(cam)
        + f"\n\n## 2. Other car parks' photos ({n_pho} bays; errors: {int(pho['bays'].sum())})\n\n"
        + md(pho)
        + "\n\n## 3. Model B, public plate test (all outcomes)\n\n"
        + md(plates())
        + "\n\n## 4. Model C, frozen test (160 commands)\n\n"
        + md(commands())
        + "\n\n## Fixes made, each tied to an observed failure\n\n"
        + md(pd.DataFrame(FIXES, columns=["failure seen", "fix", "evidence (before -> after)"]))
        + "\n\n## Failure modes that remain\n\n"
        + "\n".join(f"- {r}" for r in REMAINING)
        + "\n"
    )
    logger.info("Failure analysis -> {}", OUT / "failures.md")


def main() -> None:
    """Set up logging and run the failure analysis."""
    setup_logging(load_config().logging)
    run()


if __name__ == "__main__":
    main()
