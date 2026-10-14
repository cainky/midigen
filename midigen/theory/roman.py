"""
Native Roman Numeral Parser for Chord Progressions.

This module replaces music21 for Roman numeral chord analysis,
providing a lightweight implementation for common chord progressions.

Supports:
- Major chords: I, II, III, IV, V, VI, VII
- Minor chords: i, ii, iii, iv, v, vi, vii
- Diminished: vii°, viio, viidim
- Diminished seventh: vii°7, viio7, viidim7
- Half-diminished seventh: viiø, viiø7
- Augmented: V+, Vaug
- Seventh chords: V7 (dominant), ii7 (minor)
- Major seventh: Imaj7, IM7, IΔ7, IΔ (lowercase imaj7 = minor-major seventh)
- Root accidentals: bVII, #IV (also ♭ / ♯)

Any other suffix (inversions such as V6 or V65, extensions such as V9,
suspensions such as Isus4) raises ValueError instead of being silently
dropped.

In minor keys, chords built on the 6th and 7th degrees follow the common
practice (and music21) convention: major/augmented chords (VI, VII, VII7)
use the natural minor degree, while minor/diminished chords (vi, vi°, vii°,
vii°7, viiø7) use the raised degree, so vii° in A minor is G#-B-D.
"""

import re
from typing import List
from dataclasses import dataclass
from enum import Enum


class ChordQuality(Enum):
    """Chord quality types."""

    MAJOR = "major"
    MINOR = "minor"
    DIMINISHED = "diminished"
    AUGMENTED = "augmented"
    DOMINANT_7 = "dominant_7"
    MAJOR_7 = "major_7"
    MINOR_7 = "minor_7"
    MINOR_MAJOR_7 = "minor_major_7"
    DIMINISHED_7 = "diminished_7"
    HALF_DIMINISHED_7 = "half_diminished_7"


# Semitones from root for each scale degree in major scale
# Degree: 1=0, 2=2, 3=4, 4=5, 5=7, 6=9, 7=11
MAJOR_SCALE_SEMITONES = {
    1: 0,  # I (C in C major)
    2: 2,  # II (D in C major)
    3: 4,  # III (E in C major)
    4: 5,  # IV (F in C major)
    5: 7,  # V (G in C major)
    6: 9,  # VI (A in C major)
    7: 11,  # VII (B in C major)
}

# Natural minor scale semitones (relative to major)
# Same as major but with flat 3, 6, 7
MINOR_SCALE_SEMITONES = {
    1: 0,  # i (A in A minor)
    2: 2,  # ii (B in A minor)
    3: 3,  # III (C in A minor) - flat 3
    4: 5,  # iv (D in A minor)
    5: 7,  # v (E in A minor)
    6: 8,  # VI (F in A minor) - flat 6
    7: 10,  # VII (G in A minor) - flat 7
}

# Chord intervals (semitones from root)
CHORD_INTERVALS = {
    ChordQuality.MAJOR: [0, 4, 7],  # Root, M3, P5
    ChordQuality.MINOR: [0, 3, 7],  # Root, m3, P5
    ChordQuality.DIMINISHED: [0, 3, 6],  # Root, m3, d5
    ChordQuality.AUGMENTED: [0, 4, 8],  # Root, M3, A5
    ChordQuality.DOMINANT_7: [0, 4, 7, 10],  # Root, M3, P5, m7
    ChordQuality.MAJOR_7: [0, 4, 7, 11],  # Root, M3, P5, M7
    ChordQuality.MINOR_7: [0, 3, 7, 10],  # Root, m3, P5, m7
    ChordQuality.MINOR_MAJOR_7: [0, 3, 7, 11],  # Root, m3, P5, M7
    ChordQuality.DIMINISHED_7: [0, 3, 6, 9],  # Root, m3, d5, d7
    ChordQuality.HALF_DIMINISHED_7: [0, 3, 6, 10],  # Root, m3, d5, m7
}

# Note name to semitone offset from C
NOTE_TO_SEMITONE = {
    "C": 0,
    "D": 2,
    "E": 4,
    "F": 5,
    "G": 7,
    "A": 9,
    "B": 11,
}

# Accidental adjustments
ACCIDENTAL_ADJUSTMENT = {
    "#": 1,
    "♯": 1,
    "b": -1,
    "♭": -1,
    "": 0,
}


_DEGREES = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7}

# Suffix (lowercased) -> (quality for uppercase numeral, quality for lowercase numeral)
_MODIFIER_QUALITIES = {
    "": (ChordQuality.MAJOR, ChordQuality.MINOR),
    "7": (ChordQuality.DOMINANT_7, ChordQuality.MINOR_7),
    "maj7": (ChordQuality.MAJOR_7, ChordQuality.MINOR_MAJOR_7),
    "°": (ChordQuality.DIMINISHED, ChordQuality.DIMINISHED),
    "o": (ChordQuality.DIMINISHED, ChordQuality.DIMINISHED),
    "dim": (ChordQuality.DIMINISHED, ChordQuality.DIMINISHED),
    "°7": (ChordQuality.DIMINISHED_7, ChordQuality.DIMINISHED_7),
    "o7": (ChordQuality.DIMINISHED_7, ChordQuality.DIMINISHED_7),
    "dim7": (ChordQuality.DIMINISHED_7, ChordQuality.DIMINISHED_7),
    "ø": (ChordQuality.HALF_DIMINISHED_7, ChordQuality.HALF_DIMINISHED_7),
    "ø7": (ChordQuality.HALF_DIMINISHED_7, ChordQuality.HALF_DIMINISHED_7),
    "+": (ChordQuality.AUGMENTED, ChordQuality.AUGMENTED),
    "aug": (ChordQuality.AUGMENTED, ChordQuality.AUGMENTED),
}

# Major-seventh spellings that must be matched before lowercasing ('M7' vs 'm7', 'Δ' vs 'δ')
_CASE_SENSITIVE_MAJOR_7 = ("M7", "Δ", "Δ7", "∆", "∆7")

# Qualities that put a minor-key 6th/7th-degree chord on the raised degree
_RAISED_IN_MINOR = {
    ChordQuality.MINOR,
    ChordQuality.DIMINISHED,
    ChordQuality.MINOR_7,
    ChordQuality.MINOR_MAJOR_7,
    ChordQuality.DIMINISHED_7,
    ChordQuality.HALF_DIMINISHED_7,
}


@dataclass
class ParsedRomanNumeral:
    """Parsed Roman numeral information."""

    degree: int  # Scale degree (1-7)
    quality: ChordQuality  # Chord quality
    is_uppercase: bool  # True if uppercase (originally major)
    accidental: str  # '', '#', or 'b' for root alteration
    original: str  # Original string


def parse_roman_numeral(numeral: str) -> ParsedRomanNumeral:
    """
    Parse a Roman numeral string into its components.

    Args:
        numeral: Roman numeral string (e.g., 'I', 'V7', 'vi', 'vii°')

    Returns:
        ParsedRomanNumeral with degree, quality, and other info.

    Raises:
        ValueError: If the numeral cannot be parsed.
    """
    original = numeral
    numeral = numeral.strip()

    if not numeral:
        raise ValueError("Empty Roman numeral")

    # Check for accidentals at the start (e.g., bVII, #IV)
    accidental = ""
    if numeral[0] in "#♯":
        accidental = "#"
        numeral = numeral[1:]
    elif numeral[0] in "b♭":
        accidental = "b"
        numeral = numeral[1:]

    # Extract the Roman numeral part (before any modifiers)
    # Pattern: Roman numeral, then optional modifiers (°, o, dim, 7, maj7, etc.)
    match = re.match(r"^([IiVv]+)(.*)", numeral)
    if not match:
        raise ValueError(f"Cannot parse Roman numeral: {original}")

    rn_part = match.group(1)
    modifier = match.group(2)

    # Case carries meaning, so mixed case like "iV" is ambiguous
    if not (rn_part.isupper() or rn_part.islower()):
        raise ValueError(f"Mixed-case Roman numeral: {original!r}")
    is_uppercase = rn_part.isupper()

    degree = _DEGREES.get(rn_part.upper())
    if degree is None:
        raise ValueError(f"Invalid Roman numeral: {rn_part}")

    quality = _determine_quality(is_uppercase, modifier, original)

    return ParsedRomanNumeral(
        degree=degree,
        quality=quality,
        is_uppercase=is_uppercase,
        accidental=accidental,
        original=original,
    )


def _determine_quality(
    is_uppercase: bool, modifier: str, original: str = ""
) -> ChordQuality:
    """
    Determine chord quality from case and modifier.

    Args:
        is_uppercase: True if Roman numeral was uppercase
        modifier: Modifier string (e.g., '7', '°', 'dim', 'maj7')
        original: Full numeral, used in error messages

    Returns:
        ChordQuality enum value.

    Raises:
        ValueError: If the modifier is not supported.
    """
    modifier = modifier.strip()
    if modifier in _CASE_SENSITIVE_MAJOR_7:
        modifier = "maj7"

    qualities = _MODIFIER_QUALITIES.get(modifier.lower())
    if qualities is None:
        # ASCII-only message so it prints on any console encoding
        raise ValueError(
            f"Unsupported chord suffix {modifier!a} in {original!a}. Supported suffixes: "
            "7, maj7, M7, o, dim, o7, dim7, +, aug (plus the degree sign, slashed-o and delta symbols). "
            "Inversions, extensions and suspensions are not supported."
        )
    return qualities[0] if is_uppercase else qualities[1]


def get_root_pitch(
    key_name: str, key_mode: str, degree: int, accidental: str = ""
) -> int:
    """
    Get the MIDI pitch of the root note for a scale degree.

    Args:
        key_name: Key name (e.g., 'C', 'F#', 'Bb')
        key_mode: Key mode ('major' or 'minor')
        degree: Scale degree (1-7)
        accidental: Optional accidental ('#' or 'b') to apply to root

    Returns:
        MIDI pitch number for the root (in octave 0, add 12*octave for desired octave).
    """
    # Get base pitch of key
    key_letter = key_name[0].upper()
    key_accidental = key_name[1:] if len(key_name) > 1 else ""

    base_pitch = NOTE_TO_SEMITONE.get(key_letter, 0)
    base_pitch += ACCIDENTAL_ADJUSTMENT.get(key_accidental, 0)

    # Get semitones for degree based on mode
    if key_mode.lower() == "minor":
        scale_semitones = MINOR_SCALE_SEMITONES
    else:
        scale_semitones = MAJOR_SCALE_SEMITONES

    degree_semitones = scale_semitones.get(degree, 0)

    # Apply accidental to root
    accidental_adjustment = ACCIDENTAL_ADJUSTMENT.get(accidental, 0)

    # Calculate root pitch (mod 12 to get pitch class)
    root_pitch = (base_pitch + degree_semitones + accidental_adjustment) % 12

    return root_pitch


def get_chord_pitches(
    key_name: str, key_mode: str, numeral: str, octave: int = 4
) -> List[int]:
    """
    Get MIDI pitches for a Roman numeral chord.

    Every chord tone is placed inside the given octave (C to B), so upper chord
    tones can sound below the root: V in C major at octave 4 is G4, B4, D4.
    This keeps all chords in the same register but is not voice leading.

    Args:
        key_name: Key name (e.g., 'C', 'G', 'F#')
        key_mode: Key mode ('major' or 'minor')
        numeral: Roman numeral (e.g., 'I', 'V7', 'vi')
        octave: Base octave for the chord (default 4)

    Returns:
        List of MIDI pitch numbers for the chord.

    Raises:
        ValueError: If the numeral is invalid or the octave puts the chord outside 0-127.
    """
    parsed = parse_roman_numeral(numeral)

    # Get root pitch class (0-11)
    root_pitch_class = get_root_pitch(
        key_name, key_mode, parsed.degree, parsed.accidental
    )
    if (
        key_mode.lower() == "minor"
        and parsed.degree in (6, 7)
        and not parsed.accidental
        and parsed.quality in _RAISED_IN_MINOR
    ):
        root_pitch_class = (root_pitch_class + 1) % 12

    # Get chord intervals
    intervals = CHORD_INTERVALS.get(parsed.quality, [0, 4, 7])

    # All chord tones are wrapped into the requested octave.
    # MIDI: C4 = 60, so octave N starts at (N+1)*12
    base_midi = (octave + 1) * 12  # MIDI pitch for C in the octave

    pitches = []
    for interval in intervals:
        # Calculate pitch class for this chord tone
        pitch_class = (root_pitch_class + interval) % 12
        pitch = base_midi + pitch_class
        if not 0 <= pitch <= 127:
            raise ValueError(
                f"Octave {octave} puts {numeral.strip()!a} outside the MIDI range 0-127"
            )
        pitches.append(pitch)

    return pitches


def get_note_names_for_pitches(pitches: List[int]) -> List[str]:
    """
    Convert MIDI pitches to note names (for debugging/testing).

    Args:
        pitches: List of MIDI pitch numbers.

    Returns:
        List of note names (e.g., ['C4', 'E4', 'G4']).
    """
    pitch_to_name = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    names = []
    for pitch in pitches:
        octave = pitch // 12 - 1  # MIDI octave convention
        note = pitch_to_name[pitch % 12]
        names.append(f"{note}{octave}")
    return names
