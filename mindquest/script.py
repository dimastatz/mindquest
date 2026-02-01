"""Core script generation functionality for MindQuest."""

from mindquest.utils import search_wikikids, get_wikikids_summary
from mindquest.utils.chatgpt import generate_script_with_chatgpt


def create_script(api_key: str, topic: str, number_of_words: int = 500) -> str:
    """
    Generate an educational podcast script for children.

    This function:
    1. Searches WikiKids for age-appropriate information about the topic
    2. Uses ChatGPT-4 LLM to synthesize the data into a conversational script
    3. Returns the script featuring Plato (wise professor) and Pixel (curious kid)

    Args:
        api_key: OpenAI API key (must be provided as parameter, not hardcoded).
        topic: The educational topic for the podcast.
        number_of_words: Target word count for the script (default: 500).

    Returns:
        A conversational podcast script as a string.

    Raises:
        ValueError: If topic is empty or api_key is not provided.
    """
    if not api_key or not isinstance(api_key, str):
        raise ValueError("API key must be provided")

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

Target Word Count: {number_of_words}
"""

    # Generate conversational script using ChatGPT
    script = generate_script_with_chatgpt(topic, context, api_key)

    return script
