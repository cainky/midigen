class Chord:
    def __init__(self, root):
        self.root = root

    def major_triad(self):
        return [self.root, self.root + 4, self.root + 7]

    def minor_triad(self):
        return [self.root, self.root + 3, self.root + 7]

    def dominant_seventh(self):
        return self.major_triad() + [self.root + 10]

    def major_seventh(self):
        return self.major_triad() + [self.root + 11]

    def minor_seventh(self):
        return self.minor_triad() + [self.root + 10]

    def half_diminished_seventh(self):
        return self.minor_triad() + [self.root + 9]

    def diminished_seventh(self):
        return self.minor_triad()[:-1] + [self.root + 9] + [self.root + 12]

    def minor_ninth(self):
        return self.minor_seventh() + [self.root + 14]

    def major_ninth(self):
        return self.major_seventh() + [self.root + 14]

    def dominant_ninth(self):
        return self.dominant_seventh() + [self.root + 14]


class ChordProgression:
    def __init__(self, chords):
        self.chords = chords
        self.key_map = {
            "C": 60,
            "C#": 61,
            "Db": 61,
            "D": 62,
            "D#": 63,
            "Eb": 63,
            "E": 64,
            "F": 65,
            "F#": 66,
            "Gb": 66,
            "G": 67,
            "G#": 68,
            "Ab": 68,
            "A": 69,
            "A#": 70,
            "Bb": 70,
            "B": 71
        }
        self.minor_map = {
            "C": 60,
            "C#": 61,
            "Db": 61,
            "D": 62,
            "D#": 63,
            "Eb": 63,
            "E": 64,
            "F": 65,
            "F#": 66,
            "Gb": 66,
            "G": 67,
            "G#": 68,
            "Ab": 68,
            "A": 69,
            "A#": 70,
            "Bb": 70,
            "B": 71
        }

    def get_major_triad(self, root):
        root_note = self.key_map[root]
        return Chord(root_note).major_triad()

    def get_minor_triad(self, root):
        root_note = self.minor_map[root]
        return Chord(root_note).minor_triad()

    def get_progression(self):
        progression = []
        for chord in self.chords:
            if chord.isupper():
                progression.append(self.get_major_triad(chord))
            else:
                chord = chord.upper()
                progression.append(self.get_minor_triad(chord))
        return progression
