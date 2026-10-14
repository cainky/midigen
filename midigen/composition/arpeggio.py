from typing import List
from enum import Enum
from midigen.theory.note import Note
from midigen.composition.chord import Chord


class ArpeggioPattern(Enum):
    ASCENDING = "ascending"
    DESCENDING = "descending"
    ALTERNATING = "alternating"


class Arpeggio(Chord):
    def __init__(
        self,
        notes: List[Note],
        delay: int = 0,
        pattern: ArpeggioPattern = ArpeggioPattern.ASCENDING,
        loops: int = 1,
    ):
        """
        Args:
            notes: The chord tones, in any order. The arpeggio starts at the earliest note time.
            delay: Ticks between consecutive notes.
            pattern: An ArpeggioPattern or its value: "ascending" (low to high pitch),
                "descending" (high to low), or "alternating" (up, then down on the next loop).
            loops: How many times the pattern is played.
        """
        super().__init__(notes)
        if not isinstance(delay, int) or isinstance(delay, bool) or delay < 0:
            raise ValueError(
                f"Arpeggio delay must be a non-negative integer, got {delay!r}"
            )
        if not isinstance(loops, int) or isinstance(loops, bool) or loops < 1:
            raise ValueError(
                f"Arpeggio loops must be a positive integer, got {loops!r}"
            )
        self.delay = delay
        self.pattern = ArpeggioPattern(pattern)
        self.loops = loops

    def get_notes(self) -> List[Note]:
        return self.notes

    def get_sequential_notes(self) -> List[Note]:
        """Get the sequential notes of the arpeggio based on the pattern, delay, and looping."""
        ascending = sorted(self.notes, key=lambda note: note.pitch)
        descending = ascending[::-1]
        sequential_notes = []
        for loop in range(self.loops):
            if self.pattern == ArpeggioPattern.ASCENDING:
                notes = ascending
            elif self.pattern == ArpeggioPattern.DESCENDING:
                notes = descending
            else:  # ALTERNATING
                notes = ascending if loop % 2 == 0 else descending

            loop_start = self.time + loop * len(notes) * self.delay
            for i, note in enumerate(notes):
                sequential_notes.append(
                    Note(
                        note.pitch,
                        note.velocity,
                        note.duration,
                        loop_start + i * self.delay,
                    )
                )

        return sequential_notes
