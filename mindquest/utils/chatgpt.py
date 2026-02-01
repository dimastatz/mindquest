"""ChatGPT API integration for script and audio generation."""

from openai import OpenAI


def generate_script_with_chatgpt(
    topic: str, context: str, api_key: str, language: str = "en"
) -> str:
    """
    Generate a podcast script using ChatGPT.

    Args:
        topic: The educational topic for the podcast.
        context: Background information from WikiKids.
        api_key: OpenAI API key.
        language: Language code for script generation (default: "en" for English).

    Returns:
        A conversational podcast script with [Plato] and [Pixel] characters.

    Raises:
        RuntimeError: If API call fails.
    """
    try:
        client = OpenAI(api_key=api_key)

        # Language names mapping for better prompts
        language_names = {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "ja": "Japanese",
            "zh": "Chinese",
            "ar": "Arabic",
            "he": "Hebrew",
            "hi": "Hindi",
        }
        lang_name = language_names.get(language, language.upper())

        prompt = f"""Generate a podcast script in {lang_name} for children aged 8-12 about "{topic}".

The script should feature two characters:
- Plato: A wise, old professor who explains concepts
- Pixel: A curious, funny 10-year-old kid who asks questions

Use the following context:
{context}

Format the script with character names in brackets like [Plato] and [Pixel].
Make it engaging, educational, and fun for kids.
Target around 500 words.
Write the entire script in {lang_name}."""

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
    script: str,
    character: str,
    api_key: str,
    language: str = "en",  # pylint: disable=unused-argument
) -> bytes:
    """
    Generate audio bytes using OpenAI TTS API.

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
            "Plato": "onyx",  # Deep, calm voice
            "Pixel": "shimmer",  # Bright, energetic voice
        }

        voice = voice_config.get(character, "shimmer")

        # Use OpenAI TTS API to generate actual audio
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=script,
        )

        # Return the audio bytes directly
        return response.content
    except Exception as exception:
        raise RuntimeError(
            f"Failed to generate audio with OpenAI TTS: {str(exception)}"
        ) from exception
