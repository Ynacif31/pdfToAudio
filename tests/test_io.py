from __future__ import annotations

import json
from pathlib import Path

from app.io import (
    chapters_path_beside,
    default_chapters_path,
    save_chapters_to_json,
)
from app.models import ChapterData


class TestIoPaths:
    def test_default_chapters_path(self) -> None:
        assert default_chapters_path(Path("livro.pdf")) == Path(
            "output/livro/chapters.json"
        )

    def test_chapters_path_beside_extracted(self) -> None:
        assert chapters_path_beside(Path("output/x/extracted.json")) == Path(
            "output/x/chapters.json"
        )


class TestSaveChapters:
    def test_writes_chapter_count_and_full_text(self, tmp_path: Path) -> None:
        chapters = [
            ChapterData(
                title="Intro",
                start_page=1,
                end_page=2,
                text_combined="Hello chapter",
            ),
        ]
        out = tmp_path / "chapters.json"
        save_chapters_to_json(chapters, str(out))

        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["chapter_count"] == 1
        assert data["chapters"][0]["title"] == "Intro"
        assert data["chapters"][0]["text_combined"] == "Hello chapter"
