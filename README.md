# MidiGen: Your Intuitive MIDI Music Generation Library

[![PyPI version](https://badge.fury.io/py/midigen.svg)](https://badge.fury.io/py/midigen)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/cainky/midigen/issues)

MidiGen is a Python library designed to make creating and manipulating MIDI files as simple and intuitive as possible. Whether you're a developer looking to integrate music generation into your application, a musician experimenting with algorithmic composition, or a hobbyist exploring the world of MIDI, MidiGen provides the tools you need to bring your musical ideas to life.

Built on top of the robust `mido` library, MidiGen offers a high-level, object-oriented API that abstracts away the complexities of the MIDI protocol. From crafting simple melodies to orchestrating multi-track songs with complex chord progressions, MidiGen streamlines the entire process.

## Features

-   **High-Level Song Structure:** Organize your music into `Song` and `Section` objects, making it easy to compose with familiar concepts like verses and choruses.
-   **Music Theory-Powered Composition:** Generate `ChordProgression`s from Roman numeral notation (e.g., "I-IV-V-I"). MidiGen leverages the `music21` library to handle the music theory for you.
-   **Multi-Track Support:** Create rich, layered compositions by adding multiple tracks to your `MidiGen` object.
-   **Named Instruments:** Assign instruments to your tracks using a comprehensive list of General MIDI instrument names. No need to memorize MIDI program numbers!
-   **Drum Kits:** Easily create rhythm tracks using the `DrumKit` class and a dictionary of standard drum names.
-   **Advanced Musical Constructs:** Effortlessly add notes, chords, and arpeggios with various patterns (ascending, descending, alternating).
-   **Full MIDI Control:** Fine-tune your compositions with control over tempo, time signature, key signature, and more.

## Installation

First, ensure you have Python 3.7+ installed. Then, you can install MidiGen using pip:

```bash
pip install midigen-lib
```

Alternatively, for development, clone the repository and install with [Poetry](https://python-poetry.org/):

```bash
git clone https://github.com/cainky/midigen.git
cd midigen
poetry install
```

## Getting Started: Create a Song in 5 Lines

The easiest way to get started with MidiGen is by using the `Song` class. Here's how you can create a simple song with a classic I-V-vi-IV chord progression:

```python
from midigen import Song, Section, Key

# 1. Create a Song with a key and tempo
song = Song(key=Key("C", "major"), tempo=120)

# 2. Add a section with a chord progression
song.add_section(Section(name="Verse", length=8, chord_progression="I-V-vi-IV"))

# 3. Add an instrument to play the progression
song.add_instrument("Acoustic Grand Piano")

# 4. Generate the notes for the instrument
song.generate(instrument_name="Acoustic Grand Piano")

# 5. Save the MIDI file
song.save("my_first_song.mid")

print("Song 'my_first_song.mid' created successfully!")
```

## Advanced Usage

### Working with Multiple Tracks and Instruments

MidiGen makes it easy to create multi-track songs. Simply add as many instruments as you like, and MidiGen will automatically assign them to new tracks.

```python
from midigen import Song, Section, Key

# Create a song
song = Song(key=Key("Am", "minor"), tempo=90)

# Define the song structure
song.add_section(Section(name="Intro", length=4, chord_progression="i-VI-III-VII"))
song.add_section(Section(name="Verse", length=8, chord_progression="i-VI-III-VII-i-VI-iv-V"))

# Add instruments, which will be assigned to separate tracks
song.add_instrument("Synth Bass 1")
song.add_instrument("String Ensemble 1")
song.add_instrument("Lead 1 (square)")

# Generate the parts for each instrument
song.generate(instrument_name="Synth Bass 1", octave=3)
song.generate(instrument_name="String Ensemble 1", octave=4)
song.generate(instrument_name="Lead 1 (square)", octave=5)

# Save the multi-track MIDI file
song.save("multi_track_song.mid")
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

### Generating Arpeggios

Use the `Arpeggio` class to add flowing arpeggios to your tracks.

```python
from midigen import MidiGen, Note, Arpeggio, ArpeggioPattern, Key, KEY_MAP

midi = MidiGen(tempo=140, key=Key("C"))
track = midi.get_active_track()

# Define the notes of a C major 7 chord
c_maj7_notes = [
    Note(pitch=KEY_MAP["C4"], velocity=70, duration=120, time=0),
    Note(pitch=KEY_MAP["E4"], velocity=70, duration=120, time=0),
    Note(pitch=KEY_MAP["G4"], velocity=70, duration=120, time=0),
    Note(pitch=KEY_MAP["B4"], velocity=70, duration=120, time=0)
]

# Create an ascending arpeggio
arpeggio = Arpeggio(
    notes=c_maj7_notes,
    pattern=ArpeggioPattern.ASCENDING,
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

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

## License

MidiGen is distributed under the [GNU General Public License, Version 3](LICENSE). Please see the `LICENSE` file for more information.
