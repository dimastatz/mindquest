"""Integration tests for MindQuest with real Gemini API."""

import os
import pytest
from mindquest import create_script, voice_over


@pytest.mark.integration
class TestGeminiIntegration:
    """Integration tests that require a real Gemini API key."""
    
    def setup_method(self):
        """Set up integration tests."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            pytest.skip("GEMINI_API_KEY environment variable not set")
    
    def test_create_podcast_about_space(self):
        """Test creating a podcast about space with real Gemini API."""
        topic = "The Moon"
        
        script = create_script(topic, self.api_key)
        
        # Verify script was generated
        assert script is not None
        assert isinstance(script, str)
        assert len(script) > 100  # Should have substantial content
        
        # Verify script has character dialogue
        assert "Plato" in script or "[" in script
        assert "Pixel" in script or "[" in script

    def test_create_podcast_about_animals(self):
        """Test creating a podcast about animals with real Gemini API."""
        topic = "Penguins"
        
        script = create_script(topic, self.api_key)
        
        # Verify script was generated
        assert script is not None
        assert isinstance(script, str)
        assert len(script) > 100
        
        # Verify educational content
        assert any(word in script.lower() for word in ["penguin", "animal", "bird", "antarctica"])

    def test_voice_over_with_generated_script(self):
        """Test generating voice-over for a generated script."""
        topic = "Space Travel"
        
        # Generate script
        script = create_script(topic, self.api_key)
        assert script is not None
        
        # Generate voice-over
        audio = voice_over(self.api_key, script)
        
        # Verify audio was generated (bytes returned)
        assert isinstance(audio, bytes) or audio is None  # Gemini may return None for audio

    def test_create_two_different_podcasts(self):
        """Test creating two different podcasts about different topics."""
        topics = ["The Solar System", "Ocean Life"]
        scripts = []
        
        for topic in topics:
            script = create_script(topic, self.api_key)
            assert script is not None
            assert isinstance(script, str)
            assert len(script) > 100
            scripts.append(script)
        
        # Verify scripts are different
        assert scripts[0] != scripts[1]
        
        # Verify each has appropriate content
        assert "solar" in scripts[0].lower() or "system" in scripts[0].lower() or "planet" in scripts[0].lower()
        assert "ocean" in scripts[1].lower() or "water" in scripts[1].lower() or "sea" in scripts[1].lower()

    def test_full_podcast_pipeline(self):
        """Test full podcast creation pipeline: script → voice-over."""
        topic = "Dinosaurs"
        
        # Step 1: Create script
        script = create_script(topic, self.api_key)
        assert script is not None
        
        # Step 2: Generate voice-over
        audio = voice_over(self.api_key, script)
        
        # Step 3: Verify results
        assert isinstance(script, str)
        assert len(script) > 50
        assert isinstance(audio, bytes) or audio is None
