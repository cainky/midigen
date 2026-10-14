VALID_KEYS = [
    (note, mode)
    for note in [
        "A",
        "A#",
        "Ab",
        "B",
        "Bb",
        "C",
        "C#",
        "Cb",
        "D",
        "D#",
        "Db",
        "E",
        "Eb",
        "F",
        "F#",
        "Fb",
        "G",
        "G#",
        "Gb",
    ]
    for mode in ["major", "minor"]
]

_LETTER_SEMITONES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_ACCIDENTAL_SEMITONES = {"": 0, "#": 1, "b": -1}
_NOTE_SPELLINGS = [
    "C",
    "B#",
    "C#",
    "Db",
    "D",
    "D#",
    "Eb",
    "E",
    "Fb",
    "E#",
    "F",
    "F#",
    "Gb",
    "G",
    "G#",
    "Ab",
    "A",
    "A#",
    "Bb",
    "B",
    "Cb",
]


def _build_key_map() -> dict:
    """Note name -> MIDI pitch for the whole MIDI range, C-1 (0) to G9 (127), e.g. "C4": 60.

    The octave number follows the letter, so "B#3" is 60 and "Cb4" is 59.
    """
    key_map = {}
    for octave in range(-1, 10):
        for name in _NOTE_SPELLINGS:
            pitch = (
                (octave + 1) * 12
                + _LETTER_SEMITONES[name[0]]
                + _ACCIDENTAL_SEMITONES[name[1:]]
            )
            if 0 <= pitch <= 127:
                key_map[f"{name}{octave}"] = pitch
    return key_map


KEY_MAP = _build_key_map()


class Key:
    def __init__(self, name: str, mode: str = "major"):
        if (name, mode) not in VALID_KEYS:
            names = ", ".join(sorted({n for n, _ in VALID_KEYS}))
            raise ValueError(
                f"Invalid key {name!r} with mode {mode!r}. "
                f"Name must be one of: {names}; mode must be 'major' or 'minor' "
                f"(e.g. Key('A', 'minor'), not Key('Am'))."
            )

        self.name = name
        self.mode = mode

    def __str__(self) -> str:
        return f"{self.name}{'' if self.mode == 'major' else 'm'}"

    def __repr__(self) -> str:
        return f"Key(name='{self.name}', mode='{self.mode}')"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Key):
            return NotImplemented
        return self.name == other.name and self.mode == other.mode

    def __hash__(self) -> int:
        return hash((self.name, self.mode))
