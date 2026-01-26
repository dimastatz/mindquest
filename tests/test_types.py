"""Tests for type definitions."""

from mindquest.types import CharacterProfile, PLATO, PIXEL


class TestCharacterProfile:
    """Test suite for CharacterProfile."""

    def test_character_profile_creation(self):
        """Test creating a character profile."""
        profile = CharacterProfile(
            name="TestChar",
            voice_persona="Test Persona",
            speech_characteristics="Test characteristics"
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
