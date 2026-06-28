import faiss
import numpy as np
import pandas as pd
import streamlit as st

@st.cache_resource
def build_faiss_index(embeddings):
    """
    Builds and caches a FAISS IndexFlatL2 for L2 distance (Euclidean).
    embeddings should be a numpy array.
    """
    dimension = embeddings.shape[1]
    # Use L2 distance for similarity (or IndexFlatIP for cosine if normalized)
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype('float32'))
    return index

def search_faiss(query_embedding, index, df, k=5):
    """
    Searches the FAISS index for the top k most similar vectors.
    Returns:
        results: list of dictionaries containing the Question, Answer, Category, and Score.
    """
    query_vector = np.array([query_embedding]).astype('float32')
    distances, indices = index.search(query_vector, k)
    
    results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(df):
            # FAISS L2 distance (lower is better). For confidence, we'll invert/normalize later.
            distance = distances[0][i]
            row = df.iloc[idx]
            results.append({
                "question": row['Question'],
                "answer": row['Answer'],
                "category": row['Category'],
                "distance": distance
            })
    return results
