"""Pytest configuration for MindQuest tests."""

import os
import pytest


def pytest_collection_modifyitems(config, items):  # pylint: disable=unused-argument
    """Modify test collection to skip integration tests if GEMINI_API_KEY not set."""
    if not os.getenv("GEMINI_API_KEY"):
        skip_integration = pytest.mark.skip(
            reason="GEMINI_API_KEY environment variable not set"
        )
        for item in items:
            if "TestGeminiIntegration" in item.nodeid:
                item.add_marker(skip_integration)
