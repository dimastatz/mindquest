<div align="center">
<h1 align="center">  MindQuest </h1> 
<h3>AI-Powered Kids’ Podcast Platform</br></h3>
<img src="https://img.shields.io/badge/Progress-1%25-red"> <img src="https://img.shields.io/badge/Feedback-Welcome-green">
</br>
</br>
<kbd>
<img src="./docs/imgs/mindquest.png" width="256px"> 
</kbd>
</div>

## Mini-Book Generator (Kids 8–12)

Create a kid-friendly mini-book PDF from a topic, using Simple Wikipedia as a primary source and optionally an LLM for expansion/translation.

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Generate a Book

```bash
python -m mindquest.make_minibook "Robotics" -l en -o docs/series/robotics
```

- Default: 7 chapters (~2000 words each) with 3 questions per chapter and an answers appendix.
- Output files: `<Topic>-for-Kids-(Ages-8–12)-<lang>.md` and a PDF (if `pandoc/tectonic` or `LibreOffice` are available).

To enable LLM (OpenAI):

```bash
export OPENAI_API_KEY=your_key
# optional
export OPENAI_MODEL=gpt-4o-mini
```

Disable LLM with `--no-llm`.

### PDF Rendering

- LTR languages: `pandoc` + `tectonic` if available.
- RTL languages (he, ar, fa, ur): HTML + `soffice --headless` for robust right-to-left output.

Install tools (macOS):

```bash
brew install pandoc tectonic
brew install --cask libreoffice
```

### Licensing

Wikipedia content is CC BY-SA 4.0. The generator includes attribution; share derivative works under compatible terms.

## 1. Executive Summary

**MindQuest** is an AI-driven platform that generates engaging, educational, and age-appropriate podcasts for children aged 6–12. By combining Large Language Models (LLMs), high-quality Text-to-Speech (TTS) technology, and curated educational content (e.g., Wikipedia), MindQuest transforms verified facts into fun, interactive audio stories.  

The platform aims to make learning **screen-free, safe, and enjoyable**, while providing parents and educators with a reliable source of educational audio content.

---

## 2. Problem Statement

- Children are increasingly consuming content online, but much of it is entertainment-focused and lacks educational value.  
- Creating high-quality educational audio content at scale is resource-intensive and time-consuming for educators and media producers.  
- Parents and teachers need **trustworthy, safe, and engaging audio content** for children that adapts to different ages and learning styles.

---

## 3. Proposed Solution

MindQuest offers:  

1. **Automated Podcast Generation** – LLMs create short stories and lessons from curated educational sources.  
2. **High-Quality Audio** – TTS converts text into natural, expressive voices suitable for children.  
3. **Age-Appropriate Design** – Episodes are tailored for different reading levels and attention spans.  
4. **Safety & Accuracy** – Multi-layer moderation (automated + human-in-the-loop) ensures factual correctness and child-safe content.  
5. **Parental Transparency** – Clear attribution, optional episode previews, and minimal data collection.

---

## 4. Key Features

- **Content Pipeline:** Wikipedia & vetted sources → LLM script generation → TTS → moderation → podcast distribution.  
- **Episode Structure:** Hook → simplified facts → short dialogue → reflective question/exercise.  
- **Platform Flexibility:** On-demand episodes, subscription bundles, classroom integration, or branded partnerships.  
- **Metrics & Insights:** Listenership, retention, drop-off points, parental feedback.

---

## 5. Technology Stack

| Component | Suggested Technology |
|-----------|--------------------|
| LLM | OpenAI, Gemini, LLaMA |
| TTS | Google Cloud TTS, Amazon Polly, ElevenLabs, Kokoro |
| Moderation | OpenAI moderation + human review |
| Hosting & Distribution | Heroku |
| Analytics | Telegram, Youtube, or podcast platforms analytics |

---

## 6. Roadmap

**Phase 1 (0–2 months):** Build MVP with 5 pilot episodes, integrate Wikipedia extraction, LLM generation, and TTS.  
**Phase 2 (2–4 months):** Add moderation, age-based controls, and analytics dashboard.  
**Phase 3 (4–6 months):** Closed beta release, parental testing, feedback collection.  
**Phase 4 (6–12 months):** Public launch, platform scalability, integration with education partners, subscription or licensing model.

---

## 7. Success Metrics

- Episode completion rate >80%  
- Positive parental feedback ≥90%  
- Safety and accuracy: 0 critical content issues per 100 episodes  
- User engagement: >10k listens in first 3 months of beta

---

## 8. Benefits & Impact

- Scalable, cost-effective educational content for children.  
- Encourages curiosity, learning, and cognitive development.  
- Provides parents and educators a trusted tool for safe, screen-free entertainment.  
- Establishes a unique brand in the growing educational podcast space.

---
