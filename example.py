"""midigen example — a few ways to make MIDI."""
from midigen import (
    Song, Section, Key, MidiCompiler,
    MidiGen, Note, Chord, Scale, Melody,
    DrumKit, Arpeggio, ArpeggioPattern, KEY_MAP,
)

# --- 1. Song API: compose with chord progressions ---

song = Song(key=Key("C", "major"), tempo=120)
song.add_section(Section("Verse", 4, "I-V-vi-IV"))
song.add_section(Section("Chorus", 4, "IV-I-V-vi"))
song.add_instrument("Acoustic Grand Piano")

MidiCompiler(song).compile().save("song.mid")
print("song.mid - done")

# --- 2. Low-level API: notes, chords, melody on a track ---

midi = MidiGen(tempo=100, key_signature=Key("G"))
track = midi.get_active_track()

# melody from a scale
scale = Scale.major(KEY_MAP["G4"])
melody = Melody.from_degrees(scale, degrees=[1, 3, 5, 8, 5, 3, 1], rhythms=480)
for note in melody.get_notes():
    track.add_note(note)

# a chord after the melody
start = len(melody.get_notes()) * 480
chord = Chord([
    Note(KEY_MAP["G4"], 70, 960, start),
    Note(KEY_MAP["B4"], 70, 960, start),
    Note(KEY_MAP["D5"], 70, 960, start),
])
track.add_chord(chord)

midi.save("melody_and_chord.mid")
print("melody_and_chord.mid - done")

# --- 3. Drums ---

drum_midi = MidiGen(tempo=120, key_signature=Key("C"))
drum_track = drum_midi.get_active_track()

kit = DrumKit()
for i in range(4):
    t = i * 480
    kit.add_drum("Bass Drum 1", time=t)
    kit.add_drum("Closed Hi Hat", time=t)
    kit.add_drum("Closed Hi Hat", time=t + 240)
    kit.add_drum("Acoustic Snare", time=t + 240)

drum_track.add_drum_kit(kit)
drum_midi.save("drums.mid")
print("drums.mid - done")

# --- 4. Arpeggio ---

arp_midi = MidiGen(tempo=140, key_signature=Key("C"))
arp_track = arp_midi.get_active_track()

arpeggio = Arpeggio(
    notes=[
        Note(KEY_MAP["C4"], 70, 120, 0),
        Note(KEY_MAP["E4"], 70, 120, 0),
        Note(KEY_MAP["G4"], 70, 120, 0),
        Note(KEY_MAP["B4"], 70, 120, 0),
    ],
    pattern=ArpeggioPattern.ALTERNATING,
    delay=120,
    loops=4,
)
arp_track.add_arpeggio(arpeggio)
arp_midi.save("arpeggio.mid")
print("arpeggio.mid - done")
