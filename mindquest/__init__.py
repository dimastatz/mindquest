"""MindQuest: Automated Kids' Podcast Studio.

A Python library that automates the end-to-end production of educational
podcasts tailored for children aged 8-12.
"""

from mindquest.script import create_script
from mindquest.voice import voice_over

__version__ = "0.1.0"

__all__ = [
    "create_script",
    "voice_over",
]
