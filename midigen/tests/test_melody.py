import unittest
from midigen import Melody, Scale, Note, KEY_MAP


class TestMelody(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.c_major_scale = Scale.major(60)  # C major starting at C4

    def test_melody_initialization(self):
        """Test basic melody initialization"""
        notes = [
            Note(60, 80, 480, 0),
            Note(64, 80, 480, 480),
            Note(67, 80, 480, 960)
        ]
        melody = Melody(notes)
        self.assertEqual(len(melody), 3)
        self.assertEqual(melody.get_notes(), notes)

    def test_from_scale_basic(self):
        """Test melody creation from scale with basic pattern"""
        pattern = [0, 2, 4, 2, 0]  # C E G E C
        melody = Melody.from_scale(self.c_major_scale, pattern)

        self.assertEqual(len(melody), 5)
        self.assertEqual(melody[0].pitch, 60)  # C
        self.assertEqual(melody[1].pitch, 64)  # E
        self.assertEqual(melody[2].pitch, 67)  # G
        self.assertEqual(melody[3].pitch, 64)  # E
        self.assertEqual(melody[4].pitch, 60)  # C

    def test_from_scale_with_custom_params(self):
        """Test melody from scale with custom parameters"""
        pattern = [0, 1, 2]
        melody = Melody.from_scale(
            self.c_major_scale,
            pattern,
            start_time=960,
            note_duration=240,
            velocity=100
        )

        self.assertEqual(melody[0].time, 960)
        self.assertEqual(melody[1].time, 1200)  # 960 + 240
        self.assertEqual(melody[0].duration, 240)
        self.assertEqual(melody[0].velocity, 100)

    def test_from_scale_octave_shift(self):
        """Test octave shifting in from_scale"""
        pattern = [0]
        melody_up = Melody.from_scale(self.c_major_scale, pattern, octave_shift=1)
        melody_down = Melody.from_scale(self.c_major_scale, pattern, octave_shift=-1)

        self.assertEqual(melody_up[0].pitch, 72)  # C5
        self.assertEqual(melody_down[0].pitch, 48)  # C3

    def test_from_scale_invalid_degree(self):
        """Test from_scale with invalid scale degree"""
        pattern = [0, 10]  # 10 is out of range for 8-note scale
        with self.assertRaises(ValueError):
            Melody.from_scale(self.c_major_scale, pattern)

    def test_from_scale_empty_inputs(self):
        """Test from_scale with empty inputs"""
        with self.assertRaises(ValueError):
            Melody.from_scale([], [0, 1, 2])
        with self.assertRaises(ValueError):
            Melody.from_scale(self.c_major_scale, [])

    def test_from_note_names_basic(self):
        """Test melody creation from note names"""
        melody = Melody.from_note_names("C4 E4 G4 C5")

        self.assertEqual(len(melody), 4)
        self.assertEqual(melody[0].pitch, KEY_MAP["C4"])
        self.assertEqual(melody[1].pitch, KEY_MAP["E4"])
        self.assertEqual(melody[2].pitch, KEY_MAP["G4"])
        self.assertEqual(melody[3].pitch, KEY_MAP["C5"])

    def test_from_note_names_with_durations(self):
        """Test from_note_names with custom durations"""
        durations = [480, 240, 240, 960]
        melody = Melody.from_note_names("C4 D4 E4 F4", durations=durations)

        self.assertEqual(melody[0].duration, 480)
        self.assertEqual(melody[1].duration, 240)
        self.assertEqual(melody[2].duration, 240)
        self.assertEqual(melody[3].duration, 960)

        # Check timing
        self.assertEqual(melody[0].time, 0)
        self.assertEqual(melody[1].time, 480)
        self.assertEqual(melody[2].time, 720)
        self.assertEqual(melody[3].time, 960)

    def test_from_note_names_invalid(self):
        """Test from_note_names with invalid inputs"""
        with self.assertRaises(ValueError):
            Melody.from_note_names("")

        with self.assertRaises(ValueError):
            Melody.from_note_names("C4 InvalidNote G4")

        with self.assertRaises(ValueError):
            Melody.from_note_names("C4 E4", durations=[480, 240, 960])  # Mismatched lengths

    def test_from_degrees_basic(self):
        """Test melody from scale degrees (1-based)"""
        degrees = [1, 3, 5, 8]  # Root, 3rd, 5th, octave
        melody = Melody.from_degrees(self.c_major_scale, degrees)

        self.assertEqual(len(melody), 4)
        self.assertEqual(melody[0].pitch, 60)  # C4 (1st degree)
        self.assertEqual(melody[1].pitch, 64)  # E4 (3rd degree)
        self.assertEqual(melody[2].pitch, 67)  # G4 (5th degree)
        self.assertEqual(melody[3].pitch, 72)  # C5 (8th degree, octave)

    def test_from_degrees_descending(self):
        """Test descending melody with scale degrees"""
        degrees = [8, 7, 6, 5, 4, 3, 2, 1]
        melody = Melody.from_degrees(self.c_major_scale, degrees)

        self.assertEqual(len(melody), 8)
        self.assertEqual(melody[0].pitch, 72)  # C5
        self.assertEqual(melody[-1].pitch, 60)  # C4

    def test_from_degrees_with_rhythm_string(self):
        """Test from_degrees with rhythm string"""
        degrees = [1, 3, 5]
        melody = Melody.from_degrees(self.c_major_scale, degrees, rhythms="quarter half whole")

        self.assertEqual(melody[0].duration, 480)  # Quarter note
        self.assertEqual(melody[1].duration, 960)  # Half note
        self.assertEqual(melody[2].duration, 1920)  # Whole note

    def test_from_degrees_with_rhythm_abbreviations(self):
        """Test from_degrees with rhythm abbreviations"""
        degrees = [1, 3, 5, 8]
        melody = Melody.from_degrees(self.c_major_scale, degrees, rhythms="q q h w")

        self.assertEqual(melody[0].duration, 480)  # q = quarter
        self.assertEqual(melody[1].duration, 480)  # q = quarter
        self.assertEqual(melody[2].duration, 960)  # h = half
        self.assertEqual(melody[3].duration, 1920)  # w = whole

    def test_from_degrees_with_dotted_rhythms(self):
        """Test from_degrees with dotted rhythms"""
        degrees = [1, 3]
        melody = Melody.from_degrees(self.c_major_scale, degrees, rhythms="dq de")

        self.assertEqual(melody[0].duration, 720)  # Dotted quarter
        self.assertEqual(melody[1].duration, 360)  # Dotted eighth

    def test_from_degrees_zero_raises_error(self):
        """Test that degree 0 raises an error (degrees are 1-based)"""
        with self.assertRaises(ValueError):
            Melody.from_degrees(self.c_major_scale, [0, 1, 2])

    def test_from_degrees_invalid_rhythm(self):
        """Test from_degrees with invalid rhythm"""
        with self.assertRaises(ValueError):
            Melody.from_degrees(self.c_major_scale, [1, 3], rhythms="invalid quarter")

    def test_random_walk(self):
        """Test random walk melody generation"""
        melody = Melody.random_walk(
            start_pitch=60,
            length=10,
            scale=self.c_major_scale,
            max_interval=3,
            seed=42  # For reproducibility
        )

        self.assertEqual(len(melody), 10)
        self.assertEqual(melody[0].pitch, 60)  # Starts at specified pitch

        # All pitches should be in the scale
        for note in melody.get_notes():
            self.assertIn(note.pitch, self.c_major_scale)

    def test_random_walk_invalid_start(self):
        """Test random walk with invalid start pitch"""
        with self.assertRaises(ValueError):
            Melody.random_walk(
                start_pitch=61,  # Not in C major scale
                length=5,
                scale=self.c_major_scale
            )

    def test_transpose_up(self):
        """Test transposing melody up"""
        melody = Melody.from_note_names("C4 E4 G4")
        transposed = melody.transpose(2)  # Up 2 semitones

        self.assertEqual(transposed[0].pitch, 62)  # D4
        self.assertEqual(transposed[1].pitch, 66)  # F#4
        self.assertEqual(transposed[2].pitch, 69)  # A4

    def test_transpose_down(self):
        """Test transposing melody down"""
        melody = Melody.from_note_names("C4 E4 G4")
        transposed = melody.transpose(-3)  # Down 3 semitones

        self.assertEqual(transposed[0].pitch, 57)  # A3
        self.assertEqual(transposed[1].pitch, 61)  # C#4
        self.assertEqual(transposed[2].pitch, 64)  # E4

    def test_transpose_out_of_range(self):
        """Test transpose that goes out of MIDI range"""
        melody = Melody.from_note_names("C4 E4 G4")
        with self.assertRaises(ValueError):
            melody.transpose(100)  # Would exceed 127

    def test_reverse(self):
        """Test reversing (retrograde) melody"""
        melody = Melody.from_note_names("C4 E4 G4 C5")
        reversed_melody = melody.reverse()

        self.assertEqual(len(reversed_melody), 4)
        self.assertEqual(reversed_melody[0].pitch, KEY_MAP["C5"])
        self.assertEqual(reversed_melody[1].pitch, KEY_MAP["G4"])
        self.assertEqual(reversed_melody[2].pitch, KEY_MAP["E4"])
        self.assertEqual(reversed_melody[3].pitch, KEY_MAP["C4"])

    def test_reverse_maintains_durations(self):
        """Test that reverse maintains note durations"""
        durations = [480, 240, 960, 120]
        melody = Melody.from_note_names("C4 E4 G4 C5", durations=durations)
        reversed_melody = melody.reverse()

        # Durations should be reversed
        self.assertEqual(reversed_melody[0].duration, 120)
        self.assertEqual(reversed_melody[1].duration, 960)
        self.assertEqual(reversed_melody[2].duration, 240)
        self.assertEqual(reversed_melody[3].duration, 480)

    def test_melody_length(self):
        """Test melody length operator"""
        melody = Melody.from_note_names("C4 E4 G4 C5 E5")
        self.assertEqual(len(melody), 5)

    def test_melody_indexing(self):
        """Test melody indexing operator"""
        melody = Melody.from_note_names("C4 E4 G4")
        self.assertEqual(melody[0].pitch, KEY_MAP["C4"])
        self.assertEqual(melody[1].pitch, KEY_MAP["E4"])
        self.assertEqual(melody[2].pitch, KEY_MAP["G4"])
        self.assertEqual(melody[-1].pitch, KEY_MAP["G4"])

    def test_melody_str_repr(self):
        """Test melody string representations"""
        melody = Melody.from_note_names("C4 E4 G4")
        self.assertEqual(str(melody), "Melody(3 notes)")
        self.assertIn("Melody(notes=", repr(melody))
