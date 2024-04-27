import unittest
from midigen.drums import DrumKit, Drum, GM1_DRUM_MAP
from midigen.note import Note


class TestDrumKit(unittest.TestCase):
    def setUp(self):
        self.drum_kit = DrumKit()

    def test_add_drum_valid(self):
        """Test adding valid drums from GM1_DRUM_MAP."""
        for drum_name in GM1_DRUM_MAP:
            self.drum_kit.add_drum(drum_name)
            self.assertEqual(
                self.drum_kit.get_drums()[-1].pitch,
                GM1_DRUM_MAP[drum_name],
                f"Pitch mismatch for {drum_name}",
            )

    def test_drum_characteristics(self):
        """Test if the drum characteristics (velocity, duration, time) are set correctly."""
        velocity, duration, time = 100, 10, 5
        self.drum_kit.add_drum(
            "Bass Drum 1", velocity=velocity, duration=duration, time=time
        )
        drum = self.drum_kit.get_drums()[0]
        self.assertEqual(drum.velocity, velocity)
        self.assertEqual(drum.duration, duration)
        self.assertEqual(drum.time, time)

    def test_invalid_drum_name(self):
        """Test error handling for invalid drum names."""
        with self.assertRaises(ValueError):
            self.drum_kit.add_drum("Invalid Drum")

    def test_simultaneous_drums(self):
        """Test adding multiple drums at the same start time."""
        self.drum_kit.add_drum("Acoustic Snare", time=0)
        self.drum_kit.add_drum("Closed Hi Hat", time=0)
        drums = self.drum_kit.get_drums()
        self.assertEqual(len(drums), 2)
        self.assertTrue(
            all(drum.time == 0 for drum in drums),
            "Not all drums start at the same time.",
        )

    def test_sequential_drums(self):
        """Test adding drums with sequential start times."""
        times = [0, 10, 20]
        names = ["Acoustic Snare", "Closed Hi Hat", "Bass Drum 1"]
        for name, time in zip(names, times):
            self.drum_kit.add_drum(name, time=time)

        drums = self.drum_kit.get_drums()
        self.assertEqual([drum.time for drum in drums], times)

    def test_varying_velocities_and_durations(self):
        """Test drums with varying velocities and durations."""
        specs = [
            ("Acoustic Snare", 127, 10),
            ("Closed Hi Hat", 50, 5),
            ("Bass Drum 1", 90, 15),
        ]
        for name, velocity, duration in specs:
            self.drum_kit.add_drum(name, velocity=velocity, duration=duration)

        drums = self.drum_kit.get_drums()
        for drum, spec in zip(drums, specs):
            self.assertEqual(drum.velocity, spec[1])
            self.assertEqual(drum.duration, spec[2])

    def test_duplicate_drums(self):
        """Test handling of duplicate drums."""
        drum_name = "Acoustic Snare"
        self.drum_kit.add_drum(drum_name)
        self.drum_kit.add_drum(drum_name)
        self.assertEqual(
            len(self.drum_kit.get_drums()), 2, "Duplicate drums should be allowed."
        )


class TestDrum(unittest.TestCase):
    def test_drum_creation(self):
        pitch = GM1_DRUM_MAP["Acoustic Snare"]
        velocity = 80
        duration = 100
        time = 0
        drum = Drum(pitch, velocity, duration, time)

        self.assertIsInstance(drum.note, Note)
        self.assertEqual(drum.note.pitch, pitch)
        self.assertEqual(drum.note.velocity, velocity)
        self.assertEqual(drum.note.duration, duration)
        self.assertEqual(drum.note.time, time)

    def test_drum_negative_duration(self):
        with self.assertRaises(ValueError):
            Drum(GM1_DRUM_MAP["Acoustic Snare"], 80, -100, 0)

    def test_drum_negative_velocity(self):
        with self.assertRaises(ValueError):
            Drum(GM1_DRUM_MAP["Acoustic Snare"], -80, 100, 0)

    def test_drum_invalid_pitch(self):
        with self.assertRaises(ValueError):
            Drum(200, 80, 100, 0)  # Assuming 200 is outside the valid MIDI pitch range


if __name__ == "__main__":
    unittest.main()
