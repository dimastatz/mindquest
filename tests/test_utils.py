"""Tests for utility modules."""

import pytest
from unittest.mock import patch, MagicMock
from mindquest.utils import search_wikikids, get_wikikids_summary
from mindquest.utils.gemini import initialize_gemini, generate_script_with_gemini


class TestWikiKidsIntegration:
    """Test suite for WikiKids integration."""

    def test_search_wikikids_success(self):
        """Test successful search on WikiKids."""
        with patch("mindquest.utils.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "query": {
                    "search": [
                        {
                            "title": "Solar System",
                            "snippet": "The <span class='searchmatch'>solar system</span> consists of eight planets."
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
        with patch("mindquest.utils.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"query": {"search": []}}
            mock_get.return_value = mock_response
            
            result = search_wikikids("xyz1234567890", max_results=1)
            
            assert "No results found" in result

    def test_search_wikikids_multiple_results(self):
        """Test search with multiple results."""
        with patch("mindquest.utils.requests.get") as mock_get:
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
        with patch("mindquest.utils.requests.get") as mock_get:
            import requests
            mock_get.side_effect = requests.RequestException("Network error")
            
            result = search_wikikids("test")
            
            assert "Error searching WikiKids" in result

    def test_get_wikikids_summary_success(self):
        """Test successful summary retrieval."""
        with patch("mindquest.utils.requests.get") as mock_get:
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
        with patch("mindquest.utils.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "query": {
                    "pages": {
                        "12345": {}
                    }
                }
            }
            mock_get.return_value = mock_response
            
            result = get_wikikids_summary("xyz123")
            
            assert "No information found" in result

    def test_get_wikikids_summary_network_error(self):
        """Test summary with network error."""
        with patch("mindquest.utils.requests.get") as mock_get:
            import requests
            mock_get.side_effect = requests.RequestException("Network error")
            
            result = get_wikikids_summary("test")
            
            assert "Error fetching WikiKids" in result


class TestGeminiIntegration:
    """Test suite for Google Gemini integration."""

    def test_initialize_gemini(self):
        """Test Gemini initialization."""
        with patch("mindquest.utils.gemini.genai.configure") as mock_configure:
            initialize_gemini("test-api-key")
            
            mock_configure.assert_called_once_with(api_key="test-api-key")

    def test_generate_script_with_gemini_success(self):
        """Test successful script generation."""
        with patch("mindquest.utils.gemini.genai.GenerativeModel") as mock_model_class:
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "[Plato]: Let's learn about space.\n[Pixel]: Cool!"
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            with patch("mindquest.utils.gemini.initialize_gemini"):
                result = generate_script_with_gemini(
                    "Solar System",
                    "Background info about the solar system",
                    "test-api-key"
                )
                
                assert "[Plato]" in result
                assert "[Pixel]" in result
                mock_model.generate_content.assert_called_once()

    def test_generate_audio_with_gemini_success(self):
        """Test successful audio generation."""
        with patch("mindquest.utils.gemini.genai.GenerativeModel") as mock_model_class:
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "Audio generated"
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            with patch("mindquest.utils.gemini.initialize_gemini"):
                from mindquest.utils.gemini import generate_audio_with_gemini
                result = generate_audio_with_gemini(
                    "Test dialogue",
                    "Plato",
                    "test-api-key",
                    "en"
                )
                
                assert result is None  # Current implementation returns None
                mock_model.generate_content.assert_called_once()

    def test_generate_audio_with_gemini_pixel_voice(self):
        """Test audio generation with Pixel character."""
        with patch("mindquest.utils.gemini.genai.GenerativeModel") as mock_model_class:
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "Audio"
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            with patch("mindquest.utils.gemini.initialize_gemini"):
                from mindquest.utils.gemini import generate_audio_with_gemini
                generate_audio_with_gemini(
                    "Wow that's cool!",
                    "Pixel",
                    "test-api-key"
                )
                
                call_args = mock_model.generate_content.call_args[0]
                prompt = call_args[0]
                assert "playful" in prompt.lower() or "energetic" in prompt.lower() or "excited" in prompt.lower()

    def test_generate_audio_with_gemini_error_handling(self):
        """Test error handling in audio generation."""
        with patch("mindquest.utils.gemini.genai.GenerativeModel") as mock_model_class:
            mock_model = MagicMock()
            mock_model.generate_content.side_effect = Exception("API error")
            mock_model_class.return_value = mock_model
            
            with patch("mindquest.utils.gemini.initialize_gemini"):
                from mindquest.utils.gemini import generate_audio_with_gemini
                result = generate_audio_with_gemini(
                    "Test",
                    "Plato",
                    "test-api-key"
                )
                
                assert result is None

