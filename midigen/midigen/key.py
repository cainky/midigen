class Key:
    def __init__(self, name: str, mode: str = "major"):
        valid_keys = self.all_valid_keys()
        if name not in valid_keys():
            raise ValueError(
                f"Invalid key. Please use a valid key from the list: {format(valid_keys)}"
            )
        self.name = name
        self.mode = mode

    def __str__(self):
        return f"{self.name}{'' if self.mode == 'major' else 'm'}"

    def __repr__(self):
        return f"Key(name='{self.name}', mode='{self.mode}')"

    @classmethod
    def all_valid_keys(cls):
        return [
            cls(note, mode)
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
