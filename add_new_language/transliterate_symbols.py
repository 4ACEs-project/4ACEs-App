import json
import re
from pathlib import Path
import os
import sys

# Define a comprehensive Cyrillic to Latin transliteration map for Macedonian and Serbian
language_transliteration_maps = {
    "mk": {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ж': 'z', 'з': 'z', 'и': 'i',
        'ј': 'j', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's',
        'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'c', 'ш': 's',

        # Macedonian specific
        'ѓ': 'g', 'ќ': 'k', 'ѕ': 'z', 'џ': 'dz', 'љ': 'lj', 'њ': 'nj',

        # Capital letters (assuming same mapping, just capitalized)
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ж': 'Z', 'З': 'Z', 'И': 'I',
        'Ј': 'J', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S',
        'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H', 'Ц': 'C', 'Ч': 'C', 'Ш': 'S',

        'Ѓ': 'G', 'Ќ': 'K', 'Ѕ': 'Z', 'Џ': 'Dz', 'Љ': 'Lj', 'Њ': 'Nj',
    },
    "sr": {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'ђ': 'dj', 'е': 'e', 'ж': 'z', 'з': 'z', 'и': 'i',
        'ј': 'j', 'k': 'k', 'л': 'l', 'љ': 'lj', 'м': 'm', 'н': 'n', 'њ': 'nj', 'о': 'o', 'п': 'p',
        'р': 'r', 'с': 's', 'т': 't', 'ћ': 'c', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'c',
        'џ': 'dz', 'ш': 's',

        # Capital letters
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Ђ': 'Dj', 'Е': 'E', 'Ж': 'Z', 'З': 'Z', 'И': 'I',
        'Ј': 'J', 'К': 'K', 'Л': 'L', 'Љ': 'Lj', 'М': 'M', 'Н': 'N', 'Њ': 'Nj', 'О': 'O', 'П': 'P',
        'Р': 'R', 'С': 'S', 'Т': 'T', 'Ћ': 'C', 'У': 'U', 'Ф': 'F', 'Х': 'H', 'Ц': 'C', 'Ч': 'C',
        'Џ': 'Dz', 'Ш': 'S',
    },
    "sk": {  # Slovak map
        'á': 'a', 'ä': 'a', 'č': 'c', 'ď': 'd', 'é': 'e', 'í': 'i', 'ľ': 'l', 'ĺ': 'l', 'ň': 'n',
        'ó': 'o', 'ô': 'o', 'ŕ': 'r', 'š': 's', 'ť': 't', 'ú': 'u', 'ý': 'y', 'ž': 'z',

        # Capital letters
        'Á': 'A', 'Ä': 'A', 'Č': 'C', 'Ď': 'D', 'É': 'E', 'Í': 'I', 'Ľ': 'L', 'Ĺ': 'L', 'Ň': 'N',
        'Ó': 'O', 'Ô': 'O', 'Ŕ': 'R', 'Š': 'S', 'Ť': 'T', 'Ú': 'U', 'Ý': 'Y', 'Ž': 'Z',
    },
    "pl": {  # Polish map
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',

        # Capital letters
        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z',
    },
    "hu": {  # Hungarian map
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ö': 'o', 'ő': 'o', 'ú': 'u', 'ü': 'u', 'ű': 'u',

        # Capital letters
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ö': 'O', 'Ő': 'O', 'Ú': 'U', 'Ü': 'U', 'Ű': 'U',
    }
}


def transliterate_text(text, char_map):
    result = []
    for char in text:
        result.append(char_map.get(char, char))
    return "".join(result)


def transliterate_filename(filename, char_map, is_mp3=False):
    stem = Path(filename).stem

    transliterated_stem = ""
    if is_mp3:
        # For mp3s, we need to handle _1, _2 suffixes
        match = re.match(r"(.+?)(_\d+)?$", stem)
        if match:
            symbol_base = match.group(1)
            suffix = match.group(2) if match.group(2) else ""
            transliterated_base = transliterate_text(symbol_base, char_map)
            transliterated_stem = f"{transliterated_base}{suffix}"
    else:
        transliterated_stem = transliterate_text(stem, char_map)

    return f"{transliterated_stem}{Path(filename).suffix}"


def process_language(lang_code, char_map):
    project_root = Path(__file__).parent

    # --- Rename image files ---
    symbols_dir = project_root / "frontend" / "static" / "symbols" / lang_code
    if symbols_dir.is_dir():
        print(f"Renaming image files in {symbols_dir}...")
        for p in symbols_dir.iterdir():
            if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif"}:
                old_name = p.name
                new_name = transliterate_filename(old_name, char_map)
                if old_name != new_name:
                    os.rename(p, p.parent / new_name)
                    print(f"  Renamed {old_name} to {new_name}")

    # --- Rename MP3 files ---
    mp3_dir = project_root / "frontend" / "static" / "mp3s" / lang_code
    if mp3_dir.is_dir():
        print(f"Renaming MP3 files in {mp3_dir}...")
        for p in mp3_dir.iterdir():
            if p.suffix.lower() == ".mp3":
                old_name = p.name
                new_name = transliterate_filename(old_name, char_map, is_mp3=True)
                if old_name != new_name:
                    os.rename(p, p.parent / new_name)
                    print(f"  Renamed {old_name} to {new_name}")

    # --- Update locale JSON file ---
    locale_path = project_root / "frontend" / "static" / "locales" / f"{lang_code}.json"
    if locale_path.exists():
        print(f"Updating locale file {locale_path}...")
        with open(locale_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        new_data = {}
        for key, value in data.items():
            new_key = key

            # Transliterate base key
            transliterated_base_key = transliterate_text(key, char_map)

            # Handle keys with _sentences suffix
            if key.endswith("_sentences"):
                base_key_without_suffix = key.replace("_sentences", "")
                transliterated_base_key_without_suffix = transliterate_text(base_key_without_suffix, char_map)
                new_key = f"{transliterated_base_key_without_suffix}_sentences"
            else:
                new_key = transliterated_base_key

            new_data[new_key] = value

        with open(locale_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        print(f"  Updated keys in {locale_path}")

    # --- Update TTS text file ---
    tts_path = project_root / "tts" / f"tts_{lang_code}.txt"
    if tts_path.exists():
        print(f"Updating TTS text file {tts_path}...")
        with open(tts_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            parts = line.split(" ", 1)
            if len(parts) > 1:
                key_part = parts[0]
                sentence_part = parts[1]

                # Handle keys like "ајвар_1"
                match = re.match(r"(.+?)(_\d+)?$", key_part)
                if match:
                    symbol_base = match.group(1)
                    suffix = match.group(2) if match.group(2) else ""
                    transliterated_base = transliterate_text(symbol_base, char_map)
                    new_key_part = f"{transliterated_base}{suffix}"
                    new_lines.append(f"{new_key_part} {sentence_part}")
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        with open(tts_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"  Updated keys in {tts_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transliterate_symbols.py <lang_code1> [<lang_code2> ...]")
        sys.exit(1)

    for lang_code in sys.argv[1:]:
        if lang_code in language_transliteration_maps:
            print(f"Processing language: {lang_code}")
            char_map = language_transliteration_maps[lang_code]
            process_language(lang_code, char_map)
        else:
            print(f"Error: No transliteration map defined for language code '{lang_code}'")
