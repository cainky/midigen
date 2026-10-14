"""
MIDI Compiler - Transforms musical intent into MIDI protocol.

The MidiCompiler bridges high-level musical concepts (songs, sections,
progressions) with low-level MIDI implementation. It handles:

- Channel allocation (via ChannelPool)
- Track creation and program changes
- Section processing and chord generation
- Timing calculations
- Section length enforcement (looping/truncating progressions)

Example:
    >>> song = Song(key=Key("C", "major"), tempo=120)
    >>> song.add_section(Section("Verse", 8, "I-V-vi-IV"))
    >>> song.add_instrument("Acoustic Grand Piano")
    >>>
    >>> compiler = MidiCompiler(song)
    >>> compiler.compile()
    >>> compiler.save("output.mid")

Section Length Behavior:
    Section.length is in bars of 4/4 (1920 ticks at 480 ticks per beat).
    Each chord lasts ``duration`` ticks (default 480, one beat), and the
    progression is looped or truncated to fill the section:

    - Section("Verse", 2, "I-V-vi-IV") with the default duration:
      8 beats, 4 chords -> I-V-vi-IV-I-V-vi-IV

    - Section("Verse", 4, "I-V-vi-IV") with compile_instrument(..., duration=1920):
      one chord per bar -> I-V-vi-IV

    - Section("Intro", 1, "I-IV-V-I-ii-vi") with the default duration:
      4 beats -> I-IV-V-I

    A chord that would cross the end of a section is cut at the boundary.

Drum tracks:
    Drum tracks (Song.add_drums) go on channel 9 and get no generated chords.
    Fill them with compiler.get_track("Drums").add_drum_kit(kit).
"""

from typing import Dict, List, Tuple

from midigen.api.midigen import MidiGen
from midigen.api.song import Song
from midigen.theory.note import Note
from midigen.composition.chord import Chord
from midigen.composition.progression import ChordProgression
from midigen.protocol.channel_pool import ChannelPool, ChannelExhaustedError
from midigen.protocol.instruments import INSTRUMENT_MAP


# Default timing constants
DEFAULT_TICKS_PER_BEAT = 480
DEFAULT_BEATS_PER_BAR = 4  # 4/4 time
DEFAULT_OCTAVE = 4
DEFAULT_CHORD_DURATION = DEFAULT_TICKS_PER_BEAT


class MidiCompiler:
    """
    Compiles a Song into MIDI output.

    The compiler is responsible for all MIDI protocol details:
    - Allocating channels to instruments
    - Creating tracks with proper program changes
    - Processing sections into MIDI events
    - Managing timing and delta calculations

    This separates the musical domain (Song, Section, Chord) from
    the protocol domain (MIDI channels, program numbers, ticks).

    Compiling is repeatable: recompiling an instrument replaces the notes the
    compiler generated for it earlier and leaves notes you added yourself.
    """

    def __init__(self, song: "Song"):
        """
        Initialize the compiler with a Song to compile.

        Args:
            song: The Song object containing musical intent.
        """
        self._song = song
        self._midigen = MidiGen(tempo=song.tempo, key_signature=song.key)
        self._channel_pool = ChannelPool()
        self._instrument_tracks: Dict[str, int] = {}  # instrument_name -> track_index
        self._drum_tracks = set()
        # Notes generated per instrument, and the (octave, duration) used for them
        self._generated_notes: Dict[str, List[Note]] = {}
        self._part_settings: Dict[str, Tuple[int, int]] = {}

    @property
    def midigen(self) -> MidiGen:
        """Access the underlying MidiGen for advanced operations."""
        return self._midigen

    @property
    def available_channels(self) -> int:
        """Number of melodic channels still available."""
        return self._channel_pool.available_count

    def add_instrument(self, name: str) -> int:
        """
        Register an instrument and create its track.

        Allocates a MIDI channel and creates a track on that channel with the
        appropriate program change.

        Args:
            name: The instrument name (must be in INSTRUMENT_MAP).

        Returns:
            The track index for this instrument.

        Raises:
            ValueError: If the instrument name is not found.
            ChannelExhaustedError: If all 15 melodic channels are in use.
        """
        if name in self._instrument_tracks:
            return self._instrument_tracks[name]

        program = INSTRUMENT_MAP.get(name)
        if program is None:
            raise ValueError(f"Instrument '{name}' not found in INSTRUMENT_MAP.")

        try:
            channel = self._channel_pool.allocate(name)
        except ChannelExhaustedError as e:
            raise ChannelExhaustedError(f"Cannot add instrument '{name}': {e}") from e

        track = self._midigen.add_track(channel=channel)
        track.add_program_change(program=program)

        self._instrument_tracks[name] = len(self._midigen.tracks) - 1
        return self._instrument_tracks[name]

    def add_drums(self, name: str = "Drums") -> int:
        """
        Add a drum track.

        Drums always use MIDI channel 9 per General MIDI specification.
        The compiler does not generate notes for drum tracks; add a DrumKit
        with get_track(name).add_drum_kit(kit).

        Args:
            name: A name for the drum track (default: "Drums").

        Returns:
            The track index for the drum track.
        """
        if name in self._instrument_tracks:
            return self._instrument_tracks[name]

        self._midigen.add_track(channel=self._channel_pool.allocate_drums())
        self._drum_tracks.add(name)
        self._instrument_tracks[name] = len(self._midigen.tracks) - 1
        return self._instrument_tracks[name]

    def compile(self) -> "MidiCompiler":
        """
        Compile all instruments in the song.

        Each instrument is (re)generated with the octave and duration it was last
        compiled with via compile_instrument(), or the defaults (octave 4, one
        beat per chord). Calling compile() again does not duplicate notes.

        Returns:
            self for method chaining.
        """
        for instrument_name in self._song.instruments:
            self._ensure_track(instrument_name)

        for instrument_name in self._song.instruments:
            self._compile_instrument(
                instrument_name,
                *self._part_settings.get(
                    instrument_name, (DEFAULT_OCTAVE, DEFAULT_CHORD_DURATION)
                ),
            )

        return self

    def compile_instrument(
        self,
        instrument_name: str,
        octave: int = DEFAULT_OCTAVE,
        duration: int = DEFAULT_CHORD_DURATION,
    ) -> "MidiCompiler":
        """
        Compile a single instrument's part, replacing any part generated for it before.

        Args:
            instrument_name: The instrument to compile.
            octave: Octave the chord tones are placed in (default 4).
            duration: Duration per chord in ticks (default 480, one beat).
                      1920 gives one chord per 4/4 bar.

        Returns:
            self for method chaining.

        Raises:
            ValueError: If the instrument name is unknown, or octave/duration are invalid.
        """
        if not isinstance(duration, int) or isinstance(duration, bool) or duration <= 0:
            raise ValueError(
                f"Chord duration must be a positive integer number of ticks, got {duration!r}"
            )

        self._ensure_track(instrument_name)
        self._compile_instrument(instrument_name, octave, duration)
        return self

    def save(self, filename: str, output_dir: str = None) -> str:
        """
        Save the compiled MIDI to a file.

        Instruments that have not been compiled yet are compiled with the
        defaults first; parts already compiled are kept as they are.

        Args:
            filename: The name of the MIDI file (e.g., "my_song.mid").
            output_dir: Directory to save the file. If None, uses current directory.

        Returns:
            The full path to the saved file.
        """
        for instrument_name in self._song.instruments:
            if instrument_name not in self._generated_notes:
                self.compile_instrument(instrument_name)

        return self._midigen.save(filename, output_dir)

    def get_track(self, instrument_name: str):
        """
        Get the Track object for an instrument.

        Args:
            instrument_name: The instrument name.

        Returns:
            The Track object, or None if not found.
        """
        track_index = self._instrument_tracks.get(instrument_name)
        if track_index is not None:
            return self._midigen.tracks[track_index]
        return None

    def _ensure_track(self, instrument_name: str) -> None:
        if instrument_name in self._instrument_tracks:
            return
        if instrument_name == "Drums" or instrument_name in self._song.drums:
            self.add_drums(instrument_name)
        else:
            self.add_instrument(instrument_name)

    def _compile_instrument(
        self,
        instrument_name: str,
        octave: int,
        duration: int,
        beats_per_bar: int = DEFAULT_BEATS_PER_BAR,
    ) -> None:
        """
        Generate an instrument's part for every section, replacing its previous part.

        Respects Section.length (in bars) by looping or truncating the progression.
        Drum tracks get no generated notes.
        """
        track = self._midigen.tracks[self._instrument_tracks[instrument_name]]

        # Build the whole part before touching the track, so an error leaves the old part in place
        chords: List[Chord] = []
        if instrument_name not in self._drum_tracks:
            ticks_per_bar = beats_per_bar * DEFAULT_TICKS_PER_BEAT
            section_start = 0
            for section in self._song.sections:
                section_ticks = section.length * ticks_per_bar
                progression = ChordProgression.from_roman_numerals(
                    key=self._song.key,
                    progression_string=section.chord_progression,
                    octave=octave,
                    duration=duration,
                )
                chords.extend(
                    self._fill_section(
                        progression.get_progression(),
                        section_start,
                        section_ticks,
                        duration,
                    )
                )
                section_start += section_ticks

        previous = {id(note) for note in self._generated_notes.get(instrument_name, ())}
        if previous:
            track.notes = [note for note in track.notes if id(note) not in previous]

        generated: List[Note] = []
        for chord in chords:
            track.add_chord(chord)
            generated.extend(chord.get_chord())

        self._generated_notes[instrument_name] = generated
        self._part_settings[instrument_name] = (octave, duration)

    @staticmethod
    def _fill_section(
        base_chords: List[Chord],
        start_time: int,
        section_ticks: int,
        chord_duration: int,
    ) -> List[Chord]:
        """
        Fill a section with chords, looping or truncating the progression as needed.

        Args:
            base_chords: The base chord progression to loop/truncate.
            start_time: Starting tick of the section.
            section_ticks: Length of the section in ticks.
            chord_duration: Duration of each chord in ticks.

        Returns:
            Chords filling the section; the last one is cut at the section end.
        """
        if not base_chords:
            return []

        end_time = start_time + section_ticks
        result_chords = []
        for index, chord_time in enumerate(range(start_time, end_time, chord_duration)):
            base_chord = base_chords[index % len(base_chords)]
            length = min(chord_duration, end_time - chord_time)
            result_chords.append(
                Chord(
                    [
                        Note(
                            pitch=note.pitch,
                            velocity=note.velocity,
                            duration=length,
                            time=chord_time,
                        )
                        for note in base_chord.get_chord()
                    ]
                )
            )
        return result_chords
