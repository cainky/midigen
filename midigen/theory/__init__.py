"""Music theory layer — pure logic, zero midigen dependencies."""

from midigen.theory.note import Note, NOTE_ON, NOTE_OFF
from midigen.theory.key import Key, KEY_MAP, VALID_KEYS
from midigen.theory.scale import Scale
from midigen.theory.time_utils import TimeConverter
from midigen.theory.roman import (
    ChordQuality,
    ParsedRomanNumeral,
    parse_roman_numeral,
    get_root_pitch,
    get_chord_pitches,
    get_note_names_for_pitches,
    CHORD_INTERVALS,
    MAJOR_SCALE_SEMITONES,
    MINOR_SCALE_SEMITONES,
)
