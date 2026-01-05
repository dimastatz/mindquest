import pytest
from unittest.mock import patch, MagicMock
from mindquest import studio

def test_plan_series_mocked():
    """Test plan_series with a mocked LLM call."""
    theme = "Space"
    api_key = "fake_key"
    mock_response = MagicMock()
    mock_response.text = '["Episode 1", "Episode 2"]'
    
    with patch('google.genai.Client') as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.models.generate_content.return_value = mock_response
        
        result = studio.plan_series(theme, api_key=api_key)
        
        assert result == ["Episode 1", "Episode 2"]
        mock_client.models.generate_content.assert_called_once()

def test_plan_series_missing_api_key():
    """Test plan_series raises ValueError when API key is missing."""
    theme = "Space"
    # Passing empty string or None should raise ValueError
    with pytest.raises(ValueError, match="API key is required"):
        studio.plan_series(theme, api_key="")

def test_plan_series_invalid_json():
    """Test plan_series raises ValueError when LLM returns invalid JSON."""
    theme = "Space"
    api_key = "fake_key"
    mock_response = MagicMock()
    mock_response.text = "Invalid JSON"
    
    with patch('google.genai.Client') as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.models.generate_content.return_value = mock_response
        
        with pytest.raises(ValueError, match="Failed to parse LLM response"):
            studio.plan_series(theme, api_key=api_key)

def test_plan_series_json_not_list():
    """Test plan_series raises ValueError when LLM returns JSON that is not a list."""
    theme = "Space"
    api_key = "fake_key"
    mock_response = MagicMock()
    mock_response.text = '{"episodes": ["Episode 1"]}'
    
    with patch('google.genai.Client') as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.models.generate_content.return_value = mock_response
        
        with pytest.raises(ValueError, match="Failed to parse LLM response: LLM response was not a list."):
            studio.plan_series(theme, api_key=api_key)

def test_generate_script():
    """Test generate_script returns None (stub behavior)."""
    topic = "Gravity"
    result = studio.generate_script(topic)
    assert result is None

def test_produce_audio():
    """Test produce_audio returns None (stub behavior)."""
    script = "Test script"
    result = studio.produce_audio(script)
    assert result is None

def test_create_mini_book():
    """Test create_mini_book returns None (stub behavior)."""
    topic = "Drones"
    title = "Flying Robots"
    age_group = "8-12"
    result = studio.create_mini_book(topic, title, age_group)
    assert result is None
