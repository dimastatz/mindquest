import json
from typing import List, Optional
from google import genai

"""
MindQuest Studio - Functional API

A collection of pure functions for generating educational podcast episodes and mini-books for kids.
This module handles the core content creation pipeline including theme planning,
script generation, audio production, and book creation.
"""

def _call_llm(prompt: str, api_key: str) -> str:
    """
    Calls Google's Gemini LLM using the google-genai library.
    Functional approach: no global configuration.
    
    Args:
        prompt (str): The prompt to send to the LLM.
        api_key (str): The API key for authentication.

    Raises:
        ValueError: If api_key is not provided.
    """
    if not api_key:
        raise ValueError("API key is required to call the LLM.")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt,
    )
    return response.text

def plan_series(theme: str, api_key: str) -> List[str]:
    """
    Generates a mini-series outline for a given theme.
    Functional approach: dependencies are passed as arguments.
    """
    system_instruction = (
        "You are the lead producer for 'MindQuest', a science podcast for kids (8-12). "
        "Your goal is to break down a broad theme into exciting episode topics."
    )
    
    user_prompt = (
        f"Theme: {theme}\n"
        "Task: Create a list of episode titles.\n"
        "Constraint: Return ONLY a valid JSON list of strings.\n"
    )

    full_prompt = f"{system_instruction}\n\n{user_prompt}"
    
    response_text = _call_llm(full_prompt, api_key)
    
    try:
        # Clean and parse
        clean_text = response_text.replace("```json", "").replace("```", "").strip()
        series_plan = json.loads(clean_text)
        
        if isinstance(series_plan, list):
            return series_plan
        raise ValueError("LLM response was not a list.")
            
    except (json.JSONDecodeError, Exception) as e:
        raise ValueError(f"Failed to parse LLM response: {e}")

def generate_script(topic: str) -> str:
    """
    Creates a podcast script for a specific topic.

    The script features a dialogue between:
    - **The Professor**: Calm, wise, explains from first principles.
    - **Pinocchio**: Naive, curious, asks smart questions.

    Args:
        topic (str): The specific subject of the episode (e.g., "Gravity").

    Returns:
        str: The complete dialogue script.
    """
    pass

def produce_audio(script: str) -> Optional[bytes]:
    """
    Converts the script into audio using TTS (Text-to-Speech).

    Uses distinct voices for the Professor (warm, calm) and Pinocchio (playful).

    Args:
        script (str): The text script to convert.

    Returns:
        Optional[bytes]: The audio data, or None if not implemented.
    """
    pass

def create_mini_book(topic: str, title: str, age_group: str) -> bytes:
    """
    Generates an educational mini-book in EPUB format.

    Args:
        topic (str): The subject of the book.
        title (str): The title of the book.
        age_group (str): The target age group (e.g., "8-12").

    Returns:
        bytes: The content of the generated EPUB file.
    """
    pass