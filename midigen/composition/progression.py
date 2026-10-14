from typing import List, Optional
from midigen.theory.note import Note
from midigen.theory.key import Key
from midigen.theory.roman import get_chord_pitches
from midigen.composition.chord import Chord


class ChordProgression:
    def __init__(self, chords: List[Chord]):
        self.chords = list(chords)
        for chord in self.chords:
            if not isinstance(chord, Chord):
                raise TypeError(
                    f"ChordProgression items must be Chord objects, got {type(chord).__name__}"
                )
        self._calculate_start_time()
        self._calculate_duration()

    def __str__(self) -> str:
        return f"[{', '.join(str(chord) for chord in self.chords)}]"

    def __repr__(self) -> str:
        return f"ChordProgression({self.chords!r})"

    def get_progression(self) -> List[Chord]:
        return self.chords

    def _calculate_duration(self) -> int:
        """Duration from the earliest chord start to the latest chord end, in ticks."""
        if not self.chords:
            self.duration = 0
            return self.duration
        start = min(chord._calculate_start_time() for chord in self.chords)
        end = max(chord.time + chord._calculate_duration() for chord in self.chords)
        self.duration = end - start
        return self.duration

    def _calculate_start_time(self) -> int:
        self.time = (
            min(chord._calculate_start_time() for chord in self.chords)
            if self.chords
            else 0
        )
        return self.time

    def __eq__(self, other) -> bool:
        if not isinstance(other, ChordProgression):
            return NotImplemented
        return self.chords == other.chords

    def add_chord(self, chord: Chord) -> None:
        if not isinstance(chord, Chord):
            raise TypeError(
                f"ChordProgression items must be Chord objects, got {type(chord).__name__}"
            )
        self.chords.append(chord)
        self._calculate_duration()
        self._calculate_start_time()

    @classmethod
    def from_roman_numerals(
        cls,
        key: Key,
        progression_string: str,
        octave: int = 4,
        duration: int = 480,
        time_per_chord: Optional[int] = None,
    ):
        """Create a chord progression from Roman numeral notation.

        Args:
            key: The key for the progression (e.g., Key("C", "major"))
            progression_string: Dash-separated Roman numerals (e.g., "I-V-vi-IV")
            octave: Octave the chord tones are placed in (default 4)
            duration: Duration of each note in ticks (default 480)
            time_per_chord: Time between chord starts in ticks. Defaults to
                ``duration`` (chords back to back); pass 0 to stack them all at time 0.

        Returns:
            ChordProgression containing the parsed chords.
        """
        if time_per_chord is None:
            time_per_chord = duration

        chords = []
        for index, rn_str in enumerate(progression_string.split("-")):
            pitches = get_chord_pitches(key.name, key.mode, rn_str, octave=octave)
            start = index * time_per_chord
            chords.append(
                Chord([Note(pitch, 64, duration, start) for pitch in pitches])
            )

        return cls(chords)
