from midigen.note import Note
from typing import List

GM1_DRUM_MAP = {
    "Acoustic Bass Drum": 35,
    "Bass Drum 1": 36,
    "Side Stick": 37,
    "Acoustic Snare": 38,
    "Hand Clap": 39,
    "Electric Snare": 40,
    "Low Floor Tom": 41,
    "Closed Hi Hat": 42,
    "High Floor Tom": 43,
    "Pedal Hi-Hat": 44,
    "Low Tom": 45,
    "Open Hi-Hat": 46,
    "Low-Mid Tom": 47,
    "Hi-Mid Tom": 48,
    "Crash Cymbal 1": 49,
    "High Tom": 50,
    "Ride Cymbal 1": 51,
    "Chinese Cymbal": 52,
    "Ride Bell": 53,
    "Tambourine": 54,
    "Splash Cymbal": 55,
    "Cowbell": 56,
    "Crash Cymbal 2": 57,
    "Vibraslap": 58,
    "Ride Cymbal 2": 59,
    "Hi Bongo": 60,
    "Low Bongo": 61,
    "Mute Hi Conga": 62,
    "Open Hi Conga": 63,
    "Low Conga": 64,
    "High Timbale": 65,
    "Low Timbale": 66,
    "High Agogo": 67,
    "Low Agogo": 68,
    "Cabasa": 69,
    "Maracas": 70,
    "Short Whistle": 71,
    "Long Whistle": 72,
    "Short Guiro": 73,
    "Long Guiro": 74,
    "Claves": 75,
    "Hi Wood Block": 76,
    "Low Wood Block": 77,
    "Mute Cuica": 78,
    "Open Cuica": 79,
    "Mute Triangle": 80,
    "Open Triangle": 81,
}


class Drum:
    """
    A drum sound in a drum kit, represented as a MIDI note.
    """

    def __init__(self, pitch: int, velocity: int, duration: int, time: int):
        if duration < 0:
            raise ValueError("Duration must be non-negative")
        if velocity < 0:
            raise ValueError("Velocity must be non-negative")
        if not 0 <= pitch <= 127:
            raise ValueError("Pitch must be within the MIDI standard range of 0 to 127")

        self.note = Note(pitch, velocity, duration, time)


class DrumKit:
    """
    A collection of drum sounds, each represented as a MIDI note.
    """

    def __init__(self):
        self.drums = []

    def add_drum(
        self, drum_name: str, velocity: int = 64, duration: int = 1, time: int = 0
    ) -> None:
        """
        Add a drum to the drum kit.

        :param drum_name: The name of the drum, as defined in the GM1_DRUM_MAP.
        :param velocity: The velocity of the drum sound.
        :param duration: The duration of the drum sound.
        :param time: The time at which the drum sound should start.
        """
        if drum_name not in GM1_DRUM_MAP:
            raise ValueError(
                f"Invalid drum name: {drum_name}. Please use a valid drum name from the GM1_DRUM_MAP."
            )

        drum = Drum(GM1_DRUM_MAP[drum_name], velocity, duration, time)
        self.drums.append(drum)

    def get_drums(self) -> List[Note]:
        """
        Get the list of drums in the drum kit.

        :return: A list of Drum objects.
        """
        return [drum.note for drum in self.drums]
