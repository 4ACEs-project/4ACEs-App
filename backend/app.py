from flask import Flask, jsonify, session, send_from_directory, request
from flask_cors import CORS
import random
from pathlib import Path
from functools import wraps
import json
import re

# Serve static assets (CSS, JS, images) under the "/static" URL prefix.
app = Flask(__name__, static_folder="../frontend", static_url_path="")
app.secret_key = "replace-this-secret"
# Allow CORS for development; in production restrict origins.
CORS(app)

# ---------------------------------------------------------------------------
# Highscore persistence (simple file based).
# ---------------------------------------------------------------------------
HIGH_SCORE_FILE = Path(__file__).parent / "highscore.txt"


def _load_highscore() -> int:
    try:
        return int(HIGH_SCORE_FILE.read_text().strip())
    except Exception:
        return 0


def _save_highscore(score: int) -> None:
    HIGH_SCORE_FILE.write_text(str(score))

# ---------------------------------------------------------------------------
# Dynamically build the symbol-image list from files in ``frontend/static``.
# ---------------------------------------------------------------------------


def _load_symbol_image_list(lang: str = 'en') -> list:
    """Scan ``frontend/static/symbols`` for image files and return a list of dicts."""
    result = []

    # Always load common symbols
    common_static_dir = Path(app.static_folder) / "static" / "symbols" / "common"
    if common_static_dir.is_dir():
        for p in common_static_dir.iterdir():
            if p.suffix.lower() not in {".png", ".jpg", ".jpeg", ".gif"}:
                continue
            symbol = p.stem.lower()
            result.append({"symbol": symbol, "image": f"/static/symbols/common/{p.name}"})

    # Load language-specific symbols
    lang_static_dir = Path(app.static_folder) / "static" / "symbols" / lang
    if lang_static_dir.is_dir():
        for p in lang_static_dir.iterdir():
            if p.suffix.lower() not in {".png", ".jpg", ".jpeg", ".gif"}:
                continue
            symbol = p.stem.lower()
            result.append({"symbol": symbol, "image": f"/static/symbols/{lang}/{p.name}"})

    return result


def _load_polish_sentence_data() -> list:
    """Load Polish sentence data."""
    result = []

    # Load sentences from pl.json
    locales_dir = Path(app.static_folder) / "static" / "locales"
    pl_json_path = locales_dir / "pl.json"
    if not pl_json_path.exists():
        return []

    with open(pl_json_path, 'r', encoding='utf-8') as f:
        pl_data = json.load(f)

    # Load images
    lang_static_dir = Path(app.static_folder) / "static" / "symbols" / "pl"
    if not lang_static_dir.is_dir():
        return []

    images_by_sentence = {}
    for p in lang_static_dir.iterdir():
        if p.suffix.lower() not in {".png", ".jpg", ".jpeg", ".gif"}:
            continue

        match = re.match(r"sentence(\d+)_(\w+)", p.stem)
        if match:
            sentence_num = match.group(1)
            image_type = match.group(2)

            if sentence_num not in images_by_sentence:
                images_by_sentence[sentence_num] = {}

            images_by_sentence[sentence_num][image_type] = f"/static/symbols/pl/{p.name}"

    for num, images in images_by_sentence.items():
        sentence_key = f"sentence_{num}"
        if sentence_key in pl_data and "right" in images and "wrong_a" in images and "wrong_b" in images:
            result.append({
                "sentence_key": sentence_key,
                "sentence": pl_data[sentence_key],
                "options": [images["right"], images["wrong_a"], images["wrong_b"]],
                "correct": images["right"],
            })

    return result


def set_language(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        lang = request.args.get('lang')
        print(f"ROUTE: {request.path}, lang={lang}, session={session}")
        if lang:
            session['lang'] = lang
            print(f"ROUTE: {request.path}, session after set={session}")
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
@set_language
def index():
    """Serve the main application page."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/language')
@set_language
def language_page():
    """Serve the main application page."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/game')
@set_language
def game_page():
    """Serve the main application page."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/set_lang/<lang>')
def set_lang_api(lang):
    session['lang'] = lang
    print(f"API/SET_LANG: session after set={session}")
    return jsonify({"success": True})


@app.route('/api/get_lang')
def get_lang_api():
    lang = session.get('lang', 'en')
    return jsonify({"lang": lang})


@app.route('/api/languages')
def get_languages():
    """Return a list of available languages, sorted alphabetically."""
    langs_dir = Path(app.static_folder) / "static" / "langs"
    all_languages = []
    if langs_dir.is_dir():
        for f in langs_dir.glob("*.svg"):
            lang_code = f.stem
            if lang_code == 'us':  # Convert 'us.svg' to 'en' language code
                all_languages.append('en')
            else:
                all_languages.append(lang_code)

    all_languages.sort()  # Sort all languages alphabetically
    languages = all_languages  # No special handling for 'en'

    return jsonify(languages)


@app.route('/api/next')
def next_symbol():
    """Return the next round data."""
    round_num = session.get('round', 0)
    if round_num >= 10:
        session.pop('round', None)
        session.pop('pl_sentences', None)
        return jsonify({"finished": True})

    lang = session.get('lang', 'en')
    print(f"API/NEXT: lang from session={lang}")

    if lang == 'pl':
        if 'pl_sentences' not in session:
            sentences = _load_polish_sentence_data()
            if not sentences:
                return jsonify({"error": "No Polish sentence data found."}), 500
            random.shuffle(sentences)
            session['pl_sentences'] = sentences

        pl_sentences = session['pl_sentences']
        if round_num >= len(pl_sentences):
            session.pop('round', None)
            session.pop('pl_sentences', None)
            return jsonify({"finished": True})

        target = pl_sentences[round_num]
        random.shuffle(target["options"])

        session['round'] = round_num + 1

        return jsonify({
            "sentence_key": target["sentence_key"],
            "sentence": target["sentence"],
            "options": target["options"],
            "correct": target["correct"],
            "finished": False,
        })

    else:
        symbols = _load_symbol_image_list(lang)

        if len(symbols) < 3:
            return jsonify({
                "error": "Not enough images in frontend/static/symbols/common (need ≥3)."
                }), 500

        target = random.choice(symbols)
        distractors = random.sample([p for p in symbols if p != target], 2)
        options = [target["image"]] + [d["image"] for d in distractors]
        random.shuffle(options)

        session['round'] = round_num + 1

        return jsonify({
            "symbol": target["symbol"],
            "options": options,
            "correct": target["image"],
            "finished": False,
        })


@app.route('/api/quit')
def quit_game():
    session.pop('round', None)
    session.pop('pl_sentences', None)
    return jsonify({"success": True})


@app.route('/api/highscore')
def get_highscore():
    return jsonify({"highscore": _load_highscore()})


@app.route('/api/submit', methods=['POST'])
def submit_score():
    data = request.get_json(silent=True) or {}
    score = int(data.get('score', 0))
    current = _load_highscore()
    if score > current:
        _save_highscore(score)
        current = score
    return jsonify({"highscore": current})


if __name__ == "__main__":
    _save_highscore(0)  # Erase highscore on startup
    app.run(host="0.0.0.0", port=5000, debug=True)
