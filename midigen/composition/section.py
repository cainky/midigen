from midigen.theory.roman import parse_roman_numeral


class Section:
    def __init__(self, name: str, length: int, chord_progression: str):
        self.name = name
        self.length = length
        self.chord_progression = chord_progression
        self._validate_progression()

    def _validate_progression(self):
        if not self.chord_progression or not self.chord_progression.strip():
            raise ValueError("Chord progression cannot be empty")

        tokens = self.chord_progression.split('-')
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
