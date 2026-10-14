from numbers import Integral

NOTE_ON = "note_on"
NOTE_OFF = "note_off"


def _is_int(value) -> bool:
    return isinstance(value, Integral) and not isinstance(value, bool)


class Note:
    def __init__(self, pitch: int, velocity: int, duration: int, time: int):
        """
        param pitch: MIDI pitch value
        param velocity: MIDI velocity value
        param duration: Duration of the note in ticks
        param time: Start time of the note in ticks
        """
        self.pitch = pitch
        self.velocity = velocity
        self.duration = duration
        self.time = time
        self._validate_note()

    def get_note(self) -> "Note":
        return self

    def _validate_note(self) -> None:
        for attribute in ("pitch", "velocity"):
            value = getattr(self, attribute)
            if not _is_int(value) or not 0 <= value <= 127:
                raise ValueError(
                    f"Invalid {attribute}, must be an integer between 0 and 127."
                )
        for attribute in ("duration", "time"):
            value = getattr(self, attribute)
            if not _is_int(value) or value < 0:
                raise ValueError(
                    f"Invalid {attribute} {value!r}, must be a non-negative integer number of ticks."
                )

    def __repr__(self):
        return f"Note(pitch={self.pitch}, velocity={self.velocity}, duration={self.duration}, time={self.time})"

    __str__ = __repr__

    def __eq__(self, other) -> bool:
        if not isinstance(other, Note):
            return NotImplemented
        return (self.pitch, self.velocity, self.duration, self.time) == (
            other.pitch,
            other.velocity,
            other.duration,
            other.time,
        )

    # Notes are mutable, so they compare by value but are not hashable
    __hash__ = None

    def __add__(self, other):
        """
        Define custom addition for Note instances or a Note and an int.
        This operation adds the pitch values, useful for operations like
        creating chords or transposing notes.

        :param other: The other Note instance or int to add.
        :return: A new Note instance with the sum of the pitch values,
                retaining the velocity, duration and time of the original note.

        :raises TypeError: If the other operand is not a Note or an int.
        """
        if isinstance(other, Note):
            return Note(
                self.pitch + other.pitch, self.velocity, self.duration, self.time
            )
        elif _is_int(other):
            return Note(self.pitch + other, self.velocity, self.duration, self.time)
        else:
            raise TypeError(
                f"unsupported operand type(s) for +: 'Note' and '{type(other).__name__}'"
            )
