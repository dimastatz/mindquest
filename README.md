<div align="center">
<h1 align="center">🎙️ MindQuest</h1> 
<h3>Automated AI-Powered Educational Podcast Studio for Kids (Ages 8–12)</h3>
<img src="https://img.shields.io/badge/Status-Active-green"> <img src="https://img.shields.io/badge/Coverage-95.92%25-brightgreen"> <img src="https://img.shields.io/badge/Pylint-10.0%2F10-brightgreen">
<br><br>
<kbd>
<img src="./docs/imgs/mindquest.png" width="256px"> 
</kbd>
</div>

---

## Overview

**MindQuest** is a Python-based podcast production studio that automatically generates engaging, educational podcasts for children aged 8–12. It combines:

- **Educational Content** from WikiKids (age-appropriate information)
- **AI Script Generation** using ChatGPT-4 to create engaging dialogues
- **Natural Voice Synthesis** using OpenAI's TTS API
- **Character-Based Storytelling** featuring two distinct personalities:
  - **Plato**: A wise, calm professor who explains concepts
  - **Pixel**: A curious, energetic 10-year-old asking questions

The entire system is built with **pure functional programming**, comprehensive testing, and production-grade code quality.

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/mindquest.git
cd mindquest

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Generate Your First Podcast

```python
import os
from mindquest import generate_podcast

api_key = os.getenv("OPENAI_API_KEY")

# Generate a 5-minute English podcast about Solar System
generate_podcast(
    topic="Solar System",
    api_key=api_key,
    output_file="podcast.mp3",
    word_count=700,
    languages="en"
)
```

**Result:** A professional 2.5 MB MP3 podcast ready to listen!

### Generate in Different Languages

```python
# Hebrew podcast about Drones
generate_podcast("Drones", api_key, "podcast_he.mp3", languages="he")

# Spanish podcast about Ancient Egypt
generate_podcast("Ancient Egypt", api_key, "podcast_es.mp3", languages="es")

# Multilingual (English, Spanish, French)
generate_podcast("Dinosaurs", api_key, languages="en,es,fr")
```

---

## Architecture

### Core Modules

**[mindquest/studio.py](mindquest/studio.py)** - Main production engine with:

```python
create_script()           # Generate educational scripts from WikiKids
parse_script_segments()   # Extract character dialogues
voice_over()              # Synthesize audio from scripts
extract_character_audio() # Generate audio for specific characters
generate_podcast()        # Complete end-to-end podcast production
```

**[mindquest/utils/chatgpt.py](mindquest/utils/chatgpt.py)** - OpenAI integration:
- Script generation via ChatGPT-4
- Audio synthesis via OpenAI TTS API

**[mindquest/utils/wikikids.py](mindquest/utils/wikikids.py)** - Content sourcing:
- WikiKids API integration for age-appropriate facts
- Information gathering and summarization

**[mindquest/types.py](mindquest/types.py)** - Character profiles:
- PLATO: Wise Professor (onyx voice - deep, calm)
- PIXEL: Curious Child (shimmer voice - bright, energetic)

---

## API Reference

### `generate_podcast()`

Generate a complete educational podcast.

```python
generate_podcast(
    topic: str,           # Educational topic (e.g., "Dinosaurs")
    api_key: str,        # OpenAI API key
    output_file: str = "podcast.mp3",  # Output MP3 file path
    word_count: int = 700,              # Script length (700 ≈ 5 mins)
    languages: str = "en"               # Language code(s)
) -> str                 # Returns path to generated podcast
```

**Example:**
```python
path = generate_podcast("Space Exploration", api_key, "my_podcast.mp3")
print(f"Podcast saved to: {path}")
```

### `create_script()`

Generate just the podcast script (without audio).

```python
create_script(
    api_key: str,
    topic: str,
    number_of_words: int = 500
) -> str
```

### `voice_over()`

Convert script to audio with character voices.

```python
voice_over(
    api_key: str,
    script: str,
    languages: str = "en"
) -> bytes
```

---

## Quality Metrics

✅ **Test Coverage:** 95.92% (37 comprehensive tests)  
✅ **Code Quality:** 10.00/10 Pylint score  
✅ **Testing Framework:** pytest with pure function tests  
✅ **Type Hints:** Full type annotation coverage  
✅ **Error Handling:** Comprehensive exception handling with descriptive messages

### Running Tests

```bash
# Run all tests
python -m pytest tests/test_all.py -v

# Run with coverage report
python -m pytest tests/test_all.py --cov=mindquest --cov-report=term-missing

# Full validation (formatting, linting, tests)
./run.sh -local
```

---

## Example Workflows

### Workflow 1: Generate English Podcast

```python
from mindquest import generate_podcast
import os

api_key = os.getenv("OPENAI_API_KEY")
generate_podcast("The Water Cycle", api_key, "water_cycle.mp3")
```

### Workflow 2: Extract Character Audio

```python
from mindquest import create_script, extract_character_audio
import os

api_key = os.getenv("OPENAI_API_KEY")

# Create script
script = create_script(api_key, "Ancient Rome", 600)

# Generate only Plato's audio
plato_audio = extract_character_audio(script, "Plato", api_key)

with open("plato_only.mp3", "wb") as f:
    f.write(plato_audio)
```

### Workflow 3: Custom Language with Specific Word Count

```python
from mindquest import generate_podcast
import os

api_key = os.getenv("OPENAI_API_KEY")

# 3-minute French podcast (~420 words at 140 wpm)
generate_podcast(
    topic="Marie Curie",
    api_key=api_key,
    output_file="marie_curie_fr.mp3",
    word_count=420,
    languages="fr"
)
```

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.9+ |
| **LLM** | OpenAI ChatGPT-4 |
| **TTS** | OpenAI TTS API |
| **Content** | WikiKids |
| **Testing** | pytest, pytest-cov |
| **Code Quality** | pylint, black, type hints |
| **Package Manager** | pip |

---

## File Structure

```
mindquest/
├── __init__.py              # Package exports
├── studio.py               # Main production engine (all functionality)
├── types.py                # Character profile definitions
└── utils/
    ├── __init__.py
    ├── chatgpt.py          # OpenAI API integration
    └── wikikids.py         # WikiKids content sourcing

tests/
└── test_all.py             # 37 comprehensive tests

docs/
├── requirements.md         # Original requirements
└── series/                 # Example podcast content

requirements.txt            # Project dependencies
README.md                   # This file
```

---

## Dependencies

- **openai** ≥1.0.0 - OpenAI API client
- **requests** ≥2.31.0 - HTTP library for WikiKids
- **beautifulsoup4** ≥4.12.0 - HTML parsing for content extraction
- **pytest** ≥7.4.0 - Testing framework
- **pytest-cov** ≥4.1.0 - Coverage reporting
- **black** - Code formatting
- **pylint** - Code linting

---

## Environment Setup

### Set OpenAI API Key

```bash
# macOS/Linux
export OPENAI_API_KEY=your_actual_key_here

# Windows (PowerShell)
$env:OPENAI_API_KEY="your_actual_key_here"
```

### Verify Installation

```bash
python -c "from mindquest import generate_podcast; print('✅ MindQuest ready!')"
```

---

## Features

✨ **Automatic Podcast Generation**
- End-to-end pipeline from topic to MP3
- No manual script writing required
- Real-time progress feedback

🎭 **Character-Based Learning**
- Two distinct characters with different personalities
- Natural dialogue flow for engagement
- Character-specific voices (Plato: calm/explanatory, Pixel: energetic/curious)

🌍 **Multilingual Support**
- English, Spanish, French, German, Hebrew, Arabic, and more
- Language parameter for voice synthesis
- Compatible with OpenAI's TTS language support

📚 **Educational Content**
- WikiKids integration for age-appropriate information
- Factual, verified content sources
- Context-aware script generation

🔧 **Production-Grade Quality**
- 95%+ test coverage
- 10.0/10 code quality score
- Full error handling and validation
- Type hints throughout codebase

---

## Roadmap

- [ ] Add support for multiple voice options per character
- [ ] Implement audio concatenation for proper multi-segment synthesis
- [ ] Add subtitle/transcript generation
- [ ] Support for custom character profiles
- [ ] Batch podcast generation API
- [ ] Web UI for podcast creation
- [ ] Distribution to podcast platforms (Spotify, Apple Podcasts)

---

## Contributing

Contributions welcome! Please ensure:

1. All tests pass: `python -m pytest tests/test_all.py`
2. Coverage maintained: >95%
3. Code formatted: `black mindquest/`
4. Linting passes: `pylint mindquest/`

---

## License

MIT License - See LICENSE file for details

---

## Acknowledgments

- **WikiKids API** - Educational content source
- **OpenAI** - ChatGPT and TTS APIs
- **Children's Learning Research** - Pedagogical principles
