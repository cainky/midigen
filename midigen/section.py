from typing import Optional
from midigen.rhythm import Rhythm

class Section:
    def __init__(self, name: str, length: int, chord_progression: str, rhythm: Optional[Rhythm] = None):
        self.name = name
        self.length = length
        self.chord_progression = chord_progression
        self.rhythm = rhythm
