import nltk
import re

# Ensure necessary NLTK data is downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

def preprocess_text(text: str) -> str:
    """
    Cleans text for basic tokenization if needed.
    Note: For all-MiniLM-L6-v2, raw text is often best, but 
    this handles basic normalization (extra spaces, basic case).
    """
    if not isinstance(text, str):
        return ""
        
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
