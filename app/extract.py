from __future__ import annotations

import re
from pathlib import Path

import pymupdf

from app.models import TocItem, PageData, ExtractedDocument


def normalize_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_toc(doc: pymupdf.Document) -> list[TocItem]:
    raw_toc = doc.get_toc() or []
    items: list[TocItem] = []

    for entry in raw_toc:
        if len(entry) >= 3:
            level, title, page = entry[:3]
            items.append(
                TocItem(
                    level=int(level),
                    title=normalize_text(str(title)),
                    page=int(page),
                )
            )

    return items


def extract_pages(doc: pymupdf.Document) -> list[PageData]:
    pages: list[PageData] = []

    for page_index in range(len(doc)):
        page = doc.load_page(page_index)
        text = normalize_text(page.get_text("text", sort=True))

        pages.append(
            PageData(
                page_number=page_index + 1,
                text=text,
                char_count=len(text),
            )
        )

    return pages


def build_full_text(pages: list[PageData]) -> str:
    parts = [
        f"\n\n--- PAGE {p.page_number} ---\n\n{p.text}"
        for p in pages
    ]
    return "".join(parts).strip()


def build_extracted_document(doc: pymupdf.Document, file_name: str) -> ExtractedDocument:
    toc = extract_toc(doc)
    pages = extract_pages(doc)
    full_text = build_full_text(pages)

    return ExtractedDocument(
        file_name=file_name,
        total_pages=len(doc),
        toc=toc,
        pages=pages,
        full_text=full_text,
    )


def extract_pdf(pdf_path: str) -> ExtractedDocument:
    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_file}")

    doc = pymupdf.open(pdf_file)

    try:
        return build_extracted_document(doc, pdf_file.name)
    finally:
        doc.close()


def extract_pdf_bytes(data: bytes, file_name: str) -> ExtractedDocument:
    if not data:
        raise ValueError("PDF data is empty")

    doc = pymupdf.open(stream=data, filetype="pdf")

    try:
        return build_extracted_document(doc, file_name)
    finally:
        doc.close()
