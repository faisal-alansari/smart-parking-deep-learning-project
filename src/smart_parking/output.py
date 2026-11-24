"""The product's structured output (Pydantic): one record per bay decision, per command, and
per input that could not be used, each with a reason and plain guidance when a person must act.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

Status = Literal["EMPTY", "AUTHORIZED", "POTENTIALLY_UNAUTHORIZED", "NEEDS_REVIEW"]

GUIDANCE = {
    "camera_blocked": "The camera looks blocked or blinded. Check the lens and the light.",
    "unfamiliar_view": "This does not look like the configured camera. If it is a new camera, add "
    "bays.yaml with its bay boxes; if the camera moved, take a new snapshot.",
    "blurred_view": "The image is blurred. Clean the lens or check the focus.",
    "occupancy_unsure": "The system is unsure whether the bay is occupied. Look at the frame.",
    "no_plate_found": "A car is parked but no plate was found. Look at the evidence frame.",
    "plate_unclear": "The plate could not be read with confidence. Look at the evidence frame.",
    "unauthorized": "This car has no valid permit. Check it, or allow it with a command.",
    "unreadable_file": "The file could not be opened as a photo or a video.",
    "unsupported_file": "Only photos (.jpg, .jpeg, .png, .heic), videos (.mov, .mp4, .m4v), "
    "commands.txt and bays.yaml are read.",
    "bad_command_line": "Write one command per line, for example: "
    "`2026-11-22 09:05 | allow car 12345 until 6 pm`.",
    "bad_bays_file": "bays.yaml needs `boxes: {left: [x0, y0, x1, y1], right: [...]}` as "
    "fractions of the frame (0-1, x0 < x1, y0 < y1).",
    "empty_folder": "Put photos, videos or a commands.txt file in the folder.",
}
PLATE_REASONS = {"low_confidence", "missing_code", "invalid_length", "no_emirate",
                 "too_many_letters", "no_digits", "plate_too_small"}  # fmt: skip


def guidance(status: str, reason: str | None) -> str | None:
    """Plain guidance for a status that needs the owner, else None."""
    if status == "POTENTIALLY_UNAUTHORIZED":
        return GUIDANCE["unauthorized"]
    if status != "NEEDS_REVIEW":
        return None
    key = "plate_unclear" if reason in PLATE_REASONS else reason
    return GUIDANCE.get(key or "", "Look at the evidence frame.")


class BayDecision(BaseModel):
    """One bay in one photo or video frame."""

    model_config = ConfigDict(extra="forbid")

    source: str
    time: datetime
    clock: str | None = None  # position in a video (m:ss)
    bay: str
    status: Status  # this frame on its own
    stay_status: Status  # one decision per car's stay (videos); the same as status for photos
    occupied: bool | None  # None: the frame was not judged (camera check)
    occupancy_confidence: float | None  # Model A's mean probability of "occupied"
    plate: str | None = None
    plate_confidence: float | None = None  # calibrated (Platt) plate confidence
    reason: str | None = None  # why a person is asked
    guidance: str | None = None
    evidence: str | None = None  # path of the saved evidence frame, when one was saved


class CommandResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    time: datetime
    command: str
    reply: str


class InputProblem(BaseModel):
    """An input the product could not use, and what to do about it."""

    model_config = ConfigDict(extra="forbid")

    source: str
    reason: Literal["unreadable_file", "unsupported_file", "bad_command_line", "bad_bays_file",
                    "empty_folder"]  # fmt: skip
    detail: str = ""
    guidance: str


class RunResult(BaseModel):
    """Everything one folder run produced."""

    model_config = ConfigDict(extra="forbid")

    folder: str
    camera: str  # how the bays were set up
    occupancy_model: str  # "adapted" (owner's camera) or "final" (public data only)
    decisions: list[BayDecision] = []
    commands: list[CommandResult] = []
    problems: list[InputProblem] = []
