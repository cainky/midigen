from midigen.scale import Scale
from midigen.key import KEY_MAP
import unittest


class TestScale(unittest.TestCase):
    def test_generate_major_scale(self):
        root = KEY_MAP["C4"]
        c_major = Scale.major(root)
        expected_scale = [root]
        for interval in Scale.MAJOR_INTERVALS:
            expected_scale.append(expected_scale[-1] + interval)
        self.assertEqual(c_major, expected_scale)

    def test_generate_minor_scale(self):
        root = KEY_MAP["A4"]
        a_minor = Scale.minor(root)
        expected_scale = [root]
        for interval in Scale.MINOR_INTERVALS:
            expected_scale.append(expected_scale[-1] + interval)
        self.assertEqual(a_minor, expected_scale)

    def test_invalid_root_major_scale(self):
        invalid_root = -1  # an invalid MIDI note number
        with self.assertRaises(ValueError):
            Scale.major(invalid_root)

    def test_invalid_root_minor_scale(self):
        invalid_root = -1  # an invalid MIDI note number
        with self.assertRaises(ValueError):
            Scale.minor(invalid_root)

    def test_all_valid_roots_major_scale(self):
        for root in range(0, 128):  # All possible MIDI note numbers
            try:
                Scale.major(root)  # If this fails, it will raise an error
            except ValueError:
                self.fail(
                    f"Unexpected error when generating a major scale with root {root}"
                )

    def test_all_valid_roots_minor_scale(self):
        for root in range(0, 128):  # All possible MIDI note numbers
            try:
                Scale.minor(root)  # If this fails, it will raise an error
            except ValueError:
                self.fail(
                    f"Unexpected error when generating a minor scale with root {root}"
                )

    # ===== Pentatonic Scale Tests =====

    def test_major_pentatonic_scale(self):
        """Test major pentatonic scale generation"""
        root = KEY_MAP["C4"]
        scale = Scale.major_pentatonic(root)
        # C major pentatonic: C D E G A (C)
        self.assertEqual(len(scale), 6)  # 5 intervals + root
        self.assertEqual(scale[0], root)

    def test_minor_pentatonic_scale(self):
        """Test minor pentatonic scale generation"""
        root = KEY_MAP["A4"]
        scale = Scale.minor_pentatonic(root)
        # A minor pentatonic: A C D E G (A)
        self.assertEqual(len(scale), 6)  # 5 intervals + root
        self.assertEqual(scale[0], root)

    # ===== Blues Scale Test =====

    def test_blues_scale(self):
        """Test blues scale generation"""
        root = KEY_MAP["C4"]
        scale = Scale.blues(root)
        # C blues: C Eb F F# G Bb (C)
        self.assertEqual(len(scale), 7)  # 6 intervals + root
        self.assertEqual(scale[0], root)

    # ===== Mode Tests =====

    def test_ionian_mode(self):
        """Test Ionian mode (same as major)"""
        root = KEY_MAP["C4"]
        ionian = Scale.ionian(root)
        major = Scale.major(root)
        self.assertEqual(ionian, major)

    def test_dorian_mode(self):
        """Test Dorian mode"""
        root = KEY_MAP["D4"]
        scale = Scale.dorian(root)
        self.assertEqual(len(scale), 8)
        self.assertEqual(scale[0], root)

    def test_phrygian_mode(self):
        """Test Phrygian mode"""
        root = KEY_MAP["E4"]
        scale = Scale.phrygian(root)
        self.assertEqual(len(scale), 8)
        self.assertEqual(scale[0], root)

    def test_lydian_mode(self):
        """Test Lydian mode"""
        root = KEY_MAP["F4"]
        scale = Scale.lydian(root)
        self.assertEqual(len(scale), 8)
        self.assertEqual(scale[0], root)

    def test_mixolydian_mode(self):
        """Test Mixolydian mode"""
        root = KEY_MAP["G4"]
        scale = Scale.mixolydian(root)
        self.assertEqual(len(scale), 8)
        self.assertEqual(scale[0], root)

    def test_aeolian_mode(self):
        """Test Aeolian mode (same as natural minor)"""
        root = KEY_MAP["A4"]
        aeolian = Scale.aeolian(root)
        minor = Scale.minor(root)
        self.assertEqual(aeolian, minor)

    def test_locrian_mode(self):
        """Test Locrian mode"""
        root = KEY_MAP["B4"]
        scale = Scale.locrian(root)
        self.assertEqual(len(scale), 8)
        self.assertEqual(scale[0], root)

    # ===== Other Scale Tests =====

    def test_harmonic_minor_scale(self):
        """Test harmonic minor scale"""
        root = KEY_MAP["A4"]
        scale = Scale.harmonic_minor(root)
        self.assertEqual(len(scale), 8)
        self.assertEqual(scale[0], root)

    def test_melodic_minor_scale(self):
        """Test melodic minor scale"""
        root = KEY_MAP["A4"]
        scale = Scale.melodic_minor(root)
        self.assertEqual(len(scale), 8)
        self.assertEqual(scale[0], root)

    def test_whole_tone_scale(self):
        """Test whole tone scale"""
        root = KEY_MAP["C4"]
        scale = Scale.whole_tone(root)
        # Whole tone has 6 notes + octave
        self.assertEqual(len(scale), 7)
        self.assertEqual(scale[0], root)
        # All intervals should be 2 semitones (whole steps)
        for i in range(len(scale) - 1):
            self.assertEqual(scale[i+1] - scale[i], 2)

    def test_chromatic_scale(self):
        """Test chromatic scale"""
        root = KEY_MAP["C4"]
        scale = Scale.chromatic(root)
        # Chromatic has 12 notes + octave
        self.assertEqual(len(scale), 13)
        self.assertEqual(scale[0], root)
        # All intervals should be 1 semitone (half steps)
        for i in range(len(scale) - 1):
            self.assertEqual(scale[i+1] - scale[i], 1)

    def test_scale_boundary_check(self):
        """Test that scales stop at MIDI limit (127)"""
        root = 120  # High root note
        scale = Scale.major(root)
        # Should stop before exceeding 127
        for note in scale:
            self.assertLessEqual(note, 127)
