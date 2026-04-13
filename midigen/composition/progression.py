from typing import List
from midigen.theory.note import Note
from midigen.theory.key import Key
from midigen.theory.roman import get_chord_pitches
from midigen.composition.chord import Chord


class ChordProgression:
    def __init__(self, chords: List[Chord]):
        self.chords = chords
        self._calculate_start_time()
        self._calculate_duration()

    def __str__(self) -> str:
        return f"[{', '.join(str(chord) for chord in self.chords)}]"

    def get_progression(self) -> List[Chord]:
        return self.chords

    def _calculate_duration(self) -> int:
        self.duration = sum(chord._calculate_duration() for chord in self.chords)
        return self.duration

    def _calculate_start_time(self) -> int:
        self.time = min(chord._calculate_start_time() for chord in self.chords) if self.chords else 0
        return self.time

    def __eq__(self, other) -> bool:
        return self.chords == other.chords

    def add_chord(self, chord: Chord) -> None:
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
        time_per_chord: int = 0
    ):
        """Create a chord progression from Roman numeral notation.

        Args:
            key: The key for the progression (e.g., Key("C", "major"))
            progression_string: Dash-separated Roman numerals (e.g., "I-V-vi-IV")
            octave: Base octave for the chords (default 4)
            duration: Duration of each note in ticks (default 480)
            time_per_chord: Time between chord starts in ticks (default 0)

        Returns:
            ChordProgression containing the parsed chords.
        """
        roman_numerals = progression_string.split('-')
        chords = []
        current_time = 0

        for rn_str in roman_numerals:
            pitches = get_chord_pitches(key.name, key.mode, rn_str, octave=octave)

            notes = []
            for midi_pitch in pitches:
                notes.append(Note(
                    pitch=midi_pitch,
                    velocity=64,
                    duration=duration,
                    time=current_time
                ))

            if notes:
                chords.append(Chord(notes))
            current_time += time_per_chord

        return cls(chords)
