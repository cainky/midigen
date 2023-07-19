from midigen.key import Key
import unittest

class TestKey(unittest.TestCase):
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
