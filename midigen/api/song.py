"""
Song - High-level musical composition container.

The Song class represents the musical intent of a composition:
- Key and tempo
- Sections (verse, chorus, bridge, etc.)
- Instrument definitions

For MIDI generation, use the MidiCompiler:

    >>> from midigen import Song, Section, Key, MidiCompiler
    >>>
    >>> song = Song(key=Key("C", "major"), tempo=120)
    >>> song.add_section(Section("Verse", 8, "I-V-vi-IV"))
    >>> song.add_instrument("Acoustic Grand Piano")
    >>>
    >>> compiler = MidiCompiler(song)
    >>> compiler.compile()
    >>> compiler.save("output.mid")
"""

from typing import List, Set

from midigen.theory.key import Key
from midigen.composition.section import Section
from midigen.protocol.instruments import INSTRUMENT_MAP


class Song:
    """
    High-level song composition container.

    A Song is a pure data container that holds:
    - Musical metadata (key, tempo)
    - Sections (verse, chorus, bridge, etc.)
    - Instrument definitions (what instruments to use)

    The actual MIDI generation is handled by MidiCompiler.

    Example:
        >>> song = Song(key=Key("C", "major"), tempo=120)
        >>> song.add_section(Section("Verse", 8, "I-V-vi-IV"))
        >>> song.add_instrument("Acoustic Grand Piano")
        >>>
        >>> from midigen.api.compiler import MidiCompiler
        >>> compiler = MidiCompiler(song)
        >>> compiler.compile().save("output.mid")
    """

    def __init__(self, tempo: int = 120, key: Key = None):
        self.tempo = tempo
        self.key = key if key else Key("C")
        self.sections: List[Section] = []
        self.instruments: Set[str] = set()

    def add_section(self, section: Section) -> "Song":
        """Add a section to the song. Returns self for chaining."""
        self.sections.append(section)
        return self

    def add_instrument(self, name: str) -> "Song":
        """Register an instrument. Raises ValueError if name is invalid."""
        if name not in INSTRUMENT_MAP:
            raise ValueError(f"Instrument '{name}' not found in INSTRUMENT_MAP.")
        self.instruments.add(name)
        return self

    def add_drums(self, name: str = "Drums") -> "Song":
        """Register a drum track. Returns self for chaining."""
        self.instruments.add(name)
        return self
