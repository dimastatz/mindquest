"""ChatGPT API integration for script and audio generation."""

import requests
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
    """
    try:
        client = OpenAI(api_key=api_key)

        prompt = (
            f"Generate a podcast script in language code {language} for "
            f"children aged 8-12 about '{topic}'.\n\n"
            "The script should feature two characters:\n"
            "- Plato: A wise, old professor who explains concepts calmly.\n"
            "- Pixel: A curious, funny kid who asks questions.\n\n"
            "Use the following context gathered from WikiKids:\n"
            f"{context}\n\n"
            "Format the script with character names in brackets like [Plato].\n"
            "Make it engaging, educational, and fun for kids.\n"
            "Target around 500 words.\n"
            f"Ensure the entire script is in language {language}."
        )

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000,
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
    language: str = "en",
) -> bytes:
    """
    Generate audio bytes using OpenAI TTS API.
    """
    try:
        client = OpenAI(api_key=api_key)
        _ = language

        # Map characters to OpenAI TTS voices
        voice_map = {
            "Plato": "onyx",
            "Pixel": "shimmer",
        }

        voice = voice_map.get(character, "nova")

        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=script,
        )

        return response.content
    except Exception as exception:
        raise RuntimeError(
            f"Failed to generate audio with OpenAI TTS: {str(exception)}"
        ) from exception


def generate_minibook_with_chatgpt(
    topic: str,
    context: str,
    api_key: str,
    language: str = "en",
    number_of_chapters: int = 7,
) -> str:
    """
    Generate a mini-book using ChatGPT.
    """
    try:
        client = OpenAI(api_key=api_key)

        prompt = (
            f"Generate a comprehensive mini-book in language code {language} for "
            f"children aged 8-12 about '{topic}'.\n\n"
            "The mini-book must:\n"
            "1. Start with a Table of Contents.\n"
            f"2. Include {number_of_chapters} chapters.\n"
            "3. Each chapter should be around 200-300 words.\n"
            "4. Each chapter must conclude with 3 knowledge assessment questions.\n"
            "5. Include a section for a 'Mind Map' placeholder.\n"
            "6. Format with markdown headers (# for title, ## for chapters).\n\n"
            "Use this context from WikiKids:\n"
            f"{context}\n\n"
            f"Write the entire mini-book in language {language}."
        )

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4000,
        )

        return response.choices[0].message.content
    except Exception as exception:
        raise RuntimeError(
            f"Failed to generate mini-book with ChatGPT: {str(exception)}"
        ) from exception


def generate_cover_image_with_dalle(topic: str, api_key: str) -> bytes:
    """
    Generate a Pixar-style cover image using DALL-E 3.

    Args:
        topic: The topic of the book.
        api_key: OpenAI API key.

    Returns:
        Image bytes.
    """
    try:
        client = OpenAI(api_key=api_key)

        prompt = (
            f"A cute, vibrant, 3D Pixar-style movie poster illustration for a "
            f"children's educational book about '{topic}'. "
            "Colorful, engaging, high quality, suitable for 8-12 year olds."
        )

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url
        if not image_url:
            raise RuntimeError("No image URL returned from DALL-E")

        # Download the image
        image_response = requests.get(image_url, timeout=30)
        image_response.raise_for_status()

        return image_response.content

    except Exception as exception:
        raise RuntimeError(
            f"Failed to generate cover image with DALL-E: {str(exception)}"
        ) from exception
