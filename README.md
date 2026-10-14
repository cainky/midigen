# MidiGen

[![PyPI version](https://badge.fury.io/py/midigen-lib.svg)](https://badge.fury.io/py/midigen-lib)
[![Tests](https://github.com/cainky/midigen/actions/workflows/tests.yml/badge.svg)](https://github.com/cainky/midigen/actions/workflows/tests.yml)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPLv3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

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
from midigen import Song, Section, Key, MidiCompiler

song = Song(key=Key("C", "major"), tempo=120)
song.add_section(Section("Verse", 8, "I-V-vi-IV"))
song.add_section(Section("Chorus", 4, "IV-I-V-vi"))
song.add_instrument("Acoustic Grand Piano")

MidiCompiler(song).compile().save("my_song.mid")
```

`Song` holds your musical intent. `MidiCompiler` handles MIDI protocol details (channels, tracks, timing). See [How Song compilation works](#how-song-compilation-works) for what ends up in the file.

## Features

- **Song structure** - Compose with `Song` and `Section` objects using familiar concepts like verses and choruses
- **Chord progressions** - Roman numeral notation (e.g., "I-IV-V-I") with sevenths, diminished, half-diminished, augmented and major-seventh chords, plus borrowed roots like `bVII`
- **14 scale types** - Major, minor (natural/harmonic/melodic), pentatonic, blues, whole tone, chromatic, and all seven modes
- **27 chord types** - Triads, suspended, sixth, seventh, ninth, eleventh, thirteenth, add9/add11, augmented, and diminished chords via `Chord.build()`
- **Melody generation** - From note names, scale degrees, or random walk algorithm
- **Arpeggio patterns** - Ascending, descending, and alternating
- **Drum programming** - `DrumKit` class with standard General MIDI drum names (played on MIDI channel 9)
- **Multi-track support** - Each instrument gets its own track and MIDI channel, using General MIDI instrument names
- **Time utilities** - Convert between musical time (measures, beats) and MIDI ticks

## Examples

### Melodies

```python
from midigen import MidiGen, Melody, Scale

# From note names (C-1 to G9, sharps or flats: "F#3", "Bb4")
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

# Put it on a track
midi = MidiGen(tempo=100)
midi.get_active_track().add_melody(melody)
midi.save("melody.mid")
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
from midigen import Song, Section, Key, MidiCompiler

song = Song(key=Key("A", "minor"), tempo=90)

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

Each instrument plays on its own channel (0, 1, 2, ... in the order added). `save()` keeps the parts you compiled with `compile_instrument()` and compiles any remaining instruments with the defaults.

### Drums in a Song

The compiler puts drum tracks on channel 9 and leaves them empty, so you fill them with a `DrumKit`:

```python
from midigen import Song, Section, Key, MidiCompiler, DrumKit

song = Song(key=Key("C"), tempo=110)
song.add_section(Section("Verse", 2, "I-vi-IV-V"))
song.add_instrument("Acoustic Grand Piano")
song.add_drums()

compiler = MidiCompiler(song).compile()

kit = DrumKit()
for beat in range(8):  # 2 bars of 4/4
    kit.add_drum("Bass Drum 1" if beat % 2 == 0 else "Acoustic Snare", time=beat * 480)
compiler.get_track("Drums").add_drum_kit(kit)

compiler.save("song_with_drums.mid")
```

### Drum Patterns

```python
from midigen import MidiGen, DrumKit, Key

midi = MidiGen(key_signature=Key("C"))
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

track = midi.add_track(channel=9)  # General MIDI drums only sound on channel 9
track.add_drum_kit(drum_kit)
midi.save("drum_beat.mid")
```

Drum names follow the General MIDI list (`GM1_DRUM_MAP`). Case, spaces and hyphens don't matter, so `"open hi hat"` finds `"Open Hi-Hat"`. Adding a `DrumKit` to a track on any other channel plays the hits as pitched notes and issues a warning.

### Arpeggios

```python
from midigen import MidiGen, Note, Arpeggio, ArpeggioPattern, Key, KEY_MAP

midi = MidiGen(tempo=140, key_signature=Key("C"))
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

The notes can be in any order: `ASCENDING` plays them low to high, `DESCENDING` high to low, and `ALTERNATING` goes up, then down on the next loop. The arpeggio starts at the earliest note time, and each following note is `delay` ticks later.

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

# Controller and pitch-bend times are absolute ticks, like note times
track.add_control_change(control=64, value=127, time=480)  # sustain pedal down at beat 2
track.add_control_change(control=64, value=0, time=960)    # and up at beat 3
track.add_pitch_bend(value=2048, time=720)

# A second instrument on its own channel
bass = midi.add_track(channel=1)
bass.add_program_change(program=32)  # Acoustic Bass
bass.add_note(Note(pitch=KEY_MAP["C2"], velocity=90, duration=960, time=0))

# Modes: MIDI key signatures are major/minor, so D dorian is written as C major
midi.set_mode("D", "dorian")

midi.save("low_level.mid")

# MidiGen is a mido.MidiFile, so mido's helpers work on it
print(f"{midi.length:.1f} seconds")
```

## How Song compilation works

- **Section length is in bars of 4/4** (1920 ticks per bar at 480 ticks per beat).
- **Each chord lasts one beat (480 ticks) by default**, and the progression loops or is cut off to fill the section. `Section("Verse", 8, "I-V-vi-IV")` plays the four chords eight times (32 chords). For one chord per bar, use `compiler.compile_instrument("Acoustic Grand Piano", duration=1920)`. A chord that would cross the end of a section is shortened to end on it.
- **Chord tones are placed within one octave** (set with `octave`, default 4), so V in C major is G4, B4, D4. There is no automatic voice leading or inversion.
- **Tracks and channels follow the order instruments were added.** Drum tracks (`song.add_drums()`) use channel 9; at most 15 melodic instruments fit alongside them.
- **Compiling is repeatable.** Calling `compile()` again doesn't duplicate notes, `compile_instrument()` replaces that instrument's part (notes you added by hand stay), and `save()` compiles only what hasn't been compiled yet.

### Roman numerals

| Notation | Chord |
|----------|-------|
| `I`, `IV`, `V` / `i`, `ii`, `vi` | Major / minor triad (case sets the quality) |
| `V7` / `ii7` | Dominant seventh / minor seventh |
| `Imaj7`, `IM7`, `IΔ7` / `imaj7` | Major seventh / minor-major seventh |
| `vii°`, `viio`, `viidim` | Diminished triad |
| `vii°7`, `viio7`, `viidim7` | Diminished seventh |
| `viiø`, `viiø7` | Half-diminished seventh |
| `III+`, `IIIaug` | Augmented triad |
| `bVII`, `#iv°` | Root lowered or raised by a semitone (`♭`/`♯` also work) |

In minor keys, minor and diminished chords on the 6th and 7th degrees use the raised degree (`vii°` in A minor is G#-B-D), while major chords there use the natural degree (`VII` in A minor is G-B-D). Inversions (`V6`, `V65`), extensions (`V9`) and suspensions (`Isus4`) are not supported and raise `ValueError` instead of being silently dropped.

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

AGPL-3.0. See [LICENSE](LICENSE).
