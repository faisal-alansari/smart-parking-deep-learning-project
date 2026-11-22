"""Model C Step 4: download the pretrained candidates and measure them.

`--download` fetches each candidate at a pinned revision into `weights_dir` (local weights
only; nothing is fine-tuned). `--measure` loads each candidate in a fresh process and records
its parameter count (counted, not quoted), licence, disk size, memory and time per command on
the 60 dev commands, then writes `outputs/commands/candidates.md`.

Run: `just download-command-models`, then `just command-candidates`.
"""

import argparse
import json
import re
import resource
import subprocess
import sys
import time
from pathlib import Path

from loguru import logger
from pydantic import BaseModel

from smart_parking.common.config import CommandsConfig, load_config


class Weights(BaseModel):
    repo: str
    revision: str  # pinned commit, so a later download gets the same files
    files: list[str]


WEIGHTS: dict[str, Weights] = {
    "smollm2-135m": Weights(
        repo="HuggingFaceTB/SmolLM2-135M-Instruct",
        revision="12fd25f77366fa6b3b4b768ec3050bf629380bac",
        files=["config.json", "generation_config.json", "merges.txt", "model.safetensors",
               "special_tokens_map.json", "tokenizer.json", "tokenizer_config.json",
               "vocab.json", "README.md"],
    ),
    "flan-t5-small": Weights(
        repo="google/flan-t5-small",
        revision="0fc9ddf78a1e988dac52e2dac162b0ede4fd74ab",
        files=["config.json", "generation_config.json", "model.safetensors",
               "special_tokens_map.json", "spiece.model", "tokenizer.json",
               "tokenizer_config.json", "README.md"],
    ),
    "gliner-small-v2.1": Weights(
        repo="urchade/gliner_small-v2.1",
        revision="4e091416cf7c3481db542c2a3d26156916f3a47f",
        files=["gliner_config.json", "pytorch_model.bin", "README.md"],
    ),
    # GLiNER's backbone: only its config and tokenizer (the weights are inside GLiNER's file)
    "deberta-v3-small": Weights(
        repo="microsoft/deberta-v3-small",
        revision="a36c739020e01763fe789b4b85e2df55d6180012",
        files=["config.json", "spm.model", "tokenizer_config.json", "README.md"],
    ),
    "minilm-l6-v2": Weights(
        repo="sentence-transformers/all-MiniLM-L6-v2",
        revision="1110a243fdf4706b3f48f1d95db1a4f5529b4d41",
        files=["1_Pooling/config.json", "config.json", "config_sentence_transformers.json",
               "model.safetensors", "modules.json", "sentence_bert_config.json",
               "special_tokens_map.json", "tokenizer.json", "tokenizer_config.json",
               "vocab.txt", "README.md"],
    ),
}  # fmt: skip

# Each candidate parser and the weight folders it reads.
CANDIDATES: dict[str, list[str]] = {
    "smollm2": ["smollm2-135m"],
    "flan-t5": ["flan-t5-small"],
    "gliner-minilm": ["gliner-small-v2.1", "deberta-v3-small", "minilm-l6-v2"],
    "checked": ["gliner-small-v2.1", "deberta-v3-small", "minilm-l6-v2", "smollm2-135m"],
}


def download(cfg: CommandsConfig) -> None:
    from huggingface_hub import snapshot_download

    for name, w in WEIGHTS.items():
        path = Path(cfg.weights_dir) / name
        snapshot_download(w.repo, revision=w.revision, local_dir=path, allow_patterns=w.files)
        logger.info("{} -> {}", w.repo, path)
    # GLiNER names its backbone by Hub id; point it at the local copy so loading needs no
    # network (paths are relative to the project root, where `just` runs).
    config = Path(cfg.weights_dir) / "gliner-small-v2.1" / "gliner_config.json"
    data = json.loads(config.read_text())
    data["model_name"] = str(Path(cfg.weights_dir) / "deberta-v3-small")
    config.write_text(json.dumps(data, indent=2) + "\n")


def licence(path: Path) -> str:
    m = re.search(r"^license:\s*(\S+)", (path / "README.md").read_text(), flags=re.M)
    return m[1] if m else "unknown"


def disk_mb(path: Path) -> float:
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file()) / 2**20


def _peak_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20  # bytes on macOS


def probe(name: str, device: str) -> dict:
    """Load one candidate and time it on the dev commands (run in a fresh process)."""
    from datetime import datetime

    import gliner  # noqa: F401  (imported before measuring, so only the model is counted)
    import sentence_transformers  # noqa: F401
    import torch
    import transformers  # noqa: F401

    from smart_parking.commands.score import PARSERS, load_set

    cfg = load_config().commands.model_copy(update={"device": device})
    rows = load_set(cfg.data_dir / "dev.jsonl")
    base = _peak_mb()
    start = time.perf_counter()
    parser = PARSERS[name].load(cfg)
    load_s = time.perf_counter() - start
    loaded = _peak_mb()
    decide = getattr(parser, "decide", None)  # a parser with its own safety checks

    def answer(row: dict) -> None:
        decide(row, datetime.fromisoformat(row["now"])) if decide else parser(row)

    for row in rows[:3]:  # warm-up
        answer(row)
    times = []
    for row in rows:
        start = time.perf_counter()
        answer(row)
        if device == "mps":
            torch.mps.synchronize()
        times.append((time.perf_counter() - start) * 1000)
    times.sort()
    params = {type(m).__name__: sum(p.numel() for p in m.parameters()) for m in parser.models}
    return {
        "params": params,
        "load_s": load_s,
        "load_mb": loaded - base,
        "peak_mb": _peak_mb() - base,
        "ms_mean": sum(times) / len(times),
        "ms_p95": times[int(0.95 * (len(times) - 1))],
    }


def measure(cfg: CommandsConfig) -> str:
    rows = []
    for name, folders in CANDIDATES.items():
        got = {}
        for device in ("cpu", "mps"):
            out = subprocess.run(
                [sys.executable, "-m", "smart_parking.commands.candidates", "--probe", name,
                 "--device", device],
                capture_output=True, text=True, check=True,
            )  # fmt: skip
            got[device] = json.loads(out.stdout.strip().splitlines()[-1])
            logger.info("{} on {}: {}", name, device, got[device])
        paths = [Path(cfg.weights_dir) / f for f in folders]
        params = got["cpu"]["params"]
        cpu, mps = got["cpu"], got["mps"]
        rows.append(
            f"| {name} | {' + '.join(WEIGHTS[f].repo for f in folders)} | "
            + " + ".join(f"{p / 1e6:.1f}M" for p in params.values())
            + f" ({sum(params.values()) / 1e6:.1f}M) | "
            + ", ".join(sorted({licence(p) for p in paths}))
            + f" | {sum(disk_mb(p) for p in paths):.0f} | {cpu['load_mb']:.0f} | "
            f"{cpu['peak_mb']:.0f} | {cpu['ms_mean']:.0f} / {cpu['ms_p95']:.0f}"
            f" | {mps['ms_mean']:.0f} / {mps['ms_p95']:.0f} |"
        )
    head = (
        "# Model C candidates (Step 4)\n\n"
        "Measured on the owner's Mac (Apple M4 Max), Python 3.14, local weights at pinned "
        f"revisions, {cfg.threads} CPU threads. Parameters are counted from the loaded models. "
        "Memory is the growth in the process's peak resident memory on CPU: after loading, and "
        "after running the 60 dev commands (on MPS the weights sit in GPU memory, which this "
        "does not count). SmolLM2 and FLAN-T5 weights are read lazily from `.safetensors`, so "
        "their memory after load looks small: peak memory is the fair comparison. "
        "Time is per command on the 60 dev commands after 3 warm-up commands, "
        "including the candidate's own steps (mean / 95th percentile); loading is not "
        "included. Nothing is fine-tuned.\n\n"
        "| candidate | weights | parameters | licence | disk (MB) | memory after load (MB) | "
        "peak memory (MB) | CPU ms / p95 | MPS ms / p95 |\n|---|---|---|---|---|---|---|---|---|\n"
    )
    return head + "\n".join(rows) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--probe", choices=sorted(CANDIDATES), help=argparse.SUPPRESS)
    ap.add_argument("--device", default="cpu", help=argparse.SUPPRESS)
    args = ap.parse_args()
    cfg = load_config().commands
    if args.probe:
        logger.remove()  # stdout carries the result only
        sys.stdout.write(json.dumps(probe(args.probe, args.device)) + "\n")
        return
    if args.download:
        download(cfg)
    if args.measure:
        out = Path(cfg.results_dir) / "candidates.md"
        out.write_text(measure(cfg))
        logger.info("Candidate table -> {}", out)


if __name__ == "__main__":
    main()
