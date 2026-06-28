# 🎵 Music Generation AI

> **End-to-end AI music generation** using LSTM neural networks, TensorFlow/Keras, and Music21. Learns patterns from MIDI files and generates new musical sequences with a Streamlit web interface.

![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-FF6F00?logo=tensorflow&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🏗️ Architecture

```
┌──────────────┐     ┌────────────────┐     ┌──────────────┐
│  MIDI Files  │────▶│  Preprocessing │────▶│   Training   │
│  (dataset/)  │     │  (music21)     │     │   (LSTM)     │
└──────────────┘     └────────────────┘     └──────┬───────┘
                                                    │
                     ┌────────────────┐     ┌──────▼───────┐
                     │  MIDI Output   │◀────│  Generation  │
                     │  (music21)     │     │  (sampling)  │
                     └────────┬───────┘     └──────────────┘
                              │
                     ┌────────▼───────┐
                     │   Streamlit    │
                     │   Web UI       │
                     └────────────────┘
```

### Model Architecture

```
Input (seq_length, 1)
    │
    ▼
LSTM (512 units, return_sequences=True)
    │
Dropout (0.3)
    │
LSTM (512 units, return_sequences=False)
    │
Dropout (0.3)
    │
Dense (256, ReLU) + L2 Regularization
    │
BatchNormalization
    │
Dense (vocab_size, Softmax)
    │
    ▼
Output: P(next_token | context)
```

---

## 📂 Project Structure

```
Music_Generation_AI/
├── app.py                  # Streamlit web interface
├── config.yaml             # All hyperparameters
├── requirements.txt        # Python dependencies
├── README.md               # This file
│
├── dataset/                # Place MIDI files here
│   └── *.mid / *.midi
│
├── src/
│   ├── preprocess.py       # MIDI → tokens → training sequences
│   ├── model.py            # LSTM model architecture
│   ├── train.py            # Training loop with callbacks
│   ├── generate.py         # Autoregressive generation + temperature sampling
│   └── utils.py            # Tokens → MIDI, audio conversion
│
├── notebooks/
│   └── eda.py              # Exploratory data analysis (4 charts)
│
├── models/                 # Saved weights, vocabulary, checkpoints
│   └── checkpoints/
│
├── outputs/                # Generated MIDI files and plots
└── logs/                   # Training logs and TensorBoard data
    └── tensorboard/
```

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
# Clone the repository
git clone https://github.com/your-username/Music_Generation_AI.git
cd Music_Generation_AI

# Create virtual environment
python -m venv venv
source venv/bin/activate      # Linux/Mac
# venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Get MIDI Data

Place MIDI files in the `dataset/` folder. Recommended starters:

| Dataset | Genre | Size | Link |
|---------|-------|------|------|
| MAESTRO v3 | Classical Piano | 200+ hours | [Download](https://magenta.tensorflow.org/datasets/maestro) |
| Nottingham | Folk / Traditional | 1,200 tunes | [GitHub](https://github.com/jukedeck/nottingham-dataset) |
| Lakh MIDI | Multi-genre | 176K files | [Download](https://colinraffel.com/projects/lmd/) |

**Dataset Statistics:**
- 128 General MIDI instruments
- 128 MIDI note values (0–127)
- 88 piano-key range supported
- 50,000+ note events extracted from MIDI files
- Duration, velocity, and timing information preserved

```bash
# Example: Download MAESTRO dataset
wget https://storage.googleapis.com/magentadata/datasets/maestro/v3.0.0/maestro-v3.0.0-midi.zip
unzip maestro-v3.0.0-midi.zip -d dataset/maestro/
```

### 3. Preprocess

```bash
python src/preprocess.py
```

Outputs: `models/X_input.npy`, `models/y_output.npy`, vocabulary pickles.

### 4. Explore Data (Optional)

```bash
python notebooks/eda.py
```

Generates 4 visualizations in `outputs/`.

### 5. Train

```bash
python src/train.py
```

- Training runs up to 50 epochs (early stopping at 10-epoch patience)
- Best weights saved to `models/checkpoints/best_weights.h5`
- Loss curves saved to `outputs/training_history.png`
- TensorBoard logs: `tensorboard --logdir logs/tensorboard/`

### 6. Launch Web Interface

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## ⚙️ Configuration

All hyperparameters are in [`config.yaml`](config.yaml):

| Parameter | Default | Description |
|-----------|---------|-------------|
| `model.sequence_length` | 100 | Input window size (time steps) |
| `model.lstm_units` | 512 | Hidden units per LSTM layer |
| `model.dropout_rate` | 0.3 | Dropout probability |
| `training.epochs` | 50 | Maximum training epochs |
| `training.batch_size` | 64 | Batch size |
| `training.learning_rate` | 0.001 | Adam initial learning rate |
| `generation.temperature` | 1.0 | Sampling temperature |
| `generation.n_notes` | 200 | Notes to generate |

---

## 🌡️ Temperature Guide

| Temperature | Effect | Best For |
|-------------|--------|----------|
| 0.1 – 0.5 | Conservative, repetitive | Predictable melodies |
| 0.6 – 1.0 | Balanced | General music generation |
| 1.1 – 1.5 | Creative, surprising | Experimental pieces |
| 1.6 – 2.0 | Very random | Abstract compositions |

---

## 🐳 Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
# Build and run
docker build -t music-gen-ai .
docker run -p 8501:8501 music-gen-ai
```

---

## ☁️ Streamlit Cloud Deployment

1. Push your repo to GitHub (include trained model weights in `models/`)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set main file: `app.py`
5. Deploy!

---

## 📊 Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| Deep Learning | TensorFlow 2.x / Keras |
| Music Parsing | Music21 |
| Data Processing | NumPy |
| Visualization | Matplotlib, Seaborn |
| Web Interface | Streamlit |
| Config | YAML |
| Audio (optional) | FluidSynth, pydub, ffmpeg |

---

## 📝 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [Music21](https://web.mit.edu/music21/) — MIT's music analysis toolkit
- [MAESTRO Dataset](https://magenta.tensorflow.org/datasets/maestro) — Google Magenta
- [TensorFlow](https://www.tensorflow.org/) — Google's ML framework
- [Streamlit](https://streamlit.io/) — Python web app framework

---

<p align="center">
  Built with ❤️ and AI
</p>
