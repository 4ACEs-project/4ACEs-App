# Adding a New Language

This guide provides a step-by-step process for adding a new language to the 4ACEs WebApp. The process is semi-automated with a set of Python scripts.

## 📋 Prerequisites

-   Python 3.9+ with `gtts` and `pydub` libraries installed (`pip install gtts pydub`).
-   A generative AI tool (like [Gemini](https://gemini.google.com/) or ChatGPT) for creating sentences.
-   A translation tool (like [Google Translate](https://translate.google.com/)) for translating UI elements.

## 🚀 Process Overview

The process is divided into two main parts:

1.  **Part 1: Prepare Language Assets:** Create all the necessary text, image, and audio files for the new language.
2.  **Part 2: Integrate the New Language:** Run a script to copy all the assets into the main application structure.

---

## Part 1: Prepare Language Assets

### Step 1.1: Create Language Directory

First, create a new directory for your language within `add_new_language/`.

*   **Action:** Create a new folder: `add_new_language/{LanguageName}` (e.g., `add_new_language/Serbian`).

### Step 1.2: Generate Translation Input File for UI

To make translating the UI text (buttons, labels, etc.) easier, first generate a plain text file containing all the English strings.

*   **Run the script:**
    ```bash
    python add_new_language/prepare_translation.py
    ```
*   **Result:** This will create a `translation_input.txt` file inside the `add_new_language/` directory. This file contains only the UI text, not the game sentences.

### Step 1.3: Translate the UI Strings

1.  Open the `add_new_language/translation_input.txt` file.
2.  Copy the text and paste it into a translation service like [Google Translate](https://translate.google.com/).
3.  Save the translated UI text into a new plain text file named `translated_ui.txt` inside your language directory (e.g., `add_new_language/{LanguageName}/`).

### Step 1.4: Add Language-Specific Symbols and Flag

If your language has unique symbols that are not in the `frontend/static/symbols/common` directory, you can add them here.

*   **Action:**
    1.  Create a new folder: `add_new_language/{LanguageName}/symbols` (e.g., `add_new_language/Serbian/symbols`).
    2.  Place your language-specific symbol images (e.g., `ajvar.png`) in this new folder. You can find a wide range of symbols at [Global Symbols](https://globalsymbols.com/).
    3.  Add your language flag icon (e.g., `{lang_code}.svg`, for Serbian `sr.svg`) into your language directory (e.g., `add_new_language/{LanguageName}/`). You can download flag icons from [Flag Icons](https://flagicons.lipis.dev/).

### Step 1.5: Generate Sentences for Symbols

This step creates a helper file that you can use with a generative AI to create the descriptive sentences for each game symbol.

*   **Run the script:**
    ```bash
    python add_new_language/generate_prompt_sentences_symbols.py {LanguageName}
    ```
    e.g. for Serbian:
    ```bash
    python add_new_language/generate_prompt_sentences_symbols.py Serbian
    ```
*   **Result:** This creates a `prompts_sentences_symbols.md` file in the `add_new_language/{LanguageName}/` directory.
*   **Action:**
    1.  Open the `add_new_language/{LanguageName}/prompts_sentences_symbols.md` file.
    2.  Copy the entire text and paste it into a generative AI like the [Gemini](https://gemini.google.com/) web UI.
    3.  Save the generated JSON output to a new file named `generated_sentences.json` inside your language directory (e.g., `add_new_language/{LanguageName}/`).

### Step 1.6: Generate TTS Text File

This step extracts the sentences from your `generated_sentences.json` file into a plain text file, which will be used by the TTS generation script.

*   **Run the script:**
    ```bash
    python add_new_language/extract_sentences_tts.py <LanguageName> <lang_code>
    ```
    e.g. for Serbian:
    ```bash
    python add_new_language/extract_sentences_tts.py Serbian sr
    ```
*   **Result:** This creates a `tts_{lang_code}.txt` file in the `tts/` directory.

### Step 1.7: Generate Audio Files

This step uses a Text-to-Speech (TTS) engine (like gTTS) to convert the sentences in the `tts_{lang_code}.txt` file into MP3 audio files.

*   **Run the script:**
    ```bash
    python tts/generate_tts_audio.py <lang_code>
    ```
    e.g. for Serbian:
    ```bash
    python tts/generate_tts_audio.py sr
    ```
*   **Result:** This creates MP3 files in the `tts/{lang_code}/` directory.

---

## Part 2: Integrate the New Language

Once you have prepared all the assets, you can run the integration script.

*   **Run the script:**
    ```bash
    python add_new_language/integrate_language.py <LanguageName> <lang_code>
    ```
    e.g. for Serbian:
    ```bash
    python add_new_language/integrate_language.py Serbian sr
    ```
*   **Result:** This will:
    *   Create a new `{lang_code}.json` file in `frontend/static/locales/`.
    *   Copy the `{lang_code}.svg` flag to `frontend/static/langs/`.
    *   Copy the MP3 files from `tts/{lang_code}/` to `frontend/static/mp3s/{lang_code}/`.
    *   Copy the symbol images from `add_new_language/{LanguageName}/symbols/` to `frontend/static/symbols/{lang_code}/`.

After running the script, the new language will be available in the application.

### Language Codes

The `{lang_code}` should be a two-letter ISO 639-1 code. For example, `en` for English, `sr` for Serbian.
