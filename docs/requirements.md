

# Speech Project: Automated Kids' Podcast Studio

## 1. Project Overview

**Goal:** Create a Python library that automates the end-to-end production of educational podcasts tailored for children aged 8-12.
**Agent Role:** Parse this file, generate the necessary code, and iterate based on updates until the acceptance criteria are met.

## 2. Functional Requirements

### 2.1 Core Functionality

The system must expose three primary pure functions to handle script generation and audio synthesis.

#### Function: `create_minibook`

* **Signature:** `create_minibook(api_key: str, topic: str, language='en', number_of_chapters=7, format='ebub') -> str`
* **Workflow:**
1. Accept a topic string.
2. Search **WikiKids** and **Google Scholar** to gather factual, age-appropriate information.
3. Utilize **ChatGPT LLM** to synthesize the gathered data into a mini book
4. Make it accessible to 8-12 y.o. Engaging and easy to read.
5. Organize the content into chapters, each chapter of 200-300 words, with three knowledge assessment questions following each chapter. Add Table of content in the beginning and a mind map diagramm. Add a nice image pixar like on the cover.
6. Support two book formats, ebub and pdf.


#### Function: `create_script`

* **Signature:** `create_script(api_key: str, topic: str, number_of_words = 500) -> str`
* **Workflow:**
1. Accept a topic string.
2. Search **WikiKids** to gather factual, age-appropriate information.
3. Utilize **ChatGPT LLM** to synthesize the gathered data into a conversational script.


* **Character Profiles:**
* **Plato:** An old, wise professor. His role is to explain concepts, answer questions, and facilitate understanding.
* **Pixel:** A curious, funny, and excited 10-year-old kid. His role is to ask questions and express wonder until he understands the topic.



#### Function: `voice_over`

* **Signature:** `voice_over(api_key: str, script: str, language: str='en') -> bytes`
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
* 90% of the codebase must be implemented as **pure functions** (deterministic, no side effects).
* Avoid class-based OOP unless strictly necessary for state management integration.
* Do not create files in the root folder. It should stay clean. All Python scripts should go to mindquest/mindquest all test to mindquest/tests and all docs to mindquest/docs


---

## 4. Acceptance Criteria & Testing

### 4.1 Definition of Success

The task is considered complete only when the automated test script executes without errors.

### 4.2 Execution

* **Command:** `run.sh -local`
* **Condition:** The script must generate a valid script and a valid audio file based on the input topic.
* **Run.sh**: you cannot change the script run.sh. 
* **Testing:**: perform testing with pytest and keep all in one file. Do not create classes in test. It should be pure functions only.

