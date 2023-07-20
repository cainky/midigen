from midigen.note import Note
from midigen.key import KEY_MAP
from midigen.chord import Chord, ChordProgression, Arpeggio, ArpeggioPattern
import unittest

class TestChord(unittest.TestCase):
    def setUp(self):
        root_note = Note(KEY_MAP["C"], 64, 100, 0)
        self.chord = Chord(root_note)

    def test_chord_creation(self):
        self.assertEqual(self.chord.get_root(), Note(KEY_MAP["C"], 64, 100, 0))

    def test_add_note(self):
        new_note = Note(62, 64, 100, 100)
        self.chord.add_note(new_note)
        self.assertEqual(self.chord.get_notes(), [Note(KEY_MAP["C"], 64, 100, 0), new_note])

    def test_chord_triads(self):
        major_triad = self.chord.major_triad()
        self.assertEqual(major_triad, [Note(KEY_MAP["C"], 64, 100, 0), Note(KEY_MAP["E"], 64, 100, 0), Note(KEY_MAP["G"], 64, 100, 0)])

        minor_triad = self.chord.minor_triad()
        self.assertEqual(minor_triad, [Note(KEY_MAP["C"], 64, 100, 0), Note(KEY_MAP["D#"], 64, 100, 0), Note(KEY_MAP["G"], 64, 100, 0)])

    def test_chord_seventh(self):
        dominant_seventh = self.chord.dominant_seventh()
        self.assertEqual(dominant_seventh, [Note(KEY_MAP["C"], 64, 100, 0), Note(KEY_MAP["E"], 64, 100, 0), 
                                            Note(KEY_MAP["G"], 64, 100, 0), Note(KEY_MAP["Bb"], 64, 100, 0)])

        major_seventh = self.chord.major_seventh()
        self.assertEqual(major_seventh, [Note(KEY_MAP["C"], 64, 100, 0), Note(KEY_MAP["E"], 64, 100, 0), 
                                         Note(KEY_MAP["G"], 64, 100, 0), Note(KEY_MAP["B"], 64, 100, 0)])
    def test_minor_seventh_chord(self):
        minor_seventh = self.chord.minor_seventh()
        self.assertEqual(minor_seventh, [Note(KEY_MAP["C"], 64, 100, 0), Note(KEY_MAP["Eb"], 64, 100, 0), 
                                         Note(KEY_MAP["G"], 64, 100, 0), Note(KEY_MAP["Bb"], 64, 100, 0)])
        
    def test_half_diminished_seventh_chord(self):
        half_diminished_seventh = self.chord.half_diminished_seventh()
        expected_notes = [Note(KEY_MAP[note], self.chord.root.velocity, self.chord.root.duration, self.chord.root.time) for note in ["C", "Eb", "Gb", "Bb"]]
        self.assertEqual(half_diminished_seventh, expected_notes)

    def test_diminished_seventh_chord(self):
        diminished_seventh = self.chord.diminished_seventh()
        expected_notes = [Note(KEY_MAP[note], self.chord.root.velocity, self.chord.root.duration, self.chord.root.time) for note in ["C", "Eb", "Gb", "A"]]
        self.assertEqual(diminished_seventh, expected_notes)


    def test_minor_ninth_chord(self):
        minor_ninth = self.chord.minor_ninth()
        expected_notes = [Note(KEY_MAP["C"], 64, 100, 0), Note(KEY_MAP["Eb"], 64, 100, 0), 
                        Note(KEY_MAP["G"], 64, 100, 0), Note(KEY_MAP["Bb"], 64, 100, 0), 
                        Note(KEY_MAP["D"] + 12, 64, 100, 0)]  # Note the "+ 12" here
        self.assertEqual(minor_ninth, expected_notes)

    def test_dominant_ninth_chord(self):
        dominant_ninth = self.chord.dominant_ninth()
        expected_notes = [Note(KEY_MAP["C"], 64, 100, 0), Note(KEY_MAP["E"], 64, 100, 0), 
                        Note(KEY_MAP["G"], 64, 100, 0), Note(KEY_MAP["Bb"], 64, 100, 0), 
                        Note(KEY_MAP["D"] + 12, 64, 100, 0)]  # And here
        self.assertEqual(dominant_ninth, expected_notes)
    
    def test_major_ninth_chord(self):
        major_ninth = self.chord.major_ninth()
        expected_major_ninth = [Note(KEY_MAP["C"], 64, 100, 0), Note(KEY_MAP["E"], 64, 100, 0),
                                Note(KEY_MAP["G"], 64, 100, 0), Note(KEY_MAP["B"], 64, 100, 0),
                                Note(KEY_MAP["D"], 64, 100, 0) + 12]  # Increase the octave for the ninth note
        for note_actual, note_expected in zip(major_ninth, expected_major_ninth):
            self.assertEqual(note_actual, note_expected)


class TestChordProgression(unittest.TestCase):
    def setUp(self):
        self.root_note1 = Note(KEY_MAP["C"], 64, 100, 0)
        self.root_note2 = Note(KEY_MAP["D"], 64, 100, 0)
        self.chord1 = Chord(self.root_note1)
        self.chord2 = Chord(self.root_note2)
        self.progression = ChordProgression([self.chord1, self.chord2])

    def test_add_chord(self):
        new_chord = Chord(Note(KEY_MAP["E"], 64, 100, 0))
        self.progression.add_chord(new_chord)
        self.assertEqual(self.progression.chords[-1], new_chord)

    def test_duration_calculation(self):
        expected_duration = self.chord1._calculate_duration() + self.chord2._calculate_duration()
        self.assertEqual(self.progression.duration, expected_duration)

    def test_start_time_calculation(self):
        expected_start_time = min(self.chord1._calculate_start_time(), self.chord2._calculate_start_time())
        self.assertEqual(self.progression.time, expected_start_time)
        
    def test_str_representation(self):
        self.assertEqual(str(self.progression), f"[{str(self.chord1)}, {str(self.chord2)}]")

    def test_equality(self):
        other_progression = ChordProgression([self.chord1, self.chord2])
        self.assertEqual(self.progression, other_progression)
        new_chord = Chord(Note(KEY_MAP["E"], 64, 100, 0))
        other_progression.add_chord(new_chord)
        self.assertNotEqual(self.progression, other_progression)

class TestArpeggio(unittest.TestCase):
    def setUp(self):
        self.root_note = Note(KEY_MAP["C"], 64, 100, 0)
        self.notes = [Note(62, 64, 100, 100), Note(64, 64, 100, 200)]
        self.arpeggio = Arpeggio(self.root_note, self.notes, delay=100, pattern=ArpeggioPattern.ASCENDING, loops=1)

    def test_arpeggio_creation(self):
        self.assertEqual(self.arpeggio.get_root(), Note(KEY_MAP["C"], 64, 100, 0))

    def test_get_sequential_notes(self):
        sequential_notes = self.arpeggio.get_sequential_notes()
        self.assertEqual(sequential_notes, [Note(KEY_MAP["C"], 64, 100, 0), Note(KEY_MAP["D"], 64, 100, 100), Note(KEY_MAP["E"], 64, 100, 200)])

    def test_get_sequential_notes_ascending(self):
        arpeggio = Arpeggio(self.root_note, self.notes, delay=100, pattern=ArpeggioPattern.ASCENDING, loops=1)
        sequential_notes = arpeggio.get_sequential_notes()
        expected_notes = [Note(KEY_MAP["C"], 64, 100, 0), Note(KEY_MAP["D"], 64, 100, 100), Note(KEY_MAP["E"], 64, 100, 200)]
        self.assertEqual(sequential_notes, expected_notes)

    def test_get_sequential_notes_descending(self):
        arpeggio = Arpeggio(self.root_note, self.notes, delay=100, pattern=ArpeggioPattern.DESCENDING, loops=1)
        sequential_notes = arpeggio.get_sequential_notes()
        expected_notes = [Note(KEY_MAP["E"], 64, 100, 200), Note(KEY_MAP["D"], 64, 100, 100), Note(KEY_MAP["C"], 64, 100, 0)]
        self.assertEqual(sequential_notes, expected_notes)

    def test_get_sequential_notes_alternating(self):
        arpeggio = Arpeggio(self.root_note, self.notes, delay=100, pattern=ArpeggioPattern.ALTERNATING, loops=2)
        sequential_notes = arpeggio.get_sequential_notes()
        expected_notes = [Note(KEY_MAP["C"], 64, 100, 0), Note(KEY_MAP["D"], 64, 100, 100), Note(KEY_MAP["E"], 64, 100, 200),
                        Note(KEY_MAP["E"], 64, 100, 200), Note(KEY_MAP["D"], 64, 100, 100), Note(KEY_MAP["C"], 64, 100, 0)]
        self.assertEqual(sequential_notes, expected_notes)
