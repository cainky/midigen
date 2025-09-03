from midigen.midigen import MidiGen
from midigen.note import Note
from midigen.key import KEY_MAP
from midigen.chord import Chord, Arpeggio
from midigen.track import MAX_MIDI_TICKS
import unittest


class TestTrack(unittest.TestCase):
    def setUp(self):
        self.midi_gen = MidiGen()
        self.track = self.midi_gen.get_active_track()

    def test_add_note(self):
        new_note = Note(KEY_MAP["C4"], 64, 127, 0)
        self.track.add_note(new_note)
        messages = self.track.get_track()
        note_on_msgs = [
            msg
            for msg in messages
            if msg.type == "note_on" and msg.note == new_note.pitch
        ]

        self.assertEqual(len(note_on_msgs), 1, "Should have one note_on message")
        self.assertEqual(
            note_on_msgs[0].velocity, new_note.velocity, "Velocity should match"
        )

    def test_add_chord(self):
        new_note = Note(KEY_MAP["C4"], velocity=64, duration=120, time=0)
        chord = Chord([new_note, new_note + 4, new_note + 7])  # Simple C major triad
        self.track.add_chord(chord)
        messages = self.track.get_track()

        note_on_msgs = [msg for msg in messages if msg.type == "note_on"]

        # Assuming 3 notes in the chord, each with a note_on and note_off
        self.assertEqual(
            len(note_on_msgs), 3, "Should have 3 note_on messages for the chord"
        )

    def test_add_arpeggio(self):
        notes = [
            Note(KEY_MAP["C4"], 64, 100, 0),
            Note(KEY_MAP["E4"], 64, 100, 100),
            Note(KEY_MAP["G4"], 64, 100, 200),
        ]
        arpeggio = Arpeggio(notes)
        self.track.add_arpeggio(arpeggio)
        messages = self.track.get_track()

        note_on_msgs = [msg for msg in messages if msg.type == "note_on"]

        self.assertEqual(
            len(note_on_msgs), 3, "Should have 3 note_on messages for the arpeggio"
        )

    def test_quantize(self):
        time_value = 123
        quantization_value = 128
        quantized_value = self.track.quantize(time_value, quantization_value)
        self.assertEqual(quantized_value, 128)

    def test_quantize_edge_cases(self):
        # Test that the quantization value doesn't exceed the maximum MIDI ticks
        time_value = 5000
        quantization_value = MAX_MIDI_TICKS + 1
        with self.assertRaises(ValueError):
            self.track.quantize(time_value, quantization_value)

        # Test for negative time_value and quantization_value
        time_value = -50
        quantization_value = -128
        with self.assertRaises(ValueError):
            self.track.quantize(time_value, quantization_value)

    def test_add_program_change(self):
        self.track.add_program_change(channel=0, program=42)
        program_change_msgs = [
            msg for msg in self.track.get_track() if msg.type == "program_change"
        ]
        self.assertEqual(len(program_change_msgs), 1)
        self.assertEqual(program_change_msgs[0].program, 42)

    def test_add_control_change(self):
        self.track.add_control_change(channel=0, control=1, value=64)
        control_change_msgs = [
            msg for msg in self.track.get_track() if msg.type == "control_change"
        ]
        self.assertEqual(len(control_change_msgs), 1)
        self.assertEqual(control_change_msgs[0].value, 64)

    def test_add_pitch_bend(self):
        self.track.add_pitch_bend(channel=0, value=8191)
        pitch_bend_msgs = [
            msg for msg in self.track.get_track() if msg.type == "pitchwheel"
        ]
        self.assertEqual(len(pitch_bend_msgs), 1)
        self.assertEqual(pitch_bend_msgs[0].pitch, 8191)

    def test_invalid_control_change(self):
        with self.assertRaises(ValueError):
            self.track.add_control_change(channel=-1, control=0, value=64)

        with self.assertRaises(ValueError):
            self.track.add_control_change(channel=16, control=0, value=64)

        with self.assertRaises(ValueError):
            self.track.add_control_change(channel=0, control=-1, value=64)

        with self.assertRaises(ValueError):
            self.track.add_control_change(channel=0, control=120, value=64)

        with self.assertRaises(ValueError):
            self.track.add_control_change(channel=0, control=0, value=-1)

        with self.assertRaises(ValueError):
            self.track.add_control_change(channel=0, control=0, value=128)

    def test_invalid_pitch_bend(self):
        with self.assertRaises(ValueError):
            self.track.add_pitch_bend(channel=-1, value=8192)

        with self.assertRaises(ValueError):
            self.track.add_pitch_bend(channel=16, value=8192)

        with self.assertRaises(ValueError):
            self.track.add_pitch_bend(channel=0, value=-8193)

        with self.assertRaises(ValueError):
            self.track.add_pitch_bend(channel=0, value=8193)

    def test_chord_notes_start_simultaneously(self):
        # Create notes for a C major chord
        note_c = Note(pitch=KEY_MAP["C4"], velocity=64, duration=480, time=0)
        note_e = Note(pitch=KEY_MAP["E4"], velocity=64, duration=480, time=0)
        note_g = Note(pitch=KEY_MAP["G4"], velocity=64, duration=480, time=0)

        # Create a chord and add it to the track
        c_major_chord = Chord([note_c, note_e, note_g])
        self.track.add_chord(c_major_chord)

        messages = self.track.get_track()[3:]

        # Test that the first note_on starts at its specified time (which should be 0) and subsequent ones immediately after
        first_note_on_time = messages[0].time
        self.assertEqual(
            first_note_on_time,
            0,
            f"First note on should start at time 0 but started at {first_note_on_time}",
        )

        # All subsequent note_on messages should have a time of 0 if they are part of the same chord played simultaneously
        for i in range(
            2, len(messages), 2
        ):  # Every second message starting from the second note_on
            self.assertEqual(
                messages[i].time,
                0,
                f"Note on at index {i} did not start at expected time 0",
            )


if __name__ == "__main__":
    unittest.main()
