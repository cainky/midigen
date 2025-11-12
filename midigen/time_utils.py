"""
Time conversion utilities for working with MIDI ticks, beats, and measures.

MIDI uses "ticks" as the base unit of time. The number of ticks per quarter note
is defined by the MIDI file's resolution (typically 480 ticks per quarter note).
"""


class TimeConverter:
    """
    Utility class for converting between musical time units (measures, beats)
    and MIDI ticks.

    Default resolution is 480 ticks per quarter note, which is a common standard.
    """

    DEFAULT_TICKS_PER_QUARTER_NOTE = 480

    def __init__(self, ticks_per_quarter_note: int = DEFAULT_TICKS_PER_QUARTER_NOTE):
        """
        Initialize the TimeConverter with a specific resolution.

        Args:
            ticks_per_quarter_note: Number of ticks in a quarter note (default: 480)
        """
        if ticks_per_quarter_note <= 0:
            raise ValueError("Ticks per quarter note must be positive")
        self.ticks_per_quarter_note = ticks_per_quarter_note

    def beats_to_ticks(self, beats: float, beat_unit: int = 4) -> int:
        """
        Convert beats to ticks.

        Args:
            beats: Number of beats
            beat_unit: The note value that represents one beat (4 = quarter note,
                      8 = eighth note, 2 = half note). Default is 4 (quarter note).

        Returns:
            Number of ticks

        Example:
            >>> tc = TimeConverter()
            >>> tc.beats_to_ticks(4)  # 4 quarter note beats
            1920
            >>> tc.beats_to_ticks(2, beat_unit=8)  # 2 eighth note beats
            480
        """
        if beats < 0:
            raise ValueError("Beats must be non-negative")
        if beat_unit not in [1, 2, 4, 8, 16, 32]:
            raise ValueError("Beat unit must be a valid note division (1, 2, 4, 8, 16, 32)")

        # Calculate ticks based on the beat unit
        # beat_unit=4 means quarter notes, beat_unit=8 means eighth notes, etc.
        ticks_per_beat = self.ticks_per_quarter_note * (4 / beat_unit)
        return int(beats * ticks_per_beat)

    def measures_to_ticks(
        self,
        measures: float,
        time_signature_numerator: int = 4,
        time_signature_denominator: int = 4
    ) -> int:
        """
        Convert measures (bars) to ticks.

        Args:
            measures: Number of measures
            time_signature_numerator: Top number of time signature (beats per measure)
            time_signature_denominator: Bottom number of time signature (beat unit)

        Returns:
            Number of ticks

        Example:
            >>> tc = TimeConverter()
            >>> tc.measures_to_ticks(1)  # 1 measure in 4/4 time
            1920
            >>> tc.measures_to_ticks(1, time_signature_numerator=3, time_signature_denominator=4)  # 3/4 time
            1440
        """
        if measures < 0:
            raise ValueError("Measures must be non-negative")
        if time_signature_numerator <= 0 or time_signature_denominator <= 0:
            raise ValueError("Time signature values must be positive")
        if time_signature_denominator not in [1, 2, 4, 8, 16, 32]:
            raise ValueError("Time signature denominator must be a valid note division")

        # Calculate beats per measure based on time signature
        beats_per_measure = time_signature_numerator
        beat_unit = time_signature_denominator

        total_beats = measures * beats_per_measure
        return self.beats_to_ticks(total_beats, beat_unit)

    def ticks_to_beats(self, ticks: int, beat_unit: int = 4) -> float:
        """
        Convert ticks to beats.

        Args:
            ticks: Number of ticks
            beat_unit: The note value that represents one beat (default: 4 = quarter note)

        Returns:
            Number of beats

        Example:
            >>> tc = TimeConverter()
            >>> tc.ticks_to_beats(1920)  # 1920 ticks to quarter note beats
            4.0
        """
        if ticks < 0:
            raise ValueError("Ticks must be non-negative")
        if beat_unit not in [1, 2, 4, 8, 16, 32]:
            raise ValueError("Beat unit must be a valid note division")

        ticks_per_beat = self.ticks_per_quarter_note * (4 / beat_unit)
        return ticks / ticks_per_beat

    def ticks_to_measures(
        self,
        ticks: int,
        time_signature_numerator: int = 4,
        time_signature_denominator: int = 4
    ) -> float:
        """
        Convert ticks to measures (bars).

        Args:
            ticks: Number of ticks
            time_signature_numerator: Top number of time signature
            time_signature_denominator: Bottom number of time signature

        Returns:
            Number of measures

        Example:
            >>> tc = TimeConverter()
            >>> tc.ticks_to_measures(1920)  # 1920 ticks in 4/4 time
            1.0
        """
        if ticks < 0:
            raise ValueError("Ticks must be non-negative")

        beats = self.ticks_to_beats(ticks, time_signature_denominator)
        beats_per_measure = time_signature_numerator
        return beats / beats_per_measure

    def note_duration(self, note_type: str) -> int:
        """
        Get the duration in ticks for common note types.

        Args:
            note_type: One of: "whole", "half", "quarter", "eighth", "sixteenth",
                      "dotted_half", "dotted_quarter", "dotted_eighth",
                      "triplet_quarter", "triplet_eighth"

        Returns:
            Duration in ticks

        Example:
            >>> tc = TimeConverter()
            >>> tc.note_duration("quarter")
            480
            >>> tc.note_duration("dotted_quarter")
            720
        """
        durations = {
            "whole": self.ticks_per_quarter_note * 4,
            "half": self.ticks_per_quarter_note * 2,
            "quarter": self.ticks_per_quarter_note,
            "eighth": self.ticks_per_quarter_note // 2,
            "sixteenth": self.ticks_per_quarter_note // 4,
            "thirty_second": self.ticks_per_quarter_note // 8,
            # Dotted notes (1.5x duration)
            "dotted_whole": int(self.ticks_per_quarter_note * 6),
            "dotted_half": int(self.ticks_per_quarter_note * 3),
            "dotted_quarter": int(self.ticks_per_quarter_note * 1.5),
            "dotted_eighth": int(self.ticks_per_quarter_note * 0.75),
            "dotted_sixteenth": int(self.ticks_per_quarter_note * 0.375),
            # Triplets (2/3 of normal duration)
            "triplet_whole": int(self.ticks_per_quarter_note * 8/3),
            "triplet_half": int(self.ticks_per_quarter_note * 4/3),
            "triplet_quarter": int(self.ticks_per_quarter_note * 2/3),
            "triplet_eighth": int(self.ticks_per_quarter_note / 3),
            "triplet_sixteenth": int(self.ticks_per_quarter_note / 6),
        }

        if note_type not in durations:
            valid_types = ", ".join(durations.keys())
            raise ValueError(f"Invalid note type: {note_type}. Valid types: {valid_types}")

        return durations[note_type]

    @staticmethod
    def bpm_to_microseconds_per_quarter(bpm: int) -> int:
        """
        Convert BPM (beats per minute) to microseconds per quarter note.
        This is the format used in MIDI tempo messages.

        Args:
            bpm: Beats per minute

        Returns:
            Microseconds per quarter note

        Example:
            >>> TimeConverter.bpm_to_microseconds_per_quarter(120)
            500000
        """
        if bpm <= 0:
            raise ValueError("BPM must be positive")
        return int(60_000_000 / bpm)

    @staticmethod
    def microseconds_per_quarter_to_bpm(microseconds: int) -> float:
        """
        Convert microseconds per quarter note to BPM.

        Args:
            microseconds: Microseconds per quarter note

        Returns:
            Beats per minute

        Example:
            >>> TimeConverter.microseconds_per_quarter_to_bpm(500000)
            120.0
        """
        if microseconds <= 0:
            raise ValueError("Microseconds must be positive")
        return 60_000_000 / microseconds
