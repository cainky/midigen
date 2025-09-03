import unittest
from midigen.track import Track
from midigen.note import Note
from midigen.chord import Chord
from midigen.key import Key, KEY_MAP

class TestTrack(unittest.TestCase):

    def setUp(self):
        self.track = Track()
        self.key = Key("C", "major")

    def test_add_note(self):
        note = Note(pitch=60, velocity=100, time=0, duration=480)
        self.track.add_note(note)
        self.assertEqual(len(self.track.events), 2)
        note_on = self.track.events[0]
        self.assertEqual(note_on['type'], 'note_on')
        note_off = self.track.events[1]
        self.assertEqual(note_off['type'], 'note_off')
        self.assertEqual(note_off['time'], 480)

    def test_add_chord(self):
        c_major = Chord([
            Note(KEY_MAP["C4"], 100, 480, 0),
            Note(KEY_MAP["E4"], 100, 480, 0),
            Note(KEY_MAP["G4"], 100, 480, 0),
        ])
        self.track.add_chord(c_major)
        self.assertEqual(len(self.track.events), 6)
        note_off_events = [e for e in self.track.events if e['type'] == 'note_off']
        self.assertTrue(all(e['time'] == 480 for e in note_off_events))

    def test_compile_track_timing(self):
        self.track.add_note(Note(pitch=60, velocity=100, time=0, duration=480))
        self.track.add_note(Note(pitch=67, velocity=100, time=480, duration=480))

        compiled_track = self.track.compile(
            channel=0,
            tempo=120,
            time_signature=(4, 4),
            key_signature=self.key
        )

        note_events = [m for m in compiled_track if m.type in ['note_on', 'note_off']]
        self.assertEqual(len(note_events), 4)

        # msg[4] is note_on C (t=0, dt=0)
        self.assertEqual(compiled_track[4].type, 'note_on')
        self.assertEqual(compiled_track[4].note, 60)
        self.assertEqual(compiled_track[4].time, 0)

        # msg[5] is note_off C (t=480, dt=480)
        self.assertEqual(compiled_track[5].type, 'note_off')
        self.assertEqual(compiled_track[5].note, 60)
        self.assertEqual(compiled_track[5].time, 480)

        # msg[6] is note_on G (t=480, dt=0)
        self.assertEqual(compiled_track[6].type, 'note_on')
        self.assertEqual(compiled_track[6].note, 67)
        self.assertEqual(compiled_track[6].time, 0)

        # msg[7] is note_off G (t=960, dt=480)
        self.assertEqual(compiled_track[7].type, 'note_off')
        self.assertEqual(compiled_track[7].note, 67)
        self.assertEqual(compiled_track[7].time, 480)

if __name__ == '__main__':
    unittest.main()
