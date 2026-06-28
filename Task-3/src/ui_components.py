#!/usr/bin/env python3
"""
src/ui_components.py
Reusable Streamlit UI components for the Harmonix Music Generation AI.
Provides helper functions for instrument selectors, metric cards, and composition plans.
"""

# pyrefly: ignore [missing-import]
import streamlit as st
from src.constants import GM_INSTRUMENTS, get_category_and_sound_from_program


def render_instrument_selector(
    label: str,
    icon: str,
    session_key_suffix: str,
    default_program: int,
    expanded: bool = False
) -> int:
    """
    Render a single instrument selector expander with category + sound dropdowns.
    Returns the selected MIDI program number.

    Args:
        label: Display label for the section (e.g., "Lead Melody")
        icon: Emoji icon for the expander
        session_key_suffix: Suffix for session state keys (e.g., "1", "2", etc.)
        default_program: Default MIDI program number
        expanded: Whether the expander starts expanded
    """
    prog_key = f'prog_val_{session_key_suffix}'

    # Initialize session state if needed
    if prog_key not in st.session_state:
        st.session_state[prog_key] = default_program

    with st.expander(f"{icon} Section {session_key_suffix}: {label}", expanded=expanded):
        def_cat, def_sound = get_category_and_sound_from_program(st.session_state[prog_key])
        cat_list = list(GM_INSTRUMENTS.keys())
        cat_idx = cat_list.index(def_cat) if def_cat in cat_list else 0

        cat = st.selectbox(
            f"Category ({label})",
            cat_list,
            index=cat_idx,
            key=f'cat_val_{session_key_suffix}'
        )
        insts = GM_INSTRUMENTS[cat]
        sound_list = list(insts.values())
        sound_idx = sound_list.index(def_sound) if def_sound in sound_list else 0

        sound = st.selectbox(
            f"Sound ({label})",
            sound_list,
            index=sound_idx,
            key=f'sound_val_{session_key_suffix}'
        )
        prog = [k for k, v in insts.items() if v == sound][0]
        st.session_state[prog_key] = prog

    return prog


def render_metric_card(label: str, value, icon: str = ""):
    """Render a glassmorphic metric card with an icon."""
    display_val = str(value)
    st.markdown(f'''
    <div class="glass-metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{display_val}</div>
        <div class="metric-label">{label}</div>
    </div>
    ''', unsafe_allow_html=True)


def render_composition_plan(preset: dict, selected_emotion: str, n_notes: int):
    """Render the AI Music Composition Plan grid."""

    col_grid1, col_grid2 = st.columns(2)
    with col_grid1:
        st.markdown(f"""
        <div class="glass-info-panel">
            <div class="info-item"><span class="info-icon">🎭</span> <strong>Emotion & Mood:</strong> {selected_emotion} — <em>{', '.join([k.capitalize() for k in preset['keywords'][:4]])}</em></div>
            <div class="info-item"><span class="info-icon">🎵</span> <strong>Genre & Tempo:</strong> {preset['genre']} @ <strong>{preset['bpm']} BPM</strong></div>
            <div class="info-item"><span class="info-icon">🔑</span> <strong>Key Signature:</strong> {preset['key']}</div>
            <div class="info-item"><span class="info-icon">🎹</span> <strong>Chord Progression:</strong> <code>{preset['chord_prog']}</code></div>
        </div>
        """, unsafe_allow_html=True)

    with col_grid2:
        st.markdown(f'<div class="glass-info-panel">', unsafe_allow_html=True)
        st.markdown(f"**🌡️ AI Parameters:** Temp = `{preset['temp']}`, Length = `{n_notes}` events")
        st.markdown("**🎷 Orchestration (5-Instrument Ensemble):**")
        for i, prog in enumerate(preset["instruments"]):
            cat, name = get_category_and_sound_from_program(prog)
            st.markdown(f"- **Section {i+1}**: {name} ({cat})")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="glass-detail-box">
        <strong>🎻 Composition Details:</strong>
        <ul>
            <li><strong>Melody Style:</strong> {preset['melody']}</li>
            <li><strong>Rhythm & Percussion:</strong> {preset['rhythm']}</li>
            <li><strong>Song Structure:</strong> {preset['structure']}</li>
            <li><strong>Dynamics:</strong> {preset['dynamics']}</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.info(f"✨ **How it feels:** {preset['listener_feeling']}")


def get_premium_css() -> str:
    """Return the complete premium glassmorphism CSS theme."""
    return """
    <style>
        /* ── Google Fonts Import ──────────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

        /* ── CSS Variables ────────────────────────────────────────────── */
        :root {
            --bg-base: #0a0a14;
            --bg-surface: rgba(15, 12, 30, 0.85);
            --bg-glass: rgba(25, 20, 50, 0.45);
            --bg-glass-hover: rgba(35, 28, 65, 0.55);
            --border-glass: rgba(139, 92, 246, 0.18);
            --border-glass-hover: rgba(139, 92, 246, 0.35);
            --gradient-primary: linear-gradient(135deg, #7c3aed, #a855f7, #c084fc);
            --gradient-accent: linear-gradient(135deg, #6366f1, #8b5cf6, #a855f7);
            --gradient-warm: linear-gradient(135deg, #f472b6, #c084fc, #818cf8);
            --gradient-surface: linear-gradient(145deg, rgba(30, 24, 60, 0.6), rgba(15, 12, 30, 0.8));
            --text-primary: #f1f0f5;
            --text-secondary: #a5a1b7;
            --text-muted: #6b6880;
            --accent-purple: #a855f7;
            --accent-violet: #8b5cf6;
            --accent-indigo: #6366f1;
            --accent-pink: #ec4899;
            --glow-purple: 0 0 30px rgba(168, 85, 247, 0.15);
            --glow-strong: 0 0 40px rgba(168, 85, 247, 0.25);
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-xl: 20px;
            --blur-glass: 16px;
            --transition-smooth: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        }

        /* ── Global Styles ────────────────────────────────────────────── */
        .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        .stApp > header {
            background: transparent !important;
        }

        /* ── Animated Header ──────────────────────────────────────────── */
        .harmonix-header {
            text-align: center;
            padding: 1.5rem 0 0.5rem;
            position: relative;
        }

        .harmonix-title {
            font-family: 'Inter', sans-serif;
            font-size: 2.8rem;
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
            font-size: 1.05rem;
            font-weight: 400;
            margin-top: 0.4rem;
            letter-spacing: 0.02em;
        }

        .harmonix-version {
            display: inline-block;
            background: var(--bg-glass);
            border: 1px solid var(--border-glass);
            border-radius: 20px;
            padding: 0.15rem 0.7rem;
            font-size: 0.7rem;
            color: var(--accent-purple);
            font-weight: 500;
            margin-top: 0.5rem;
            backdrop-filter: blur(8px);
        }

        @keyframes shimmer {
            0%, 100% { background-position: 0% center; }
            50% { background-position: 200% center; }
        }

        /* ── Glass Metric Cards ───────────────────────────────────────── */
        .glass-metric-card {
            background: var(--bg-glass);
            backdrop-filter: blur(var(--blur-glass));
            -webkit-backdrop-filter: blur(var(--blur-glass));
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-lg);
            padding: 1.4rem 1rem;
            text-align: center;
            transition: var(--transition-smooth);
            position: relative;
            overflow: hidden;
        }

        .glass-metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: var(--gradient-primary);
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .glass-metric-card:hover {
            background: var(--bg-glass-hover);
            border-color: var(--border-glass-hover);
            transform: translateY(-3px);
            box-shadow: var(--glow-purple);
        }

        .glass-metric-card:hover::before {
            opacity: 1;
        }

        .metric-icon {
            font-size: 1.6rem;
            margin-bottom: 0.3rem;
        }

        .metric-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.7rem;
            font-weight: 700;
            color: var(--text-primary);
            margin: 0.2rem 0;
        }

        .metric-label {
            font-size: 0.78rem;
            color: var(--text-secondary);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        /* ── Glass Info Panels ─────────────────────────────────────────── */
        .glass-info-panel {
            background: var(--bg-glass);
            backdrop-filter: blur(var(--blur-glass));
            -webkit-backdrop-filter: blur(var(--blur-glass));
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-lg);
            padding: 1.2rem 1.5rem;
            margin-bottom: 1rem;
        }

        .glass-info-panel .info-item {
            padding: 0.4rem 0;
            color: var(--text-primary);
            font-size: 0.92rem;
            line-height: 1.6;
        }

        .glass-info-panel .info-icon {
            margin-right: 0.3rem;
        }

        .glass-detail-box {
            background: var(--bg-glass);
            backdrop-filter: blur(var(--blur-glass));
            -webkit-backdrop-filter: blur(var(--blur-glass));
            border-left: 3px solid var(--accent-purple);
            border-radius: 0 var(--radius-md) var(--radius-md) 0;
            padding: 1rem 1.5rem;
            margin: 1rem 0;
            color: var(--text-primary);
            font-size: 0.9rem;
        }

        .glass-detail-box ul {
            margin: 0.5rem 0 0;
            padding-left: 1.2rem;
        }

        .glass-detail-box li {
            padding: 0.25rem 0;
            line-height: 1.5;
        }

        /* ── Buttons ──────────────────────────────────────────────────── */
        .stButton > button {
            background: var(--gradient-accent) !important;
            color: white !important;
            border: none !important;
            padding: 0.75rem 2rem !important;
            border-radius: var(--radius-md) !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
            width: 100% !important;
            transition: var(--transition-smooth) !important;
            position: relative !important;
            overflow: hidden !important;
            letter-spacing: 0.01em !important;
        }

        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 30px rgba(99, 102, 241, 0.35) !important;
        }

        .stButton > button:active {
            transform: translateY(0) !important;
        }

        /* Generate button pulse */
        .generate-pulse .stButton > button {
            animation: btn-pulse 2.5s ease-in-out infinite;
        }

        @keyframes btn-pulse {
            0%, 100% { box-shadow: 0 0 0 0 rgba(139, 92, 246, 0.4); }
            50% { box-shadow: 0 0 0 12px rgba(139, 92, 246, 0); }
        }

        /* ── Upload Status ─────────────────────────────────────────────── */
        .upload-status {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: var(--radius-md);
            padding: 0.75rem 1rem;
            margin-top: 0.5rem;
            font-size: 0.85rem;
            color: #6ee7b7;
            backdrop-filter: blur(8px);
        }

        /* ── Sidebar Enhancements ─────────────────────────────────────── */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(10, 8, 20, 0.97), rgba(15, 12, 30, 0.98)) !important;
            border-right: 1px solid var(--border-glass) !important;
        }

        section[data-testid="stSidebar"] .stMarkdown h2 {
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 1.3rem;
        }

        section[data-testid="stSidebar"] .stMarkdown h3 {
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            color: var(--text-primary);
            font-size: 1rem;
        }

        /* ── Expanders ────────────────────────────────────────────────── */
        .streamlit-expanderHeader {
            background: var(--bg-glass) !important;
            border: 1px solid var(--border-glass) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-primary) !important;
            font-weight: 500 !important;
            transition: var(--transition-smooth) !important;
        }

        .streamlit-expanderHeader:hover {
            background: var(--bg-glass-hover) !important;
            border-color: var(--border-glass-hover) !important;
        }

        /* ── Mode Radio Buttons ───────────────────────────────────────── */
        .stRadio > div {
            gap: 0.5rem;
        }

        /* ── Player Wrapper ───────────────────────────────────────────── */
        .player-wrapper {
            background: var(--bg-glass);
            backdrop-filter: blur(var(--blur-glass));
            -webkit-backdrop-filter: blur(var(--blur-glass));
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-lg);
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            box-shadow: var(--glow-purple);
        }

        /* ── Section Dividers ─────────────────────────────────────────── */
        hr {
            border: none !important;
            height: 1px !important;
            background: linear-gradient(90deg, transparent, var(--border-glass), var(--accent-purple), var(--border-glass), transparent) !important;
            margin: 1.5rem 0 !important;
        }

        /* ── Scrollbar ────────────────────────────────────────────────── */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }

        ::-webkit-scrollbar-track {
            background: transparent;
        }

        ::-webkit-scrollbar-thumb {
            background: rgba(139, 92, 246, 0.3);
            border-radius: 3px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: rgba(139, 92, 246, 0.5);
        }

        /* ── Text Areas & Inputs ──────────────────────────────────────── */
        .stTextArea textarea, .stTextInput input {
            background: var(--bg-glass) !important;
            border: 1px solid var(--border-glass) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-primary) !important;
            font-family: 'Inter', sans-serif !important;
            transition: var(--transition-smooth) !important;
        }

        .stTextArea textarea:focus, .stTextInput input:focus {
            border-color: var(--accent-purple) !important;
            box-shadow: 0 0 0 2px rgba(168, 85, 247, 0.15) !important;
        }

        /* ── Select Boxes ─────────────────────────────────────────────── */
        .stSelectbox > div > div {
            background: var(--bg-glass) !important;
            border: 1px solid var(--border-glass) !important;
            border-radius: var(--radius-md) !important;
            transition: var(--transition-smooth) !important;
        }

        /* ── Quick Preset Buttons ─────────────────────────────────────── */
        .preset-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 0.6rem;
            margin: 0.8rem 0;
        }

        .preset-btn {
            background: var(--bg-glass);
            backdrop-filter: blur(8px);
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-md);
            padding: 0.6rem 0.5rem;
            text-align: center;
            cursor: pointer;
            transition: var(--transition-smooth);
            color: var(--text-primary);
            font-size: 0.8rem;
            font-weight: 500;
        }

        .preset-btn:hover {
            background: var(--bg-glass-hover);
            border-color: var(--accent-purple);
            transform: translateY(-2px);
            box-shadow: var(--glow-purple);
        }

        .preset-btn .preset-icon {
            font-size: 1.4rem;
            display: block;
            margin-bottom: 0.25rem;
        }

        /* ── History Table ─────────────────────────────────────────────── */
        .history-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            font-size: 0.85rem;
        }

        .history-table th {
            background: var(--bg-glass);
            color: var(--accent-purple);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.72rem;
            letter-spacing: 0.08em;
            padding: 0.7rem 0.8rem;
            border-bottom: 1px solid var(--border-glass);
        }

        .history-table th:first-child { border-radius: var(--radius-sm) 0 0 0; }
        .history-table th:last-child { border-radius: 0 var(--radius-sm) 0 0; }

        .history-table td {
            padding: 0.6rem 0.8rem;
            color: var(--text-primary);
            border-bottom: 1px solid rgba(139, 92, 246, 0.08);
        }

        .history-table tr:hover td {
            background: var(--bg-glass);
        }

        /* ── Blend Slider Visual ──────────────────────────────────────── */
        .blend-label {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.3rem;
        }

        .blend-label .emotion-tag {
            background: var(--bg-glass);
            border: 1px solid var(--border-glass);
            border-radius: 20px;
            padding: 0.2rem 0.8rem;
            font-size: 0.82rem;
            font-weight: 500;
            color: var(--text-primary);
        }

        .blend-label .emotion-tag.active {
            border-color: var(--accent-purple);
            color: var(--accent-purple);
        }

        /* ── Generation Badge ─────────────────────────────────────────── */
        .gen-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            background: var(--gradient-accent);
            color: white;
            font-size: 0.72rem;
            font-weight: 600;
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            margin-left: 0.5rem;
        }

        /* ── Fade In Animation ─────────────────────────────────────────── */
        .fade-in {
            animation: fadeIn 0.6s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* ── Slide Up Animation ───────────────────────────────────────── */
        .slide-up {
            animation: slideUp 0.5s ease-out;
        }

        @keyframes slideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* ── Footer ───────────────────────────────────────────────────── */
        .harmonix-footer {
            text-align: center;
            color: var(--text-muted);
            font-size: 0.8rem;
            padding: 1.5rem 0;
            font-family: 'Inter', sans-serif;
        }

        .harmonix-footer a {
            color: var(--accent-purple);
            text-decoration: none;
        }

        .harmonix-footer .footer-divider {
            margin: 0 0.5rem;
            color: var(--text-muted);
        }
    </style>
    """
