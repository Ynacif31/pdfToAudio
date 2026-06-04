from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.io import (
    chapters_path_beside,
    default_output_path,
    save_chapters_to_json,
    save_to_json,
)
from app.pipeline import process_pdf_file


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract text from a PDF and split into chapters when a TOC exists.",
    )
    parser.add_argument(
        "pdf",
        type=Path,
        help="Path to the PDF file to process",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output JSON path (default: output/<pdf-name>/extracted.json)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    pdf_path = args.pdf.resolve()

    if not pdf_path.is_file():
        print(f"Error: PDF not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    if pdf_path.suffix.lower() != ".pdf":
        print(f"Error: not a PDF file: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    output_path = (args.output or default_output_path(pdf_path)).resolve()

    print(f"Extracting: {pdf_path}")
    result = process_pdf_file(str(pdf_path))

    print(f"  Pages: {result.extracted.total_pages}")
    print(f"  TOC items: {len(result.extracted.toc)}")

    if result.repeated_lines:
        print(f"  Repeated lines found (headers/footers): {len(result.repeated_lines)}")
        for line in sorted(result.repeated_lines):
            print(f'    - "{line}"')

    print(f"  Chapters: {len(result.chapters)}")
    for i, ch in enumerate(result.chapters, start=1):
        print(
            f"    {i}. {ch.title} (pp. {ch.start_page}-{ch.end_page})"
            f" — {len(ch.text_combined)} chars"
        )

    chapters_path = chapters_path_beside(output_path)

    save_to_json(result.extracted, str(output_path))
    save_chapters_to_json(result.chapters, str(chapters_path))
    print(f"  JSON saved to: {output_path}")
    print(f"  Chapters JSON saved to: {chapters_path}")


if __name__ == "__main__":
    main()
