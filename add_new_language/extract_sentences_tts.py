#!/usr/bin/env python
import sys
import json
from pathlib import Path


def main():
    """
    Extracts sentences from a language's generated_sentences.json file and saves them to a text file
    in the format: symbol_name_1 "sentence"
    """
    if len(sys.argv) != 3:
        print("Usage: python extract_sentences.py <LanguageName> <lang_code>")
        print("Example: python extract_sentences.py Serbian sr")
        return

    lang_name = sys.argv[1]
    lang_code = sys.argv[2]

    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    lang_dir = script_dir / lang_name
    generated_sentences_path = lang_dir / "generated_sentences.json"

    tts_dir = project_root / "tts"
    output_tts_path = tts_dir / f"tts_{lang_code}.txt"

    if not generated_sentences_path.exists():
        print(f"Error: generated_sentences.json not found at {generated_sentences_path}")
        return

    with open(generated_sentences_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    output_lines = []
    for key, value in data.items():
        if isinstance(value, list):
            for i, sentence in enumerate(value):
                output_lines.append(f'{key.lower()}_{i + 1} "{sentence}"')

    with open(output_tts_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(output_lines))

    print(f"Successfully extracted sentences to {output_tts_path}")


if __name__ == "__main__":
    main()
