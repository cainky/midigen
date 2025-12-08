"""
Song - High-level musical composition container.

The Song class represents the musical intent of a composition:
- Key and tempo
- Sections (verse, chorus, bridge, etc.)
- Instrument definitions

For MIDI generation, use the MidiCompiler:

    >>> from midigen import Song, Section, Key
    >>> from midigen.compiler import MidiCompiler
    >>>
    >>> song = Song(key=Key("C", "major"), tempo=120)
    >>> song.add_section(Section("Verse", 8, "I-V-vi-IV"))
    >>> song.add_instrument("Acoustic Grand Piano")
    >>>
    >>> compiler = MidiCompiler(song)
    >>> compiler.compile()
    >>> compiler.save("output.mid")

For backward compatibility, Song still supports the legacy API:
    >>> song.generate("Acoustic Grand Piano")  # Deprecated
    >>> song.save("output.mid")  # Deprecated
"""

import warnings
from typing import List, Set

from midigen.key import Key
from midigen.section import Section


class Song:
    """
    High-level song composition container.

    A Song is a pure data container that holds:
    - Musical metadata (key, tempo)
    - Sections (verse, chorus, bridge, etc.)
    - Instrument definitions (what instruments to use)

    The actual MIDI generation is handled by MidiCompiler.

    Example (New API):
        >>> song = Song(key=Key("C", "major"), tempo=120)
        >>> song.add_section(Section("Verse", 8, "I-V-vi-IV"))
        >>> song.add_instrument("Acoustic Grand Piano")
        >>>
        >>> from midigen.compiler import MidiCompiler
        >>> compiler = MidiCompiler(song)
        >>> compiler.compile().save("output.mid")

    Example (Legacy API - Deprecated):
        >>> song = Song(key=Key("C", "major"), tempo=120)
        >>> song.add_section(Section("Verse", 8, "I-V-vi-IV"))
        >>> song.add_instrument("Acoustic Grand Piano")
        >>> song.generate("Acoustic Grand Piano")
        >>> song.save("output.mid")
    """

    def __init__(self, tempo: int = 120, key: Key = None):
        """
        Initialize a new Song.

        Args:
            tempo: Beats per minute (default 120).
            key: The key signature (default C major).
        """
        self.tempo = tempo
        self.key = key if key else Key("C")
        self.sections: List[Section] = []
        self.instruments: Set[str] = set()

        # Lazy-initialized compiler for backward compatibility
        self._compiler = None

    def add_section(self, section: Section) -> "Song":
        """
        Add a section to the song.

        Args:
            section: A Section object (verse, chorus, etc.).

        Returns:
            self for method chaining.
        """
        self.sections.append(section)
        # Invalidate any existing compiler
        self._compiler = None
        return self

    def add_instrument(self, name: str) -> "Song":
        """
        Register an instrument to be used in the song.

        This method now only records the instrument name. The actual
        MIDI channel allocation happens during compilation.

        Args:
            name: The instrument name (must be in INSTRUMENT_MAP).

        Returns:
            self for method chaining.

        Raises:
            ValueError: If the instrument name is not valid.
        """
        from midigen.instruments import INSTRUMENT_MAP

        if name not in INSTRUMENT_MAP:
            raise ValueError(f"Instrument '{name}' not found in INSTRUMENT_MAP.")

        self.instruments.add(name)
        # Invalidate any existing compiler
        self._compiler = None
        return self

    def add_drums(self, name: str = "Drums") -> "Song":
        """
        Register a drum track.

        Args:
            name: A name for the drum track (default: "Drums").

        Returns:
            self for method chaining.
        """
        self.instruments.add(name)
        # Invalidate any existing compiler
        self._compiler = None
        return self

    # =========================================================================
    # LEGACY API (Backward Compatibility)
    # These methods delegate to MidiCompiler but are deprecated.
    # =========================================================================

    def _get_compiler(self):
        """Get or create the compiler for legacy operations."""
        if self._compiler is None:
            from midigen.compiler import MidiCompiler
            self._compiler = MidiCompiler(self)
            # Pre-register all instruments
            for name in self.instruments:
                if name == "Drums":
                    self._compiler.add_drums(name)
                else:
                    self._compiler.add_instrument(name)
        return self._compiler

    @property
    def midigen(self):
        """
        Access the underlying MidiGen object.

        Deprecated: Use MidiCompiler instead.
        """
        return self._get_compiler().midigen

    @property
    def available_channels(self) -> int:
        """
        Number of melodic channels still available.

        Deprecated: Use MidiCompiler.available_channels instead.
        """
        return self._get_compiler().available_channels

    def generate(self, instrument_name: str, octave: int = 4, duration: int = 480):
        """
        Generate MIDI events for an instrument.

        Deprecated: Use MidiCompiler.compile_instrument() instead.

        Args:
            instrument_name: The instrument to generate.
            octave: Base octave for chords (default 4).
            duration: Duration per chord in ticks (default 480).
        """
        warnings.warn(
            "Song.generate() is deprecated. Use MidiCompiler instead:\n"
            "  compiler = MidiCompiler(song)\n"
            "  compiler.compile_instrument(instrument_name)",
            DeprecationWarning,
            stacklevel=2
        )
        self._get_compiler().compile_instrument(instrument_name, octave, duration)

    def save(self, filename: str, output_dir: str = None) -> str:
        """
        Save the song to a MIDI file.

        Deprecated: Use MidiCompiler.save() instead.

        Args:
            filename: The name of the MIDI file.
            output_dir: Directory to save the file.

        Returns:
            The full path to the saved file.
        """
        warnings.warn(
            "Song.save() is deprecated. Use MidiCompiler instead:\n"
            "  compiler = MidiCompiler(song)\n"
            "  compiler.compile().save(filename)",
            DeprecationWarning,
            stacklevel=2
        )
        return self._get_compiler().save(filename, output_dir)
