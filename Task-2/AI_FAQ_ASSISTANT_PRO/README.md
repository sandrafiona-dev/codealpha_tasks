# AI FAQ ASSISTANT PRO (2026 EDITION)

A production-ready AI FAQ Assistant powered by Streamlit, FAISS, Sentence Transformers, and Google Gemini.

## Features
- **Semantic Search**: Powered by `all-MiniLM-L6-v2` and FAISS vector database.
- **RAG Generation**: Uses Gemini to synthesize accurate answers based on retrieved context.
- **Confidence Engine**: Calculates a confidence score for each response.
- **Voice Assistant**: Text-to-Speech and Speech-to-Text integration.
- **Analytics Dashboard**: Real-time insights into user interactions.
- **Modern UI**: Glassmorphism, animated gradients, and dark theme.

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Generate FAQ Dataset (Optional if already generated):
   *Note: Ensure you have run the FAQ generation script if `data/faq.csv` is missing.*

3. Configure API Keys:
   Edit `.env` and insert your Gemini API Key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. Run the application:
   ```bash
   streamlit run app.py
   ```
