"""MindQuest: Automated Kids' Podcast Studio.

A Python library that automates the end-to-end production of educational
podcasts tailored for children aged 8-12.
"""

from mindquest.studio import (
    create_script,
    voice_over,
    parse_script_segments,
    extract_character_audio,
    generate_podcast,
)

__all__ = [
    "create_script",
    "voice_over",
    "parse_script_segments",
    "extract_character_audio",
    "generate_podcast",
]
