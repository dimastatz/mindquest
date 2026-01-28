"""ChatGPT integration utilities for MindQuest."""

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


def generate_script_with_chatgpt(topic: str, context: str, api_key: str) -> str:
    """
    Generate a podcast script using ChatGPT-4.

    This is a pure function that takes input and returns a script without side effects.

    Args:
        topic: The educational topic for the podcast.
        context: Background information from WikiKids.
        api_key: OpenAI API key.

    Returns:
        A conversational podcast script with [Plato] and [Pixel] characters.

    Raises:
        ValueError: If inputs are invalid.
        RuntimeError: If API call fails.
    """
    if not api_key or not isinstance(api_key, str):
        raise ValueError("Valid API key must be provided")

    if not topic or not isinstance(topic, str):
        raise ValueError("Topic must be a non-empty string")

    if OpenAI is None:
        raise RuntimeError(
            "OpenAI package not installed. Install with: pip install openai"
        )

    try:
        client = OpenAI(api_key=api_key)

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
            "3. About 3-5 minutes of dialogue\n"
            "4. Engaging and fun while educational\n\n"
            "Start the script now:"
        )

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert children's podcast writer. Create "
                        "engaging, educational content for kids aged 8-12."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=2000,
        )

        script = response.choices[0].message.content
        return script

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
    Generate audio bytes from script text using ChatGPT's multimodal capabilities.

    This is a pure function that generates audio without side effects.

    Args:
        script: The dialogue text to convert to speech.
        character: The character name (Plato or Pixel) for voice selection.
        api_key: OpenAI API key.
        language: Language code (default: "en").

    Returns:
        Audio data as bytes.

    Raises:
        ValueError: If inputs are invalid.
        RuntimeError: If API call fails.
    """
    if not api_key or not isinstance(api_key, str):
        raise ValueError("Valid API key must be provided")

    if not script or not isinstance(script, str):
        raise ValueError("Script must be a non-empty string")

    if not character or not isinstance(character, str):
        raise ValueError("Character must be specified")

    if OpenAI is None:
        raise RuntimeError(
            "OpenAI package not installed. Install with: pip install openai"
        )

    try:
        client = OpenAI(api_key=api_key)

        # Map character to voice and emotional tone
        voice_config = {
            "Plato": {
                "voice": "onyx",  # Deep, wise voice
                "speed": 0.9,  # Slower for explanation
                "description": "old, wise professor with a calm, deliberate tone",
            },
            "Pixel": {
                "voice": "nova",  # Bright, expressive voice
                "speed": 1.1,  # Faster, more energetic
                "description": "curious, funny, excited 10-year-old kid",
            },
        }

        config = voice_config.get(character, voice_config["Plato"])

        # Use TTS endpoint (language parameter reserved for future multi-language support)
        # Currently, ChatGPT TTS works best with the input language detected from script
        response = client.audio.speech.create(
            model="tts-1-hd", voice=config["voice"], input=script, speed=config["speed"]
        )

        # Read audio content as bytes
        audio_bytes = response.content
        return audio_bytes

    except Exception as exception:
        raise RuntimeError(
            f"Failed to generate audio with ChatGPT: {str(exception)}"
        ) from exception


def combine_audio_segments(audio_segments: list) -> bytes:
    """
    Combine multiple audio byte segments into a single audio file.

    Pure function for audio concatenation.

    Args:
        audio_segments: List of audio byte objects.

    Returns:
        Combined audio bytes.
    """
    if not audio_segments:
        return b""

    # For now, simple concatenation (WAV/MP3 would need proper header handling)
    combined = b"".join(audio_segments)
    return combined
