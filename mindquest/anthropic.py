from anthropic import Anthropic

def _call_llm(prompt: str, api_key: str) -> str:
    """
    Calls Anthropic's Claude LLM.
    
    Args:
        prompt (str): The prompt to send to the LLM.
        api_key (str): The API key for authentication.

    Raises:
        ValueError: If api_key is not provided.
    """
    if not api_key:
        raise ValueError("API key is required to call the LLM.")

    client = Anthropic(api_key=api_key)
    
    message = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return message.content[0].text
