"""Parameter budget, counted from the loaded models (`just budget` -> outputs/budget.md).

Limits: no model above 200M parameters; the from-scratch model within 50M; pretrained and
fine-tuned models together within 1B. Also the fine-tuning item count against the 10,000 cap.
"""

import json

import pandas as pd
from loguru import logger

from smart_parking.common.config import load_config
from smart_parking.common.log import setup_logging
from smart_parking.loop import _md


def count(module) -> int:  # noqa: ANN001
    return sum(p.numel() for p in module.parameters())


def run() -> None:
    from ultralytics import YOLO

    from smart_parking.commands.score import PARSERS
    from smart_parking.occupancy.train import load_checkpoint

    cfg = load_config()
    occ, plates = cfg.occupancy, cfg.plates
    model_a = load_checkpoint(occ.checkpoint_dir / f"{occ.deploy}_s{occ.seeds[0]}.pt", "cpu")[0]
    model_b = YOLO(str(plates.checkpoint_dir / "final_s42.pt")).model
    tiered = PARSERS["tiered"].load(cfg.commands)
    gliner, minilm, smol = tiered.models
    rows = [
        (
            "A occupancy (OccupancyCNN)",
            "camera: is each bay occupied",
            "trained from scratch",
            count(model_a),
            50e6,
        ),
        (
            "B plate reader (YOLO11n)",
            "camera: plate, characters and emirate in the bay",
            "pretrained (COCO), fine-tuned",
            count(model_b),
            200e6,
        ),
        (
            "C1 GLiNER small v2.1 (DeBERTa-v3-small)",
            "text: plate number and end time in a command",
            "pretrained, not fine-tuned",
            count(gliner),
            200e6,
        ),
        (
            "C2 all-MiniLM-L6-v2",
            "text: allow, remove or other (closest examples)",
            "pretrained, not fine-tuned",
            count(minilm),
            200e6,
        ),
        (
            "C3 SmolLM2-135M-Instruct",
            "text: second opinion on action and number",
            "pretrained, not fine-tuned",
            count(smol),
            200e6,
        ),
    ]
    table = pd.DataFrame(rows, columns=["model", "role", "training", "parameters", "limit"])
    table["within limit"] = table["parameters"] <= table["limit"]
    pretrained = int(table.loc[table["training"] != "trained from scratch", "parameters"].sum())
    table["parameters"] = table["parameters"].map("{:,}".format)
    table["limit"] = table["limit"].map(lambda v: f"{v / 1e6:.0f}M")
    ledger = pd.read_csv(plates.ledger_csv) if plates.ledger_csv.exists() else None
    plate_items = len(ledger) if ledger is not None else 0
    crops = pd.read_csv("data/processed/video_crops/local_video_night_2_64.csv")
    local = len(crops) + len(pd.read_csv("data/processed/video_crops/local_video_night_1_64.csv"))
    items = pd.DataFrame(
        [
            {
                "items": "plate images used to fine-tune YOLO11n (train, validation and test)",
                "count": plate_items,
            },
            {
                "items": "local bay crops used to adapt Model A (night 2) and test it "
                "(night 1); scratch-model data, counted here to be safe",
                "count": local,
            },
            {"items": "total", "count": plate_items + local},
        ]
    )
    out = cfg.occupancy.results_dir.parent / "budget.md"
    out.write_text(
        "# Parameter budget and fine-tuning items\n\nCounted from the loaded models.\n\n"
        + _md(table)
        + f"\n\nPretrained and fine-tuned models together: {pretrained:,} parameters "
        f"(limit 1,000,000,000): {'within' if pretrained <= 1e9 else 'OVER'} the limit.\n\n"
        "## Fine-tuning items (cap 10,000)\n\n" + _md(items) + "\n"
    )
    (out.parent / "budget.json").write_text(json.dumps({"pretrained_total": pretrained}))
    logger.info("Budget -> {}", out)


def main() -> None:
    setup_logging(load_config().logging)
    run()


if __name__ == "__main__":
    main()
