# 🤖 CodeAlpha AI Internship Tasks

 

Internship tasks completed as part of the **CodeAlpha Artificial Intelligence Internship Program** — June 2026 Batch.

 

**Intern:** Sandra Fiona 

**GitHub:** [@sandrafiona-dev](https://github.com/sandrafiona-dev) 

**Repo:** [codealpha_tasks](https://github.com/sandrafiona-dev/codealpha_tasks)

 

---

 

## ✅ Tasks Completed

 

| # | Task | Status |

|---|------|--------|

| Task 1 | Language Translation Tool | ✅ Completed |

| Task 2 | Chatbot for FAQs | ✅ Completed |

| Task 3 | Music Generation with AI | ✅ Completed |

 

---

 

## 📁 Repository Structure

 

```

codealpha_tasks/

├── task1_language_translation/

│   ├── app.py

│   ├── templates/

│   └── requirements.txt

├── task2_faq_chatbot/

│   ├── chatbot.py

│   ├── faqs.json

│   ├── ui/

│   └── requirements.txt

├── task3_music_generation/

│   ├── train.py

│   ├── generate.py

│   ├── requirements.txt

│   └── output/

└── README.md

```

 

---

 

## 🌐 Task 1 — Language Translation Tool

 

A web-based translation interface that lets users enter text, choose source and target languages, and receive instant translations.

 

**Features:**

- Clean UI with source and target language selectors

- Translation powered by Google Translate API / Deep Translator

- Copy-to-clipboard support

- Text-to-speech for translated output (optional)

**Tech Stack:** Python · Flask · Google Translate API · HTML/CSS/JavaScript

 

**Run locally:**

```bash

cd task1_language_translation

pip install -r requirements.txt

python app.py

```

 

---

 

## 💬 Task 2 — Chatbot for FAQs

 

An NLP-powered FAQ chatbot that matches user queries to the most relevant pre-defined answers using cosine similarity.

 

**Features:**

- NLP preprocessing pipeline (tokenization, stopword removal, lemmatization) via NLTK/SpaCy

- TF-IDF vectorization + cosine similarity for intent matching

- Chat UI built with JavaScript (ported from Python prototype)

- Fallback response for low-confidence matches

**Tech Stack:** Python · NLTK / SpaCy · scikit-learn · JavaScript · HTML/CSS

 

**Run locally:**

```bash

cd task2_faq_chatbot

pip install -r requirements.txt

python chatbot.py

```

 

---

 

## 🎵 Task 3 — Music Generation with AI

 

An AI model trained on MIDI music data to learn musical patterns and generate original music sequences using deep learning.

 

**Features:**

- MIDI dataset preprocessing into note sequences using `music21`

- LSTM-based deep learning model to learn and generate music patterns

- Training pipeline with configurable epochs and sequence length

- Generated sequences exported as MIDI files and playable audio

**Tech Stack:** Python · PyTorch · music21 · LSTM · MIDI

 

**Run locally:**

```bash

cd task3_music_generation

pip install -r requirements.txt

# Train the model:

python train.py

# Generate music:

python generate.py

```

 

---

 

## 🛠️ Requirements

 

Each task has its own `requirements.txt`. To install dependencies for a specific task:

 

```bash

pip install -r taskN_folder/requirements.txt

```

 

**Common dependencies across tasks:**

```

numpy

opencv-python

torch

scikit-learn

flask

```

 

---

 

## 📬 Submission Details

 

- **Batch:** June 2026 

- **Deadline:** 30th June 2026 

- **Organization:** [CodeAlpha](https://www.codealpha.tech)
