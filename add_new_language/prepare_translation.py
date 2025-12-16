import json
from pathlib import Path


def main():
    """
    Extracts UI string values from the en.json locale file and saves them
    to a text file to be used as input for translation services.
    """
    # Define paths relative to the script's location
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    en_json_path = project_root / "frontend" / "static" / "locales" / "en.json"
    output_txt_path = script_dir / "translation_input.txt"

    # Check if the source file exists
    if not en_json_path.exists():
        print(f"Error: Source file not found at {en_json_path}")
        return

    # Read the JSON file
    with open(en_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract the values, ignoring sentence arrays
    values_to_translate = []
    for key, value in data.items():
        if isinstance(value, str) and key[0].islower():
            values_to_translate.append(value)

    # Write the values to the output file, separated by newlines
    with open(output_txt_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(values_to_translate))

    # Print a success message
    print(f"Successfully extracted UI strings to '{output_txt_path}'")


if __name__ == "__main__":
    main()
