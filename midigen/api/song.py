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

from typing import List

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

    ``instruments`` lists every melodic instrument and drum track in the order
    they were added (that order decides track and channel order). ``drums``
    lists the names registered with add_drums().

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
        if not isinstance(tempo, int) or isinstance(tempo, bool) or tempo <= 0:
            raise ValueError(f"Tempo must be a positive integer (BPM), got {tempo!r}")
        if key is not None and not isinstance(key, Key):
            raise ValueError(
                f"key must be a Key object, e.g. Key('C') or Key('A', 'minor'), got {key!r}"
            )
        self.tempo = tempo
        self.key = key if key else Key("C")
        self.sections: List[Section] = []
        self.instruments: List[str] = []
        self.drums: List[str] = []

    def add_section(self, section: Section) -> "Song":
        """Add a section to the song. Returns self for chaining."""
        if not isinstance(section, Section):
            raise TypeError(
                f"Expected a Section object, e.g. Section('Verse', 8, 'I-V-vi-IV'), "
                f"got {type(section).__name__}"
            )
        self.sections.append(section)
        return self

    def add_instrument(self, name: str) -> "Song":
        """Register an instrument. Raises ValueError if name is invalid."""
        if name not in INSTRUMENT_MAP:
            raise ValueError(f"Instrument '{name}' not found in INSTRUMENT_MAP.")
        if name not in self.instruments:
            self.instruments.append(name)
        return self

    def add_drums(self, name: str = "Drums") -> "Song":
        """
        Register a drum track (MIDI channel 9). Returns self for chaining.

        The compiler creates the track but does not generate chords for it;
        add a DrumKit with compiler.get_track(name).add_drum_kit(kit).
        """
        if name in self.instruments and name not in self.drums:
            raise ValueError(f"'{name}' is already registered as a melodic instrument.")
        if name not in self.drums:
            self.drums.append(name)
            self.instruments.append(name)
        return self
