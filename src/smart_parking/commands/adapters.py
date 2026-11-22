"""Model C candidates: pretrained models, used without fine-tuning, that fill an `Extraction`.

Each adapter only extracts pieces of the command (action, plate numbers as said, end-time
phrase as said); the shared rules (`commands.rules.finish`) do the rest.

Copy-only decoding (SmolLM2, FLAN-T5): the two text generators may only answer in a fixed
shape, and every number or time they give must be copied word for word from the command,
so they cannot invent a plate number or an end time.

The worked examples below were written by hand in the dev set's wording only (allow / add /
let ... in / approve; remove / delete / take ... off). They are not copied from dev rows and
they avoid the test set's unseen wording, so the test set stays a fair check.
"""

import json
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

import regex

from smart_parking.commands.rules import NUMBER_WORDS, SCALES
from smart_parking.commands.schema import (
    Action,
    Extraction,
    NeedsReview,
    ParsedCommand,
    Result,
)
from smart_parking.common.config import CommandsConfig, load_config

ACTIONS = ("ALLOW", "REMOVE", "OTHER", "NONE")  # NONE: no clear allow or remove said

EXAMPLES: list[tuple[str, dict]] = [
    ("allow car 4821 until 9 pm", {"action": "ALLOW", "numbers": ["4821"], "time": "until 9 pm"}),
    ("please remove plate number 77310", {"action": "REMOVE", "numbers": ["77310"], "time": None}),
    ("let car seven two five in for three hours",
     {"action": "ALLOW", "numbers": ["seven two five"], "time": "for three hours"}),
    ("add 5 0 9 1 2 in bay 1 till tomorrow",
     {"action": "ALLOW", "numbers": ["5 0 9 1 2"], "time": "till tomorrow"}),
    ("delete car 60218 from bay two", {"action": "REMOVE", "numbers": ["60218"], "time": None}),
    ("approve car number 3305 thanks", {"action": "ALLOW", "numbers": ["3305"], "time": None}),
    ("hey take 912 off the list", {"action": "REMOVE", "numbers": ["912"], "time": None}),
    ("what cars are allowed today", {"action": "OTHER", "numbers": [], "time": None}),
    ("car 4410 until friday", {"action": "NONE", "numbers": ["4410"], "time": "until friday"}),
    ("allow my sister's car", {"action": "ALLOW", "numbers": [], "time": None}),
    ("add 12 and car 87", {"action": "ALLOW", "numbers": ["12", "87"], "time": None}),
]  # fmt: skip


# More examples per action for the MiniLM helper, which compares a command with the average
# of each action's examples (same dev wording only; written by hand).
ACTION_EXAMPLES: dict[str, list[str]] = {
    "ALLOW": [
        "allow car 4821 until 9 pm", "add 5 0 9 1 2 in bay 1 till tomorrow",
        "let car seven two five in for three hours", "approve car number 3305 thanks",
        "please allow plate 618", "okay add number 2290", "let plate 77 in",
        "hey approve 3 1 4 until friday",
    ],
    "REMOVE": [
        "please remove plate number 77310", "delete car 60218 from bay two",
        "hey take 912 off the list", "remove number 5521", "okay delete plate eight one two",
        "take car 4 4 0 off the list please",
    ],
    "OTHER": [
        "what cars are allowed today", "is plate 3310 parked", "good evening",
        "how long is car 52 allowed", "show the list",
    ],
    "NONE": ["car 4410 until friday", "plate number 918", "number 23 in bay 1", "car 66 tomorrow"],
}  # fmt: skip


def to_extraction(action: str | None, numbers: list[str], time: str | None) -> Extraction:
    """Map a candidate's raw answer to an `Extraction` (NONE or unknown -> no action)."""
    act = action if action in ("ALLOW", "REMOVE", "OTHER") else None
    nums = [n.strip(" .,") for n in numbers if n.strip(" .,")]
    t = time.strip(" .,") if time else None
    return Extraction(action=act, numbers=nums, time=t or None)


def split_numbers(span: str) -> list[str]:
    """One copied answer may hold several numbers: "12 and 87" -> ["12", "87"]."""
    return [p for p in regex.split(r"\s*(?:,|&|\band\b(?! car)|\band car\b)\s*", span) if p]


# ---- copy-only constrained decoding ---------------------------------------------------------


def constrained_generate(
    model, tok, prompt_ids, pieces: list[str], cands: list[int], state: Callable[[str], str],
    eos: int, max_new: int = 48,
) -> tuple[str, float]:  # fmt: skip
    """Greedy decoding where each step may only add a token that keeps `state(text)` valid.

    `state(s)` returns "bad", "partial" (a valid start) or "done" (a complete answer).
    `cands` are the token ids worth trying (pieces found in the command or the answer shape).
    An answer that does not end complete (no allowed token left, or too long) gives "".
    Also returns how sure the model was: the lowest probability it gave its chosen token,
    among the tokens allowed, over the steps where it had a real choice (1.0 if none).
    """
    import torch
    from transformers import LogitsProcessor, LogitsProcessorList

    start = prompt_ids.shape[1] if not model.config.is_encoder_decoder else 1
    sure = [1.0]

    class CopyOnly(LogitsProcessor):
        """Blocks every token that would break the answer shape and notes how sure the model
        is of its pick (greedy decoding picks the most likely allowed token)."""

        def __call__(self, ids: torch.Tensor, scores: torch.Tensor) -> torch.Tensor:
            s = "".join(pieces[i] for i in ids[0, start:].tolist())
            ok = [i for i in cands if state(s + pieces[i]) != "bad"]
            if state(s) == "done":
                ok.append(eos)
            ok = ok or [eos]
            masked = torch.full_like(scores, float("-inf"))
            masked[0, ok] = scores[0, ok]
            if len(ok) > 1:
                sure[0] = min(sure[0], float(masked[0].float().softmax(-1).max()))
            return masked

    out = model.generate(
        input_ids=prompt_ids, attention_mask=torch.ones_like(prompt_ids), max_new_tokens=max_new,
        do_sample=False, num_beams=1, logits_processor=LogitsProcessorList([CopyOnly()]),
        eos_token_id=eos, pad_token_id=tok.pad_token_id if tok.pad_token_id is not None else eos,
    )  # fmt: skip
    text = "".join(pieces[i] for i in out[0, start:].tolist() if i != eos)
    return (text, sure[0]) if state(text) == "done" else ("", 0.0)  # stuck or cut off


def token_pieces(tok) -> list[str]:
    """The text each token id adds (special tokens add nothing)."""
    special = set(tok.all_special_ids)
    pieces = []
    for i in range(len(tok)):
        if i in special:
            pieces.append("")
            continue
        t = tok.convert_ids_to_tokens(i)
        pieces.append(t.replace("▁", " ") if "▁" in t else tok.convert_tokens_to_string([t]))
    return pieces


def candidate_ids(pieces: list[str], allowed_text: str) -> list[int]:
    return [i for i, p in enumerate(pieces) if p and p in allowed_text]


def is_copy(value: str, text: str, closed: bool) -> bool:
    """Whether `value` is copied from whole words of `text` ("62" is not a copy from "626").

    An unfinished value only has to start at a word; a finished one must also end at one.
    """
    v = value.strip()
    if not v:
        return not closed
    end = r"(?![A-Za-z0-9])" if closed else ""
    return regex.search(r"(?<![A-Za-z0-9])" + regex.escape(v) + end, text) is not None


# ---- SmolLM2-135M-Instruct: an action question, then a JSON answer --------------------------

SMOL_ACTION_SYSTEM = (
    "Classify the parking command. Answer ALLOW if it asks to allow, add, let in or approve a "
    "car; REMOVE if it asks to remove, delete or take a car off the list; OTHER for a question "
    "or any other request; NONE if no allow or remove word is said."
)
SMOL_JSON_SYSTEM = (
    'You read a short spoken parking command and fill a JSON object. "numbers" lists each car '
    'plate number exactly as written. "time" is the end-time words exactly as written, or null. '
    "Ignore any bay. Copy words; never invent them."
)
# The answer starts after '{"numbers":' (the model writes ' ["' as one token, so the fixed
# start stops before it).
SMOL_PREFIX = '{"numbers":'
_VAL = r'"[^"]+"'
SMOL_JSON = regex.compile(rf' \[(?:{_VAL}(?:, {_VAL}){{0,2}})?\], "time": (?:null|{_VAL})\}}')
SMOL_SHAPE = ' ["x", "x"], "time": null}'


def smol_values(s: str) -> list[tuple[str, bool]]:
    """The copied values in a (possibly unfinished) answer, each with whether it is closed."""
    nums, sep, tail = s[2:].partition("]")
    values = [(m[1], m[2] == '"') for m in regex.finditer(r'"([^"]*)("?)', nums)]
    t = regex.match(r', "time": "([^"]*)("?)', tail) if sep else None
    return values + ([(t[1], t[2] == '"')] if t else [])


def smol_state(s: str, text: str) -> str:
    if not SMOL_JSON.fullmatch(s, partial=True):
        return "bad"
    if not all(is_copy(v, text, closed) for v, closed in smol_values(s)):
        return "bad"
    return "done" if SMOL_JSON.fullmatch(s) else "partial"


def parse_smol(s: str) -> tuple[list[str], str | None]:
    try:
        d = json.loads(SMOL_PREFIX + s)
    except json.JSONDecodeError:
        return [], None  # no valid answer: the shared rules ask the owner
    return d["numbers"], d["time"]


def option_state(s: str, options: list[str]) -> str:
    s = s.lstrip()
    if s in options:
        return "done"
    return "partial" if any(o.startswith(s) for o in options) else "bad"


class SmolLM:
    name = "smollm2-135m"

    def __init__(self, cfg: CommandsConfig) -> None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        torch.set_num_threads(cfg.threads)
        path = cfg.weights_dir / self.name
        self.tok = AutoTokenizer.from_pretrained(path)
        self.model = AutoModelForCausalLM.from_pretrained(path).to(cfg.device).eval()
        self.device = cfg.device
        self.pieces = token_pieces(self.tok)
        self.models = [self.model]

    def chat(self, system: str, shots: list[tuple[str, str]], text: str) -> str:
        msgs = [{"role": "system", "content": system}]
        for said, answer in shots:
            msgs += [{"role": "user", "content": said}, {"role": "assistant", "content": answer}]
        msgs.append({"role": "user", "content": text})
        return self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)

    def _generate(
        self, prompt: str, state: Callable[[str], str], allowed_text: str
    ) -> tuple[str, float]:
        ids = self.tok(prompt, return_tensors="pt").input_ids.to(self.device)
        cands = candidate_ids(self.pieces, allowed_text)
        eos = self.tok.eos_token_id
        return constrained_generate(self.model, self.tok, ids, self.pieces, cands, state, eos)

    def extract(self, row: dict) -> tuple[Extraction, dict[str, float]]:
        text = row["text"]
        shots = [(said, a["action"]) for said, a in EXAMPLES]
        action, action_sure = self._generate(
            self.chat(SMOL_ACTION_SYSTEM, shots, text),
            lambda s: option_state(s, list(ACTIONS)), " ".join(ACTIONS),
        )  # fmt: skip
        shots = [(said, json.dumps({"numbers": a["numbers"], "time": a["time"]}))
                 for said, a in EXAMPLES]  # fmt: skip
        answer, values_sure = self._generate(
            self.chat(SMOL_JSON_SYSTEM, shots, text) + SMOL_PREFIX,
            lambda s: smol_state(s, text), text + SMOL_SHAPE,
        )  # fmt: skip
        sure = {"action": action_sure, "values": values_sure}
        return to_extraction(action.strip(), *parse_smol(answer)), sure

    def __call__(self, row: dict) -> Extraction:
        return self.extract(row)[0]


# ---- FLAN-T5-Small: one short question per field --------------------------------------------

FLAN_ACTION = (
    'Command: "{text}"\nWhat does the command ask for?\nOPTIONS:\n- allow a car\n'
    "- remove a car\n- something else\n- unclear"
)
FLAN_ACTIONS = {"allow a car": "ALLOW", "remove a car": "REMOVE", "something else": "OTHER",
                "unclear": "NONE"}  # fmt: skip
FLAN_NUMBER = 'Command: "{text}"\nWhat is the car plate number? Copy it, or answer none.'
FLAN_TIME = 'Command: "{text}"\nUntil what time or for how long? Answer none if no time is given.'


def copy_state(s: str, text: str, none: str = "none") -> str:
    """An answer that is "none" or whole words copied from the command."""
    v = s.lstrip()
    if v == none:
        return "done"
    if v and none.startswith(v):
        return "partial"
    if not is_copy(v, text, closed=False):
        return "bad"
    return "done" if v and is_copy(v, text, closed=True) else "partial"


class FlanT5:
    name = "flan-t5-small"

    def __init__(self, cfg: CommandsConfig) -> None:
        import torch
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        torch.set_num_threads(cfg.threads)
        path = cfg.weights_dir / self.name
        self.tok = AutoTokenizer.from_pretrained(path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(path).to(cfg.device).eval()
        self.device = cfg.device
        self.pieces = token_pieces(self.tok)
        self.models = [self.model]

    def _ask(
        self, question: str, state: Callable[[str], str], allowed_text: str
    ) -> tuple[str, float]:
        ids = self.tok(question, return_tensors="pt").input_ids.to(self.device)
        cands = candidate_ids(self.pieces, allowed_text)
        out, sure = constrained_generate(
            self.model, self.tok, ids, self.pieces, cands, state, eos=self.tok.eos_token_id,
            max_new=24,
        )  # fmt: skip
        return out.strip(), sure

    def extract(self, row: dict) -> tuple[Extraction, dict[str, float]]:
        text = row["text"]
        opts = list(FLAN_ACTIONS)
        action, action_sure = self._ask(
            FLAN_ACTION.format(text=text), lambda s: option_state(s, opts), " ".join(opts)
        )
        number, number_sure = self._ask(
            FLAN_NUMBER.format(text=text), lambda s: copy_state(s, text), text + " none"
        )
        time, time_sure = self._ask(
            FLAN_TIME.format(text=text), lambda s: copy_state(s, text), text + " none"
        )
        numbers = [] if number in ("none", "") else split_numbers(number)
        ex = to_extraction(
            FLAN_ACTIONS.get(action), numbers, None if time in ("none", "") else time
        )
        return ex, {"action": action_sure, "number": number_sure, "time": time_sure}

    def __call__(self, row: dict) -> Extraction:
        return self.extract(row)[0]


# ---- GLiNER Small v2.1 (spans) + all-MiniLM-L6-v2 (action) ----------------------------------

GLINER_LABELS = ["plate number", "end time", "parking bay"]
GLINER_LOOK = 0.02  # spans down to this score are looked at, to see near misses


def merge_spans(spans: list[dict], text: str, label: str) -> list[str]:
    """Join spans of one label that touch (only spaces or commas between them).

    GLiNER often splits a number said digit by digit ("four zero six") into one span per word.
    """
    out: list[list[int]] = []
    for s in sorted((s for s in spans if s["label"] == label), key=lambda s: s["start"]):
        if out and regex.fullmatch(r"[\s,]*", text[out[-1][1] : s["start"]]):
            out[-1][1] = max(out[-1][1], s["end"])
        else:
            out.append([s["start"], s["end"]])
    return [text[a:b] for a, b in out]


def _is_number_word(w: str) -> bool:
    return w.isdigit() or w.lower() in NUMBER_WORDS or w.lower() in SCALES


def number_runs(spans: list[dict], text: str, label: str = "plate number") -> list[str]:
    """The spoken numbers that the found spans point at.

    A span is cut to its number words ("plate 35" -> "35") and grown to the whole run of
    number words around it, because GLiNER often finds only part of a number said digit by
    digit ("four zero six zero nine"). Spans pointing at the same run count once.
    """
    words = [(m.start(), m.end()) for m in regex.finditer(r"[A-Za-z']+|\d+", text)]
    runs: list[tuple[int, int]] = []  # word index ranges of consecutive number words
    i = 0
    while i < len(words):
        if _is_number_word(text[slice(*words[i])]):
            j = i
            while j + 1 < len(words) and _is_number_word(text[slice(*words[j + 1])]):
                j += 1
            runs.append((i, j))
            i = j + 1
        else:
            i += 1
    hit: list[tuple[int, int]] = []
    for s in sorted((s for s in spans if s["label"] == label), key=lambda s: s["start"]):
        for a, b in runs:
            if words[a][0] < s["end"] and s["start"] < words[b][1] and (a, b) not in hit:
                hit.append((a, b))
    return [text[words[a][0] : words[b][1]] for a, b in sorted(hit)]


class GlinerMiniLM:
    name = "gliner-minilm"

    def __init__(self, cfg: CommandsConfig) -> None:
        import torch
        from gliner import GLiNER
        from sentence_transformers import SentenceTransformer

        torch.set_num_threads(cfg.threads)
        self.cfg = cfg
        self.gliner = GLiNER.from_pretrained(
            str(cfg.weights_dir / "gliner-small-v2.1"), local_files_only=True, load_tokenizer=True
        ).to(cfg.device)
        self.gliner.eval()
        self.encoder = SentenceTransformer(str(cfg.weights_dir / "minilm-l6-v2"), device=cfg.device)
        self.labels = list(ACTION_EXAMPLES)
        protos = [
            self.encoder.encode(v, normalize_embeddings=True, convert_to_tensor=True).mean(0)
            for v in ACTION_EXAMPLES.values()
        ]
        self.protos = torch.nn.functional.normalize(torch.stack(protos), dim=1)
        self.models = [self.gliner, self.encoder]

    def action(self, text: str) -> tuple[str, float]:
        """The action whose average example is closest to the command, and its lead over the
        second closest (a small lead means MiniLM is unsure)."""
        vec = self.encoder.encode(text, normalize_embeddings=True, convert_to_tensor=True)
        sims = (self.protos @ vec).tolist()
        order = sorted(range(len(sims)), key=sims.__getitem__, reverse=True)
        return self.labels[order[0]], sims[order[0]] - sims[order[1]]

    def extract(self, row: dict) -> tuple[Extraction, dict[str, float]]:
        text = row["text"]
        th = self.cfg.gliner_threshold
        found = self.gliner.predict_entities(text, GLINER_LABELS, threshold=GLINER_LOOK)
        spans = [s for s in found if s["score"] >= th]
        used = [s["score"] for s in spans if s["label"] != "parking bay"]
        missed = [s for s in found if s["score"] < th and s["label"] != "parking bay"]
        numbers = number_runs(spans, text)
        times = merge_spans(spans, text, "end time")
        action, lead = self.action(text)
        sure = {
            "action_lead": lead,
            "span_min": min(used, default=1.0),  # the weakest number or time span used
            "near_miss": max((s["score"] for s in missed), default=0.0),  # best span not used
            "time_near_miss": max(
                (s["score"] for s in missed if s["label"] == "end time"), default=0.0
            ),  # an end time GLiNER half-saw but did not use
        }
        return to_extraction(action, numbers, " ".join(times) or None), sure

    def __call__(self, row: dict) -> Extraction:
        return self.extract(row)[0]


# ---- the safe combination: GLiNER + MiniLM answers, SmolLM2 checks every change ------------


class Checked:
    """GLiNER + MiniLM gives the answer; a permit change goes to the owner only if SmolLM2,
    reading the same command on its own, reaches exactly the same change. Otherwise the
    answer is NEEDS_REVIEW ("unsure").

    Also "unsure": an allow with no end time while GLiNER half-saw an end time (a score
    between `time_near_miss` and its cut-off), because a dropped end time turns into a
    permanent permit. Questions and reviews from GLiNER + MiniLM are kept as they are.
    SmolLM2 runs only when a change is proposed.
    """

    name = "checked"

    def __init__(self, cfg: CommandsConfig) -> None:
        self.cfg = cfg
        self.main = GlinerMiniLM(cfg)
        self.check = SmolLM(cfg)
        self.models = self.main.models + self.check.models

    def decide(self, row: dict, now: datetime) -> Result:
        from smart_parking.commands.rules import finish

        ex, sure = self.main.extract(row)
        result = finish(ex, now)
        change = result if isinstance(result, ParsedCommand) else getattr(result, "proposal", None)
        if change is None:
            return result  # a question or "unsupported": nothing to guard
        no_time = change.action is Action.ALLOW and change.until is None
        if no_time and sure["time_near_miss"] >= self.cfg.time_near_miss:
            return NeedsReview(reason="unsure")
        if finish(self.check(row), now) != result:
            return NeedsReview(reason="unsure")
        return result

    def __call__(self, row: dict) -> Extraction:
        return self.main(row)  # the extraction alone (the checks need `decide`)


class Lazy:
    """Load a candidate on first use, so registering it in `PARSERS` costs nothing."""

    def __init__(self, factory: Callable[[CommandsConfig], Callable[[dict], Extraction]]) -> None:
        self.factory = factory
        self.parser: Callable[[dict], Extraction] | None = None

    def load(self, cfg: CommandsConfig | None = None) -> Callable[[dict], Extraction]:
        if self.parser is None:
            self.parser = self.factory(cfg or load_config().commands)
        return self.parser

    def __call__(self, row: dict) -> Extraction:
        return self.load()(row)


def weights_present(cfg: CommandsConfig, names: list[str]) -> bool:
    return all((Path(cfg.weights_dir) / n).is_dir() for n in names)
