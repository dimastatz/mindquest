"""Integration tests for ebook creation workflow."""

import os
import pytest
from mindquest.studio import create_minibook


@pytest.mark.integration
def test_ebook_creation_integration():
    """
    Integration test for creating a mini-book.
    Requires OPENAI_API_KEY to be set in the environment.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set, skipping integration test")

    topic = "The History of Printing"
    language = "en"
    number_of_chapters = 2  # Keep it small to save costs/time

    # We'll run it and check the return value.
    try:
        output_path = create_minibook(
            api_key=api_key,
            topic=topic,
            language=language,
            number_of_chapters=number_of_chapters,
        )

        assert output_path is not None
        assert os.path.exists(output_path)
        assert output_path.endswith(".epub") or output_path.endswith(".pdf")

        # Clean up is handled by tmp_path if we wrote there, but create_minibook might write to CWD.
        # If it writes to CWD, we should probably clean it up.
        if os.path.exists(output_path):
            os.remove(output_path)

    except Exception as error:  # pylint: disable=broad-exception-caught
        pytest.fail(f"Mini-book creation failed with error: {error}")
