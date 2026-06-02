from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from app.extract import extract_pdf
from app.cleanup import clean_pages, detect_repeated_lines
from app.models import ExtractedDocument


def save_to_json(data: ExtractedDocument, output_path: str) -> None:
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


def main() -> None:
    pdf_path = "CV-Ygor Nacif.pdf"
    output_path = "output/extracted.json"

    print(f"Extracting: {pdf_path}")
    extracted = extract_pdf(pdf_path)

    print(f"  Pages: {extracted.total_pages}")
    print(f"  TOC items: {len(extracted.toc)}")

    repeated = detect_repeated_lines(extracted.pages)
    if repeated:
        print(f"  Repeated lines found (headers/footers): {len(repeated)}")
        for line in sorted(repeated):
            print(f'    - "{line}"')

    cleaned_pages = clean_pages(extracted.pages)
    extracted = ExtractedDocument(
        file_name=extracted.file_name,
        total_pages=extracted.total_pages,
        toc=extracted.toc,
        pages=cleaned_pages,
        full_text=extracted.full_text,
    )

    save_to_json(extracted, output_path)
    print(f"  JSON saved to: {output_path}")


if __name__ == "__main__":
    main()
