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

    def test_key_equality(self):
        c_major_1 = Key("C", "major")
        c_major_2 = Key("C", "major")
        self.assertEqual(c_major_1, c_major_2)

        a_minor_1 = Key("A", "minor")
        a_minor_2 = Key("A", "minor")
        self.assertEqual(a_minor_1, a_minor_2)

    def test_key_inequality(self):
        c_major = Key("C", "major")
        a_minor = Key("A", "minor")
        self.assertNotEqual(c_major, a_minor)

    def test_all_valid_keys(self):
        for note, mode in VALID_KEYS:
            key = Key(note, mode)
            self.assertEqual(key.name, note)
            self.assertEqual(key.mode, mode)
