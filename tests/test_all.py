"""Comprehensive test suite for MindQuest project."""

from unittest.mock import patch, MagicMock
import pytest
import requests
from mindquest.script import create_script
from mindquest.voice import voice_over, parse_script_segments, extract_character_audio
from mindquest.utils import search_wikikids, get_wikikids_summary
from mindquest.utils.gemini import (
    generate_script_with_gemini,
    generate_audio_with_gemini,
)
from mindquest.types import CharacterProfile, PLATO, PIXEL


# ===================== Script Generation Tests =====================


class TestCreateScript:
    """Test suite for the create_script function."""

    def test_create_script_valid_topic(self):
        """Test script creation with a valid topic."""
        topic = "Solar System"

        with patch("mindquest.script.get_wikikids_summary") as mock_summary, patch(
            "mindquest.script.search_wikikids"
        ) as mock_search, patch(
            "mindquest.script.generate_script_with_gemini"
        ) as mock_generate:
            mock_summary.return_value = (
                "The solar system consists of the Sun and eight planets."
            )
            mock_search.return_value = "**Solar System**: Information about planets..."
            mock_generate.return_value = (
                "[Plato]: The solar system is...\n[Pixel]: Cool!"
            )

            result = create_script(topic)

            assert result is not None
            assert isinstance(result, str)
            assert len(result) > 0
            mock_summary.assert_called_once_with(topic)
            mock_search.assert_called_once()
            mock_generate.assert_called_once()

    def test_create_script_with_word_count(self):
        """Test script creation with specific word count."""
        topic = "Solar System"
        word_count = 1000

        with patch("mindquest.script.get_wikikids_summary") as mock_summary, patch(
            "mindquest.script.search_wikikids"
        ) as mock_search, patch(
            "mindquest.script.generate_script_with_gemini"
        ) as mock_generate:
            mock_summary.return_value = "Summary"
            mock_search.return_value = "Results"
            mock_generate.return_value = "Script"

            create_script(topic, word_count)

            # Verify word count was passed to Gemini
            call_args = mock_generate.call_args
            assert call_args[0][2] == word_count

    def test_create_script_empty_topic(self):
        """Test script creation with empty topic raises ValueError."""
        with pytest.raises(ValueError, match="Topic must be a non-empty string"):
            create_script("")

    def test_create_script_none_topic(self):
        """Test script creation with None topic raises ValueError."""
        with pytest.raises(ValueError, match="Topic must be a non-empty string"):
            create_script(None)

    def test_create_script_default_word_count(self):
        """Test that default word count is 500."""
        topic = "Animals"

        with patch("mindquest.script.get_wikikids_summary") as mock_summary, patch(
            "mindquest.script.search_wikikids"
        ) as mock_search, patch(
            "mindquest.script.generate_script_with_gemini"
        ) as mock_generate:
            mock_summary.return_value = "Summary"
            mock_search.return_value = "Results"
            mock_generate.return_value = "Script"

            create_script(topic)

            # Verify default 500 words was used
            call_args = mock_generate.call_args
            assert call_args[0][2] == 500

    def test_create_script_strips_whitespace(self):
        """Test that topic whitespace is properly stripped."""
        topic = "  Solar System  "

        with patch("mindquest.script.get_wikikids_summary") as mock_summary, patch(
            "mindquest.script.search_wikikids"
        ) as mock_search, patch(
            "mindquest.script.generate_script_with_gemini"
        ) as mock_generate:
            mock_summary.return_value = "Summary"
            mock_search.return_value = "Results"
            mock_generate.return_value = "Script"

            create_script(topic)

            # Verify the topic was stripped
            assert mock_summary.call_args[0][0] == "Solar System"

    def test_create_script_passes_context_to_gemini(self):
        """Test that WikiKids data is passed as context to Gemini."""
        topic = "Dinosaurs"

        with patch("mindquest.script.get_wikikids_summary") as mock_summary, patch(
            "mindquest.script.search_wikikids"
        ) as mock_search, patch(
            "mindquest.script.generate_script_with_gemini"
        ) as mock_generate:
            mock_summary.return_value = "Dinosaurs were ancient reptiles."
            mock_search.return_value = "**Dinosaur**: Extinct reptile species."
            mock_generate.return_value = "Script content"

            create_script(topic)

            # Verify context was built and passed
            call_args = mock_generate.call_args
            context = call_args[0][1]
            assert "Dinosaurs were ancient reptiles" in context
            assert "Dinosaur" in context


# ===================== Gemini Utility Tests =====================


class TestGenerateScriptWithGemini:
    """Test suite for Gemini script generation utility."""

    def test_generate_script_valid_inputs(self):
        """Test script generation with valid inputs."""
        topic = "Space"
        context = "Space is vast"
        word_count = 500

        with patch("mindquest.utils.gemini.genai") as mock_genai:
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_response = MagicMock()
            mock_response.text = "[Plato]: Space is vast"
            mock_model.generate_content.return_value = mock_response

            result = generate_script_with_gemini(topic, context, word_count)

            assert result == "[Plato]: Space is vast"
            mock_genai.GenerativeModel.assert_called_once_with("gemini-1.5-flash")

    def test_generate_script_missing_topic(self):
        """Test script generation with empty topic uses what's provided."""
        with patch("mindquest.utils.gemini.genai") as mock_genai:
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_response = MagicMock()
            mock_response.text = "Script"
            mock_model.generate_content.return_value = mock_response

            result = generate_script_with_gemini("", "context", 500)
            assert result == "Script"

    def test_generate_script_genai_not_installed(self):
        """Test script generation raises error if Gemini not available."""
        with patch("mindquest.utils.gemini.genai", None):
            with pytest.raises(
                RuntimeError, match="Google Generative AI package not installed"
            ):
                generate_script_with_gemini("Space", "Context", 500)

    def test_generate_script_api_error(self):
        """Test script generation handles API errors."""
        with patch("mindquest.utils.gemini.genai") as mock_genai:
            mock_genai.GenerativeModel.return_value.generate_content.side_effect = (
                Exception("API Error")
            )

            with pytest.raises(RuntimeError, match="Failed to generate script"):
                generate_script_with_gemini("Space", "Context", 500)


class TestGenerateAudioWithGemini:
    """Test suite for Gemini audio generation utility."""

    def test_generate_audio_valid_inputs(self):
        """Test audio generation with valid inputs."""
        script = "Hello world"
        character = "Plato"

        with patch("mindquest.utils.gemini.genai") as mock_genai:
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_response = MagicMock()
            mock_response.text = "audio_data"
            mock_model.generate_content.return_value = mock_response

            result = generate_audio_with_gemini(script, character)

            assert result == b"audio_data"
            mock_genai.GenerativeModel.assert_called_with("gemini-1.5-flash")

    def test_generate_audio_missing_script(self):
        """Test audio generation with empty script."""
        with patch("mindquest.utils.gemini.genai") as mock_genai:
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_response = MagicMock()
            mock_response.text = "audio_data"
            mock_model.generate_content.return_value = mock_response

            result = generate_audio_with_gemini("", "Plato")
            assert result == b"audio_data"

    def test_generate_audio_missing_character(self):
        """Test audio generation with unknown character uses default."""
        script = "Hello"
        character = "Unknown"

        with patch("mindquest.utils.gemini.genai") as mock_genai:
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_response = MagicMock()
            mock_response.text = "audio_data"
            mock_model.generate_content.return_value = mock_response

            result = generate_audio_with_gemini(script, character)

            assert result == b"audio_data"

    def test_generate_audio_genai_not_installed(self):
        """Test audio generation raises error if Gemini not available."""
        with patch("mindquest.utils.gemini.genai", None):
            with pytest.raises(
                RuntimeError, match="Google Generative AI package not installed"
            ):
                generate_audio_with_gemini("Script", "Plato")

    def test_generate_audio_api_error(self):
        """Test audio generation handles API errors."""
        with patch("mindquest.utils.gemini.genai") as mock_genai:
            mock_genai.GenerativeModel.return_value.generate_content.side_effect = (
                Exception("API Error")
            )

            with pytest.raises(RuntimeError, match="Failed to generate audio"):
                generate_audio_with_gemini("Script", "Plato")

    def test_generate_audio_pixel_character(self):
        """Test audio generation uses correct voice for Pixel."""
        with patch("mindquest.utils.gemini.genai") as mock_genai:
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_response = MagicMock()
            mock_response.text = "audio_data"
            mock_model.generate_content.return_value = mock_response

            generate_audio_with_gemini("Hello", "Pixel")

            # Verify Pixel's voice config was used
            call_args = mock_model.generate_content.call_args
            prompt = call_args[0][0]
            assert "Cheerful and Energetic" in prompt


# ===================== Voice and Audio Tests =====================


class TestParseScriptSegments:
    """Test suite for script parsing functionality."""

    def test_parse_simple_script(self):
        """Test parsing a simple script with character tags."""
        script = """[Plato]: Hello, Pixel.
[Pixel]: Hi, Plato! What are we learning today?
[Plato]: Today we'll learn about the solar system."""

        segments = parse_script_segments(script)

        assert len(segments) == 3
        assert segments[0] == ("Plato", "Hello, Pixel.")
        assert segments[1] == ("Pixel", "Hi, Plato! What are we learning today?")
        assert segments[2] == ("Plato", "Today we'll learn about the solar system.")

    def test_parse_script_with_dashes(self):
        """Test parsing script with dash separators."""
        script = "[Plato] - Let me explain.\n[Pixel] - Okay, I'm listening."
        segments = parse_script_segments(script)

        assert len(segments) >= 1
        assert segments[0][0] == "Plato"

    def test_parse_empty_script(self):
        """Test parsing empty script returns empty list."""
        segments = parse_script_segments("")
        assert not segments

    def test_parse_script_no_tags(self):
        """Test parsing script without character tags returns empty list."""
        script = "Just plain text without any tags."
        segments = parse_script_segments(script)
        assert not segments


class TestVoiceOver:
    """Test suite for the voice_over function."""

    def test_voice_over_valid_input(self):
        """Test voice_over with valid script."""
        script = "[Plato]: Hello.\n[Pixel]: Hi!"
        api_key = "test-key"

        with patch("mindquest.voice.generate_audio_with_gemini") as mock_audio:
            mock_audio.return_value = b"fake_audio_data"

            result = voice_over(api_key, script)

            assert isinstance(result, bytes)

    def test_voice_over_missing_api_key(self):
        """Test voice_over raises error without API key."""
        script = "[Plato]: Hello."

        with pytest.raises(ValueError, match="API key must be provided"):
            voice_over(None, script)

    def test_voice_over_empty_api_key(self):
        """Test voice_over raises error with empty API key."""
        script = "[Plato]: Hello."

        with pytest.raises(ValueError, match="API key must be provided"):
            voice_over("", script)

    def test_voice_over_missing_script(self):
        """Test voice_over raises error without script."""
        api_key = "test-key"

        with pytest.raises(ValueError, match="Script must be a non-empty string"):
            voice_over(api_key, None)

    def test_voice_over_empty_script(self):
        """Test voice_over raises error with empty script."""
        api_key = "test-key"

        with pytest.raises(ValueError, match="Script must be a non-empty string"):
            voice_over(api_key, "")

    def test_voice_over_no_valid_segments(self):
        """Test voice_over raises error when no valid segments found."""
        api_key = "test-key"
        script = "Just plain text without any tags."

        with pytest.raises(ValueError, match="No valid script segments found"):
            voice_over(api_key, script)

    def test_voice_over_multiple_languages(self):
        """Test voice_over handles multiple languages."""
        script = "[Plato]: Hello.\n[Pixel]: Hi!"
        api_key = "test-key"
        languages = "en,es,fr"

        with patch("mindquest.voice.generate_audio_with_gemini") as mock_audio:
            mock_audio.return_value = b"fake_audio"

            result = voice_over(api_key, script, languages)

            assert isinstance(result, bytes)
            # Verify the first language was used
            assert mock_audio.call_args[1]["language"] == "en"

    def test_voice_over_audio_generation_error(self):
        """Test voice_over when audio generation fails."""
        script = "[Plato]: Hello.\n[Pixel]: Hi!"
        api_key = "test-key"

        with patch("mindquest.voice.generate_audio_with_gemini") as mock_audio:
            mock_audio.side_effect = Exception("Audio generation failed")

            with pytest.raises(RuntimeError, match="Failed to generate audio"):
                voice_over(api_key, script)

    def test_voice_over_returns_bytes(self):
        """Test that voice_over returns bytes type."""
        script = "[Plato]: Hello.\n[Pixel]: Hi!"
        api_key = "test-key"

        with patch("mindquest.voice.generate_audio_with_gemini") as mock_audio:
            mock_audio.return_value = b"fake_audio_chunk"

            result = voice_over(api_key, script)

            assert isinstance(result, bytes)

    def test_voice_over_empty_audio_segments(self):
        """Test voice_over when audio generation returns empty bytes."""
        script = "[Plato]: Hello.\n[Pixel]: Hi!"
        api_key = "test-key"

        with patch("mindquest.voice.generate_audio_with_gemini") as mock_audio:
            mock_audio.return_value = b""

            result = voice_over(api_key, script)

            assert isinstance(result, bytes)


class TestExtractCharacterAudio:
    """Test suite for character-specific audio extraction."""

    def test_extract_character_audio_valid(self):
        """Test extracting audio for a specific character."""
        script = "[Plato]: First line.\n[Plato]: Second line.\n[Pixel]: Interruption."
        api_key = "test-key"

        with patch("mindquest.voice.generate_audio_with_gemini") as mock_audio:
            mock_audio.return_value = b"plato_audio"

            result = extract_character_audio(script, "Plato", api_key)

            assert isinstance(result, bytes)

    def test_extract_character_audio_nonexistent(self):
        """Test extracting audio for nonexistent character."""
        script = "[Plato]: Hello.\n[Pixel]: Hi!"
        api_key = "test-key"

        with pytest.raises(ValueError, match="No dialogue found for character"):
            extract_character_audio(script, "NonExistent", api_key)


# ===================== WikiKids Integration Tests =====================


class TestWikiKidsIntegration:
    """Test suite for WikiKids integration."""

    def test_search_wikikids_success(self):
        """Test successful search on WikiKids."""
        with patch("mindquest.utils.wikikids.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "query": {
                    "search": [
                        {
                            "title": "Solar System",
                            "snippet": (
                                "The <span class='searchmatch'>solar "
                                "system</span> consists of eight planets."
                            ),
                        }
                    ]
                }
            }
            mock_get.return_value = mock_response

            result = search_wikikids("solar system", max_results=1)

            assert "Solar System" in result
            assert "solar system" in result

    def test_search_wikikids_no_results(self):
        """Test search with no results."""
        with patch("mindquest.utils.wikikids.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"query": {"search": []}}
            mock_get.return_value = mock_response

            result = search_wikikids("xyz1234567890", max_results=1)

            assert "No results found" in result

    def test_search_wikikids_multiple_results(self):
        """Test search with multiple results."""
        with patch("mindquest.utils.wikikids.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "query": {
                    "search": [
                        {"title": "Result1", "snippet": "First result"},
                        {"title": "Result2", "snippet": "Second result"},
                        {"title": "Result3", "snippet": "Third result"},
                    ]
                }
            }
            mock_get.return_value = mock_response

            result = search_wikikids("test", max_results=3)

            assert "Result1" in result
            assert "Result2" in result
            assert "Result3" in result

    def test_search_wikikids_network_error(self):
        """Test search with network error."""
        with patch("mindquest.utils.wikikids.requests.get") as mock_get:
            mock_get.side_effect = requests.RequestException("Network error")

            result = search_wikikids("test")

            assert "Error searching WikiKids" in result

    def test_get_wikikids_summary_success(self):
        """Test successful summary retrieval."""
        with patch("mindquest.utils.wikikids.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "query": {
                    "pages": {
                        "12345": {
                            "extract": "The solar system is a planetary system..."
                        }
                    }
                }
            }
            mock_get.return_value = mock_response

            result = get_wikikids_summary("solar system")

            assert "solar system" in result

    def test_get_wikikids_summary_no_extract(self):
        """Test summary when no extract is available."""
        with patch("mindquest.utils.wikikids.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"query": {"pages": {"12345": {}}}}
            mock_get.return_value = mock_response

            result = get_wikikids_summary("nonexistent")

            assert "No summary found" in result

    def test_get_wikikids_summary_network_error(self):
        """Test summary retrieval with network error."""
        with patch("mindquest.utils.wikikids.requests.get") as mock_get:
            mock_get.side_effect = requests.RequestException("Network error")

            result = get_wikikids_summary("test")

            assert "Error fetching summary" in result


# ===================== Character Profile Tests =====================


class TestCharacterProfile:  # pylint: disable=too-few-public-methods
    """Test suite for CharacterProfile."""

    def test_character_profile_creation(self):
        """Test creating a character profile."""
        profile = CharacterProfile(
            name="TestChar",
            voice_persona="Test Persona",
            speech_characteristics="Test characteristics",
        )

        assert profile.name == "TestChar"
        assert profile.voice_persona == "Test Persona"
        assert profile.speech_characteristics == "Test characteristics"


class TestPredefinedCharacters:
    """Test suite for predefined character profiles."""

    def test_plato_profile(self):
        """Test Plato character profile."""
        assert PLATO.name == "Plato"
        assert PLATO.voice_persona == "Wise Professor"
        assert "Slow" in PLATO.speech_characteristics
        assert "calm" in PLATO.speech_characteristics.lower()

    def test_pixel_profile(self):
        """Test Pixel character profile."""
        assert PIXEL.name == "Pixel"
        assert PIXEL.voice_persona == "10-year-old Child"
        assert "playful" in PIXEL.speech_characteristics.lower()
        assert "energy" in PIXEL.speech_characteristics.lower()

    def test_character_profiles_are_unique(self):
        """Test that character profiles are distinct."""
        assert PLATO.name != PIXEL.name
        assert PLATO.voice_persona != PIXEL.voice_persona


# ===================== Integration Tests =====================
