from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pymupdf
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _build_sample_book(path: Path) -> None:
    """Create a small 2-page PDF with TOC for end-to-end coverage."""
    doc = pymupdf.open()
    try:
        page1 = doc.new_page()
        page1.insert_text(
            (72, 72),
            "Capitulo Um. Este e um texto curto para teste de audio.",
        )
        page1.insert_text((72, 100), "Aprender Python com projetos reais.")

        page2 = doc.new_page()
        page2.insert_text(
            (72, 72),
            "Capitulo Dois. Segunda parte do livro de exemplo.",
        )
        page2.insert_text((72, 100), "Gerando audiolivro a partir de PDF.")

        # Repeated header-like lines (cleanup should not break the flow)
        for page in doc:
            page.insert_text((72, 40), "Sample Book Header")

        doc.set_toc(
            [
                [1, "Capitulo Um", 1],
                [1, "Capitulo Dois", 2],
            ]
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(path)
    finally:
        doc.close()


def _is_mp3(path: Path) -> bool:
    data = path.read_bytes()
    if len(data) < 100:
        return False
    # edge-tts usually writes ID3-tagged MP3, sometimes raw MPEG frames
    return data.startswith(b"ID3") or data[:2] in (b"\xff\xfb", b"\xff\xfa", b"\xff\xf3")


@pytest.mark.e2e
def test_cli_pdf_to_audio_end_to_end(tmp_path: Path) -> None:
    pdf_path = tmp_path / "sample-book.pdf"
    out_dir = tmp_path / "out"
    extracted_path = out_dir / "extracted.json"
    chapters_path = out_dir / "chapters.json"
    audio_dir = out_dir / "audio"

    _build_sample_book(pdf_path)

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "main.py"),
            str(pdf_path),
            "-o",
            str(extracted_path),
            "--tts",
            "--voice",
            "pt-BR-FranciscaNeural",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )

    assert result.returncode == 0, (
        "CLI failed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    assert extracted_path.is_file(), "extracted.json was not created"
    assert chapters_path.is_file(), "chapters.json was not created"

    extracted = json.loads(extracted_path.read_text(encoding="utf-8"))
    chapters = json.loads(chapters_path.read_text(encoding="utf-8"))

    assert extracted["total_pages"] == 2
    assert extracted["file_name"] == "sample-book.pdf"
    assert len(extracted["toc"]) == 2
    assert chapters["chapter_count"] == 2
    assert chapters["chapters"][0]["title"] == "Capitulo Um"
    assert chapters["chapters"][1]["title"] == "Capitulo Dois"
    assert "texto curto" in chapters["chapters"][0]["text_combined"].lower()
    assert "segunda parte" in chapters["chapters"][1]["text_combined"].lower()

    playlist = audio_dir / "playlist.m3u"
    assert playlist.is_file(), "playlist.m3u was not created"

    mp3_files = sorted(audio_dir.glob("*.mp3"))
    assert len(mp3_files) == 2, f"expected 2 mp3 files, got {mp3_files}"

    for mp3 in mp3_files:
        assert _is_mp3(mp3), f"{mp3.name} does not look like a valid MP3"
        assert mp3.stat().st_size > 1000

    playlist_text = playlist.read_text(encoding="utf-8")
    assert playlist_text.startswith("#EXTM3U")
    for mp3 in mp3_files:
        assert mp3.name in playlist_text

    assert "Chapters: 2" in result.stdout
    assert "Generating audio" in result.stdout
