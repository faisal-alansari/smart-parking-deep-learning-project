"""Rule-parser baseline for Model C: keywords and patterns, no model.

Written from the dev set's wording only (allow / add / let ... in / approve; remove /
delete / take ... off; questions and greetings as other requests; "bay N" removed;
until / till / for / today / tonight / tomorrow), so the test set's unseen wording
measures how it copes with new phrasing. A word it does not know is never corrected:
no known action word means no action.
"""

import re

from smart_parking.commands.rules import NUMBER_WORDS, SCALES
from smart_parking.commands.schema import OTHER, Action, Extraction

OTHER_REQUEST = re.compile(r"^(is|are|what|what's|whats|how|hello|hi|show|extend)\b")
REMOVE = re.compile(r"\b(remove|delete|take)\b")
ALLOW = re.compile(r"\b(allow|add|let|approve)\b")
BAY = re.compile(r"\b(?:(?:in|for|from)\s+)?bay\s+(?:number\s+)?(?:\d+|[a-z]+)\b")
TIME = re.compile(r"\b(until|till|til|for|today|tonight|tomorrow)\b")


def _number_spans(text: str) -> list[str]:
    """Runs of number tokens: "car 1 2 3 and 45" -> ["1 2 3", "45"]."""
    spans, current = [], []
    for tok in re.findall(r"[a-z']+|\d+", text):
        is_number = (
            tok.isdigit() or tok in SCALES or (tok in NUMBER_WORDS and (tok != "oh" or current))
        )
        if is_number:
            current.append(tok)
        elif current:
            spans.append(" ".join(current))
            current = []
    if current:
        spans.append(" ".join(current))
    return spans


def extract(text: str) -> Extraction:
    """Rule parser: OTHER for other requests, else the action, numbers and end time."""
    t = re.sub(r"[,!?]|\.(?=\s|$)", " ", text.lower()).strip()
    if OTHER_REQUEST.match(t):
        return Extraction(action=OTHER)
    action = Action.REMOVE if REMOVE.search(t) else Action.ALLOW if ALLOW.search(t) else None
    t = BAY.sub(" ", t)  # permits are not tied to a bay
    time = None
    m = TIME.search(t)
    if m:
        time = t[m.start() :].strip()
        t = t[: m.start()]
    return Extraction(action=action, numbers=_number_spans(t), time=time)
