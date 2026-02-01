"""Unified podcast production studio for MindQuest.

Consolidates script generation, voice synthesis, and podcast creation.
"""

import re
from pathlib import Path
from typing import List, Tuple

from mindquest.utils import search_wikikids, get_wikikids_summary
from mindquest.utils.chatgpt import (
    generate_script_with_chatgpt,
    generate_audio_with_chatgpt,
)


# ============================================================================
# Script Generation
# ============================================================================


def create_script(api_key: str, topic: str, number_of_words: int = 500) -> str:
    """
    Generate an educational podcast script for children.

    This function:
    1. Searches WikiKids for age-appropriate information about the topic
    2. Uses ChatGPT-4 LLM to synthesize the data into a conversational script
    3. Returns the script featuring Plato (wise professor) and Pixel (curious kid)

    Args:
        api_key: OpenAI API key (must be provided as parameter, not hardcoded).
        topic: The educational topic for the podcast.
        number_of_words: Target word count for the script (default: 500).

    Returns:
        A conversational podcast script as a string.

    Raises:
        ValueError: If topic is empty or api_key is not provided.
    """
    if not api_key or not isinstance(api_key, str):
        raise ValueError("API key must be provided")

    if not topic or not isinstance(topic, str) or topic.strip() == "":
        raise ValueError("Topic must be a non-empty string")

    topic = topic.strip()

    # Gather factual information from WikiKids
    summary = get_wikikids_summary(topic)
    search_results = search_wikikids(topic, max_results=3)

    context = f"""
Summary:
{summary}

Search Results:
{search_results}

Target Word Count: {number_of_words}
"""

    # Generate conversational script using ChatGPT
    script = generate_script_with_chatgpt(topic, context, api_key)

    return script


# ============================================================================
# Voice Synthesis
# ============================================================================


def parse_script_segments(script: str) -> List[Tuple[str, str]]:
    """
    Parse a script to identify speaker segments.

    Args:
        script: The podcast script with [Character] tags.

    Returns:
        A list of tuples (character_name, dialogue).
    """
    # Pattern to match [Character] Speaker: dialogue
    pattern = r"\[(\w+)\]\s*[:\-]?\s*(.+?)(?=\[|\Z)"
    matches = re.findall(pattern, script, re.DOTALL)

    segments = []
    for character, dialogue in matches:
        # Clean up dialogue
        dialogue = dialogue.strip()
        if dialogue:
            segments.append((character, dialogue))

    return segments


def voice_over(api_key: str, script: str, languages: str = "en") -> bytes:
    """
    Generate audio synthesis from a podcast script.

    This function:
    1. Parses the input script to identify speaker segments
    2. Generates Text-to-Speech audio using OpenAI TTS API
    3. Returns the final audio file as bytes

    Args:
        api_key: OpenAI API key (passed as parameter, not hardcoded).
        script: The podcast script with speaker annotations.
        languages: Comma-separated language codes (default: "en" for English).

    Returns:
        Audio file as bytes.

    Raises:
        ValueError: If api_key or script is empty.
        RuntimeError: If audio generation fails.
    """
    if not api_key or not isinstance(api_key, str):
        raise ValueError("API key must be provided")

    if not script or not isinstance(script, str) or script.strip() == "":
        raise ValueError("Script must be a non-empty string")

    # Parse script segments
    segments = parse_script_segments(script)

    if not segments:
        raise ValueError("No valid script segments found in the script")

    # Generate audio for each segment
    audio_segments: List[bytes] = []

    for character, dialogue in segments:
        try:
            # Generate audio with emotional annotation based on character
            audio_bytes = generate_audio_with_chatgpt(
                script=dialogue,
                character=character,
                api_key=api_key,
                language=languages.split(",")[0].strip(),
            )

            if audio_bytes:
                audio_segments.append(audio_bytes)
        except Exception as exception:
            raise RuntimeError(
                f"Failed to generate audio for {character}: {str(exception)}"
            ) from exception

    # Combine audio segments (placeholder implementation)
    # In a real implementation, this would concatenate audio files
    if audio_segments:
        combined_audio = b"".join(audio_segments)
    else:
        # Fallback: return empty bytes if no audio was generated
        combined_audio = b""

    return combined_audio


def extract_character_audio(
    script: str, character: str, api_key: str, language: str = "en"
) -> bytes:
    """
    Extract and generate audio for a specific character in the script.

    Args:
        script: The podcast script.
        character: The character name to extract.
        api_key: OpenAI API key.
        language: Language code for speech generation.

    Returns:
        Audio file as bytes for the specified character.

    Raises:
        ValueError: If character not found in script.
        RuntimeError: If audio generation fails.
    """
    segments = parse_script_segments(script)

    character_segments = [dialogue for char, dialogue in segments if char == character]

    if not character_segments:
        raise ValueError(f"No dialogue found for character: {character}")

    combined_dialogue = " ".join(character_segments)

    return generate_audio_with_chatgpt(
        script=combined_dialogue,
        character=character,
        api_key=api_key,
        language=language,
    )


# ============================================================================
# Podcast Production
# ============================================================================


def generate_podcast(
    topic: str,
    api_key: str,
    output_file: str = "podcast.mp3",
    word_count: int = 700,
    languages: str = "en",
) -> str:
    """
    Generate a complete educational podcast on a given topic.

    Args:
        topic: The educational topic for the podcast.
        api_key: OpenAI API key.
        output_file: Output file path for the generated audio.
        word_count: Target word count for the script (default: 700 for ~5 mins).
        languages: Comma-separated language codes (default: "en" for English).

    Returns:
        Path to the generated podcast file.

    Raises:
        ValueError: If topic or api_key is invalid.
        RuntimeError: If generation fails.
    """
    print(f"🎙️  Generating podcast on: {topic}")
    print("=" * 60)

    # Generate script (5 min ≈ 700 words at ~140 wpm)
    print("\n📝 Creating script...")
    try:
        script = create_script(api_key, topic, number_of_words=word_count)
        print(f"✓ Script generated ({len(script)} characters)")
        print("\n--- Script Preview ---")
        print(script[:500] + "...\n")
    except Exception as exc:  # pylint: disable=broad-except
        raise RuntimeError(f"Script generation failed: {exc}") from exc

    # Generate audio
    print("\n🎵 Generating audio...")
    try:
        audio_bytes = voice_over(api_key, script, languages=languages)
        print(f"✓ Audio generated ({len(audio_bytes)} bytes)")
    except Exception as exc:  # pylint: disable=broad-except
        raise RuntimeError(f"Audio generation failed: {exc}") from exc

    # Save to file
    output_path = Path(output_file)
    try:
        with open(output_path, "wb") as file:  # pylint: disable=unspecified-encoding
            file.write(audio_bytes)
        print(f"✓ Podcast saved to: {output_path.absolute()}")
        print("=" * 60)
        print("🎙️  Podcast ready! ✨")
        return str(output_path.absolute())
    except Exception as exc:  # pylint: disable=broad-except
        raise RuntimeError(f"Failed to save podcast: {exc}") from exc
