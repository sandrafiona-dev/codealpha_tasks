import streamlit as st
import pandas as pd
import time
import os

from utils.preprocess import preprocess_text
from utils.embeddings import load_embedding_model, get_embeddings
from utils.vector_store import build_faiss_index, search_faiss
from utils.rag_engine import (
    generate_rag_response, 
    calculate_confidence, 
    get_confidence_badge_class,
    calculate_reading_time,
    extract_intent_and_difficulty
)
from utils.speech import speech_to_text, text_to_speech, SPEECH_REC_AVAILABLE, TTS_AVAILABLE
from utils.analytics import update_analytics, generate_dashboard_figures

st.set_page_config(page_title="AI FAQ Assistant Pro", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# Absolute path resolution relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load Premium CSS
def load_css():
    try:
        css_path = os.path.join(BASE_DIR, "assets", "style.css")
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css()

# Session State Initialization
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "voice_input" not in st.session_state:
    st.session_state.voice_input = ""
if "current_intent" not in st.session_state:
    st.session_state.current_intent = None
if "current_difficulty" not in st.session_state:
    st.session_state.current_difficulty = None
if "current_category" not in st.session_state:
    st.session_state.current_category = None

# Load Data and Models
@st.cache_data
def load_faq_data(path, mtime):
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame(columns=['Question', 'Answer', 'Category'])

faq_path = os.path.join(BASE_DIR, "data", "faq.csv")
mtime = os.path.getmtime(faq_path) if os.path.exists(faq_path) else 0
df = load_faq_data(faq_path, mtime)
model = load_embedding_model()

@st.cache_resource
def get_index(_df, _model, mtime):
    if _df.empty:
        return None
    questions = _df['Question'].tolist()
    embeddings = get_embeddings(questions, _model)
    return build_faiss_index(embeddings)

faiss_index = get_index(df, model, mtime)

# ==========================================
# LEFT PANEL (SIDEBAR)
# ==========================================
st.sidebar.markdown("<h2 style='text-align:center; color: #7C3AED; font-weight:800; font-size: 1.8rem; margin-bottom: 0;'>⚡ AI FAQ Pro</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align:center; color:#94a3b8; font-size:0.8rem; margin-bottom: 30px;'>Workspace / Personal</p>", unsafe_allow_html=True)

if st.sidebar.button("➕ New Chat", use_container_width=True):
    st.session_state.chat_history = []
    st.session_state.current_intent = None
    st.rerun()

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("### Categories")

if not df.empty and 'Category' in df.columns:
    categories = df['Category'].dropna().unique().tolist()
else:
    categories = ["AI", "ML", "NLP", "LLM", "RAG", "Python", "Data Science"]

for cat in categories:
    with st.sidebar.expander(f"📌 {cat}"):
        if not df.empty and 'Category' in df.columns:
            cat_questions = df[df['Category'] == cat]['Question'].tolist()
            for i, q in enumerate(cat_questions[:5]):
                if st.button(f"{q}", key=f"sidebar_btn_{cat}_{i}", use_container_width=True):
                    st.session_state.sidebar_query = q
                    st.rerun()
        else:
            st.write("No questions available.")

# Removed Shortcuts and User Profile section per user request.

# ==========================================
# MAIN LAYOUT: CENTER AND RIGHT PANELS
# ==========================================
center_col, right_col = st.columns([3, 1], gap="large")

with center_col:
    if not st.session_state.chat_history:
        st.markdown("<h1 class='animated-title fade-in'>Good Morning 👋</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#94a3b8; font-weight:400; margin-bottom:30px;' class='fade-in'>What would you like to learn today?</h3>", unsafe_allow_html=True)
        
        # Suggestion Cards
        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            st.markdown("<div class='suggestion-card'>What is RAG?</div>", unsafe_allow_html=True)
        with s_col2:
            st.markdown("<div class='suggestion-card'>Explain Transformers</div>", unsafe_allow_html=True)
        with s_col3:
            st.markdown("<div class='suggestion-card'>What are Embeddings?</div>", unsafe_allow_html=True)
        
        st.write("<br><br>", unsafe_allow_html=True)

    # Search Bar & Voice
    with st.form("search_form", clear_on_submit=True):
        col_in, col_btn = st.columns([8, 1])
        with col_in:
            user_query = st.text_input("AI Search Bar", label_visibility="collapsed", placeholder="Ask anything about AI, ML, NLP, Python...", value=st.session_state.voice_input)
        with col_btn:
            submit_search = st.form_submit_button("🔍")
            
    if SPEECH_REC_AVAILABLE:
        if st.button("🎤 Voice Input", help="Click to use voice recognition"):
            with st.spinner("Listening..."):
                recognized_text = speech_to_text()
                if recognized_text and not recognized_text.startswith("Timeout"):
                    st.session_state.voice_input = recognized_text
                    st.rerun()

    # Search Logic
    sidebar_query = st.session_state.pop("sidebar_query", None)
    active_query = user_query if (submit_search and user_query) else sidebar_query

    if active_query:
        start_time = time.time()
        
        with st.spinner("Analyzing and synthesizing..."):
            if df.empty or faiss_index is None:
                st.error("FAQ Database is empty or index could not be built.")
            else:
                clean_query = preprocess_text(active_query)
                query_emb = get_embeddings([clean_query], model)[0]
                
                top_faqs = search_faiss(query_emb, faiss_index, df, k=5)
                distances = [f['distance'] for f in top_faqs]
                confidence = calculate_confidence(distances)
                
                answer = generate_rag_response(active_query, top_faqs)
                
                duration = time.time() - start_time
                timestamp = time.strftime('%H:%M %p')
                top_category = top_faqs[0]['category'] if top_faqs else "General"
                
                # Advanced Insights Extraction
                meta_info = extract_intent_and_difficulty(active_query)
                read_time = calculate_reading_time(answer)
                
                st.session_state.current_intent = meta_info['intent']
                st.session_state.current_difficulty = meta_info['difficulty']
                st.session_state.current_category = top_category

                chat_record = {
                    "question": active_query,
                    "answer": answer,
                    "confidence": confidence,
                    "timestamp": timestamp,
                    "duration": duration,
                    "category": top_category,
                    "difficulty": meta_info['difficulty'],
                    "read_time": read_time,
                    "sources": len(top_faqs)
                }
                
                st.session_state.chat_history.insert(0, chat_record)
                update_analytics(st.session_state, user_query, top_category, confidence, duration)
                
                st.session_state.voice_input = ""
                st.rerun()

    # Chat UI Rendering
    st.write("<br>", unsafe_allow_html=True)
    for idx, chat in enumerate(st.session_state.chat_history):
        # User Message
        st.markdown(f"""
        <div class="chat-row user fade-in">
            <div class="chat-bubble">
                {chat['question']}
            </div>
        </div>
        """.replace('\n\n', '\n'), unsafe_allow_html=True)
        
        # AI Answer Card
        badge_class = get_confidence_badge_class(chat['confidence'])
        
        # Clean answer to prevent markdown breaking
        safe_answer = str(chat['answer']).replace('\n\n', '<br><br>').replace('\n', '<br>')
        
        st.markdown(f"""
        <div class="chat-row ai fade-in">
            <div class="premium-card" style="width: 100%;">
                <div style="display:flex; justify-content:space-between; margin-bottom: 15px;">
                    <div><span style="font-weight:bold; color: #7C3AED;">✨ AI FAQ Assistant</span> <span style="color:#94a3b8; font-size:0.8rem; margin-left: 10px;">{chat['timestamp']}</span></div>
                    <div><span class="badge {badge_class}">{chat['confidence']}% Match</span></div>
                </div>
                <div style="font-size: 1.05rem; line-height: 1.7;">
                    {safe_answer}
                </div>
                <div class="ai-meta">
                    <div>
                        <span style="margin-right: 15px;">⏱️ {chat['read_time']}</span>
                        <span style="margin-right: 15px;">📚 {chat['sources']} Sources Used</span>
                        <span>🎯 Level: {chat['difficulty']}</span>
                    </div>
                </div>
            </div>
        </div>
        """.replace('\n\n', '\n'), unsafe_allow_html=True)
        
        # Action Buttons below AI Card
        if TTS_AVAILABLE:
            col_action1, col_action2 = st.columns([1, 10])
            with col_action1:
                if st.button("🔊", key=f"speak_{idx}", help="Read aloud"):
                    text_to_speech(chat['answer'])
            st.markdown("<br>", unsafe_allow_html=True)

    # Learning Path (Smart Recommendations) for the latest query
    if st.session_state.chat_history and st.session_state.current_category:
        st.markdown("### 🎓 Smart Recommendations")
        st.markdown(f"<p style='color:#94a3b8;'>Because you asked about <b>{st.session_state.current_category}</b></p>", unsafe_allow_html=True)
        rec_col1, rec_col2, rec_col3 = st.columns(3)
        with rec_col1:
            st.markdown("<div class='premium-card' style='text-align:center; padding:15px;'><b style='color:#06B6D4;'>1. Core Concepts</b><br><span style='font-size:0.8rem;color:#94a3b8;'>Foundation</span></div>", unsafe_allow_html=True)
        with rec_col2:
            st.markdown("<div class='premium-card' style='text-align:center; padding:15px;'><b style='color:#22C55E;'>2. Architectures</b><br><span style='font-size:0.8rem;color:#94a3b8;'>Deep Dive</span></div>", unsafe_allow_html=True)
        with rec_col3:
            st.markdown("<div class='premium-card' style='text-align:center; padding:15px;'><b style='color:#f59e0b;'>3. Optimization</b><br><span style='font-size:0.8rem;color:#94a3b8;'>Advanced</span></div>", unsafe_allow_html=True)


# ==========================================
# RIGHT PANEL (INSIGHTS)
# ==========================================
with right_col:
    st.markdown("### 🔍 Live Insights")
    
    if st.session_state.chat_history:
        latest = st.session_state.chat_history[0]
        st.markdown(f"""
        <div class="premium-card" style="padding: 15px;">
            <p style="margin:0; font-size:0.8rem; color:#94a3b8;">Detected Topic</p>
            <p style="margin:0; font-weight:bold; font-size:1.1rem; color:#06B6D4;">{latest['category']}</p>
            <hr style="border-color: rgba(255,255,255,0.05); margin: 10px 0;">
            <p style="margin:0; font-size:0.8rem; color:#94a3b8;">Intent Classification</p>
            <p style="margin:0; font-weight:bold; font-size:1.1rem; color:#22C55E;">{st.session_state.current_intent}</p>
            <hr style="border-color: rgba(255,255,255,0.05); margin: 10px 0;">
            <p style="margin:0; font-size:0.8rem; color:#94a3b8;">Search Duration</p>
            <p style="margin:0; font-weight:bold; font-size:1.1rem; color:#f59e0b;">{latest['duration']:.2f}s</p>
        </div>
        """.replace('\n\n', '\n'), unsafe_allow_html=True)
    else:
        st.info("Awaiting your first query...")

    st.markdown("<br>### 📊 Analytics", unsafe_allow_html=True)
    figs = generate_dashboard_figures(st.session_state)
    
    if figs:
        # Mini Metrics
        m1, m2 = st.columns(2)
        m1.metric("Searches", figs['total_questions'])
        m2.metric("Avg Conf", f"{figs['avg_confidence']:.1f}%")
        
        st.plotly_chart(figs['confidence_gauge'], use_container_width=True, config={'displayModeBar': False})
        st.plotly_chart(figs['category_dist'], use_container_width=True, config={'displayModeBar': False})
    else:
        st.write("<p style='color:#94a3b8; font-size:0.9rem;'>No analytics data available yet.</p>", unsafe_allow_html=True)

    st.markdown("<br>### 🕸️ AI Knowledge Map", unsafe_allow_html=True)
    st.markdown("""
    <div class="premium-card" style="padding: 20px; text-align:center;">
        <span style="font-size: 2rem;">🧠</span><br>
        <span style="color:#94a3b8; font-size:0.9rem;">Interactive Map <br> (Powered by Graphviz)</span>
        <br><br>
        <button style="background:var(--primary); color:white; border:none; padding:8px 16px; border-radius:8px; cursor:pointer;">Explore Graph</button>
    </div>
    """, unsafe_allow_html=True)
