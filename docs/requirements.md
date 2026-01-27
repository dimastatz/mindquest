

# Speech Project: Automated Kids' Podcast Studio

## 1. Project Overview

**Goal:** Create a Python library that automates the end-to-end production of educational podcasts tailored for children aged 8-12.
**Agent Role:** Parse this file, generate the necessary code, and iterate based on updates until the acceptance criteria are met.

## 2. Functional Requirements

### 2.1 Core Functionality

The system must expose two primary pure functions to handle script generation and audio synthesis.

#### Function: `create_script`

* **Signature:** `create_script(topic: str) -> str`
* **Workflow:**
1. Accept a topic string.
2. Search **WikiKids** to gather factual, age-appropriate information.
3. Utilize **Google Gemini LLM** to synthesize the gathered data into a conversational script.


* **Character Profiles:**
* **Plato:** An old, wise professor. His role is to explain concepts, answer questions, and facilitate understanding.
* **Pixel:** A curious, funny, and excited 10-year-old kid. His role is to ask questions and express wonder until he understands the topic.



#### Function: `voice_over`

* **Signature:** `voice_over(key: str, script: str, languages: str) -> bytes`
* **Workflow:**
1. Parse the input script to identify speaker segments.
2. Generate Text-to-Speech (TTS) audio using **Google Gemini Multimodal** capabilities.
3. Return the final audio file as bytes.


* **Voice Profiles:**

| Character | Voice Persona | Speech Characteristics |
| --- | --- | --- |
| **Plato** | Wise Professor | Slow, deliberate, explanatory, and calm. |
| **Pixel** | 10-year-old Child | Fast, playful, expressive; includes laughter and high energy. |

* **Emotional Annotation:** The TTS engine must apply emotional annotations where possible to ensure the tone (excitement, curiosity, wisdom) matches the context of the script.

---

## 3. Non-Functional Requirements

### 3.1 Technical Stack & Environment

* **Language:** Python **3.14.1**
* **Architecture:** Python Library (must be structured for deployment to PyPI).
* **AI Provider:** ChatGPT (Multimodal LLM).
* *Constraint:* The API Key must be passed as a parameter, not hardcoded.



### 3.2 Coding Standards

* **Paradigm:** **Functional Programming**.
* The majority of the codebase must be implemented as **pure functions** (deterministic, no side effects).
* Avoid class-based OOP unless strictly necessary for state management integration.
* Do not create files in the root folder. It should stay clean. All Python scripts should go to mindquest/mindquest all test to mindquest/tests and all docs to mindquest/docs


---

## 4. Acceptance Criteria & Testing

### 4.1 Definition of Success

The task is considered complete only when the automated test script executes without errors.

### 4.2 Execution

* **Command:** `run.sh -local`
* **Condition:** The script must generate a valid script and a valid audio file based on the input topic.
* **Run.sh**: you cannot change the script run.sh. If change is needed asks.