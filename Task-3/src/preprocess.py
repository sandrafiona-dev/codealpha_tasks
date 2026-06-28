#!/usr/bin/env python3
"""
src/preprocess.py
REMI event-based MIDI preprocessing pipeline for the Music Transformer.
Extracts quantized note-on/duration/velocity, instrument, bar, position, and tempo events.
"""

import os
import glob
import pickle
import logging
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict

# pyrefly: ignore [missing-import]
import pretty_midi

# ── Logging setup ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/preprocess.log')
    ]
)
logger = logging.getLogger(__name__)


def load_config() -> dict:
    """Load hyperparameters from config.yaml."""
    import yaml
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)


def extract_remi_events(midi_path: str, steps_per_quarter: int = 4) -> List[str]:
    """
    Convert a single MIDI file into a sequence of REMI token strings.
    """
    try:
        pm = pretty_midi.PrettyMIDI(midi_path)
    except Exception as e:
        logger.warning(f'Failed to parse {midi_path}: {e}')
        return []
        
    all_notes = []
    for instrument in pm.instruments:
        program = instrument.program + 1  # 1-128
        if instrument.is_drum:
            program = 129
            
        for note in instrument.notes:
            all_notes.append({
                'pitch': note.pitch,
                'start': note.start,
                'end': note.end,
                'velocity': note.velocity,
                'program': program
            })
            
    if not all_notes:
        return []
        
    # Get tempo changes
    try:
        tempo_changes = pm.get_tempo_changes()
    except Exception:
        tempo_changes = (np.array([0.0]), np.array([120.0]))
        
    def get_tempo_at_time(t):
        times, values = tempo_changes
        if len(times) == 0:
            return 120
        idx = np.searchsorted(times, t, side='right') - 1
        return int(round(values[max(0, idx)]))

    # Convert seconds to grid steps
    beat_times = pm.get_beats()
    steps_per_bar = 4 * steps_per_quarter
    
    notes_with_steps = []
    for n in all_notes:
        try:
            # Interpolate to find note start/end in beats
            start_beat = np.interp(n['start'], beat_times, np.arange(len(beat_times)))
            end_beat = np.interp(n['end'], beat_times, np.arange(len(beat_times)))
            
            start_step = int(round(start_beat * steps_per_quarter))
            end_step = int(round(end_beat * steps_per_quarter))
            duration_steps = max(1, end_step - start_step)
            
            notes_with_steps.append({
                'pitch': n['pitch'],
                'start_step': start_step,
                'duration_steps': duration_steps,
                'velocity': n['velocity'],
                'program': n['program'],
                'start_time': n['start']
            })
        except Exception:
            continue
            
    # Sort notes chronologically by start_step, then program, then pitch
    notes_with_steps = sorted(notes_with_steps, key=lambda x: (x['start_step'], x['program'], x['pitch']))
    
    remi_events = []
    last_bar = -1
    last_pos = -1
    last_program = -1
    last_tempo = -1
    
    for note in notes_with_steps:
        start_step = note['start_step']
        bar = start_step // steps_per_bar
        position = start_step % steps_per_bar
        
        # 1. Bar event
        if bar > last_bar:
            if last_bar == -1:
                remi_events.append('Bar')
            else:
                for _ in range(bar - last_bar):
                    remi_events.append('Bar')
            last_bar = bar
            last_pos = -1
            
        # 2. Position event
        if position != last_pos:
            remi_events.append(f'Position_{position}')
            last_pos = position
            
        # 3. Tempo event
        tempo = get_tempo_at_time(note['start_time'])
        quantized_tempo = int(round(tempo / 5.0) * 5)
        quantized_tempo = max(30, min(250, quantized_tempo))
        if quantized_tempo != last_tempo:
            remi_events.append(f'Tempo_{quantized_tempo}')
            last_tempo = quantized_tempo
            
        # 4. Instrument event
        if note['program'] != last_program:
            remi_events.append(f'Instrument_{note["program"]}')
            last_program = note['program']
            
        # 5. Note event: Velocity -> Duration -> Pitch
        vel_quant = int(round(note['velocity'] / 4.0) * 4)
        vel_quant = max(4, min(124, vel_quant))
        
        dur_quant = min(64, note['duration_steps'])
        
        remi_events.append(f'Velocity_{vel_quant}')
        remi_events.append(f'Duration_{dur_quant}')
        remi_events.append(f'Pitch_{note["pitch"]}')
        
    return remi_events


def build_vocabulary(all_notes: List[str]) -> Tuple[List[str], Dict, Dict]:
    """
    Build token vocabulary and integer mappings.
    Includes PAD, START, and END special tokens.
    """
    unique_tokens = sorted(set(all_notes))
    
    # 0 -> PAD, 1 -> START, 2 -> END
    vocab = ['PAD', 'START', 'END'] + unique_tokens
    
    note2int = {token: idx for idx, token in enumerate(vocab)}
    int2note = {idx: token for token, idx in note2int.items()}
    logger.info(f'Vocabulary size: {len(vocab)} unique tokens (including special tokens)')
    return vocab, note2int, int2note


def create_sequences(
    notes: List[str],
    note2int: Dict,
    seq_length: int = 100
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Slide a window of length seq_length + 1 to create input-target sequences.
    X[i] = [T_0, T_1, ..., T_N-1]
    y[i] = [T_1, T_2, ..., T_N]
    """
    network_input = []
    network_output = []

    # Slide window (using a step of 4 to keep sequence count reasonable but diverse)
    for i in range(0, len(notes) - seq_length - 1, 4):
        window = notes[i : i + seq_length + 1]
        network_input.append([note2int[n] for n in window[:-1]])
        network_output.append([note2int[n] for n in window[1:]])

    X = np.array(network_input, dtype=np.int32)
    y = np.array(network_output, dtype=np.int32)
    
    logger.info(f'Created {len(X)} training sequences')
    return X, y


def preprocess_dataset(dataset_dir: str, config: dict) -> None:
    """
    Run the full REMI preprocessing pipeline.
    """
    seq_length = config['model']['sequence_length']

    # Step 1: Discover MIDI files
    midi_files = glob.glob(os.path.join(dataset_dir, '**/*.mid'), recursive=True)
    midi_files += glob.glob(os.path.join(dataset_dir, '**/*.midi'), recursive=True)
    logger.info(f'Found {len(midi_files)} MIDI files in {dataset_dir}')

    if not midi_files:
        raise FileNotFoundError(f'No MIDI files found in {dataset_dir}')

    # Step 2: Extract notes from every file
    all_notes: List[str] = []
    for midi_path in midi_files:
        logger.info(f'Parsing: {midi_path}')
        events = extract_remi_events(midi_path)
        all_notes.extend(events)

    logger.info(f'Total REMI events extracted: {len(all_notes)}')

    # Step 3: Build vocabulary
    vocab, note2int, int2note = build_vocabulary(all_notes)

    # Step 4: Create training sequences
    X, y = create_sequences(all_notes, note2int, seq_length)

    # Step 5: Save artefacts
    os.makedirs('models', exist_ok=True)
    with open('models/note2int.pkl', 'wb') as f:
        pickle.dump(note2int, f)
    with open('models/int2note.pkl', 'wb') as f:
        pickle.dump(int2note, f)
    with open('models/all_notes.pkl', 'wb') as f:
        pickle.dump(all_notes, f)

    np.save('models/X_input.npy', X)
    np.save('models/y_output.npy', y)

    logger.info('Preprocessing complete. REMI artefacts saved to models/')
    logger.info(f'X shape: {X.shape}  |  y shape: {y.shape}')
    logger.info(f'Vocabulary size: {len(vocab)}')


if __name__ == '__main__':
    config = load_config()
    preprocess_dataset(
        dataset_dir=config['dataset']['path'],
        config=config
    )
