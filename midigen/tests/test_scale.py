from midigen.scale import Scale
from midigen.key import KEY_MAP
import unittest

class TestScale(unittest.TestCase):
    def test_generate_major_scale(self):
        root = KEY_MAP["C"]
        c_major = Scale.major(root)
        expected_scale = [root]
        for interval in Scale.MAJOR_INTERVALS:
            expected_scale.append(expected_scale[-1] + interval)
        self.assertEqual(c_major, expected_scale)

    def test_generate_minor_scale(self):
        root = KEY_MAP["A"]
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
                self.fail(f"Unexpected error when generating a major scale with root {root}")

    def test_all_valid_roots_minor_scale(self):
        for root in range(0, 128):  # All possible MIDI note numbers
            try:
                Scale.minor(root)  # If this fails, it will raise an error
            except ValueError:
                self.fail(f"Unexpected error when generating a minor scale with root {root}")
