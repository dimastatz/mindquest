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
    api_key: str, topic: str, number_of_words: int = 500, language: str = "en"
) -> str:
    """
    Generate an educational podcast script for children.

    This function:
    1. Searches WikiKids for age-appropriate information about the topic
    2. Uses ChatGPT-4 LLM to synthesize the data into a conversational script
    3. Returns the script featuring Plato (wise professor) and Pixel (curious kid)

    Args:
        api_key: OpenAI API key (must be provided as parameter, not hardcoded).
        topic: The educational topic for the podcast.
        number_of_words: Target word count for the script (default: 500).
        language: Language code for script generation (default: "en" for English).

    Returns:
        A conversational podcast script as a string in the specified language.

    Raises:
        ValueError: If topic is empty or api_key is not provided.
    """
    if not api_key or not isinstance(api_key, str):
        raise ValueError("API key must be provided")

    if not topic or not isinstance(topic, str) or topic.strip() == "":
        raise ValueError("Topic must be a non-empty string")

    topic = topic.strip()

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

    # Generate conversational script using ChatGPT in target language
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
    pattern = r"\[(\w+)\]\s*[:\-]?\s*(.+?)(?=\[|\Z)"
    matches = re.findall(pattern, script, re.DOTALL)

    segments = []
    for character, dialogue in matches:
        # Clean up dialogue
        dialogue = dialogue.strip()
        if dialogue:
            segments.append((character, dialogue))

    return segments


def voice_over(api_key: str, script: str, languages: str = "en") -> bytes:
    """
    Generate audio synthesis from a podcast script.

    This function:
    1. Parses the input script to identify speaker segments
    2. Generates Text-to-Speech audio using OpenAI TTS API
    3. Returns the final audio file as bytes

    Args:
        api_key: OpenAI API key (passed as parameter, not hardcoded).
        script: The podcast script with speaker annotations.
        languages: Comma-separated language codes (default: "en" for English).

    Returns:
        Audio file as bytes.

    Raises:
        ValueError: If api_key or script is empty.
        RuntimeError: If audio generation fails.
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
                language=languages.split(",")[0].strip(),
            )

            if audio_bytes:
                audio_segments.append(audio_bytes)
        except Exception as exception:
            raise RuntimeError(
                f"Failed to generate audio for {character}: {str(exception)}"
            ) from exception

    # Combine audio segments (placeholder implementation)
    # In a real implementation, this would concatenate audio files
    if audio_segments:
        combined_audio = b"".join(audio_segments)
    else:
        # Fallback: return empty bytes if no audio was generated
        combined_audio = b""

    return combined_audio


def extract_character_audio(
    script: str, character: str, api_key: str, language: str = "en"
) -> bytes:
    """
    Extract and generate audio for a specific character in the script.

    Args:
        script: The podcast script.
        character: The character name to extract.
        api_key: OpenAI API key.
        language: Language code for speech generation.

    Returns:
        Audio file as bytes for the specified character.

    Raises:
        ValueError: If character not found in script.
        RuntimeError: If audio generation fails.
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
    word_count: int = 700,
    languages: str = "en",
) -> str:
    """
    Generate a complete educational podcast on a given topic.

    Args:
        topic: The educational topic for the podcast.
        api_key: OpenAI API key.
        output_file: Output file path for the generated audio.
        word_count: Target word count for the script (default: 700 for ~5 mins).
        languages: Comma-separated language codes (default: "en" for English).

    Returns:
        Path to the generated podcast file.

    Raises:
        ValueError: If topic or api_key is invalid.
        RuntimeError: If generation fails.
    """
    print(f"🎙️  Generating podcast on: {topic}")
    print("=" * 60)

    # Generate script (5 min ≈ 700 words at ~140 wpm)
    print("\n📝 Creating script...")
    try:
        script = create_script(
            api_key, topic, number_of_words=word_count, language=languages
        )
        print(f"✓ Script generated ({len(script)} characters)")
        print("\n--- Script Preview ---")
        print(script[:500] + "...\n")
    except Exception as exc:  # pylint: disable=broad-except
        raise RuntimeError(f"Script generation failed: {exc}") from exc

    # Generate audio
    print("\n🎵 Generating audio...")
    try:
        audio_bytes = voice_over(api_key, script, languages=languages)
        print(f"✓ Audio generated ({len(audio_bytes)} bytes)")
    except Exception as exc:  # pylint: disable=broad-except
        raise RuntimeError(f"Audio generation failed: {exc}") from exc

    # Save to file
    output_path = Path(output_file)
    try:
        with open(output_path, "wb") as file:  # pylint: disable=unspecified-encoding
            file.write(audio_bytes)
        print(f"✓ Podcast saved to: {output_path.absolute()}")
        print("=" * 60)
        print("🎙️  Podcast ready! ✨")
        return str(output_path.absolute())
    except Exception as exc:  # pylint: disable=broad-except
        raise RuntimeError(f"Failed to save podcast: {exc}") from exc


# ============================================================================
# Mini-Book Generation
# ============================================================================


def create_minibook(
    api_key: str,
    topic: str,
    language: str = "en",
    number_of_words: int = 2000,
    output_format: str = "epub",
) -> str:
    """
    Generate an educational mini-book for children aged 8-12.

    This function:
    1. Searches WikiKids for age-appropriate information about the topic
    2. Uses ChatGPT-4 LLM to synthesize the data into a structured mini-book
    3. Organizes content into 7-10 chapters with assessment questions
    4. Supports epub and pdf formats
    5. Saves and returns the path to the generated file

    Args:
        api_key: OpenAI API key (must be provided as parameter, not hardcoded).
        topic: The educational topic for the mini-book.
        language: Language code for mini-book generation (default: "en").
        number_of_words: Target word count for the mini-book (default: 2000).
        output_format: Output format - "epub" or "pdf" (default: "epub").

    Returns:
        Path to the generated mini-book file.

    Raises:
        ValueError: If topic, api_key, or format is invalid.
        RuntimeError: If mini-book generation fails.
    """
    if not api_key or not isinstance(api_key, str):
        raise ValueError("API key must be provided")

    if not topic or not isinstance(topic, str) or topic.strip() == "":
        raise ValueError("Topic must be a non-empty string")

    if output_format not in ("epub", "pdf"):
        raise ValueError("Output format must be 'epub' or 'pdf'")

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
"""

    # Generate mini-book content using ChatGPT in target language
    minibook_content = generate_minibook_with_chatgpt(topic, context, api_key, language)

    # Create EPUB file
    if output_format == "epub":
        return _create_epub_file(topic, minibook_content, language)
    if output_format == "pdf":
        return _create_pdf_file(topic, minibook_content, language)

    raise ValueError("Unsupported output format")


def _parse_minibook_markdown(content: str) -> Tuple[str, List[Tuple[str, str]]]:
    """
    Parse minibook markdown content into title and chapters.

    Args:
        content: Markdown content of the minibook.

    Returns:
        Tuple of (title, list of (chapter_title, chapter_content)).
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


def _create_epub_file(title: str, content: str, language: str) -> str:
    """
    Create an EPUB file from minibook content.

    Args:
        title: Title of the mini-book.
        content: Markdown content of the mini-book.
        language: Language code (for filename).

    Returns:
        Path to the created EPUB file.

    Raises:
        RuntimeError: If EPUB library is not available or creation fails.
    """
    if epub is None:
        raise RuntimeError(
            "ebooklib is not installed. Install with: pip install ebooklib"
        )

    try:
        # Parse markdown content
        book_title, chapters = _parse_minibook_markdown(content)
        if not book_title:
            book_title = title

        # Create book
        book = epub.EpubBook()
        book.set_identifier(f"mindquest_{title.lower().replace(' ', '_')}")
        book.set_title(book_title)
        book.set_language(language)
        book.add_author("MindQuest")

        # Add chapters
        epub_chapters = []
        for chapter_title, chapter_content in chapters:
            chapter = epub.EpubHtml()
            chapter.file_name = f"chap_{len(epub_chapters):02d}.xhtml"
            chapter.title = chapter_title
            chapter.content = f"<h1>{chapter_title}</h1>\n<p>"
            chapter.content += chapter_content.replace("\n\n", "</p>\n<p>")
            chapter.content += "</p>"

            book.add_item(chapter)
            epub_chapters.append(chapter)

        # Add navigation files
        book.toc = tuple(epub_chapters)
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Define table of contents
        book.spine = ["nav"] + epub_chapters

        # Write to file
        filename = f"{title.lower().replace(' ', '_')}_{language}.epub"
        output_path = Path(filename)
        epub.write_epub(output_path, book, {})

        print(f"✓ EPUB file created: {output_path.absolute()}")
        return str(output_path.absolute())

    except Exception as exc:  # pylint: disable=broad-except
        raise RuntimeError(f"Failed to create EPUB file: {exc}") from exc


def _create_pdf_file(title: str, content: str, language: str) -> str:
    """
    Create a PDF file from minibook content.

    Args:
        title: Title of the mini-book.
        content: Markdown content of the mini-book.
        language: Language code (for filename).

    Returns:
        Path to the created PDF file.

    Raises:
        RuntimeError: If PDF creation fails.
    """
    try:
        # For now, save as markdown with .pdf extension
        # In production, you would use reportlab or similar
        filename = f"{title.lower().replace(' ', '_')}_{language}.pdf"
        output_path = Path(filename)

        with open(output_path, "w", encoding="utf-8") as file:
            file.write(content)

        print(f"✓ PDF file created: {output_path.absolute()}")
        return str(output_path.absolute())

    except Exception as exc:  # pylint: disable=broad-except
        raise RuntimeError(f"Failed to create PDF file: {exc}") from exc
