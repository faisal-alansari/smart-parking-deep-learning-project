"""Fixed rules that turn detected boxes into plate reads (emirate, text) or a review request.

The detector finds the plate, each character and the emirate type. These rules
group boxes into plates, read the characters in order, and check the result.

Rules added after the local night test (2026-11-20), each tied to an observed failure
(numbers reproduced by `just plate-rule-evidence`):
- duplicate boxes for one thin character ("1" read as "111") are merged when they
  overlap sideways by more than 50% of the narrower box. Only 36 of 81,622 real
  neighbouring pairs in the train/val labels do; on validation, 50% gave the best exact
  match of 70%, 60%, 50% and 40%;
- a Dubai read without a code letter is incomplete (0 of 4,302 main Dubai plates in the
  train/val labels lack one), so it goes to review;
- a plate narrower than 10% of the bay width belongs to a car further back, not the
  parked car (parked-car plates: 13-29%; background plates: 4-9%).
"""

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel

from smart_parking.plates.classes import CHARACTERS, PLATE, TYPE_TO_EMIRATE

MAX_CHARS = 7
MAX_LETTERS = 2
DUPLICATE_IOU = 0.5
DUPLICATE_SIDE_OVERLAP = 0.5
CODE_REQUIRED = {"Dubai"}
MIN_PLATE_BAY_WIDTH = 0.10


@dataclass
class Box:
    """One detection or ground-truth box in pixel corners."""

    name: str
    conf: float
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def cx(self) -> float:
        return (self.x0 + self.x1) / 2

    @property
    def cy(self) -> float:
        return (self.y0 + self.y1) / 2

    @property
    def h(self) -> float:
        return self.y1 - self.y0

    @property
    def area(self) -> float:
        return max(0.0, self.x1 - self.x0) * max(0.0, self.y1 - self.y0)


class PlateRead(BaseModel):
    """Structured result for one detected plate."""

    emirate: str | None
    text: str
    confidence: float
    decision: Literal["READ", "NEEDS_REVIEW"]
    reason: str | None
    box: tuple[float, float, float, float]


def iou(a: Box, b: Box) -> float:
    ix = max(0.0, min(a.x1, b.x1) - max(a.x0, b.x0))
    iy = max(0.0, min(a.y1, b.y1) - max(a.y0, b.y0))
    inter = ix * iy
    union = a.area + b.area - inter
    return inter / union if union > 0 else 0.0


def _inside(child: Box, parent: Box) -> bool:
    return parent.x0 <= child.cx <= parent.x1 and parent.y0 <= child.cy <= parent.y1


def _dedupe(boxes: list[Box]) -> list[Box]:
    """Keep the most confident box where two character boxes overlap strongly."""
    kept: list[Box] = []
    for b in sorted(boxes, key=lambda b: -b.conf):
        if all(iou(b, k) < DUPLICATE_IOU for k in kept):
            kept.append(b)
    return kept


def _same_spot(a: Box, b: Box) -> bool:
    """Two character boxes in one row that overlap sideways almost fully."""
    mean_h = (a.h + b.h) / 2
    if abs(a.cy - b.cy) >= 0.5 * mean_h:
        return False
    inter = max(0.0, min(a.x1, b.x1) - max(a.x0, b.x0))
    narrow = min(a.x1 - a.x0, b.x1 - b.x0)
    return narrow > 0 and inter / narrow > DUPLICATE_SIDE_OVERLAP


def _dedupe_chars(chars: list[Box]) -> list[Box]:
    """Keep the most confident box per character position."""
    kept: list[Box] = []
    for b in sorted(chars, key=lambda b: -b.conf):
        if all(iou(b, k) < DUPLICATE_IOU and not _same_spot(b, k) for k in kept):
            kept.append(b)
    return kept


def order_characters(chars: list[Box]) -> str:
    """Read one row left to right, or the top row then the bottom row."""
    if not chars:
        return ""
    ys = sorted(c.cy for c in chars)
    gaps = [b - a for a, b in zip(ys, ys[1:], strict=False)]
    mean_h = sum(c.h for c in chars) / len(chars)
    if gaps and max(gaps) > 0.6 * mean_h:
        cut = ys[gaps.index(max(gaps))]
        top = sorted((c for c in chars if c.cy <= cut), key=lambda c: c.cx)
        bottom = sorted((c for c in chars if c.cy > cut), key=lambda c: c.cx)
        return "".join(c.name for c in top + bottom)
    return "".join(c.name for c in sorted(chars, key=lambda c: c.cx))


def check_text(text: str, emirate: str | None = None) -> str | None:
    """Reason the text is not a valid UAE plate read, or None if it looks valid."""
    letters = sum(ch.isalpha() for ch in text)
    digits = sum(ch.isdigit() for ch in text)
    if len(text) < 2 or len(text) > MAX_CHARS:
        return "invalid_length"
    if digits == 0:
        return "no_digits"
    if letters > MAX_LETTERS:
        return "too_many_letters"
    if emirate in CODE_REQUIRED and letters == 0:
        return "missing_code"
    return None


def fits_bay(read: PlateRead, bay_width: float) -> bool:
    """Whether the plate is wide enough to belong to the car parked in the bay."""
    return (read.box[2] - read.box[0]) >= MIN_PLATE_BAY_WIDTH * bay_width


def read_plates(boxes: list[Box], min_conf: float) -> list[PlateRead]:
    """Group boxes into plates and return one structured read per plate."""
    boxes = [b for b in boxes if b.conf >= min_conf]
    plates = _dedupe([b for b in boxes if b.name == PLATE])
    others = [b for b in boxes if b.name != PLATE]
    reads = []
    for p in plates:
        mine = [b for b in others if _inside(b, p)]
        chars = _dedupe_chars([b for b in mine if b.name in CHARACTERS])
        types = sorted((b for b in mine if b.name in TYPE_TO_EMIRATE), key=lambda b: -b.conf)
        emirate = TYPE_TO_EMIRATE[types[0].name] if types else None
        text = order_characters(chars)
        confs = [p.conf, *(c.conf for c in chars), *(t.conf for t in types[:1])]
        reason = "no_emirate" if emirate is None else check_text(text, emirate)
        reads.append(
            PlateRead(
                emirate=emirate,
                text=text,
                confidence=min(confs),
                decision="NEEDS_REVIEW" if reason else "READ",
                reason=reason,
                box=(p.x0, p.y0, p.x1, p.y1),
            )
        )
    return reads
