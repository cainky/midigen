import unittest
from midigen import Song, Section, Key
from midigen.rhythm import Rhythm

class TestSong(unittest.TestCase):

    def setUp(self):
        self.song = Song(key=Key("C", "major"), tempo=120)

    def test_create_song(self):
        self.assertEqual(self.song.key, Key("C", "major"))
        self.assertEqual(self.song.tempo, 120)

    def test_add_section(self):
        section = Section(name="Verse", length=8, chord_progression="I-V-vi-IV")
        self.song.add_section(section)
        self.assertEqual(len(self.song.sections), 1)
        self.assertEqual(self.song.sections[0].name, "Verse")

    def test_add_instrument(self):
        self.song.add_instrument("Acoustic Grand Piano")
        self.assertIn("Acoustic Grand Piano", self.song.instruments)
        track_index = self.song.instruments["Acoustic Grand Piano"]
        track = self.song.midigen.tracks[track_index]
        # Program 0 is Acoustic Grand Piano
        self.assertEqual(track.program, 0)

    def test_generate_song_no_rhythm(self):
        self.song.add_section(Section(name="Verse", length=4, chord_progression="I-V"))
        self.song.add_instrument("Acoustic Grand Piano")
        self.song.generate("Acoustic Grand Piano")

        track_index = self.song.instruments["Acoustic Grand Piano"]
        track = self.song.midigen.tracks[track_index]
        # 2 chords * 3 notes/chord * 2 events/note = 12 events
        self.assertEqual(len(track.events), 12)

        # Check timing of the second chord
        second_chord_time = 4 * 480 # 4 beats per chord
        second_chord_events = [e for e in track.events if e['time'] >= second_chord_time]
        self.assertTrue(len(second_chord_events) > 0)
        self.assertEqual(second_chord_events[0]['time'], second_chord_time)

    def test_generate_with_rhythm(self):
        # A simple rhythm: two quarter notes
        rhythm = Rhythm("x...x...", beat_duration=120) # 1 char = 16th note
        # A simple progression: one chord
        section = Section(name="Verse", length=2, chord_progression="I", rhythm=rhythm)

        self.song.add_section(section)
        self.song.add_instrument("Acoustic Grand Piano")
        self.song.generate("Acoustic Grand Piano")

        track_index = self.song.instruments["Acoustic Grand Piano"]
        track = self.song.midigen.tracks[track_index]

        # 1 chord (3 notes) * 2 rhythmic hits = 6 notes. 6 notes * 2 events/note = 12 events.
        self.assertEqual(len(track.events), 12)

        # Check the timing and duration of the events
        # The rhythm "x...x..." with beat_duration=120 generates events at t=0 and t=480, each with duration 120.

        # First hit (3 notes) at t=0
        first_hit_ons = [e for e in track.events if e['type'] == 'note_on' and e['time'] == 0]
        self.assertEqual(len(first_hit_ons), 3)

        # First hit note_offs should be at t=120
        first_hit_offs = [e for e in track.events if e['type'] == 'note_off' and e['time'] == 120]
        self.assertEqual(len(first_hit_offs), 3)

        # Second hit (3 notes) at t=480
        second_hit_ons = [e for e in track.events if e['type'] == 'note_on' and e['time'] == 480]
        self.assertEqual(len(second_hit_ons), 3)

        # Second hit note_offs should be at t=480+120=600
        second_hit_offs = [e for e in track.events if e['type'] == 'note_off' and e['time'] == 600]
        self.assertEqual(len(second_hit_offs), 3)

if __name__ == '__main__':
    unittest.main()
