#!/usr/bin/env python
import sys
import json
from pathlib import Path
import shutil


def main():
    """
    Integrates a new language into the application.
    """
    if len(sys.argv) != 3:
        print("Usage: python integrate_language.py <LanguageName> <lang_code>")
        print("Example: python integrate_language.py Serbian sr")
        return

    lang_name = sys.argv[1]
    lang_code = sys.argv[2]

    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    lang_dir = script_dir / lang_name

    # Define paths
    translated_ui_path = lang_dir / "translated_ui.txt"
    generated_sentences_path = lang_dir / "generated_sentences.json"
    flag_icon_path = lang_dir / f"{lang_code}.svg"
    mp3_source_dir = project_root / "tts" / lang_code
    symbols_source_dir = lang_dir / "symbols"

    locales_dir = project_root / "frontend" / "static" / "locales"
    langs_dir = project_root / "frontend" / "static" / "langs"
    mp3_dest_dir = project_root / "frontend" / "static" / "mp3s" / lang_code
    symbols_dest_dir = project_root / "frontend" / "static" / "symbols" / lang_code

    output_locale_path = locales_dir / f"{lang_code}.json"

    # Check if source files exist
    if not lang_dir.is_dir():
        print(f"Error: Language directory not found at {lang_dir}")
        return
    if not translated_ui_path.exists():
        print(f"Error: translated_ui.txt not found in {lang_dir}")
        return
    if not generated_sentences_path.exists():
        print(f"Error: generated_sentences.json not found in {lang_dir}")
        return
    if not flag_icon_path.exists():
        print(f"Error: {lang_code}.svg not found in {lang_dir}")
        return

    # Create the locale JSON file
    locale_data = {}

    # Read UI translations from the original English file to get the keys
    en_locale_path = locales_dir / "en.json"
    if not en_locale_path.exists():
        print(f"Error: en.json not found at {en_locale_path}")
        return

    with open(en_locale_path, 'r', encoding='utf-8') as f:
        en_data = json.load(f)

    sentence_keys = {k.replace("_sentences", "") for k in en_data if k.endswith("_sentences")}
    ui_keys = [k for k in en_data if not k.endswith("_sentences") and k not in sentence_keys]

    with open(translated_ui_path, 'r', encoding='utf-8') as f:
        ui_translations = [line.strip() for line in f.readlines()]

    if len(ui_keys) != len(ui_translations):
        print("Error: Mismatch between the number of UI keys and translated strings.")
        print(f"UI keys ({len(ui_keys)}): {ui_keys}")
        print(f"UI translations ({len(ui_translations)}): {ui_translations}")
        return

    for key, translation in zip(ui_keys, ui_translations):
        locale_data[key] = translation

    # Add sentences from generated_sentences.json
    with open(generated_sentences_path, 'r', encoding='utf-8') as f:
        sentences_data = json.load(f)

    # Add translations for the symbol names themselves
    for key in sentences_data:
        locale_data[key.lower()] = key.replace('_', ' ').title()

    # Add sentences for each symbol
    for key, value in sentences_data.items():
        locale_data[f"{key.lower()}_sentences"] = value

    # Write the new locale file
    with open(output_locale_path, 'w', encoding='utf-8') as f:
        json.dump(locale_data, f, ensure_ascii=False, indent=2)

    print(f"Successfully created {output_locale_path}")

    # Move the flag icon
    shutil.copy(flag_icon_path, langs_dir / f"{lang_code}.svg")
    print(f"Successfully copied {flag_icon_path} to {langs_dir}")

    # Move the mp3 files
    if mp3_source_dir.is_dir():
        mp3_dest_dir.mkdir(parents=True, exist_ok=True)
        for mp3_file in mp3_source_dir.glob("*.mp3"):
            shutil.copy(mp3_file, mp3_dest_dir / mp3_file.name)
        print(f"Successfully copied MP3s from {mp3_source_dir} to {mp3_dest_dir}")
    else:
        print(f"Warning: MP3 source directory not found at {mp3_source_dir}")

    # Move the symbol images
    if symbols_source_dir.is_dir():
        symbols_dest_dir.mkdir(parents=True, exist_ok=True)
        for symbol_file in symbols_source_dir.glob("*.png"):
            shutil.copy(symbol_file, symbols_dest_dir / symbol_file.name)
        for symbol_file in symbols_source_dir.glob("*.jpg"):
            shutil.copy(symbol_file, symbols_dest_dir / symbol_file.name)
        for symbol_file in symbols_source_dir.glob("*.jpeg"):
            shutil.copy(symbol_file, symbols_dest_dir / symbol_file.name)
        for symbol_file in symbols_source_dir.glob("*.gif"):
            shutil.copy(symbol_file, symbols_dest_dir / symbol_file.name)
        print(f"Successfully copied symbols from {symbols_source_dir} to {symbols_dest_dir}")
    else:
        print(f"Warning: Symbols source directory not found at {symbols_source_dir}")


if __name__ == "__main__":
    main()
