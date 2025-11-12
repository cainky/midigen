"""
Melody generation utilities for creating melodic sequences.
"""

from typing import List, Union
from midigen.note import Note
from midigen.key import KEY_MAP
from midigen.time_utils import TimeConverter
import random


class Melody:
    """
    High-level class for creating and manipulating melodies.
    """

    def __init__(self, notes: List[Note]):
        """
        Initialize a Melody with a list of notes.

        Args:
            notes: List of Note objects
        """
        self.notes = notes

    def get_notes(self) -> List[Note]:
        """Get the list of notes in the melody."""
        return self.notes

    @classmethod
    def from_scale(
        cls,
        scale: List[int],
        pattern: List[int],
        start_time: int = 0,
        note_duration: int = 480,
        velocity: int = 80,
        octave_shift: int = 0
    ) -> 'Melody':
        """
        Create a melody from a scale using a pattern of scale degrees.

        Args:
            scale: List of MIDI note numbers representing a scale
            pattern: List of scale degree indices (0-based). Example: [0, 2, 4, 2]
                    for root, 3rd, 5th, 3rd of the scale
            start_time: Starting time in ticks
            note_duration: Duration of each note in ticks
            velocity: MIDI velocity for all notes
            octave_shift: Number of octaves to shift the melody up (positive) or down (negative)

        Returns:
            Melody object

        Example:
            >>> from midigen import Scale, Melody
            >>> scale = Scale.major(60)  # C major scale
            >>> pattern = [0, 2, 4, 2, 0]  # C E G E C
            >>> melody = Melody.from_scale(scale, pattern)
        """
        if not scale:
            raise ValueError("Scale cannot be empty")
        if not pattern:
            raise ValueError("Pattern cannot be empty")

        notes = []
        current_time = start_time
        octave_shift_semitones = octave_shift * 12

        for degree in pattern:
            if degree < 0 or degree >= len(scale):
                raise ValueError(f"Scale degree {degree} is out of range for scale with {len(scale)} notes")

            pitch = scale[degree] + octave_shift_semitones
            if pitch < 0 or pitch > 127:
                raise ValueError(f"Resulting pitch {pitch} is out of MIDI range (0-127)")

            note = Note(
                pitch=pitch,
                velocity=velocity,
                duration=note_duration,
                time=current_time
            )
            notes.append(note)
            current_time += note_duration

        return cls(notes)

    @classmethod
    def from_note_names(
        cls,
        note_names: str,
        durations: Union[List[int], int] = 480,
        start_time: int = 0,
        velocity: int = 80
    ) -> 'Melody':
        """
        Create a melody from note names like "C4 E4 G4 C5".

        Args:
            note_names: Space-separated note names (e.g., "C4 E4 G4 C5")
            durations: Single duration for all notes, or list of durations for each note
            start_time: Starting time in ticks
            velocity: MIDI velocity for all notes

        Returns:
            Melody object

        Example:
            >>> melody = Melody.from_note_names("C4 E4 G4 C5")
            >>> melody = Melody.from_note_names("C4 E4 G4", durations=[480, 240, 960])
        """
        if not note_names or not note_names.strip():
            raise ValueError("Note names cannot be empty")

        names = note_names.strip().split()
        notes = []
        current_time = start_time

        # Handle durations
        if isinstance(durations, int):
            durations_list = [durations] * len(names)
        else:
            if len(durations) != len(names):
                raise ValueError(f"Number of durations ({len(durations)}) must match number of notes ({len(names)})")
            durations_list = durations

        for name, duration in zip(names, durations_list):
            if name not in KEY_MAP:
                raise ValueError(f"Invalid note name: {name}. Note must be in format like 'C4' or 'F#3'")

            pitch = KEY_MAP[name]
            note = Note(
                pitch=pitch,
                velocity=velocity,
                duration=duration,
                time=current_time
            )
            notes.append(note)
            current_time += duration

        return cls(notes)

    @classmethod
    def from_degrees(
        cls,
        scale: List[int],
        degrees: List[int],
        rhythms: Union[List[int], str] = 480,
        start_time: int = 0,
        velocity: int = 80
    ) -> 'Melody':
        """
        Create a melody from scale degrees (1-based, like music theory notation).

        Args:
            scale: List of MIDI note numbers representing a scale
            degrees: List of scale degrees (1-based). Example: [1, 3, 5, 8] for
                    root, 3rd, 5th, octave. Negative numbers go down octaves.
            rhythms: Single duration for all notes, list of durations, or rhythm string
                    like "quarter quarter half" or "q q h"
            start_time: Starting time in ticks
            velocity: MIDI velocity for all notes

        Returns:
            Melody object

        Example:
            >>> from midigen import Scale, Melody
            >>> scale = Scale.major(60)
            >>> melody = Melody.from_degrees(scale, [1, 3, 5, 8])  # Ascending
            >>> melody = Melody.from_degrees(scale, [8, 5, 3, 1])  # Descending
        """
        if not scale:
            raise ValueError("Scale cannot be empty")
        if not degrees:
            raise ValueError("Degrees cannot be empty")

        notes = []
        current_time = start_time
        tc = TimeConverter()

        # Handle rhythms
        if isinstance(rhythms, str):
            # Parse rhythm string
            rhythm_map = {
                'w': 'whole', 'h': 'half', 'q': 'quarter',
                'e': 'eighth', 's': 'sixteenth',
                'whole': 'whole', 'half': 'half', 'quarter': 'quarter',
                'eighth': 'eighth', 'sixteenth': 'sixteenth',
                'dh': 'dotted_half', 'dq': 'dotted_quarter', 'de': 'dotted_eighth',
                'dotted_half': 'dotted_half', 'dotted_quarter': 'dotted_quarter',
                'dotted_eighth': 'dotted_eighth'
            }
            rhythm_names = rhythms.strip().split()
            durations_list = []
            for r in rhythm_names:
                r_lower = r.lower()
                if r_lower not in rhythm_map:
                    raise ValueError(f"Invalid rhythm: {r}. Use w, h, q, e, s or full names like 'quarter'")
                durations_list.append(tc.note_duration(rhythm_map[r_lower]))

            if len(durations_list) != len(degrees):
                raise ValueError(f"Number of rhythms ({len(durations_list)}) must match number of degrees ({len(degrees)})")
        elif isinstance(rhythms, int):
            durations_list = [rhythms] * len(degrees)
        else:
            if len(rhythms) != len(degrees):
                raise ValueError(f"Number of rhythms ({len(rhythms)}) must match number of degrees ({len(degrees)})")
            durations_list = rhythms

        scale_length = len(scale) - 1  # Exclude octave note
        base_octave_pitch = scale[0]

        for degree, duration in zip(degrees, durations_list):
            if degree == 0:
                raise ValueError("Scale degrees are 1-based. Use 1 for root, not 0")

            # Calculate pitch from scale degree
            # Positive degrees: 1 = root, 2 = 2nd, etc.
            # Negative degrees go down octaves
            if degree > 0:
                octave_offset = (degree - 1) // scale_length
                scale_index = (degree - 1) % scale_length
                pitch = scale[scale_index] + (octave_offset * 12)
            else:
                # Negative degree
                octave_offset = (abs(degree) - 1) // scale_length + 1
                scale_index = scale_length - ((abs(degree) - 1) % scale_length)
                if scale_index == scale_length:
                    scale_index = 0
                    octave_offset -= 1
                pitch = scale[scale_index] - (octave_offset * 12)

            if pitch < 0 or pitch > 127:
                raise ValueError(f"Degree {degree} results in pitch {pitch}, which is out of MIDI range (0-127)")

            note = Note(
                pitch=pitch,
                velocity=velocity,
                duration=duration,
                time=current_time
            )
            notes.append(note)
            current_time += duration

        return cls(notes)

    @classmethod
    def random_walk(
        cls,
        start_pitch: int,
        length: int,
        scale: List[int],
        max_interval: int = 5,
        duration: int = 480,
        start_time: int = 0,
        velocity: int = 80,
        seed: int = None
    ) -> 'Melody':
        """
        Generate a random melody using a random walk algorithm within a scale.

        Args:
            start_pitch: Starting MIDI pitch
            length: Number of notes to generate
            scale: List of valid pitches to choose from
            max_interval: Maximum interval jump in scale degrees
            duration: Duration of each note in ticks
            start_time: Starting time in ticks
            velocity: MIDI velocity for all notes
            seed: Random seed for reproducibility (optional)

        Returns:
            Melody object
        """
        if seed is not None:
            random.seed(seed)

        if start_pitch not in scale:
            raise ValueError(f"Start pitch {start_pitch} is not in the provided scale")

        notes = []
        current_pitch = start_pitch
        current_time = start_time
        current_index = scale.index(current_pitch)

        for _ in range(length):
            note = Note(
                pitch=current_pitch,
                velocity=velocity,
                duration=duration,
                time=current_time
            )
            notes.append(note)
            current_time += duration

            # Random walk: move up or down by a random interval within max_interval
            step = random.randint(-max_interval, max_interval)
            new_index = current_index + step

            # Keep within scale bounds
            new_index = max(0, min(new_index, len(scale) - 1))
            current_index = new_index
            current_pitch = scale[current_index]

        return cls(notes)

    def transpose(self, semitones: int) -> 'Melody':
        """
        Transpose the melody by a number of semitones.

        Args:
            semitones: Number of semitones to transpose (positive = up, negative = down)

        Returns:
            New Melody object with transposed notes
        """
        transposed_notes = []
        for note in self.notes:
            new_pitch = note.pitch + semitones
            if new_pitch < 0 or new_pitch > 127:
                raise ValueError(f"Transposition results in pitch {new_pitch}, out of MIDI range")
            transposed_notes.append(note + semitones)
        return Melody(transposed_notes)

    def reverse(self) -> 'Melody':
        """
        Reverse the melody (retrograde).

        Returns:
            New Melody object with notes in reverse order
        """
        reversed_notes = []
        total_duration = sum(n.duration for n in self.notes)
        start_time = self.notes[0].time if self.notes else 0

        current_time = start_time
        for note in reversed(self.notes):
            new_note = Note(
                pitch=note.pitch,
                velocity=note.velocity,
                duration=note.duration,
                time=current_time
            )
            reversed_notes.append(new_note)
            current_time += note.duration

        return Melody(reversed_notes)

    def __len__(self) -> int:
        """Return the number of notes in the melody."""
        return len(self.notes)

    def __getitem__(self, index: int) -> Note:
        """Get a note by index."""
        return self.notes[index]

    def __str__(self) -> str:
        """String representation of the melody."""
        return f"Melody({len(self.notes)} notes)"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Melody(notes={self.notes})"
