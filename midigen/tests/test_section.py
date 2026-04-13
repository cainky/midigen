import unittest
from midigen.composition.section import Section


class TestSectionValidation(unittest.TestCase):
    def test_valid_progressions(self):
        """Valid Roman numeral progressions parse without error."""
        Section("Verse", 4, "I-V-vi-IV")
        Section("Chorus", 8, "I")
        Section("Bridge", 2, "ii-V")
        Section("Intro", 4, "I-IV-V-I")
        Section("Minor", 4, "i-iv-v-i")
        Section("Seventh", 4, "V7-I")
        Section("Diminished", 4, "vii°")

    def test_empty_string_raises(self):
        with self.assertRaises(ValueError):
            Section("Bad", 4, "")

    def test_whitespace_only_raises(self):
        with self.assertRaises(ValueError):
            Section("Bad", 4, "   ")

    def test_double_dash_raises(self):
        with self.assertRaises(ValueError):
            Section("Bad", 4, "I--V")

    def test_trailing_dash_raises(self):
        with self.assertRaises(ValueError):
            Section("Bad", 4, "I-V-")

    def test_leading_dash_raises(self):
        with self.assertRaises(ValueError):
            Section("Bad", 4, "-I-V")

    def test_invalid_numeral_raises(self):
        with self.assertRaises(ValueError):
            Section("Bad", 4, "I-garbage-IV")

    def test_error_message_includes_progression(self):
        try:
            Section("Bad", 4, "I-xyz-IV")
            self.fail("Should have raised ValueError")
        except ValueError as e:
            self.assertIn("I-xyz-IV", str(e))
            self.assertIn("xyz", str(e))
