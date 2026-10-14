from typing import Tuple
import os
from mido import MidiFile
from midigen.theory.key import Key, VALID_KEYS
from midigen.protocol.track import Track, _validate_time_signature


# Semitones from the relative major's tonic up to the mode's tonic
_MODE_OFFSETS = {
    "major": 0,
    "ionian": 0,
    "dorian": 2,
    "phrygian": 4,
    "lydian": 5,
    "mixolydian": 7,
    "aeolian": 9,
    "minor": 9,
    "locrian": 11,
}
_MINOR_MODES = ("minor", "aeolian")
_NOTE_NAMES = {n for n, _ in VALID_KEYS}
_LETTER_SEMITONES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
# Major key names with the fewest accidentals for each pitch class
_MAJOR_KEY_NAMES = ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


class MidiGen(MidiFile):
    def __init__(
        self,
        tempo: int = 120,
        time_signature: Tuple = (4, 4),
        key_signature: Key = None,
    ):
        """
        Initialize a new MidiGen instance.

        :param tempo: The tempo in BPM.
        :param time_signature: 2 ints tuple representing the numerator and denominator.
        :param key_signature: A Key object, e.g. Key("C") or Key("A", "minor"). Defaults to C major.
        """
        super().__init__()
        self.midi_file = MidiFile()
        self.tracks = []
        self.active_track_index = None
        self.mode = None

        self.set_tempo(tempo)
        self.set_time_signature(*time_signature)
        self.set_key_signature(key_signature if key_signature else Key("C"))

        # Automatically add a default track
        self.add_track()

    def __str__(self):
        """
        Return a string representation of the MidiGen object.
        :return: A string with the tracks, tempo, time signature, and key signature of the MidiGen object.
        """
        tracks = ", ".join(str(track) for track in self.tracks)
        return (
            f"Tracks: [{tracks}]\nTempo: {self.tempo}\n"
            f"Time Signature: {self.time_signature[0]}/{self.time_signature[1]}\n"
            f"Key Signature: {self.key_signature}"
        )

    def __repr__(self):
        return (
            f"MidiGen(tempo={self.tempo}, time_signature={self.time_signature}, "
            f"key_signature={self.key_signature!r}, tracks={len(self.tracks)})"
        )

    def add_track(self, channel: int = 0):
        """
        Add a new track to the MIDI composition and sets it as the active track.

        :param channel: MIDI channel for the track (0-15). Use 9 for drums.
        :return: The newly created Track instance.
        """
        new_track = Track(channel=channel)
        new_track.apply_global_settings(
            self.tempo, self.time_signature, self.key_signature
        )

        self.tracks.append(new_track)
        self.active_track_index = len(self.tracks) - 1  # Set the new track as active
        return new_track

    def get_active_track(self):
        """
        Returns the currently active track. If there's only one track, it returns that track.
        """
        if not self.tracks:
            raise ValueError("No tracks available in the MIDI file.")

        if len(self.tracks) == 1:
            return self.tracks[0]

        return self.tracks[self.active_track_index]

    def set_active_track(self, track_index):
        """
        Sets the active track based on the provided track index.

        :param track_index: The index of the track to be set as active.
        """
        if not isinstance(track_index, int) or not 0 <= track_index < len(self.tracks):
            raise IndexError(
                f"Track index {track_index!r} out of range (0-{len(self.tracks) - 1})."
            )

        self.active_track_index = track_index

    def set_tempo(self, tempo: int):
        """
        Set the tempo for every track, including tracks added later.
        Args:
            tempo (int): Beats per minute. Must be an integer greater than 0.
        Raises:
            ValueError: If tempo is not an integer or is less than or equal to 0.
        """
        if not isinstance(tempo, int) or tempo <= 0:
            raise ValueError("Invalid tempo value: tempo must be a positive integer")

        self.tempo = tempo
        for track in self.tracks:
            track.set_tempo(tempo)

    def set_time_signature(self, numerator: int, denominator: int):
        """
        Set the time signature for every track, including tracks added later.

        Args:
            numerator (int): The numerator of the time signature. Must be an integer greater than 0.
            denominator (int): The denominator of the time signature. Must be a power of 2 (1, 2, 4, 8, ...).

        Raises:
            ValueError: If numerator is not a positive integer or denominator is not a power of 2.
        """
        _validate_time_signature(numerator, denominator)

        self.time_signature = (numerator, denominator)
        for track in self.tracks:
            track.set_time_signature(numerator, denominator)

    def set_key_signature(self, key: Key):
        """
        Set the key signature for every track, including tracks added later.
        Args:
            key (Key): The key signature. Must be a valid key signature (see Key class).
        Raises:
            ValueError: If key is not a Key object.
        """
        if not isinstance(key, Key):
            raise ValueError("Invalid key signature: must be a Key object")

        self.key_signature = key
        for track in self.tracks:
            track.set_key_signature(key)

    def set_mode(self, key_name: str, mode: str) -> None:
        """
        Set the key signature from a tonic and a mode.

        MIDI key signatures only describe major or minor keys, so modes are written
        as the key signature that has the same accidentals: D dorian is written as
        C major, A aeolian as A minor. ``self.mode`` keeps the requested mode and
        ``self.key_signature`` holds the Key that was written.

        Args:
            key_name: The root note of the key, e.g. 'C', 'F#', 'Bb'.
            mode: One of 'major', 'minor', 'ionian', 'dorian', 'phrygian',
                  'lydian', 'mixolydian', 'aeolian', 'locrian'.

        Example:
            >>> midi.set_mode('D', 'dorian')  # writes C major's signature (no sharps or flats)
            >>> midi.set_mode('A', 'minor')   # writes A minor
        """
        if mode not in _MODE_OFFSETS:
            raise ValueError(
                f"Invalid mode {mode!r}. Please use a valid mode from the list: {list(_MODE_OFFSETS)}"
            )
        if key_name not in _NOTE_NAMES:
            raise ValueError(
                f"Invalid key name {key_name!r}. Must be one of: {sorted(_NOTE_NAMES)}"
            )

        if mode in _MINOR_MODES:
            key = Key(key_name, "minor")
        else:
            accidental = key_name[1:]
            tonic = _LETTER_SEMITONES[key_name[0]] + (
                1 if accidental == "#" else -1 if accidental == "b" else 0
            )
            relative_major = _MAJOR_KEY_NAMES[(tonic - _MODE_OFFSETS[mode]) % 12]
            if relative_major == "F#" and accidental == "b":
                relative_major = "Gb"
            key = Key(relative_major, "major")

        self.set_key_signature(key)
        self.mode = mode

    def save(self, filename: str, output_dir: str = None) -> str:
        """
        Compile all tracks and save the MIDI file to the specified path.

        This method compiles all tracks with proper delta timing and saves
        the complete MIDI composition to the specified filename.

        Args:
            filename (str): The name of the MIDI file (e.g., "my_song.mid")
            output_dir (str, optional): Directory to save the file. If None, uses current directory.
                                       Can be absolute or relative path.

        Returns:
            str: The full path to the saved file

        Example:
            >>> midi = MidiGen()
            >>> midi.save("song.mid")  # Saves to current directory
            >>> midi.save("song.mid", "output/music")  # Saves to output/music/
            >>> midi.save("song.mid", "/absolute/path")  # Saves to absolute path
        """
        # Written with this object's resolution, so the file matches self.length
        self.midi_file = MidiFile(type=self.type, ticks_per_beat=self.ticks_per_beat)
        for track in self.tracks:
            # Use compile() for proper delta-time MIDI output
            compiled_track = track.compile()
            self.midi_file.tracks.append(compiled_track)

        # Determine output directory
        if output_dir is None:
            # Use current working directory if not specified
            output_dir = os.getcwd()

        # Create directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)  # Recursively create directory if it does not exist

        filepath = os.path.join(output_dir, filename)
        try:
            self.midi_file.save(filename=filepath)
            return filepath
        except FileNotFoundError as e:
            raise ValueError(
                f"Cannot save file: Invalid filename or directory: '{filepath}'"
            ) from e
        except PermissionError as e:
            raise ValueError(
                f"Cannot save file: Permission denied: '{filepath}'"
            ) from e
        except Exception as e:
            raise ValueError(f"Cannot save file: Unknown error: {str(e)}") from e
