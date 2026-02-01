"""Character profile definitions for MindQuest."""

from dataclasses import dataclass


@dataclass
class CharacterProfile:
    """A character profile with voice and speech characteristics."""

    name: str
    voice_persona: str
    speech_characteristics: str


# Predefined character profiles
PLATO = CharacterProfile(
    name="Plato",
    voice_persona="Wise Professor",
./    speech_characteristics=(
        "Slow, deliberate, explanatory, and calm. Uses sophisticated language "
        "but explains complex concepts in child-friendly terms."
    ),
)

PIXEL = CharacterProfile(
    name="Pixel",
    voice_persona="10-year-old Child",
    speech_characteristics=(
        "Fast, playful, expressive, includes laughter and high energy. "
        "Asks curious questions and shows genuine wonder."
    ),
)
