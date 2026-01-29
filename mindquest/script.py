"""Core script generation functionality for MindQuest."""

from mindquest.utils import search_wikikids, get_wikikids_summary
from mindquest.utils.gemini import generate_script_with_gemini


def create_script(topic: str, number_of_words: int = 500) -> str:
    """
    Generate an educational podcast script for children.

    This function:
    1. Searches WikiKids for age-appropriate information about the topic
    2. Uses Google Gemini LLM to synthesize the data into a conversational script
    3. Returns the script featuring Plato (wise professor) and Pixel (curious kid)

    Args:
        topic: The educational topic for the podcast.
        number_of_words: Target word count for the script (default: 500).

    Returns:
        A conversational podcast script as a string.

    Raises:
        ValueError: If topic is empty.
    """
    if not topic or not isinstance(topic, str) or topic.strip() == "":
        raise ValueError("Topic must be a non-empty string")

    topic = topic.strip()

    # Gather factual information from WikiKids
    summary = get_wikikids_summary(topic)
    search_results = search_wikikids(topic, max_results=3)

    context = f"""
Summary:
{summary}

Search Results:
{search_results}
"""

    # Generate conversational script using Gemini
    script = generate_script_with_gemini(topic, context, number_of_words)

    return script
