from __future__ import annotations

from dataclasses import asdict, dataclass

from app.chapters import split_chapters
from app.cleanup import clean_pages, detect_repeated_lines
from app.extract import extract_pdf, extract_pdf_bytes
from app.models import ChapterData, ExtractedDocument


@dataclass
class PipelineResult:
    extracted: ExtractedDocument
    chapters: list[ChapterData]
    repeated_lines: set[str]


def _finalize_document(extracted: ExtractedDocument) -> PipelineResult:
    repeated = detect_repeated_lines(extracted.pages)
    cleaned_pages = clean_pages(extracted.pages)
    cleaned = ExtractedDocument(
        file_name=extracted.file_name,
        total_pages=extracted.total_pages,
        toc=extracted.toc,
        pages=cleaned_pages,
        full_text=extracted.full_text,
    )
    chapters = split_chapters(
        cleaned.toc,
        cleaned.pages,
        cleaned.total_pages,
    )
    return PipelineResult(
        extracted=cleaned,
        chapters=chapters,
        repeated_lines=repeated,
    )


def process_pdf_file(pdf_path: str) -> PipelineResult:
    extracted = extract_pdf(pdf_path)
    return _finalize_document(extracted)


def process_pdf_upload(data: bytes, file_name: str) -> PipelineResult:
    extracted = extract_pdf_bytes(data, file_name)
    return _finalize_document(extracted)


def pipeline_result_to_dict(result: PipelineResult) -> dict[str, object]:
    return {
        "file_name": result.extracted.file_name,
        "total_pages": result.extracted.total_pages,
        "toc": [asdict(item) for item in result.extracted.toc],
        "toc_count": len(result.extracted.toc),
        "repeated_lines_removed": sorted(result.repeated_lines),
        "chapters": [
            {
                "title": ch.title,
                "start_page": ch.start_page,
                "end_page": ch.end_page,
                "char_count": len(ch.text_combined),
                "text_preview": ch.text_combined[:200],
            }
            for ch in result.chapters
        ],
        "chapter_count": len(result.chapters),
    }
