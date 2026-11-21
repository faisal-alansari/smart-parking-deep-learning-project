"""Class list used for plate fine-tuning (48 classes).

The AddingUAE export has 51 classes. `exp` (3 boxes) and the two Umm Al Quwain
types are dropped: UAQ plates go straight to human review (decision 2026-11-07).
"""

SOURCE_DROP = ("exp", "new_am", "old_am")
PLATE = "plate"
CHARACTERS = tuple("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
# Emirate/style classes -> emirate name.
TYPE_TO_EMIRATE = {
    "new_DUBAI": "Dubai",
    "old_DUBAI": "Dubai",
    "new_abudabi": "Abu Dhabi",
    "old_abudabi": "Abu Dhabi",
    "old_sharka": "Sharjah",
    "new_fujairah": "Fujairah",
    "old_fujira": "Fujairah",
    "new_RAK": "Ras Al Khaimah",
    "old_RAK": "Ras Al Khaimah",
    "new_ajman": "Ajman",
    "old_ajman": "Ajman",
}


def target_names(source_names: list[str]) -> list[str]:
    """Training class names: the source order without the dropped classes."""
    return [n for n in source_names if n not in SOURCE_DROP]


def remap_table(source_names: list[str]) -> dict[int, int]:
    """Source class index -> training class index (dropped classes are absent)."""
    names = target_names(source_names)
    return {i: names.index(n) for i, n in enumerate(source_names) if n in names}
