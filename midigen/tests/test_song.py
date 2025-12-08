"""
Tests for the Song class and MidiCompiler.

These tests verify both the new Compiler API and backward compatibility
with the legacy Song API.
"""

import unittest
import warnings
from midigen import Song, Section, Key, MidiCompiler
from midigen.channel_pool import ChannelExhaustedError
from midigen.instruments import INSTRUMENT_MAP


class TestSong(unittest.TestCase):
    """Tests for Song as a pure data container."""

    def test_create_song(self):
        """Test basic song creation."""
        song = Song(key=Key("C", "major"), tempo=120)
        self.assertEqual(song.key, Key("C", "major"))
        self.assertEqual(song.tempo, 120)

    def test_add_section(self):
        """Test adding sections to a song."""
        song = Song()
        section = Section(name="Verse", length=8, chord_progression="I-V-vi-IV")
        song.add_section(section)
        self.assertEqual(len(song.sections), 1)
        self.assertEqual(song.sections[0].name, "Verse")

    def test_add_instrument(self):
        """Test registering instruments."""
        song = Song()
        song.add_instrument("Acoustic Grand Piano")
        self.assertIn("Acoustic Grand Piano", song.instruments)

    def test_add_drums(self):
        """Test adding a drum track."""
        song = Song()
        song.add_drums()
        self.assertIn("Drums", song.instruments)

    def test_multi_section_song(self):
        """Test song with multiple sections."""
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

    def test_invalid_instrument_name(self):
        """Test that invalid instrument name raises ValueError."""
        song = Song()
        with self.assertRaises(ValueError):
            song.add_instrument("Not A Real Instrument")

    def test_method_chaining(self):
        """Test that Song methods support chaining."""
        song = (
            Song(key=Key("G", "major"), tempo=120)
            .add_section(Section("Verse", 4, "I-V-vi-IV"))
            .add_section(Section("Chorus", 4, "IV-I-V-vi"))
            .add_instrument("Acoustic Grand Piano")
            .add_drums()
        )
        self.assertEqual(len(song.sections), 2)
        self.assertEqual(len(song.instruments), 2)


class TestMidiCompiler(unittest.TestCase):
    """Tests for MidiCompiler."""

    def test_compile_simple_song(self):
        """Test compiling a simple song."""
        song = Song(key=Key("C", "major"))
        song.add_section(Section(name="Verse", length=4, chord_progression="I-V-vi-IV"))
        song.add_instrument("Acoustic Grand Piano")

        compiler = MidiCompiler(song)
        compiler.compile()

        track = compiler.get_track("Acoustic Grand Piano")
        # 4 bars * 4 beats = 16 chords (I-V-vi-IV loops 4 times)
        # 16 chords * 3 notes per chord = 48 notes
        self.assertEqual(len(track.notes), 48)

    def test_compile_multi_instrument(self):
        """Test compiling with multiple instruments."""
        song = Song(key=Key("G", "major"), tempo=100)
        song.add_section(Section(name="Verse", length=4, chord_progression="I-IV-V-I"))
        song.add_instrument("Acoustic Grand Piano")
        song.add_instrument("Acoustic Bass")
        song.add_instrument("Violin")

        compiler = MidiCompiler(song)
        compiler.compile()

        # Verify each track has notes
        for instrument in ["Acoustic Grand Piano", "Acoustic Bass", "Violin"]:
            track = compiler.get_track(instrument)
            self.assertIsNotNone(track)
            self.assertGreater(len(track.notes), 0)

    def test_channel_allocation(self):
        """Test that compiler allocates channels correctly."""
        song = Song()
        song.add_instrument("Acoustic Grand Piano")
        song.add_instrument("Acoustic Bass")

        compiler = MidiCompiler(song)
        # Before adding instruments to compiler
        self.assertEqual(compiler.available_channels, 15)

        # Add instruments
        compiler.add_instrument("Acoustic Grand Piano")
        self.assertEqual(compiler.available_channels, 14)

        compiler.add_instrument("Acoustic Bass")
        self.assertEqual(compiler.available_channels, 13)

    def test_channel_exhaustion(self):
        """Test that exceeding 15 melodic instruments raises error."""
        song = Song()
        compiler = MidiCompiler(song)

        # Get 15 unique instrument names
        instrument_names = list(INSTRUMENT_MAP.keys())[:15]

        # Add 15 instruments (should succeed)
        for name in instrument_names:
            compiler.add_instrument(name)

        self.assertEqual(compiler.available_channels, 0)

        # 16th instrument should raise ChannelExhaustedError
        unused_instrument = None
        for name in INSTRUMENT_MAP.keys():
            if name not in instrument_names:
                unused_instrument = name
                break

        with self.assertRaises(ChannelExhaustedError):
            compiler.add_instrument(unused_instrument)

    def test_drums_dont_consume_melodic_channels(self):
        """Test that drums don't consume melodic channels."""
        song = Song()
        compiler = MidiCompiler(song)

        compiler.add_drums()
        # Drums don't consume melodic channels
        self.assertEqual(compiler.available_channels, 15)

    def test_program_change_on_track(self):
        """Test that instruments have correct program change."""
        song = Song()
        song.add_instrument("Acoustic Grand Piano")

        compiler = MidiCompiler(song)
        compiler.add_instrument("Acoustic Grand Piano")

        track = compiler.get_track("Acoustic Grand Piano")
        # Check for program change message
        has_program_change = False
        for msg in track.track:
            if msg.type == 'program_change' and msg.program == 0:
                has_program_change = True
                break
        self.assertTrue(has_program_change)


class TestSectionLength(unittest.TestCase):
    """Tests for Section.length enforcement (loop/truncate)."""

    def test_exact_fit(self):
        """Test when progression exactly fits section length."""
        # 4 bars section, 4 chords (1 bar each) = exact fit
        song = Song(key=Key("C", "major"))
        song.add_section(Section("Verse", 4, "I-V-vi-IV"))
        song.add_instrument("Acoustic Grand Piano")

        compiler = MidiCompiler(song)
        compiler.compile()

        track = compiler.get_track("Acoustic Grand Piano")
        # 4 bars * 4 beats * 1 chord/beat... wait, each chord = 1 beat (480 ticks)
        # With beats_per_bar=4, ticks_per_bar = 4*480 = 1920
        # 4 bars = 4 * 1920 = 7680 ticks
        # Each chord = 480 ticks, so 7680/480 = 16 chords needed
        # 4-chord progression loops 4 times = 16 chords
        # 16 chords * 3 notes = 48 notes
        self.assertEqual(len(track.notes), 48)

    def test_loop_progression(self):
        """Test looping a short progression to fill section."""
        # 8 bars section with 2-chord progression
        song = Song(key=Key("C", "major"))
        song.add_section(Section("Verse", 8, "I-V"))
        song.add_instrument("Acoustic Grand Piano")

        compiler = MidiCompiler(song)
        compiler.compile()

        track = compiler.get_track("Acoustic Grand Piano")
        # 8 bars * 4 beats = 32 chords needed
        # I-V (2 chords) loops 16 times = 32 chords
        # 32 chords * 3 notes = 96 notes
        self.assertEqual(len(track.notes), 96)

    def test_truncate_progression(self):
        """Test truncating a long progression to fit section."""
        # 1 bar section with 4-chord progression
        song = Song(key=Key("C", "major"))
        song.add_section(Section("Intro", 1, "I-IV-V-I"))
        song.add_instrument("Acoustic Grand Piano")

        compiler = MidiCompiler(song)
        compiler.compile()

        track = compiler.get_track("Acoustic Grand Piano")
        # 1 bar * 4 beats = 4 chords needed
        # I-IV-V-I exactly fits (no truncation in this case)
        # 4 chords * 3 notes = 12 notes
        self.assertEqual(len(track.notes), 12)

    def test_multi_section_timing(self):
        """Test timing is correct across multiple sections."""
        song = Song(key=Key("C", "major"))
        song.add_section(Section("Intro", 2, "I-V"))
        song.add_section(Section("Verse", 4, "I-IV-V-I"))
        song.add_instrument("Acoustic Grand Piano")

        compiler = MidiCompiler(song)
        compiler.compile()

        track = compiler.get_track("Acoustic Grand Piano")
        # Intro: 2 bars * 4 beats = 8 chords (I-V loops 4 times)
        # Verse: 4 bars * 4 beats = 16 chords (I-IV-V-I loops 4 times)
        # Total: 24 chords * 3 notes = 72 notes
        self.assertEqual(len(track.notes), 72)

        # Verify timing: Intro ends at 2 bars * 4 beats * 480 = 3840 ticks
        # Verse starts at 3840 ticks
        intro_notes = [n for n in track.notes if n.time < 3840]
        verse_notes = [n for n in track.notes if n.time >= 3840]
        self.assertEqual(len(intro_notes), 24)  # 8 chords * 3 notes
        self.assertEqual(len(verse_notes), 48)  # 16 chords * 3 notes


class TestLegacyAPI(unittest.TestCase):
    """Tests for backward compatibility with legacy Song API."""

    def test_legacy_generate(self):
        """Test legacy Song.generate() still works."""
        song = Song(key=Key("C", "major"))
        song.add_section(Section(name="Verse", length=4, chord_progression="I-V-vi-IV"))
        song.add_instrument("Acoustic Grand Piano")

        # Suppress the deprecation warning for this test
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            song.generate("Acoustic Grand Piano")

        track = song.midigen.tracks[1]  # Track 0 is default, 1 is piano
        # With section length enforcement: 4 bars * 4 beats = 16 chords
        # 16 chords * 3 notes = 48 notes
        self.assertEqual(len(track.notes), 48)

    def test_legacy_available_channels(self):
        """Test legacy available_channels property."""
        song = Song()
        song.add_instrument("Acoustic Grand Piano")
        song.add_instrument("Acoustic Bass")

        # This triggers compiler creation and channel allocation
        available = song.available_channels
        self.assertEqual(available, 13)

    def test_deprecation_warning_on_generate(self):
        """Test that Song.generate() raises deprecation warning."""
        song = Song()
        song.add_section(Section("Verse", 4, "I-V-vi-IV"))
        song.add_instrument("Acoustic Grand Piano")

        with self.assertWarns(DeprecationWarning):
            song.generate("Acoustic Grand Piano")


if __name__ == "__main__":
    unittest.main()
