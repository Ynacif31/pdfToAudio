from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from app.models import ChapterData, ExtractedDocument


def output_dir_for(pdf_path: Path) -> Path:
    return Path("output") / pdf_path.stem


def default_output_path(pdf_path: Path) -> Path:
    return output_dir_for(pdf_path) / "extracted.json"


def default_chapters_path(pdf_path: Path) -> Path:
    return output_dir_for(pdf_path) / "chapters.json"


def chapters_path_beside(extracted_path: Path) -> Path:
    return extracted_path.parent / "chapters.json"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def save_to_json(data: ExtractedDocument, output_path: str) -> None:
    serializable: dict[str, object] = {
        "file_name": data.file_name,
        "total_pages": data.total_pages,
        "toc": [asdict(item) for item in data.toc],
        "pages": [asdict(page) for page in data.pages],
        "full_text": data.full_text,
    }
    _write_json(Path(output_path), serializable)


def save_chapters_to_json(chapters: list[ChapterData], output_path: str) -> None:
    serializable: dict[str, object] = {
        "chapter_count": len(chapters),
        "chapters": [asdict(ch) for ch in chapters],
    }
    _write_json(Path(output_path), serializable)
