"""
Minimal stubs for mini-book and podcast pipeline.

Functions:
- create_minibook: Build a mini-book structure from a topic.
- generate_podcast_script: Turn chapter text into a podcast-friendly script.
- synthesize_podcast: Convert a script to audio using TTS.

These are stubs intended for future implementation and integration with
content generation and TTS services.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, TypedDict


class Chapter(TypedDict):
    """Functional-style chapter representation as a TypedDict."""

    title: str
    content: str
    questions: List[str]
    answers: List[str]


class MiniBook(TypedDict):
    """Functional-style mini-book container as a TypedDict."""

    topic: str
    language: str
    age_group: str
    title: str
    chapters: List[Chapter]


def create_minibook(
    topic: str,
    *,
    language: str = "en",
    age_group: str = "8-12",
    title: Optional[str] = None,
    chapters_count: int = 7,
    words_per_chapter: int = 2000,
) -> MiniBook:
    """
    Create a mini-book skeleton from a topic.

    Stub behavior:
    - Returns a MiniBook with `chapters_count` empty chapters and placeholders.
    - Intended to be backed by data sources (e.g., Simple Wikipedia) and LLM.

    Args:
            topic: Subject to cover.
            language: Target language (e.g., "en", "he").
            age_group: Target age range (e.g., "8-12", "6-8", "10-14"); default "8-12".
            title: Optional book title; defaults to "{topic} for Kids ({age_group})".
            chapters_count: Number of chapters; default 7.
            words_per_chapter: Target length per chapter; used by future implementation.

    Returns:
            MiniBook: a container with placeholder chapters.
    """
    book_title = title or f"{topic} for Kids ({age_group})"
    chapters: List[Chapter] = []
    for i in range(1, chapters_count + 1):
        ch_title = f"{topic}: Chapter {i}"
        ch_content = (
            "TODO: Generate approximately "
            f"{words_per_chapter} words covering subtopic {i} in {language}."
        )
        ch_questions = [
            "TODO: Question 1",
            "TODO: Question 2",
            "TODO: Question 3",
        ]
        ch_answers = [
            "TODO: Answer 1",
            "TODO: Answer 2",
            "TODO: Answer 3",
        ]
        chapters.append(
            {
                "title": ch_title,
                "content": ch_content,
                "questions": ch_questions,
                "answers": ch_answers,
            }
        )
    return {
        "topic": topic,
        "language": language,
        "age_group": age_group,
        "title": book_title,
        "chapters": chapters,
    }


def generate_podcast_script(
    chapter: Chapter,
    *,
    language: Optional[str] = None,
    narrator_style: str = "friendly",
    include_questions: bool = True,
) -> str:
    """
    Create a podcast script from a chapter.

    Stub behavior:
    - Formats the chapter into a simple narration script with optional Q&A.
    - Future implementation can add dialogs, sound cues, and pacing notes.

    Args:
            chapter: Chapter data source.
            language: Override language for script (defaults to the book's language when available).
            narrator_style: Style hint (e.g., "friendly", "excited").
            include_questions: If True, append the chapter questions at the end.

    Returns:
            str: A plain-text script suitable for TTS.
    """
    lang_hint = f"[{language}] " if language else ""
    lines: List[str] = []
    lines.append(
        f"{lang_hint}Narrator ({narrator_style}): Welcome! Today we explore '{chapter['title']}'."
    )
    lines.append("")
    lines.append("Narrator:")
    lines.append(chapter["content"].strip())
    lines.append("")
    if include_questions and chapter.get("questions"):
        lines.append("Narrator: Before we finish, here are three quick questions!")
        for idx, q in enumerate(chapter["questions"], 1):
            lines.append(f"Question {idx}: {q}")
    return "\n".join(lines).strip() + "\n"


def synthesize_podcast(
    script_text: str,
    *,
    voice: str = "kids_friendly",
    out_path: Path | str = "podcast.wav",
) -> Path:
    """
    Convert a script to audio using TTS.

    Stub behavior:
    - Writes the script to a sidecar .txt file and emits an empty .wav placeholder.
    - Intended to be replaced by a real TTS integration (e.g., Polly, Google TTS, ElevenLabs).

    Args:
            script_text: The narration script.
            voice: Voice preset or identifier.
            out_path: Target audio path.

    Returns:
            Path: Path to the synthesized audio file.
    """
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    # Sidecar script file
    script_sidecar = p.with_suffix(".txt")
    script_sidecar.write_text(f"VOICE={voice}\n\n{script_text}", encoding="utf-8")
    # Placeholder audio file
    if not p.exists():
        p.write_bytes(b"")
    return p


__all__ = [
    "Chapter",
    "MiniBook",
    "create_minibook",
    "generate_podcast_script",
    "synthesize_podcast",
]
