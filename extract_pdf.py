from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

import pymupdf


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
    toc: List[TocItem]
    pages: List[PageData]
    full_text: str


def normalize_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf(pdf_path: str) -> ExtractedDocument:
    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_file}")

    doc = pymupdf.open(pdf_file)

    toc_items: List[TocItem] = []
    raw_toc = doc.get_toc() or []

    for item in raw_toc:
        if len(item) >= 3:
            level, title, page = item[:3]
            toc_items.append(
                TocItem(
                    level=int(level),
                    title=normalize_text(str(title)),
                    page=int(page),
                )
            )

    pages_data: List[PageData] = []
    full_text_parts: List[str] = []

    for page_index in range(len(doc)):
        page = doc.load_page(page_index)

        text = page.get_text("text", sort=True)
        text = normalize_text(text)

        pages_data.append(
            PageData(
                page_number=page_index + 1,
                text=text,
                char_count=len(text),
            )
        )

        full_text_parts.append(f"\n\n--- PAGE {page_index + 1} ---\n\n{text}")

    full_text = "".join(full_text_parts).strip()

    extracted = ExtractedDocument(
        file_name=pdf_file.name,
        total_pages=len(doc),
        toc=toc_items,
        pages=pages_data,
        full_text=full_text,
    )

    doc.close()
    return extracted


def save_extraction_to_json(data: ExtractedDocument, output_path: str) -> None:
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


if __name__ == "__main__":
    pdf_path = "CV-Ygor Nacif.pdf"
    output_path = "output/extracted.json"

    extracted = extract_pdf(pdf_path)
    save_extraction_to_json(extracted, output_path)

    print(f"Arquivo: {extracted.file_name}")
    print(f"Páginas: {extracted.total_pages}")
    print(f"Itens no TOC: {len(extracted.toc)}")
    print(f"JSON salvo em: {output_path}")