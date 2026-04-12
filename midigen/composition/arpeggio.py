from typing import List
from enum import Enum
from midigen.theory.note import Note
from midigen.composition.chord import Chord


class ArpeggioPattern(Enum):
    ASCENDING = "ascending"
    DESCENDING = "descending"
    ALTERNATING = "alternating"


class Arpeggio(Chord):
    def __init__(self, notes: List[Note], delay: int = 0, pattern: ArpeggioPattern = ArpeggioPattern.ASCENDING, loops: int = 1):
        super().__init__(notes)
        self.delay = delay
        self.pattern = pattern
        self.loops = loops

    def get_notes(self) -> List[Note]:
        return self.notes

    def get_sequential_notes(self) -> List[Note]:
        """Get the sequential notes of the arpeggio based on the pattern, delay, and looping."""
        sequential_notes = []
        for loop in range(self.loops):
            if self.pattern == ArpeggioPattern.ASCENDING:
                notes = self.notes
            elif self.pattern == ArpeggioPattern.DESCENDING:
                notes = list(reversed(self.notes))
            elif self.pattern == ArpeggioPattern.ALTERNATING:
                notes = self.notes if loop % 2 == 0 else list(reversed(self.notes))

            for i, note in enumerate(notes):
                time_offset = loop * len(notes) * self.delay
                time = note.time + time_offset if i == 0 else self.delay * i + time_offset
                new_note = Note(note.pitch, note.velocity, note.duration, time)
                sequential_notes.append(new_note)

        return sequential_notes
