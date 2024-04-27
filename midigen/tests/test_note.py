from midigen.note import Note
from midigen.key import KEY_MAP
import unittest


class TestNote(unittest.TestCase):
    def setUp(self):
        self.note = Note(KEY_MAP["C4"], 64, 100, 0)

    def test_note_creation(self):
        self.assertEqual(self.note.pitch, KEY_MAP["C4"])
        self.assertEqual(self.note.velocity, 64)
        self.assertEqual(self.note.duration, 100)
        self.assertEqual(self.note.time, 0)

    def test_note_addition(self):
        note_sum = self.note + 5
        self.assertEqual(note_sum.pitch, 65)
        self.assertEqual(note_sum.velocity, 64)
        self.assertEqual(note_sum.duration, 100)
        self.assertEqual(note_sum.time, 0)

    def test_invalid_note_value(self):
        with self.assertRaises(ValueError):
            Note(-1, 64, 100, 0)
        with self.assertRaises(ValueError):
            Note(128, 64, 100, 0)


if __name__ == "__main__":
    unittest.main()
