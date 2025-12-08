"""
Golden Master Tests for MIDI Output.

These tests verify the exact binary output of MIDI generation against
known-good reference files. This catches regressions in MIDI timing,
message ordering, and encoding.

To update golden files after verified-correct changes:
    REGENERATE_GOLDEN=1 python -m unittest midigen.tests.test_golden_master
"""

import os
import hashlib
import unittest
from io import BytesIO
from pathlib import Path

from midigen import MidiGen, Song, Section, Key, Note, Chord


GOLDEN_DIR = Path(__file__).parent / "golden_files"


def get_midi_bytes(midi_gen: MidiGen) -> bytes:
    """Extract MIDI file bytes without saving to disk."""
    buffer = BytesIO()

    # Clear and compile all tracks
    midi_gen.midi_file.tracks.clear()
    for track in midi_gen.tracks:
        compiled_track = track.compile()
        midi_gen.midi_file.tracks.append(compiled_track)

    midi_gen.midi_file.save(file=buffer)
    return buffer.getvalue()


def hash_bytes(data: bytes) -> str:
    """Generate SHA256 hash of bytes, truncated for display."""
    return hashlib.sha256(data).hexdigest()[:16]


class TestGoldenMaster(unittest.TestCase):
    """
    Golden Master tests verify the exact binary output of MIDI generation.

    These tests compare generated MIDI against reference files. If the
    MIDI format, timing, or encoding changes, these tests will fail.

    To regenerate golden files after intentional changes:
        set REGENERATE_GOLDEN=1 (Windows)
        export REGENERATE_GOLDEN=1 (Unix)
    """

    @classmethod
    def setUpClass(cls):
        """Ensure golden files directory exists."""
        GOLDEN_DIR.mkdir(exist_ok=True)

    def _compare_or_regenerate(self, output: bytes, golden_name: str, description: str):
        """
        Compare output against golden file, or regenerate if requested.

        Args:
            output: The generated MIDI bytes
            golden_name: Name of the golden file (without path)
            description: Human-readable description for error messages
        """
        golden_path = GOLDEN_DIR / golden_name

        if os.environ.get("REGENERATE_GOLDEN"):
            golden_path.write_bytes(output)
            self.skipTest(f"Golden file '{golden_name}' regenerated")

        if not golden_path.exists():
            golden_path.write_bytes(output)
            self.skipTest(
                f"Golden file '{golden_name}' created. "
                f"Run again to verify, or review the file manually."
            )

        expected = golden_path.read_bytes()
        expected_hash = hash_bytes(expected)
        actual_hash = hash_bytes(output)

        self.assertEqual(
            actual_hash,
            expected_hash,
            f"MIDI output mismatch for {description}.\n"
            f"Expected hash: {expected_hash}\n"
            f"Actual hash:   {actual_hash}\n"
            f"Run with REGENERATE_GOLDEN=1 to update if change is intentional."
        )

    def test_simple_c_major_chord(self):
        """Test a simple C major chord."""
        midi = MidiGen(tempo=120, time_signature=(4, 4), key_signature=Key("C"))

        note_c = Note(pitch=60, velocity=64, duration=480, time=0)
        note_e = Note(pitch=64, velocity=64, duration=480, time=0)
        note_g = Note(pitch=67, velocity=64, duration=480, time=0)

        chord = Chord([note_c, note_e, note_g])
        track = midi.get_active_track()
        track.add_chord(chord)

        output = get_midi_bytes(midi)
        self._compare_or_regenerate(output, "simple_c_major_chord.mid", "C major chord")

    def test_sequential_notes_timing(self):
        """Test that sequential notes have correct delta timing."""
        midi = MidiGen(tempo=120)

        track = midi.get_active_track()

        # Add notes at specific times to verify delta calculation
        track.add_note(Note(pitch=60, velocity=80, duration=240, time=0))
        track.add_note(Note(pitch=64, velocity=80, duration=240, time=480))
        track.add_note(Note(pitch=67, velocity=80, duration=240, time=960))
        track.add_note(Note(pitch=72, velocity=80, duration=240, time=1440))

        output = get_midi_bytes(midi)
        self._compare_or_regenerate(output, "sequential_notes.mid", "sequential notes")

    def test_overlapping_notes(self):
        """Test overlapping notes (polyphony)."""
        midi = MidiGen(tempo=100)
        track = midi.get_active_track()

        # Long bass note
        track.add_note(Note(pitch=36, velocity=100, duration=1920, time=0))
        # Melody notes over the bass
        track.add_note(Note(pitch=60, velocity=80, duration=480, time=0))
        track.add_note(Note(pitch=64, velocity=80, duration=480, time=480))
        track.add_note(Note(pitch=67, velocity=80, duration=480, time=960))
        track.add_note(Note(pitch=72, velocity=80, duration=480, time=1440))

        output = get_midi_bytes(midi)
        self._compare_or_regenerate(output, "overlapping_notes.mid", "overlapping notes")

    def test_song_progression_i_v_vi_iv(self):
        """Test the classic I-V-vi-IV progression."""
        song = Song(key=Key("C", "major"), tempo=120)
        song.add_section(Section(name="Verse", length=4, chord_progression="I-V-vi-IV"))
        song.add_instrument("Acoustic Grand Piano")
        song.generate("Acoustic Grand Piano")

        output = get_midi_bytes(song.midigen)
        self._compare_or_regenerate(
            output, "progression_i_v_vi_iv.mid", "I-V-vi-IV progression"
        )

    def test_multi_track_arrangement(self):
        """Test multi-track arrangement with proper timing."""
        midi = MidiGen(tempo=140, time_signature=(4, 4), key_signature=Key("G"))

        # Track 0: Melody
        melody_track = midi.get_active_track()
        melody_track.add_program_change(channel=0, program=0)  # Piano
        melody_track.add_note(Note(pitch=67, velocity=80, duration=480, time=0))
        melody_track.add_note(Note(pitch=71, velocity=80, duration=480, time=480))
        melody_track.add_note(Note(pitch=74, velocity=80, duration=960, time=960))

        # Track 1: Bass
        midi.add_track()
        bass_track = midi.tracks[1]
        bass_track.add_program_change(channel=1, program=32)  # Acoustic Bass
        bass_track.add_note(Note(pitch=43, velocity=90, duration=960, time=0))
        bass_track.add_note(Note(pitch=47, velocity=90, duration=960, time=960))

        output = get_midi_bytes(midi)
        self._compare_or_regenerate(output, "multi_track.mid", "multi-track arrangement")

    def test_zero_duration_note_edge_case(self):
        """Test handling of zero-duration notes (edge case)."""
        midi = MidiGen(tempo=120)
        track = midi.get_active_track()

        # Zero duration note - should still produce note_on before note_off
        track.add_note(Note(pitch=60, velocity=64, duration=0, time=0))
        # Normal note after
        track.add_note(Note(pitch=64, velocity=64, duration=480, time=0))

        output = get_midi_bytes(midi)
        self._compare_or_regenerate(
            output, "zero_duration_note.mid", "zero duration note"
        )


if __name__ == "__main__":
    unittest.main()
