from __future__ import annotations

import pymupdf

from app.extract import extract_pdf_bytes
from app.pipeline import process_pdf_upload


def _minimal_pdf_bytes() -> bytes:
    doc = pymupdf.open()
    try:
        page = doc.new_page()
        page.insert_text((72, 72), "Hello from test PDF")
        return doc.tobytes()
    finally:
        doc.close()


class TestProcessPdfUpload:
    def test_processes_uploaded_bytes(self) -> None:
        data = _minimal_pdf_bytes()
        result = process_pdf_upload(data, "sample.pdf")

        assert result.extracted.file_name == "sample.pdf"
        assert result.extracted.total_pages == 1
        assert len(result.chapters) == 1
        assert result.chapters[0].title == "Full Document"
        assert "Hello" in result.chapters[0].text_combined

    def test_extract_pdf_bytes_matches(self) -> None:
        data = _minimal_pdf_bytes()
        doc = extract_pdf_bytes(data, "x.pdf")
        assert doc.total_pages == 1
