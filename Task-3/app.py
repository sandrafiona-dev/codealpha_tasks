#!/usr/bin/env python3
"""
app.py — Harmonix: AI Music Generation
Premium Streamlit web interface with glassmorphic design,
emotion-to-music composition, and MIDI piano-roll playback.
"""

import os
import sys
import pickle
import tempfile
import base64
import numpy as np
# pyrefly: ignore [missing-import]
import streamlit as st
import yaml
from pathlib import Path

from src.preprocess import extract_remi_events
from src.constants import (
    GM_INSTRUMENTS, MASTERPIECES, EMOTIONS,
    get_category_and_sound_from_program, analyze_emotion_from_text
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# ═══════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Harmonix: AI Music Generation",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════
#  PREMIUM HARMONIX CSS
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── Root Design Tokens ─────────────────────────────────────── */
    :root {
        --bg-base: #0a0a14;
        --bg-surface: rgba(15, 12, 30, 0.85);
        --bg-glass: rgba(20, 16, 40, 0.6);
        --bg-glass-hover: rgba(30, 24, 55, 0.75);
        --border-glass: rgba(130, 80, 255, 0.22);
        --border-glow: rgba(130, 80, 255, 0.5);
        --gradient-primary: linear-gradient(135deg, #7c3aed, #a855f7, #c084fc);
        --gradient-accent: linear-gradient(135deg, #6366f1, #8b5cf6, #a855f7);
        --text-primary: #f1f0f5;
        --text-secondary: #a5a1b7;
        --text-muted: #6b6880;
        --accent-purple: #a855f7;
        --accent-violet: #8b5cf6;
        --glow-purple: 0 0 25px rgba(130, 80, 255, 0.15);
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --blur-glass: 16px;
    }

    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    .stApp > header { background: transparent !important; }

    /* ── Animated Header ────────────────────────────────────────── */
    .harmonix-header {
        text-align: center;
        padding: 0.8rem 0 0.2rem;
    }
    .harmonix-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(120deg, #818cf8, #a855f7, #ec4899, #a855f7, #818cf8);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 4s ease-in-out infinite;
        letter-spacing: -0.02em;
        margin: 0;
        line-height: 1.2;
    }
    .harmonix-subtitle {
        font-family: 'Inter', sans-serif;
        color: var(--text-secondary);
        font-size: 0.95rem;
        font-weight: 400;
        margin-top: 0.2rem;
        letter-spacing: 0.02em;
    }
    @keyframes shimmer {
        0%, 100% { background-position: 0% center; }
        50% { background-position: 200% center; }
    }

    /* ── Section Labels ─────────────────────────────────────────── */
    .section-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--text-secondary);
        margin-bottom: 0.6rem;
        margin-top: 0.2rem;
    }

    /* ── Composition Card Grid ──────────────────────────────────── */
    .comp-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-top: 0.6rem;
    }
    .comp-card {
        background: var(--bg-glass);
        backdrop-filter: blur(var(--blur-glass));
        -webkit-backdrop-filter: blur(var(--blur-glass));
        border: 1px solid var(--border-glass);
        border-radius: var(--radius-md);
        padding: 14px 16px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .comp-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: var(--gradient-primary);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .comp-card:hover {
        border-color: var(--border-glow);
        box-shadow: var(--glow-purple);
        transform: translateY(-3px);
    }
    .comp-card:hover::before { opacity: 1; }
    .comp-card .card-icon { font-size: 1.5rem; margin-bottom: 6px; }
    .comp-card .card-title {
        font-size: 0.62rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #c4b5fd;
        margin-bottom: 4px;
    }
    .comp-card .card-value {
        font-size: 0.88rem;
        color: var(--text-primary);
        line-height: 1.45;
    }
    .comp-card .card-value.large {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .comp-card .card-sub {
        color: var(--text-secondary);
        font-size: 0.78rem;
    }

    /* ── Piano Roll Container ───────────────────────────────────── */
    .piano-roll-box {
        background: rgba(10, 8, 20, 0.92);
        border: 1px solid var(--border-glass);
        border-radius: var(--radius-lg);
        padding: 1.2rem;
        min-height: 300px;
    }
    .piano-placeholder {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 300px;
        color: var(--text-muted);
        font-size: 0.95rem;
    }
    .piano-placeholder .ph-icon {
        font-size: 3.5rem;
        margin-bottom: 14px;
        opacity: 0.4;
        animation: float 3s ease-in-out infinite;
    }
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }

    /* ── Sidebar ────────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(10, 8, 20, 0.97), rgba(15, 12, 30, 0.98)) !important;
        border-right: 1px solid var(--border-glass) !important;
    }
    .sidebar-logo {
        text-align: center;
        padding: 1.2rem 0 0.6rem;
        font-size: 2.2rem;
        line-height: 1;
    }
    .sidebar-brand {
        text-align: center;
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        font-weight: 700;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.8rem;
    }
    section[data-testid="stSidebar"] .stRadio > label { display: none; }
    section[data-testid="stSidebar"] .stRadio > div {
        flex-direction: column;
        gap: 6px;
    }
    section[data-testid="stSidebar"] .stRadio > div > label {
        padding: 0.7rem 1.1rem !important;
        border-radius: var(--radius-md) !important;
        margin: 2px 0;
        transition: all 0.25s ease !important;
        font-size: 0.95rem !important;
        border: 1px solid transparent !important;
        background: transparent !important;
        cursor: pointer !important;
    }
    section[data-testid="stSidebar"] .stRadio > div > label:hover {
        background: var(--bg-glass-hover) !important;
        border-color: rgba(130, 80, 255, 0.15) !important;
    }
    section[data-testid="stSidebar"] .stRadio > div > label:has(input:checked) {
        background: rgba(130, 80, 255, 0.25) !important;
        border: 1px solid rgba(130, 80, 255, 0.45) !important;
        color: #f1f0f5 !important;
        font-weight: 600 !important;
        box-shadow: var(--glow-purple) !important;
    }
    section[data-testid="stSidebar"] .stRadio > div > label > div:first-child {
        display: none !important;
    }
    section[data-testid="stSidebar"] .stMarkdown h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: var(--text-primary);
        font-size: 0.95rem;
    }

    /* ── Buttons ────────────────────────────────────────────────── */
    .stButton > button {
        background: var(--gradient-accent) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        letter-spacing: 0.01em !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(99, 102, 241, 0.35) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* ── Text Areas & Inputs ────────────────────────────────────── */
    .stTextArea textarea {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.92rem !important;
        transition: all 0.3s ease !important;
    }
    .stTextArea textarea:focus {
        border-color: var(--accent-purple) !important;
        box-shadow: 0 0 0 2px rgba(168, 85, 247, 0.15) !important;
    }

    /* ── Select Boxes ───────────────────────────────────────────── */
    .stSelectbox > div > div {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: var(--radius-md) !important;
    }

    /* ── Expanders ──────────────────────────────────────────────── */
    .streamlit-expanderHeader {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: var(--radius-md) !important;
        font-weight: 500 !important;
        transition: all 0.25s ease !important;
    }
    .streamlit-expanderHeader:hover {
        background: var(--bg-glass-hover) !important;
        border-color: var(--border-glow) !important;
    }

    /* ── Dividers ───────────────────────────────────────────────── */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, var(--border-glass), var(--accent-purple), var(--border-glass), transparent) !important;
        margin: 1.2rem 0 !important;
    }

    /* ── Scrollbar ──────────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(139, 92, 246, 0.3);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(139, 92, 246, 0.5);
    }

    /* ── Metrics ────────────────────────────────────────────────── */
    [data-testid="stMetric"] {
        background: var(--bg-glass);
        border: 1px solid var(--border-glass);
        border-radius: var(--radius-md);
        padding: 10px 14px;
        text-align: center;
    }

    /* ── Upload Status ──────────────────────────────────────────── */
    .upload-status {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: var(--radius-md);
        padding: 0.6rem 0.8rem;
        font-size: 0.82rem;
        color: #6ee7b7;
        backdrop-filter: blur(8px);
    }

    /* ── Footer ─────────────────────────────────────────────────── */
    .harmonix-footer {
        text-align: center;
        color: var(--text-muted);
        font-size: 0.78rem;
        padding: 1.2rem 0 0.5rem;
        font-family: 'Inter', sans-serif;
    }

    /* ── Fade-in Animation ──────────────────────────────────────── */
    .fade-in { animation: fadeIn 0.5s ease-out; }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  CACHED FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

@st.cache_data
def load_config():
    """Load config.yaml with caching."""
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)


@st.cache_resource
def load_model_and_artefacts(config, reload_trigger=0):
    """
    Load the trained model, vocabulary mappings, and training notes.
    Cached so model is loaded only once per session.
    """
    # pyrefly: ignore [missing-import]
    from model import load_model as build_and_load

    with open('models/note2int.pkl', 'rb') as f:
        note2int = pickle.load(f)
    with open('models/int2note.pkl', 'rb') as f:
        int2note = pickle.load(f)
    with open('models/all_notes.pkl', 'rb') as f:
        all_notes = pickle.load(f)

    vocab_size = len(note2int)
    seq_length = config['model']['sequence_length']

    model = build_and_load(
        weights_path='models/checkpoints/best_weights.weights.h5',
        seq_length=seq_length,
        vocab_size=vocab_size
    )
    return model, note2int, int2note, all_notes


# ═══════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def parse_uploaded_midi(uploaded_file) -> list:
    """Parse an uploaded MIDI file into REMI event tokens."""
    with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
    try:
        events = extract_remi_events(tmp_path)
    finally:
        os.unlink(tmp_path)
    return events


def generate_music(model, all_notes, note2int, int2note, n_notes, temperature, seed_events=None):
    """Generate music tokens using the loaded model."""
    # pyrefly: ignore [missing-import]
    from generate import generate_notes
    return generate_notes(
        model=model, all_notes=all_notes,
        note2int=note2int, int2note=int2note,
        n_notes=n_notes, temperature=temperature,
        seed_notes=seed_events
    )


def create_midi(events, bpm, note_duration, program_mapping):
    """Convert generated REMI events to an orchestrated MIDI file."""
    # pyrefly: ignore [missing-import]
    from utils import remi_events_to_midi
    output_path = 'outputs/streamlit_output.mid'
    os.makedirs('outputs', exist_ok=True)
    return remi_events_to_midi(
        events=events,
        output_path=output_path,
        default_bpm=bpm,
        program_mapping=program_mapping
    )


def init_session_defaults(config):
    """Initialize session state with sensible defaults from config."""
    defaults = {
        'n_notes': min(config['generation']['n_notes'], 400),
        'temperature': config['generation']['temperature'],
        'bpm': config['generation']['bpm'],
        'note_duration': config['generation']['note_duration'],
        'prog_val_1': 1,     # Acoustic Grand Piano
        'prog_val_2': 49,    # String Ensemble 1
        'prog_val_3': 34,    # Electric Bass (finger)
        'prog_val_4': 82,    # Lead 2 (sawtooth)
        'prog_val_5': 115,   # Steel Drums
        'current_emotion': None,
        'reload_trigger': 0,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def build_composition_cards_html(detected_emotion, preset):
    """Build the HTML for the 6 composition plan cards."""
    keywords = ", ".join([k.capitalize() for k in preset['keywords'][:3]])
    genre = preset['genre']
    bpm_display = st.session_state['bpm']

    key_name = preset['key'].split('(')[0].strip()
    chord_raw = preset['chord_prog']
    chord_simple = chord_raw.split('(')[1].rstrip(')') if '(' in chord_raw else chord_raw

    inst_names = []
    for i in range(1, 6):
        _, name = get_category_and_sound_from_program(st.session_state[f'prog_val_{i}'])
        inst_names.append(name)
    inst_display = "<br>".join(inst_names[:3])

    structure = preset['structure'].replace(' -> ', ' | ')

    return f"""
    <div class="comp-grid fade-in">
        <div class="comp-card">
            <div class="card-icon">⭐</div>
            <div class="card-title">EMOTION</div>
            <div class="card-value">{detected_emotion}<br><span class="card-sub">{keywords}</span></div>
        </div>
        <div class="comp-card">
            <div class="card-icon">🎼</div>
            <div class="card-title">GENRE</div>
            <div class="card-value">{genre}</div>
        </div>
        <div class="comp-card">
            <div class="card-icon">🎚️</div>
            <div class="card-title">BPM</div>
            <div class="card-value large">{bpm_display}</div>
        </div>
        <div class="comp-card">
            <div class="card-icon">🎹</div>
            <div class="card-title">KEY & CHORD PROGRESSION</div>
            <div class="card-value">{key_name}:<br><span style="color:#c4b5fd;">{chord_simple}</span></div>
        </div>
        <div class="comp-card">
            <div class="card-icon">🎷</div>
            <div class="card-title">INSTRUMENTS</div>
            <div class="card-value" style="font-size:0.82rem;">{inst_display}</div>
        </div>
        <div class="comp-card">
            <div class="card-icon">📐</div>
            <div class="card-title">STRUCTURE</div>
            <div class="card-value" style="font-size:0.8rem;">{structure}</div>
        </div>
    </div>
    """


def render_piano_roll_player(midi_path):
    """Render the interactive MIDI piano-roll player."""
    with open(midi_path, 'rb') as f:
        midi_bytes = f.read()
    b64_midi = base64.b64encode(midi_bytes).decode('utf-8')
    midi_data_url = f"data:audio/midi;base64,{b64_midi}"

    player_html = f"""
    <script src="https://cdn.jsdelivr.net/combine/npm/tone@14.7.58,npm/@magenta/music@1.22.0/es6/core.js,npm/html-midi-player@1.5.0"></script>
    <style>
        body {{ margin: 0; padding: 0; background: transparent; color: #fff; }}
        .roll-wrap {{
            background: rgba(10, 8, 20, 0.95);
            border: 1px solid rgba(130, 80, 255, 0.22);
            border-radius: 14px;
            padding: 1rem;
            box-shadow: 0 0 30px rgba(130, 80, 255, 0.08);
        }}
        midi-player {{
            width: 100%;
            --primary-color: #a855f7;
            --play-button-color: #3b82f6;
            --control-panel-background: rgba(15, 12, 30, 0.85);
            --control-panel-border-radius: 10px;
            --track-color: #2d2640;
            --progress-color: #a855f7;
            --time-color: #a5a1b7;
        }}
        midi-visualizer {{
            width: 100%;
            background: rgba(10, 8, 20, 0.9);
            border-radius: 10px;
            border: 1px solid rgba(130, 80, 255, 0.12);
            overflow: hidden;
            max-height: 280px;
        }}
        midi-visualizer .note.active {{
            fill: #a855f7 !important;
        }}
    </style>
    <div class="roll-wrap">
        <midi-player
            src="{midi_data_url}"
            sound-font
            visualizer="#harmonix-viz">
        </midi-player>
        <midi-visualizer type="piano-roll" id="harmonix-viz"></midi-visualizer>
    </div>
    """
    # pyrefly: ignore [missing-import]
    import streamlit.components.v1 as components
    components.html(player_html, height=380)
    return midi_bytes


# ═══════════════════════════════════════════════════════════════════
#  COMPOSE PAGE
# ═══════════════════════════════════════════════════════════════════

def compose_page():
    """Main composition page: story input + cards on left, piano roll on right."""
    config = load_config()

    # ── Detect emotion from story ──────────────────────────────────
    user_story = st.session_state.get('user_story', '')
    detected_emotion = analyze_emotion_from_text(user_story)
    preset = EMOTIONS[detected_emotion]

    # Auto-apply emotion preset when emotion changes
    if st.session_state.get('current_emotion') != detected_emotion:
        st.session_state['current_emotion'] = detected_emotion
        st.session_state['bpm'] = preset['bpm']
        st.session_state['temperature'] = preset['temp']
        for i in range(1, 6):
            st.session_state[f'prog_val_{i}'] = preset['instruments'][i - 1]
            # Clear widget keys so Settings page re-derives from prog_val
            for prefix in ['cat_val_', 'sound_val_']:
                st.session_state.pop(f'{prefix}{i}', None)

    # ── Two-Column Layout ──────────────────────────────────────────
    col_left, col_right = st.columns([5, 6], gap="large")

    with col_left:
        # INPUT STORY
        st.markdown('<div class="section-label">INPUT STORY</div>', unsafe_allow_html=True)
        st.text_area(
            "story_input",
            placeholder="Describe your situation, story, or emotion...",
            key='user_story',
            height=120,
            label_visibility="collapsed"
        )

        # Emotion override
        emotion_options = list(EMOTIONS.keys())
        override_idx = emotion_options.index(detected_emotion)
        selected_emotion = st.selectbox(
            "Detected Emotion (override):",
            options=emotion_options,
            index=override_idx,
            key='emotion_override',
            help="Auto-detected from your story. Select to override."
        )

        # If user manually overrides the emotion
        if selected_emotion != detected_emotion:
            detected_emotion = selected_emotion
            preset = EMOTIONS[detected_emotion]
            if st.session_state.get('current_emotion') != detected_emotion:
                st.session_state['current_emotion'] = detected_emotion
                st.session_state['bpm'] = preset['bpm']
                st.session_state['temperature'] = preset['temp']
                for i in range(1, 6):
                    st.session_state[f'prog_val_{i}'] = preset['instruments'][i - 1]
                    for prefix in ['cat_val_', 'sound_val_']:
                        st.session_state.pop(f'{prefix}{i}', None)
                st.rerun()

        # GENERATE BUTTON
        st.markdown("")
        generate_clicked = st.button("🎵 Generate Music", use_container_width=True, key="gen_btn")

        # AI MUSIC COMPOSITION PLAN
        st.markdown("")
        st.markdown('<div class="section-label">AI MUSIC COMPOSITION PLAN</div>', unsafe_allow_html=True)
        cards_html = build_composition_cards_html(detected_emotion, preset)
        st.markdown(cards_html, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-label">VISUAL PIANO ROLL</div>', unsafe_allow_html=True)

        # ── Check model ────────────────────────────────────────────
        model_exists = os.path.exists('models/checkpoints/best_weights.weights.h5')
        if not model_exists:
            st.warning("""
            ⚠️ **No trained model found!**

            1. Place MIDI files in `dataset/`
            2. Run: `python src/preprocess.py`
            3. Run: `python src/train.py`
            4. Restart this app
            """)
            return

        # ── Load model ─────────────────────────────────────────────
        try:
            reload_trigger = st.session_state.get('reload_trigger', 0)
            model, note2int, int2note, all_notes = load_model_and_artefacts(config, reload_trigger)
        except Exception as e:
            st.error(f"Failed to load model: {e}")
            return

        # ── Handle generation ──────────────────────────────────────
        instrument_programs = [st.session_state[f'prog_val_{i}'] for i in range(1, 6)]
        custom_seed = st.session_state.get('custom_seed', None)

        if generate_clicked:
            n_notes = st.session_state['n_notes']
            temperature = st.session_state['temperature']
            bpm = st.session_state['bpm']
            note_duration = st.session_state['note_duration']

            with st.spinner("🎼 Composing with Music Transformer..."):
                events = generate_music(
                    model, all_notes, note2int, int2note,
                    n_notes=n_notes, temperature=temperature,
                    seed_events=custom_seed
                )
                midi_path = create_midi(events, bpm, note_duration, instrument_programs)
                st.session_state['generated_tokens'] = events
                st.session_state['midi_path'] = midi_path

            st.success(f"✅ Generated {n_notes} events!")
            st.rerun()

        # ── Display piano roll or placeholder ──────────────────────
        if 'generated_tokens' in st.session_state and 'midi_path' in st.session_state:
            midi_path = st.session_state['midi_path']
            if os.path.exists(midi_path):
                midi_bytes = render_piano_roll_player(midi_path)

                # Download button
                st.markdown("")
                st.download_button(
                    label="⬇️ Download MIDI",
                    data=midi_bytes,
                    file_name="harmonix_generated.mid",
                    mime="application/octet-stream",
                    use_container_width=True
                )

                # Stats row
                tokens = st.session_state['generated_tokens']
                pitches = sum(1 for t in tokens if t.startswith('Pitch_'))
                bars = sum(1 for t in tokens if t == 'Bar')
                s1, s2, s3 = st.columns(3)
                s1.metric("Tokens", len(tokens))
                s2.metric("Pitches", pitches)
                s3.metric("Bars", bars)
            else:
                st.warning("MIDI file not found. Generate again.")
        else:
            # Placeholder
            st.markdown("""
            <div class="piano-roll-box">
                <div class="piano-placeholder">
                    <div class="ph-icon">🎹</div>
                    <div>Click <strong>Generate Music</strong> to create a composition</div>
                    <div style="font-size:0.8rem; margin-top:8px; color:#6b6880;">
                        Your emotion-driven AI composition will appear here
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  LIBRARY PAGE
# ═══════════════════════════════════════════════════════════════════

def library_page():
    """Browse and download previously generated compositions."""
    st.markdown('<div class="section-label" style="font-size:1.05rem;">📋 Music Library</div>',
                unsafe_allow_html=True)
    st.markdown("Browse and download your previously generated compositions.")
    st.markdown("---")

    outputs_dir = Path('outputs')
    if outputs_dir.exists():
        midi_files = sorted(outputs_dir.glob('*.mid'), key=os.path.getmtime, reverse=True)
        if midi_files:
            for f in midi_files:
                col1, col2, col3 = st.columns([5, 2, 2])
                with col1:
                    st.markdown(f"🎵 **{f.name}**")
                with col2:
                    size_kb = f.stat().st_size / 1024
                    st.caption(f"{size_kb:.1f} KB")
                with col3:
                    with open(f, 'rb') as fp:
                        st.download_button(
                            "⬇️ Download", fp.read(), f.name,
                            mime="application/octet-stream",
                            key=f"dl_{f.name}"
                        )
                st.markdown("---")
        else:
            st.info("No generated files yet. Go to **Compose** and create some music!")
    else:
        st.info("No outputs directory found. Generate music first!")


# ═══════════════════════════════════════════════════════════════════
#  SETTINGS PAGE
# ═══════════════════════════════════════════════════════════════════

def settings_page():
    """Full manual controls: generation params, instruments, MIDI seed, model."""
    config = load_config()

    st.markdown('<div class="section-label" style="font-size:1.05rem;">⚙️ Generation Settings</div>',
                unsafe_allow_html=True)
    st.markdown("Fine-tune your music generation parameters and instruments.")
    st.markdown("---")

    col1, col2 = st.columns(2)

    # ── Left column: Generation parameters ─────────────────────────
    with col1:
        st.markdown("### 🎶 Generation Parameters")

        new_n = st.slider("🎶 Number of Notes", 50, 400,
                          value=st.session_state['n_notes'], step=50)
        st.session_state['n_notes'] = new_n

        new_t = st.slider("🌡️ Temperature", 0.1, 2.0,
                          value=float(st.session_state['temperature']), step=0.1)
        st.session_state['temperature'] = new_t

        new_bpm = st.slider("⏱️ Tempo (BPM)", 40, 240,
                            value=st.session_state['bpm'], step=10)
        st.session_state['bpm'] = new_bpm

        dur_options = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0]
        cur_dur = st.session_state['note_duration']
        if cur_dur not in dur_options:
            cur_dur = 0.5
        new_dur = st.select_slider("📏 Note Duration", options=dur_options, value=cur_dur)
        st.session_state['note_duration'] = new_dur

        st.markdown("---")
        st.markdown("### 📊 Temperature Guide")
        st.markdown("""
        | Value | Style |
        |-------|-------|
        | 0.1–0.5 | Conservative, repetitive |
        | 0.6–1.0 | Balanced, musical |
        | 1.1–1.5 | Creative, experimental |
        | 1.6–2.0 | Very random, chaotic |
        """)

    # ── Right column: Instruments & Seeds ──────────────────────────
    with col2:
        st.markdown("### 🎷 5-Instrument Ensemble")

        labels = [
            ("🎵 Lead Melody", '1'),
            ("🎻 Harmony / Chords", '2'),
            ("🎸 Bassline", '3'),
            ("🎺 Arpeggiator", '4'),
            ("🔔 Percussion / FX", '5'),
        ]

        for label, suffix in labels:
            with st.expander(label, expanded=False):
                prog_key = f'prog_val_{suffix}'
                def_cat, def_sound = get_category_and_sound_from_program(
                    st.session_state[prog_key])
                cat_list = list(GM_INSTRUMENTS.keys())
                cat_idx = cat_list.index(def_cat) if def_cat in cat_list else 0

                cat = st.selectbox(
                    "Category", cat_list, index=cat_idx,
                    key=f'cat_val_{suffix}')
                insts = GM_INSTRUMENTS[cat]
                sound_list = list(insts.values())
                sound_idx = sound_list.index(def_sound) if def_sound in sound_list else 0

                sound = st.selectbox(
                    "Sound", sound_list, index=sound_idx,
                    key=f'sound_val_{suffix}')
                prog = [k for k, v in insts.items() if v == sound][0]
                st.session_state[prog_key] = prog

        st.markdown("---")
        st.markdown("### 🎤 Custom MIDI Seed")

        if 'uploader_version' not in st.session_state:
            st.session_state['uploader_version'] = 0

        uploaded_midi = st.file_uploader(
            "Upload a .mid / .midi file",
            type=['mid', 'midi'],
            key=f"midi_uploader_{st.session_state['uploader_version']}",
            help="Upload your own MIDI file as a generation seed."
        )
        if uploaded_midi is not None:
            if st.session_state.get('uploaded_midi_name') != uploaded_midi.name:
                try:
                    seed_events = parse_uploaded_midi(uploaded_midi)
                    if seed_events:
                        st.session_state['custom_seed'] = seed_events
                        st.session_state['uploaded_midi_name'] = uploaded_midi.name
                        st.toast(f"✅ Loaded: {uploaded_midi.name}!", icon="🎼")
                        st.rerun()
                    else:
                        st.warning("No notes found in the uploaded file.")
                except Exception as e:
                    st.error(f"Failed to parse MIDI: {e}")

        if 'custom_seed' in st.session_state:
            st.markdown(
                f'<div class="upload-status">✅ <strong>'
                f'{st.session_state.get("uploaded_midi_name", "MIDI")}</strong> — '
                f'{len(st.session_state["custom_seed"])} events</div>',
                unsafe_allow_html=True
            )
            if st.button("🗑️ Clear Seed", use_container_width=True):
                st.session_state.pop('custom_seed', None)
                st.session_state.pop('uploaded_midi_name', None)
                st.session_state['uploader_version'] += 1
                st.rerun()

        st.markdown("---")
        st.markdown("### 🎻 Classical Masterpiece Seeds")
        masterpiece_options = ["None (random seed)"] + list(MASTERPIECES.keys())
        selected_piece = st.selectbox(
            "Load a masterpiece as seed:",
            options=masterpiece_options,
            help="Use a classical piece's notes as the generation seed."
        )
        if selected_piece != "None (random seed)":
            if st.session_state.get('_last_masterpiece') != selected_piece:
                info = MASTERPIECES[selected_piece]
                try:
                    seed_events = extract_remi_events(info['midi_path'])
                    if seed_events:
                        st.session_state['custom_seed'] = seed_events
                        st.session_state['uploaded_midi_name'] = selected_piece
                        st.session_state['_last_masterpiece'] = selected_piece
                        st.success(f"Loaded seed: {selected_piece}")
                except Exception as e:
                    st.error(f"Failed: {e}")

        st.markdown("---")
        st.markdown("### 🔄 Model Control")
        if st.button("Reload Model Weights", use_container_width=True):
            st.session_state['reload_trigger'] = st.session_state.get('reload_trigger', 0) + 1
            st.success("Model queued for reload!")
            st.rerun()


# ═══════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    config = load_config()
    init_session_defaults(config)

    # ── Header ─────────────────────────────────────────────────────
    st.markdown("""
    <div class="harmonix-header">
        <h1 class="harmonix-title">👑 Harmonix: AI Music Generation</h1>
        <div class="harmonix-subtitle">Emotion-to-Music Mode</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar Navigation ─────────────────────────────────────────
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">🎛️</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-brand">Harmonix</div>', unsafe_allow_html=True)

        page = st.radio(
            "Navigation",
            ["✏️ Compose", "📋 Library", "⚙️ Settings"],
            label_visibility="collapsed",
            key="nav_radio"
        )

        # Quick info on Compose page
        if "Compose" in page:
            st.markdown("---")
            st.markdown("### ⚡ Quick Info")
            emotion = st.session_state.get('current_emotion', '—')
            st.caption(f"🎭 Emotion: **{emotion}**")
            st.caption(f"🎶 Notes: **{st.session_state.get('n_notes', 200)}**")
            st.caption(f"🌡️ Temp: **{st.session_state.get('temperature', 1.0):.1f}**")
            st.caption(f"⏱️ BPM: **{st.session_state.get('bpm', 120)}**")

            if 'custom_seed' in st.session_state:
                name = st.session_state.get('uploaded_midi_name', 'Custom')
                st.caption(f"🎼 Seed: **{name}**")

    # ── Route to page ──────────────────────────────────────────────
    if "Compose" in page:
        compose_page()
    elif "Library" in page:
        library_page()
    elif "Settings" in page:
        settings_page()

    # ── Footer ─────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        '<div class="harmonix-footer">👑 Harmonix v1.0.0 — AI Music Generation &nbsp;·&nbsp; '
        'Built with TensorFlow, Music21 & Streamlit</div>',
        unsafe_allow_html=True
    )


if __name__ == '__main__':
    main()
