# MidiGen

MidiGen is a Python class that helps you create, modify, and save MIDI files using the Mido library. It provides an object-oriented approach for managing MIDI files and simplifies common MIDI operations such as adding notes, chords, arpeggios, changing instruments, as well as managing tempo, time signatures, and key signatures.

## Features

- **Dynamic MIDI Creation**: Quickly generate MIDI files programmatically.
- **Note and Chord Support**: Easily add notes or chords to your MIDI tracks.
- **Advanced Musical Constructs**: Support for multiple tracks, simultaneous notes, and drum patterns.
- **Humanization**: Apply slight timing variations to mimic human play.

## Installation

First, install Poetry if you haven't already:

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

Then, clone the repository and install dependencies using Poetry:

```bash
git clone https://github.com/cainky/midigen.git
cd midigen
poetry install
```
## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MidiGen is distributed under the GNU General Public License, Version 3, allowing for free software distribution and modification while ensuring that all copies and modified versions remain free.

## Usage

```python
from midigen import MidiGen, Track, Note, Chord, Key, KEY_MAP

midi_gen = MidiGen(tempo=120, time_signature=(4, 4), key_signature=Key("C"))

note_c = Note(pitch=KEY_MAP["C"], velocity=64, duration=480, time=0)
note_e = Note(pitch=KEY_MAP["E"], velocity=64, duration=480, time=0)
note_g = Note(pitch=KEY_MAP["G"], velocity=64, duration=480, time=0)

c_major_chord = Chord([note_c, note_e, note_g])

track = midi_gen.get_active_track()
track.add_chord(c_major_chord)

midi_gen.save("example_song_with_chord.mid")
```

### Class Methods

### __init__(self, tempo=120, time_signature=(4, 4), key_signature=0)

The constructor creates a new MidiGen instance with the specified tempo, time signature, and key signature.

### set_tempo(self, tempo)

Sets the tempo (in BPM) for the MIDI file.

### set_time_signature(self, numerator, denominator)

Sets the time signature for the MIDI file.

### set_key_signature(self, key)

Sets the key signature for the MIDI file.

### add_program_change(self, channel, program)

Adds a program change (instrument) event to the specified channel.

A program change is a MIDI message used to change the instrument or sound (also known as "patch" or "preset") used by a synthesizer or other MIDI device. In a General MIDI (GM) system, there are 128 standard instruments that can be selected using program change messages, allowing you to switch between different instrument sounds such as piano, guitar, strings, and more.

In the context of the MidiGen class, the add_program_change method allows you to change the instrument sound for a specific MIDI channel.

### add_control_change(self, channel, control, value)

Adds a control change event to the specified channel.

### add_pitch_bend(self, channel, value)

Adds a pitch bend event to the specified channel.

### add_note(self, note, velocity, duration, time=0)

Adds a note with the specified pitch, velocity, and duration at the given time (in ticks).

### add_chord(self, notes, velocity, duration, time=0)

Adds a chord with the specified notes, velocity, and duration at the given time (in ticks).

### add_arpeggio(self, notes, velocity, duration, arp_duration, time=0)

Adds an arpeggio with the specified notes, velocity, duration, and arpeggio duration at the given time (in ticks).

### quantize(self, time_value, quantization_value)

Quantizes the given time value to the nearest multiple of the quantization value.

### load_midi_file(self, filename)

Loads an existing MIDI file for further processing or manipulation.

### save(self, filename)

Saves the MIDI file to the specified filename.

## Properties

### tempo

The tempo (in BPM) of the MIDI file.

### time_signature

The time signature of the MIDI file.

### key_signature

The key signature of the MIDI file.

### track

The Mido MidiTrack object associated with the MidiGen instance.
