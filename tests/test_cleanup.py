from __future__ import annotations

from app.cleanup import (
    _get_edge_lines,
    detect_repeated_lines,
    remove_lines,
    clean_pages,
)
from app.models import PageData


class TestGetEdgeLines:
    def test_returns_top_and_bottom(self) -> None:
        text = "line1\nline2\nline3\nline4\nline5\nline6\nline7"
        result = _get_edge_lines(text, count=2)
        assert result == ["line1", "line2", "line6", "line7"]

    def test_skips_empty_lines(self) -> None:
        text = "\n\nline1\n\nline2\n\n"
        result = _get_edge_lines(text, count=2)
        assert result == ["line1", "line2"]

    def test_short_text_no_bottom_overlap(self) -> None:
        text = "only one"
        result = _get_edge_lines(text, count=3)
        assert result == ["only one"]


class TestDetectRepeatedLines:
    def _make_pages(self, texts: list[str]) -> list[PageData]:
        return [
            PageData(page_number=i + 1, text=t, char_count=len(t))
            for i, t in enumerate(texts)
        ]

    def test_detects_header_present_on_all_pages(self) -> None:
        pages = self._make_pages([
            "HEADER\ncontent page 1\nfooter",
            "HEADER\ncontent page 2\nfooter",
            "HEADER\ncontent page 3\nfooter",
            "HEADER\ncontent page 4\nfooter",
            "HEADER\ncontent page 5\nfooter",
        ])
        repeated = detect_repeated_lines(pages, threshold=0.4)
        assert "HEADER" in repeated
        assert "footer" in repeated

    def test_does_not_flag_unique_content(self) -> None:
        pages = self._make_pages([
            "unique line A\ncontent 1",
            "unique line B\ncontent 2",
            "unique line C\ncontent 3",
        ])
        repeated = detect_repeated_lines(pages, threshold=0.4)
        assert len(repeated) == 0

    def test_ignores_very_short_lines(self) -> None:
        pages = self._make_pages([
            "ab\nreal content 1",
            "ab\nreal content 2",
            "ab\nreal content 3",
        ])
        repeated = detect_repeated_lines(pages, threshold=0.4)
        assert "ab" not in repeated


class TestRemoveLines:
    def test_removes_matching_lines(self) -> None:
        text = "HEADER\ncontent here\nFOOTER"
        result = remove_lines(text, {"HEADER", "FOOTER"})
        assert result == "content here"

    def test_preserves_non_matching_lines(self) -> None:
        text = "line1\nline2\nline3"
        result = remove_lines(text, {"other"})
        assert result == "line1\nline2\nline3"


class TestCleanPages:
    def _make_pages(self, texts: list[str]) -> list[PageData]:
        return [
            PageData(page_number=i + 1, text=t, char_count=len(t))
            for i, t in enumerate(texts)
        ]

    def test_removes_headers_from_pages(self) -> None:
        pages = self._make_pages([
            "HEADER\ncontent 1\nFOOTER",
            "HEADER\ncontent 2\nFOOTER",
            "HEADER\ncontent 3\nFOOTER",
            "HEADER\ncontent 4\nFOOTER",
            "HEADER\ncontent 5\nFOOTER",
        ])
        cleaned = clean_pages(pages, threshold=0.4)
        for page in cleaned:
            assert "HEADER" not in page.text
            assert "FOOTER" not in page.text
            assert "content" in page.text

    def test_returns_original_when_no_repeated_lines(self) -> None:
        pages = self._make_pages([
            "unique A\ncontent 1",
            "unique B\ncontent 2",
        ])
        cleaned = clean_pages(pages, threshold=0.4)
        assert cleaned is pages

    def test_updates_char_count(self) -> None:
        pages = self._make_pages([
            "HEADER\nshort\nFOOTER",
            "HEADER\nlonger text here\nFOOTER",
            "HEADER\nx\nFOOTER",
            "HEADER\ny\nFOOTER",
            "HEADER\nz\nFOOTER",
        ])
        cleaned = clean_pages(pages, threshold=0.4)
        for page in cleaned:
            assert page.char_count == len(page.text)
