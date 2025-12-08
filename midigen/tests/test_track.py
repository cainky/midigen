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

        # Notes are stored internally and compiled to MIDI messages
        self.assertEqual(len(self.track.notes), 1, "Should have one note stored")

        # Verify the note appears in compiled output
        compiled = self.track.compile()
        note_on_msgs = [
            msg
            for msg in compiled
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

        # Verify notes are stored
        self.assertEqual(len(self.track.notes), 3, "Should have 3 notes stored")

        # Verify compiled output has correct messages
        compiled = self.track.compile()
        note_on_msgs = [msg for msg in compiled if msg.type == "note_on"]

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

        # Verify notes are stored
        self.assertEqual(len(self.track.notes), 3, "Should have 3 notes stored")

        # Verify compiled output
        compiled = self.track.compile()
        note_on_msgs = [msg for msg in compiled if msg.type == "note_on"]

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
        """Test that chord notes have correct delta timing (simultaneous notes)."""
        # Create notes for a C major chord - all at time 0
        note_c = Note(pitch=KEY_MAP["C4"], velocity=64, duration=480, time=0)
        note_e = Note(pitch=KEY_MAP["E4"], velocity=64, duration=480, time=0)
        note_g = Note(pitch=KEY_MAP["G4"], velocity=64, duration=480, time=0)

        # Create a chord and add it to the track
        c_major_chord = Chord([note_c, note_e, note_g])
        self.track.add_chord(c_major_chord)

        # Compile to get proper delta-timed messages
        compiled = self.track.compile()

        # Filter out metadata messages, keep only note messages
        note_msgs = [msg for msg in compiled if msg.type in ("note_on", "note_off")]

        # For simultaneous notes (all at time 0), the first note_on has delta 0,
        # and subsequent note_on messages also have delta 0 (no time elapsed)
        note_on_msgs = [msg for msg in note_msgs if msg.type == "note_on"]

        self.assertEqual(len(note_on_msgs), 3, "Should have 3 note_on messages")

        # First note_on at delta 0
        self.assertEqual(
            note_on_msgs[0].time,
            0,
            f"First note_on should have delta time 0, got {note_on_msgs[0].time}",
        )

        # All subsequent note_on messages should also have delta 0 (simultaneous)
        for i, msg in enumerate(note_on_msgs[1:], start=1):
            self.assertEqual(
                msg.time,
                0,
                f"Note_on {i} should have delta time 0 (simultaneous), got {msg.time}",
            )

    def test_delta_timing_sequential_notes(self):
        """Test that sequential notes have correct delta timing."""
        # Create notes at different times
        note1 = Note(pitch=KEY_MAP["C4"], velocity=64, duration=240, time=0)
        note2 = Note(pitch=KEY_MAP["E4"], velocity=64, duration=240, time=480)
        note3 = Note(pitch=KEY_MAP["G4"], velocity=64, duration=240, time=960)

        self.track.add_note(note1)
        self.track.add_note(note2)
        self.track.add_note(note3)

        compiled = self.track.compile()
        note_msgs = [msg for msg in compiled if msg.type in ("note_on", "note_off")]

        # Expected sequence (sorted by absolute time, note_on before note_off):
        # t=0: note_on C4 (delta=0)
        # t=240: note_off C4 (delta=240)
        # t=480: note_on E4 (delta=240)
        # t=720: note_off E4 (delta=240)
        # t=960: note_on G4 (delta=240)
        # t=1200: note_off G4 (delta=240)

        expected_deltas = [0, 240, 240, 240, 240, 240]
        actual_deltas = [msg.time for msg in note_msgs]

        self.assertEqual(
            actual_deltas,
            expected_deltas,
            f"Delta times should be {expected_deltas}, got {actual_deltas}",
        )


if __name__ == "__main__":
    unittest.main()
