from __future__ import annotations

from collections import Counter

from app.models import PageData


def _get_edge_lines(text: str, count: int = 3) -> list[str]:
    """Return the first and last `count` non-empty lines from text."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    top = lines[:count]
    bottom = lines[-count:] if len(lines) > count else []
    return top + bottom


def detect_repeated_lines(
    pages: list[PageData],
    threshold: float = 0.4,
    edge_lines: int = 3,
) -> set[str]:
    """Find lines that repeat on more than `threshold` fraction of pages.

    Only checks the first/last `edge_lines` lines of each page,
    since headers and footers live at the edges.
    """
    line_counts: Counter[str] = Counter()

    for page in pages:
        unique_edge = set(_get_edge_lines(page.text, count=edge_lines))
        for line in unique_edge:
            if len(line) > 2:
                line_counts[line] += 1

    min_occurrences = max(2, int(len(pages) * threshold))

    return {
        line for line, count in line_counts.items()
        if count >= min_occurrences
    }


def remove_lines(text: str, lines_to_remove: set[str]) -> str:
    """Remove lines that match the repeated set."""
    cleaned = [
        line for line in text.split("\n")
        if line.strip() not in lines_to_remove
    ]
    return "\n".join(cleaned).strip()


def clean_pages(
    pages: list[PageData],
    threshold: float = 0.4,
) -> list[PageData]:
    """Detect repeated headers/footers and remove them from all pages."""
    repeated = detect_repeated_lines(pages, threshold=threshold)

    if not repeated:
        return pages

    cleaned: list[PageData] = []

    for page in pages:
        clean_text = remove_lines(page.text, repeated)
        cleaned.append(
            PageData(
                page_number=page.page_number,
                text=clean_text,
                char_count=len(clean_text),
            )
        )

    return cleaned
