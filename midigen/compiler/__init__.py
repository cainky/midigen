"""
Compiler package for transforming musical intent into MIDI protocol.

This package bridges the gap between high-level musical concepts
(songs, sections, progressions) and low-level MIDI implementation.
"""

from .midi_compiler import MidiCompiler

__all__ = ["MidiCompiler"]
