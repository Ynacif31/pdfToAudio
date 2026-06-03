from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TocItem:
    level: int
    title: str
    page: int


@dataclass
class PageData:
    page_number: int
    text: str
    char_count: int


@dataclass
class ExtractedDocument:
    file_name: str
    total_pages: int
    toc: list[TocItem]
    pages: list[PageData]
    full_text: str


@dataclass
class ChapterData:
    title: str
    start_page: int
    end_page: int
    text_combined: str
