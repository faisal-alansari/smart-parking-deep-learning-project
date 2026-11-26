"""Smart Parking demo: the owner's commands, the permit table, and the camera (`just demo`).

1. Owner commands: type a command; Model C proposes a change; accept, reject, or fix the
   fields. Only then does the permit table change (each decision is a feedback record).
2. Camera: run a sample folder (or uploaded photos and videos) through Models A and B, the
   permit table and the time check. One answer per car's stay, evidence frames, and a reason and
   guidance whenever a person must look. Mark any answer as wrong (a feedback record).
"""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from smart_parking.commands.owner import HumanFeedback
from smart_parking.commands.schema import NeedsReview, ParsedCommand, PermitTable, Unsupported
from smart_parking.output import DecisionFeedback

TZ = ZoneInfo("Asia/Dubai")
OUT = Path("outputs/runs/app")
SAMPLES = Path("samples")
STATUS_COLOUR = {
    "AUTHORIZED": "green",
    "POTENTIALLY_UNAUTHORIZED": "red",
    "NEEDS_REVIEW": "orange",
    "EMPTY": "gray",
}


@st.cache_resource
def model_c():  # noqa: ANN201
    """Model C (the tiered command reader), loaded once and cached."""
    from smart_parking.commands.score import PARSERS
    from smart_parking.common.config import load_config

    return PARSERS["tiered"].load(load_config().commands)


@st.cache_resource
def pipelines() -> dict:
    """A cached, initially empty dict of pipelines, one per occupancy model."""
    return {}  # filled on first use by run_folder, one per occupancy model


def state() -> st.session_state:
    """The session state, with an empty permit table and no pending command by default."""
    s = st.session_state
    s.setdefault("table", PermitTable())
    s.setdefault("pending", None)
    return s


def _save(record, name: str) -> None:  # noqa: ANN001
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open("a") as f:
        f.write(record.model_dump_json() + "\n")


def commands_tab() -> None:
    """Owner commands tab: Model C proposes a change; the owner accepts, fixes or rejects it."""
    s = state()
    st.subheader("Owner commands")
    st.caption(
        "For example: `allow car 33044`, `add 12345 until 6 pm`, `remove car 66705`. "
        "Model C proposes; nothing changes until you accept."
    )
    with st.form("command"):
        text = st.text_input("Command")
        now = datetime.now(TZ)
        if st.form_submit_button("Send") and text.strip():
            result = model_c().decide({"text": text}, now)
            s.pending = (text, now, result)
    if s.pending:
        text, now, result = s.pending
        proposal = (
            result if isinstance(result, ParsedCommand) else getattr(result, "proposal", None)
        )
        if proposal is None:
            reply = result.message if isinstance(result, Unsupported) else result.question
            st.warning(f"Model C asks: {reply}")
            if st.button("OK"):
                s.pending = None
                st.rerun()
            return
        question = s.table.confirmation(proposal)
        if isinstance(result, NeedsReview):
            question = f"{result.question} {question}"
        st.info(question)
        number = st.text_input("Number", proposal.number)
        until = st.text_input(
            "Until (YYYY-MM-DD HH:MM, empty = permanent)",
            f"{proposal.until:%Y-%m-%d %H:%M}" if proposal.until else "",
        )
        left, middle, right = st.columns(3)
        change = None
        if left.button("Accept"):
            change = proposal
        if middle.button("Accept with my fixes"):
            change = corrected(proposal, number, until)
            if change is None:
                st.error("That fix is not valid: use digits for the number and YYYY-MM-DD HH:MM.")
        if right.button("Reject"):
            _save(
                HumanFeedback(at=now, command=text, proposed=proposal, accepted=False),
                "command_feedback.jsonl",
            )
            s.pending = None
            st.rerun()
        if change is not None:
            _save(
                HumanFeedback(
                    at=now,
                    command=text,
                    proposed=proposal,
                    accepted=change == proposal,
                    corrected=None if change == proposal else change,
                ),
                "command_feedback.jsonl",
            )
            s.table.apply(change, confirm=lambda q: True)
            s.pending = None
            st.rerun()
    rows = [
        {
            "car number": p.number,
            "allowed until": f"{p.until:%a %d %b %H:%M}" if p.until else "permanent",
        }
        for p in s.table.permits.values()
    ]
    st.markdown("**Permit table**")
    st.dataframe(
        pd.DataFrame(rows) if rows else pd.DataFrame(columns=["car number", "allowed until"])
    )


def camera_tab() -> None:
    """Camera tab: run Models A and B on a sample folder or uploads and show the decisions."""
    from smart_parking.pipeline import run_folder

    s = state()
    st.subheader("Camera")
    folders = sorted(p for p in SAMPLES.iterdir() if p.is_dir())
    choice = st.selectbox("Sample folder", folders, format_func=lambda p: p.name)
    upload = st.file_uploader(
        "…or upload photos and videos (the owner's camera is assumed)", accept_multiple_files=True
    )
    use_commands = st.checkbox("Also apply the folder's commands.txt", value=False)
    if st.button("Run"):
        folder = choice
        if upload:
            folder = OUT / "upload" / datetime.now(TZ).strftime("%Y%m%d-%H%M%S")
            folder.mkdir(parents=True)
            for f in upload:
                (folder / f.name).write_bytes(f.getbuffer())
        elif not use_commands:  # run the media only, with the app's own permit table
            folder = _without_commands(choice)
        with st.spinner("Running Models A and B (first run loads the models)…"):
            s.result = run_folder(folder, 2.0, True, OUT, s.table, pipelines())
    result = s.get("result")
    if result is None:
        return
    st.caption(f"Camera: {result.camera}. Occupancy model: {result.occupancy_model}.")
    for p in result.problems:
        st.error(f"{p.source}: {p.guidance}")
    for c in result.commands:
        st.write(f"Command `{c.command}` → {c.reply}")
    if not result.decisions:
        return
    d = pd.DataFrame([x.model_dump() for x in result.decisions])
    st.markdown("**Answers that needed you** (each notification, with its evidence frame)")
    for x in result.decisions:
        if x.evidence is None:
            continue
        colour = STATUS_COLOUR[x.stay_status]
        cols = st.columns([1, 2])
        cols[0].image(x.evidence)
        cols[1].markdown(
            f"**{x.source}** {x.clock or ''} · {x.bay} bay · :{colour}[{x.stay_status}]"
        )
        if x.plate:
            cols[1].write(f"Plate: {x.plate} (confidence {x.plate_confidence})")
        if x.reason:
            cols[1].write(f"Reason: {x.reason}")
        if x.guidance:
            cols[1].write(x.guidance)
        key = f"{x.source}-{x.clock}-{x.bay}"
        right = cols[1].selectbox(
            "If this is wrong, what should it be?",
            ["(it is right)", "EMPTY", "AUTHORIZED", "POTENTIALLY_UNAUTHORIZED", "NEEDS_REVIEW"],
            key=key,
        )
        if right != "(it is right)" and cols[1].button("Save correction", key=key + "-save"):
            _save(
                DecisionFeedback(
                    at=datetime.now(TZ),
                    source=x.source,
                    clock=x.clock,
                    bay=x.bay,
                    system_said=x.stay_status,
                    owner_says=right,
                ),
                "decision_feedback.jsonl",
            )
            cols[1].success("Saved as feedback.")
    st.markdown("**Every decision**")
    st.dataframe(d.drop(columns=["guidance"]), height=300)


def _without_commands(folder: Path) -> Path:
    """A copy of the folder's links without commands.txt (the app's table is used instead)."""
    out = OUT / "folders" / folder.name
    out.mkdir(parents=True, exist_ok=True)
    for f in folder.iterdir():
        target = out / f.name
        if f.name != "commands.txt" and not target.exists():
            target.symlink_to(f.resolve())
    return out


def corrected(proposal: ParsedCommand, number: str, until: str) -> ParsedCommand | None:
    """The owner's fixed proposal, fully validated; None if a field is not valid."""
    try:
        when = datetime.fromisoformat(until.strip()).replace(tzinfo=TZ) if until.strip() else None
        return ParsedCommand.model_validate(
            {**proposal.model_dump(), "number": number.strip(), "until": when}
        )
    except ValueError:  # pydantic's ValidationError is a ValueError
        return None


def main() -> None:
    """Run the documented entry point with contextual, rotating application logs."""
    from smart_parking.common.config import load_config
    from smart_parking.common.log import setup_logging

    setup_logging(load_config().logging)
    st.set_page_config(page_title="Smart Parking", layout="wide")
    st.title("Smart Parking: two private bays, one camera")
    st.caption(
        "Model A: is a bay occupied (camera). Model B: whose plate is it (camera). "
        "Model C: the owner's spoken or typed permit commands (text). The permit table "
        "and the time (tabular) decide AUTHORIZED, POTENTIALLY_UNAUTHORIZED or NEEDS_REVIEW."
    )
    tab1, tab2 = st.tabs(["1. Owner commands", "2. Camera"])
    with tab1:
        commands_tab()
    with tab2:
        camera_tab()
    st.caption(
        "Feedback records are saved in outputs/runs/app/ (command_feedback.jsonl, "
        "decision_feedback.jsonl)."
    )


main()
