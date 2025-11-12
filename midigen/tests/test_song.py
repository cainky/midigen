import unittest
from midigen import Song, Section, Key

class TestSong(unittest.TestCase):
    def test_create_song(self):
        song = Song(key=Key("C", "major"), tempo=120)
        self.assertEqual(song.key, Key("C", "major"))
        self.assertEqual(song.tempo, 120)

    def test_add_section(self):
        song = Song()
        section = Section(name="Verse", length=8, chord_progression="I-V-vi-IV")
        song.add_section(section)
        self.assertEqual(len(song.sections), 1)
        self.assertEqual(song.sections[0].name, "Verse")

    def test_add_instrument(self):
        song = Song()
        song.add_instrument("Acoustic Grand Piano")
        self.assertIn("Acoustic Grand Piano", song.instruments)
        track_index = song.instruments["Acoustic Grand Piano"]
        track = song.midigen.tracks[track_index]
        # Check for program change message
        has_program_change = False
        for msg in track.track:
            if msg.type == 'program_change' and msg.program == 0:
                has_program_change = True
                break
        self.assertTrue(has_program_change)

    def test_generate_song(self):
        song = Song(key=Key("C", "major"))
        song.add_section(Section(name="Verse", length=4, chord_progression="I-V-vi-IV"))
        song.add_instrument("Acoustic Grand Piano")
        song.generate("Acoustic Grand Piano")

        track_index = song.instruments["Acoustic Grand Piano"]
        track = song.midigen.tracks[track_index]

        # 4 chords, 3 notes per chord = 12 notes
        self.assertEqual(len(track.notes), 12)

    def test_multi_section_song(self):
        """Test song with multiple sections"""
        song = Song(key=Key("C", "major"), tempo=120)
        verse = Section(name="Verse", length=4, chord_progression="I-V-vi-IV")
        chorus = Section(name="Chorus", length=4, chord_progression="IV-I-V-vi")
        bridge = Section(name="Bridge", length=2, chord_progression="ii-V")

        song.add_section(verse)
        song.add_section(chorus)
        song.add_section(bridge)

        self.assertEqual(len(song.sections), 3)
        self.assertEqual(song.sections[0].name, "Verse")
        self.assertEqual(song.sections[1].name, "Chorus")
        self.assertEqual(song.sections[2].name, "Bridge")

    def test_multi_instrument_song(self):
        """Test song with multiple instruments"""
        song = Song(key=Key("G", "major"), tempo=100)
        song.add_section(Section(name="Verse", length=4, chord_progression="I-IV-V-I"))

        # Add multiple instruments
        song.add_instrument("Acoustic Grand Piano")
        song.add_instrument("Acoustic Bass")
        song.add_instrument("Violin")

        self.assertEqual(len(song.instruments), 3)
        self.assertIn("Acoustic Grand Piano", song.instruments)
        self.assertIn("Acoustic Bass", song.instruments)
        self.assertIn("Violin", song.instruments)

        # Generate for each instrument
        song.generate("Acoustic Grand Piano")
        song.generate("Acoustic Bass")
        song.generate("Violin")

        # Verify each track has notes
        for instrument in ["Acoustic Grand Piano", "Acoustic Bass", "Violin"]:
            track_index = song.instruments[instrument]
            track = song.midigen.tracks[track_index]
            self.assertGreater(len(track.notes), 0)
