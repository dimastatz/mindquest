"""Comprehensive test suite for MindQuest project."""

from unittest.mock import patch, MagicMock
import pytest
import requests
from mindquest.studio import (
    create_script,
    voice_over,
    parse_script_segments,
    extract_character_audio,
    generate_podcast,
    create_minibook,
    _parse_minibook_markdown,
    _create_epub_file,
    _create_pdf_file,
)
from mindquest.utils import search_wikikids, get_wikikids_summary
from mindquest.utils.chatgpt import (
    generate_script_with_chatgpt,
    generate_audio_with_chatgpt,
    generate_minibook_with_chatgpt,
)
from mindquest.types import CharacterProfile, PLATO, PIXEL


# ============================================================================
# Script Generation Tests
# ============================================================================


def test_create_script_valid_inputs():
    """Test script creation with valid inputs."""
    with patch("mindquest.studio.get_wikikids_summary") as mock_summary, patch(
        "mindquest.studio.search_wikikids"
    ) as mock_search, patch(
        "mindquest.studio.generate_script_with_chatgpt"
    ) as mock_generate:
        mock_summary.return_value = "Solar system summary"
        mock_search.return_value = "Solar system results"
        mock_generate.return_value = "[Plato]: Info\n[Pixel]: Cool!"

        result = create_script("test-key", "Solar System")

        assert isinstance(result, str)
        assert len(result) > 0
        assert mock_generate.call_args[0][3] == "en"


def test_create_script_with_word_count():
    """Test script creation with specific word count."""
    with patch("mindquest.studio.get_wikikids_summary") as mock_summary, patch(
        "mindquest.studio.search_wikikids"
    ) as mock_search, patch(
        "mindquest.studio.generate_script_with_chatgpt"
    ) as mock_generate:
        mock_summary.return_value = "Summary"
        mock_search.return_value = "Results"
        mock_generate.return_value = "Script"

        create_script("key", "Topic", number_of_words=1000)
        assert mock_generate.call_args is not None


def test_create_script_with_language():
    """Test script creation with specific language."""
    with patch("mindquest.studio.get_wikikids_summary") as mock_summary, patch(
        "mindquest.studio.search_wikikids"
    ) as mock_search, patch(
        "mindquest.studio.generate_script_with_chatgpt"
    ) as mock_generate:
        mock_summary.return_value = "Summary"
        mock_search.return_value = "Results"
        mock_generate.return_value = "Script"

        create_script("key", "Topic", language="he")
        assert mock_generate.call_args[0][3] == "he"


def test_create_script_empty_topic():
    """Test script creation with empty topic raises ValueError."""
    with pytest.raises(ValueError, match="Topic must be a non-empty string"):
        create_script("key", "")


def test_create_script_none_topic():
    """Test script creation with None topic raises ValueError."""
    with pytest.raises(ValueError, match="Topic must be a non-empty string"):
        create_script("key", None)


def test_create_script_missing_api_key():
    """Test script creation without API key raises ValueError."""
    with pytest.raises(ValueError, match="API key must be provided"):
        create_script(None, "Topic")


def test_create_script_none_api_key():
    """Test script creation with None API key raises ValueError."""
    with pytest.raises(ValueError, match="API key must be provided"):
        create_script(None, "Topic")


# ============================================================================
# ChatGPT Utility Tests
# ============================================================================


def test_generate_script_with_chatgpt():
    """Test script generation with ChatGPT."""
    with patch("mindquest.utils.chatgpt.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "[Plato]: Hello\n[Pixel]: Hi!"
        mock_client.chat.completions.create.return_value = mock_response

        result = generate_script_with_chatgpt("Topic", "Context", "key")
        assert isinstance(result, str)
        assert len(result) > 0


def test_generate_script_api_error():
    """Test script generation handles API errors."""
    with patch("mindquest.utils.chatgpt.OpenAI") as mock_openai:
        mock_openai.return_value.chat.completions.create.side_effect = Exception(
            "API Error"
        )

        with pytest.raises(RuntimeError, match="Failed to generate script"):
            generate_script_with_chatgpt("Topic", "Context", "key")


def test_generate_audio_with_chatgpt():
    """Test audio generation with ChatGPT."""
    with patch("mindquest.utils.chatgpt.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_audio = MagicMock()
        mock_audio.content = b"audio_bytes"
        mock_client.audio.speech.create.return_value = mock_audio

        result = generate_audio_with_chatgpt("Script", "Plato", "key")
        assert isinstance(result, bytes)


def test_generate_audio_api_error():
    """Test audio generation handles API errors."""
    with patch("mindquest.utils.chatgpt.OpenAI") as mock_openai:
        mock_openai.return_value.audio.speech.create.side_effect = Exception(
            "API Error"
        )

        with pytest.raises(RuntimeError, match="Failed to generate audio"):
            generate_audio_with_chatgpt("Script", "Plato", "key")


# ============================================================================
# Script Parsing Tests
# ============================================================================


def test_parse_simple_script():
    """Test parsing a simple script."""
    script = "[Plato]: Hello\n[Pixel]: Hi there"
    segments = parse_script_segments(script)

    assert len(segments) == 2
    assert segments[0] == ("Plato", "Hello")
    assert segments[1] == ("Pixel", "Hi there")


def test_parse_script_with_dashes():
    """Test parsing script with dashes."""
    script = "[Plato] - Intro\n[Pixel] - Response"
    segments = parse_script_segments(script)

    assert len(segments) == 2


def test_parse_empty_script():
    """Test parsing empty script."""
    segments = parse_script_segments("")
    assert len(segments) == 0


def test_parse_script_no_tags():
    """Test parsing script without tags."""
    script = "No tags here"
    segments = parse_script_segments(script)
    assert len(segments) == 0


# ============================================================================
# Voice Synthesis Tests
# ============================================================================


def test_voice_over_valid_input():
    """Test voice_over with valid input."""
    with patch("mindquest.studio.parse_script_segments") as mock_parse, patch(
        "mindquest.studio.generate_audio_with_chatgpt"
    ) as mock_audio:
        mock_parse.return_value = [("Plato", "Hello"), ("Pixel", "Hi")]
        mock_audio.return_value = b"audio"

        result = voice_over("key", "[Plato]: Hello\n[Pixel]: Hi")
        assert isinstance(result, bytes)
        assert len(result) > 0


def test_voice_over_missing_api_key():
    """Test voice_over without API key raises ValueError."""
    with pytest.raises(ValueError, match="API key must be provided"):
        voice_over(None, "Script")


def test_voice_over_empty_api_key():
    """Test voice_over with empty API key raises ValueError."""
    with pytest.raises(ValueError, match="API key must be provided"):
        voice_over("", "Script")


def test_voice_over_missing_script():
    """Test voice_over without script raises ValueError."""
    with pytest.raises(ValueError, match="Script must be a non-empty string"):
        voice_over("key", None)


def test_voice_over_empty_script():
    """Test voice_over with empty script raises ValueError."""
    with pytest.raises(ValueError, match="Script must be a non-empty string"):
        voice_over("key", "")


def test_voice_over_no_valid_segments():
    """Test voice_over with script having no valid segments raises ValueError."""
    with patch("mindquest.studio.parse_script_segments") as mock_parse:
        mock_parse.return_value = []

        with pytest.raises(ValueError, match="No valid script segments found"):
            voice_over("key", "No segments")


def test_voice_over_multiple_languages():
    """Test voice_over with multiple languages."""
    with patch("mindquest.studio.parse_script_segments") as mock_parse, patch(
        "mindquest.studio.generate_audio_with_chatgpt"
    ) as mock_audio:
        mock_parse.return_value = [("Plato", "Hello")]
        mock_audio.return_value = b"audio"

        result = voice_over("key", "Script", languages="en,es")
        assert isinstance(result, bytes)


def test_extract_character_audio_valid():
    """Test extracting audio for a specific character."""
    with patch("mindquest.studio.parse_script_segments") as mock_parse, patch(
        "mindquest.studio.generate_audio_with_chatgpt"
    ) as mock_audio:
        mock_parse.return_value = [("Plato", "Hello"), ("Pixel", "Hi")]
        mock_audio.return_value = b"audio"

        result = extract_character_audio("[Plato]: Hello", "Plato", "key")
        assert isinstance(result, bytes)


def test_extract_character_audio_nonexistent():
    """Test extracting audio for nonexistent character."""
    with patch("mindquest.studio.parse_script_segments") as mock_parse:
        mock_parse.return_value = [("Plato", "Hello")]

        with pytest.raises(ValueError, match="No dialogue found for character"):
            extract_character_audio("Script", "Unknown", "key")


# ============================================================================
# WikiKids Tests
# ============================================================================


def test_search_wikikids_success():
    """Test successful WikiKids search."""
    with patch("mindquest.utils.wikikids.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "query": {"search": [{"title": "Test"}]}
        }

        result = search_wikikids("test")
        assert isinstance(result, str)


def test_search_wikikids_no_results():
    """Test WikiKids search with no results."""
    with patch("mindquest.utils.wikikids.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"query": {"search": []}}

        result = search_wikikids("nonexistent")
        assert "No results" in result or isinstance(result, str)


def test_search_wikikids_network_error():
    """Test WikiKids search with network error."""
    with patch("mindquest.utils.wikikids.requests.get") as mock_get:
        mock_get.side_effect = requests.RequestException("Network error")

        result = search_wikikids("test")
        assert isinstance(result, str)


def test_get_wikikids_summary_success():
    """Test successful WikiKids summary retrieval."""
    with patch("mindquest.utils.wikikids.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "query": {"pages": {"1": {"extract": "Summary"}}}
        }

        result = get_wikikids_summary("test")
        assert isinstance(result, str)


def test_get_wikikids_summary_no_extract():
    """Test WikiKids summary with no extract."""
    with patch("mindquest.utils.wikikids.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"query": {"pages": {"1": {}}}}

        result = get_wikikids_summary("test")
        assert isinstance(result, str)


def test_get_wikikids_summary_network_error():
    """Test WikiKids summary with network error."""
    with patch("mindquest.utils.wikikids.requests.get") as mock_get:
        mock_get.side_effect = requests.RequestException("Network error")

        result = get_wikikids_summary("test")
        assert isinstance(result, str)


# ============================================================================
# Character Profile Tests
# ============================================================================


def test_character_profile_creation():
    """Test creating a character profile."""
    profile = CharacterProfile(
        name="TestChar", voice_persona="Test", speech_characteristics="Test"
    )
    assert profile.name == "TestChar"


def test_plato_profile():
    """Test Plato profile exists and is configured."""
    assert PLATO.name == "Plato"
    assert isinstance(PLATO, CharacterProfile)


def test_pixel_profile():
    """Test Pixel profile exists and is configured."""
    assert PIXEL.name == "Pixel"
    assert isinstance(PIXEL, CharacterProfile)


def test_character_profiles_unique():
    """Test that Plato and Pixel are different."""
    assert PLATO.name != PIXEL.name


# ============================================================================
# Podcast Generation Tests
# ============================================================================


def test_generate_podcast_valid_inputs():
    """Test podcast generation with valid inputs."""
    with patch("mindquest.studio.create_script") as mock_script, patch(
        "mindquest.studio.voice_over"
    ) as mock_voice, patch("builtins.open", create=True):
        mock_script.return_value = "[Plato]: Script"
        mock_voice.return_value = b"audio"

        from pathlib import Path

        output_file = Path("/tmp/test_podcast.mp3")
        result = generate_podcast("Topic", "key", str(output_file))
        assert isinstance(result, str)


def test_generate_podcast_script_error():
    """Test podcast generation handles script generation errors."""
    with patch("mindquest.studio.create_script") as mock_script:
        mock_script.side_effect = RuntimeError("Script generation failed")

        with pytest.raises(RuntimeError, match="Script generation failed"):
            generate_podcast("Topic", "key", "/tmp/podcast.mp3")


def test_generate_podcast_audio_error():
    """Test podcast generation handles audio generation errors."""
    with patch("mindquest.studio.create_script") as mock_script, patch(
        "mindquest.studio.voice_over"
    ) as mock_voice:
        mock_script.return_value = "Script"
        mock_voice.side_effect = RuntimeError("Audio generation failed")

        with pytest.raises(RuntimeError, match="Audio generation failed"):
            generate_podcast("Topic", "key", "/tmp/podcast.mp3")


def test_generate_podcast_word_count():
    """Test podcast generation with custom word count."""
    with patch("mindquest.studio.create_script") as mock_script, patch(
        "mindquest.studio.voice_over"
    ) as mock_voice, patch("builtins.open", create=True):
        mock_script.return_value = "[Plato]: Script"
        mock_voice.return_value = b"audio"

        from pathlib import Path

        output_file = Path("/tmp/test_podcast.mp3")
        generate_podcast("Topic", "key", str(output_file), word_count=1000)
        mock_script.assert_called_once()
        assert mock_script.call_args[1]["number_of_words"] == 1000


# ============================================================================
# Mini-Book Generation Tests
# ============================================================================


def test_create_minibook_valid_inputs():
    """Test mini-book creation with valid inputs."""
    with patch("mindquest.studio.get_wikikids_summary") as mock_summary, patch(
        "mindquest.studio.search_wikikids"
    ) as mock_search, patch(
        "mindquest.studio.generate_minibook_with_chatgpt"
    ) as mock_generate, patch(
        "mindquest.studio.epub.write_epub"
    ) as mock_write_epub:
        mock_summary.return_value = "Topic summary"
        mock_search.return_value = "Search results"
        mock_generate.return_value = "# Mini-book\n## Chapter 1\nContent..."

        result = create_minibook("key", "Test Topic")

        assert isinstance(result, str)
        assert ".epub" in result
        assert mock_write_epub.called


def test_create_minibook_with_language():
    """Test mini-book creation with specific language."""
    with patch("mindquest.studio.get_wikikids_summary") as mock_summary, patch(
        "mindquest.studio.search_wikikids"
    ) as mock_search, patch(
        "mindquest.studio.generate_minibook_with_chatgpt"
    ) as mock_generate, patch(
        "mindquest.studio.epub.write_epub"
    ) as mock_write_epub:
        mock_summary.return_value = "Summary"
        mock_search.return_value = "Results"
        mock_generate.return_value = "Content"

        create_minibook("key", "Topic", language="es")
        assert mock_generate.call_args[0][3] == "es"
        assert mock_write_epub.called


def test_create_minibook_invalid_format():
    """Test mini-book creation with invalid format raises ValueError."""
    with pytest.raises(ValueError, match="Output format must be"):
        create_minibook("key", "Topic", output_format="invalid")


def test_create_minibook_missing_api_key():
    """Test mini-book creation without API key raises ValueError."""
    with pytest.raises(ValueError, match="API key must be provided"):
        create_minibook(None, "Topic")


def test_create_minibook_empty_topic():
    """Test mini-book creation with empty topic raises ValueError."""
    with pytest.raises(ValueError, match="Topic must be a non-empty string"):
        create_minibook("key", "")


def test_create_minibook_generation_error():
    """Test mini-book generation handles errors."""
    with patch("mindquest.studio.get_wikikids_summary") as mock_summary, patch(
        "mindquest.studio.search_wikikids"
    ) as mock_search, patch(
        "mindquest.studio.generate_minibook_with_chatgpt"
    ) as mock_generate:
        mock_summary.return_value = "Summary"
        mock_search.return_value = "Results"
        mock_generate.side_effect = RuntimeError("Generation failed")

        with pytest.raises(RuntimeError, match="Generation failed"):
            create_minibook("key", "Topic")


def test_generate_minibook_with_chatgpt():
    """Test minibook generation with ChatGPT."""
    with patch("mindquest.utils.chatgpt.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "# Book\n## Chapter"
        mock_client.chat.completions.create.return_value = mock_response

        result = generate_minibook_with_chatgpt("Topic", "Context", "key")
        assert isinstance(result, str)
        assert len(result) > 0


def test_generate_minibook_api_error():
    """Test minibook generation handles API errors."""
    with patch("mindquest.utils.chatgpt.OpenAI") as mock_openai:
        mock_openai.return_value.chat.completions.create.side_effect = Exception(
            "API Error"
        )

        with pytest.raises(RuntimeError, match="Failed to generate mini-book"):
            generate_minibook_with_chatgpt("Topic", "Context", "key")


def test_create_minibook_epub_format():
    """Test mini-book creation with epub format."""
    with patch("mindquest.studio.get_wikikids_summary") as mock_summary, patch(
        "mindquest.studio.search_wikikids"
    ) as mock_search, patch(
        "mindquest.studio.generate_minibook_with_chatgpt"
    ) as mock_generate, patch(
        "mindquest.studio.epub.write_epub"
    ) as mock_write_epub:
        mock_summary.return_value = "Summary"
        mock_search.return_value = "Results"
        mock_generate.return_value = "# Book"

        result = create_minibook("key", "Topic", output_format="epub")
        assert isinstance(result, str)
        assert ".epub" in result
        assert mock_write_epub.called


def test_create_minibook_pdf_format():
    """Test mini-book creation with pdf format."""
    with patch("mindquest.studio.get_wikikids_summary") as mock_summary, patch(
        "mindquest.studio.search_wikikids"
    ) as mock_search, patch(
        "mindquest.studio.generate_minibook_with_chatgpt"
    ) as mock_generate, patch(
        "builtins.open", create=True
    ) as mock_open:
        mock_summary.return_value = "Summary"
        mock_search.return_value = "Results"
        mock_generate.return_value = "# Book"

        result = create_minibook("key", "Topic", output_format="pdf")
        assert isinstance(result, str)
        assert ".pdf" in result
        assert mock_open.called


def test_parse_minibook_markdown():
    """Test parsing minibook markdown content."""
    content = "# Test Book\n## Chapter 1\nContent 1\n## Chapter 2\nContent 2"
    title, chapters = _parse_minibook_markdown(content)

    assert title == "Test Book"
    assert len(chapters) == 2
    assert chapters[0][0] == "Chapter 1"
    assert chapters[1][0] == "Chapter 2"


def test_create_epub_file_missing_library():
    """Test epub creation fails gracefully without library."""
    import mindquest.studio as studio

    original_epub = studio.epub
    try:
        studio.epub = None
        with pytest.raises(RuntimeError, match="ebooklib is not installed"):
            _create_epub_file("Test", "# Content", "en")
    finally:
        studio.epub = original_epub


def test_create_epub_file_success():
    """Test successful epub file creation."""
    with patch("mindquest.studio.epub.write_epub") as mock_write, patch(
        "mindquest.studio.epub.EpubBook"
    ) as mock_book_class, patch(
        "mindquest.studio.epub.EpubHtml"
    ) as mock_html_class, patch(
        "mindquest.studio.epub.EpubNcx"
    ), patch(
        "mindquest.studio.epub.EpubNav"
    ):
        mock_book = MagicMock()
        mock_book_class.return_value = mock_book
        mock_html = MagicMock()
        mock_html_class.return_value = mock_html

        result = _create_epub_file("Test Topic", "# Title\n## Ch1\nContent", "en")

        assert isinstance(result, str)
        assert ".epub" in result
        assert mock_write.called


def test_create_pdf_file_success():
    """Test successful pdf file creation."""
    with patch("builtins.open", create=True) as mock_open:
        result = _create_pdf_file("Test Topic", "# Title\nContent", "en")

        assert isinstance(result, str)
        assert ".pdf" in result
        assert mock_open.called


def test_parse_minibook_markdown_empty():
    """Test parsing minibook markdown with empty content."""
    content = ""
    title, chapters = _parse_minibook_markdown(content)

    assert title == ""
    assert len(chapters) == 0


def test_parse_minibook_markdown_no_title():
    """Test parsing minibook markdown without title."""
    content = "## Chapter 1\nContent 1"
    title, chapters = _parse_minibook_markdown(content)

    assert title == ""
    assert len(chapters) == 1


def test_create_minibook_returns_file_path():
    """Test that create_minibook returns a proper file path."""
    with patch("mindquest.studio.get_wikikids_summary") as mock_summary, patch(
        "mindquest.studio.search_wikikids"
    ) as mock_search, patch(
        "mindquest.studio.generate_minibook_with_chatgpt"
    ) as mock_generate, patch(
        "mindquest.studio.epub.write_epub"
    ) as mock_write_epub:
        mock_summary.return_value = "Summary"
        mock_search.return_value = "Results"
        mock_generate.return_value = "# Book\n## Chap\nContent"

        result = create_minibook("key", "FPV Drones", language="he")

        assert isinstance(result, str)
        assert "FPV_Drones" in result or "fpv_drones" in result.lower()
        assert "he.epub" in result
        assert mock_write_epub.called


def test_voice_over_with_no_audio_fallback():
    """Test voice_over fallback when no audio is generated."""
    with patch("mindquest.studio.parse_script_segments") as mock_parse, patch(
        "mindquest.studio.generate_audio_with_chatgpt"
    ) as mock_audio:
        mock_parse.return_value = [("Plato", "Hello")]
        mock_audio.return_value = None

        result = voice_over("key", "[Plato]: Hello")
        assert isinstance(result, bytes)
        assert len(result) == 0


def test_create_script_comprehensive():
    """Test comprehensive script creation with all parameters."""
    with patch("mindquest.studio.get_wikikids_summary") as mock_summary, patch(
        "mindquest.studio.search_wikikids"
    ) as mock_search, patch(
        "mindquest.studio.generate_script_with_chatgpt"
    ) as mock_generate:
        mock_summary.return_value = "Detailed summary"
        mock_search.return_value = "Multiple results"
        mock_generate.return_value = "[Plato]: Explanation\n[Pixel]: Question"

        result = create_script(
            "test-key", "Advanced Topic", number_of_words=1500, language="fr"
        )

        assert isinstance(result, str)
        assert mock_generate.call_args[0][3] == "fr"
