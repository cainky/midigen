from midigen.scale import Scale
import unittest

class TestScale(unittest.TestCase):
    def test_major_scale(self):
        c_major = Scale.major(60)
        self.assertEqual(c_major, [60, 62, 64, 65, 67, 69, 71, 72])

    def test_minor_scale(self):
        a_minor = Scale.minor(57)
        self.assertEqual(a_minor, [57, 59, 60, 62, 64, 65, 67, 69])
