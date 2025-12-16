#!/usr/bin/env python
import json
from pathlib import Path

def main():
    """
    Generates tts_{lang}.txt files for all locales in frontend/static/locales/.
    """
    project_root = Path(__file__).parent.parent
    locales_dir = project_root / "frontend" / "static" / "locales"
    tts_dir = project_root / "tts"

    if not locales_dir.is_dir():
        print(f"Error: Locales directory not found at {locales_dir}")
        return

    for locale_file in locales_dir.glob("*.json"):
        lang_code = locale_file.stem
        
        with open(locale_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        output_lines = []
        for key, value in data.items():
            if key.endswith("_sentences"):
                symbol_name = key.replace("_sentences", "")
                if isinstance(value, list):
                    for i, sentence in enumerate(value):
                        output_lines.append(f'{symbol_name.lower()}_{i+1} "{sentence}"')
        
        output_tts_path = tts_dir / f"tts_{lang_code}.txt"
        with open(output_tts_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(output_lines))

        print(f"Successfully generated {output_tts_path}")

if __name__ == "__main__":
    main()
