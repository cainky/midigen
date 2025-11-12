import os
from midigen.midigen import MidiGen
from midigen.note import Note
from mido import MidiFile
from midigen.key import Key
import unittest

from mido import bpm2tempo, Message


class TestMidigen(unittest.TestCase):
    def setUp(self):
        self.output_dir = os.path.join(os.getcwd(), "generate", "output")
        self.filename = os.path.join(self.output_dir, "test.mid")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.midi_gen = MidiGen()

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def create_note_on_message(self, note, time):
        return Message(
            f"note_on channel=0 note={note.pitch} velocity={note.velocity} time={time}"
        )

    def create_note_off_message(self, note, time):
        return Message(
            f"note_off channel=0 note={note.pitch} velocity={note.velocity} time={time}"
        )

    def test_midi_gen_creation(self):
        self.assertIsNotNone(self.midi_gen)

    def test_tracks(self):
        self.assertEqual(len(self.midi_gen.tracks), 1)

    def test_set_tempo(self):
        self.midi_gen.set_tempo(90)
        active_track = self.midi_gen.get_active_track()
        tempo_msgs = [
            msg for msg in active_track.get_track() if msg.type == "set_tempo"
        ]
        self.assertEqual(len(tempo_msgs), 1)
        expected_tempo = bpm2tempo(90)
        self.assertEqual(tempo_msgs[0].tempo, expected_tempo)

    def test_set_time_signature(self):
        self.midi_gen.set_time_signature(3, 4)
        active_track = self.midi_gen.get_active_track()
        time_sig_msgs = [
            msg for msg in active_track.get_track() if msg.type == "time_signature"
        ]
        self.assertEqual(len(time_sig_msgs), 1)
        self.assertEqual(time_sig_msgs[0].numerator, 3)
        self.assertEqual(time_sig_msgs[0].denominator, 4)

    def test_set_key_signature(self):
        key = Key("C#", "minor")  # Create a Key object
        self.midi_gen.set_key_signature(key)
        active_track = self.midi_gen.get_active_track()
        key_sig_msgs = [
            msg for msg in active_track.get_track() if msg.type == "key_signature"
        ]
        self.assertEqual(len(key_sig_msgs), 1)

        expected_key_str = (
            "C#m"  # Replace with the correct string representation for C# minor
        )
        self.assertEqual(key_sig_msgs[0].key, expected_key_str)

    def test_save(self):
        self.note = Note(pitch=60, velocity=64, duration=480, time=0)
        track = self.midi_gen.get_active_track()
        track.add_note(self.note)
        # Save the MIDI file with custom output directory
        filepath = self.midi_gen.save("test.mid", output_dir=self.output_dir)
        self.assertTrue(os.path.exists(filepath), "MIDI file was not created.")
        self.assertEqual(filepath, self.filename)

        # Load the saved MIDI file to check the messages
        midi_file = MidiFile(filepath)
        note_on_found = False
        note_off_found = False
        note_on_time = None
        note_off_time = None

        for msg in midi_file.tracks[0]:
            if (
                msg.type == "note_on"
                and msg.note == self.note.pitch
                and msg.velocity == self.note.velocity
            ):
                note_on_found = True
                note_on_time = msg.time  # Capture the time of the note_on message
            if msg.type == "note_off" and msg.note == self.note.pitch:
                note_off_found = True
                note_off_time = msg.time  # Capture the time of the note_off message

        self.assertTrue(note_on_found, "Note on message not found in the MIDI file.")
        self.assertTrue(note_off_found, "Note off message not found in the MIDI file.")

        # Check if the duration from note_on to note_off matches the note's duration
        if note_on_found and note_off_found:
            calculated_duration = note_off_time - note_on_time
            self.assertEqual(
                calculated_duration,
                self.note.duration,
                "The duration of the note does not match the expected value.",
            )

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

    def test_save_default_directory(self):
        """Test save to current directory (default behavior)"""
        self.note = Note(pitch=60, velocity=64, duration=480, time=0)
        track = self.midi_gen.get_active_track()
        track.add_note(self.note)

        # Save without specifying output_dir (should save to current directory)
        filepath = self.midi_gen.save("test_default.mid")
        self.assertTrue(os.path.exists(filepath), "MIDI file was not created in current directory.")

        # Cleanup
        if os.path.exists(filepath):
            os.remove(filepath)

    def test_save_error(self):
        with self.assertRaises(ValueError):
            self.midi_gen.save("")


if __name__ == "__main__":
    unittest.main()
