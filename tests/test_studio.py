import pytest
from mindquest import studio

def test_plan_series():
    """Test plan_series returns None (stub behavior)."""
    theme = "Space"
    # The function is currently a stub, so it returns None.
    # We verify that it runs without error.
    result = studio.plan_series(theme)
    assert result is None

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
