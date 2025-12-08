from typing import List
from midigen.note import Note
from midigen.key import KEY_MAP, Key
from midigen.roman import get_chord_pitches
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
        self.time = min(note.time for note in self.notes) if self.notes else 0
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
        if self.notes:
            self.root = self.notes[0]
            return self.root
        return None

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

    @classmethod
    def create_major_triad(cls, root: Note) -> 'Chord':
        """Create a major triad chord from a root note."""
        notes = [root, root + 4, root + 7]
        return cls(notes)

    @classmethod
    def create_minor_triad(cls, root: Note) -> 'Chord':
        """Create a minor triad chord from a root note."""
        notes = [root, root + 3, root + 7]
        return cls(notes)

    @classmethod
    def create_dominant_seventh(cls, root: Note) -> 'Chord':
        """Create a dominant seventh chord from a root note."""
        notes = [root, root + 4, root + 7, root + 10]
        return cls(notes)

    @classmethod
    def create_major_seventh(cls, root: Note) -> 'Chord':
        """Create a major seventh chord from a root note."""
        notes = [root, root + 4, root + 7, root + 11]
        return cls(notes)

    @classmethod
    def create_minor_seventh(cls, root: Note) -> 'Chord':
        """Create a minor seventh chord from a root note."""
        notes = [root, root + 3, root + 7, root + 10]
        return cls(notes)

    @classmethod
    def create_half_diminished_seventh(cls, root: Note) -> 'Chord':
        """Create a half-diminished seventh chord from a root note."""
        notes = [root, root + 3, root + 6, root + 10]
        return cls(notes)

    @classmethod
    def create_diminished_seventh(cls, root: Note) -> 'Chord':
        """Create a diminished seventh chord from a root note."""
        notes = [root, root + 3, root + 6, root + 9]
        return cls(notes)

    @classmethod
    def create_minor_ninth(cls, root: Note) -> 'Chord':
        """Create a minor ninth chord from a root note."""
        notes = [root, root + 3, root + 7, root + 10, root + 14]
        return cls(notes)

    @classmethod
    def create_major_ninth(cls, root: Note) -> 'Chord':
        """Create a major ninth chord from a root note."""
        notes = [root, root + 4, root + 7, root + 11, root + 14]
        return cls(notes)

    @classmethod
    def create_dominant_ninth(cls, root: Note) -> 'Chord':
        """Create a dominant ninth chord from a root note."""
        notes = [root, root + 4, root + 7, root + 10, root + 14]
        return cls(notes)

    # ===== Suspended Chords =====

    @classmethod
    def create_sus2(cls, root: Note) -> 'Chord':
        """Create a suspended 2nd chord from a root note (root, 2nd, 5th)."""
        notes = [root, root + 2, root + 7]
        return cls(notes)

    @classmethod
    def create_sus4(cls, root: Note) -> 'Chord':
        """Create a suspended 4th chord from a root note (root, 4th, 5th)."""
        notes = [root, root + 5, root + 7]
        return cls(notes)

    # ===== Augmented and Diminished Triads =====

    @classmethod
    def create_augmented(cls, root: Note) -> 'Chord':
        """Create an augmented triad from a root note (root, major 3rd, augmented 5th)."""
        notes = [root, root + 4, root + 8]
        return cls(notes)

    @classmethod
    def create_diminished(cls, root: Note) -> 'Chord':
        """Create a diminished triad from a root note (root, minor 3rd, diminished 5th)."""
        notes = [root, root + 3, root + 6]
        return cls(notes)

    # ===== 6th Chords =====

    @classmethod
    def create_major_sixth(cls, root: Note) -> 'Chord':
        """Create a major 6th chord from a root note (major triad + 6th)."""
        notes = [root, root + 4, root + 7, root + 9]
        return cls(notes)

    @classmethod
    def create_minor_sixth(cls, root: Note) -> 'Chord':
        """Create a minor 6th chord from a root note (minor triad + 6th)."""
        notes = [root, root + 3, root + 7, root + 9]
        return cls(notes)

    # ===== 11th Chords =====

    @classmethod
    def create_dominant_eleventh(cls, root: Note) -> 'Chord':
        """Create a dominant 11th chord from a root note."""
        notes = [root, root + 4, root + 7, root + 10, root + 14, root + 17]
        return cls(notes)

    @classmethod
    def create_major_eleventh(cls, root: Note) -> 'Chord':
        """Create a major 11th chord from a root note."""
        notes = [root, root + 4, root + 7, root + 11, root + 14, root + 17]
        return cls(notes)

    @classmethod
    def create_minor_eleventh(cls, root: Note) -> 'Chord':
        """Create a minor 11th chord from a root note."""
        notes = [root, root + 3, root + 7, root + 10, root + 14, root + 17]
        return cls(notes)

    # ===== 13th Chords =====

    @classmethod
    def create_dominant_thirteenth(cls, root: Note) -> 'Chord':
        """Create a dominant 13th chord from a root note."""
        notes = [root, root + 4, root + 7, root + 10, root + 14, root + 17, root + 21]
        return cls(notes)

    @classmethod
    def create_major_thirteenth(cls, root: Note) -> 'Chord':
        """Create a major 13th chord from a root note."""
        notes = [root, root + 4, root + 7, root + 11, root + 14, root + 17, root + 21]
        return cls(notes)

    @classmethod
    def create_minor_thirteenth(cls, root: Note) -> 'Chord':
        """Create a minor 13th chord from a root note."""
        notes = [root, root + 3, root + 7, root + 10, root + 14, root + 17, root + 21]
        return cls(notes)

    # ===== Add Chords =====

    @classmethod
    def create_add9(cls, root: Note) -> 'Chord':
        """Create an add9 chord from a root note (major triad + 9th, no 7th)."""
        notes = [root, root + 4, root + 7, root + 14]
        return cls(notes)

    @classmethod
    def create_minor_add9(cls, root: Note) -> 'Chord':
        """Create a minor add9 chord from a root note (minor triad + 9th, no 7th)."""
        notes = [root, root + 3, root + 7, root + 14]
        return cls(notes)

    @classmethod
    def create_add11(cls, root: Note) -> 'Chord':
        """Create an add11 chord from a root note (major triad + 11th, no 7th or 9th)."""
        notes = [root, root + 4, root + 7, root + 17]
        return cls(notes)

    # ===== Augmented 7th Chords =====

    @classmethod
    def create_augmented_seventh(cls, root: Note) -> 'Chord':
        """Create an augmented 7th chord from a root note (augmented triad + minor 7th)."""
        notes = [root, root + 4, root + 8, root + 10]
        return cls(notes)

    @classmethod
    def create_augmented_major_seventh(cls, root: Note) -> 'Chord':
        """Create an augmented major 7th chord from a root note (augmented triad + major 7th)."""
        notes = [root, root + 4, root + 8, root + 11]
        return cls(notes)


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
        """
        Add a chord (simultaneous notes) to the track.

        :param chord: A Chord object.
        """
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
        """
        Create a chord progression from Roman numeral notation.

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
            # Use native parser to get MIDI pitches
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
