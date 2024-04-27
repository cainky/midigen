from midigen.midigen import MidiGen
from midigen.note import Note
from midigen.chord import Chord
from midigen.key import Key, KEY_MAP

midi_gen = MidiGen(tempo=120, time_signature=(4, 4), key_signature=Key("C"))

note_c = Note(pitch=KEY_MAP["C4"], velocity=64, duration=480, time=0)
note_e = Note(pitch=KEY_MAP["E4"], velocity=64, duration=480, time=0)
note_g = Note(pitch=KEY_MAP["G4"], velocity=64, duration=480, time=0)

c_major_chord = Chord([note_c, note_e, note_g])

track = midi_gen.get_active_track()
track.add_chord(c_major_chord)
midi_gen.save("example.mid")
