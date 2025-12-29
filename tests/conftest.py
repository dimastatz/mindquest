"""
Pytest configuration and fixtures.
"""

import pytest
from pathlib import Path


@pytest.fixture
def sample_chapter():
    """Fixture providing a sample chapter for testing."""
    return {
        "title": "Sample Chapter",
        "content": "This is sample content for testing purposes.",
        "questions": [
            "What is the main topic?",
            "Why is this important?",
            "How can you apply this?",
        ],
        "answers": [
            "The main topic is testing.",
            "It ensures code quality.",
            "By writing comprehensive tests.",
        ],
    }


@pytest.fixture
def sample_minibook():
    """Fixture providing a sample mini-book for testing."""
    return {
        "topic": "Testing",
        "language": "en",
        "title": "Testing for Kids",
        "chapters": [
            {
                "title": "Chapter 1: Introduction",
                "content": "Welcome to testing!",
                "questions": ["What is testing?"],
                "answers": ["Testing verifies code works correctly."],
            },
            {
                "title": "Chapter 2: Best Practices",
                "content": "Always write tests first.",
                "questions": ["Why test first?"],
                "answers": ["It clarifies requirements."],
            },
        ],
    }
