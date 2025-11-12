from midigen.note import Note
from midigen.key import KEY_MAP
from midigen.chord import Chord, ChordProgression, Arpeggio, ArpeggioPattern
import unittest


class TestChord(unittest.TestCase):
    def setUp(self):
        self.notes = [Note(KEY_MAP["C4"], 64, 100, 0)]
        self.chord = Chord(self.notes)

    def test_chord_creation(self):
        self.assertEqual(self.chord.get_chord(), self.notes)

    def test_add_note(self):
        new_note = Note(62, 64, 100, 100)
        self.chord.add_note(new_note)
        self.assertEqual(
            self.chord.get_chord(), [Note(KEY_MAP["C4"], 64, 100, 0), new_note]
        )

    def test_chord_triads(self):
        major_triad = self.chord.major_triad()
        self.assertEqual(
            major_triad,
            [
                Note(KEY_MAP["C4"], 64, 100, 0),
                Note(KEY_MAP["E4"], 64, 100, 0),
                Note(KEY_MAP["G4"], 64, 100, 0),
            ],
        )

        minor_triad = self.chord.minor_triad()
        self.assertEqual(
            minor_triad,
            [
                Note(KEY_MAP["C4"], 64, 100, 0),
                Note(KEY_MAP["D#4"], 64, 100, 0),
                Note(KEY_MAP["G4"], 64, 100, 0),
            ],
        )

    def test_chord_seventh(self):
        dominant_seventh = self.chord.dominant_seventh()
        self.assertEqual(
            dominant_seventh,
            [
                Note(KEY_MAP["C4"], 64, 100, 0),
                Note(KEY_MAP["E4"], 64, 100, 0),
                Note(KEY_MAP["G4"], 64, 100, 0),
                Note(KEY_MAP["Bb4"], 64, 100, 0),
            ],
        )

        major_seventh = self.chord.major_seventh()
        self.assertEqual(
            major_seventh,
            [
                Note(KEY_MAP["C4"], 64, 100, 0),
                Note(KEY_MAP["E4"], 64, 100, 0),
                Note(KEY_MAP["G4"], 64, 100, 0),
                Note(KEY_MAP["B4"], 64, 100, 0),
            ],
        )

    def test_minor_seventh_chord(self):
        minor_seventh = self.chord.minor_seventh()
        self.assertEqual(
            minor_seventh,
            [
                Note(KEY_MAP["C4"], 64, 100, 0),
                Note(KEY_MAP["Eb4"], 64, 100, 0),
                Note(KEY_MAP["G4"], 64, 100, 0),
                Note(KEY_MAP["Bb4"], 64, 100, 0),
            ],
        )

    def test_half_diminished_seventh_chord(self):
        half_diminished_seventh = self.chord.half_diminished_seventh()
        expected_notes = [
            Note(
                KEY_MAP[note],
                self.chord.root.velocity,
                self.chord.root.duration,
                self.chord.root.time,
            )
            for note in ["C4", "Eb4", "Gb4", "Bb4"]
        ]
        self.assertEqual(half_diminished_seventh, expected_notes)

    def test_diminished_seventh_chord(self):
        diminished_seventh = self.chord.diminished_seventh()
        expected_notes = [
            Note(
                KEY_MAP[note],
                self.chord.root.velocity,
                self.chord.root.duration,
                self.chord.root.time,
            )
            for note in ["C4", "Eb4", "Gb4", "A4"]
        ]
        self.assertEqual(diminished_seventh, expected_notes)

    def test_minor_ninth_chord(self):
        minor_ninth = self.chord.minor_ninth()
        expected_notes = [
            Note(KEY_MAP["C4"], 64, 100, 0),
            Note(KEY_MAP["Eb4"], 64, 100, 0),
            Note(KEY_MAP["G4"], 64, 100, 0),
            Note(KEY_MAP["Bb4"], 64, 100, 0),
            Note(KEY_MAP["D4"] + 12, 64, 100, 0),
        ]  # Note the "+ 12" here
        self.assertEqual(minor_ninth, expected_notes)

    def test_dominant_ninth_chord(self):
        dominant_ninth = self.chord.dominant_ninth()
        expected_notes = [
            Note(KEY_MAP["C4"], 64, 100, 0),
            Note(KEY_MAP["E4"], 64, 100, 0),
            Note(KEY_MAP["G4"], 64, 100, 0),
            Note(KEY_MAP["Bb4"], 64, 100, 0),
            Note(KEY_MAP["D4"] + 12, 64, 100, 0),
        ]  # And here
        self.assertEqual(dominant_ninth, expected_notes)

    def test_major_ninth_chord(self):
        major_ninth = self.chord.major_ninth()
        expected_major_ninth = [
            Note(KEY_MAP["C4"], 64, 100, 0),
            Note(KEY_MAP["E4"], 64, 100, 0),
            Note(KEY_MAP["G4"], 64, 100, 0),
            Note(KEY_MAP["B4"], 64, 100, 0),
            Note(KEY_MAP["D4"], 64, 100, 0) + 12,
        ]  # Increase the octave for the ninth note
        for note_actual, note_expected in zip(major_ninth, expected_major_ninth):
            self.assertEqual(note_actual, note_expected)


class TestChordProgression(unittest.TestCase):
    def setUp(self):
        self.root_note1 = Note(KEY_MAP["C4"], 64, 100, 0)
        self.root_note2 = Note(KEY_MAP["D4"], 64, 100, 0)
        self.chord1 = Chord([self.root_note1])
        self.chord2 = Chord([self.root_note2])
        self.progression = ChordProgression([self.chord1, self.chord2])

    def test_add_chord(self):
        new_chord = Chord([Note(KEY_MAP["E4"], 64, 100, 0)])
        self.progression.add_chord(new_chord)
        self.assertEqual(self.progression.chords[-1], new_chord)

    def test_duration_calculation(self):
        expected_duration = (
            self.chord1._calculate_duration() + self.chord2._calculate_duration()
        )
        self.assertEqual(self.progression.duration, expected_duration)

    def test_start_time_calculation(self):
        expected_start_time = min(
            self.chord1._calculate_start_time(), self.chord2._calculate_start_time()
        )
        self.assertEqual(self.progression.time, expected_start_time)

    def test_str_representation(self):
        self.assertEqual(
            str(self.progression), f"[{str(self.chord1)}, {str(self.chord2)}]"
        )

    def test_equality(self):
        other_progression = ChordProgression([self.chord1, self.chord2])
        self.assertEqual(self.progression, other_progression)
        new_chord = Chord([Note(KEY_MAP["E4"], 64, 100, 0)])
        other_progression.add_chord(new_chord)
        self.assertNotEqual(self.progression, other_progression)


class TestArpeggio(unittest.TestCase):
    def setUp(self):
        # Updated to use the new KEY_MAP with octaves
        self.notes = [
            Note(KEY_MAP["C4"], 64, 100, 0),
            Note(KEY_MAP["D4"], 64, 100, 0),
            Note(KEY_MAP["E4"], 64, 100, 0),
        ]
        self.arpeggio = Arpeggio(
            self.notes, delay=100, pattern=ArpeggioPattern.ASCENDING, loops=1
        )

    def test_arpeggio_creation(self):
        self.assertEqual(self.arpeggio.get_chord(), self.notes)

    def test_get_sequential_notes(self):
        sequential_notes = self.arpeggio.get_sequential_notes()
        self.assertEqual(
            sequential_notes,
            [
                Note(KEY_MAP["C4"], 64, 100, 0),
                Note(KEY_MAP["D4"], 64, 100, 100),
                Note(KEY_MAP["E4"], 64, 100, 200),
            ],
        )

    def test_get_sequential_notes_ascending(self):
        arpeggio = Arpeggio(
            self.notes, delay=100, pattern=ArpeggioPattern.ASCENDING, loops=1
        )
        sequential_notes = arpeggio.get_sequential_notes()
        expected_notes = [
            Note(KEY_MAP["C4"], 64, 100, 0),
            Note(KEY_MAP["D4"], 64, 100, 100),
            Note(KEY_MAP["E4"], 64, 100, 200),
        ]
        self.assertEqual(sequential_notes, expected_notes)

    def test_get_sequential_notes_descending(self):
        arpeggio = Arpeggio(
            self.notes, delay=100, pattern=ArpeggioPattern.DESCENDING, loops=1
        )
        sequential_notes = arpeggio.get_sequential_notes()
        expected_notes = [
            Note(KEY_MAP["E4"], 64, 100, 0),
            Note(KEY_MAP["D4"], 64, 100, 100),
            Note(KEY_MAP["C4"], 64, 100, 200),
        ]
        self.assertEqual(sequential_notes, expected_notes)

    def test_get_sequential_notes_alternating(self):
        arpeggio = Arpeggio(
            self.notes, delay=100, pattern=ArpeggioPattern.ALTERNATING, loops=2
        )
        sequential_notes = arpeggio.get_sequential_notes()
        expected_notes = [
            # First loop - ascending
            Note(KEY_MAP["C4"], 64, 100, 0),
            Note(KEY_MAP["D4"], 64, 100, 100),
            Note(KEY_MAP["E4"], 64, 100, 200),
            # Second loop - descending
            Note(KEY_MAP["E4"], 64, 100, 300),
            Note(KEY_MAP["D4"], 64, 100, 400),
            Note(KEY_MAP["C4"], 64, 100, 500),
        ]
        self.assertEqual(sequential_notes, expected_notes)

    def test_arpeggio_multiple_loops(self):
        arpeggio = Arpeggio(
            self.notes, delay=50, pattern=ArpeggioPattern.ASCENDING, loops=3
        )
        sequential_notes = arpeggio.get_sequential_notes()
        # Should have 9 notes total (3 notes x 3 loops)
        self.assertEqual(len(sequential_notes), 9)
        # Verify timing of first note in each loop
        self.assertEqual(sequential_notes[0].time, 0)      # Loop 1
        self.assertEqual(sequential_notes[3].time, 150)    # Loop 2
        self.assertEqual(sequential_notes[6].time, 300)    # Loop 3


from midigen.key import Key

class TestChordProgressionFromRomanNumerals(unittest.TestCase):

    def test_from_roman_numerals_major(self):
        key = Key("C", "major")
        progression = ChordProgression.from_roman_numerals(
            key=key,
            progression_string="I-V-vi-IV",
            octave=4,
            duration=480,
            time_per_chord=480
        )
        self.assertEqual(len(progression.chords), 4)

        # Check root notes (C, G, A, F)
        root_pitches = [chord.get_root().pitch for chord in progression.chords]
        expected_pitches = [KEY_MAP["C4"], KEY_MAP["G4"], KEY_MAP["A4"], KEY_MAP["F4"]]
        self.assertEqual(root_pitches, expected_pitches)

    def test_from_roman_numerals_minor(self):
        key = Key("A", "minor")
        progression = ChordProgression.from_roman_numerals(
            key=key,
            progression_string="i-iv-v",
            octave=4,
            duration=480,
            time_per_chord=480
        )
        self.assertEqual(len(progression.chords), 3)

        # Check root notes (A, D, E)
        root_pitches = [chord.get_root().pitch for chord in progression.chords]
        expected_pitches = [KEY_MAP["A4"], KEY_MAP["D4"], KEY_MAP["E4"]]
        self.assertEqual(root_pitches, expected_pitches)

    def test_chord_timing(self):
        key = Key("C", "major")
        progression = ChordProgression.from_roman_numerals(
            key=key,
            progression_string="I-V",
            octave=4,
            duration=480,
            time_per_chord=480
        )

        chord1_time = progression.chords[0].time
        chord2_time = progression.chords[1].time

        self.assertEqual(chord1_time, 0)
        # This is tricky because the time is distributed among the notes.
        # The first note of the second chord should have the time of the first chord's duration.
        self.assertEqual(progression.chords[1].notes[0].time, 480)
