import sys
from pathlib import Path


def main():
    """
    Scans the common and language-specific symbols directories, extracts the symbol words,
    and generates a text file with a pre-written symbol for a generative AI.
    """
    if len(sys.argv) > 1:
        target_language = sys.argv[1]
    else:
        target_language = "[TARGET LANGUAGE]"

    # Define paths relative to the script's location
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    lang_dir = script_dir / target_language

    if not lang_dir.is_dir():
        print(f"Error: Language directory not found at '{lang_dir}'")
        print(
            "Please create the directory and add your language-specific files "
            "before running this script."
            )
        return

    common_symbols_dir = project_root / "frontend" / "static" / "symbols" / "common"
    lang_symbols_dir = lang_dir / "symbols"
    output_md_path = lang_dir / "prompts_sentences_symbols.md"

    symbol_words = []

    # Extract symbol words from common symbols
    if common_symbols_dir.is_dir():
        for p in sorted(common_symbols_dir.iterdir()):
            if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif"}:
                symbol_word = p.stem.capitalize()
                symbol_words.append(symbol_word)

    # Extract symbol words from language-specific symbols
    if lang_symbols_dir.is_dir():
        for p in sorted(lang_symbols_dir.iterdir()):
            if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif"}:
                symbol_word = p.stem.capitalize()
                symbol_words.append(symbol_word)

    if not symbol_words:
        print("No symbol image files found.")
        return

    # Create the content for the symbol file
    symbol_header = (
        "For each of the following words, please generate two simple, "
        f"descriptive sentences in {target_language}. "
        "The sentences should be suitable for a language learning game for "
        "people with cognitive decline.\n"
    )
    word_list = "\nWord list:\n" + "\n".join([f"- {word}" for word in symbol_words])
    json_format_example = '''

Please format the output as a JSON object, where the key is the English word and the value is an array of the two sentences.
Don't use any Markdown formatting like **.
For example:
```json
{
  "Apple": ["Sentence 1 in target language.", "Sentence 2 in target language."],
  "Bike": ["Sentence 1 in target language.", "Sentence 2 in target language."]
}
```
'''

    file_content = f"{symbol_header}{word_list}\n{json_format_example}"

    # Write the content to the output file
    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write(file_content)

    print(f"Successfully generated prompt for creating sentences for symbols to '{output_md_path}'")


if __name__ == "__main__":
    main()
