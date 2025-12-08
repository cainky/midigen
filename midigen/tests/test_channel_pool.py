import unittest
from midigen.channel_pool import ChannelPool, ChannelExhaustedError


class TestChannelPool(unittest.TestCase):
    def setUp(self):
        self.pool = ChannelPool()

    def test_initial_state(self):
        """Test initial pool state."""
        self.assertEqual(self.pool.available_count, 15)
        self.assertEqual(self.pool.allocated_count, 0)
        self.assertFalse(self.pool.is_drums_allocated())

    def test_allocate_basic(self):
        """Test basic channel allocation."""
        ch = self.pool.allocate("Piano")
        self.assertEqual(ch, 0)  # First allocation gets channel 0
        self.assertEqual(self.pool.available_count, 14)
        self.assertEqual(self.pool.allocated_count, 1)

    def test_allocate_multiple(self):
        """Test allocating multiple instruments."""
        ch1 = self.pool.allocate("Piano")
        ch2 = self.pool.allocate("Bass")
        ch3 = self.pool.allocate("Guitar")

        self.assertEqual(ch1, 0)
        self.assertEqual(ch2, 1)
        self.assertEqual(ch3, 2)
        self.assertEqual(self.pool.allocated_count, 3)

    def test_allocate_idempotent(self):
        """Test that allocating same instrument returns same channel."""
        ch1 = self.pool.allocate("Piano")
        ch2 = self.pool.allocate("Piano")
        ch3 = self.pool.allocate("Piano")

        self.assertEqual(ch1, ch2)
        self.assertEqual(ch2, ch3)
        self.assertEqual(self.pool.allocated_count, 1)

    def test_allocate_skips_drum_channel(self):
        """Test that allocation skips channel 9 (drums)."""
        # Allocate channels 0-8
        for i in range(9):
            self.pool.allocate(f"Instrument{i}")

        # Next allocation should skip 9 and go to 10
        ch = self.pool.allocate("Instrument9")
        self.assertEqual(ch, 10)

    def test_allocate_exhaustion(self):
        """Test that exhausting all channels raises error."""
        # Allocate all 15 melodic channels
        for i in range(15):
            self.pool.allocate(f"Instrument{i}")

        self.assertEqual(self.pool.available_count, 0)

        # 16th allocation should raise
        with self.assertRaises(ChannelExhaustedError) as ctx:
            self.pool.allocate("OneTooMany")

        self.assertIn("exhausted", str(ctx.exception).lower())

    def test_allocate_drums(self):
        """Test drum channel allocation."""
        ch = self.pool.allocate_drums()
        self.assertEqual(ch, 9)
        self.assertTrue(self.pool.is_drums_allocated())

    def test_drums_independent_of_melodic(self):
        """Test that drum channel is independent of melodic pool."""
        # Allocate some melodic channels
        self.pool.allocate("Piano")
        self.pool.allocate("Bass")

        # Drum allocation should not affect melodic count
        self.pool.allocate_drums()

        self.assertEqual(self.pool.allocated_count, 2)  # Only melodic
        self.assertTrue(self.pool.is_drums_allocated())

    def test_release(self):
        """Test releasing a channel."""
        ch1 = self.pool.allocate("Piano")
        self.pool.allocate("Bass")

        self.assertEqual(self.pool.available_count, 13)

        self.pool.release("Piano")

        self.assertEqual(self.pool.available_count, 14)
        self.assertFalse(self.pool.is_allocated("Piano"))
        self.assertTrue(self.pool.is_allocated("Bass"))

    def test_release_and_reallocate(self):
        """Test that released channel can be reallocated."""
        ch1 = self.pool.allocate("Piano")
        self.pool.allocate("Bass")
        self.pool.allocate("Guitar")

        self.pool.release("Piano")

        # New allocation should get the released channel (0)
        ch_new = self.pool.allocate("Strings")
        self.assertEqual(ch_new, 0)

    def test_release_unallocated_is_noop(self):
        """Test that releasing unallocated instrument is safe."""
        self.pool.release("NonExistent")  # Should not raise
        self.assertEqual(self.pool.available_count, 15)

    def test_release_drums(self):
        """Test releasing drum channel."""
        self.pool.allocate_drums()
        self.assertTrue(self.pool.is_drums_allocated())

        self.pool.release_drums()
        self.assertFalse(self.pool.is_drums_allocated())

    def test_get_channel(self):
        """Test getting channel for instrument."""
        self.pool.allocate("Piano")

        self.assertEqual(self.pool.get_channel("Piano"), 0)
        self.assertIsNone(self.pool.get_channel("NonExistent"))

    def test_allocated_instruments(self):
        """Test getting allocated instruments mapping."""
        self.pool.allocate("Piano")
        self.pool.allocate("Bass")

        instruments = self.pool.allocated_instruments

        self.assertEqual(instruments, {"Piano": 0, "Bass": 1})

        # Should be a copy, not the original
        instruments["New"] = 99
        self.assertNotIn("New", self.pool.allocated_instruments)

    def test_reset(self):
        """Test resetting the pool."""
        self.pool.allocate("Piano")
        self.pool.allocate("Bass")
        self.pool.allocate_drums()

        self.pool.reset()

        self.assertEqual(self.pool.available_count, 15)
        self.assertEqual(self.pool.allocated_count, 0)
        self.assertFalse(self.pool.is_drums_allocated())

    def test_repr(self):
        """Test string representation."""
        self.pool.allocate("Piano")
        repr_str = repr(self.pool)

        self.assertIn("available=14", repr_str)
        self.assertIn("allocated=1", repr_str)
        self.assertIn("drums=free", repr_str)

    def test_drum_channel_constant(self):
        """Test that drum channel is always 9."""
        self.assertEqual(ChannelPool.DRUM_CHANNEL, 9)

    def test_max_channels_constant(self):
        """Test max channels constant."""
        self.assertEqual(ChannelPool.MAX_CHANNELS, 16)

    def test_melodic_channels_excludes_nine(self):
        """Test melodic channels set excludes channel 9."""
        self.assertNotIn(9, ChannelPool.MELODIC_CHANNELS)
        self.assertEqual(len(ChannelPool.MELODIC_CHANNELS), 15)


if __name__ == "__main__":
    unittest.main()
