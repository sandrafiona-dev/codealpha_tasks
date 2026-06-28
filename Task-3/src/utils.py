#!/usr/bin/env python3
"""
src/utils.py
Utility functions: convert generated token sequences to MIDI files
and optionally to WAV/MP3 using FluidSynth or pydub.
"""

import os
import logging
from typing import List, Tuple

# pyrefly: ignore [missing-import]
from music21 import stream, note, chord, instrument, tempo

logger = logging.getLogger(__name__)


def tokens_to_midi(
    tokens: List[str],
    output_path: str = 'outputs/output.mid',
    bpm: int = 120,
    note_duration: float = 0.5,
    instrument_program: int = 1
) -> str:
    """
    Convert a list of note/chord token strings into a MIDI file.

    The token format matches what preprocess.py produces:
      - Single note  : 'C4', 'G#3', 'Bb5'
      - Chord        : '0.4.7' (MIDI normal order integers)

    Args:
        tokens            : List of generated token strings.
        output_path       : Destination .mid file path.
        bpm               : Beats per minute for the generated piece.
        note_duration     : Duration of each note in quarter notes (0.5 = eighth note).
        instrument_program: General MIDI program number (1-128).

    Returns:
        Absolute path to the saved MIDI file.
    """
    # Create instrument with custom MIDI program change (1-128 converted to 0-127)
    inst = instrument.Instrument()
    inst.midiProgram = instrument_program - 1

    output_notes = []
    offset = 0.0  # Current position in the stream (quarter notes)

    for token in tokens:
        try:
            if '.' in token or token.isdigit():
                # ── Chord token (e.g. '0.4.7') ────────────────────────────
                # Normal order integers → list of Note objects → Chord
                pitches = [int(p) for p in token.split('.')]
                chord_notes = [note.Note(p) for p in pitches]
                new_chord = chord.Chord(chord_notes)
                new_chord.offset = offset
                new_chord.quarterLength = note_duration
                output_notes.append(new_chord)

            else:
                # ── Single note token (e.g. 'C4') ─────────────────────────
                new_note = note.Note(token)
                new_note.offset = offset
                new_note.quarterLength = note_duration
                new_note.storedInstrument = inst
                output_notes.append(new_note)

        except Exception as e:
            # Skip malformed tokens gracefully
            logger.debug(f'Skipping token "{token}": {e}')
            continue

        offset += note_duration  # Advance timeline

    # Build music21 stream
    midi_stream = stream.Stream(output_notes)

    # Set tempo and instrument
    midi_stream.insert(0, tempo.MetronomeMark(number=bpm))
    midi_stream.insert(0, inst)

    # Write MIDI file
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    midi_stream.write('midi', fp=output_path)
    logger.info(f'MIDI saved: {output_path}')
    return os.path.abspath(output_path)


def shift_octave(token: str, shift_by: int) -> str:
    """
    Shift the octave of a note string.
    Example: shift_octave('C4', -2) -> 'C2'
    """
    import re
    # Match standard note strings like 'C4', 'F#5', 'B-3', 'A4'
    match = re.match(r"^([A-G]#?b?-?)(\d+)$", token)
    if match:
        pitch_name = match.group(1)
        octave = int(match.group(2))
        new_octave = max(0, min(9, octave + shift_by))
        return f"{pitch_name}{new_octave}"
    return token


def create_multitrack_midi(
    tracks: List[Tuple[List[str], int]],
    output_path: str = 'outputs/output.mid',
    bpm: int = 120,
    note_duration: float = 0.5
) -> str:
    """
    Convert multiple token sequences (each with a different instrument) into a single multitrack MIDI score.

    Args:
        tracks       : List of tuples (tokens_list, general_midi_program_number).
        output_path  : Destination .mid file path.
        bpm          : Beats per minute.
        note_duration: Duration of each note.

    Returns:
        Absolute path to the saved MIDI file.
    """
    score = stream.Score()

    for idx, (tokens, program) in enumerate(tracks):
        part = stream.Part()
        inst = instrument.Instrument()
        inst.midiProgram = program - 1
        part.insert(0, inst)

        offset = 0.0
        for token in tokens:
            try:
                # Apply octave shift for the bass track (index 2) and arpeggio track (index 3)
                if idx == 2:    # Bass track
                    token = shift_octave(token, -2)
                elif idx == 3:  # Arpeggio/high track
                    token = shift_octave(token, 1)

                if '.' in token or token.isdigit():
                    # Chord token
                    pitches = [int(p) for p in token.split('.')]
                    
                    # For chords in bass track, transpose pitches down by 24 semitones
                    if idx == 2:
                        pitches = [max(0, p - 24) for p in pitches]
                    elif idx == 3:
                        pitches = [min(127, p + 12) for p in pitches]
                        
                    chord_notes = [note.Note(p) for p in pitches]
                    new_chord = chord.Chord(chord_notes)
                    new_chord.offset = offset
                    new_chord.quarterLength = note_duration
                    part.append(new_chord)
                else:
                    # Single note token
                    new_note = note.Note(token)
                    new_note.offset = offset
                    new_note.quarterLength = note_duration
                    new_note.storedInstrument = inst
                    part.append(new_note)

            except Exception:
                continue

            offset += note_duration

        score.insert(0, part)

    # Insert tempo mark at offset 0
    score.insert(0, tempo.MetronomeMark(number=bpm))

    # Write multi-track score
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    score.write('midi', fp=output_path)
    logger.info(f'Multitrack MIDI saved: {output_path}')
    return os.path.abspath(output_path)


def midi_to_wav(midi_path: str, wav_path: str, soundfont: str = '/usr/share/sounds/sf2/FluidR3_GM.sf2') -> str:
    """
    Convert MIDI to WAV using FluidSynth.

    Prerequisites:
        sudo apt-get install fluidsynth
        pip install pyfluidsynth

    Args:
        midi_path  : Input .mid file.
        wav_path   : Output .wav file.
        soundfont  : Path to a .sf2 soundfont file.

    Returns:
        Path to the generated WAV file.
    """
    try:
        # pyrefly: ignore [missing-import]
        import fluidsynth
        fs = fluidsynth.Synth()
        fs.start(driver='file', filename=wav_path)
        sfid = fs.sfload(soundfont)
        fs.program_select(0, sfid, 0, 0)

        # Play MIDI via FluidSynth (simplified — use midi2audio for robustness)
        os.system(f'fluidsynth -ni {soundfont} {midi_path} -F {wav_path} -r 44100')
        logger.info(f'WAV saved: {wav_path}')
        return wav_path
    except ImportError:
        # Fallback: use midi2audio library
        try:
            # pyrefly: ignore [missing-import]
            from midi2audio import FluidSynth
            FluidSynth(soundfont).midi_to_audio(midi_path, wav_path)
            logger.info(f'WAV saved via midi2audio: {wav_path}')
            return wav_path
        except ImportError:
            logger.error('Install midi2audio: pip install midi2audio')
            raise


def wav_to_mp3(wav_path: str, mp3_path: str, bitrate: str = '192k') -> str:
    """
    Convert WAV to MP3 using pydub (requires ffmpeg).

    Prerequisites:
        pip install pydub
        sudo apt-get install ffmpeg

    Args:
        wav_path : Input .wav file.
        mp3_path : Output .mp3 file.
        bitrate  : MP3 encoding bitrate.

    Returns:
        Path to the generated MP3 file.
    """
    try:
        # pyrefly: ignore [missing-import]
        from pydub import AudioSegment
        audio = AudioSegment.from_wav(wav_path)
        audio.export(mp3_path, format='mp3', bitrate=bitrate)
        logger.info(f'MP3 saved: {mp3_path}')
        return mp3_path
    except ImportError:
        logger.error('Install pydub: pip install pydub')
        raise


def remi_events_to_midi(
    events: list,
    output_path: str = 'outputs/output.mid',
    default_bpm: int = 120,
    steps_per_quarter: int = 4,
    program_mapping: list = None
) -> str:
    """
    Convert a list of REMI event tokens back to a standard multitrack MIDI file.
    Optionally orchestrates the output into a 5-instrument ensemble based on pitch registers.
    """
    # pyrefly: ignore [missing-import]
    import pretty_midi
    import numpy as np

    notes = []
    tempo_changes = {0: default_bpm}
    
    steps_per_bar = 4 * steps_per_quarter
    
    current_bar = 0
    current_pos = 0
    current_program = 1
    current_velocity = 80
    current_duration = 2
    
    for event in events:
        if event == 'Bar':
            current_bar += 1
            current_pos = 0
        elif event.startswith('Position_'):
            current_pos = int(event.split('_')[1])
        elif event.startswith('Tempo_'):
            tempo_val = int(event.split('_')[1])
            step = current_bar * steps_per_bar + current_pos
            tempo_changes[step] = tempo_val
        elif event.startswith('Instrument_'):
            current_program = int(event.split('_')[1])
        elif event.startswith('Velocity_'):
            current_velocity = int(event.split('_')[1])
        elif event.startswith('Duration_'):
            current_duration = int(event.split('_')[1])
        elif event.startswith('Pitch_'):
            pitch = int(event.split('_')[1])
            start_step = current_bar * steps_per_bar + current_pos
            
            # Orchestrate pitch register to 5-instrument ensemble
            if program_mapping is not None and len(program_mapping) >= 5:
                if pitch >= 72:
                    prog = program_mapping[0]      # Section 1: Lead Melody
                elif 60 <= pitch < 72:
                    prog = program_mapping[1]      # Section 2: Harmony/Chords
                elif 48 <= pitch < 60:
                    prog = program_mapping[3]      # Section 4: Arpeggiator
                else:
                    prog = program_mapping[2]      # Section 3: Bassline
                
                # Accented beat percussion: trigger percussion on beat (every 4 steps)
                if start_step % 4 == 0 and (pitch < 60 or start_step % 8 == 0):
                    notes.append({
                        'pitch': max(36, min(76, pitch)),
                        'start_step': start_step,
                        'duration_steps': 1,
                        'velocity': max(40, current_velocity - 20),
                        'program': program_mapping[4]  # Section 5: Percussion/FX
                    })
            else:
                prog = current_program
                
            notes.append({
                'pitch': pitch,
                'start_step': start_step,
                'duration_steps': current_duration,
                'velocity': current_velocity,
                'program': prog
            })
            
    if not notes:
        # Default fallback note
        notes.append({
            'pitch': 60,
            'start_step': 0,
            'duration_steps': 4,
            'velocity': 80,
            'program': 1
        })
        
    # Reconstruct step to time mapping
    max_step = max(n['start_step'] + n['duration_steps'] for n in notes) + 1
    
    step_times = np.zeros(max_step)
    current_time = 0.0
    current_tempo = default_bpm
    
    for step in range(max_step):
        if step in tempo_changes:
            current_tempo = tempo_changes[step]
        step_times[step] = current_time
        
        step_duration = (60.0 / current_tempo) / steps_per_quarter
        current_time += step_duration
        
    pm = pretty_midi.PrettyMIDI()
    
    instruments = {}
    for n in notes:
        prog = n['program']
        if prog not in instruments:
            is_drum = (prog == 129)
            real_prog = 0 if is_drum else (prog - 1)
            inst = pretty_midi.Instrument(program=real_prog, is_drum=is_drum)
            instruments[prog] = inst
            pm.instruments.append(inst)
            
        inst = instruments[prog]
        
        start_time = step_times[n['start_step']]
        end_step = min(max_step - 1, n['start_step'] + n['duration_steps'])
        end_time = step_times[end_step]
        
        note_obj = pretty_midi.Note(
            velocity=n['velocity'],
            pitch=n['pitch'],
            start=start_time,
            end=end_time
        )
        inst.notes.append(note_obj)
        
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    pm.write(output_path)
    return os.path.abspath(output_path)
