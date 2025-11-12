import unittest
from midigen import MidiGen, Track, Note, Chord, ChordProgression, Key, DrumKit, Drum, Song, Section


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple components"""

    def test_complete_song_with_drums_chords_and_melody(self):
        """Test creating a complete song with drums, chord progression, and melody"""
        # Create MIDI generator
        midi = MidiGen(tempo=120, key_signature=Key("C", "major"))

        # Track 0: Melody (use active track which is track 0)
        melody_track = midi.get_active_track()
        melody_notes = [
            Note(pitch=60, velocity=80, duration=480, time=0),      # C
            Note(pitch=64, velocity=80, duration=480, time=480),    # E
            Note(pitch=67, velocity=80, duration=480, time=960),    # G
            Note(pitch=72, velocity=80, duration=480, time=1440),   # C (octave up)
        ]
        for note in melody_notes:
            melody_track.add_note(note)
        melody_track.add_note_off_messages()

        # Track 1: Chord progression
        midi.add_track()
        chord_track = midi.tracks[1]  # Access track directly
        chord_track.add_program_change(channel=1, program=0)  # Piano

        progression = ChordProgression.from_roman_numerals(
            key=Key("C", "major"),
            progression_string="I-V-vi-IV",
            octave=3,
            duration=480,
            time_per_chord=480
        )
        chord_track.add_chord_progression(progression)
        chord_track.add_note_off_messages()

        # Track 2: Drums
        midi.add_track()
        drum_track = midi.tracks[2]  # Access track directly

        drum_kit = DrumKit()
        # Simple rock beat pattern
        drum_kit.add_drum("Bass Drum 1", velocity=90, duration=240, time=0)
        drum_kit.add_drum("Acoustic Snare", velocity=80, duration=240, time=480)
        drum_kit.add_drum("Bass Drum 1", velocity=90, duration=240, time=960)
        drum_kit.add_drum("Acoustic Snare", velocity=80, duration=240, time=1440)

        drum_track.add_drum_kit(drum_kit)
        drum_track.add_note_off_messages()

        # Verify tracks were created (includes default track 0)
        self.assertEqual(len(midi.tracks), 3)

        # Verify melody track has notes
        self.assertEqual(len(melody_track.notes), 4)

        # Verify chord track has notes (4 chords × 3 notes each)
        self.assertEqual(len(chord_track.notes), 12)

        # Verify drum track has drum hits
        self.assertEqual(len(drum_track.notes), 4)

    def test_song_class_with_multiple_sections_and_instruments(self):
        """Test Song class with complex arrangement"""
        song = Song(key=Key("D", "minor"), tempo=110)

        # Add sections
        intro = Section(name="Intro", length=4, chord_progression="i-VII-VI-VII")
        verse = Section(name="Verse", length=8, chord_progression="i-iv-VII-III")
        chorus = Section(name="Chorus", length=8, chord_progression="VI-VII-i-i")

        song.add_section(intro)
        song.add_section(verse)
        song.add_section(chorus)

        # Add multiple instruments
        song.add_instrument("Electric Piano 1")
        song.add_instrument("String Ensemble 1")
        song.add_instrument("Synth Bass 1")

        # Generate for all instruments
        song.generate("Electric Piano 1")
        song.generate("String Ensemble 1")
        song.generate("Synth Bass 1")

        # Verify song structure
        self.assertEqual(len(song.sections), 3)
        self.assertEqual(len(song.instruments), 3)

        # Verify each instrument has generated notes
        for instrument_name in song.instruments:
            track_idx = song.instruments[instrument_name]
            track = song.midigen.tracks[track_idx]
            self.assertGreater(len(track.notes), 0)

    def test_overlapping_notes(self):
        """Test handling of overlapping notes with different timing"""
        midi = MidiGen(tempo=120)
        track = midi.get_active_track()

        # Create overlapping notes
        note1 = Note(pitch=60, velocity=64, duration=960, time=0)      # Long C
        note2 = Note(pitch=64, velocity=64, duration=480, time=480)    # E starts during C
        note3 = Note(pitch=67, velocity=64, duration=480, time=480)    # G starts with E

        track.add_note(note1)
        track.add_note(note2)
        track.add_note(note3)
        track.add_note_off_messages()

        # Verify all notes were added
        self.assertEqual(len(track.notes), 3)

        # Verify notes have correct timing
        self.assertEqual(track.notes[0].time, 0)
        self.assertEqual(track.notes[1].time, 480)
        self.assertEqual(track.notes[2].time, 480)

    def test_complex_timing_scenarios(self):
        """Test complex timing with chords, arpeggios, and rests"""
        midi = MidiGen(tempo=140, key_signature=Key("A", "minor"))
        track = midi.get_active_track()

        # Add a chord
        root = Note(pitch=57, velocity=70, duration=480, time=0)  # A3
        chord = Chord.create_minor_triad(root)
        track.add_chord(chord)

        # Add notes after a "rest" (gap in time)
        rest_note = Note(pitch=60, velocity=70, duration=240, time=960)  # Gap from 480-960
        track.add_note(rest_note)

        # Add another chord
        root2 = Note(pitch=60, velocity=70, duration=480, time=1440)
        chord2 = Chord.create_major_triad(root2)
        track.add_chord(chord2)

        track.add_note_off_messages()

        # Verify timing structure
        self.assertEqual(len(track.notes), 7)  # 3 from first chord + 1 note + 3 from second chord

        # Verify first chord notes all start at time 0
        self.assertEqual(track.notes[0].time, 0)
        self.assertEqual(track.notes[1].time, 0)
        self.assertEqual(track.notes[2].time, 0)

        # Verify rest note at time 960
        self.assertEqual(track.notes[3].time, 960)

        # Verify second chord notes all start at time 1440
        self.assertEqual(track.notes[4].time, 1440)
        self.assertEqual(track.notes[5].time, 1440)
        self.assertEqual(track.notes[6].time, 1440)

    def test_factory_chord_methods(self):
        """Test new Chord factory class methods"""
        root = Note(pitch=60, velocity=64, duration=480, time=0)

        # Test all factory methods
        major = Chord.create_major_triad(root)
        minor = Chord.create_minor_triad(root)
        dom7 = Chord.create_dominant_seventh(root)
        maj7 = Chord.create_major_seventh(root)
        min7 = Chord.create_minor_seventh(root)
        half_dim = Chord.create_half_diminished_seventh(root)
        dim7 = Chord.create_diminished_seventh(root)
        min9 = Chord.create_minor_ninth(root)
        maj9 = Chord.create_major_ninth(root)
        dom9 = Chord.create_dominant_ninth(root)

        # Verify they all return Chord objects
        self.assertIsInstance(major, Chord)
        self.assertIsInstance(minor, Chord)
        self.assertIsInstance(dom7, Chord)
        self.assertIsInstance(maj7, Chord)
        self.assertIsInstance(min7, Chord)
        self.assertIsInstance(half_dim, Chord)
        self.assertIsInstance(dim7, Chord)
        self.assertIsInstance(min9, Chord)
        self.assertIsInstance(maj9, Chord)
        self.assertIsInstance(dom9, Chord)

        # Verify correct number of notes
        self.assertEqual(len(major.notes), 3)
        self.assertEqual(len(minor.notes), 3)
        self.assertEqual(len(dom7.notes), 4)
        self.assertEqual(len(maj7.notes), 4)
        self.assertEqual(len(min7.notes), 4)
        self.assertEqual(len(half_dim.notes), 4)
        self.assertEqual(len(dim7.notes), 4)
        self.assertEqual(len(min9.notes), 5)
        self.assertEqual(len(maj9.notes), 5)
        self.assertEqual(len(dom9.notes), 5)
