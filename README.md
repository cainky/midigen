# MidiGen

[![PyPI version](https://badge.fury.io/py/midigen-lib.svg)](https://badge.fury.io/py/midigen-lib)
[![Tests](https://github.com/cainky/midigen/actions/workflows/tests.yml/badge.svg)](https://github.com/cainky/midigen/actions/workflows/tests.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A Python library for creating and manipulating MIDI files with a music-theory-aware API. Build anything from simple melodies to multi-track compositions with chord progressions, scales, and rhythmic patterns.

Built on [mido](https://github.com/mido/mido) with a custom Roman numeral analysis engine for chord progression parsing. No heavy dependencies.

> The package is published on PyPI as `midigen-lib` but you import it as `midigen`.

## Installation

Requires Python 3.10+:

```bash
pip install midigen-lib
```

For development:

```bash
git clone https://github.com/cainky/midigen.git
cd midigen
uv sync
```

## Quick Start

```python
from midigen import Song, Section, Key
from midigen import MidiCompiler

song = Song(key=Key("C", "major"), tempo=120)
song.add_section(Section(name="Verse", length=8, chord_progression="I-V-vi-IV"))
song.add_instrument("Acoustic Grand Piano")

compiler = MidiCompiler(song)
compiler.compile().save("my_song.mid")
```

The `Song` class holds your musical intent as data. The `MidiCompiler` handles all MIDI protocol details (channels, tracks, timing). This separation makes songs easier to manipulate and test.

## Features

- **Song structure** - Compose with `Song` and `Section` objects using familiar concepts like verses and choruses
- **Chord progressions** - Roman numeral notation (e.g., "I-IV-V-I") with automatic voice leading
- **14 scale types** - Major, minor (natural/harmonic/melodic), pentatonic, blues, whole tone, chromatic, and all seven modes
- **22 chord types** - Triads, suspended, seventh, ninth, eleventh, thirteenth, augmented, and diminished voicings
- **Melody generation** - From note names, scale degrees, or random walk algorithm
- **Arpeggio patterns** - Ascending, descending, and alternating
- **Drum programming** - `DrumKit` class with standard General MIDI drum names
- **Multi-track support** - Layer instruments across separate MIDI tracks with General MIDI instrument names
- **Time utilities** - Convert between musical time (measures, beats) and MIDI ticks

## Examples

### Melodies

```python
from midigen import Melody, Scale

# From note names
melody = Melody.from_note_names("C4 E4 G4 E4 C4", durations=480)

# From scale degrees with rhythm
scale = Scale.major(60)  # C major
melody = Melody.from_degrees(
    scale,
    degrees=[1, 3, 5, 8, 5, 3, 1],
    rhythms="quarter quarter quarter half quarter quarter half"
)

# Random walk (reproducible with seed)
melody = Melody.random_walk(
    start_pitch=60, length=16, scale=scale, max_interval=3, seed=42
)

# Transform
transposed = melody.transpose(5)
retrograde = melody.reverse()
```

### Scales and Modes

```python
from midigen import Scale

# Basic
c_major = Scale.major(60)
a_minor = Scale.minor(57)
a_harmonic_minor = Scale.harmonic_minor(57)

# Pentatonic and blues
c_pent = Scale.major_pentatonic(60)
c_blues = Scale.blues(60)

# Modes
d_dorian = Scale.dorian(62)
e_phrygian = Scale.phrygian(64)
f_lydian = Scale.lydian(65)
g_mixolydian = Scale.mixolydian(67)
b_locrian = Scale.locrian(71)

# Other
c_whole_tone = Scale.whole_tone(60)
c_chromatic = Scale.chromatic(60)
```

### Multi-Track Compositions

```python
from midigen import Song, Section, Key
from midigen import MidiCompiler

song = Song(key=Key("Am", "minor"), tempo=90)

song.add_section(Section(name="Intro", length=4, chord_progression="i-VI-III-VII"))
song.add_section(Section(name="Verse", length=8, chord_progression="i-VI-III-VII-i-VI-iv-V"))

song.add_instrument("Synth Bass 1")
song.add_instrument("String Ensemble 1")
song.add_instrument("Lead 1 (square)")

compiler = MidiCompiler(song)
compiler.compile_instrument("Synth Bass 1", octave=3)
compiler.compile_instrument("String Ensemble 1", octave=4)
compiler.compile_instrument("Lead 1 (square)", octave=5)
compiler.save("multi_track.mid", output_dir="./output")
```

### Drum Patterns

```python
from midigen import MidiGen, DrumKit, Key

midi = MidiGen(key=Key("C"))
drum_kit = DrumKit()

# Simple 4/4 rock beat
for i in range(4):
    t = i * 480
    drum_kit.add_drum("Bass Drum 1", time=t)
    drum_kit.add_drum("Acoustic Snare", time=t + 240)
    drum_kit.add_drum("Closed Hi Hat", time=t)
    drum_kit.add_drum("Closed Hi Hat", time=t + 120)
    drum_kit.add_drum("Closed Hi Hat", time=t + 240)
    drum_kit.add_drum("Closed Hi Hat", time=t + 360)

track = midi.get_active_track()
track.add_drum_kit(drum_kit)
midi.save("drum_beat.mid")
```

### Arpeggios

```python
from midigen import MidiGen, Note, Arpeggio, ArpeggioPattern, Key, KEY_MAP

midi = MidiGen(tempo=140, key=Key("C"))
track = midi.get_active_track()

notes = [
    Note(pitch=KEY_MAP["C4"], velocity=70, duration=120, time=0),
    Note(pitch=KEY_MAP["E4"], velocity=70, duration=120, time=0),
    Note(pitch=KEY_MAP["G4"], velocity=70, duration=120, time=0),
    Note(pitch=KEY_MAP["B4"], velocity=70, duration=120, time=0),
]

arpeggio = Arpeggio(
    notes=notes,
    pattern=ArpeggioPattern.ASCENDING,  # or DESCENDING, ALTERNATING
    delay=120,
    loops=4,
)

track.add_arpeggio(arpeggio)
midi.save("arpeggio.mid")
```

### Time Conversions

```python
from midigen import TimeConverter

tc = TimeConverter(ticks_per_quarter_note=480)

one_measure = tc.measures_to_ticks(1)         # 1920 ticks in 4/4
half_note = tc.note_duration("half")           # 960 ticks
dotted_quarter = tc.note_duration("dotted_quarter")  # 720
triplet_eighth = tc.note_duration("triplet_eighth")  # 160

# Different time signatures
waltz_measure = tc.measures_to_ticks(
    1, time_signature_numerator=3, time_signature_denominator=4
)
```

### Low-Level API

For full control, bypass Song/MidiCompiler and work directly with tracks and notes:

```python
from midigen import MidiGen, Note, Chord, Key, KEY_MAP

midi = MidiGen(tempo=120, time_signature=(4, 4), key_signature=Key("C"))
track = midi.get_active_track()

track.add_note(Note(pitch=KEY_MAP["C4"], velocity=64, duration=480, time=0))

chord = Chord([
    Note(pitch=KEY_MAP["E4"], velocity=64, duration=480, time=480),
    Note(pitch=KEY_MAP["G4"], velocity=64, duration=480, time=480),
])
track.add_chord(chord)

midi.save("low_level.mid")
```

## Architecture

The library is organized into four layers:

- **`midigen.theory`** — Pure music theory (Note, Key, Scale, roman numeral parsing, time conversion)
- **`midigen.composition`** — Musical structures (Chord, ChordProgression, Arpeggio, Melody, DrumKit, Section)
- **`midigen.protocol`** — MIDI protocol (Track, ChannelPool, instruments)
- **`midigen.api`** — High-level API (Song, MidiGen, MidiCompiler)

All public names are available via `from midigen import ...`.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

GPL-3.0. See [LICENSE](LICENSE).
