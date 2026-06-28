#!/usr/bin/env python3
"""
create_sample_data.py
Generates synthetic MIDI files for testing the pipeline.
Creates simple classical-style piano melodies using music21.
"""

import os
import random
# pyrefly: ignore [missing-import]
from music21 import stream, note, chord, tempo, instrument, meter, key

random.seed(42)

# ── Musical building blocks ────────────────────────────────────────────────
SCALES = {
    'C_major':  ['C', 'D', 'E', 'F', 'G', 'A', 'B'],
    'G_major':  ['G', 'A', 'B', 'C', 'D', 'E', 'F#'],
    'D_minor':  ['D', 'E', 'F', 'G', 'A', 'Bb', 'C'],
    'A_minor':  ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
    'F_major':  ['F', 'G', 'A', 'Bb', 'C', 'D', 'E'],
    'Bb_major': ['Bb', 'C', 'D', 'Eb', 'F', 'G', 'A'],
    'E_minor':  ['E', 'F#', 'G', 'A', 'B', 'C', 'D'],
    'D_major':  ['D', 'E', 'F#', 'G', 'A', 'B', 'C#'],
}

CHORD_PROGRESSIONS = [
    # I - IV - V - I patterns
    [(0, 2, 4), (3, 5, 0), (4, 6, 1), (0, 2, 4)],
    # I - V - vi - IV
    [(0, 2, 4), (4, 6, 1), (5, 0, 2), (3, 5, 0)],
    # I - vi - IV - V
    [(0, 2, 4), (5, 0, 2), (3, 5, 0), (4, 6, 1)],
    # vi - IV - I - V
    [(5, 0, 2), (3, 5, 0), (0, 2, 4), (4, 6, 1)],
]

DURATIONS = [0.25, 0.5, 0.5, 0.5, 1.0, 1.0, 1.5, 2.0]
OCTAVES = [3, 4, 4, 4, 5, 5]


def generate_melody(scale_notes, n_notes=80):
    """Generate a simple melodic line."""
    notes = []
    prev_idx = random.randint(0, len(scale_notes) - 1)

    for _ in range(n_notes):
        # Step-wise motion with occasional leaps
        step = random.choice([-2, -1, -1, 0, 1, 1, 2])
        idx = (prev_idx + step) % len(scale_notes)
        pitch_name = scale_notes[idx]
        octave = random.choice(OCTAVES)
        duration = random.choice(DURATIONS)

        n = note.Note(f'{pitch_name}{octave}')
        n.quarterLength = duration
        n.volume.velocity = random.randint(50, 100)
        notes.append(n)
        prev_idx = idx

    return notes


def generate_chord_section(scale_notes, progression, repeats=4):
    """Generate a chord progression section."""
    elements = []
    for _ in range(repeats):
        for chord_degrees in progression:
            pitches = []
            for deg in chord_degrees:
                pitch_name = scale_notes[deg % len(scale_notes)]
                pitches.append(f'{pitch_name}4')
            c = chord.Chord(pitches)
            c.quarterLength = 2.0
            c.volume.velocity = random.randint(40, 80)
            elements.append(c)
    return elements


def create_midi_file(filepath, scale_name='C_major', bpm_val=120, n_notes=120):
    """Create a single MIDI file with melody and chords."""
    scale_notes = SCALES[scale_name]
    s = stream.Stream()

    # Metadata
    s.insert(0, tempo.MetronomeMark(number=bpm_val))
    s.insert(0, instrument.Piano())
    s.insert(0, meter.TimeSignature('4/4'))

    # Generate melody
    melody = generate_melody(scale_notes, n_notes)
    offset = 0.0
    for n in melody:
        n.offset = offset
        s.insert(offset, n)
        offset += n.quarterLength

    # Add some chords interspersed
    progression = random.choice(CHORD_PROGRESSIONS)
    chords = generate_chord_section(scale_notes, progression, repeats=3)
    chord_offset = 0.0
    for c in chords:
        c.offset = chord_offset
        s.insert(chord_offset, c)
        chord_offset += c.quarterLength

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    s.write('midi', fp=filepath)
    print(f'  ✅ Created: {filepath}')


def main():
    """Generate a diverse set of sample MIDI files."""
    print('🎵 Generating sample MIDI dataset...\n')

    dataset_dir = 'dataset'
    os.makedirs(dataset_dir, exist_ok=True)

    configs = [
        ('bach_prelude_1',    'C_major',  100, 150),
        ('bach_prelude_2',    'G_major',  108, 140),
        ('bach_invention_1',  'D_minor',  92,  130),
        ('bach_invention_2',  'A_minor',  96,  135),
        ('mozart_sonata_1',   'F_major',  120, 160),
        ('mozart_sonata_2',   'Bb_major', 116, 155),
        ('chopin_nocturne_1', 'E_minor',  72,  180),
        ('chopin_nocturne_2', 'D_minor',  68,  175),
        ('chopin_waltz_1',    'D_major',  140, 140),
        ('chopin_waltz_2',    'A_minor',  132, 145),
        ('beethoven_piece_1', 'C_major',  108, 160),
        ('beethoven_piece_2', 'G_major',  112, 155),
        ('simple_melody_1',   'C_major',  100, 120),
        ('simple_melody_2',   'F_major',  100, 120),
        ('simple_melody_3',   'G_major',  100, 120),
        ('etude_1',           'D_minor',  88,  200),
        ('etude_2',           'E_minor',  84,  190),
        ('etude_3',           'A_minor',  80,  185),
        ('prelude_3',         'Bb_major', 76,  170),
        ('prelude_4',         'D_major',  82,  165),
    ]

    for name, scale, bpm_val, n_notes in configs:
        filepath = os.path.join(dataset_dir, f'{name}.mid')
        create_midi_file(filepath, scale, bpm_val, n_notes)

    total = len(configs)
    print(f'\n✅ Generated {total} MIDI files in {dataset_dir}/')
    print(f'   Total notes: ~{sum(c[3] for c in configs):,}')
    print(f'\nNext: run "python src/preprocess.py" to build training data')


if __name__ == '__main__':
    main()
