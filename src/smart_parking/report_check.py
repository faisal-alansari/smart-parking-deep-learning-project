"""Check the report word limit without opening data or running any model."""

import json
import re
from pathlib import Path

from loguru import logger

from smart_parking.common.config import load_config
from smart_parking.common.log import setup_logging


def prose(text: str) -> str:
    """Exclude fenced diagrams, table rows, images and italic Table/Figure captions.

    Headings count conservatively as prose. Captions follow the existing report's Markdown
    convention, including captions that span multiple lines. Words are whitespace-separated.
    """
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"\*(?:Table|Figure) .*?\*", "", text, flags=re.S)
    return "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith(("|", "!["))
    )


def main() -> None:
    """Write the deterministic word count; Markdown page count requires a stated layout."""
    setup_logging(load_config().logging)
    path = Path("docs/final_report.md")
    words = len(prose(path.read_text()).split())
    result = {
        "report": str(path),
        "words_including_headings": words,
        "limit": 3000,
        "within_word_limit": words <= 3000,
        "exclusions": "tables, images, fenced diagrams and Table/Figure captions",
        "page_count": None,
        "page_note": "Markdown has no intrinsic pages; tables, figures and captions do not count.",
    }
    out = Path("outputs/audit/report_length.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    logger.info("Report: {} words (limit 3000); evidence -> {}", words, out)
    if words > 3000:
        raise SystemExit("The report exceeds the 3,000-word prose limit.")


if __name__ == "__main__":
    main()
