from midigen.note import Note
from midigen.key import KEY_MAP
from midigen.chord import Chord, ChordProgression

F = Note(KEY_MAP["F"], 64, 100, 0)
G = Note(KEY_MAP["G"], 64, 100, 0)
C = Note(KEY_MAP["C"], 64, 100, 0)
D = Note(KEY_MAP["D"], 64, 100, 0)
E = Note(KEY_MAP["E"], 64, 100, 0)
A = Note(KEY_MAP["A"], 64, 100, 0)
B = Note(KEY_MAP["B"], 64, 100, 0)


CMajor = Chord(C, [E, G])
FMajor = Chord(F, [A, C])
GMajor = Chord(G, [B, D])

chord_progression = ChordProgression([CMajor, FMajor, GMajor, FMajor])

# Define the structure of the song
song_structure = ['verse', 'chorus', 'verse', 'chorus', 'bridge', 'chorus']

# Create the song
song = []

for section in song_structure:
    if section == 'verse':
        # Create a simple ascending melody
        melody = [C, D, E, F, G, F, E, D]
    elif section == 'chorus':
        # Create a simple descending melody
        melody = [G, F, E, D, C, D, E, F]
    elif section == 'bridge':
        # Create a simple oscillating melody
        melody = [C, E, C, E, C, E, C, E]

    # Combine the chord progression with the melody
    for chord in chord_progression.get_progression():
        for note in melody:
            chord.add_note(note)

    # Add the section to the song
    song.append(chord_progression)


