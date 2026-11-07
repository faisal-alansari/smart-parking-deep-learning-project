import pandas as pd
import yaml

from smart_parking.common.config import PlateTrainConfig
from smart_parking.plates.train import _train_list


def test_train_subset_list_keeps_processed_paths(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    yolo = tmp_path / "yolo"
    (yolo / "train" / "images").mkdir(parents=True)
    names = [f"img{i}.jpg" for i in range(8)]
    for n in names:
        (raw / n).write_bytes(b"x")
        (yolo / "train" / "images" / n).symlink_to(raw / n)
    (yolo / "data.yaml").write_text(yaml.safe_dump({"train": "train/images", "nc": 48}))
    ledger = tmp_path / "ledger.csv"
    pd.DataFrame({"image": names, "split": "train", "family": ["a", "b"] * 4}).to_csv(ledger)
    cfg = PlateTrainConfig(yolo_dir=yolo, ledger_csv=ledger)

    data = yaml.safe_load(_train_list(cfg, 4, seed=42).read_text())
    paths = (tmp_path / "yolo" / "train_4.txt").read_text().splitlines()
    assert len(paths) == 4
    assert all("/yolo/train/images/" in p and "/raw/" not in p for p in paths)
    assert data["train"].endswith("train_4.txt")
