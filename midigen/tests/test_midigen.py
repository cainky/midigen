import os
from midigen.midigen import MidiGen
from midigen.key import Key
import unittest

from mido import bpm2tempo, Message


class TestMidigen(unittest.TestCase):
    def setUp(self):
        self.midi_gen = MidiGen()

    def create_note_on_message(self, note, time):
        return f'note_on channel=0 note={note.pitch} velocity={note.velocity} time={time}'

    def create_note_off_message(self, note, time):
        return f'note_off channel=0 note={note.pitch} velocity={note.velocity} time={time}'

    def test_midi_gen_creation(self):
        self.assertIsNotNone(self.midi_gen)

    def test_tracks(self):
        self.assertEqual(len(self.midi_gen.tracks), 1)

    def test_set_tempo(self):
        self.midi_gen.set_tempo(90)
        active_track = self.midi_gen.get_active_track()
        tempo_msgs = [msg for msg in active_track.get_track() if msg.type == "set_tempo"]
        self.assertEqual(len(tempo_msgs), 1)
        expected_tempo = bpm2tempo(90)
        self.assertEqual(tempo_msgs[0].tempo, expected_tempo)

    def test_set_time_signature(self):
        self.midi_gen.set_time_signature(3, 4)
        active_track = self.midi_gen.get_active_track()
        time_sig_msgs = [msg for msg in active_track.get_track() if msg.type == "time_signature"]
        self.assertEqual(len(time_sig_msgs), 1)
        self.assertEqual(time_sig_msgs[0].numerator, 3)
        self.assertEqual(time_sig_msgs[0].denominator, 4)

    def test_set_key_signature(self):
        key = Key("C#", "minor")  # Create a Key object
        self.midi_gen.set_key_signature(key)
        active_track = self.midi_gen.get_active_track()
        key_sig_msgs = [msg for msg in active_track.get_track() if msg.type == "key_signature"]
        self.assertEqual(len(key_sig_msgs), 1)

        expected_key_str = "C#m"  # Replace with the correct string representation for C# minor
        self.assertEqual(key_sig_msgs[0].key, expected_key_str)

    def test_save(self):
        self.midi_gen.save("test.mid")
        self.assertTrue(os.path.exists("test.mid"), "MIDI file was not created.")
        os.remove("test.mid")

    def test_invalid_tempo(self):
        with self.assertRaises(ValueError):
            self.midi_gen.set_tempo(-1)

    def test_invalid_time_signature(self):
        with self.assertRaises(ValueError):
            self.midi_gen.set_time_signature(0, 4)

        with self.assertRaises(ValueError):
            self.midi_gen.set_time_signature(4, 0)

    def test_invalid_key_signature(self):
        with self.assertRaises(ValueError):
            self.midi_gen.set_key_signature(0)

        with self.assertRaises(ValueError):
            self.midi_gen.set_key_signature("H")

    def test_invalid_program_change(self):
        active_track = self.midi_gen.get_active_track()
        with self.assertRaises(ValueError):
            active_track.add_program_change(channel=-1, program=0)

        with self.assertRaises(ValueError):
            active_track.add_program_change(channel=16, program=0)

        with self.assertRaises(ValueError):
            active_track.add_program_change(channel=0, program=-1)

        with self.assertRaises(ValueError):
            active_track.add_program_change(channel=0, program=128)

    def test_save_error(self):
        with self.assertRaises(ValueError):
            self.midi_gen.save("")



if __name__ == '__main__':
    unittest.main()
