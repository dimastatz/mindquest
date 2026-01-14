import pytest
from unittest.mock import patch, MagicMock
from mindquest import studio


def test_plan_series(api_key, llm_response, expected_result, expected_error):
    """Parameterized test for plan_series handling success and various error cases."""
    theme = "Space"
    
    if expected_error:
        # If we expect an error, we check if it raises ValueError
        if not api_key:
             with pytest.raises(ValueError, match=expected_error):
                studio.plan_series(theme, api_key=api_key)
        else:
            mock_response = MagicMock()
            mock_response.text = llm_response
            
            with patch('google.genai.Client') as mock_client_class:
                mock_client = mock_client_class.return_value
                mock_client.models.generate_content.return_value = mock_response
                
                with pytest.raises(ValueError, match=expected_error):
                    studio.plan_series(theme, api_key=api_key)
    else:
        # Success case
        mock_response = MagicMock()
        mock_response.text = llm_response
        
        with patch('google.genai.Client') as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_client.models.generate_content.return_value = mock_response
            
            result = studio.plan_series(theme, api_key=api_key)
            
            assert result == expected_result
            mock_client.models.generate_content.assert_called_once()

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