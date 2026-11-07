import pandas as pd
import pytest

from smart_parking.plates.data.split import check_no_leakage, select_and_split, similarity_groups


def _images(n_dubai=60, n_rak=14):
    rows = []
    for i in range(n_dubai + n_rak):
        fam = "Dubai" if i < n_dubai else "Ras Al Khaimah"
        rows.append(
            {
                "image": f"img{i}.jpg",
                "identity": f"name:P-{i}",
                "kind": "car_photo",
                "family": fam,
                "has_rare_char": False,
                "md5": f"m{i}",
            }
        )
    df = pd.DataFrame(rows)
    df.loc[1, "identity"] = df.loc[0, "identity"]  # same plate twice
    return df


def test_groups_join_same_identity_and_near_duplicates():
    df = _images()
    pairs = pd.DataFrame({"image_a": ["img5.jpg"], "image_b": ["img6.jpg"]})
    g = similarity_groups(df, pairs)
    assert g[0] == g[1]
    assert g[5] == g[6]
    assert g[2] != g[3]


def test_split_sizes_priority_and_no_leakage():
    df = _images()
    df["group"] = similarity_groups(df, pd.DataFrame(columns=["image_a", "image_b"]))
    out = select_and_split(df, extra_train=["img73.jpg"], total=40, val_size=8, test_size=8, seed=0)
    assert len(out) == 40
    assert (out["split"] == "val").sum() == 8 and (out["split"] == "test").sum() == 8
    assert set(df.loc[df["family"] == "Ras Al Khaimah", "image"]) <= set(out["image"])
    assert out.loc[out["image"] == "img73.jpg", "split"].item() == "train"
    check_no_leakage(out)


def test_leakage_check_catches_shared_identity():
    out = pd.DataFrame(
        {
            "identity": ["a", "a"],
            "group": ["g1", "g2"],
            "md5": ["x", "y"],
            "split": ["train", "test"],
        }
    )
    with pytest.raises(ValueError):
        check_no_leakage(out)
