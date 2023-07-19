from midigen.note import Note
from midigen.chord import Chord, Arpeggio, ArpeggioPattern
import unittest

class TestChord(unittest.TestCase):
    def setUp(self):
        root_note = Note(60, 64, 100, 0)
        self.chord = Chord(root_note)

    def test_chord_creation(self):
        self.assertEqual(self.chord.get_root(), Note(60, 64, 100, 0))

    def test_add_note(self):
        new_note = Note(62, 64, 100, 100)
        self.chord.add_note(new_note)
        self.assertEqual(self.chord.get_notes(), [Note(60, 64, 100, 0), new_note])

    def test_chord_triads(self):
        major_triad = self.chord.major_triad()
        self.assertEqual(major_triad, [Note(60, 64, 100, 0), Note(64, 64, 100, 0), Note(67, 64, 100, 0)])

        minor_triad = self.chord.minor_triad()
        self.assertEqual(minor_triad, [Note(60, 64, 100, 0), Note(63, 64, 100, 0), Note(67, 64, 100, 0)])


class TestArpeggio(unittest.TestCase):
    def setUp(self):
        root_note = Note(60, 64, 100, 0)
        self.notes = [Note(62, 64, 100, 100), Note(64, 64, 100, 200)]
        self.arpeggio = Arpeggio(root_note, self.notes, delay=100, pattern=ArpeggioPattern.ASCENDING, loops=1)

    def test_arpeggio_creation(self):
        self.assertEqual(self.arpeggio.get_root(), Note(60, 64, 100, 0))

    def test_get_sequential_notes(self):
        sequential_notes = self.arpeggio.get_sequential_notes()
        self.assertEqual(sequential_notes, [Note(60, 64, 100, 0), Note(62, 64, 100, 100), Note(64, 64, 100, 200)])
