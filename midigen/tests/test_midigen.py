from midigen.midigen import MidiGen
from unittest import Testcase


class TestMidigen(TestCase):
    def setUp(self):
        self.midi_gen = MidiGen(tempo=120, time_signature=(4, 4), key_signature=0)

    def test_midi_gen_creation(self):
        self.assertIsNotNone(self.midi_gen)

    def test_set_tempo(self):
        self.midi_gen.set_tempo(90)
        tempo_msg = self.midi_gen.track[0]
        self.assertEqual(tempo_msg.type, 'set_tempo')
        self.assertEqual(tempo_msg.tempo, 666667)

    def test_set_time_signature(self):
        self.midi_gen.set_time_signature(3, 4)
        time_sig_msg = self.midi_gen.track[1]
        self.assertEqual(time_sig_msg.type, 'time_signature')
        self.assertEqual(time_sig_msg.numerator, 3)
        self.assertEqual(time_sig_msg.denominator, 4)

    def test_set_key_signature(self):
        self.midi_gen.set_key_signature(-3)
        key_sig_msg = self.midi_gen.track[2]
        self.assertEqual(key_sig_msg.type, 'key_signature')
        self.assertEqual(key_sig_msg.key, -3)

    def test_add_program_change(self):
        self.midi_gen.add_program_change(channel=0, program=0)
        program_change_msg = self.midi_gen.track[3]
        self.assertEqual(program_change_msg.type, 'program_change')
        self.assertEqual(program_change_msg.channel, 0)
        self.assertEqual(program_change_msg.program, 0)

    def test_add_note(self):
        self.midi_gen.add_note(60, 64, 500)
        note_on_msg = self.midi_gen.track[3]
        note_off_msg = self.midi_gen.track[4]
        self.assertEqual(note_on_msg.type, 'note_on')
        self.assertEqual(note_on_msg.note, 60)
        self.assertEqual(note_off_msg.type, 'note_off')
        self.assertEqual(note_off_msg.note, 60)

    def test_add_chord(self):
        self.midi_gen.add_chord([60, 64, 67], 64, 500)
        note_on_msgs = self.midi_gen.track[3:6]
        note_off_msgs = self.midi_gen.track[6:9]
        self.assertTrue(all(msg.type == 'note_on' for msg in note_on_msgs))
        self.assertTrue(all(msg.type == 'note_off' for msg in note_off_msgs))

    def test_add_arpeggio(self):
        self.midi_gen.add_arpeggio([60, 64, 67], 64, 500, 125)
        note_on_msgs = self.midi_gen.track[3:6]
        note_off_msgs = self.midi_gen.track[6:9]
        self.assertTrue(all(msg.type == 'note_on' for msg in note_on_msgs))
        self.assertTrue(all(msg.type == 'note_off' for msg in note_off_msgs))

    def test_quantize(self):
        time_value = 123
        quantization_value = 128
        quantized_value = self.midi_gen.quantize(time_value, quantization_value)
        self.assertEqual(quantized_value, 128)

    def test_save_and_load(self):
        self.midi_gen.add_program_change(channel=0, program=0)
        self.midi_gen.add_note(60, 64, 500)
        self.midi_gen.save('test_output.mid')

        loaded_midi_gen = MidiGen()
        loaded_midi_gen.load_midi_file('test_output.mid')
        self.assertEqual(len(loaded_midi_gen.track), len(self.midi_gen.track))

    def test_add_control_change(self):
        self.midi_gen.add_control_change(channel=0, control=1, value=64)
        control_change_msg = self.midi_gen.track[3]
        self.assertEqual(control_change_msg.type, 'control_change')
        self.assertEqual(control_change_msg.channel, 0)
        self.assertEqual(control_change_msg.control, 1)
        self.assertEqual(control_change_msg.value, 64)

    def test_add_pitch_bend(self):
        self.midi_gen.add_pitch_bend(channel=0, value=8192)
        pitch_bend_msg = self.midi_gen.track[3]
        self.assertEqual(pitch_bend_msg.type, 'pitch_bend')
        self.assertEqual(pitch_bend_msg.channel, 0)
        self.assertEqual(pitch_bend_msg.pitch, 8192)

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
            self.midi_gen.set_key_signature(8)

        with self.assertRaises(ValueError):
            self.midi_gen.set_key_signature(-8)

    def test_invalid_note_value(self):
        with self.assertRaises(ValueError):
            self.midi_gen.add_note(-1, 64, 500)

        with self.assertRaises(ValueError):
            self.midi_gen.add_note(128, 64, 500)
