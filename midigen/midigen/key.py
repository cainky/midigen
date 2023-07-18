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

KEY_MAP = {
    "C": 60,
    "C#": 61,
    "Db": 61,
    "D": 62,
    "D#": 63,
    "Eb": 63,
    "E": 64,
    "F": 65,
    "F#": 66,
    "Gb": 66,
    "G": 67,
    "G#": 68,
    "Ab": 68,
    "A": 69,
    "A#": 70,
    "Bb": 70,
    "B": 71
}


class Key:
    def __init__(self, name: str, mode: str = "major"):
        if (name, mode) not in VALID_KEYS:
            raise ValueError(
                f"Invalid key. Please use a valid key from the list: {format(VALID_KEYS)}"
            )

        self.name = name
        self.mode = mode

    def __str__(self) -> str:
        return f"{self.name}{'' if self.mode == 'major' else 'm'}"

    def __repr__(self) -> str:
        return f"Key(name='{self.name}', mode='{self.mode}')"

    def __eq__(self, other) -> bool:
        if isinstance(other, Key):
            return self.name == other.name and self.mode == other.mode
        return False
