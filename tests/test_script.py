"""Tests for script generation functionality."""

import pytest
from unittest.mock import patch, MagicMock
from mindquest.script import create_script


class TestCreateScript:
    """Test suite for the create_script function."""

    def test_create_script_valid_topic(self):
        """Test script creation with a valid topic."""
        topic = "Solar System"
        api_key = "test-api-key"
        
        with patch("mindquest.script.get_wikikids_summary") as mock_summary, \
             patch("mindquest.script.search_wikikids") as mock_search, \
             patch("mindquest.script.generate_script_with_gemini") as mock_generate:
            
            mock_summary.return_value = "The solar system consists of the Sun and eight planets."
            mock_search.return_value = "**Solar System**: Information about planets and stars..."
            mock_generate.return_value = "[Plato]: The solar system is...\n[Pixel]: That's cool!"
            
            result = create_script(topic, api_key)
            
            assert result is not None
            assert isinstance(result, str)
            assert len(result) > 0
            mock_summary.assert_called_once_with(topic)
            mock_search.assert_called_once()
            mock_generate.assert_called_once()

    def test_create_script_empty_topic(self):
        """Test script creation with empty topic raises ValueError."""
        with pytest.raises(ValueError, match="Topic must be a non-empty string"):
            create_script("", "test-api-key")

    def test_create_script_none_topic(self):
        """Test script creation with None topic raises ValueError."""
        with pytest.raises(ValueError, match="Topic must be a non-empty string"):
            create_script(None, "test-api-key")

    def test_create_script_missing_api_key(self):
        """Test script creation without API key raises ValueError."""
        with pytest.raises(ValueError, match="API key must be provided"):
            create_script("Solar System", None)

    def test_create_script_empty_api_key(self):
        """Test script creation with empty API key raises ValueError."""
        with pytest.raises(ValueError, match="API key must be provided"):
            create_script("Solar System", "")

    def test_create_script_strips_whitespace(self):
        """Test that topic whitespace is properly stripped."""
        topic = "  Solar System  "
        api_key = "test-api-key"
        
        with patch("mindquest.script.get_wikikids_summary") as mock_summary, \
             patch("mindquest.script.search_wikikids") as mock_search, \
             patch("mindquest.script.generate_script_with_gemini") as mock_generate:
            
            mock_summary.return_value = "Summary"
            mock_search.return_value = "Results"
            mock_generate.return_value = "Script"
            
            result = create_script(topic, api_key)
            
            # Verify the topic was stripped before passing to WikiKids
            assert mock_summary.call_args[0][0] == "Solar System"

    def test_create_script_passes_context_to_gemini(self):
        """Test that WikiKids data is passed as context to Gemini."""
        topic = "Dinosaurs"
        api_key = "test-api-key"
        
        with patch("mindquest.script.get_wikikids_summary") as mock_summary, \
             patch("mindquest.script.search_wikikids") as mock_search, \
             patch("mindquest.script.generate_script_with_gemini") as mock_generate:
            
            mock_summary.return_value = "Dinosaurs were ancient reptiles."
            mock_search.return_value = "**Dinosaur**: Extinct reptile species."
            mock_generate.return_value = "Script content"
            
            result = create_script(topic, api_key)
            
            # Verify context was built and passed to generate_script_with_gemini
            call_args = mock_generate.call_args
            context = call_args[0][1]
            assert "Dinosaurs were ancient reptiles" in context
            assert "Dinosaur" in context

