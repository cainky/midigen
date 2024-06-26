from typing import List
from midigen.note import Note
from midigen.key import KEY_MAP
from enum import Enum

class Chord:
    def __init__(self, notes: List[Note]):
        self.notes = notes
        self.root = self.get_root()
        self._calculate_start_time()
        self._calculate_duration()
            
    def __str__(self) -> str:
        return f"[{', '.join(str(note) for note in self.notes)}]"

    def _calculate_start_time(self) -> int:
        """
        Calculate the start time of the chord.

        Returns:
            The start time of the chord.
        """
        self.time = min(note.time for note in self.notes)
        return self.time
    
    def _calculate_duration(self) -> int:
        """
        Calculate the duration of the chord.

        Returns:
            The duration of the longest note in the chord.
        """
        if not self.notes:
            return 0

        # Find the earliest start time of any note in the chord
        earliest_start_time = min(note.time for note in self.notes)
        # Find the latest ending time, calculated as start time plus duration for each note
        latest_end_time = max(note.time + note.duration for note in self.notes)

        # The duration of the chord is the difference between the earliest start and the latest end
        self.duration = latest_end_time - earliest_start_time
        return self.duration

    def add_note(self, note: Note) -> None:
        self.notes.append(note)
        self._calculate_duration()
        self._calculate_start_time()

    def get_chord(self) -> List[Note]:
        return self.notes

    def get_root(self) -> Note:
        self.root = self.notes[0]
        return self.root

    def major_triad(self) -> List[Note]:
        return [self.root, self.root + 4, self.root + 7]

    def minor_triad(self) -> List[Note]:
        return [self.root, self.root + 3, self.root + 7]

    def dominant_seventh(self) -> List[Note]:
        return self.major_triad() + [self.root + 10]

    def major_seventh(self) -> List[Note]:
        return self.major_triad() + [self.root + 11]

    def minor_seventh(self) -> List[Note]:
        return self.minor_triad() + [self.root + 10]

    def half_diminished_seventh(self) -> List[Note]:
        return [self.root, self.root + 3, self.root + 6, self.root + 10]

    def diminished_seventh(self) -> List[Note]:
        return [self.root, self.root + 3, self.root + 6, self.root + 9]

    def minor_ninth(self) -> List[Note]:
        return self.minor_seventh() + [self.root + 14]

    def major_ninth(self) -> List[Note]:
        return self.major_seventh() + [self.root + 14]

    def dominant_ninth(self) -> List[Note]:
        return self.dominant_seventh() + [self.root + 14]


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
        self.time = min(chord._calculate_start_time() for chord in self.chords)
        return self.time
    
    def __eq__(self, other) -> bool:
        return self.chords == other.chords

    def add_chord(self, chord: Chord) -> None:
        """
        Add a chord (simultaneous notes) to the track.

        :param chord: A Chord object.
        """
        self.chords.append(chord)
        self._calculate_duration()
        self._calculate_start_time()


class ArpeggioPattern(Enum):
    ASCENDING = "ascending"
    DESCENDING = "descending"
    ALTERNATING = "alternating"

    
class Arpeggio(Chord):
    def __init__(self, notes: List[Note], delay: int = 0, pattern: ArpeggioPattern = ArpeggioPattern.ASCENDING, loops: int = 1):
        """
        :param root_note: The root note of the arpeggio.
        :param delay: The delay between each note in the arpeggio.
        """
        super().__init__(notes)
        self.delay = delay
        self.pattern = pattern
        self.loops = loops
    
    def get_notes(self) -> List[Note]:
        return self.notes
    
    def get_sequential_notes(self) -> List[Note]:
        """
        Get the sequential notes of the arpeggio based on the pattern, delay, and looping.

        Returns:
            A list of notes representing the arpeggio.
        """
        sequential_notes = []
        for loop in range(self.loops):
            if self.pattern == ArpeggioPattern.ASCENDING:
                notes = self.notes
            elif self.pattern == ArpeggioPattern.DESCENDING:
                notes = list(reversed(self.notes))
            elif self.pattern == ArpeggioPattern.ALTERNATING:
                notes = self.notes if loop % 2 == 0 else list(reversed(self.notes))

            for i, note in enumerate(notes):
                # Add an offset to the time for the second and subsequent loops
                time_offset = loop * len(notes) * self.delay
                time = note.time + time_offset if i == 0 else self.delay * i + time_offset
                new_note = Note(note.pitch, note.velocity, note.duration, time)
                sequential_notes.append(new_note)

        return sequential_notes
