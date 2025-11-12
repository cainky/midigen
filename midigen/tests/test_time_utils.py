import unittest
from midigen import TimeConverter


class TestTimeConverter(unittest.TestCase):
    def setUp(self):
        self.tc = TimeConverter()

    def test_initialization(self):
        """Test TimeConverter initialization"""
        tc = TimeConverter(480)
        self.assertEqual(tc.ticks_per_quarter_note, 480)

        tc = TimeConverter(960)
        self.assertEqual(tc.ticks_per_quarter_note, 960)

    def test_initialization_invalid(self):
        """Test TimeConverter initialization with invalid values"""
        with self.assertRaises(ValueError):
            TimeConverter(0)
        with self.assertRaises(ValueError):
            TimeConverter(-100)

    def test_beats_to_ticks_quarter_notes(self):
        """Test converting quarter note beats to ticks"""
        self.assertEqual(self.tc.beats_to_ticks(1), 480)
        self.assertEqual(self.tc.beats_to_ticks(4), 1920)
        self.assertEqual(self.tc.beats_to_ticks(0.5), 240)

    def test_beats_to_ticks_eighth_notes(self):
        """Test converting eighth note beats to ticks"""
        self.assertEqual(self.tc.beats_to_ticks(1, beat_unit=8), 240)
        self.assertEqual(self.tc.beats_to_ticks(8, beat_unit=8), 1920)

    def test_beats_to_ticks_half_notes(self):
        """Test converting half note beats to ticks"""
        self.assertEqual(self.tc.beats_to_ticks(1, beat_unit=2), 960)
        self.assertEqual(self.tc.beats_to_ticks(2, beat_unit=2), 1920)

    def test_beats_to_ticks_invalid(self):
        """Test beats_to_ticks with invalid values"""
        with self.assertRaises(ValueError):
            self.tc.beats_to_ticks(-1)
        with self.assertRaises(ValueError):
            self.tc.beats_to_ticks(1, beat_unit=5)

    def test_measures_to_ticks_4_4_time(self):
        """Test converting measures in 4/4 time to ticks"""
        self.assertEqual(self.tc.measures_to_ticks(1), 1920)  # 4 beats * 480 ticks
        self.assertEqual(self.tc.measures_to_ticks(2), 3840)
        self.assertEqual(self.tc.measures_to_ticks(0.5), 960)

    def test_measures_to_ticks_3_4_time(self):
        """Test converting measures in 3/4 time to ticks"""
        self.assertEqual(self.tc.measures_to_ticks(1, 3, 4), 1440)  # 3 beats * 480 ticks
        self.assertEqual(self.tc.measures_to_ticks(2, 3, 4), 2880)

    def test_measures_to_ticks_6_8_time(self):
        """Test converting measures in 6/8 time to ticks"""
        self.assertEqual(self.tc.measures_to_ticks(1, 6, 8), 1440)  # 6 eighth notes
        self.assertEqual(self.tc.measures_to_ticks(2, 6, 8), 2880)

    def test_measures_to_ticks_invalid(self):
        """Test measures_to_ticks with invalid values"""
        with self.assertRaises(ValueError):
            self.tc.measures_to_ticks(-1)
        with self.assertRaises(ValueError):
            self.tc.measures_to_ticks(1, 0, 4)
        with self.assertRaises(ValueError):
            self.tc.measures_to_ticks(1, 4, 5)

    def test_ticks_to_beats(self):
        """Test converting ticks to beats"""
        self.assertEqual(self.tc.ticks_to_beats(480), 1.0)
        self.assertEqual(self.tc.ticks_to_beats(1920), 4.0)
        self.assertEqual(self.tc.ticks_to_beats(240), 0.5)
        self.assertEqual(self.tc.ticks_to_beats(960, beat_unit=2), 1.0)  # Half note
        self.assertEqual(self.tc.ticks_to_beats(240, beat_unit=8), 1.0)  # Eighth note

    def test_ticks_to_beats_invalid(self):
        """Test ticks_to_beats with invalid values"""
        with self.assertRaises(ValueError):
            self.tc.ticks_to_beats(-100)
        with self.assertRaises(ValueError):
            self.tc.ticks_to_beats(100, beat_unit=5)

    def test_ticks_to_measures(self):
        """Test converting ticks to measures"""
        self.assertEqual(self.tc.ticks_to_measures(1920), 1.0)  # 4/4 time
        self.assertEqual(self.tc.ticks_to_measures(3840), 2.0)
        self.assertEqual(self.tc.ticks_to_measures(1440, 3, 4), 1.0)  # 3/4 time
        self.assertEqual(self.tc.ticks_to_measures(1440, 6, 8), 1.0)  # 6/8 time

    def test_ticks_to_measures_invalid(self):
        """Test ticks_to_measures with invalid values"""
        with self.assertRaises(ValueError):
            self.tc.ticks_to_measures(-100)

    def test_note_duration_basic(self):
        """Test getting duration for basic note types"""
        self.assertEqual(self.tc.note_duration("whole"), 1920)
        self.assertEqual(self.tc.note_duration("half"), 960)
        self.assertEqual(self.tc.note_duration("quarter"), 480)
        self.assertEqual(self.tc.note_duration("eighth"), 240)
        self.assertEqual(self.tc.note_duration("sixteenth"), 120)

    def test_note_duration_dotted(self):
        """Test getting duration for dotted note types"""
        self.assertEqual(self.tc.note_duration("dotted_half"), 1440)  # 1.5 * 960
        self.assertEqual(self.tc.note_duration("dotted_quarter"), 720)  # 1.5 * 480
        self.assertEqual(self.tc.note_duration("dotted_eighth"), 360)  # 1.5 * 240

    def test_note_duration_triplets(self):
        """Test getting duration for triplet note types"""
        self.assertEqual(self.tc.note_duration("triplet_quarter"), 320)  # 2/3 * 480
        self.assertEqual(self.tc.note_duration("triplet_eighth"), 160)  # 1/3 * 480

    def test_note_duration_invalid(self):
        """Test note_duration with invalid note type"""
        with self.assertRaises(ValueError):
            self.tc.note_duration("invalid_note")

    def test_bpm_to_microseconds(self):
        """Test BPM to microseconds conversion"""
        self.assertEqual(TimeConverter.bpm_to_microseconds_per_quarter(120), 500000)
        self.assertEqual(TimeConverter.bpm_to_microseconds_per_quarter(60), 1000000)
        self.assertEqual(TimeConverter.bpm_to_microseconds_per_quarter(240), 250000)

    def test_bpm_to_microseconds_invalid(self):
        """Test BPM to microseconds with invalid values"""
        with self.assertRaises(ValueError):
            TimeConverter.bpm_to_microseconds_per_quarter(0)
        with self.assertRaises(ValueError):
            TimeConverter.bpm_to_microseconds_per_quarter(-100)

    def test_microseconds_to_bpm(self):
        """Test microseconds to BPM conversion"""
        self.assertEqual(TimeConverter.microseconds_per_quarter_to_bpm(500000), 120.0)
        self.assertEqual(TimeConverter.microseconds_per_quarter_to_bpm(1000000), 60.0)
        self.assertEqual(TimeConverter.microseconds_per_quarter_to_bpm(250000), 240.0)

    def test_microseconds_to_bpm_invalid(self):
        """Test microseconds to BPM with invalid values"""
        with self.assertRaises(ValueError):
            TimeConverter.microseconds_per_quarter_to_bpm(0)
        with self.assertRaises(ValueError):
            TimeConverter.microseconds_per_quarter_to_bpm(-100)

    def test_roundtrip_beats(self):
        """Test roundtrip conversion: beats -> ticks -> beats"""
        beats = 4
        ticks = self.tc.beats_to_ticks(beats)
        result = self.tc.ticks_to_beats(ticks)
        self.assertAlmostEqual(result, beats)

    def test_roundtrip_measures(self):
        """Test roundtrip conversion: measures -> ticks -> measures"""
        measures = 2
        ticks = self.tc.measures_to_ticks(measures)
        result = self.tc.ticks_to_measures(ticks)
        self.assertAlmostEqual(result, measures)

    def test_different_resolutions(self):
        """Test TimeConverter with different resolutions"""
        tc_960 = TimeConverter(960)
        self.assertEqual(tc_960.beats_to_ticks(1), 960)
        self.assertEqual(tc_960.note_duration("quarter"), 960)
        self.assertEqual(tc_960.measures_to_ticks(1), 3840)  # 4 beats * 960
