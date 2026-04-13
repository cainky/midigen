from typing import List
from midigen.theory.note import Note


CHORD_TYPES = {
    "major_triad": (0, 4, 7),
    "minor_triad": (0, 3, 7),
    "dominant_seventh": (0, 4, 7, 10),
    "major_seventh": (0, 4, 7, 11),
    "minor_seventh": (0, 3, 7, 10),
    "half_diminished_seventh": (0, 3, 6, 10),
    "diminished_seventh": (0, 3, 6, 9),
    "minor_ninth": (0, 3, 7, 10, 14),
    "major_ninth": (0, 4, 7, 11, 14),
    "dominant_ninth": (0, 4, 7, 10, 14),
    "sus2": (0, 2, 7),
    "sus4": (0, 5, 7),
    "augmented": (0, 4, 8),
    "diminished": (0, 3, 6),
    "major_sixth": (0, 4, 7, 9),
    "minor_sixth": (0, 3, 7, 9),
    "dominant_eleventh": (0, 4, 7, 10, 14, 17),
    "major_eleventh": (0, 4, 7, 11, 14, 17),
    "minor_eleventh": (0, 3, 7, 10, 14, 17),
    "dominant_thirteenth": (0, 4, 7, 10, 14, 17, 21),
    "major_thirteenth": (0, 4, 7, 11, 14, 17, 21),
    "minor_thirteenth": (0, 3, 7, 10, 14, 17, 21),
    "add9": (0, 4, 7, 14),
    "minor_add9": (0, 3, 7, 14),
    "add11": (0, 4, 7, 17),
    "augmented_seventh": (0, 4, 8, 10),
    "augmented_major_seventh": (0, 4, 8, 11),
}


class Chord:
    def __init__(self, notes: List[Note]):
        self.notes = notes
        self.root = self.get_root()
        self._calculate_start_time()
        self._calculate_duration()

    def __str__(self) -> str:
        return f"[{', '.join(str(note) for note in self.notes)}]"

    def _calculate_start_time(self) -> int:
        self.time = min(note.time for note in self.notes) if self.notes else 0
        return self.time

    def _calculate_duration(self) -> int:
        if not self.notes:
            return 0
        earliest_start_time = min(note.time for note in self.notes)
        latest_end_time = max(note.time + note.duration for note in self.notes)
        self.duration = latest_end_time - earliest_start_time
        return self.duration

    def add_note(self, note: Note) -> None:
        self.notes.append(note)
        self._calculate_duration()
        self._calculate_start_time()

    def get_chord(self) -> List[Note]:
        return self.notes

    def get_root(self) -> Note:
        if self.notes:
            self.root = self.notes[0]
            return self.root
        return None

    # Instance voicing methods (return List[Note] relative to self.root)

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

    # Data-driven factory

    @classmethod
    def build(cls, chord_type: str, root: Note) -> 'Chord':
        """Build a chord from a type name and root note.

        Args:
            chord_type: Key from CHORD_TYPES (e.g. "major_triad", "sus2", "dominant_ninth")
            root: The root Note for the chord.

        Returns:
            A new Chord instance.

        Raises:
            KeyError: If chord_type is not in CHORD_TYPES.
        """
        intervals = CHORD_TYPES[chord_type]
        notes = [root + interval for interval in intervals]
        return cls(notes)

    # Named factory wrappers (backwards-compatible API)

    @classmethod
    def create_major_triad(cls, root: Note) -> 'Chord':
        """Create a major triad chord from a root note."""
        return cls.build("major_triad", root)

    @classmethod
    def create_minor_triad(cls, root: Note) -> 'Chord':
        """Create a minor triad chord from a root note."""
        return cls.build("minor_triad", root)

    @classmethod
    def create_dominant_seventh(cls, root: Note) -> 'Chord':
        """Create a dominant seventh chord from a root note."""
        return cls.build("dominant_seventh", root)

    @classmethod
    def create_major_seventh(cls, root: Note) -> 'Chord':
        """Create a major seventh chord from a root note."""
        return cls.build("major_seventh", root)

    @classmethod
    def create_minor_seventh(cls, root: Note) -> 'Chord':
        """Create a minor seventh chord from a root note."""
        return cls.build("minor_seventh", root)

    @classmethod
    def create_half_diminished_seventh(cls, root: Note) -> 'Chord':
        """Create a half-diminished seventh chord from a root note."""
        return cls.build("half_diminished_seventh", root)

    @classmethod
    def create_diminished_seventh(cls, root: Note) -> 'Chord':
        """Create a diminished seventh chord from a root note."""
        return cls.build("diminished_seventh", root)

    @classmethod
    def create_minor_ninth(cls, root: Note) -> 'Chord':
        """Create a minor ninth chord from a root note."""
        return cls.build("minor_ninth", root)

    @classmethod
    def create_major_ninth(cls, root: Note) -> 'Chord':
        """Create a major ninth chord from a root note."""
        return cls.build("major_ninth", root)

    @classmethod
    def create_dominant_ninth(cls, root: Note) -> 'Chord':
        """Create a dominant ninth chord from a root note."""
        return cls.build("dominant_ninth", root)

    @classmethod
    def create_sus2(cls, root: Note) -> 'Chord':
        """Create a suspended 2nd chord from a root note."""
        return cls.build("sus2", root)

    @classmethod
    def create_sus4(cls, root: Note) -> 'Chord':
        """Create a suspended 4th chord from a root note."""
        return cls.build("sus4", root)

    @classmethod
    def create_augmented(cls, root: Note) -> 'Chord':
        """Create an augmented triad from a root note."""
        return cls.build("augmented", root)

    @classmethod
    def create_diminished(cls, root: Note) -> 'Chord':
        """Create a diminished triad from a root note."""
        return cls.build("diminished", root)

    @classmethod
    def create_major_sixth(cls, root: Note) -> 'Chord':
        """Create a major 6th chord from a root note."""
        return cls.build("major_sixth", root)

    @classmethod
    def create_minor_sixth(cls, root: Note) -> 'Chord':
        """Create a minor 6th chord from a root note."""
        return cls.build("minor_sixth", root)

    @classmethod
    def create_dominant_eleventh(cls, root: Note) -> 'Chord':
        """Create a dominant 11th chord from a root note."""
        return cls.build("dominant_eleventh", root)

    @classmethod
    def create_major_eleventh(cls, root: Note) -> 'Chord':
        """Create a major 11th chord from a root note."""
        return cls.build("major_eleventh", root)

    @classmethod
    def create_minor_eleventh(cls, root: Note) -> 'Chord':
        """Create a minor 11th chord from a root note."""
        return cls.build("minor_eleventh", root)

    @classmethod
    def create_dominant_thirteenth(cls, root: Note) -> 'Chord':
        """Create a dominant 13th chord from a root note."""
        return cls.build("dominant_thirteenth", root)

    @classmethod
    def create_major_thirteenth(cls, root: Note) -> 'Chord':
        """Create a major 13th chord from a root note."""
        return cls.build("major_thirteenth", root)

    @classmethod
    def create_minor_thirteenth(cls, root: Note) -> 'Chord':
        """Create a minor 13th chord from a root note."""
        return cls.build("minor_thirteenth", root)

    @classmethod
    def create_add9(cls, root: Note) -> 'Chord':
        """Create an add9 chord from a root note."""
        return cls.build("add9", root)

    @classmethod
    def create_minor_add9(cls, root: Note) -> 'Chord':
        """Create a minor add9 chord from a root note."""
        return cls.build("minor_add9", root)

    @classmethod
    def create_add11(cls, root: Note) -> 'Chord':
        """Create an add11 chord from a root note."""
        return cls.build("add11", root)

    @classmethod
    def create_augmented_seventh(cls, root: Note) -> 'Chord':
        """Create an augmented 7th chord from a root note."""
        return cls.build("augmented_seventh", root)

    @classmethod
    def create_augmented_major_seventh(cls, root: Note) -> 'Chord':
        """Create an augmented major 7th chord from a root note."""
        return cls.build("augmented_major_seventh", root)
