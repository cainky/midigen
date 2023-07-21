from midigen.note import Note
from midigen.key import KEY_MAP
from midigen.chord import Chord, ChordProgression
from midigen.midigen import MidiGen
midi_gen = MidiGen()

dm9 = Chord([Note(pitch, 64, 480, 0) for pitch in [62, 65, 69, 74, 77]])
g7 = Chord([Note(pitch, 64, 480, 0) for pitch in [67, 71, 74, 77]])
cm9 = Chord([Note(pitch, 64, 480, 0) for pitch in [60, 64, 67, 72, 74]])

chord_progression = ChordProgression([dm9, g7, cm9])

midi_gen.add_chord_progression(chord_progression)
print(midi_gen)
midi_gen.save("rnb_progression.mid")

