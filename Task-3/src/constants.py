#!/usr/bin/env python3
"""
src/constants.py
Centralized constants and data structures for the Harmonix Music Generation AI.
Includes General MIDI instruments, emotion presets, key signatures, and quick presets.
"""

from typing import Dict, List, Tuple, Any


# ── General MIDI (GM) Instruments Mapping ──────────────────────────────────
GM_INSTRUMENTS: Dict[str, Dict[int, str]] = {
    "Piano": {
        1: "Acoustic Grand Piano",
        2: "Bright Acoustic Piano",
        3: "Electric Grand Piano",
        4: "Honky-tonk Piano",
        5: "Electric Piano 1",
        6: "Electric Piano 2",
        7: "Harpsichord",
        8: "Clavinet"
    },
    "Chromatic Percussion": {
        9: "Celesta",
        10: "Glockenspiel",
        11: "Music Box",
        12: "Vibraphone",
        13: "Marimba",
        14: "Xylophone",
        15: "Tubular Bells",
        16: "Dulcimer"
    },
    "Organ": {
        17: "Drawbar Organ",
        18: "Percussive Organ",
        19: "Rock Organ",
        20: "Church Organ",
        21: "Reed Organ",
        22: "Accordion",
        23: "Harmonica",
        24: "Tango Accordion"
    },
    "Guitar": {
        25: "Acoustic Guitar (nylon)",
        26: "Acoustic Guitar (steel)",
        27: "Electric Guitar (jazz)",
        28: "Electric Guitar (clean)",
        29: "Electric Guitar (muted)",
        30: "Overdriven Guitar",
        31: "Distortion Guitar",
        32: "Guitar Harmonics"
    },
    "Bass": {
        33: "Acoustic Bass",
        34: "Electric Bass (finger)",
        35: "Electric Bass (pick)",
        36: "Fretless Bass",
        37: "Slap Bass 1",
        38: "Slap Bass 2",
        39: "Synth Bass 1",
        40: "Synth Bass 2"
    },
    "Strings": {
        41: "Violin",
        42: "Viola",
        43: "Cello",
        44: "Contrabass",
        45: "Tremolo Strings",
        46: "Pizzicato Strings",
        47: "Orchestral Harp",
        48: "Timpani"
    },
    "Ensemble": {
        49: "String Ensemble 1",
        50: "String Ensemble 2",
        51: "Synth Strings 1",
        52: "Synth Strings 2",
        53: "Choir Aahs",
        54: "Voice Oohs",
        55: "Synth Voice",
        56: "Orchestra Hit"
    },
    "Brass": {
        57: "Trumpet",
        58: "Trombone",
        59: "Tuba",
        60: "Muted Trumpet",
        61: "French Horn",
        62: "Brass Section",
        63: "Synth Brass 1",
        64: "Synth Brass 2"
    },
    "Reed": {
        65: "Soprano Sax",
        66: "Alto Sax",
        67: "Tenor Sax",
        68: "Baritone Sax",
        69: "Oboe",
        70: "English Horn",
        71: "Bassoon",
        72: "Clarinet"
    },
    "Pipe": {
        73: "Piccolo",
        74: "Flute",
        75: "Recorder",
        76: "Pan Flute",
        77: "Blown Bottle",
        78: "Shakuhachi",
        79: "Whistle",
        80: "Ocarina"
    },
    "Synth Lead": {
        81: "Lead 1 (square)",
        82: "Lead 2 (sawtooth)",
        83: "Lead 3 (calliope)",
        84: "Lead 4 (chiff)",
        85: "Lead 5 (charang)",
        86: "Lead 6 (voice)",
        87: "Lead 7 (fifths)",
        88: "Lead 8 (bass + lead)"
    },
    "Synth Pad": {
        89: "Pad 1 (new age)",
        90: "Pad 2 (warm)",
        91: "Pad 3 (polysynth)",
        92: "Pad 4 (choir)",
        93: "Pad 5 (bowed)",
        94: "Pad 6 (metallic)",
        95: "Pad 7 (halo)",
        96: "Pad 8 (sweep)"
    },
    "Synth Effects": {
        97: "FX 1 (rain)",
        98: "FX 2 (soundtrack)",
        99: "FX 3 (crystal)",
        100: "FX 4 (atmosphere)",
        101: "FX 5 (brightness)",
        102: "FX 6 (goblins)",
        103: "FX 7 (echoes)",
        104: "FX 8 (sci-fi)"
    },
    "Ethnic": {
        105: "Sitar",
        106: "Banjo",
        107: "Shamisen",
        108: "Koto",
        109: "Kalimba",
        110: "Bag Pipe",
        111: "Fiddle",
        112: "Shanai"
    },
    "Percussive": {
        113: "Tinkle Bell",
        114: "Agogo",
        115: "Steel Drums",
        116: "Woodblock",
        117: "Taiko Drum",
        118: "Melodic Tom",
        119: "Synth Drum",
        120: "Reverse Cymbal"
    },
    "Sound Effects": {
        121: "Guitar Fret Noise",
        122: "Breath Noise",
        123: "Seashore",
        124: "Bird Tweet",
        125: "Telephone Ring",
        126: "Helicopter",
        127: "Applause",
    }
}


# ── Classical Masterpieces for Seeding ─────────────────────────────────────
MASTERPIECES: Dict[str, Dict[str, str]] = {
    "Bach - Prelude in C Major": {
        "midi_path": "dataset/bach_prelude_1.mid"
    },
    "Bach - Invention No. 1": {
        "midi_path": "dataset/bach_invention_1.mid"
    },
    "Beethoven - Moonlight Sonata (Theme)": {
        "midi_path": "dataset/beethoven_piece_1.mid"
    },
    "Chopin - Nocturne Op. 9 No. 2": {
        "midi_path": "dataset/chopin_nocturne_1.mid"
    },
    "Chopin - Waltz in C-sharp Minor": {
        "midi_path": "dataset/chopin_waltz_1.mid"
    },
    "Mozart - Sonata Facile (K. 545)": {
        "midi_path": "dataset/mozart_sonata_1.mid"
    }
}


# ── Emotion-to-Music Presets ───────────────────────────────────────────────
EMOTIONS: Dict[str, Dict[str, Any]] = {
    "Happy": {
        "genre": "Pop, Dance, Funk",
        "bpm": 120,
        "temp": 1.0,
        "key": "G Major (bright, cheerful)",
        "instruments": [1, 8, 28, 37, 63],
        "chord_prog": "I - V - vi - IV (G - D - Em - C)",
        "melody": "Syncopated, bouncy, upbeat melody with short, staccato phrasing.",
        "rhythm": "Steady four-on-the-floor dance groove with active bassline and crisp hi-hat accents.",
        "structure": "Intro (4 bars) -> Verse (8 bars) -> Chorus (8 bars) -> Outro (4 bars)",
        "dynamics": "Bright and consistently energetic, maintaining a strong forte (f) presence.",
        "listener_feeling": "Joyful, lighthearted, and ready to dance.",
        "keywords": ["happy", "joy", "smile", "cheerful", "glad", "delight", "celebrate", "laugh", "fun"]
    },
    "Sad": {
        "genre": "Piano, Classical, Ambient",
        "bpm": 65,
        "temp": 0.6,
        "key": "A Minor (sorrowful, reflective)",
        "instruments": [1, 41, 43, 49, 90],
        "chord_prog": "i - VI - III - VII (Am - F - C - G)",
        "melody": "Sustained, slow, and weeping notes with gentle downward step-wise motion.",
        "rhythm": "Very slow and spacious, minimal percussion, soft downbeat marks.",
        "structure": "Intro (4 bars) -> Theme A (8 bars) -> Theme B (8 bars) -> Outro (4 bars)",
        "dynamics": "Soft and intimate, ranging from pianissimo (pp) to mezzo-piano (mp).",
        "listener_feeling": "Melancholic, reflective, and emotionally moving.",
        "keywords": ["sad", "grief", "cry", "lost", "death", "tear", "pain", "sorry", "hurt", "unhappy", "depressed", "weep"]
    },
    "Romantic": {
        "genre": "R&B, Soft Pop, Jazz",
        "bpm": 80,
        "temp": 0.8,
        "key": "F Major (warm, sweet)",
        "instruments": [5, 26, 33, 65, 90],
        "chord_prog": "I - vi - IV - V (F - Dm - Bb - C)",
        "melody": "Smooth, lyrical, and expressive soprano sax solos weaving around piano chords.",
        "rhythm": "Gentle, swaying swing feel with soft brush snare hits and smooth bass sweeps.",
        "structure": "Intro (4 bars) -> Verse (8 bars) -> Chorus (8 bars) -> Bridge (4 bars) -> Outro (4 bars)",
        "dynamics": "Warm and expressive, swelling dynamically in the chorus.",
        "listener_feeling": "Warmth, tenderness, intimacy, and affection.",
        "keywords": ["love", "romantic", "heart", "date", "sweetheart", "sweet", "passion", "hug", "kiss", "warmth"]
    },
    "Angry": {
        "genre": "Rock, Metal, Industrial",
        "bpm": 140,
        "temp": 1.3,
        "key": "D Minor (heavy, aggressive)",
        "instruments": [31, 30, 35, 82, 48],
        "chord_prog": "i - VI - V (Dm - Bb - Ab power chords)",
        "melody": "Aggressive, fast, repetitive jagged intervals with sudden register jumps.",
        "rhythm": "Driving, frantic syncopated beats, heavy downbeats, and intense timpani rolls.",
        "structure": "Intro (4 bars) -> Verse (8 bars) -> Chorus (8 bars) -> Outro (4 bars)",
        "dynamics": "Loud, high-intensity fortissimo (ff) with explosive changes.",
        "listener_feeling": "Aggressive, energized, tense, and cathartic.",
        "keywords": ["angry", "rage", "mad", "hate", "fight", "furious", "annoyed", "anger", "screaming", "destroy"]
    },
    "Fear": {
        "genre": "Cinematic, Horror, Ambient",
        "bpm": 60,
        "temp": 1.4,
        "key": "C# Minor (unsettling, tense)",
        "instruments": [7, 16, 45, 102, 48],
        "chord_prog": "i - idim - iv (C#m - Ddim - F#m)",
        "melody": "Dissonant, creeping minor seconds and chromatic movements that sound unpredictable.",
        "rhythm": "Irregular, halting rhythms with sudden shocking stabs and silence.",
        "structure": "Tension Build (8 bars) -> Shocker (4 bars) -> Creeping Outro (8 bars)",
        "dynamics": "Whispering pianissimo (pp) punctuated by sudden fortissimo (ff) accents.",
        "listener_feeling": "Tense, anxious, spooked, and on edge.",
        "keywords": ["fear", "scared", "horror", "ghost", "dark", "afraid", "spooky", "terrified", "panic", "dread"]
    },
    "Suspense": {
        "genre": "Orchestral, Thriller",
        "bpm": 90,
        "temp": 0.9,
        "key": "G Minor (mysterious, urgent)",
        "instruments": [46, 45, 44, 61, 48],
        "chord_prog": "i - iv - v - i (Gm - Cm - Dm - Gm in loops)",
        "melody": "Repetitive, short motifs that slowly ascend in pitch, building unresolved tension.",
        "rhythm": "Constant driving pizzicato eighth-notes with syncopated string pulses.",
        "structure": "Intro (4 bars) -> Chase (12 bars) -> Cliffhanger (4 bars)",
        "dynamics": "Crescendo (gradually getting louder) starting from quiet piano (p) to loud forte (f).",
        "listener_feeling": "Anticipation, suspense, and curiosity.",
        "keywords": ["suspense", "thriller", "mystery", "chase", "hide", "stalk", "shadow", "waiting", "tension"]
    },
    "Excited": {
        "genre": "EDM, Pop, Electro",
        "bpm": 130,
        "temp": 1.2,
        "key": "C Major (bright, open)",
        "instruments": [6, 81, 82, 39, 119],
        "chord_prog": "I - IV - V - IV (C - F - G - F)",
        "melody": "Fast-paced, leaping arpeggios and high-energy repeating synth melodies.",
        "rhythm": "Uptempo electronic dance beats with energetic build-ups and drum fills.",
        "structure": "Build-up (8 bars) -> Drop (8 bars) -> Chorus (8 bars) -> Outro (4 bars)",
        "dynamics": "High energy throughout with a massive volume lift during the drop.",
        "listener_feeling": "Euphoric, hyperactive, motivated, and happy.",
        "keywords": ["excited", "thrilled", "party", "celebration", "hype", "yay", "cheer", "dance", "enthusiastic"]
    },
    "Calm": {
        "genre": "Lo-fi, Ambient, Acoustic",
        "bpm": 70,
        "temp": 0.7,
        "key": "C Major (peaceful, simple)",
        "instruments": [25, 74, 90, 33, 12],
        "chord_prog": "IM7 - IVM7 - IM7 - IVM7 (Cmaj7 - Fmaj7)",
        "melody": "Gentle, spaced-out notes with plenty of silence between phrases. Very relaxing.",
        "rhythm": "Slow, soft lo-fi tap drum rhythm or completely beat-less ambient washes.",
        "structure": "A Section (8 bars) -> B Section (8 bars) -> A Section (8 bars) Outro",
        "dynamics": "Consistently quiet, staying in the pianissimo (pp) to piano (p) range.",
        "listener_feeling": "Relaxed, calm, tranquil, and clear-headed.",
        "keywords": ["calm", "relax", "peace", "soft", "quiet", "gentle", "smooth", "soothe", "rest", "sleepy"]
    },
    "Nostalgic": {
        "genre": "Piano, Indie, Lo-fi",
        "bpm": 75,
        "temp": 0.8,
        "key": "E Major (sweet, bittersweet)",
        "instruments": [1, 6, 26, 43, 89],
        "chord_prog": "I - V/vii - vi - IV (E - B/D# - C#m - A)",
        "melody": "Bittersweet, song-like acoustic guitar and piano lines that feel familiar.",
        "rhythm": "Soft, steady, vintage-sounding acoustic rhythms with occasional organic pauses.",
        "structure": "Intro (4 bars) -> A Section (8 bars) -> B Section (8 bars) -> Outro (6 bars)",
        "dynamics": "Gently expressive, maintaining a moderate, comforting volume.",
        "listener_feeling": "Nostalgic, bittersweet, longing, and reflective.",
        "keywords": ["nostalgic", "memory", "old days", "past", "remember", "childhood", "bittersweet", "reminisce", "yesterday"]
    },
    "Lonely": {
        "genre": "Ambient, Classical",
        "bpm": 55,
        "temp": 0.5,
        "key": "D Minor (solitary, cold)",
        "instruments": [1, 41, 74, 92, 98],
        "chord_prog": "i - v - VI - i (Dm - Am - Bb - Dm)",
        "melody": "A single, isolated flute or piano line carrying a quiet melody over empty pads.",
        "rhythm": "No percussion; rhythm is dictated by slow, breathing chords.",
        "structure": "Intro (4 bars) -> Solitary Theme (12 bars) -> Fade Out (4 bars)",
        "dynamics": "Very quiet, dropping down to near silence at the end.",
        "listener_feeling": "Solitary, cold, reflective, and spacious.",
        "keywords": ["lonely", "alone", "isolated", "empty", "deserted", "abandoned", "single", "solitude"]
    },
    "Hopeful": {
        "genre": "Cinematic, Pop",
        "bpm": 95,
        "temp": 0.9,
        "key": "G Major (bright, promising)",
        "instruments": [1, 49, 26, 61, 90],
        "chord_prog": "IV - V - vi - I (C - D - Em - G)",
        "melody": "Rising melodic shape that climbs higher with each phrase, expressing optimism.",
        "rhythm": "Warm, building acoustic rhythm that expands and grows in confidence.",
        "structure": "Intro (4 bars) -> Verse (8 bars) -> Build-up (4 bars) -> Chorus (8 bars) -> Outro (4 bars)",
        "dynamics": "Crescendo from piano (p) to a rich, warm forte (f).",
        "listener_feeling": "Optimistic, inspired, comforted, and forward-looking.",
        "keywords": ["hopeful", "future", "optimistic", "light", "faith", "hope", "bright", "looking forward", "dreaming"]
    },
    "Motivated": {
        "genre": "Rock, EDM, Epic",
        "bpm": 120,
        "temp": 1.1,
        "key": "A Minor (resolute, driving)",
        "instruments": [30, 63, 34, 81, 48],
        "chord_prog": "i - VII - VI - VII (Am - G - F - G in a loop)",
        "melody": "Punchy, rhythmic, repetitive patterns designed to drive forward movement.",
        "rhythm": "Strong driving groove, walking bassline, and punchy drum beats.",
        "structure": "Intro (4 bars) -> Drive (8 bars) -> Power Section (8 bars) -> Outro (4 bars)",
        "dynamics": "Energetic, driving, and consistently loud (f to ff).",
        "listener_feeling": "Determined, focused, strong, and ready for action.",
        "keywords": ["motivated", "drive", "focus", "work hard", "push", "energy", "determined", "ambition", "power", "grind"]
    },
    "Triumphant": {
        "genre": "Orchestral, Epic",
        "bpm": 135,
        "temp": 1.1,
        "key": "D Major (glorious, majestic)",
        "instruments": [57, 61, 62, 49, 48],
        "chord_prog": "I - V - vi - IV (D - A - Bm - G) or I - IV - V - I",
        "melody": "Bold, soaring trumpet fanfares and epic brass lines climbing the major scales.",
        "rhythm": "March-like orchestral beats with powerful accentuating timpani rolls on downbeats.",
        "structure": "Intro (4 bars) -> Verse (8 bars) -> Triumphant Chorus (12 bars) -> Outro (4 bars)",
        "dynamics": "Explosively loud, reaching grand fortissimo (ff) in the climax.",
        "listener_feeling": "Victorious, epic, heroic, and proud.",
        "keywords": ["triumphant", "dream", "success", "achieve", "win", "victory", "won", "hard work", "proud", "glory"]
    },
    "Mysterious": {
        "genre": "Ambient, Electronic",
        "bpm": 72,
        "temp": 1.2,
        "key": "E Minor (enigmatic, dark)",
        "instruments": [9, 69, 95, 99, 36],
        "chord_prog": "i - v7 - iv6 - i (Em - Am7 - Bm6 - Em)",
        "melody": "Enigmatic, winding woodwind (oboe) melodies over shimmering, magical keys.",
        "rhythm": "Sparse, off-beat percussion clicks and smooth fretless bass glides.",
        "structure": "Intro (4 bars) -> Enigma A (8 bars) -> Enigma B (8 bars) -> Outro (4 bars)",
        "dynamics": "Quiet, shifting dynamically with mysterious whispers and sweeps.",
        "listener_feeling": "Intrigued, curious, and mystified.",
        "keywords": ["mysterious", "secret", "hidden", "strange", "odd", "mystic", "unsolved", "whisper", "shadowy"]
    },
    "Dreamy": {
        "genre": "Ambient, Chillout",
        "bpm": 65,
        "temp": 0.9,
        "key": "A Major (airy, floating)",
        "instruments": [5, 12, 90, 101, 25],
        "chord_prog": "I - IVM7 - I - IVM7 (A - Dmaj7)",
        "melody": "Echoing, shimmering vibraphone notes that drift across the soundstage.",
        "rhythm": "Slow, floating acoustic rhythms that feel weightless and slow.",
        "structure": "Dream Intro (4 bars) -> Float (8 bars) -> Drift (8 bars) -> Wake up (4 bars)",
        "dynamics": "Gently undulating, soft, and cloud-like (pp to p).",
        "listener_feeling": "Floating, peaceful, sleepy, and imaginative.",
        "keywords": ["dreamy", "sleep", "cloud", "wonder", "float", "drift", "sleepy", "dream", "starry", "night"]
    },
    "Spiritual": {
        "genre": "Choir, Classical, World",
        "bpm": 68,
        "temp": 0.7,
        "key": "F Major (sacred, serene)",
        "instruments": [53, 54, 20, 51, 74],
        "chord_prog": "I - IV - I - V (F - Bb - F - C)",
        "melody": "Long, flowing choir melodies and peaceful organ chorales.",
        "rhythm": "Breath-like, free tempo without strict drum beats.",
        "structure": "Intro (4 bars) -> Hymn (12 bars) -> Outro (4 bars)",
        "dynamics": "Sustained, warm, and resonant, swelling like a breath.",
        "listener_feeling": "Peaceful, spiritual, humble, and connected.",
        "keywords": ["spiritual", "god", "soul", "sacred", "holy", "church", "peace", "zen", "temple", "divine"]
    },
    "Playful": {
        "genre": "Jazz, Funk, Pop",
        "bpm": 112,
        "temp": 1.1,
        "key": "F# Major (quirky, lively)",
        "instruments": [2, 46, 72, 13, 33],
        "chord_prog": "I - ii7 - V7 - I (F# - G#m7 - C#7 - F#)",
        "melody": "Quirky, hopping clarinet jumps and marimba rolls with high syncopation.",
        "rhythm": "Bouncy, swing-like, staccato rhythm with pizzicato double bass walks.",
        "structure": "Playful Intro (4 bars) -> Theme (8 bars) -> Dialogue (8 bars) -> Outro (4 bars)",
        "dynamics": "Light and bouncy, jumping quickly between quiet and moderately loud.",
        "listener_feeling": "Amused, happy, lighthearted, and playful.",
        "keywords": ["playful", "fun", "kid", "game", "laugh", "happy", "silly", "joke", "bounce"]
    },
    "Emotional": {
        "genre": "Piano, Cinematic",
        "bpm": 78,
        "temp": 0.8,
        "key": "C Minor (intense, dramatic)",
        "instruments": [1, 41, 43, 50, 90],
        "chord_prog": "i - v - VI - iv (Cm - Gm - Ab - Fm)",
        "melody": "Deeply expressive piano lines coupled with sobbing violin phrases.",
        "rhythm": "Slow, swelling orchestration that builds to a dramatic peak.",
        "structure": "Intro (4 bars) -> Build-up (8 bars) -> Climax (8 bars) -> Outro (4 bars)",
        "dynamics": "Extremely wide dynamic range, moving from quiet piano (p) to a heavy, sweeping forte (f).",
        "listener_feeling": "Heartbroken, deeply moved, empathetic, and inspired.",
        "keywords": ["emotional", "touching", "heartfelt", "deep", "sadness", "crying", "moving", "tearful", "feelings"]
    },
    "Energetic": {
        "genre": "EDM, Rock",
        "bpm": 145,
        "temp": 1.3,
        "key": "A Minor (frantic, rapid)",
        "instruments": [31, 82, 40, 57, 119],
        "chord_prog": "i - iv - VII - III (Am - Dm - G - C)",
        "melody": "Fast, driving riffs and punchy synthesizer arpeggios.",
        "rhythm": "Fast-paced driving drums with frequent crashes and energy builders.",
        "structure": "Intro (4 bars) -> Verse (8 bars) -> Chorus (8 bars) -> Drop (8 bars) -> Outro (4 bars)",
        "dynamics": "High intensity, consistently loud (ff) and driving.",
        "listener_feeling": "Pumped, excited, energetic, and active.",
        "keywords": ["energetic", "fast", "run", "jump", "power", "electro", "energy", "active", "workout", "speed"]
    },
    "Peaceful": {
        "genre": "Ambient, New Age",
        "bpm": 50,
        "temp": 0.6,
        "key": "C Major (still, calm)",
        "instruments": [25, 74, 89, 51, 97],
        "chord_prog": "I - IV - I - IV (C - F - C - F)",
        "melody": "Extremely slow, sustained wind instrument notes floating over a soft guitar base.",
        "rhythm": "No percussion; rhythmic flow relies entirely on the pad swells and rain soundscapes.",
        "structure": "Stillness A (8 bars) -> Stillness B (8 bars) -> Stillness A (8 bars)",
        "dynamics": "Very quiet and calming, maintaining a steady pianissimo (pp).",
        "listener_feeling": "Zen, serene, peaceful, and grounded.",
        "keywords": ["peaceful", "zen", "nature", "forest", "ocean", "wind", "still", "serene", "calmness", "tranquility"]
    }
}


# ── Key Signatures ─────────────────────────────────────────────────────────
KEY_SIGNATURES: Dict[str, Dict[str, str]] = {
    "C Major": {"mood": "Pure, simple, innocent", "relative": "A Minor"},
    "G Major": {"mood": "Bright, cheerful, pastoral", "relative": "E Minor"},
    "D Major": {"mood": "Triumphant, majestic, glorious", "relative": "B Minor"},
    "A Major": {"mood": "Warm, joyful, confident", "relative": "F# Minor"},
    "E Major": {"mood": "Brilliant, luminous, sweet", "relative": "C# Minor"},
    "B Major": {"mood": "Hard, powerful, energetic", "relative": "G# Minor"},
    "F Major": {"mood": "Pastoral, warm, sacred", "relative": "D Minor"},
    "Bb Major": {"mood": "Bold, noble, majestic", "relative": "G Minor"},
    "Eb Major": {"mood": "Heroic, bold, grand", "relative": "C Minor"},
    "Ab Major": {"mood": "Soft, gentle, dreamy", "relative": "F Minor"},
    "A Minor": {"mood": "Melancholic, sorrowful, tender", "relative": "C Major"},
    "E Minor": {"mood": "Dark, brooding, enigmatic", "relative": "G Major"},
    "D Minor": {"mood": "Serious, somber, heavy", "relative": "F Major"},
    "G Minor": {"mood": "Mysterious, urgent, dramatic", "relative": "Bb Major"},
    "C Minor": {"mood": "Dark, intense, dramatic", "relative": "Eb Major"},
    "F Minor": {"mood": "Deep, passionate, melancholic", "relative": "Ab Major"},
    "B Minor": {"mood": "Solitary, patient, contemplative", "relative": "D Major"},
    "F# Minor": {"mood": "Gloomy, mysterious, passionate", "relative": "A Major"},
    "C# Minor": {"mood": "Tense, unsettling, poignant", "relative": "E Major"},
    "G# Minor": {"mood": "Dusky, shadowy, grave", "relative": "B Major"},
    "F# Major": {"mood": "Quirky, bright, lively", "relative": "D# Minor"},
}


# ── Quick Presets ──────────────────────────────────────────────────────────
QUICK_PRESETS: Dict[str, Dict[str, Any]] = {
    "🎹 Solo Piano": {
        "instruments": [1, 2, 3, 5, 7],
        "bpm": 90,
        "temp": 0.8,
        "description": "Intimate grand piano with subtle variations"
    },
    "🎸 Rock Band": {
        "instruments": [30, 31, 35, 57, 119],
        "bpm": 130,
        "temp": 1.1,
        "description": "Guitars, bass, brass, and driving drums"
    },
    "🎷 Jazz Combo": {
        "instruments": [5, 67, 33, 72, 46],
        "bpm": 100,
        "temp": 1.0,
        "description": "Electric piano, sax, bass, clarinet, pizzicato"
    },
    "🎻 Full Orchestra": {
        "instruments": [49, 61, 57, 43, 48],
        "bpm": 110,
        "temp": 0.9,
        "description": "Strings, brass, cello, and timpani ensemble"
    },
    "🔊 Electronic": {
        "instruments": [81, 82, 39, 96, 119],
        "bpm": 128,
        "temp": 1.2,
        "description": "Synth leads, bass, pads, and electronic drums"
    },
    "🌿 Ambient": {
        "instruments": [89, 90, 74, 97, 25],
        "bpm": 60,
        "temp": 0.6,
        "description": "New age pads, flute, rain FX, nylon guitar"
    },
    "🎬 Cinematic": {
        "instruments": [49, 48, 61, 53, 98],
        "bpm": 95,
        "temp": 0.9,
        "description": "Strings, timpani, horns, choir, soundtrack FX"
    },
}


# ── Helper Functions ───────────────────────────────────────────────────────

def get_category_and_sound_from_program(program_id: int) -> Tuple[str, str]:
    """Finds the GM_INSTRUMENTS category and sound name for a given 1-based program_id."""
    for category, instruments in GM_INSTRUMENTS.items():
        if program_id in instruments:
            return category, instruments[program_id]
    return "Piano", "Acoustic Grand Piano"


def analyze_emotion_from_text(text: str) -> str:
    """Analyze the text and return the best matching emotion from EMOTIONS database."""
    text_lower = text.lower()
    scores = {}
    for emotion, data in EMOTIONS.items():
        score = 0
        for kw in data["keywords"]:
            if kw in text_lower:
                score += 1
        scores[emotion] = score

    max_emotion = max(scores, key=scores.get)
    if scores[max_emotion] > 0:
        return max_emotion

    # Fallback to general keyword match or sentiment
    sad_kws = ["sad", "blue", "cry", "hurt", "pain", "dark", "heavy", "grief", "lonely", "alone", "isolated"]
    happy_kws = ["happy", "good", "great", "awesome", "joy", "fun", "excited", "hype", "win", "victory"]

    sad_score = sum(1 for kw in sad_kws if kw in text_lower)
    happy_score = sum(1 for kw in happy_kws if kw in text_lower)

    if sad_score > happy_score:
        return "Sad"
    elif happy_score > sad_score:
        return "Happy"

    return "Hopeful"  # General neutral positive fallback


def blend_emotions(emotion_a: str, emotion_b: str, ratio: float) -> Dict[str, Any]:
    """
    Blend two emotion presets together based on a ratio (0.0 = pure A, 1.0 = pure B).
    Interpolates numeric values and selects instruments from both.
    """
    preset_a = EMOTIONS[emotion_a]
    preset_b = EMOTIONS[emotion_b]

    # Interpolate numeric values
    blended_bpm = int(round(preset_a["bpm"] * (1 - ratio) + preset_b["bpm"] * ratio))
    blended_temp = round(preset_a["temp"] * (1 - ratio) + preset_b["temp"] * ratio, 2)

    # Blend instruments: take from A and B based on ratio
    insts_a = preset_a["instruments"]
    insts_b = preset_b["instruments"]
    blended_instruments = []
    for i in range(5):
        if i / 5.0 < (1 - ratio):
            blended_instruments.append(insts_a[i])
        else:
            blended_instruments.append(insts_b[i])

    # Select key from the dominant emotion
    blended_key = preset_a["key"] if ratio < 0.5 else preset_b["key"]

    # Merge keywords
    ratio_a_kws = int(len(preset_a["keywords"]) * (1 - ratio))
    ratio_b_kws = int(len(preset_b["keywords"]) * ratio)
    blended_keywords = preset_a["keywords"][:max(1, ratio_a_kws)] + preset_b["keywords"][:max(1, ratio_b_kws)]

    # Select text fields from dominant emotion, noting the blend
    dominant = preset_a if ratio < 0.5 else preset_b
    secondary = preset_b if ratio < 0.5 else preset_a

    return {
        "genre": f"{dominant['genre']} + {secondary['genre']}",
        "bpm": blended_bpm,
        "temp": blended_temp,
        "key": blended_key,
        "instruments": blended_instruments,
        "chord_prog": dominant["chord_prog"],
        "melody": f"Blend of: {dominant['melody'][:60]}... & {secondary['melody'][:60]}...",
        "rhythm": dominant["rhythm"],
        "structure": dominant["structure"],
        "dynamics": f"Transitioning between {preset_a['dynamics'][:40]}... and {preset_b['dynamics'][:40]}...",
        "listener_feeling": f"{preset_a['listener_feeling']} blending into {preset_b['listener_feeling']}",
        "keywords": blended_keywords,
        "blend_info": {
            "emotion_a": emotion_a,
            "emotion_b": emotion_b,
            "ratio": ratio,
        }
    }
