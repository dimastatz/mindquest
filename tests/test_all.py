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
)
from mindquest.utils import search_wikikids, get_wikikids_summary
from mindquest.utils.chatgpt import (
    generate_script_with_chatgpt,
    generate_audio_with_chatgpt,
)
from mindquest.types import CharacterProfile, PLATO, PIXEL


# Script Generation Tests
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

        create_script("key", "Topic", 1000)
        assert mock_generate.called


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
        create_script("", "Topic")


def test_create_script_none_api_key():
    """Test script creation with None API key raises ValueError."""
    with pytest.raises(ValueError, match="API key must be provided"):
        create_script(None, "Topic")


# ChatGPT Utility Tests
def test_generate_script_with_chatgpt():
    """Test script generation with ChatGPT."""
    with patch("mindquest.utils.chatgpt.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "[Plato]: Space"
        mock_client.chat.completions.create.return_value = mock_response

        result = generate_script_with_chatgpt("Space", "Context", "key")
        assert result == "[Plato]: Space"


def test_generate_script_api_error():
    """Test script generation handles API errors."""
    with patch("mindquest.utils.chatgpt.OpenAI") as mock_openai:
        mock_openai.return_value.chat.completions.create.side_effect = Exception(
            "API Error"
        )

        with pytest.raises(RuntimeError, match="Failed to generate script"):
            generate_script_with_chatgpt("Space", "Context", "key")


def test_generate_audio_with_chatgpt():
    """Test audio generation with OpenAI TTS."""
    with patch("mindquest.utils.chatgpt.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = b"audio_data"
        mock_client.audio.speech.create.return_value = mock_response

        result = generate_audio_with_chatgpt("Hello", "Plato", "key")
        assert isinstance(result, bytes)


def test_generate_audio_api_error():
    """Test audio generation handles API errors."""
    with patch("mindquest.utils.chatgpt.OpenAI") as mock_openai:
        mock_openai.return_value.audio.speech.create.side_effect = Exception(
            "API Error"
        )

        with pytest.raises(RuntimeError, match="Failed to generate audio"):
            generate_audio_with_chatgpt("Script", "Plato", "key")


# Voice and Audio Tests
def test_parse_simple_script():
    """Test parsing a simple script with character tags."""
    script = "[Plato]: Hello, Pixel.\n[Pixel]: Hi!\n[Plato]: Learn."
    segments = parse_script_segments(script)

    assert len(segments) == 3
    assert segments[0] == ("Plato", "Hello, Pixel.")
    assert segments[1] == ("Pixel", "Hi!")
    assert segments[2] == ("Plato", "Learn.")


def test_parse_script_with_dashes():
    """Test parsing script with dash separators."""
    script = "[Plato] - Explain.\n[Pixel] - Listen."
    segments = parse_script_segments(script)

    assert len(segments) >= 1
    assert segments[0][0] == "Plato"


def test_parse_empty_script():
    """Test parsing empty script returns empty list."""
    assert not parse_script_segments("")


def test_parse_script_no_tags():
    """Test parsing script without tags returns empty list."""
    assert not parse_script_segments("Plain text")


def test_voice_over_valid_input():
    """Test voice_over with valid script."""
    with patch("mindquest.studio.generate_audio_with_chatgpt") as mock_audio:
        mock_audio.return_value = b"audio_data"

        result = voice_over("key", "[Plato]: Hello.\n[Pixel]: Hi!")
        assert isinstance(result, bytes)


def test_voice_over_missing_api_key():
    """Test voice_over raises error without API key."""
    with pytest.raises(ValueError, match="API key must be provided"):
        voice_over(None, "[Plato]: Hello.")


def test_voice_over_empty_api_key():
    """Test voice_over raises error with empty API key."""
    with pytest.raises(ValueError, match="API key must be provided"):
        voice_over("", "[Plato]: Hello.")


def test_voice_over_missing_script():
    """Test voice_over raises error without script."""
    with pytest.raises(ValueError, match="Script must be a non-empty string"):
        voice_over("key", None)


def test_voice_over_empty_script():
    """Test voice_over raises error with empty script."""
    with pytest.raises(ValueError, match="Script must be a non-empty string"):
        voice_over("key", "")


def test_voice_over_no_valid_segments():
    """Test voice_over raises error when no valid segments found."""
    with pytest.raises(ValueError, match="No valid script segments found"):
        voice_over("key", "Plain text")


def test_voice_over_multiple_languages():
    """Test voice_over handles multiple languages."""
    with patch("mindquest.studio.generate_audio_with_chatgpt") as mock_audio:
        mock_audio.return_value = b"audio"

        result = voice_over("key", "[Plato]: Hello.\n[Pixel]: Hi!", "en,es,fr")
        assert isinstance(result, bytes)
        assert mock_audio.call_args[1]["language"] == "en"


def test_extract_character_audio_valid():
    """Test extracting audio for a specific character."""
    with patch("mindquest.studio.generate_audio_with_chatgpt") as mock_audio:
        mock_audio.return_value = b"plato_audio"

        result = extract_character_audio(
            "[Plato]: Line1.\n[Plato]: Line2.\n[Pixel]: Other.",
            "Plato",
            "key",
        )
        assert isinstance(result, bytes)


def test_extract_character_audio_nonexistent():
    """Test extracting audio for nonexistent character."""
    with pytest.raises(ValueError, match="No dialogue found for character"):
        extract_character_audio("[Plato]: Hello.", "NonExistent", "key")


# WikiKids Integration Tests
def test_search_wikikids_success():
    """Test successful search on WikiKids."""
    with patch("mindquest.utils.wikikids.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "query": {
                "search": [
                    {
                        "title": "Solar System",
                        "snippet": "The <span class='searchmatch'>solar system</span>.",
                    }
                ]
            }
        }
        mock_get.return_value = mock_response

        result = search_wikikids("solar system", max_results=1)
        assert "Solar System" in result


def test_search_wikikids_no_results():
    """Test search with no results."""
    with patch("mindquest.utils.wikikids.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"query": {"search": []}}
        mock_get.return_value = mock_response

        result = search_wikikids("xyz1234567890")
        assert "No results found" in result


def test_search_wikikids_network_error():
    """Test search with network error."""
    with patch("mindquest.utils.wikikids.requests.get") as mock_get:
        mock_get.side_effect = requests.RequestException("Network error")

        result = search_wikikids("test")
        assert "Error searching WikiKids" in result


def test_get_wikikids_summary_success():
    """Test successful summary retrieval."""
    with patch("mindquest.utils.wikikids.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "query": {"pages": {"12345": {"extract": "Solar system is..."}}}
        }
        mock_get.return_value = mock_response

        result = get_wikikids_summary("solar system")
        assert "Solar system is" in result


def test_get_wikikids_summary_no_extract():
    """Test summary when no extract is available."""
    with patch("mindquest.utils.wikikids.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"query": {"pages": {"12345": {}}}}
        mock_get.return_value = mock_response

        result = get_wikikids_summary("topic")
        assert "No summary found" in result


def test_get_wikikids_summary_network_error():
    """Test summary retrieval with network error."""
    with patch("mindquest.utils.wikikids.requests.get") as mock_get:
        mock_get.side_effect = requests.RequestException("Network error")

        result = get_wikikids_summary("test")
        assert "Error fetching summary" in result


# Character Profile Tests
def test_character_profile_creation():
    """Test creating a character profile."""
    profile = CharacterProfile(
        name="Test",
        voice_persona="Persona",
        speech_characteristics="Characteristics",
    )

    assert profile.name == "Test"
    assert profile.voice_persona == "Persona"
    assert profile.speech_characteristics == "Characteristics"


def test_plato_profile():
    """Test Plato character profile."""
    assert PLATO.name == "Plato"
    assert PLATO.voice_persona == "Wise Professor"
    assert "Slow" in PLATO.speech_characteristics
    assert "calm" in PLATO.speech_characteristics.lower()


def test_pixel_profile():
    """Test Pixel character profile."""
    assert PIXEL.name == "Pixel"
    assert PIXEL.voice_persona == "10-year-old Child"
    assert "playful" in PIXEL.speech_characteristics.lower()
    assert "energy" in PIXEL.speech_characteristics.lower()


def test_character_profiles_unique():
    """Test that character profiles are distinct."""
    assert PLATO.name != PIXEL.name
    assert PLATO.voice_persona != PIXEL.voice_persona


# Podcast Generation Tests
def test_generate_podcast_valid_inputs(tmp_path):
    """Test podcast generation with valid inputs."""
    output_file = tmp_path / "test.mp3"
    with patch("mindquest.studio.create_script") as mock_script, patch(
        "mindquest.studio.voice_over"
    ) as mock_voice:
        mock_script.return_value = "[Plato]: Test script"
        mock_voice.return_value = b"audio_data"

        result = generate_podcast("Test Topic", "test-key", str(output_file), 500)

        assert str(output_file) in result
        assert mock_script.called
        assert mock_voice.called


def test_generate_podcast_script_error():
    """Test podcast generation handles script generation errors."""
    with patch("mindquest.studio.create_script") as mock_script:
        mock_script.side_effect = ValueError("Script error")

        with pytest.raises(RuntimeError, match="Script generation failed"):
            generate_podcast("Topic", "key")


def test_generate_podcast_audio_error():
    """Test podcast generation handles audio generation errors."""
    with patch("mindquest.studio.create_script") as mock_script, patch(
        "mindquest.studio.voice_over"
    ) as mock_voice:
        mock_script.return_value = "[Plato]: Script"
        mock_voice.side_effect = RuntimeError("Audio error")

        with pytest.raises(RuntimeError, match="Audio generation failed"):
            generate_podcast("Topic", "key")


def test_generate_podcast_word_count():
    """Test podcast generation with custom word count."""
    with patch("mindquest.studio.create_script") as mock_script, patch(
        "mindquest.studio.voice_over"
    ) as mock_voice:
        mock_script.return_value = "[Plato]: Script"
        mock_voice.return_value = b"audio"

        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            generate_podcast("Topic", "key", tmp.name, 1000)
            mock_script.assert_called_once()
            # Check that word_count was passed
            assert mock_script.call_args[1]["number_of_words"] == 1000
