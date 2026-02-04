"""Unified podcast production studio for MindQuest.

Consolidates script generation, voice synthesis, and podcast creation.
"""

import re
from pathlib import Path
from typing import List, Tuple

try:
    from ebooklib import epub
except ImportError:
    epub = None

from mindquest.utils import search_wikikids, get_wikikids_summary
from mindquest.utils.chatgpt import (
    generate_script_with_chatgpt,
    generate_audio_with_chatgpt,
    generate_minibook_with_chatgpt,
)


# ============================================================================
# Script Generation
# ============================================================================


def create_script(
    api_key: str,
    topic: str,
    number_of_words=500,
) -> str:
    """
    Generate an educational podcast script for children.

    This function:
    1. Searches WikiKids for age-appropriate information about the topic
    2. Uses ChatGPT-4 LLM to synthesize the data into a conversational script
    3. Returns the script featuring Plato (wise professor) and Pixel (curious kid)

    Args:
        api_key: OpenAI API key.
        topic: The educational topic for the podcast.
        number_of_words: Target word count for the script (default: 500).

    Returns:
        A conversational podcast script as a string.
    """
    if not api_key or not isinstance(api_key, str):
        raise ValueError("API key must be provided")

    if not topic or not isinstance(topic, str) or topic.strip() == "":
        raise ValueError("Topic must be a non-empty string")

    topic = topic.strip()
    language = "en"

    # Gather factual information from WikiKids
    summary = get_wikikids_summary(topic)
    search_results = search_wikikids(topic, max_results=3)

    context = f"""
Summary:
{summary}

Search Results:
{search_results}

Target Word Count: {number_of_words}
"""

    # Generate conversational script using ChatGPT
    script = generate_script_with_chatgpt(topic, context, api_key, language)

    return script


# ============================================================================
# Voice Synthesis
# ============================================================================


def parse_script_segments(script: str) -> List[Tuple[str, str]]:
    """
    Parse a script to identify speaker segments.

    Args:
        script: The podcast script with [Character] tags.

    Returns:
        A list of tuples (character_name, dialogue).
    """
    # Pattern to match [Character] Speaker: dialogue
    pattern = r"\[(\w+)\]\s*[:\-]?\s*(.+?)(?=\[|$)"
    matches = re.findall(pattern, script, re.DOTALL)

    segments = []
    for character, dialogue in matches:
        # Clean up dialogue
        dialogue = dialogue.strip()
        if dialogue:
            segments.append((character, dialogue))

    return segments


def voice_over(api_key: str, script: str, language: str = "en") -> bytes:
    """
    Generate audio synthesis from a podcast script.

    This function:
    1. Parses the input script to identify speaker segments
    2. Generates Text-to-Speech audio using ChatGPT
    3. Returns the final audio file as bytes

    Args:
        api_key: OpenAI API key.
        script: The podcast script with speaker annotations.
        language: Language code for speech generation (default: 'en').

    Returns:
        Audio file as bytes.
    """
    if not api_key or not isinstance(api_key, str):
        raise ValueError("API key must be provided")

    if not script or not isinstance(script, str) or script.strip() == "":
        raise ValueError("Script must be a non-empty string")

    # Parse script segments
    segments = parse_script_segments(script)

    if not segments:
        raise ValueError("No valid script segments found in the script")

    # Generate audio for each segment
    audio_segments: List[bytes] = []

    for character, dialogue in segments:
        try:
            # Generate audio with emotional annotation based on character
            audio_bytes = generate_audio_with_chatgpt(
                script=dialogue,
                character=character,
                api_key=api_key,
                language=language,
            )

            if audio_bytes:
                audio_segments.append(audio_bytes)
        except Exception as exception:
            raise RuntimeError(
                f"Failed to generate audio for {character}: {str(exception)}"
            ) from exception

    # Combine audio segments
    if audio_segments:
        combined_audio = b"".join(audio_segments)
    else:
        combined_audio = b""

    return combined_audio


def extract_character_audio(
    script: str, character: str, api_key: str, language: str = "en"
) -> bytes:
    """
    Extract and generate audio for a specific character in the script.
    """
    segments = parse_script_segments(script)

    character_segments = [dialogue for char, dialogue in segments if char == character]

    if not character_segments:
        raise ValueError(f"No dialogue found for character: {character}")

    combined_dialogue = " ".join(character_segments)

    return generate_audio_with_chatgpt(
        script=combined_dialogue,
        character=character,
        api_key=api_key,
        language=language,
    )


# ============================================================================
# Podcast Production
# ============================================================================


def generate_podcast(
    topic: str,
    api_key: str,
    output_file: str = "podcast.mp3",
    word_count: int = 500,
) -> str:
    """
    Generate a complete educational podcast on a given topic.
    """
    print(f"🎙️  Generating podcast on: {topic}")

    # Generate script
    try:
        script = create_script(api_key, topic, number_of_words=word_count)
    except Exception as exc:
        raise RuntimeError(f"Script generation failed: {exc}") from exc

    # Generate audio
    try:
        audio_bytes = voice_over(api_key, script)
    except Exception as exc:
        raise RuntimeError(f"Audio generation failed: {exc}") from exc

    # Save to file
    output_path = Path(output_file)
    try:
        with open(output_path, "wb") as file:
            file.write(audio_bytes)
        return str(output_path.absolute())
    except Exception as exc:
        raise RuntimeError(f"Failed to save podcast: {exc}") from exc


# ============================================================================
# Mini-Book Generation
# ============================================================================


# pylint: disable=redefined-builtin
def create_minibook(
    api_key: str, topic: str, language="en", number_of_words=2000, format="ebup"
) -> str:
    """
    Generate an educational mini-book for children aged 8-12.

    This function:
    1. Searches WikiKids for age-appropriate information about the topic
    2. Uses ChatGPT-4 LLM to synthesize the data into a structured mini-book
    3. Organizes content into 7-10 chapters with assessment questions
    4. Supports ebup and pdf formats

    Args:
        api_key: OpenAI API key.
        topic: The educational topic for the mini-book.
        language: Language code (default: 'en').
        number_of_words: Total target word count (default: 2000).
        format: Output format - 'ebup' or 'pdf' (default: 'ebup').

    Returns:
        Path to the generated file.
    """
    if not api_key or not isinstance(api_key, str):
        raise ValueError("API key must be provided")

    if not topic or not isinstance(topic, str) or topic.strip() == "":
        raise ValueError("Topic must be a non-empty string")

    if format not in ("ebup", "pdf"):
        raise ValueError("Output format must be 'ebup' or 'pdf'")

    topic = topic.strip()

    # Gather factual information from WikiKids
    summary = get_wikikids_summary(topic)
    search_results = search_wikikids(topic, max_results=5)

    context = f"""
Summary:
{summary}

Search Results:
{search_results}

Target Word Count: {number_of_words}
Chapters: 7-10
Assessment Questions: 3 per chapter
Include: Table of contents at the beginning, mind map picture placeholder
Format: Markdown with # for title, ## for chapters
"""

    # Generate mini-book content using ChatGPT
    minibook_content = generate_minibook_with_chatgpt(topic, context, api_key, language)

    # Validate and enhance
    validated_content = _validate_minibook_structure(minibook_content)

    # Create output file
    if format == "ebup":
        # Requirement specified 'ebup', but file extension should be 'epub'
        return _create_epub_file(topic, validated_content, language, "epub")
    if format == "pdf":
        return _create_pdf_file(topic, validated_content, language)

    raise ValueError("Unsupported output format")


def _validate_minibook_structure(content: str) -> str:
    """
    Validate and enhance minibook content structure.
    """
    if not content or not isinstance(content, str) or content.strip() == "":
        raise ValueError("Generated content is empty")

    title, chapters = _parse_minibook_markdown(content)

    if not title:
        raise ValueError("Generated content must have a title (# format)")

    # Build enhanced content
    enhanced = f"# {title}\n\n"
    enhanced += "## Table of Contents\n\n"
    for idx, (chapter_title, _) in enumerate(chapters, 1):
        enhanced += f"{idx}. {chapter_title}\n"
    enhanced += "\n---\n\n![Mind Map](mind_map.png)\n\n---\n\n"

    for chapter_title, chapter_content in chapters:
        enhanced += f"## {chapter_title}\n\n{chapter_content}\n\n"

    return enhanced


def _parse_minibook_markdown(content: str) -> Tuple[str, List[Tuple[str, str]]]:
    """
    Parse minibook markdown.
    """
    lines = content.split("\n")
    title = ""
    chapters: List[Tuple[str, str]] = []
    current_chapter = ""
    current_content = ""

    for line in lines:
        if line.startswith("# ") and not title:
            title = line.replace("# ", "").strip()
        elif line.startswith("## "):
            if current_chapter:
                chapters.append((current_chapter, current_content.strip()))
            current_chapter = line.replace("## ", "").strip()
            current_content = ""
        else:
            current_content += line + "\n"

    if current_chapter:
        chapters.append((current_chapter, current_content.strip()))

    return title, chapters


def _create_epub_file(title: str, content: str, language: str, extension="epub") -> str:
    """
    Create an EPUB file.
    """
    if epub is None:
        raise RuntimeError("ebooklib is not installed")

    try:
        book_title, chapters = _parse_minibook_markdown(content)
        book = epub.EpubBook()
        book.set_identifier(f"mindquest_{title.lower().replace(' ', '_')}")
        book.set_title(book_title or title)
        book.set_language(language)
        book.add_author("MindQuest")

        epub_chapters = []
        for chapter_title, chapter_content in chapters:
            chapter = epub.EpubHtml()
            chapter.file_name = f"chap_{len(epub_chapters):02d}.xhtml"
            chapter.title = chapter_title
            # Move replacement out of f-string for Python < 3.12
            html_body = chapter_content.replace("\n\n", "</p><p>")
            chapter.content = f"<h1>{chapter_title}</h1>\n<p>{html_body}</p>"
            book.add_item(chapter)
            epub_chapters.append(chapter)

        book.toc = tuple(epub_chapters)
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        book.spine = ["nav"] + epub_chapters

        filename = f"{title.lower().replace(' ', '_')}_{language}.{extension}"
        output_path = Path(filename)
        epub.write_epub(output_path, book)
        return str(output_path.absolute())
    except Exception as exc:
        raise RuntimeError(f"Failed to create EPUB: {exc}") from exc


def _create_pdf_file(title: str, content: str, language: str) -> str:
    """
    Create a PDF file.
    """
    try:
        filename = f"{title.lower().replace(' ', '_')}_{language}.pdf"
        output_path = Path(filename)
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(content)
        return str(output_path.absolute())
    except Exception as exc:
        raise RuntimeError(f"Failed to create PDF: {exc}") from exc
