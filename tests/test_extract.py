from __future__ import annotations

from app.extract import normalize_text, build_full_text
from app.models import PageData


class TestNormalizeText:
    def test_replaces_non_breaking_spaces(self) -> None:
        assert normalize_text("hello\u00a0world") == "hello world"

    def test_collapses_multiple_spaces(self) -> None:
        assert normalize_text("hello    world") == "hello world"

    def test_collapses_tabs_and_spaces(self) -> None:
        assert normalize_text("hello \t\t world") == "hello world"

    def test_collapses_excessive_newlines(self) -> None:
        result = normalize_text("a\n\n\n\n\nb")
        assert result == "a\n\nb"

    def test_strips_whitespace(self) -> None:
        assert normalize_text("  hello  ") == "hello"

    def test_empty_string(self) -> None:
        assert normalize_text("") == ""

    def test_combined_normalization(self) -> None:
        raw = "  hello\u00a0\u00a0world  \n\n\n\nbye  "
        # \u00a0 → space, then multiple spaces collapse, but trailing space
        # before newline stays since we only collapse spaces (not space+newline)
        assert normalize_text(raw) == "hello world \n\nbye"


class TestBuildFullText:
    def test_single_page(self) -> None:
        pages = [PageData(page_number=1, text="hello", char_count=5)]
        result = build_full_text(pages)
        assert "--- PAGE 1 ---" in result
        assert "hello" in result

    def test_multiple_pages(self) -> None:
        pages = [
            PageData(page_number=1, text="first", char_count=5),
            PageData(page_number=2, text="second", char_count=6),
        ]
        result = build_full_text(pages)
        assert "--- PAGE 1 ---" in result
        assert "--- PAGE 2 ---" in result
        assert "first" in result
        assert "second" in result

    def test_empty_pages(self) -> None:
        result = build_full_text([])
        assert result == ""
