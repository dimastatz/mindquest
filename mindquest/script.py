"""Core script generation functionality for MindQuest."""

from mindquest.utils import search_wikikids, get_wikikids_summary
from mindquest.utils.gemini import generate_script_with_gemini


def create_script(topic: str, api_key: str) -> str:
    """
    Generate an educational podcast script for children.
    
    This function:
    1. Searches WikiKids for age-appropriate information about the topic
    2. Uses Google Gemini LLM to synthesize the data into a conversational script
    3. Returns the script featuring Plato (wise professor) and Pixel (curious kid)
    
    Args:
        topic: The educational topic for the podcast.
        api_key: Google Gemini API key (must be provided as parameter, not hardcoded).
    
    Returns:
        A conversational podcast script as a string.
    
    Raises:
        ValueError: If topic is empty or api_key is not provided.
    """
    if not topic or not isinstance(topic, str) or topic.strip() == "":
        raise ValueError("Topic must be a non-empty string")
    
    if not api_key or not isinstance(api_key, str):
        raise ValueError("API key must be provided")
    
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
    script = generate_script_with_gemini(topic, context, api_key)
    
    return script
