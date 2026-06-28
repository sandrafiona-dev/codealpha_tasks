# 🌐 AI-Powered Language Translation Tool

A modern, full-stack web application for translating text across **100+ languages** — built with **Python Flask** backend and **HTML/CSS/JavaScript** frontend, powered by Google Translate.

> **CodeAlpha AI Internship — Task 1**

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🌍 **100+ Languages** | Translate between over 100 languages worldwide |
| 🔍 **Auto-Detect** | Automatically detect the source language |
| 🔄 **Swap Languages** | One-click language swap with text exchange |
| 📋 **Copy to Clipboard** | Instantly copy translated text (Clipboard API) |
| 🔊 **Text-to-Speech** | Listen to translations via Web Speech API + gTTS fallback |
| 📜 **Translation History** | Persistent history stored in SQLite database |
| 🌙 **Dark/Light Mode** | Toggle themes with localStorage persistence |
| ⚡ **Fast Translation** | Responses under 2 seconds with live stats |
| 📊 **Character Counter** | Real-time counter with warning indicators |
| ⌨️ **Keyboard Shortcuts** | `Ctrl+Enter` to translate, `Escape` to close sidebar |
| 📱 **Responsive Design** | Works on desktop, tablet, and mobile |
| 🛡️ **Error Handling** | Graceful API failure handling and input validation |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10** or higher
- **pip** (Python package manager)
- Internet connection (for translations and TTS)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd "Language Translation Tool"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open your browser** at `http://localhost:5000`

---

## 📁 Project Structure

```
Language Translation Tool/
├── app.py                    # Flask application entry point
├── config.py                 # Configuration: language maps, constants
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation (this file)
├── services/
│   ├── __init__.py
│   ├── translator.py         # Translation engine (deep-translator)
│   └── tts_service.py        # Server-side TTS fallback (gTTS)
├── database/
│   ├── __init__.py
│   ├── models.py             # SQLite schema & DB operations
│   └── translations.db       # Auto-created database
├── templates/
│   └── index.html            # Main HTML page
└── static/
    ├── css/
    │   └── style.css         # Premium CSS (dark/light themes)
    └── js/
        └── script.js         # Frontend logic
```

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Backend** | Python 3.10+, Flask |
| **Database** | SQLite |
| **Translation API** | Google Translate (via `deep-translator`) |
| **Language Detection** | `langdetect` |
| **Text-to-Speech** | Web Speech API (browser) + `gTTS` (server fallback) |
| **Clipboard** | Clipboard API (browser-native) |
| **Styling** | Custom CSS (glassmorphism, gradients, animations) |

---

## 🔌 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Serve the main translation page |
| `POST` | `/translate` | Translate text between languages |
| `GET` | `/history` | Retrieve translation history |
| `DELETE` | `/history` | Clear all translation history |
| `POST` | `/tts` | Generate TTS audio (server-side fallback) |
| `GET` | `/languages` | List all supported languages |

### Example: POST /translate

```json
// Request
{
  "text": "Hello, how are you?",
  "source": "Auto-Detect",
  "target": "Spanish"
}

// Response
{
  "translated_text": "Hola, ¿cómo estás?",
  "source_language": "English",
  "target_language": "Spanish",
  "detected_language": "English",
  "elapsed_ms": 342.5,
  "success": true
}
```

---

## 📖 Usage Guide

1. **Enter text** in the source text area (left panel)
2. **Select languages** — choose source (or Auto-Detect) and target
3. **Click Translate** (or press `Ctrl+Enter`) — see instant results
4. **Copy** the translation with one click
5. **Listen** to the translation using Text-to-Speech
6. **Browse history** — click 📜 to open the sidebar
7. **Toggle theme** — click 🌙/☀️ to switch dark/light mode

---

## 🌍 Supported Languages

The tool supports **100+ languages** including:

Afrikaans, Albanian, Amharic, Arabic, Armenian, Bangla, Basque, Bosnian, Bulgarian, Catalan, Chinese (Simplified/Traditional), Croatian, Czech, Danish, Dutch, English, Estonian, Filipino, Finnish, French, Galician, Georgian, German, Greek, Gujarati, Hausa, Hebrew, Hindi, Hungarian, Icelandic, Indonesian, Irish, Italian, Japanese, Kannada, Kazakh, Khmer, Korean, Kurdish, Lao, Latin, Latvian, Lithuanian, Malay, Malayalam, Maltese, Maori, Marathi, Mongolian, Nepali, Norwegian, Pashto, Persian, Polish, Portuguese, Punjabi, Romanian, Russian, Serbian, Sinhala, Slovak, Slovenian, Somali, Spanish, Swahili, Swedish, Tamil, Telugu, Thai, Turkish, Ukrainian, Urdu, Uzbek, Vietnamese, Welsh, Yoruba, Zulu, *and many more…*

---

## 🗄️ Database Schema

```sql
CREATE TABLE translations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source_text     TEXT NOT NULL,
    translated_text TEXT NOT NULL,
    source_language VARCHAR(50) NOT NULL,
    target_language VARCHAR(50) NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## ⚠️ Error Handling

| Scenario | Message |
|----------|---------|
| Empty input | "Please enter text to translate." |
| API failure | "Translation failed: [details]" |
| Character limit | "Text exceeds the 5,000 character limit." |
| Network error | "Network error. Please check your connection." |
| TTS unavailable | Falls back to server-side gTTS silently |

---

## 🔮 Future Enhancements

- 🎤 Voice Input (Speech-to-Text)
- 🖼️ Image Translation (OCR)
- 📄 PDF Document Translation
- 💬 Real-Time Chat Translation
- ✍️ AI Grammar Correction
- 🧠 AI Language Learning Assistant

---

## 📄 License

This project is developed as part of the **CodeAlpha AI Internship** program.

---

<div align="center">
  Built with ❤️ using Python & Flask
</div>
