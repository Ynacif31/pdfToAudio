from __future__ import annotations
from app.models import TocItem, PageData, ChapterData


def _collect_page_text(
    pages: list[PageData],
    start_page: int,
    end_page: int,
) -> str:
    """Join text from all pages between start_page and end_page (inclusive)."""
    return "\n\n".join(page.text for page in pages if start_page <= page.page_number <= end_page)

def split_by_toc(
    toc: list[TocItem],
    pages: list[PageData],
    total_pages: int,
) -> list[ChapterData]:
    """Split pages into chapters using TOC entries.
    Each TOC entry marks where a chapter starts.
    A chapter ends where the next one begins (or at the last page).
    """
    if not toc:
        return []
    
    chapters: list[ChapterData] = []

    for current, next_item in zip(toc, toc[1:]):
        start_page = current.page
        end_page = next_item.page - 1
        text = _collect_page_text(pages, start_page, end_page)

        chapters.append(
            ChapterData(
                title=current.title,
                start_page=start_page,
                end_page=end_page,
                text_combined=text,
            )
        )
    

    last_item = toc[-1]
    text = _collect_page_text(pages, last_item.page, total_pages)

    chapters.append(
        ChapterData(
            title=last_item.title,
            start_page=last_item.page,
            end_page=total_pages,
            text_combined=text,
        )
    )

    return chapters

def split_chapters(
    toc: list[TocItem] | None,
    pages: list[PageData],
    total_pages: int,
) -> list[ChapterData]:
    """Main entry point for chapter splitting.
    Uses TOC if available, otherwise returns all pages as a single chapter.
    """
    if toc: 
        return split_by_toc(toc, pages, total_pages)

    return [
        ChapterData(
            title="Full Document",
            start_page=1,
            end_page=total_pages,
            text_combined=_collect_page_text(pages, 1, total_pages),
        )
    ]