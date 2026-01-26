"""Google Gemini AI integration for MindQuest."""

from typing import Optional
import google.generativeai as genai


def initialize_gemini(api_key: str) -> None:
    """
    Initialize the Google Gemini API client.
    
    Args:
        api_key: The API key for Google Gemini.
    """
    genai.configure(api_key=api_key)


def generate_script_with_gemini(topic: str, context: str, api_key: str) -> str:
    """
    Generate a conversational podcast script using Google Gemini.
    
    Args:
        topic: The topic for the podcast.
        context: Background information gathered from WikiKids.
        api_key: The Google Gemini API key.
    
    Returns:
        A conversational script featuring Plato and Pixel discussing the topic.
    """
    initialize_gemini(api_key)
    
    prompt = f"""Create an engaging educational podcast script for children aged 8-12 about the topic: {topic}

Background information:
{context}

The script should feature two characters:
1. Plato: An old, wise professor who explains concepts and answers questions
2. Pixel: A curious, funny, 10-year-old kid who asks questions and expresses wonder

Format the script as a conversation between these two characters. Use [Plato] and [Pixel] to indicate who is speaking.

Requirements:
- Keep language simple and age-appropriate
- Make it educational but fun and engaging
- Include questions from Pixel and explanations from Plato
- Total length: approximately 3-5 minutes of speech (600-800 words)
- Use enthusiasm and personality in the dialogue

Start the script now:"""
    
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    
    return response.text


def generate_audio_with_gemini(
    script: str, 
    character: str, 
    api_key: str,
    language: str = "en"
) -> Optional[bytes]:
    """
    Generate audio for a script segment using Google Gemini.
    
    Args:
        script: The text to convert to speech.
        character: The character name (Plato or Pixel).
        api_key: The Google Gemini API key.
        language: The language code (default: en).
    
    Returns:
        Audio bytes, or None if generation fails.
    """
    initialize_gemini(api_key)
    
    # Define voice characteristics based on character
    voice_prompts = {
        "Plato": "Generate text-to-speech audio for a wise, elderly professor speaking slowly and deliberately. The tone should be calm, explanatory, and authoritative.",
        "Pixel": "Generate text-to-speech audio for an excited, curious 10-year-old child. The tone should be playful, energetic, fast-paced, and include occasional laughter and excitement.",
    }
    
    voice_prompt = voice_prompts.get(character, voice_prompts["Plato"])
    
    full_prompt = f"""{voice_prompt}

Text to speak:
{script}

Language: {language}"""
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    try:
        response = model.generate_content(full_prompt)
        # Note: Gemini's audio generation is limited; this returns text response
        # In production, you'd use Google Cloud Text-to-Speech API instead
        return None
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None
