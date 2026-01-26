"""Tests for voice-over and audio synthesis functionality."""

import pytest
from mindquest.voice import voice_over, parse_script_segments, extract_character_audio
from unittest.mock import patch


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
        assert segments == []

    def test_parse_script_no_tags(self):
        """Test parsing script without character tags returns empty list."""
        script = "Just plain text without any tags."
        segments = parse_script_segments(script)
        assert segments == []


class TestVoiceOver:
    """Test suite for the voice_over function."""

    def test_voice_over_valid_input(self):
        """Test voice_over with valid script and API key."""
        script = "[Plato]: Hello.\n[Pixel]: Hi!"
        api_key = "test-api-key"
        
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
        api_key = "test-api-key"
        
        with pytest.raises(ValueError, match="Script must be a non-empty string"):
            voice_over(api_key, None)

    def test_voice_over_empty_script(self):
        """Test voice_over raises error with empty script."""
        api_key = "test-api-key"
        
        with pytest.raises(ValueError, match="Script must be a non-empty string"):
            voice_over(api_key, "")

    def test_voice_over_no_valid_segments(self):
        """Test voice_over raises error when no valid segments found."""
        api_key = "test-api-key"
        script = "Just plain text without any tags."
        
        with pytest.raises(ValueError, match="No valid script segments found"):
            voice_over(api_key, script)

    def test_voice_over_multiple_languages(self):
        """Test voice_over handles multiple languages."""
        script = "[Plato]: Hello.\n[Pixel]: Hi!"
        api_key = "test-api-key"
        languages = "en,es,fr"
        
        with patch("mindquest.voice.generate_audio_with_gemini") as mock_audio:
            mock_audio.return_value = b"fake_audio"
            
            result = voice_over(api_key, script, languages)
            
            assert isinstance(result, bytes)
            # Verify the first language was used
            assert mock_audio.call_args[1]["language"] == "en"


class TestExtractCharacterAudio:
    """Test suite for character-specific audio extraction."""

    def test_extract_character_audio_valid(self):
        """Test extracting audio for a specific character."""
        script = "[Plato]: First line.\n[Plato]: Second line.\n[Pixel]: Interruption."
        api_key = "test-api-key"
        
        with patch("mindquest.voice.generate_audio_with_gemini") as mock_audio:
            mock_audio.return_value = b"plato_audio"
            
            result = extract_character_audio(script, "Plato", api_key)
            
            assert isinstance(result, bytes)

    def test_extract_character_audio_nonexistent(self):
        """Test extracting audio for nonexistent character."""
        script = "[Plato]: Hello.\n[Pixel]: Hi!"
        api_key = "test-api-key"
        
        with pytest.raises(ValueError, match="No dialogue found for character"):
            extract_character_audio(script, "NonExistent", api_key)

    def test_voice_over_audio_generation_error(self):
        """Test voice_over when audio generation fails."""
        script = "[Plato]: Hello.\n[Pixel]: Hi!"
        api_key = "test-api-key"
        
        with patch("mindquest.voice.generate_audio_with_gemini") as mock_audio:
            mock_audio.side_effect = Exception("Audio generation failed")
            
            with pytest.raises(RuntimeError, match="Failed to generate audio"):
                voice_over(api_key, script)

    def test_voice_over_returns_bytes(self):
        """Test that voice_over returns bytes type."""
        script = "[Plato]: Hello.\n[Pixel]: Hi!"
        api_key = "test-api-key"
        
        with patch("mindquest.voice.generate_audio_with_gemini") as mock_audio:
            mock_audio.return_value = b"fake_audio_chunk"
            
            result = voice_over(api_key, script)
            
            assert isinstance(result, bytes)

