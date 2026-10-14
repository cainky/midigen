"""
Regression tests for bugs found in the 1.1.0 audit.

Each test pins a behavior that was broken before the fix. Most check what a
synth would actually hear (via ``heard_notes``) rather than raw message
counts, because several of these bugs produced well-formed MIDI that played
wrong.
"""

import os
import random
import tempfile
import unittest
import warnings

import mido

from midigen import (
    Arpeggio,
    ArpeggioPattern,
    Chord,
    ChordProgression,
    DrumKit,
    Key,
    MidiCompiler,
    MidiGen,
    Melody,
    Note,
    Scale,
    Section,
    Song,
    TimeConverter,
    Track,
    VALID_KEYS,
    get_chord_pitches,
    parse_roman_numeral,
)
from midigen.theory.roman import ChordQuality, get_note_names_for_pitches


def heard_notes(midi_track):
    """
    Simulate how a synth interprets a compiled track.

    A note_off (or note_on with velocity 0) ends the sounding note of that
    pitch on that channel. Returns (pitch, start_tick, length, channel) for
    every note_on, in order of note_on.
    """
    sounding = {}
    heard = []
    now = 0
    for msg in midi_track:
        now += msg.time
        if msg.type == "note_on" and msg.velocity > 0:
            key = (msg.channel, msg.note)
            if key in sounding:  # retrigger while sounding: old note ends here
                idx = sounding.pop(key)
                p, s, _, c = heard[idx]
                heard[idx] = (p, s, now - s, c)
            sounding[key] = len(heard)
            heard.append((msg.note, now, None, msg.channel))
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            key = (msg.channel, msg.note)
            if key in sounding:
                idx = sounding.pop(key)
                p, s, _, c = heard[idx]
                heard[idx] = (p, s, now - s, c)
    return heard


def absolute_times(midi_track, msg_type):
    now, out = 0, []
    for msg in midi_track:
        now += msg.time
        if msg.type == msg_type:
            out.append(now)
    return out


def timeline(midi_track, types):
    now, out = 0, []
    for msg in midi_track:
        now += msg.time
        if msg.type in types:
            out.append((msg.type, now))
    return out


def simple_song(
    progression="I-V-vi-IV", length=1, instruments=("Acoustic Grand Piano",), key=None
):
    song = Song(key=key or Key("C"))
    song.add_section(Section("A", length, progression))
    for name in instruments:
        song.add_instrument(name)
    return song


class TestNoteEventOrdering(unittest.TestCase):
    """note_off must precede note_on at the same tick, or repeated pitches get cut off."""

    def test_repeated_pitch_both_notes_heard_full_length(self):
        track = Track()
        track.add_note(Note(60, 80, 480, 0))
        track.add_note(Note(60, 80, 480, 480))
        heard = heard_notes(track.compile())
        self.assertEqual(
            [(p, s, n) for p, s, n, _ in heard], [(60, 0, 480), (60, 480, 480)]
        )

    def test_song_common_tones_are_not_silenced(self):
        # I-V share G, vi-IV share A and C, IV-I share C.
        compiler = MidiCompiler(simple_song()).compile()
        heard = heard_notes(compiler.get_track("Acoustic Grand Piano").compile())
        self.assertEqual(len(heard), 4 * 3)  # 1 bar = 4 one-beat chords
        self.assertTrue(all(length == 480 for _, _, length, _ in heard), heard)

    def test_random_walk_repeated_notes_are_heard(self):
        melody = Melody.random_walk(60, 16, Scale.major(60), max_interval=3, seed=42)
        track = Track()
        for note in melody:
            track.add_note(note)
        heard = heard_notes(track.compile())
        self.assertEqual(len(heard), 16)
        self.assertTrue(all(length == 480 for _, _, length, _ in heard), heard)

    def test_zero_duration_note_is_paired(self):
        track = Track()
        track.add_note(Note(60, 64, 0, 0))
        track.add_note(Note(64, 64, 480, 0))
        msgs = [
            (m.type, m.note)
            for m in track.compile()
            if m.type in ("note_on", "note_off")
        ]
        # zero-length note: on before its own off; the other note is untouched
        self.assertLess(msgs.index(("note_on", 60)), msgs.index(("note_off", 60)))
        heard = {p: length for p, _, length, _ in heard_notes(track.compile())}
        self.assertEqual(heard, {60: 0, 64: 480})


class TestCompilerChannels(unittest.TestCase):
    def test_each_instrument_plays_on_its_allocated_channel(self):
        names = ("Acoustic Grand Piano", "Violin", "Acoustic Bass")
        compiler = MidiCompiler(simple_song(instruments=names)).compile()
        seen = set()
        for name in names:
            compiled = compiler.get_track(name).compile()
            program_channels = {
                m.channel for m in compiled if m.type == "program_change"
            }
            note_channels = {
                m.channel for m in compiled if m.type in ("note_on", "note_off")
            }
            self.assertEqual(len(program_channels), 1, name)
            self.assertEqual(note_channels, program_channels, name)
            seen |= note_channels
        self.assertEqual(seen, {0, 1, 2})

    def test_drum_track_is_channel_9_and_gets_no_chord_tones(self):
        song = simple_song()
        song.add_drums()
        compiler = MidiCompiler(song).compile()
        drums = compiler.get_track("Drums")
        self.assertEqual(drums.channel, 9)
        self.assertEqual(drums.notes, [])

        kit = DrumKit()
        kit.add_drum("Bass Drum 1", time=0)
        drums.add_drum_kit(kit)
        channels = {m.channel for m in drums.compile() if m.type == "note_on"}
        self.assertEqual(channels, {9})

    def test_custom_drum_track_name(self):
        song = simple_song()
        song.add_drums("Percussion")
        compiler = MidiCompiler(song).compile()
        self.assertEqual(compiler.get_track("Percussion").channel, 9)

    def test_instrument_tracks_follow_insertion_order(self):
        names = ["Trumpet", "Acoustic Grand Piano", "Violin", "Flute", "Cello"]
        compiler = MidiCompiler(simple_song(instruments=names)).compile()
        tracks = [compiler.get_track(n) for n in names]
        self.assertEqual([t.channel for t in tracks], [0, 1, 2, 3, 4])
        self.assertEqual(
            [compiler.midigen.tracks.index(t) for t in tracks], [1, 2, 3, 4, 5]
        )


class TestCompilerIdempotency(unittest.TestCase):
    def test_compile_twice_does_not_duplicate_notes(self):
        compiler = MidiCompiler(simple_song())
        compiler.compile()
        first = len(compiler.get_track("Acoustic Grand Piano").notes)
        compiler.compile()
        self.assertEqual(len(compiler.get_track("Acoustic Grand Piano").notes), first)

    def test_compile_instrument_then_save_keeps_custom_octave(self):
        # The README multi-track flow: compile_instrument(...) per instrument, then save().
        song = simple_song(
            "i-VI-III-VII",
            instruments=("Synth Bass 1", "Lead 1 (square)"),
            key=Key("A", "minor"),
        )
        compiler = MidiCompiler(song)
        compiler.compile_instrument("Synth Bass 1", octave=3)
        compiler.compile_instrument("Lead 1 (square)", octave=5)
        with tempfile.TemporaryDirectory() as d:
            path = compiler.save("x.mid", output_dir=d)
            saved = mido.MidiFile(path)
        for name, octave in (("Synth Bass 1", 3), ("Lead 1 (square)", 5)):
            notes = compiler.get_track(name).notes
            self.assertEqual(len(notes), 4 * 3, name)
            self.assertEqual({n.pitch // 12 - 1 for n in notes}, {octave}, name)
        note_ons = sum(1 for t in saved.tracks for m in t if m.type == "note_on")
        self.assertEqual(note_ons, 2 * 4 * 3)

    def test_compile_instrument_twice_replaces_previous_part(self):
        compiler = MidiCompiler(simple_song())
        compiler.compile_instrument("Acoustic Grand Piano", octave=3)
        compiler.compile_instrument("Acoustic Grand Piano", octave=5)
        notes = compiler.get_track("Acoustic Grand Piano").notes
        self.assertEqual(len(notes), 12)
        self.assertEqual({n.pitch // 12 - 1 for n in notes}, {5})

    def test_recompile_keeps_notes_added_by_hand(self):
        compiler = MidiCompiler(simple_song())
        compiler.compile_instrument("Acoustic Grand Piano")
        extra = Note(100, 80, 480, 0)
        compiler.get_track("Acoustic Grand Piano").add_note(extra)
        compiler.compile_instrument("Acoustic Grand Piano", octave=3)
        self.assertIn(extra, compiler.get_track("Acoustic Grand Piano").notes)

    def test_compile_after_compile_instrument_keeps_its_settings(self):
        compiler = MidiCompiler(simple_song())
        compiler.compile_instrument("Acoustic Grand Piano", octave=3, duration=960)
        compiler.compile()
        notes = compiler.get_track("Acoustic Grand Piano").notes
        self.assertEqual({n.pitch // 12 - 1 for n in notes}, {3})
        self.assertEqual({n.duration for n in notes}, {960})
        self.assertEqual(len(notes), 2 * 3)

    def test_compile_again_picks_up_new_sections(self):
        song = simple_song()
        compiler = MidiCompiler(song).compile()
        song.add_section(Section("B", 1, "IV"))
        compiler.compile()
        self.assertEqual(
            len(compiler.get_track("Acoustic Grand Piano").notes), 4 * 3 + 4 * 3
        )

    def test_failed_recompile_keeps_previous_part(self):
        compiler = MidiCompiler(simple_song()).compile()
        before = list(compiler.get_track("Acoustic Grand Piano").notes)
        with self.assertRaises(ValueError):
            compiler.compile_instrument(
                "Acoustic Grand Piano", octave=10
            )  # pitches above 127
        self.assertEqual(compiler.get_track("Acoustic Grand Piano").notes, before)
        compiler.compile_instrument("Acoustic Grand Piano", octave=3)
        self.assertEqual(
            len(compiler.get_track("Acoustic Grand Piano").notes), len(before)
        )

    def test_non_positive_chord_duration_rejected(self):
        # duration=0 would never advance through the section
        for duration in (0, -480, 1.5):
            with self.subTest(duration=duration):
                with self.assertRaises(ValueError):
                    MidiCompiler(simple_song()).compile_instrument(
                        "Acoustic Grand Piano", duration=duration
                    )


class TestCompilerTiming(unittest.TestCase):
    def test_section_length_is_bars_regardless_of_chord_duration(self):
        song = simple_song(length=4)
        compiler = MidiCompiler(song).compile_instrument(
            "Acoustic Grand Piano", duration=960
        )
        notes = compiler.get_track("Acoustic Grand Piano").notes
        self.assertEqual(max(n.time + n.duration for n in notes), 4 * 1920)
        self.assertEqual(
            len({n.time for n in notes}), 8
        )  # 8 half-note chords in 4 bars

    def test_last_chord_is_truncated_at_section_boundary(self):
        song = Song()
        song.add_section(Section("A", 1, "I"))
        song.add_section(Section("B", 1, "IV"))
        song.add_instrument("Acoustic Grand Piano")
        compiler = MidiCompiler(song).compile_instrument(
            "Acoustic Grand Piano", duration=720
        )
        notes = compiler.get_track("Acoustic Grand Piano").notes
        section_a = sorted({(n.time, n.duration) for n in notes if n.time < 1920})
        self.assertEqual(section_a, [(0, 720), (720, 720), (1440, 480)])
        self.assertEqual(min(n.time for n in notes if n.time >= 1920), 1920)


class TestSongInstruments(unittest.TestCase):
    def test_instruments_keep_insertion_order_without_duplicates(self):
        song = Song()
        for name in ["Violin", "Acoustic Grand Piano", "Violin", "Cello"]:
            song.add_instrument(name)
        song.add_drums()
        song.add_drums()
        self.assertEqual(
            list(song.instruments), ["Violin", "Acoustic Grand Piano", "Cello", "Drums"]
        )
        self.assertEqual(song.drums, ["Drums"])

    def test_drum_name_cannot_reuse_melodic_instrument(self):
        song = Song().add_instrument("Violin")
        with self.assertRaises(ValueError):
            song.add_drums("Violin")


class TestTimedControlEvents(unittest.TestCase):
    def test_pitch_bend_time_is_absolute_and_does_not_shift_notes(self):
        track = Track()
        track.add_note(Note(60, 80, 480, 0))
        track.add_pitch_bend(value=4096, time=960)
        compiled = track.compile()
        self.assertEqual(absolute_times(compiled, "note_on"), [0])
        self.assertEqual(absolute_times(compiled, "pitchwheel"), [960])

    def test_control_change_is_interleaved_with_notes(self):
        track = Track()
        track.add_note(Note(60, 80, 480, 0))
        track.add_note(Note(62, 80, 480, 960))
        track.add_control_change(control=64, value=127, time=480)
        self.assertEqual(
            timeline(track.compile(), ("note_on", "note_off", "control_change")),
            [
                ("note_on", 0),
                ("note_off", 480),
                ("control_change", 480),
                ("note_on", 960),
                ("note_off", 1440),
            ],
        )

    def test_negative_control_change_time_rejected(self):
        with self.assertRaises(ValueError):
            Track().add_control_change(control=1, value=1, time=-1)


class TestArpeggio(unittest.TestCase):
    def _notes(self, t):
        return [Note(60, 70, 120, t), Note(64, 70, 120, t), Note(67, 70, 120, t)]

    def test_start_time_applies_to_every_note(self):
        arp = Arpeggio(self._notes(960), delay=120)
        self.assertEqual(
            [n.time for n in arp.get_sequential_notes()], [960, 1080, 1200]
        )

    def test_start_time_with_descending_loops(self):
        arp = Arpeggio(
            self._notes(960), delay=100, pattern=ArpeggioPattern.DESCENDING, loops=2
        )
        notes = arp.get_sequential_notes()
        self.assertEqual([n.time for n in notes], [960, 1060, 1160, 1260, 1360, 1460])
        self.assertEqual([n.pitch for n in notes], [67, 64, 60, 67, 64, 60])

    def test_pattern_accepts_string_value(self):
        arp = Arpeggio(self._notes(0), delay=10, pattern="descending")
        self.assertEqual(arp.pattern, ArpeggioPattern.DESCENDING)

    def test_invalid_pattern_rejected_at_construction(self):
        with self.assertRaises(ValueError):
            Arpeggio(self._notes(0), pattern="sideways")

    def test_invalid_delay_or_loops_rejected(self):
        with self.assertRaises(ValueError):
            Arpeggio(self._notes(0), delay=-1)
        with self.assertRaises(ValueError):
            Arpeggio(self._notes(0), loops=0)


class TestMidiGen(unittest.TestCase):
    def test_set_tempo_applies_to_tracks_added_later(self):
        midi = MidiGen(tempo=120)
        midi.set_tempo(90)
        track = midi.add_track()
        self.assertEqual(midi.tempo, 90)
        tempos = [
            round(mido.tempo2bpm(m.tempo))
            for m in track.get_track()
            if m.type == "set_tempo"
        ]
        self.assertEqual(tempos, [90])

    def test_set_key_signature_applies_to_tracks_added_later(self):
        midi = MidiGen()
        midi.set_key_signature(Key("E", "minor"))
        track = midi.add_track()
        self.assertEqual(midi.key_signature, Key("E", "minor"))
        keys = [m.key for m in track.get_track() if m.type == "key_signature"]
        self.assertEqual(keys, ["Em"])

    def test_repr_does_not_crash(self):
        self.assertIn("MidiGen", repr(MidiGen()))
        self.assertIn("Tempo: 120", str(MidiGen()))

    def test_add_track_with_channel(self):
        track = MidiGen().add_track(channel=9)
        self.assertEqual(track.channel, 9)

    def test_set_mode_dorian_writes_relative_major_signature(self):
        cases = {
            ("D", "dorian"): "C",
            ("E", "phrygian"): "C",
            ("F", "lydian"): "C",
            ("G", "mixolydian"): "C",
            ("B", "locrian"): "C",
            ("A", "aeolian"): "Am",
            ("A", "minor"): "Am",
            ("C", "ionian"): "C",
            ("F#", "dorian"): "E",
            ("Eb", "dorian"): "Db",
        }
        for (name, mode), expected in cases.items():
            with self.subTest(name=name, mode=mode):
                midi = MidiGen()
                midi.set_mode(name, mode)
                keys = {
                    m.key
                    for t in midi.tracks
                    for m in t.get_track()
                    if m.type == "key_signature"
                }
                self.assertEqual(keys, {expected})
                self.assertEqual(midi.mode, mode)

    def test_set_mode_rejects_bad_input(self):
        with self.assertRaises(ValueError):
            MidiGen().set_mode("D", "bebop")
        with self.assertRaises(ValueError):
            MidiGen().set_mode("H", "dorian")

    def test_time_signature_denominator_must_be_power_of_two(self):
        with self.assertRaises(ValueError):
            MidiGen(time_signature=(4, 3))
        with self.assertRaises(ValueError):
            MidiGen().set_time_signature(7, 6)
        MidiGen(time_signature=(7, 8))

    def test_every_valid_key_can_be_saved(self):
        names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        flats = {
            "Db": "C#",
            "Eb": "D#",
            "Gb": "F#",
            "Ab": "G#",
            "Bb": "A#",
            "Cb": "B",
            "Fb": "E",
        }

        def pitch_class(name):
            return names.index(flats.get(name, name))

        with tempfile.TemporaryDirectory() as d:
            for name, mode in VALID_KEYS:
                with self.subTest(key=(name, mode)):
                    path = MidiGen(key_signature=Key(name, mode)).save(
                        "k.mid", output_dir=d
                    )
                    written = [
                        m.key
                        for m in mido.MidiFile(path).tracks[0]
                        if m.type == "key_signature"
                    ][0]
                    self.assertEqual(written.endswith("m"), mode == "minor")
                    self.assertEqual(
                        pitch_class(written.rstrip("m")), pitch_class(name)
                    )

    def test_save_error_keeps_cause(self):
        midi = MidiGen()
        midi.get_active_track().add_note(Note(60, 64, 480, 0))
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError) as ctx:
                midi.save(os.path.join("missing", "x.mid"), output_dir=d)
        self.assertIsNotNone(ctx.exception.__cause__)


class TestMelody(unittest.TestCase):
    def test_random_walk_leaves_global_rng_alone(self):
        random.seed(123)
        expected = random.random()
        random.seed(123)
        Melody.random_walk(60, 8, Scale.major(60), seed=1)
        self.assertEqual(random.random(), expected)

    def test_random_walk_seed_output_unchanged(self):
        # Pinned from the pre-fix implementation so seeded melodies stay reproducible.
        melody = Melody.random_walk(60, 16, Scale.major(60), max_interval=3, seed=42)
        self.assertEqual(
            [n.pitch for n in melody],
            [60, 64, 60, 60, 64, 62, 60, 60, 60, 64, 60, 64, 67, 69, 64, 65],
        )

    def test_reverse_preserves_rests(self):
        melody = Melody([Note(60, 80, 480, 0), Note(64, 80, 240, 960)])  # rest 480..960
        reversed_melody = melody.reverse()
        self.assertEqual(
            [(n.pitch, n.time, n.duration) for n in reversed_melody],
            [(64, 0, 240), (60, 720, 480)],
        )

    def test_from_degrees_scale_without_octave(self):
        scale = [60, 62, 64, 65, 67, 69, 71]  # C major without the top C
        self.assertEqual(
            [n.pitch for n in Melody.from_degrees(scale, [1, 7, 8])], [60, 71, 72]
        )
        self.assertEqual([n.pitch for n in Melody.from_degrees([60], [1, 2])], [60, 72])

    def test_from_degrees_scale_with_octave_unchanged(self):
        self.assertEqual(
            [n.pitch for n in Melody.from_degrees(Scale.major(60), [1, 7, 8, 9])],
            [60, 71, 72, 74],
        )

    def test_reverse_keeps_start_offset(self):
        melody = Melody.from_note_names(
            "C4 E4 G4", durations=[480, 240, 960], start_time=1920
        )
        reversed_melody = melody.reverse()
        self.assertEqual(
            [(n.pitch, n.time) for n in reversed_melody],
            [(67, 1920), (64, 2880), (60, 3120)],
        )


class TestTrack(unittest.TestCase):
    def test_quantize_zero_step_raises_value_error(self):
        with self.assertRaises(ValueError):
            Track().quantize(100, 0)

    def test_drum_kit_on_non_drum_channel_warns(self):
        kit = DrumKit()
        kit.add_drum("Bass Drum 1")
        with self.assertWarns(UserWarning):
            Track(channel=0).add_drum_kit(kit)
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            Track(channel=9).add_drum_kit(kit)


class TestChordProgression(unittest.TestCase):
    def test_from_roman_numerals_defaults_to_back_to_back(self):
        progression = ChordProgression.from_roman_numerals(
            Key("C"), "I-V-vi-IV", duration=480
        )
        self.assertEqual([c.time for c in progression.chords], [0, 480, 960, 1440])
        self.assertEqual(progression.duration, 1920)

    def test_explicit_zero_spacing_still_stacks(self):
        progression = ChordProgression.from_roman_numerals(
            Key("C"), "I-V", duration=480, time_per_chord=0
        )
        self.assertEqual([c.time for c in progression.chords], [0, 0])

    def test_duration_is_time_span(self):
        stacked = ChordProgression(
            [Chord([Note(60, 64, 100, 0)]), Chord([Note(62, 64, 100, 0)])]
        )
        self.assertEqual(stacked.duration, 100)
        gapped = ChordProgression(
            [Chord([Note(60, 64, 100, 0)]), Chord([Note(62, 64, 100, 400)])]
        )
        self.assertEqual(gapped.duration, 500)

    def test_equality_with_other_types(self):
        progression = ChordProgression([])
        self.assertFalse(progression == None)  # noqa: E711
        self.assertNotEqual(progression, "I-V")

    def test_equal_progressions_compare_equal(self):
        a = ChordProgression.from_roman_numerals(Key("C"), "I-V")
        b = ChordProgression.from_roman_numerals(Key("C"), "I-V")
        self.assertEqual(a, b)
        self.assertNotEqual(a, ChordProgression.from_roman_numerals(Key("C"), "I-IV"))


class TestChord(unittest.TestCase):
    def test_add_note_to_empty_chord_sets_root(self):
        chord = Chord([])
        note = Note(60, 64, 480, 0)
        chord.add_note(note)
        self.assertIs(chord.root, note)

    def test_chord_does_not_mutate_callers_list(self):
        notes = [Note(60, 64, 480, 0)]
        chord = Chord(notes)
        chord.add_note(Note(64, 64, 480, 0))
        self.assertEqual(len(notes), 1)

    def test_empty_chord_has_zero_duration(self):
        self.assertEqual(Chord([]).duration, 0)


class TestRomanNumerals(unittest.TestCase):
    def names(self, key, mode, numeral):
        return get_note_names_for_pitches(
            sorted(get_chord_pitches(key, mode, numeral, octave=4))
        )

    def test_minor_key_leading_tone_chords_use_raised_seventh(self):
        self.assertEqual(self.names("A", "minor", "vii°"), ["D4", "G#4", "B4"])
        self.assertEqual(self.names("A", "minor", "vii°7"), ["D4", "F4", "G#4", "B4"])
        self.assertEqual(self.names("A", "minor", "viiø7"), ["D4", "F#4", "G#4", "B4"])

    def test_minor_key_major_six_and_seven_stay_natural(self):
        self.assertEqual(self.names("A", "minor", "VII"), ["D4", "G4", "B4"])
        self.assertEqual(self.names("A", "minor", "VI"), ["C4", "F4", "A4"])

    def test_minor_key_minor_sixth_chord_uses_raised_sixth(self):
        self.assertEqual(self.names("A", "minor", "vi°"), ["C4", "F#4", "A4"])

    def test_explicit_accidental_is_not_raised_again(self):
        self.assertEqual(
            get_chord_pitches("A", "minor", "bvii")[0] % 12, 6
        )  # F#: natural G lowered

    def test_major_key_unaffected(self):
        self.assertEqual(self.names("C", "major", "vii°"), ["D4", "F4", "B4"])
        self.assertEqual(self.names("C", "major", "vi"), ["C4", "E4", "A4"])

    def test_unsupported_modifiers_raise(self):
        for numeral in ["V9", "Isus4", "I6", "V65", "Imaj", "V7b9", "iV", "Vi"]:
            with self.subTest(numeral=numeral):
                with self.assertRaises(ValueError):
                    parse_roman_numeral(numeral)

    def test_section_rejects_unsupported_modifier(self):
        with self.assertRaises(ValueError):
            Section("Bad", 4, "I-V9-I")

    def test_major_seventh_spellings(self):
        for numeral in ["Imaj7", "IMAJ7", "IM7", "IΔ7", "IΔ"]:
            with self.subTest(numeral=numeral):
                self.assertEqual(
                    parse_roman_numeral(numeral).quality, ChordQuality.MAJOR_7
                )
        self.assertEqual(
            parse_roman_numeral("imaj7").quality, ChordQuality.MINOR_MAJOR_7
        )
        self.assertEqual(self.names("C", "minor", "imaj7"), ["C4", "D#4", "G4", "B4"])

    def test_octave_out_of_range_raises(self):
        with self.assertRaises(ValueError):
            get_chord_pitches("B", "major", "I", octave=9)
        with self.assertRaises(ValueError):
            get_chord_pitches("C", "major", "I", octave=-2)
        self.assertEqual(get_chord_pitches("C", "major", "I", octave=-1), [0, 4, 7])


class TestNoteValidation(unittest.TestCase):
    def test_negative_duration_or_time_rejected(self):
        with self.assertRaises(ValueError):
            Note(60, 64, -1, 0)
        with self.assertRaises(ValueError):
            Note(60, 64, 480, -1)

    def test_non_integer_duration_or_time_rejected(self):
        with self.assertRaises(ValueError):
            Note(60, 64, 480.5, 0)
        with self.assertRaises(ValueError):
            Note(60, 64, 480, 1.5)

    def test_bool_pitch_rejected(self):
        with self.assertRaises(ValueError):
            Note(True, 64, 480, 0)


class TestSectionValidation(unittest.TestCase):
    def test_length_must_be_positive_integer(self):
        for length in (0, -1, 1.5, "4"):
            with self.subTest(length=length):
                with self.assertRaises(ValueError):
                    Section("Bad", length, "I")


class TestTimeConverter(unittest.TestCase):
    def test_ticks_to_measures_rejects_zero_numerator(self):
        with self.assertRaises(ValueError):
            TimeConverter().ticks_to_measures(1920, time_signature_numerator=0)

    def test_conversions_round_instead_of_truncating(self):
        # These are exact tick counts that floating point lands just below
        tc = TimeConverter()
        self.assertEqual(tc.beats_to_ticks(2.05), 984)
        self.assertEqual(tc.beats_to_ticks(4.1), 1968)
        self.assertEqual(tc.measures_to_ticks(0.3, 3, 4), 432)
        self.assertEqual(tc.measures_to_ticks(0.6, 12, 8), 1728)

    def test_bpm_helper_matches_tempo_written_to_file(self):
        for bpm in range(20, 300):
            with self.subTest(bpm=bpm):
                self.assertEqual(
                    TimeConverter.bpm_to_microseconds_per_quarter(bpm),
                    mido.bpm2tempo(bpm),
                )

    def test_note_durations_round_for_odd_resolutions(self):
        tc = TimeConverter(ticks_per_quarter_note=100)
        self.assertEqual(tc.note_duration("triplet_whole"), 267)  # 266.67
        self.assertEqual(tc.note_duration("eighth"), 50)
        self.assertEqual(TimeConverter().note_duration("triplet_eighth"), 160)

    def test_resolution_must_be_positive_int(self):
        for tpq in (0, -480, 480.5):
            with self.subTest(tpq=tpq):
                with self.assertRaises(ValueError):
                    TimeConverter(ticks_per_quarter_note=tpq)


class TestKey(unittest.TestCase):
    def test_error_message_names_bad_key(self):
        with self.assertRaises(ValueError) as ctx:
            Key("Am", "minor")
        self.assertIn("Am", str(ctx.exception))
        self.assertLess(len(str(ctx.exception)), 300)

    def test_key_is_hashable(self):
        self.assertEqual(len({Key("C"), Key("C"), Key("A", "minor")}), 2)
        self.assertEqual({Key("C"): 1}[Key("C")], 1)

    def test_key_map_covers_full_midi_range(self):
        from midigen import KEY_MAP

        self.assertEqual(sorted(set(KEY_MAP.values())), list(range(128)))
        self.assertEqual(KEY_MAP["C-1"], 0)
        self.assertEqual(KEY_MAP["G9"], 127)
        self.assertEqual(KEY_MAP["C4"], 60)
        self.assertNotIn("G#9", KEY_MAP)
        self.assertEqual(Melody.from_note_names("C9 G9")[1].pitch, 127)

    def test_key_map_accepts_enharmonic_spellings(self):
        from midigen import KEY_MAP

        self.assertEqual(KEY_MAP["B#3"], 60)
        self.assertEqual(KEY_MAP["Cb4"], 59)
        self.assertEqual(KEY_MAP["E#4"], 65)
        self.assertEqual(KEY_MAP["Fb4"], 64)


class TestQuantize(unittest.TestCase):
    def test_ties_round_up_consistently(self):
        track = Track()
        self.assertEqual(
            [track.quantize(t, 480) for t in (240, 720, 1200, 1680)],
            [480, 960, 1440, 1920],
        )
        self.assertEqual(track.quantize(239, 480), 0)
        self.assertEqual(track.quantize(100, 30), 90)


class TestMidiFileCompatibility(unittest.TestCase):
    """MidiGen subclasses mido.MidiFile, so mido's helpers must work on it."""

    def setUp(self):
        self.midi = MidiGen(tempo=120)
        self.midi.get_active_track().add_note(Note(60, 64, 960, 0))

    def test_length_in_seconds(self):
        self.assertAlmostEqual(self.midi.length, 1.0)

    def test_iteration_and_merged_track(self):
        notes = [m for m in self.midi if m.type == "note_on"]
        self.assertEqual([m.note for m in notes], [60])
        self.assertIn("note_off", [m.type for m in self.midi.merged_track])

    def test_track_iterates_compiled_messages(self):
        track = self.midi.get_active_track()
        self.assertEqual(list(track), list(track.compile()))


class TestRound2Composition(unittest.TestCase):
    def test_arpeggio_patterns_follow_pitch_not_list_order(self):
        notes = [Note(64, 64, 100, 0), Note(60, 64, 100, 0), Note(67, 64, 100, 0)]
        pitches = lambda pattern, loops=1: [  # noqa: E731
            n.pitch
            for n in Arpeggio(
                notes, delay=100, pattern=pattern, loops=loops
            ).get_sequential_notes()
        ]
        self.assertEqual(pitches("ascending"), [60, 64, 67])
        self.assertEqual(pitches("descending"), [67, 64, 60])
        self.assertEqual(pitches("alternating", loops=2), [60, 64, 67, 67, 64, 60])

    def test_drum_names_ignore_case_spaces_and_hyphens(self):
        kit = DrumKit()
        for name in (
            "Open Hi-Hat",
            "open hi hat",
            "OPEN HIHAT",
            "closed hi-hat",
            "bass drum 1",
        ):
            kit.add_drum(name)
        self.assertEqual([n.pitch for n in kit.get_drums()], [46, 46, 46, 42, 36])
        with self.assertRaises(ValueError):
            kit.add_drum("Kazoo")
        with self.assertRaises(ValueError):
            kit.add_drum("Bass Drum 1", velocity=200)

    def test_random_walk_validates_length_and_interval(self):
        scale = Scale.major(60)
        for kwargs in (
            {"length": -1},
            {"length": 4, "max_interval": -2},
            {"length": 2.5},
        ):
            with self.subTest(**kwargs):
                with self.assertRaises(ValueError):
                    Melody.random_walk(60, scale=scale, **kwargs)
        self.assertEqual(len(Melody.random_walk(60, length=0, scale=scale)), 0)

    def test_track_add_melody(self):
        track = Track()
        melody = Melody.from_note_names("C4 E4 G4")
        track.add_melody(melody)
        self.assertEqual([n.pitch for n in track.notes], [60, 64, 67])

    def test_song_validates_key_and_tempo(self):
        for kwargs in (
            {"key": "C"},
            {"tempo": 0},
            {"tempo": -5},
            {"tempo": 120.5},
            {"tempo": True},
        ):
            with self.subTest(**kwargs):
                with self.assertRaises(ValueError):
                    Song(**kwargs)

    def test_song_and_section_reject_wrong_types_up_front(self):
        # Used to fail only inside compile() / with AttributeError on .strip()
        with self.assertRaises(TypeError):
            Song().add_section("Verse")
        with self.assertRaises(TypeError):
            Section("Verse", 2, 5)

    def test_reprs_are_readable(self):
        chord = Chord([Note(60, 64, 480, 0)])
        self.assertTrue(repr(chord).startswith("Chord([Note(pitch=60"))
        self.assertTrue(
            repr(ChordProgression([chord])).startswith("ChordProgression([Chord(")
        )
        self.assertEqual(repr(Track(channel=3)), "Track(channel=3, notes=0)")

    def test_containers_reject_non_note_items(self):
        with self.assertRaises(TypeError):
            Chord([60, 64])
        with self.assertRaises(TypeError):
            Chord([Note(60, 64, 1, 0)]).add_note(64)
        with self.assertRaises(TypeError):
            ChordProgression([[Note(60, 64, 1, 0)]])
        with self.assertRaises(TypeError):
            ChordProgression([]).add_chord("I")
        with self.assertRaises(TypeError):
            Melody([60])

    def test_set_active_track_rejects_out_of_range(self):
        midi = MidiGen()
        midi.add_track()
        for index in (-1, -5, 2, "0"):
            with self.subTest(index=index):
                with self.assertRaises(IndexError):
                    midi.set_active_track(index)
        midi.set_active_track(0)
        self.assertEqual(midi.active_track_index, 0)

    def test_saved_file_uses_ticks_per_beat(self):
        midi = MidiGen(tempo=120)
        midi.ticks_per_beat = 960
        midi.get_active_track().add_note(Note(60, 64, 960, 0))
        with tempfile.TemporaryDirectory() as tmp:
            saved = mido.MidiFile(midi.save("tpb.mid", tmp))
        self.assertEqual(saved.ticks_per_beat, 960)
        self.assertAlmostEqual(saved.length, midi.length)
        self.assertAlmostEqual(saved.length, 0.5)

    def test_note_equality_with_other_types(self):
        self.assertNotEqual(Note(60, 64, 480, 0), "C4")
        self.assertNotEqual(Note(60, 64, 480, 0), None)
        with self.assertRaises(TypeError):
            Note(60, 64, 480, 0) + True


if __name__ == "__main__":
    unittest.main()
