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


def generate_minibook_outline(
    topic: str,
    context: str,
    api_key: str,
    language: str = "en",
    number_of_chapters: int = 7,
) -> str:
    """
    Generate an outline (list of chapters) for the mini-book.
    """
    try:
        client = OpenAI(api_key=api_key)
        prompt = (
            f"Create an outline for a children's mini-book about '{topic}' "
            f"(Language: {language}).\n"
            f"Generate exactly {number_of_chapters} chapter titles.\n"
            "Format the output as a simple numbered list (1. Title...).\n"
            "Do not include any introduction or other text, just the list of chapters.\n\n"
            f"Context:\n{context}"
        )

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as exception:
        raise RuntimeError(f"Failed to generate outline: {exception}") from exception


def generate_chapter_content(
    topic: str,
    chapter_title: str,
    context: str,
    api_key: str,
    language: str = "en",
) -> str:
    """
    Generate content for a specific chapter.
    """
    try:
        client = OpenAI(api_key=api_key)
        prompt = (
            f"Write the content for a chapter titled '{chapter_title}' "
            f"for a book about '{topic}'.\n"
            f"Target Audience: Children aged 8-12. Language: {language}.\n"
            "Requirements:\n"
            "1. Length: 250-350 words (Strictly enforce this).\n"
            "2. Tone: Educational, engaging, simple.\n"
            "3. Format: Markdown. Use '##' for the chapter title at the start.\n"
            "4. End with 3 multiple-choice assessment questions (with answers).\n\n"
            f"Context:\n{context}"
        )

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1500,
        )
        return response.choices[0].message.content
    except Exception as exception:
        raise RuntimeError(
            f"Failed to generate chapter '{chapter_title}': {exception}"
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


def generate_mindmap_image_with_dalle(topic: str, api_key: str) -> bytes:
    """
    Generate a Mind Map illustration using DALL-E 3.
    """
    try:
        client = OpenAI(api_key=api_key)
        prompt = (
            f"A simple, colorful, educational mind map illustration explaining "
            f"'{topic}' for children. "
            "Clear branches, icons, and text-like abstract shapes. White background. "
            "Cartoon style, easy to understand."
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
            raise RuntimeError("No image URL returned")

        image_response = requests.get(image_url, timeout=30)
        image_response.raise_for_status()
        return image_response.content
    except Exception as exc:
        raise RuntimeError(f"Failed to generate mind map: {exc}") from exc
