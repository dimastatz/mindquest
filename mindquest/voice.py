"""Audio synthesis and voice-over functionality for MindQuest."""

import re
from typing import List, Tuple
from mindquest.utils.chatgpt import generate_audio_with_chatgpt


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


def voice_over(key: str, script: str, languages: str = "en") -> bytes:
    """
    Generate audio synthesis from a podcast script.

    This function:
    1. Parses the input script to identify speaker segments
    2. Generates Text-to-Speech audio using ChatGPT Multimodal capabilities
    3. Returns the final audio file as bytes

    Args:
        key: OpenAI API key (passed as parameter, not hardcoded).
        script: The podcast script with speaker annotations.
        languages: Comma-separated language codes (default: "en" for English).

    Returns:
        Audio file as bytes.

    Raises:
        ValueError: If key or script is empty.
        RuntimeError: If audio generation fails.
    """
    if not key or not isinstance(key, str):
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
                api_key=key,
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
        character: The character name to extract audio for.
        api_key: OpenAI API key.
        language: Language code (default: "en").

    Returns:
        Audio bytes for the character's dialogue.
    """
    segments = parse_script_segments(script)
    character_dialogues = [dialogue for char, dialogue in segments if char == character]

    if not character_dialogues:
        raise ValueError(f"No dialogue found for character: {character}")

    combined_dialogue = " ".join(character_dialogues)

    audio_bytes = generate_audio_with_chatgpt(
        script=combined_dialogue,
        character=character,
        api_key=api_key,
        language=language,
    )

    return audio_bytes if audio_bytes else b""
