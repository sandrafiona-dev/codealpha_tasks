#!/usr/bin/env python3
"""
notebooks/eda.py
Exploratory Data Analysis for the Music Generation dataset.
Run after preprocess.py to visualise note distributions and sequence stats.
"""

import pickle
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
from collections import Counter
from pathlib import Path

# ── Style ──────────────────────────────────────────────────────────────────
plt.style.use('seaborn-v0_8-darkgrid')
PALETTE = sns.color_palette('viridis', 20)


def load_artefacts() -> tuple:
    """Load preprocessed notes and vocabulary."""
    with open('models/all_notes.pkl', 'rb') as f:
        all_notes = pickle.load(f)
    with open('models/note2int.pkl', 'rb') as f:
        note2int = pickle.load(f)
    with open('models/int2note.pkl', 'rb') as f:
        int2note = pickle.load(f)
    return all_notes, note2int, int2note


def plot_note_frequency(all_notes: list, top_n: int = 30) -> None:
    """
    Bar chart of the top-N most frequent note/chord tokens.
    Helps identify whether a few notes dominate the dataset (imbalance).
    """
    counts = Counter(all_notes)
    top_tokens = counts.most_common(top_n)
    tokens, freqs = zip(*top_tokens)

    fig, ax = plt.subplots(figsize=(14, 5))
    bars = ax.bar(tokens, freqs, color=PALETTE[:top_n])
    ax.set_title(f'Top {top_n} Most Frequent Notes / Chords', fontsize=14, pad=12)
    ax.set_xlabel('Note / Chord Token', fontsize=11)
    ax.set_ylabel('Frequency', fontsize=11)
    ax.set_xticks(range(top_n))
    ax.set_xticklabels(tokens, rotation=45, ha='right', fontsize=8)
    # Annotate bar heights
    for bar, freq in zip(bars, freqs):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                str(freq), ha='center', va='bottom', fontsize=7)
    plt.tight_layout()
    plt.savefig('outputs/note_frequency.png', dpi=150)
    plt.show()
    print(f'Saved: outputs/note_frequency.png')


def plot_pitch_distribution(all_notes: list) -> None:
    """
    Histogram of pitch values (single notes only, not chords).
    Reveals the pitch range the model needs to learn.
    """
    # Filter single notes (no dot separator)
    single_notes = [n for n in all_notes if '.' not in n and n.isalpha() is False]
    # Extract octave numbers
    octaves = []
    for n in single_notes:
        try:
            octave = int(''.join(filter(str.isdigit, n)))
            octaves.append(octave)
        except ValueError:
            pass

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(octaves, bins=range(0, 10), color='steelblue', edgecolor='white', alpha=0.85)
    ax.set_title('Octave Distribution (Single Notes)', fontsize=13)
    ax.set_xlabel('Octave', fontsize=11)
    ax.set_ylabel('Count', fontsize=11)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    plt.tight_layout()
    plt.savefig('outputs/pitch_distribution.png', dpi=150)
    plt.show()
    print(f'Saved: outputs/pitch_distribution.png')


def plot_token_type_split(all_notes: list) -> None:
    """
    Pie chart showing ratio of single notes to chords in the dataset.
    """
    chords_count = sum(1 for n in all_notes if '.' in n)
    notes_count  = len(all_notes) - chords_count

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(
        [notes_count, chords_count],
        labels=['Single Notes', 'Chords'],
        autopct='%1.1f%%',
        colors=['#4C72B0', '#55A868'],
        startangle=140,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )
    ax.set_title('Note vs. Chord Distribution', fontsize=13)
    plt.tight_layout()
    plt.savefig('outputs/note_chord_split.png', dpi=150)
    plt.show()


def plot_sequence_statistics(all_notes: list, seq_length: int = 100) -> None:
    """
    Histogram showing how many training sequences would be generated
    at various window sizes. Helps choose seq_length.
    """
    sizes = [50, 75, 100, 125, 150]
    counts = [max(0, len(all_notes) - s) for s in sizes]

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar([str(s) for s in sizes], counts, color=PALETTE[::4])
    ax.set_title('Training Samples vs. Sequence Length', fontsize=13)
    ax.set_xlabel('Sequence Length (time steps)', fontsize=11)
    ax.set_ylabel('Number of Training Samples', fontsize=11)
    for bar, cnt in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                f'{cnt:,}', ha='center', va='bottom', fontsize=9)
    plt.tight_layout()
    plt.savefig('outputs/sequence_statistics.png', dpi=150)
    plt.show()


def print_summary(all_notes: list, note2int: dict) -> None:
    """Print key dataset statistics to console."""
    counts = Counter(all_notes)
    print('\n' + '='*50)
    print('  DATASET SUMMARY')
    print('='*50)
    print(f'  Total tokens      : {len(all_notes):,}')
    print(f'  Unique tokens     : {len(note2int):,}')
    print(f'  Most common token : {counts.most_common(1)[0][0]} ({counts.most_common(1)[0][1]:,} times)')
    print(f'  Chord tokens      : {sum(1 for n in all_notes if "." in n):,}')
    print(f'  Single notes      : {sum(1 for n in all_notes if "." not in n):,}')
    print('='*50 + '\n')


if __name__ == '__main__':
    import os
    os.makedirs('outputs', exist_ok=True)

    all_notes, note2int, int2note = load_artefacts()
    print_summary(all_notes, note2int)
    plot_note_frequency(all_notes, top_n=30)
    plot_pitch_distribution(all_notes)
    plot_token_type_split(all_notes)
    plot_sequence_statistics(all_notes)
    print('EDA complete. All plots saved to outputs/')
