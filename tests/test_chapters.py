from __future__ import annotations

from app.chapters import _collect_page_text, split_by_toc, split_chapters
from app.models import TocItem, PageData


def _make_pages(count: int) -> list[PageData]:
    """Helper: create `count` pages with predictable text."""
    return [
        PageData(
            page_number=i + 1,
            text=f"content page {i + 1}",
            char_count=len(f"content page {i + 1}"),
        )
        for i in range(count)
    ]


class TestCollectPageText:
    def test_collects_range_inclusive(self) -> None:
        pages = _make_pages(5)
        result = _collect_page_text(pages, start_page=2, end_page=4)
        assert "content page 2" in result
        assert "content page 3" in result
        assert "content page 4" in result
        assert "content page 1" not in result
        assert "content page 5" not in result

    def test_single_page_range(self) -> None:
        pages = _make_pages(3)
        result = _collect_page_text(pages, start_page=2, end_page=2)
        assert result == "content page 2"

    def test_joins_with_double_newline(self) -> None:
        pages = _make_pages(3)
        result = _collect_page_text(pages, start_page=1, end_page=3)
        assert result == "content page 1\n\ncontent page 2\n\ncontent page 3"

    def test_no_pages_in_range(self) -> None:
        pages = _make_pages(3)
        result = _collect_page_text(pages, start_page=10, end_page=20)
        assert result == ""


class TestSplitByToc:
    def test_splits_three_chapters(self) -> None:
        pages = _make_pages(9)
        toc = [
            TocItem(level=1, title="Intro", page=1),
            TocItem(level=1, title="Middle", page=4),
            TocItem(level=1, title="End", page=7),
        ]

        chapters = split_by_toc(toc, pages, total_pages=9)

        assert len(chapters) == 3
        assert chapters[0].title == "Intro"
        assert chapters[0].start_page == 1
        assert chapters[0].end_page == 3
        assert chapters[1].title == "Middle"
        assert chapters[1].start_page == 4
        assert chapters[1].end_page == 6
        assert chapters[2].title == "End"
        assert chapters[2].start_page == 7
        assert chapters[2].end_page == 9

    def test_last_chapter_extends_to_total_pages(self) -> None:
        pages = _make_pages(10)
        toc = [
            TocItem(level=1, title="Chapter 1", page=1),
            TocItem(level=1, title="Chapter 2", page=5),
        ]

        chapters = split_by_toc(toc, pages, total_pages=10)

        assert chapters[-1].end_page == 10
        assert "content page 10" in chapters[-1].text_combined

    def test_single_toc_entry(self) -> None:
        pages = _make_pages(5)
        toc = [TocItem(level=1, title="Only Chapter", page=1)]

        chapters = split_by_toc(toc, pages, total_pages=5)

        assert len(chapters) == 1
        assert chapters[0].title == "Only Chapter"
        assert chapters[0].start_page == 1
        assert chapters[0].end_page == 5

    def test_empty_toc_returns_empty(self) -> None:
        pages = _make_pages(3)
        chapters = split_by_toc([], pages, total_pages=3)
        assert chapters == []

    def test_chapter_text_contains_correct_pages(self) -> None:
        pages = _make_pages(6)
        toc = [
            TocItem(level=1, title="A", page=1),
            TocItem(level=1, title="B", page=4),
        ]

        chapters = split_by_toc(toc, pages, total_pages=6)

        assert "content page 1" in chapters[0].text_combined
        assert "content page 3" in chapters[0].text_combined
        assert "content page 4" not in chapters[0].text_combined

        assert "content page 4" in chapters[1].text_combined
        assert "content page 6" in chapters[1].text_combined
        assert "content page 3" not in chapters[1].text_combined


class TestSplitChapters:
    def test_uses_toc_when_available(self) -> None:
        pages = _make_pages(4)
        toc = [
            TocItem(level=1, title="Part 1", page=1),
            TocItem(level=1, title="Part 2", page=3),
        ]

        chapters = split_chapters(toc, pages, total_pages=4)

        assert len(chapters) == 2
        assert chapters[0].title == "Part 1"
        assert chapters[1].title == "Part 2"

    def test_no_toc_returns_single_chapter(self) -> None:
        pages = _make_pages(5)

        chapters = split_chapters(None, pages, total_pages=5)

        assert len(chapters) == 1
        assert chapters[0].title == "Full Document"
        assert chapters[0].start_page == 1
        assert chapters[0].end_page == 5

    def test_empty_toc_returns_single_chapter(self) -> None:
        pages = _make_pages(3)

        chapters = split_chapters([], pages, total_pages=3)

        assert len(chapters) == 1
        assert chapters[0].title == "Full Document"
