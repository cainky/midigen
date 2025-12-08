# MidiGen: Intuitive MIDI Music Generation Library

[![PyPI version](https://badge.fury.io/py/midigen-lib.svg)](https://badge.fury.io/py/midigen-lib)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/cainky/midigen/issues)

MidiGen is a Python library for creating and manipulating MIDI files with an intuitive, music-theory-aware API. Whether you're building generative music systems, prototyping musical ideas, or exploring algorithmic composition, MidiGen provides the tools to translate musical concepts directly into MIDI.

Built on top of `mido` and `music21`, MidiGen abstracts the complexities of the MIDI protocol while giving you full control when you need it. Create everything from simple melodies to multi-track compositions with chord progressions, scales, and complex rhythms.

## Features

-   **High-Level Composition:** Structure your music with `Song` and `Section` objects using familiar concepts like verses and choruses
-   **Music Theory Integration:** Generate chord progressions from Roman numeral notation (e.g., "I-IV-V-I") with automatic voice leading
-   **Comprehensive Scale Support:** 17 scale types including major, minor, pentatonic, blues, and all seven modes (Ionian, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian)
-   **Melody Generation:** Create melodies from scales, note names, or scale degrees with rhythm notation support. Includes random walk algorithm for generative melodies
-   **Extended Chord Types:** 17+ chord types including triads, seventh chords, extended chords (9th, 11th, 13th), and altered dominants
-   **Arpeggio Patterns:** Generate arpeggios with ascending, descending, and alternating patterns
-   **Time Utilities:** Convert between musical time (measures, beats) and MIDI ticks with the `TimeConverter` class
-   **Multi-Track Support:** Layer multiple instruments across separate MIDI tracks
-   **General MIDI Instruments:** Assign instruments by name - no need to memorize program numbers
-   **Drum Programming:** Create rhythm tracks with the `DrumKit` class using standard drum names
-   **Flexible Output:** Configurable save paths with optional `output_dir` parameter

## Installation

Install MidiGen using pip (requires Python 3.10+):

```bash
pip install midigen-lib
```

For development, clone the repository and install with [Poetry](https://python-poetry.org/):

```bash
git clone https://github.com/cainky/midigen.git
cd midigen
poetry install
```

## Getting Started: Create a Song in 5 Lines

The easiest way to get started with MidiGen is by using the `Song` class and `MidiCompiler`. Here's how you can create a simple song with a classic I-V-vi-IV chord progression:

```python
from midigen import Song, Section, Key
from midigen.compiler import MidiCompiler

# 1. Create a Song with a key and tempo
song = Song(key=Key("C", "major"), tempo=120)

# 2. Add a section with a chord progression
song.add_section(Section(name="Verse", length=8, chord_progression="I-V-vi-IV"))

# 3. Add an instrument to play the progression
song.add_instrument("Acoustic Grand Piano")

# 4. Compile and save the MIDI file
compiler = MidiCompiler(song)
compiler.compile().save("my_first_song.mid")

print("Song 'my_first_song.mid' created successfully!")
```

> **Note:** The `Song` class is a pure data container for your musical intent. The `MidiCompiler` handles all MIDI protocol details (channels, tracks, timing). This separation makes songs easier to manipulate and test.

## Advanced Usage

### Creating Melodies

The `Melody` class provides powerful tools for melody generation:

```python
from midigen import Melody, Scale, TimeConverter

# Method 1: Create melody from note names
melody1 = Melody.from_note_names("C4 E4 G4 E4 C4", durations=480)

# Method 2: Create melody from scale degrees with rhythm notation
scale = Scale.major(60)  # C major
melody2 = Melody.from_degrees(
    scale,
    degrees=[1, 3, 5, 8, 5, 3, 1],
    rhythms="quarter quarter quarter half quarter quarter half"
)

# Method 3: Generate random melodies using random walk
melody3 = Melody.random_walk(
    start_pitch=60,
    length=16,
    scale=scale,
    max_interval=3,
    seed=42  # For reproducible results
)

# Transform melodies
transposed = melody1.transpose(5)  # Transpose up 5 semitones
retrograde = melody1.reverse()     # Reverse the melody
```

### Working with Scales and Modes

MidiGen supports 17 different scale types:

```python
from midigen import Scale

# Basic scales
c_major = Scale.major(60)
a_minor = Scale.minor(57)
a_harmonic_minor = Scale.harmonic_minor(57)
a_melodic_minor = Scale.melodic_minor(57)

# Pentatonic scales
c_major_pent = Scale.major_pentatonic(60)
a_minor_pent = Scale.minor_pentatonic(57)

# Blues scale
c_blues = Scale.blues(60)

# All seven modes
c_ionian = Scale.ionian(60)      # Same as major
d_dorian = Scale.dorian(62)
e_phrygian = Scale.phrygian(64)
f_lydian = Scale.lydian(65)
g_mixolydian = Scale.mixolydian(67)
a_aeolian = Scale.aeolian(57)    # Same as natural minor
b_locrian = Scale.locrian(71)

# Other scales
c_whole_tone = Scale.whole_tone(60)
c_chromatic = Scale.chromatic(60)
```

### Multi-Track Compositions

Create layered arrangements with multiple instruments:

```python
from midigen import Song, Section, Key
from midigen.compiler import MidiCompiler

# Create a song with a minor key
song = Song(key=Key("Am", "minor"), tempo=90)

# Define sections
song.add_section(Section(name="Intro", length=4, chord_progression="i-VI-III-VII"))
song.add_section(Section(name="Verse", length=8, chord_progression="i-VI-III-VII-i-VI-iv-V"))

# Add multiple instruments on separate tracks
song.add_instrument("Synth Bass 1")
song.add_instrument("String Ensemble 1")
song.add_instrument("Lead 1 (square)")

# Compile with custom settings per instrument
compiler = MidiCompiler(song)
compiler.compile_instrument("Synth Bass 1", octave=3)
compiler.compile_instrument("String Ensemble 1", octave=4)
compiler.compile_instrument("Lead 1 (square)", octave=5)

# Save with optional output directory
compiler.save("multi_track_song.mid", output_dir="./output")
```

### Creating Drum Patterns

You can add a rhythm section to your song using the `DrumKit` class.

```python
from midigen import MidiGen, DrumKit, Key

# Use the lower-level MidiGen for more control
midi = MidiGen(key=Key("C"))

# Create a drum kit
drum_kit = DrumKit()

# Add drum sounds at specific times (in ticks)
# A simple 4/4 rock beat
for i in range(4):
    beat_start_time = i * 480
    drum_kit.add_drum("Bass Drum 1", time=beat_start_time)
    drum_kit.add_drum("Acoustic Snare", time=beat_start_time + 240)
    drum_kit.add_drum("Closed Hi Hat", time=beat_start_time)
    drum_kit.add_drum("Closed Hi Hat", time=beat_start_time + 120)
    drum_kit.add_drum("Closed Hi Hat", time=beat_start_time + 240)
    drum_kit.add_drum("Closed Hi Hat", time=beat_start_time + 360)


# Add the drum kit to a track
# Note: Drum tracks are typically on channel 9
track = midi.get_active_track()
track.add_drum_kit(drum_kit)

midi.save("drum_beat.mid")
```

### Working with Time Conversions

The `TimeConverter` utility helps convert between musical time and MIDI ticks:

```python
from midigen import TimeConverter

tc = TimeConverter(ticks_per_quarter_note=480)

# Convert musical time to ticks
one_measure = tc.measures_to_ticks(1)  # 1920 ticks in 4/4 time
four_beats = tc.beats_to_ticks(4)      # 1920 ticks
half_note = tc.note_duration("half")   # 960 ticks

# Convert ticks back to musical time
measures = tc.ticks_to_measures(1920)  # 1.0 measure
beats = tc.ticks_to_beats(960)         # 2.0 beats

# Work with different time signatures
waltz_measure = tc.measures_to_ticks(1, time_signature_numerator=3,
                                     time_signature_denominator=4)

# Common note durations
quarter = tc.note_duration("quarter")          # 480
dotted_quarter = tc.note_duration("dotted_quarter")  # 720
triplet_eighth = tc.note_duration("triplet_eighth")  # 160
```

### Creating Arpeggios

Generate arpeggios with different patterns:

```python
from midigen import MidiGen, Note, Arpeggio, ArpeggioPattern, Key, KEY_MAP

midi = MidiGen(tempo=140, key=Key("C"))
track = midi.get_active_track()

# Define chord notes
c_maj7_notes = [
    Note(pitch=KEY_MAP["C4"], velocity=70, duration=120, time=0),
    Note(pitch=KEY_MAP["E4"], velocity=70, duration=120, time=0),
    Note(pitch=KEY_MAP["G4"], velocity=70, duration=120, time=0),
    Note(pitch=KEY_MAP["B4"], velocity=70, duration=120, time=0)
]

# Create arpeggio with pattern
arpeggio = Arpeggio(
    notes=c_maj7_notes,
    pattern=ArpeggioPattern.ASCENDING,  # or DESCENDING, ALTERNATING
    delay=120,  # Delay between notes in ticks
    loops=4
)

track.add_arpeggio(arpeggio)
midi.save("arpeggio_example.mid")
```

## Low-Level API

For maximum control, you can bypass the `Song` composer and interact directly with `MidiGen`, `Track`, `Note`, and `Chord` objects.

```python
from midigen import MidiGen, Track, Note, Chord, Key, KEY_MAP

# Create a MidiGen instance
midi_gen = MidiGen(tempo=120, time_signature=(4, 4), key_signature=Key("C"))

# Get the default track
track = midi_gen.get_active_track()

# Add individual notes
note_c = Note(pitch=KEY_MAP["C4"], velocity=64, duration=480, time=0)
track.add_note(note_c)

# Add a chord
note_e = Note(pitch=KEY_MAP["E4"], velocity=64, duration=480, time=480)
note_g = Note(pitch=KEY_MAP["G4"], velocity=64, duration=480, time=480)
c_major_chord = Chord([note_e, note_g])
track.add_chord(c_major_chord)

midi_gen.save("low_level_example.mid")
```

## Legacy API Support

For backward compatibility, the `Song` class still supports the older API pattern where `generate()` and `save()` are called directly on the song. This pattern is deprecated and will emit warnings:

```python
# Legacy pattern (deprecated but still works)
from midigen import Song, Section, Key

song = Song(key=Key("C", "major"), tempo=120)
song.add_section(Section("Verse", 8, "I-V-vi-IV"))
song.add_instrument("Acoustic Grand Piano")
song.generate(instrument_name="Acoustic Grand Piano")  # Deprecated
song.save("my_song.mid")  # Deprecated
```

We recommend migrating to the `MidiCompiler` pattern shown in the examples above for better separation of concerns and more control over the compilation process.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

## License

MidiGen is distributed under the [GNU General Public License, Version 3](LICENSE). Please see the `LICENSE` file for more information.
