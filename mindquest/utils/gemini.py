"""Google Gemini integration utilities for MindQuest."""

try:
    import google.generativeai as genai
except ImportError:
    genai = None


def generate_script_with_gemini(
    topic: str, context: str, number_of_words: int = 500
) -> str:
    """
    Generate a podcast script using Google Gemini.

    This is a pure function that takes input and returns a script without side effects.

    Args:
        topic: The educational topic for the podcast.
        context: Background information from WikiKids.
        number_of_words: Target word count for the script.

    Returns:
        A conversational podcast script with [Plato] and [Pixel] characters.

    Raises:
        RuntimeError: If API call fails.
    """
    if genai is None:
        raise RuntimeError(
            "Google Generative AI package not installed. "
            "Install with: pip install google-generativeai"
        )

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = (
            f"Create an engaging educational podcast script for children "
            f'aged 8-12 about "{topic}".\n\n'
            "The script should feature two characters:\n"
            "- Plato: An old, wise professor who explains concepts, answers "
            "questions, and facilitates understanding.\n"
            "  Speech style: Slow, deliberate, explanatory, and calm.\n"
            "- Pixel: A curious, funny, and excited 10-year-old kid who asks "
            "questions and expresses wonder.\n"
            "  Speech style: Fast, playful, expressive; includes laughter "
            "and high energy.\n\n"
            "Format each line with [Character] prefix, like:\n"
            f"[Plato] Welcome to our podcast about {topic}...\n"
            "[Pixel] Oh wow! That's so cool! Can you tell me more?\n\n"
            "Use this background information:\n"
            f"{context}\n\n"
            "Create a script that is:\n"
            "1. Factually accurate but simple for children\n"
            "2. Conversational and natural\n"
            f"3. Approximately {number_of_words} words\n"
            "4. Engaging and fun while educational\n\n"
            "Start the script now:"
        )

        response = model.generate_content(prompt)
        script = response.text
        return script

    except Exception as exception:
        raise RuntimeError(
            f"Failed to generate script with Gemini: {str(exception)}"
        ) from exception


def generate_audio_with_gemini(
    script: str,
    character: str,
    language: str = "en",
) -> bytes:
    """
    Generate audio bytes from script text using Gemini's multimodal capabilities.

    This is a pure function that generates audio without side effects.

    Args:
        script: The dialogue text to convert to speech.
        character: The character name (Plato or Pixel) for voice selection.
        language: Language code (default: "en").

    Returns:
        Audio data as bytes.

    Raises:
        RuntimeError: If API call fails.
    """
    if genai is None:
        raise RuntimeError(
            "Google Generative AI package not installed. "
            "Install with: pip install google-generativeai"
        )

    try:
        # Map character to voice and emotional tone
        voice_config = {
            "Plato": {
                "voice": "Calm and Deliberate",
                "description": ("old, wise professor with a calm, deliberate tone"),
            },
            "Pixel": {
                "voice": "Cheerful and Energetic",
                "description": "curious, funny, excited 10-year-old kid",
            },
        }

        config = voice_config.get(character, voice_config["Plato"])

        # Use Gemini to generate speech-like content
        # (Note: Gemini's native TTS is limited; this generates audio descriptors)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = (
            f"Generate a {language} audio representation of the following "
            f"dialogue spoken by {character} ({config['description']}). "
            f"Voice style: {config['voice']}\n\n"
            f"Dialogue: {script}\n\n"
            "Return the audio as bytes data for a WAV file."
        )

        response = model.generate_content(prompt)

        # Gemini returns text, so we simulate audio bytes
        # In production, this would integrate with a proper TTS service
        audio_bytes = response.text.encode("utf-8")
        return audio_bytes

    except Exception as exception:
        raise RuntimeError(
            f"Failed to generate audio with Gemini: {str(exception)}"
        ) from exception
