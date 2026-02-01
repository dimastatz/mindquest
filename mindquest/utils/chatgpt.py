"""ChatGPT API integration for script and audio generation."""

from openai import OpenAI


def generate_script_with_chatgpt(topic: str, context: str, api_key: str) -> str:
    """
    Generate a podcast script using ChatGPT.

    Args:
        topic: The educational topic for the podcast.
        context: Background information from WikiKids.
        api_key: OpenAI API key.

    Returns:
        A conversational podcast script with [Plato] and [Pixel] characters.

    Raises:
        RuntimeError: If API call fails.
    """
    try:
        client = OpenAI(api_key=api_key)

        prompt = f"""Generate a podcast script for children aged 8-12 about "{topic}".

The script should feature two characters:
- Plato: A wise, old professor who explains concepts
- Pixel: A curious, funny 10-year-old kid who asks questions

Use the following context:
{context}

Format the script with character names in brackets like [Plato] and [Pixel].
Make it engaging, educational, and fun for kids.
Target around 500 words."""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
        )

        return response.choices[0].message.content
    except Exception as exception:
        raise RuntimeError(
            f"Failed to generate script with ChatGPT: {str(exception)}"
        ) from exception


def generate_audio_with_chatgpt(
    script: str, character: str, api_key: str, language: str = "en"
) -> bytes:
    """
    Generate audio bytes using ChatGPT multimodal capabilities.

    Args:
        script: The dialogue text to convert to speech.
        character: The character speaking (Plato or Pixel).
        api_key: OpenAI API key.
        language: Language code for speech generation.

    Returns:
        Audio file as bytes.

    Raises:
        RuntimeError: If audio generation fails.
    """
    try:
        client = OpenAI(api_key=api_key)

        # Define voice characteristics based on character
        voice_config = {
            "Plato": {
                "persona": "Wise Professor",
                "tone": "Slow, deliberate, calm, and explanatory",
            },
            "Pixel": {
                "persona": "10-year-old Child",
                "tone": "Fast, playful, expressive, excited",
            },
        }

        config = voice_config.get(character, voice_config["Pixel"])

        prompt = f"""Convert the following text to speech instructions for a voice acting model.
Character: {config['persona']}
Tone: {config['tone']}
Language: {language}
Text: {script}

Provide detailed voice direction notes but DO NOT generate actual audio bytes."""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )

        # For now, return a placeholder audio representation
        # In production, this would integrate with actual TTS service
        audio_instructions = response.choices[0].message.content
        return audio_instructions.encode("utf-8")
    except Exception as exception:
        raise RuntimeError(
            f"Failed to generate audio with ChatGPT: {str(exception)}"
        ) from exception
