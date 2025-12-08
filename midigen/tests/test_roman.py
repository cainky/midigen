"""
Unit tests for the native Roman numeral parser.

Tests parsing of Roman numerals (I, ii, V7, vii°, etc.) and
chord pitch generation to ensure compatibility with the original
music21-based implementation.
"""

import unittest
from midigen.roman import (
    parse_roman_numeral,
    get_root_pitch,
    get_chord_pitches,
    get_note_names_for_pitches,
    ChordQuality,
    ParsedRomanNumeral,
    MAJOR_SCALE_SEMITONES,
    MINOR_SCALE_SEMITONES,
)


class TestParseRomanNumeral(unittest.TestCase):
    """Tests for parse_roman_numeral function."""

    def test_parse_major_numerals(self):
        """Test parsing uppercase (major) Roman numerals."""
        cases = [
            ("I", 1, ChordQuality.MAJOR, True),
            ("II", 2, ChordQuality.MAJOR, True),
            ("III", 3, ChordQuality.MAJOR, True),
            ("IV", 4, ChordQuality.MAJOR, True),
            ("V", 5, ChordQuality.MAJOR, True),
            ("VI", 6, ChordQuality.MAJOR, True),
            ("VII", 7, ChordQuality.MAJOR, True),
        ]
        for numeral, expected_degree, expected_quality, expected_uppercase in cases:
            with self.subTest(numeral=numeral):
                parsed = parse_roman_numeral(numeral)
                self.assertEqual(parsed.degree, expected_degree)
                self.assertEqual(parsed.quality, expected_quality)
                self.assertTrue(parsed.is_uppercase)

    def test_parse_minor_numerals(self):
        """Test parsing lowercase (minor) Roman numerals."""
        cases = [
            ("i", 1, ChordQuality.MINOR),
            ("ii", 2, ChordQuality.MINOR),
            ("iii", 3, ChordQuality.MINOR),
            ("iv", 4, ChordQuality.MINOR),
            ("v", 5, ChordQuality.MINOR),
            ("vi", 6, ChordQuality.MINOR),
            ("vii", 7, ChordQuality.MINOR),
        ]
        for numeral, expected_degree, expected_quality in cases:
            with self.subTest(numeral=numeral):
                parsed = parse_roman_numeral(numeral)
                self.assertEqual(parsed.degree, expected_degree)
                self.assertEqual(parsed.quality, expected_quality)
                self.assertFalse(parsed.is_uppercase)

    def test_parse_seventh_chords(self):
        """Test parsing seventh chord notations."""
        # Dominant 7 (uppercase + 7)
        parsed = parse_roman_numeral("V7")
        self.assertEqual(parsed.degree, 5)
        self.assertEqual(parsed.quality, ChordQuality.DOMINANT_7)

        parsed = parse_roman_numeral("I7")
        self.assertEqual(parsed.degree, 1)
        self.assertEqual(parsed.quality, ChordQuality.DOMINANT_7)

        # Minor 7 (lowercase + 7)
        parsed = parse_roman_numeral("ii7")
        self.assertEqual(parsed.degree, 2)
        self.assertEqual(parsed.quality, ChordQuality.MINOR_7)

        parsed = parse_roman_numeral("vi7")
        self.assertEqual(parsed.degree, 6)
        self.assertEqual(parsed.quality, ChordQuality.MINOR_7)

    def test_parse_major_seventh(self):
        """Test parsing major seventh chord notations."""
        for notation in ["Imaj7", "IMAJ7"]:
            with self.subTest(notation=notation):
                parsed = parse_roman_numeral(notation)
                self.assertEqual(parsed.degree, 1)
                self.assertEqual(parsed.quality, ChordQuality.MAJOR_7)

    def test_parse_diminished(self):
        """Test parsing diminished chord notations."""
        for notation in ["vii°", "viio", "viidim"]:
            with self.subTest(notation=notation):
                parsed = parse_roman_numeral(notation)
                self.assertEqual(parsed.degree, 7)
                self.assertEqual(parsed.quality, ChordQuality.DIMINISHED)

    def test_parse_diminished_seventh(self):
        """Test parsing diminished seventh chord notations."""
        for notation in ["vii°7", "viio7", "viidim7"]:
            with self.subTest(notation=notation):
                parsed = parse_roman_numeral(notation)
                self.assertEqual(parsed.degree, 7)
                self.assertEqual(parsed.quality, ChordQuality.DIMINISHED_7)

    def test_parse_half_diminished(self):
        """Test parsing half-diminished chord notations."""
        for notation in ["viiø", "viiø7"]:
            with self.subTest(notation=notation):
                parsed = parse_roman_numeral(notation)
                self.assertEqual(parsed.degree, 7)
                self.assertEqual(parsed.quality, ChordQuality.HALF_DIMINISHED_7)

    def test_parse_augmented(self):
        """Test parsing augmented chord notations."""
        for notation in ["V+", "Vaug"]:
            with self.subTest(notation=notation):
                parsed = parse_roman_numeral(notation)
                self.assertEqual(parsed.degree, 5)
                self.assertEqual(parsed.quality, ChordQuality.AUGMENTED)

    def test_parse_accidentals(self):
        """Test parsing accidentals (sharps and flats)."""
        # Flat VII (borrowed chord)
        parsed = parse_roman_numeral("bVII")
        self.assertEqual(parsed.degree, 7)
        self.assertEqual(parsed.accidental, "b")
        self.assertEqual(parsed.quality, ChordQuality.MAJOR)

        # Sharp IV
        parsed = parse_roman_numeral("#IV")
        self.assertEqual(parsed.degree, 4)
        self.assertEqual(parsed.accidental, "#")

        # Unicode accidentals
        parsed = parse_roman_numeral("♭VII")
        self.assertEqual(parsed.accidental, "b")

        parsed = parse_roman_numeral("♯IV")
        self.assertEqual(parsed.accidental, "#")

    def test_parse_preserves_original(self):
        """Test that original string is preserved."""
        parsed = parse_roman_numeral("  V7  ")
        self.assertEqual(parsed.original, "  V7  ")

    def test_parse_empty_raises(self):
        """Test that empty string raises ValueError."""
        with self.assertRaises(ValueError):
            parse_roman_numeral("")
        with self.assertRaises(ValueError):
            parse_roman_numeral("   ")

    def test_parse_invalid_raises(self):
        """Test that invalid numeral raises ValueError."""
        with self.assertRaises(ValueError):
            parse_roman_numeral("X")  # Not a valid Roman numeral
        with self.assertRaises(ValueError):
            parse_roman_numeral("ABC")


class TestGetRootPitch(unittest.TestCase):
    """Tests for get_root_pitch function."""

    def test_c_major_scale_degrees(self):
        """Test root pitches for C major scale degrees."""
        # C major: C=0, D=2, E=4, F=5, G=7, A=9, B=11
        expected = {1: 0, 2: 2, 3: 4, 4: 5, 5: 7, 6: 9, 7: 11}
        for degree, expected_pitch in expected.items():
            with self.subTest(degree=degree):
                pitch = get_root_pitch("C", "major", degree)
                self.assertEqual(pitch, expected_pitch)

    def test_g_major_scale_degrees(self):
        """Test root pitches for G major scale degrees."""
        # G major: G=7, A=9, B=11, C=0, D=2, E=4, F#=6
        expected = {1: 7, 2: 9, 3: 11, 4: 0, 5: 2, 6: 4, 7: 6}
        for degree, expected_pitch in expected.items():
            with self.subTest(degree=degree):
                pitch = get_root_pitch("G", "major", degree)
                self.assertEqual(pitch, expected_pitch)

    def test_a_minor_scale_degrees(self):
        """Test root pitches for A minor scale degrees."""
        # A natural minor: A=9, B=11, C=0, D=2, E=4, F=5, G=7
        expected = {1: 9, 2: 11, 3: 0, 4: 2, 5: 4, 6: 5, 7: 7}
        for degree, expected_pitch in expected.items():
            with self.subTest(degree=degree):
                pitch = get_root_pitch("A", "minor", degree)
                self.assertEqual(pitch, expected_pitch)

    def test_key_with_accidentals(self):
        """Test keys with sharps and flats."""
        # F# major: F#=6
        pitch = get_root_pitch("F#", "major", 1)
        self.assertEqual(pitch, 6)

        # Bb major: Bb=10
        pitch = get_root_pitch("Bb", "major", 1)
        self.assertEqual(pitch, 10)

    def test_degree_with_accidentals(self):
        """Test degree accidentals (e.g., bVII)."""
        # C major, bVII = Bb = 10
        pitch = get_root_pitch("C", "major", 7, "b")
        self.assertEqual(pitch, 10)  # B(11) - 1 = 10

        # C major, #IV = F# = 6
        pitch = get_root_pitch("C", "major", 4, "#")
        self.assertEqual(pitch, 6)  # F(5) + 1 = 6


class TestGetChordPitches(unittest.TestCase):
    """Tests for get_chord_pitches function."""

    def test_c_major_triad(self):
        """Test C major chord (I in C major)."""
        pitches = get_chord_pitches("C", "major", "I", octave=4)
        # C4=60, E4=64, G4=67
        self.assertEqual(pitches, [60, 64, 67])

    def test_g_major_triad(self):
        """Test G major chord (V in C major)."""
        pitches = get_chord_pitches("C", "major", "V", octave=4)
        # G4=67, B4=71, D4=62 (note: D wraps within octave 4)
        self.assertEqual(pitches, [67, 71, 62])

    def test_a_minor_triad(self):
        """Test A minor chord (vi in C major)."""
        pitches = get_chord_pitches("C", "major", "vi", octave=4)
        # A4=69, C4=60, E4=64 (note: C and E wrap within octave 4)
        self.assertEqual(pitches, [69, 60, 64])

    def test_f_major_triad(self):
        """Test F major chord (IV in C major)."""
        pitches = get_chord_pitches("C", "major", "IV", octave=4)
        # F4=65, A4=69, C4=60 (note: C wraps within octave 4)
        self.assertEqual(pitches, [65, 69, 60])

    def test_classic_progression(self):
        """Test the classic I-V-vi-IV progression in C major."""
        progression = ["I", "V", "vi", "IV"]
        expected = [
            [60, 64, 67],  # C major: C, E, G
            [67, 71, 62],  # G major: G, B, D
            [69, 60, 64],  # A minor: A, C, E
            [65, 69, 60],  # F major: F, A, C
        ]
        for numeral, expected_pitches in zip(progression, expected):
            with self.subTest(numeral=numeral):
                pitches = get_chord_pitches("C", "major", numeral, octave=4)
                self.assertEqual(pitches, expected_pitches)

    def test_dominant_seventh(self):
        """Test dominant seventh chord (V7)."""
        pitches = get_chord_pitches("C", "major", "V7", octave=4)
        # G7: G, B, D, F = 67, 71, 62, 65
        self.assertEqual(len(pitches), 4)
        self.assertEqual(pitches[0], 67)  # G
        self.assertEqual(pitches[1], 71)  # B
        self.assertEqual(pitches[2], 62)  # D
        self.assertEqual(pitches[3], 65)  # F

    def test_minor_seventh(self):
        """Test minor seventh chord (ii7)."""
        pitches = get_chord_pitches("C", "major", "ii7", octave=4)
        # Dm7: D, F, A, C = 62, 65, 69, 60
        self.assertEqual(len(pitches), 4)
        self.assertEqual(pitches[0], 62)  # D
        self.assertEqual(pitches[1], 65)  # F
        self.assertEqual(pitches[2], 69)  # A
        self.assertEqual(pitches[3], 60)  # C

    def test_diminished_chord(self):
        """Test diminished chord (vii°)."""
        pitches = get_chord_pitches("C", "major", "vii°", octave=4)
        # B diminished: B, D, F = 71, 62, 65
        self.assertEqual(len(pitches), 3)
        self.assertEqual(pitches[0], 71)  # B
        self.assertEqual(pitches[1], 62)  # D
        self.assertEqual(pitches[2], 65)  # F

    def test_different_octaves(self):
        """Test chord generation in different octaves."""
        # Octave 3 (C3=48)
        pitches = get_chord_pitches("C", "major", "I", octave=3)
        self.assertEqual(pitches, [48, 52, 55])

        # Octave 5 (C5=72)
        pitches = get_chord_pitches("C", "major", "I", octave=5)
        self.assertEqual(pitches, [72, 76, 79])

    def test_minor_key(self):
        """Test chord generation in minor key."""
        # i chord in A minor (A minor triad)
        pitches = get_chord_pitches("A", "minor", "i", octave=4)
        # A4=69, C5=72 -> wraps to 60, E5=76 -> wraps to 64
        # Due to flat 3 in minor scale: A=69, C=60, E=64
        self.assertEqual(pitches[0], 69)  # A

    def test_g_major_key(self):
        """Test chords in G major key."""
        # I in G major = G major triad
        pitches = get_chord_pitches("G", "major", "I", octave=4)
        # G4=67, B4=71, D4=62
        self.assertEqual(pitches, [67, 71, 62])


class TestGetNoteNamesForPitches(unittest.TestCase):
    """Tests for get_note_names_for_pitches function."""

    def test_c_major_chord_names(self):
        """Test note name conversion for C major chord."""
        pitches = [60, 64, 67]
        names = get_note_names_for_pitches(pitches)
        self.assertEqual(names, ["C4", "E4", "G4"])

    def test_across_octaves(self):
        """Test note names across different octaves."""
        pitches = [48, 60, 72]  # C3, C4, C5
        names = get_note_names_for_pitches(pitches)
        self.assertEqual(names, ["C3", "C4", "C5"])

    def test_accidentals_as_sharps(self):
        """Test that accidentals are rendered as sharps."""
        pitches = [61, 63, 66, 68, 70]  # C#, D#, F#, G#, A#
        names = get_note_names_for_pitches(pitches)
        self.assertEqual(names[0], "C#4")
        self.assertEqual(names[1], "D#4")


class TestScaleSemitones(unittest.TestCase):
    """Tests for scale semitone constants."""

    def test_major_scale_intervals(self):
        """Test major scale has correct intervals (W-W-H-W-W-W-H)."""
        # Expected intervals from tonic: 0, 2, 4, 5, 7, 9, 11
        expected = {1: 0, 2: 2, 3: 4, 4: 5, 5: 7, 6: 9, 7: 11}
        self.assertEqual(MAJOR_SCALE_SEMITONES, expected)

    def test_minor_scale_intervals(self):
        """Test natural minor scale has correct intervals (W-H-W-W-H-W-W)."""
        # Expected intervals from tonic: 0, 2, 3, 5, 7, 8, 10
        expected = {1: 0, 2: 2, 3: 3, 4: 5, 5: 7, 6: 8, 7: 10}
        self.assertEqual(MINOR_SCALE_SEMITONES, expected)


if __name__ == "__main__":
    unittest.main()
