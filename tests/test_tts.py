from __future__ import annotations

from pathlib import Path

from app.models import ChapterData
from app.tts import (
    chunk_text,
    merge_mp3_files,
    slugify_title,
    write_m3u_playlist,
)


class TestSlugifyTitle:
    def test_basic_title(self) -> None:
        assert slugify_title("Capítulo 1: Introdução!") == "capítulo-1-introdução"

    def test_empty_falls_back(self) -> None:
        assert slugify_title("!!!") == "chapter"

    def test_truncates(self) -> None:
        long_title = "a" * 100
        assert len(slugify_title(long_title, max_length=20)) <= 20


class TestChunkText:
    def test_empty_returns_empty(self) -> None:
        assert chunk_text("   ") == []

    def test_short_text_single_chunk(self) -> None:
        assert chunk_text("Hello world") == ["Hello world"]

    def test_splits_on_paragraphs(self) -> None:
        text = "A" * 100 + "\n\n" + "B" * 100
        chunks = chunk_text(text, max_chars=150)
        assert len(chunks) == 2
        assert chunks[0] == "A" * 100
        assert chunks[1] == "B" * 100

    def test_hard_splits_oversized_paragraph(self) -> None:
        text = "x" * 50
        chunks = chunk_text(text, max_chars=20)
        assert chunks == ["x" * 20, "x" * 20, "x" * 10]


class TestMergeAndPlaylist:
    def test_merge_mp3_files(self, tmp_path: Path) -> None:
        part1 = tmp_path / "a.mp3"
        part2 = tmp_path / "b.mp3"
        part1.write_bytes(b"AAA")
        part2.write_bytes(b"BBB")
        out = tmp_path / "out.mp3"
        merge_mp3_files([part1, part2], out)
        assert out.read_bytes() == b"AAABBB"

    def test_write_m3u_playlist(self, tmp_path: Path) -> None:
        audio = [
            tmp_path / "01-intro.mp3",
            tmp_path / "02-end.mp3",
        ]
        playlist = tmp_path / "playlist.m3u"
        write_m3u_playlist(audio, playlist)
        content = playlist.read_text(encoding="utf-8")
        assert content.startswith("#EXTM3U\n")
        assert "01-intro.mp3" in content
        assert "02-end.mp3" in content


class TestSkipEmptyChapterLogic:
    def test_chunk_empty_chapter_text(self) -> None:
        chapter = ChapterData(
            title="Empty",
            start_page=1,
            end_page=1,
            text_combined="  \n  ",
        )
        assert chunk_text(chapter.text_combined) == []
