import unittest
from midigen.rhythm import Rhythm, RHYTHM_LIBRARY

class TestRhythm(unittest.TestCase):

    def test_rhythm_initialization(self):
        rhythm = Rhythm("x.x.", beat_duration=120)
        self.assertEqual(rhythm.pattern, "x.x.")
        self.assertEqual(rhythm.beat_duration, 120)

    def test_total_duration(self):
        rhythm = Rhythm("x.x.", beat_duration=120)
        self.assertEqual(rhythm.total_duration, 4 * 120)

    def test_get_events_simple(self):
        rhythm = Rhythm("x.x.", beat_duration=120)
        events = rhythm.get_events()
        expected_events = [
            (True, 120),
            (False, 120),
            (True, 120),
            (False, 120),
        ]
        self.assertEqual(events, expected_events)

    def test_get_events_consecutive(self):
        rhythm = Rhythm("xx..xx", beat_duration=100)
        events = rhythm.get_events()
        expected_events = [
            (True, 200),
            (False, 200),
            (True, 200),
        ]
        self.assertEqual(events, expected_events)

    def test_get_events_empty(self):
        rhythm = Rhythm("", beat_duration=120)
        events = rhythm.get_events()
        self.assertEqual(events, [])

    def test_get_events_single_type(self):
        rhythm = Rhythm("xxxx", beat_duration=120)
        events = rhythm.get_events()
        self.assertEqual(events, [(True, 480)])

        rhythm = Rhythm("....", beat_duration=120)
        events = rhythm.get_events()
        self.assertEqual(events, [(False, 480)])

    def test_rhythm_library(self):
        self.assertIn("four_on_the_floor", RHYTHM_LIBRARY)
        # Test one of the library patterns
        rhythm = Rhythm(RHYTHM_LIBRARY["four_on_the_floor"], beat_duration=120)
        self.assertEqual(rhythm.total_duration, 16 * 120)

if __name__ == '__main__':
    unittest.main()
