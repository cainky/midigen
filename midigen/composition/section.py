from midigen.theory.roman import parse_roman_numeral


class Section:
    def __init__(self, name: str, length: int, chord_progression: str):
        """
        Args:
            name: Section name, e.g. "Verse".
            length: Length in bars of 4/4. The compiler loops or truncates the
                progression to fill it.
            chord_progression: Dash-separated Roman numerals, e.g. "I-V-vi-IV".
        """
        if not isinstance(length, int) or isinstance(length, bool) or length <= 0:
            raise ValueError(
                f"Section length must be a positive integer number of bars, got {length!r}"
            )
        self.name = name
        self.length = length
        self.chord_progression = chord_progression
        self._validate_progression()

    def _validate_progression(self):
        if self.chord_progression is not None and not isinstance(
            self.chord_progression, str
        ):
            raise TypeError(
                "Chord progression must be a string of dash-separated Roman numerals, "
                f"got {type(self.chord_progression).__name__}"
            )
        if not self.chord_progression or not self.chord_progression.strip():
            raise ValueError("Chord progression cannot be empty")

        tokens = self.chord_progression.split("-")
        for token in tokens:
            token = token.strip()
            if not token:
                raise ValueError(
                    f"Invalid chord progression '{self.chord_progression}': "
                    "contains empty token (double dash or trailing dash)"
                )
            try:
                parse_roman_numeral(token)
            except ValueError as e:
                raise ValueError(
                    f"Invalid chord progression '{self.chord_progression}': {e}"
                ) from e
