import streamlit as st
from sentence_transformers import SentenceTransformer

# Cache the model to prevent reloading on every Streamlit rerun
@st.cache_resource
def load_embedding_model():
    """
    Loads the SentenceTransformer model for generating embeddings.
    Using 'all-MiniLM-L6-v2' for fast, high-quality semantic search.
    """
    model = SentenceTransformer('all-MiniLM-L6-v2')
    return model

def get_embeddings(text_list, model):
    """
    Generates embeddings for a list of strings.
    """
    # model.encode returns a numpy array
    embeddings = model.encode(text_list, show_progress_bar=False)
    return embeddings
