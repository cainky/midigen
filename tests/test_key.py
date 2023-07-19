from midigen.key import Key, VALID_KEYS
import unittest

class TestKey(unittest.TestCase):
    def test_repr(self):
        for note, mode in VALID_KEYS:
            key = Key(note, mode)
            self.assertEqual(repr(key), f"Key(name='{note}', mode='{mode}')")

    def test_key_creation(self):
        c_major = Key("C", "major")
        self.assertEqual(str(c_major), "C")

        a_minor = Key("A", "minor")
        self.assertEqual(str(a_minor), "Am")

    def test_invalid_key(self):
        with self.assertRaises(ValueError):
            Key("H", "major")

        with self.assertRaises(ValueError):
            Key("C", "moded")
