"Comprehensive test suite for MindQuest project."

from unittest.mock import patch, MagicMock
import pytest
from mindquest.studio import (
    create_script,
    voice_over,
    parse_script_segments,
    extract_character_audio,
    generate_podcast,
    create_minibook,
    _parse_minibook_markdown,
    _validate_minibook_structure,
    _create_epub_file,
    _create_pdf_file,
)
from mindquest.utils.chatgpt import (
    generate_script_with_chatgpt,
    generate_audio_with_chatgpt,
    generate_minibook_with_chatgpt,
    generate_cover_image_with_dalle,
)
from mindquest.utils.wikikids import search_wikikids, get_wikikids_summary
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
        assert mock_generate.called


def test_create_script_empty_topic():
    """Test script creation with empty topic raises ValueError."""
    with pytest.raises(ValueError, match="Topic must be a non-empty string"):
        create_script("key", "")


def test_create_script_missing_api_key():
    """Test script creation without API key raises ValueError."""
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


def test_generate_script_error():
    """Test script generation error handling."""
    with patch("mindquest.utils.chatgpt.OpenAI") as mock_openai:
        mock_openai.return_value.chat.completions.create.side_effect = Exception(
            "Error"
        )
        with pytest.raises(RuntimeError):
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


def test_generate_audio_error():
    """Test audio generation error handling."""
    with patch("mindquest.utils.chatgpt.OpenAI") as mock_openai:
        mock_openai.return_value.audio.speech.create.side_effect = Exception("Error")
        with pytest.raises(RuntimeError):
            generate_audio_with_chatgpt("Script", "Plato", "key")


def test_generate_minibook_with_chatgpt():
    """Test mini-book generation with ChatGPT."""
    with patch("mindquest.utils.chatgpt.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "# Book\n## Chapter 1\nContent"
        mock_client.chat.completions.create.return_value = mock_response

        result = generate_minibook_with_chatgpt("Topic", "Context", "key")
        assert isinstance(result, str)
        assert len(result) > 0


def test_generate_minibook_error():
    """Test mini-book generation error handling."""
    with patch("mindquest.utils.chatgpt.OpenAI") as mock_openai:
        mock_openai.return_value.chat.completions.create.side_effect = Exception(
            "Error"
        )
        with pytest.raises(RuntimeError):
            generate_minibook_with_chatgpt("Topic", "Context", "key")


def test_generate_cover_image_with_dalle():
    """Test DALL-E cover image generation."""
    with patch("mindquest.utils.chatgpt.OpenAI") as mock_openai, patch(
        "mindquest.utils.chatgpt.requests.get"
    ) as mock_get:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.data = [MagicMock(url="http://image.url")]
        mock_client.images.generate.return_value = mock_response

        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b"image_bytes"

        result = generate_cover_image_with_dalle("Topic", "key")
        assert result == b"image_bytes"


def test_generate_cover_image_no_url():
    """Test DALL-E generation with no URL returned."""
    with patch("mindquest.utils.chatgpt.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.data = [MagicMock(url=None)]
        mock_client.images.generate.return_value = mock_response

        with pytest.raises(RuntimeError, match="No image URL"):
            generate_cover_image_with_dalle("Topic", "key")


def test_generate_cover_image_error():
    """Test DALL-E generation error handling."""
    with patch("mindquest.utils.chatgpt.OpenAI") as mock_openai:
        mock_openai.return_value.images.generate.side_effect = Exception("API Error")
        with pytest.raises(RuntimeError, match="Failed to generate cover image"):
            generate_cover_image_with_dalle("Topic", "key")


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


def test_voice_over_with_language():
    """Test voice_over with specific language."""
    with patch("mindquest.studio.parse_script_segments") as mock_parse, patch(
        "mindquest.studio.generate_audio_with_chatgpt"
    ) as mock_audio:
        mock_parse.return_value = [("Plato", "Hello")]
        mock_audio.return_value = b"audio"

        result = voice_over("key", "Script", language="es")
        assert isinstance(result, bytes)


def test_voice_over_empty_script():
    """Test voice_over with empty script."""
    with pytest.raises(ValueError):
        voice_over("key", "")


def test_voice_over_no_segments():
    """Test voice_over with no valid segments."""
    with patch("mindquest.studio.parse_script_segments") as mock_parse:
        mock_parse.return_value = []
        with pytest.raises(ValueError):
            voice_over("key", "Invalid script")


def test_voice_over_audio_generation_error():
    """Test voice_over audio generation error."""
    with patch("mindquest.studio.parse_script_segments") as mock_parse, patch(
        "mindquest.studio.generate_audio_with_chatgpt"
    ) as mock_audio:
        mock_parse.return_value = [("Plato", "Hello")]
        mock_audio.side_effect = Exception("TTS Error")
        with pytest.raises(RuntimeError, match="Failed to generate audio"):
            voice_over("key", "[Plato]: Hello")


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
        "mindquest.studio.generate_cover_image_with_dalle"
    ) as mock_cover, patch(
        "mindquest.studio.epub.write_epub"
    ):
        mock_summary.return_value = "Topic summary"
        mock_search.return_value = "Search results"
        mock_generate.return_value = "# Mini-book\n## Chapter 1\nContent..."
        mock_cover.return_value = b"image_data"

        result = create_minibook("key", "Test Topic")

        assert isinstance(result, str)
        assert ".epub" in result


def test_create_minibook_with_parameters():
    """Test mini-book creation with custom parameters."""
    with patch("mindquest.studio.get_wikikids_summary") as mock_summary, patch(
        "mindquest.studio.search_wikikids"
    ) as mock_search, patch(
        "mindquest.studio.generate_minibook_with_chatgpt"
    ) as mock_generate, patch(
        "mindquest.studio.generate_cover_image_with_dalle"
    ) as mock_cover, patch(
        "mindquest.studio.epub.write_epub"
    ):
        mock_summary.return_value = "Summary"
        mock_search.return_value = "Results"
        mock_generate.return_value = "# Book\n## Chap 1\nContent"
        mock_cover.return_value = b"image_data"

        create_minibook(
            "key", "Topic", language="he", number_of_chapters=5, format="ebup"
        )
        assert mock_generate.called
        assert mock_generate.call_args[0][4] == 5  # Check number_of_chapters passed


def test_create_minibook_pdf_format():
    """Test mini-book creation with pdf format."""
    with patch("mindquest.studio.get_wikikids_summary") as mock_summary, patch(
        "mindquest.studio.search_wikikids"
    ) as mock_search, patch(
        "mindquest.studio.generate_minibook_with_chatgpt"
    ) as mock_generate, patch(
        "mindquest.studio.generate_cover_image_with_dalle"
    ) as mock_cover, patch(
        "builtins.open", create=True
    ) as mock_open:
        mock_summary.return_value = "Summary"
        mock_search.return_value = "Results"
        mock_generate.return_value = "# Book\n## Chap 1\nContent"
        mock_cover.return_value = b"image_data"

        result = create_minibook("key", "Topic", format="pdf")
        assert isinstance(result, str)
        assert ".pdf" in result
        assert mock_open.called


def test_create_minibook_invalid_format():
    """Test mini-book creation with invalid format."""
    with pytest.raises(ValueError, match="Output format must be"):
        create_minibook("key", "Topic", format="invalid")


def test_create_minibook_errors():
    """Test validation and other errors in create_minibook."""
    with pytest.raises(ValueError, match="API key must be provided"):
        create_minibook("", "Topic")
    with pytest.raises(ValueError, match="Topic must be a non-empty string"):
        create_minibook("key", "")


def test_create_minibook_cover_error():
    """Test mini-book creation survives cover generation error."""
    with patch("mindquest.studio.get_wikikids_summary"), patch(
        "mindquest.studio.search_wikikids"
    ), patch("mindquest.studio.generate_minibook_with_chatgpt") as mock_gen, patch(
        "mindquest.studio.generate_cover_image_with_dalle"
    ) as mock_cover, patch(
        "mindquest.studio.epub.write_epub"
    ):
        mock_gen.return_value = "# Book\n## Ch1\nTxt"
        mock_cover.side_effect = RuntimeError("DALL-E Failed")

        # Should still succeed without cover
        result = create_minibook("key", "Topic")
        assert isinstance(result, str)


# ============================================================================
# WikiKids Tests
# ============================================================================


def test_search_wikikids_success():
    """Test successful WikiKids search."""
    with patch("mindquest.utils.wikikids.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "query": {"search": [{"title": "Test", "snippet": "Snippet"}]}
        }

        result = search_wikikids("test")
        assert "Test" in result


def test_search_wikikids_no_results():
    """Test WikiKids search with no results."""
    with patch("mindquest.utils.wikikids.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"query": {}}
        result = search_wikikids("test")
        assert "No results" in result


def test_search_wikikids_error():
    """Test WikiKids search error handling."""
    with patch("mindquest.utils.wikikids.requests.get") as mock_get:
        mock_get.side_effect = Exception("Network error")
        result = search_wikikids("test")
        assert "Error searching WikiKids" in result


def test_get_wikikids_summary_success():
    """Test successful WikiKids summary retrieval."""
    with patch("mindquest.utils.wikikids.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "query": {"pages": {"1": {"extract": "Summary"}}}
        }

        result = get_wikikids_summary("test")
        assert result == "Summary"


def test_get_wikikids_summary_no_summary():
    """Test WikiKids summary with no summary found."""
    with patch("mindquest.utils.wikikids.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"query": {"pages": {"-1": {}}}}
        result = get_wikikids_summary("test")
        assert "No summary found" in result


def test_get_wikikids_summary_error():
    """Test WikiKids summary error handling."""
    with patch("mindquest.utils.wikikids.requests.get") as mock_get:
        mock_get.side_effect = Exception("Error")
        result = get_wikikids_summary("test")
        assert "Error fetching summary" in result


# ============================================================================
# Character Profile Tests
# ============================================================================


def test_character_profiles():
    """Test predefined character profiles."""
    assert PLATO.name == "Plato"
    assert PIXEL.name == "Pixel"
    assert isinstance(PLATO, CharacterProfile)
    assert PLATO.voice_persona == "Wise Professor"


# ============================================================================
# Other Utility Tests
# ============================================================================


def test_parse_script_segments():
    """Test parsing script segments."""
    script = "[Plato]: Hello\n[Pixel]: Hi"
    segments = parse_script_segments(script)
    assert segments == [("Plato", "Hello"), ("Pixel", "Hi")]


def test_extract_character_audio():
    """Test extracting character audio."""
    with patch("mindquest.studio.parse_script_segments") as mock_parse, patch(
        "mindquest.studio.generate_audio_with_chatgpt"
    ) as mock_audio:
        mock_parse.return_value = [("Plato", "Hello"), ("Pixel", "Hi")]
        mock_audio.return_value = b"audio"

        result = extract_character_audio("[Plato]: Hello", "Plato", "key")
        assert result == b"audio"


def test_extract_character_audio_not_found():
    """Test extracting character audio for non-existent character."""
    with patch("mindquest.studio.parse_script_segments") as mock_parse:
        mock_parse.return_value = [("Plato", "Hello")]
        with pytest.raises(ValueError, match="No dialogue found"):
            extract_character_audio("[Plato]: Hello", "Pixel", "key")


def test_generate_podcast():
    """Test complete podcast generation."""
    with patch("mindquest.studio.create_script") as mock_script, patch(
        "mindquest.studio.voice_over"
    ) as mock_voice, patch("builtins.open", create=True):
        mock_script.return_value = "[Plato]: Script"
        mock_voice.return_value = b"audio"

        result = generate_podcast("Topic", "key")
        assert isinstance(result, str)


def test_generate_podcast_errors():
    """Test generate_podcast error handling."""
    with patch("mindquest.studio.create_script") as mock_script:
        mock_script.side_effect = Exception("Script error")
        with pytest.raises(RuntimeError, match="Script generation failed"):
            generate_podcast("Topic", "key")

    with patch("mindquest.studio.create_script") as mock_script, patch(
        "mindquest.studio.voice_over"
    ) as mock_voice:
        mock_script.return_value = "Script"
        mock_voice.side_effect = Exception("Audio error")
        with pytest.raises(RuntimeError, match="Audio generation failed"):
            generate_podcast("Topic", "key")

    with patch("mindquest.studio.create_script") as mock_script, patch(
        "mindquest.studio.voice_over"
    ) as mock_voice, patch("builtins.open", create=True) as mock_open:
        mock_script.return_value = "Script"
        mock_voice.return_value = b"audio"
        mock_open.side_effect = Exception("Save error")
        with pytest.raises(RuntimeError, match="Failed to save podcast"):
            generate_podcast("Topic", "key")


def test_parse_minibook_markdown():
    """Test minibook markdown parsing."""
    content = "# Title\n## Chapter 1\nContent 1\n## Chapter 2\nContent 2"
    title, chapters = _parse_minibook_markdown(content)
    assert title == "Title"
    assert len(chapters) == 2
    assert chapters[0] == ("Chapter 1", "Content 1")


def test_validate_minibook_structure():
    """Test _validate_minibook_structure edge cases."""
    with pytest.raises(ValueError, match="Generated content is empty"):
        _validate_minibook_structure("")
    with pytest.raises(ValueError, match="must have a title"):
        _validate_minibook_structure("## Chapter 1")


def test_create_epub_file_error():
    """Test EPUB creation error handling."""
    with patch("mindquest.studio.epub.EpubBook") as mock_book:
        mock_book.side_effect = Exception("EPUB Error")
        with pytest.raises(RuntimeError, match="Failed to create EPUB"):
            _create_epub_file("Title", "# Title\n## Ch1\nContent", "en")


def test_create_pdf_file_error():
    """Test PDF creation error handling."""
    with patch("builtins.open", create=True) as mock_open:
        mock_open.side_effect = Exception("PDF Error")
        with pytest.raises(RuntimeError, match="Failed to create PDF"):
            _create_pdf_file("Title", "Content", "en")
