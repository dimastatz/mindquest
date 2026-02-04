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
    generate_minibook_outline,
    generate_chapter_content,
    generate_cover_image_with_dalle,
    generate_mindmap_image_with_dalle,
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
    # Pattern to match [Character]: dialogue
    pattern = r"\[(\w+)\]:\s*(.+?)(?=\[|$)"
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
    script: str,
    character: str,
    api_key: str,
    language: str = "en",
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
    api_key: str,
    topic: str,
    language="en",
    number_of_chapters=7,
    format="ebup",
) -> str:
    """
    Generate an educational mini-book for children aged 8-12.

    Args:
        api_key: OpenAI API key.
        topic: The educational topic for the mini-book.
        language: Language code (default: 'en').
        number_of_chapters: Number of chapters (default: 7).
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
    print(f"📖 Starting mini-book generation for: {topic}")

    # Gather factual information from WikiKids
    summary = get_wikikids_summary(topic)
    search_results = search_wikikids(topic, max_results=5)

    context = f"Summary:\n{summary}\n\nSearch Results:\n{search_results}"

    # 1. Generate Outline
    print("📝 Generating outline...")
    outline_raw = generate_minibook_outline(
        topic, context, api_key, language, number_of_chapters
    )
    
    # Parse outline (assuming numbered list)
    chapter_titles = []
    for line in outline_raw.split('\n'):
        # Match "1. Title" or "1 Title"
        cleaned = re.sub(r'^\d+[\.\)]\s*', '', line).strip()
        if cleaned:
            chapter_titles.append(cleaned)
    
    # Limit to requested number if model halluncinated more
    chapter_titles = chapter_titles[:number_of_chapters]

    # 2. Generate Chapters (Iterative)
    chapters_data: List[Tuple[str, str]] = []
    print(f"✍️  Generating {len(chapter_titles)} chapters...")
    
    for title in chapter_titles:
        print(f"   - {title}")
        content = generate_chapter_content(topic, title, context, api_key, language)
        # Remove the Title line if the model included it, to avoid duplication
        # Simple heuristic: remove lines starting with # or ## that contain the title
        lines = content.split('\n')
        cleaned_lines = [l for l in lines if not (l.startswith('#') and title.lower() in l.lower())]
        cleaned_content = '\n'.join(cleaned_lines).strip()
        chapters_data.append((title, cleaned_content))

    # 3. Generate Images
    print("🎨 Generating cover image...")
    try:
        cover_image_bytes = generate_cover_image_with_dalle(topic, api_key)
    except Exception as exc:
        print(f"⚠️ Failed to generate cover image: {exc}")
        cover_image_bytes = None

    print("🧠 Generating mind map...")
    try:
        mind_map_bytes = generate_mindmap_image_with_dalle(topic, api_key)
    except Exception as exc:
        print(f"⚠️ Failed to generate mind map: {exc}")
        mind_map_bytes = None

    # 4. Create Output
    if format == "ebup":
        return _create_epub_file(
            topic, chapters_data, language, "epub", cover_image_bytes, mind_map_bytes
        )
    if format == "pdf":
        return _create_pdf_file(topic, chapters_data, language)

    raise ValueError("Unsupported output format")


def _create_epub_file(
    title: str,
    chapters: List[Tuple[str, str]],
    language: str,
    extension="epub",
    cover_image: bytes = None,
    mind_map_image: bytes = None,
) -> str:
    """
    Create an EPUB file from structured data.
    """
    if epub is None:
        raise RuntimeError("ebooklib is not installed")

    try:
        book = epub.EpubBook()
        book.set_identifier(f"mindquest_{title.lower().replace(' ', '_')}")
        book.set_title(title)
        book.set_language(language)
        book.add_author("MindQuest")

        if cover_image:
            book.set_cover("cover.jpg", cover_image)

        epub_chapters = []
        
        # Add Mind Map as the first "chapter" / Front Matter if it exists
        if mind_map_image:
            mm_item = epub.EpubItem(
                uid="mind_map_img",
                file_name="images/mind_map.png",
                media_type="image/png",
                content=mind_map_image,
            )
            book.add_item(mm_item)
            
            mm_page = epub.EpubHtml(title="Mind Map", file_name="mind_map.xhtml")
            mm_page.content = (
                "<h1>Mind Map</h1>"
                '<div style="text-align:center;">'
                '<img src="images/mind_map.png" alt="Mind Map" style="max-width:100%;"/>'
                "</div>"
            )
            book.add_item(mm_page)
            epub_chapters.append(mm_page)

        # Add Content Chapters
        for i, (chapter_title, chapter_content) in enumerate(chapters):
            chapter = epub.EpubHtml()
            chapter.file_name = f"chap_{i:02d}.xhtml"
            chapter.title = chapter_title
            
            # Convert basic markdown to HTML
            html_body = chapter_content.replace("\n\n", "</p><p>")
            # Handle headers
            html_body = re.sub(r'## (.*)', r'<h2>\1</h2>', html_body)
            html_body = re.sub(r'\*\*(.*)\*\*', r'<b>\1</b>', html_body)
            
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


def _create_pdf_file(
    title: str, 
    chapters: List[Tuple[str, str]], 
    language: str
) -> str:
    """
    Create a PDF file from structured data.
    """
    try:
        filename = f"{title.lower().replace(' ', '_')}_{language}.pdf"
        output_path = Path(filename)
        
        content = f"# {title}\n\n"
        for chap_title, chap_content in chapters:
            content += f"## {chap_title}\n\n{chap_content}\n\n"
            
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(content)
        return str(output_path.absolute())
    except Exception as exc:
        raise RuntimeError(f"Failed to create PDF: {exc}") from exc
