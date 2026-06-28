"""
AI Language Translation Tool — Flask Application
=================================================
A full-stack web application for translating text across 100+ languages.
Built with Flask (backend) + HTML/CSS/JS (frontend) + SQLite (database).

Routes
------
GET  /           → Serve the main HTML page
POST /translate   → Translate text
GET  /history     → Retrieve translation history
DELETE /history   → Clear all history
POST /tts         → Generate TTS audio (server-side fallback)
GET  /languages   → List all supported languages

Author : CodeAlpha AI Internship — Task 1
"""

from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS

from config import (
    SECRET_KEY,
    DEBUG,
    HOST,
    PORT,
    MAX_CHAR_LIMIT,
    LANGUAGE_NAMES,
    LANGUAGE_MAP,
)
from services.translator import TranslationEngine
from services.tts_service import TTSService
from database.models import add_translation, get_history, clear_history

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = SECRET_KEY
CORS(app)

# ---------------------------------------------------------------------------
# Service instances
# ---------------------------------------------------------------------------

engine = TranslationEngine()
tts = TTSService()

# ---------------------------------------------------------------------------
# Routes — Pages
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    """Serve the main translation page."""
    return render_template(
        "index.html",
        languages=LANGUAGE_NAMES,
        language_map=LANGUAGE_MAP,
    )


# ---------------------------------------------------------------------------
# Routes — Translation API
# ---------------------------------------------------------------------------


@app.route("/translate", methods=["POST"])
def translate():
    """
    Translate text.

    Expects JSON: { "text": str, "source": str, "target": str }
    Returns JSON:  TranslationResult dict
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid request body."}), 400

    text = (data.get("text") or "").strip()
    source = data.get("source", "Auto-Detect")
    target = data.get("target", "Spanish")

    # Validation
    if not text:
        return jsonify({"success": False, "error": "Please enter text to translate."}), 400

    if len(text) > MAX_CHAR_LIMIT:
        return jsonify({
            "success": False,
            "error": f"Text exceeds the {MAX_CHAR_LIMIT:,} character limit.",
        }), 400

    if target not in LANGUAGE_MAP:
        return jsonify({"success": False, "error": "Please select a valid target language."}), 400

    auto_detect = source == "Auto-Detect"
    if not auto_detect and source not in LANGUAGE_MAP:
        return jsonify({"success": False, "error": "Please select a valid source language."}), 400

    # Translate
    result = engine.translate(
        text=text,
        source_lang=source,
        target_lang=target,
        auto_detect=auto_detect,
    )

    # Persist to database on success
    if result.success:
        add_translation(
            source_text=text,
            translated_text=result.translated_text,
            source_language=result.source_language,
            target_language=result.target_language,
        )

    status_code = 200 if result.success else 500
    return jsonify(result.to_dict()), status_code


# ---------------------------------------------------------------------------
# Routes — History API
# ---------------------------------------------------------------------------


@app.route("/history", methods=["GET"])
def history():
    """Return recent translation history."""
    limit = request.args.get("limit", 20, type=int)
    limit = min(limit, 50)  # Cap at 50
    entries = get_history(limit)
    return jsonify({"history": entries, "count": len(entries)})


@app.route("/history", methods=["DELETE"])
def history_clear():
    """Clear all translation history."""
    deleted = clear_history()
    return jsonify({"success": True, "message": f"Cleared {deleted} translation(s)."})


# ---------------------------------------------------------------------------
# Routes — Text-to-Speech API
# ---------------------------------------------------------------------------


@app.route("/tts", methods=["POST"])
def text_to_speech():
    """
    Generate TTS audio (server-side fallback).

    Expects JSON: { "text": str, "lang": str, "slow": bool }
    Returns:       audio/mpeg binary stream
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request body."}), 400

    text = (data.get("text") or "").strip()
    lang = data.get("lang", "English")
    slow = data.get("slow", False)

    if not text:
        return jsonify({"error": "No text provided."}), 400

    # Validate gTTS language support
    gtts_code_map = {"he": "iw", "jv": "jw"}
    lang_code = LANGUAGE_MAP.get(lang, "en")
    lang_code = gtts_code_map.get(lang_code.lower(), lang_code)
    try:
        from gtts.lang import tts_langs
        if lang_code not in tts_langs() and lang_code.split("-")[0] not in tts_langs():
            return jsonify({"error": f"Text-to-speech is not supported for {lang}."}), 400
    except Exception:
        # Fallback to direct attempt if gtts imports/checks fail
        pass

    audio_bytes = tts.generate_audio(text=text, lang_name=lang, slow=slow)
    if audio_bytes is None:
        return jsonify({"error": "Text-to-speech generation failed."}), 500

    return Response(audio_bytes, mimetype="audio/mpeg")


# ---------------------------------------------------------------------------
# Routes — Languages API
# ---------------------------------------------------------------------------


@app.route("/languages", methods=["GET"])
def languages():
    """Return all supported languages."""
    return jsonify({
        "languages": LANGUAGE_NAMES,
        "count": len(LANGUAGE_NAMES),
    })


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found."}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error."}), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)
