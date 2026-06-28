import os
import json
import urllib.request
from dotenv import load_dotenv
import streamlit as st

def get_gemini_api_key():
    # 1. Try Streamlit Secrets (for Streamlit Cloud deployment)
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    
    # 2. Fall back to environment / dotenv (for local development)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dotenv_path = os.path.abspath(os.path.join(base_dir, "..", ".env"))
    load_dotenv(dotenv_path, override=True)
    return os.getenv("GEMINI_API_KEY")

def generate_rag_response(user_question, retrieved_faqs):
    """
    Uses Gemini REST API directly to avoid SDK version incompatibilities.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        return "System configuration error: GEMINI_API_KEY is not set."
    
    # Format the context
    context_text = ""
    for idx, faq in enumerate(retrieved_faqs, 1):
        context_text += f"FAQ {idx}:\nQ: {faq['question']}\nA: {faq['answer']}\n\n"

    prompt = f"""
    You are an advanced AI FAQ assistant for a premium SaaS platform.
    First, try to answer the user's question using the provided Context.
    If the Context does not contain the answer, do NOT say "I could not find relevant information." 
    Instead, seamlessly use your vast general knowledge to answer the question intelligently.

    Context:
    {context_text}

    Question:
    {user_question}

    Answer:
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        err_msg = str(e)
        if hasattr(e, 'read'):
            err_msg += f" Response: {e.read().decode('utf-8')}"
        return f"An error occurred: {err_msg}"

def calculate_confidence(distances):
    """
    Maps FAISS L2 distances to a 0-100 confidence score.
    For all-MiniLM-L6-v2, L2 distance is typically between 0 and 2 
    (since vectors might not be strictly normalized, but typically range small).
    Smaller distance = higher confidence.
    """
    if not distances:
        return 0
    
    # Take the best distance (first one)
    best_dist = distances[0]
    
    # Arbitrary heuristic for mapping distance to percentage:
    # 0 distance = 100%, >1.5 distance = low%
    # This is tuned for typical sentence-transformers L2 distances.
    score = max(0, min(100, int((1.0 - (best_dist / 2.0)) * 100)))
    
    # Add a slight boost to keep numbers in expected bounds
    if score > 0:
        score = min(100, score + 15)
        
    return score

def get_confidence_badge_class(score):
    if score >= 80:
        return "confidence-high"
    elif score >= 50:
        return "confidence-med"
    else:
        return "confidence-low"

def calculate_reading_time(text: str) -> str:
    """
    Estimates reading time based on an average reading speed of 200 words per minute.
    """
    words = len(text.split())
    minutes = max(1, round(words / 200))
    return f"{minutes} min read"

def extract_intent_and_difficulty(question: str) -> dict:
    """
    Mock/heuristic function to extract intent and difficulty level from a question
    to populate the Advanced Insights panel.
    """
    question = question.lower()
    
    # Difficulty heuristic
    if any(word in question for word in ['what', 'who', 'when', 'define']):
        difficulty = "Beginner"
    elif any(word in question for word in ['how', 'why', 'explain']):
        difficulty = "Intermediate"
    elif any(word in question for word in ['compare', 'architecture', 'implement', 'optimize']):
        difficulty = "Advanced"
    else:
        difficulty = "Beginner"

    # Intent heuristic
    if 'code' in question or 'implement' in question:
        intent = "Implementation"
    elif 'what is' in question or 'define' in question:
        intent = "Definition"
    elif 'how to' in question:
        intent = "Tutorial"
    else:
        intent = "Information Retrieval"

    return {
        "difficulty": difficulty,
        "intent": intent
    }

