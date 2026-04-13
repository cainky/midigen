"""Low-level API example — build a track note by note."""
from midigen import MidiGen, Note, Chord, Key, KEY_MAP

midi = MidiGen(tempo=120, time_signature=(4, 4), key_signature=Key("C"))
track = midi.get_active_track()

# single notes
track.add_note(Note(pitch=KEY_MAP["C4"], velocity=80, duration=480, time=0))
track.add_note(Note(pitch=KEY_MAP["E4"], velocity=80, duration=480, time=480))
track.add_note(Note(pitch=KEY_MAP["G4"], velocity=80, duration=480, time=960))

# a chord
c_major = Chord([
    Note(pitch=KEY_MAP["C4"], velocity=64, duration=960, time=1440),
    Note(pitch=KEY_MAP["E4"], velocity=64, duration=960, time=1440),
    Note(pitch=KEY_MAP["G4"], velocity=64, duration=960, time=1440),
])
track.add_chord(c_major)

midi.save("example.mid")
print("Saved example.mid")
