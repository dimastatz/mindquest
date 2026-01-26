"""Type definitions for MindQuest."""

from dataclasses import dataclass


@dataclass
class CharacterProfile:
    """Profile for a podcast character."""
    name: str
    voice_persona: str
    speech_characteristics: str


# Character definitions
PLATO = CharacterProfile(
    name="Plato",
    voice_persona="Wise Professor",
    speech_characteristics="Slow, deliberate, explanatory, and calm.",
)

PIXEL = CharacterProfile(
    name="Pixel",
    voice_persona="10-year-old Child",
    speech_characteristics="Fast, playful, expressive; includes laughter and high energy.",
)
