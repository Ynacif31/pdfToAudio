from __future__ import annotations

import asyncio
import re
import shutil
from pathlib import Path

import edge_tts

from app.models import ChapterData

DEFAULT_VOICE = "pt-BR-FranciscaNeural"
DEFAULT_MAX_CHARS = 2800


def slugify_title(title: str, max_length: int = 60) -> str:
    slug = title.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug, flags=re.UNICODE)
    slug = re.sub(r"[\s_-]+", "-", slug).strip("-")
    return (slug or "chapter")[:max_length].strip("-") or "chapter"


def chunk_text(text: str, max_chars: int = DEFAULT_MAX_CHARS) -> list[str]:
    """Split text into chunks that fit edge-tts limits, preferring paragraph breaks."""
    cleaned = text.strip()
    if not cleaned:
        return []

    paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
    if not paragraphs:
        return [cleaned]

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for para in paragraphs:
        # Oversized single paragraph: hard-split by characters.
        if len(para) > max_chars:
            if current:
                chunks.append("\n\n".join(current))
                current = []
                current_len = 0
            for start in range(0, len(para), max_chars):
                chunks.append(para[start : start + max_chars])
            continue

        extra = len(para) + (2 if current else 0)
        if current and current_len + extra > max_chars:
            chunks.append("\n\n".join(current))
            current = [para]
            current_len = len(para)
        else:
            current.append(para)
            current_len += extra

    if current:
        chunks.append("\n\n".join(current))

    return chunks


def merge_mp3_files(parts: list[Path], output: Path) -> None:
    """Concatenate MP3 parts from the same encoder (edge-tts) into one file."""
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as out:
        for part in parts:
            out.write(part.read_bytes())


def write_m3u_playlist(audio_paths: list[Path], playlist_path: Path) -> None:
    lines = ["#EXTM3U"]
    for path in audio_paths:
        lines.append(path.name)
    playlist_path.parent.mkdir(parents=True, exist_ok=True)
    playlist_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


async def synthesize_text_to_file(
    text: str,
    output_path: Path,
    voice: str,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))


async def synthesize_chapter(
    chapter: ChapterData,
    index: int,
    output_dir: Path,
    voice: str,
) -> Path:
    slug = slugify_title(chapter.title)
    final_path = output_dir / f"{index:02d}-{slug}.mp3"
    chunks = chunk_text(chapter.text_combined)

    if not chunks:
        raise ValueError(f"Chapter '{chapter.title}' has no text to synthesize")

    if len(chunks) == 1:
        await synthesize_text_to_file(chunks[0], final_path, voice)
        return final_path

    temp_dir = output_dir / "_tmp" / f"{index:02d}-{slug}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    part_paths: list[Path] = []

    try:
        for i, chunk in enumerate(chunks, start=1):
            part = temp_dir / f"part{i:03d}.mp3"
            await synthesize_text_to_file(chunk, part, voice)
            part_paths.append(part)
        merge_mp3_files(part_paths, final_path)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    return final_path


async def synthesize_chapters(
    chapters: list[ChapterData],
    output_dir: Path,
    voice: str = DEFAULT_VOICE,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    for i, chapter in enumerate(chapters, start=1):
        if not chapter.text_combined.strip():
            continue
        path = await synthesize_chapter(chapter, i, output_dir, voice)
        paths.append(path)

    if paths:
        write_m3u_playlist(paths, output_dir / "playlist.m3u")

    return paths


def run_tts(
    chapters: list[ChapterData],
    output_dir: Path,
    voice: str = DEFAULT_VOICE,
) -> list[Path]:
    return asyncio.run(synthesize_chapters(chapters, output_dir, voice))
