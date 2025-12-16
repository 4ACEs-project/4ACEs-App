#!/usr/bin/env python
import sys
from pathlib import Path
import os

# This script uses gTTS as an example Text-to-Speech engine.
# You can replace it with any other TTS library.
# Make sure to install it first: pip install gTTS
from gtts import gTTS


def main():
    """
    Generates MP3 files from a tts_{lang}.txt file using a TTS engine.
    """
    if len(sys.argv) != 2:
        print("Usage: python generate_tts_audio.py <lang_code>")
        print("Example: python generate_tts_audio.py sr")
        return

    lang_code = sys.argv[1]

    project_root = Path(__file__).parent.parent
    tts_file_path = project_root / "tts" / f"tts_{lang_code}.txt"
    output_dir = project_root / "tts" / lang_code

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    if not tts_file_path.exists():
        print(f"Error: TTS file not found at {tts_file_path}")
        return

    with open(tts_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        parts = line.split(' ', 1)
        if len(parts) != 2:
            print(f"Skipping invalid line: {line}")
            continue

        symbol_name = parts[0]
        sentence = parts[1].strip('"')

        output_file_path = output_dir / f"{symbol_name}.mp3"

        print(f"Generating TTS for '{sentence}' -> {output_file_path}")

        # --- TTS Generation ---
        # This part uses gTTS. You can replace it with your preferred TTS library.
        try:
            tts = gTTS(text=sentence, lang=lang_code, slow=False)
            tts.save(output_file_path)
        except Exception as e:
            print(f"Error generating TTS for '{sentence}': {e}")
        # --- End of TTS Generation ---


if __name__ == "__main__":
    main()
