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
    The compiler respects Section.length by looping or truncating
    the chord progression to fit the requested duration:

    - Section("Verse", 8, "I-V-vi-IV") with 4/4 time:
      - 8 bars requested, 4 chords provided
      - Each chord = 1 bar, so 4 chords = 4 bars
      - Compiler loops the progression: I-V-vi-IV-I-V-vi-IV

    - Section("Intro", 2, "I-IV-V-I") with 4/4 time:
      - 2 bars requested, 4 chords provided
      - Compiler truncates: I-IV (first 2 bars only)
"""

from typing import Dict, List, Optional

from midigen.midigen import MidiGen
from midigen.key import Key
from midigen.note import Note
from midigen.chord import Chord, ChordProgression
from midigen.channel_pool import ChannelPool, ChannelExhaustedError
from midigen.instruments import INSTRUMENT_MAP


# Default timing constants
DEFAULT_TICKS_PER_BEAT = 480
DEFAULT_BEATS_PER_BAR = 4  # 4/4 time


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
    """

    def __init__(self, song: "Song"):
        """
        Initialize the compiler with a Song to compile.

        Args:
            song: The Song object containing musical intent.
        """
        self._song = song
        self._midigen = MidiGen(
            tempo=song.tempo,
            key_signature=song.key
        )
        self._channel_pool = ChannelPool()
        self._instrument_tracks: Dict[str, int] = {}  # instrument_name -> track_index
        self._compiled = False

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

        Allocates a MIDI channel and creates a track with the
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
            raise ChannelExhaustedError(
                f"Cannot add instrument '{name}': {e}"
            ) from e

        track_index = len(self._midigen.tracks)
        self._midigen.add_track()

        self._midigen.set_active_track(track_index)
        track = self._midigen.get_active_track()
        track.add_program_change(channel=channel, program=program)

        self._instrument_tracks[name] = track_index
        return track_index

    def add_drums(self, name: str = "Drums") -> int:
        """
        Add a drum track.

        Drums always use MIDI channel 9 per General MIDI specification.

        Args:
            name: A name for the drum track (default: "Drums").

        Returns:
            The track index for the drum track.
        """
        if name in self._instrument_tracks:
            return self._instrument_tracks[name]

        channel = self._channel_pool.allocate_drums()

        track_index = len(self._midigen.tracks)
        self._midigen.add_track()

        self._midigen.set_active_track(track_index)
        self._instrument_tracks[name] = track_index
        return track_index

    def compile(self) -> "MidiCompiler":
        """
        Compile all instruments in the song.

        Processes each instrument defined in the song, generating
        MIDI events for all sections.

        Returns:
            self for method chaining.
        """
        # First, ensure all instruments have tracks
        for instrument_name in self._song.instruments:
            if instrument_name not in self._instrument_tracks:
                if instrument_name == "Drums":
                    self.add_drums(instrument_name)
                else:
                    self.add_instrument(instrument_name)

        # Then compile each instrument
        for instrument_name in self._song.instruments:
            self._compile_instrument(instrument_name)

        self._compiled = True
        return self

    def compile_instrument(
        self,
        instrument_name: str,
        octave: int = 4,
        duration: int = 480
    ) -> "MidiCompiler":
        """
        Compile a single instrument's part.

        Args:
            instrument_name: The instrument to compile.
            octave: Base octave for chord voicing (default 4).
            duration: Duration per chord in ticks (default 480).

        Returns:
            self for method chaining.

        Raises:
            ValueError: If the instrument is not registered.
        """
        if instrument_name not in self._instrument_tracks:
            if instrument_name == "Drums":
                self.add_drums(instrument_name)
            else:
                self.add_instrument(instrument_name)

        self._compile_instrument(instrument_name, octave, duration)
        return self

    def _compile_instrument(
        self,
        instrument_name: str,
        octave: int = 4,
        duration: int = 480,
        beats_per_bar: int = DEFAULT_BEATS_PER_BAR
    ):
        """
        Internal method to compile an instrument's part.

        Processes all sections in the song, generating chord progressions
        for the specified instrument. Respects Section.length by looping
        or truncating the progression as needed.

        Args:
            instrument_name: Name of the instrument to compile.
            octave: Base octave for chord voicing.
            duration: Duration per chord in ticks.
            beats_per_bar: Number of beats per bar (default 4 for 4/4 time).
        """
        track_index = self._instrument_tracks[instrument_name]
        track = self._midigen.tracks[track_index]
        current_time = 0

        for section in self._song.sections:
            # Generate the base chord progression
            progression = ChordProgression.from_roman_numerals(
                key=self._song.key,
                progression_string=section.chord_progression,
                octave=octave,
                duration=duration,
                time_per_chord=duration
            )

            base_chords = progression.get_progression()
            if not base_chords:
                continue

            # Calculate target duration based on section.length (in bars)
            ticks_per_bar = beats_per_bar * duration
            target_duration = section.length * ticks_per_bar

            # Calculate how much music the base progression provides
            progression_duration = len(base_chords) * duration

            # Generate chords to fill the target duration (loop or truncate)
            section_chords = self._fill_section(
                base_chords, target_duration, duration, current_time, octave
            )

            # Add all chords to the track
            for chord in section_chords:
                track.add_chord(chord)

            # Advance time by the section's target duration
            current_time += target_duration

    def _fill_section(
        self,
        base_chords: List[Chord],
        target_duration: int,
        chord_duration: int,
        start_time: int,
        octave: int
    ) -> List[Chord]:
        """
        Fill a section with chords, looping or truncating as needed.

        Args:
            base_chords: The base chord progression to loop/truncate.
            target_duration: Target duration in ticks for the section.
            chord_duration: Duration of each chord in ticks.
            start_time: Starting time offset for the section.
            octave: Base octave for chord voicing.

        Returns:
            List of Chord objects filling the target duration.
        """
        result_chords = []
        current_time = start_time
        chord_index = 0
        num_base_chords = len(base_chords)

        while current_time < start_time + target_duration:
            # Get the next chord from the base progression (with wrapping)
            base_chord = base_chords[chord_index % num_base_chords]

            # Create a new chord with adjusted timing
            # We need to copy the notes to avoid mutating the original
            new_notes = []
            for note in base_chord.get_chord():
                new_notes.append(Note(
                    pitch=note.pitch,
                    velocity=note.velocity,
                    duration=note.duration,
                    time=current_time
                ))

            new_chord = Chord(new_notes)
            result_chords.append(new_chord)

            current_time += chord_duration
            chord_index += 1

        return result_chords

    def save(self, filename: str, output_dir: str = None) -> str:
        """
        Save the compiled MIDI to a file.

        If compile() hasn't been called, it will be called automatically.

        Args:
            filename: The name of the MIDI file (e.g., "my_song.mid").
            output_dir: Directory to save the file. If None, uses current directory.

        Returns:
            The full path to the saved file.
        """
        if not self._compiled:
            self.compile()

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


# Import Song here to avoid circular imports
# This is at the bottom because Song is imported for type hints only
from midigen.song import Song  # noqa: E402
