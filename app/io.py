from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from app.models import ExtractedDocument


def default_output_path(pdf_path: Path) -> Path:
    return Path("output") / pdf_path.stem / "extracted.json"


def save_to_json(data: ExtractedDocument, output_path: str) -> None:
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    serializable = {
        "file_name": data.file_name,
        "total_pages": data.total_pages,
        "toc": [asdict(item) for item in data.toc],
        "pages": [asdict(page) for page in data.pages],
        "full_text": data.full_text,
    }

    output_file.write_text(
        json.dumps(serializable, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
