#!/usr/bin/env python3
"""
src/generate.py
Music generation script using a trained Music Transformer model.
Implements temperature-based causal sampling and REMI token generation.
"""

import os
import pickle
import logging
import random
import numpy as np
from typing import List, Optional

import tensorflow as tf
from model import load_model

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')


def load_config() -> dict:
    import yaml
    with open('config.yaml') as f:
        return yaml.safe_load(f)


def load_generation_artefacts() -> tuple:
    """Load vocabulary mappings and training notes."""
    with open('models/note2int.pkl', 'rb') as f:
        note2int = pickle.load(f)
    with open('models/int2note.pkl', 'rb') as f:
        int2note = pickle.load(f)
    with open('models/all_notes.pkl', 'rb') as f:
        all_notes = pickle.load(f)
    return note2int, int2note, all_notes


@tf.function
def generate_loop_tf(model_obj, initial_seq, n_notes_const, temp_const):
    """
    Causal autoregressive generation loop for a single sequence.
    """
    seq_length = initial_seq.shape[0]
    curr_seq = tf.identity(initial_seq)
    generated_indices = tf.TensorArray(dtype=tf.int32, size=n_notes_const)

    for step in tf.range(n_notes_const):
        # Shape: (1, seq_length)
        model_input = tf.reshape(curr_seq, (1, seq_length))
        
        # Forward pass: get prediction for the last position only
        probs = model_obj(model_input, training=False)[0, -1, :]

        # Scale by temperature in log space
        log_probs = tf.math.log(tf.clip_by_value(probs, 1e-10, 1.0))
        log_probs = tf.expand_dims(log_probs, 0) # shape: (1, vocab_size)

        sampled_idx = tf.random.categorical(log_probs / temp_const, num_samples=1, dtype=tf.int32)[0, 0]

        generated_indices = generated_indices.write(step, sampled_idx)
        
        # Slide window
        curr_seq = tf.concat([curr_seq[1:], [sampled_idx]], axis=0)

    return generated_indices.stack()


@tf.function
def generate_loop_batch_tf(model_obj, initial_seqs, n_notes_const, temperatures):
    """
    Causal autoregressive generation loop for multiple sequences in a batch.
    """
    batch_size = tf.shape(initial_seqs)[0]
    seq_length = tf.shape(initial_seqs)[1]
    
    curr_seqs = tf.identity(initial_seqs)
    generated_indices = tf.TensorArray(dtype=tf.int32, size=n_notes_const)
    
    for step in tf.range(n_notes_const):
        model_input = tf.reshape(curr_seqs, (batch_size, seq_length))
        
        # Forward pass: get last position prediction for all elements in the batch
        probs = model_obj(model_input, training=False)[:, -1, :]
        
        log_probs = tf.math.log(tf.clip_by_value(probs, 1e-10, 1.0))
        scaled_log_probs = log_probs / temperatures
        
        sampled_idx = tf.random.categorical(scaled_log_probs, num_samples=1, dtype=tf.int32)
        
        generated_indices = generated_indices.write(step, sampled_idx[:, 0])
        
        # Slide window across the second dimension
        curr_seqs = tf.concat([curr_seqs[:, 1:], sampled_idx], axis=1)
        
    return generated_indices.stack()


def generate_notes(
    model,
    all_notes: List[str],
    note2int: dict,
    int2note: dict,
    n_notes: int = 200,
    temperature: float = 1.0,
    seed_notes: Optional[List[str]] = None
) -> List[str]:
    """
    Autoregressively generate a sequence of REMI tokens using the Music Transformer.
    """
    vocab_size = len(note2int)
    seq_length = model.input_shape[1]

    # Choose seed sequence
    if seed_notes is None:
        start_idx = random.randint(0, len(all_notes) - seq_length - 1)
        seed_notes = all_notes[start_idx: start_idx + seq_length]
        logger.info(f'Random seed starting at index {start_idx}')
    else:
        if len(seed_notes) < seq_length:
            # Pad with START or default tokens if seed is too short
            padding = ['START'] * (seq_length - len(seed_notes))
            seed_notes = padding + seed_notes
        seed_notes = seed_notes[-seq_length:]

    current_seq = [note2int.get(n, 1) for n in seed_notes] # default to START (1)

    logger.info(f'Generating {n_notes} REMI events...')

    initial_seq_tf = tf.convert_to_tensor(current_seq, dtype=tf.int32)
    n_notes_tf = tf.constant(n_notes, dtype=tf.int32)
    temperature_tf = tf.constant(temperature, dtype=tf.float32)

    generated_indices = generate_loop_tf(model, initial_seq_tf, n_notes_tf, temperature_tf)
    generated_indices_np = generated_indices.numpy()

    generated_tokens = [int2note[idx] for idx in generated_indices_np]

    logger.info(f'Generation complete: {len(generated_tokens)} tokens')
    return generated_tokens


def generate_notes_batch(
    model,
    all_notes: List[str],
    note2int: dict,
    int2note: dict,
    n_notes: int = 200,
    temperatures: List[float] = [1.0, 1.0, 1.0, 1.0, 1.0],
    seed_notes_list: Optional[List[List[str]]] = None
) -> List[List[str]]:
    """
    Generate multiple sequences of REMI events in a single batch.
    """
    vocab_size = len(note2int)
    seq_length = model.input_shape[1]
    batch_size = len(temperatures)

    current_seqs = []
    for i in range(batch_size):
        if seed_notes_list is not None and i < len(seed_notes_list):
            seed_notes = seed_notes_list[i]
        else:
            start_idx = random.randint(0, len(all_notes) - seq_length - 1)
            seed_notes = all_notes[start_idx: start_idx + seq_length]
            logger.info(f'Random seed for track {i} starting at index {start_idx}')
        
        if len(seed_notes) < seq_length:
            padding = ['START'] * (seq_length - len(seed_notes))
            seed_notes = padding + seed_notes
        seed_notes = seed_notes[-seq_length:]
        current_seqs.append([note2int.get(n, 1) for n in seed_notes])

    logger.info(f'Generating {n_notes} steps for {batch_size} sequences in parallel...')

    initial_seqs_tf = tf.convert_to_tensor(current_seqs, dtype=tf.int32)
    n_notes_tf = tf.constant(n_notes, dtype=tf.int32)
    
    temperatures_tf = tf.convert_to_tensor(temperatures, dtype=tf.float32)
    temperatures_tf = tf.expand_dims(temperatures_tf, -1)

    generated_indices = generate_loop_batch_tf(
        model, initial_seqs_tf, n_notes_tf, temperatures_tf
    )
    generated_indices_np = generated_indices.numpy()

    tracks_tokens = []
    for track_idx in range(batch_size):
        track_indices = generated_indices_np[:, track_idx]
        tokens = [int2note[idx] for idx in track_indices]
        tracks_tokens.append(tokens)

    logger.info('Batched generation complete!')
    return tracks_tokens


if __name__ == '__main__':
    config = load_config()

    note2int, int2note, all_notes = load_generation_artefacts()
    vocab_size = len(note2int)
    seq_length = config['model']['sequence_length']

    model = load_model(
        weights_path='models/checkpoints/best_weights.weights.h5',
        seq_length=seq_length,
        vocab_size=vocab_size
    )

    generated = generate_notes(
        model=model,
        all_notes=all_notes,
        note2int=note2int,
        int2note=int2note,
        n_notes=config['generation']['n_notes'],
        temperature=config['generation']['temperature']
    )

    logger.info(f'First 10 generated tokens: {generated[:10]}')

    # Save the generated REMI tokens to a MIDI file
    from utils import remi_events_to_midi
    output_file = config['generation'].get('output_path', 'outputs/output.mid')
    remi_events_to_midi(
        events=generated,
        output_path=output_file,
        default_bpm=config['generation']['bpm']
    )
    logger.info(f'Generated song saved to: {output_file}')

