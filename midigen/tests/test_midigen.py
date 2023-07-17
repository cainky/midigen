import os
from ..midigen.midigen import MidiGen, MAX_MIDI_TICKS
import unittest

from mido import bpm2tempo, Message


class TestMidigen(unittest.TestCase):
    def setUp(self):
        self.midi_gen = MidiGen()

    def test_midi_gen_creation(self):
        self.assertIsNotNone(self.midi_gen)

    def test_set_tempo(self):
        self.midi_gen.set_tempo(90)
        tempo_msgs = [msg for msg in self.midi_gen._track if msg.type == "set_tempo"]
        self.assertEqual(len(tempo_msgs), 1)
        tempo_msg = tempo_msgs[0]
        self.assertEqual(tempo_msg.type, "set_tempo")
        self.assertEqual(tempo_msg.tempo, bpm2tempo(90))

    def test_set_time_signature(self):
        self.midi_gen.set_time_signature(3, 4)
        time_sig_msgs = [
            msg for msg in self.midi_gen._track if msg.type == "time_signature"
        ]
        self.assertEqual(len(time_sig_msgs), 1)
        time_sig_msg = time_sig_msgs[0]
        self.assertEqual(time_sig_msg.type, "time_signature")
        self.assertEqual(time_sig_msg.numerator, 3)
        self.assertEqual(time_sig_msg.denominator, 4)

    def test_set_key_signature(self):
        new_key = "C#m"
        self.midi_gen.set_key_signature(new_key)
        key_sig_msg = self.midi_gen.track[3]
        self.assertEqual(key_sig_msg.type, "key_signature")
        self.assertEqual(key_sig_msg.key, new_key)

    def test_add_program_change(self):
        self.midi_gen.add_program_change(channel=0, program=0)
        program_change_msg = self.midi_gen.track[3]
        self.assertEqual(program_change_msg.type, "program_change")
        self.assertEqual(program_change_msg.channel, 0)
        self.assertEqual(program_change_msg.program, 0)

    def test_add_note(self):
        self.midi_gen.add_note(60, 64, 500)
        note_on_msg = self.midi_gen.track[3]
        note_off_msg = self.midi_gen.track[4]
        self.assertEqual(note_on_msg.type, "note_on")
        self.assertEqual(note_on_msg.note, 60)
        self.assertEqual(note_off_msg.type, "note_off")
        self.assertEqual(note_off_msg.note, 60)
        self.assertEqual(len(self.midi_gen.track), 5)

    def test_add_chord(self):
        self.midi_gen.add_chord([60, 64, 67], 64, 500)
        messages = self.midi_gen.track[3:9]
        self.assertTrue(all(msg.type == "note_on" for msg in messages[::2]))
        self.assertTrue(all(msg.type == "note_off" for msg in messages[1::2]))

    def test_add_arpeggio(self):
        self.midi_gen.add_arpeggio([60, 64, 67], 64, 500, 125)
        messages = self.midi_gen.track[3:9]
        self.assertTrue(all(msg.type == "note_on" for msg in messages[::2]))
        self.assertTrue(all(msg.type == "note_off" for msg in messages[1::2]))

    def test_quantize(self):
        time_value = 123
        quantization_value = 128
        quantized_value = self.midi_gen.quantize(time_value, quantization_value)
        self.assertEqual(quantized_value, 128)

    def test_save_and_load(self):
        self.midi_gen.save("test.mid")
        loaded_midi_file = self.midi_gen.load_midi_file("test.mid")
        self.assertEqual(loaded_midi_file, self.midi_gen.midi_file)
        os.remove("test.mid")

    def test_add_control_change(self):
        self.midi_gen.add_control_change(channel=0, control=1, value=64)
        control_change_msg = self.midi_gen.track[3]
        self.assertEqual(control_change_msg.type, "control_change")
        self.assertEqual(control_change_msg.channel, 0)
        self.assertEqual(control_change_msg.control, 1)
        self.assertEqual(control_change_msg.value, 64)

    def add_pitch_bend(self, channel=0, value=8192, time=0):
        self._track.append(
            Message("pitchwheel", channel=channel, pitch=value, time=time)
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

    def test_invalid_note_value(self):
        with self.assertRaises(ValueError):
            self.midi_gen.add_note(-1, 64, 500)

        with self.assertRaises(ValueError):
            self.midi_gen.add_note(128, 64, 500)

    def test_add_pitch_bend(self):
        self.midi_gen.add_pitch_bend(channel=0, value=8191, time=0)
        pitch_bend_msg = self.midi_gen.track[3]
        self.assertEqual(pitch_bend_msg.type, "pitchwheel")
        self.assertEqual(pitch_bend_msg.channel, 0)
        self.assertEqual(pitch_bend_msg.pitch, 8191)
        self.assertEqual(pitch_bend_msg.time, 0)


    def test_quantize_edge_cases(self):
        # Test that the quantization value doesn't exceed the maximum MIDI ticks
        time_value = 5000
        quantization_value = MAX_MIDI_TICKS + 1
        with self.assertRaises(ValueError):
            self.midi_gen.quantize(time_value, quantization_value)

        # Test for negative time_value and quantization_value
        time_value = -50
        quantization_value = -128
        with self.assertRaises(ValueError):
            self.midi_gen.quantize(time_value, quantization_value)


if __name__ == '__main__':
    unittest.main()