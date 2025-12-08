from typing import Tuple
import os
from mido import MidiFile
from midigen.key import Key
from midigen.track import Track
from pathlib import Path


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
        :param key_signature: The key signature as a string, e.g., 'C' for C major.
        """
        self.midi_file = MidiFile()
        self.tracks = []
        self.active_track_index = None

        self.tempo = tempo
        self.time_signature = time_signature
        self.key_signature = key_signature if key_signature else Key("C")

        self.set_tempo(self.tempo)
        self.set_time_signature(*self.time_signature)
        self.set_key_signature(self.key_signature)

        # Automatically add a default track
        self.add_track()

    def __str__(self):
        """
        Return a string representation of the MidiGen object.
        :return: A string with the track, tempo, time signature, and key signature of the MidiGen object.
        """
        return f"Track: {self.tracks}\nTempo: {self.tempo}\n \
            Time Signature: {self.time_signature}\nKey Signature: {self.key_signature}"

    def add_track(self):
        """
        Add a new track to the MIDI composition and sets it as the active track.

        :return: The newly created Track instance.
        """
        new_track = Track()
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
        if track_index >= len(self.tracks):
            raise IndexError("Track index out of range.")

        self.active_track_index = track_index

    def set_tempo(self, tempo: int):
        """
        Set the tempo for every track in the MIDI file.
        Args:
            bpm (int): Beats per minute. Must be an integer greater than 0.
        Raises:
            ValueError: If bpm is not an integer or is less than or equal to 0.
        """
        if not isinstance(tempo, int) or tempo <= 0:
            raise ValueError("Invalid tempo value: tempo must be a positive integer")

        for track in self.tracks:
            track.set_tempo(tempo)

    def set_time_signature(self, numerator: int, denominator: int):
        """
        Set the time signature for every track in the MIDI file.

        Args:
            numerator (int): The numerator of the time signature. Must be an integer greater than 0.
            denominator (int): The denominator of the time signature. Must be an integer greater than 0.

        Raises:
            ValueError: If numerator or denominator is not an integer or is less than or equal to 0.
        """
        if (
            not (isinstance(numerator, int) and isinstance(denominator, int))
            or numerator <= 0
            or denominator <= 0
        ):
            raise ValueError(
                "Invalid time signature values: numerator and denominator must be positive integers"
            )

        self.time_signature = (numerator, denominator)
        for track in self.tracks:
            track.set_time_signature(numerator, denominator)

    def set_key_signature(self, key: Key):
        """
        Set the key signature for every track in the MIDI file.
        Args:
            key (Key): The key signature. Must be a valid key signature (see Key class).
        Raises:
            ValueError: If key is not a valid key signature string.
        """
        if not isinstance(key, Key):
            raise ValueError("Invalid key signature: must be a Key object")

        for track in self.tracks:
            track.set_key_signature(key)

    def set_mode(self, key_name: str, mode: str) -> None:
        """
        Set the mode of the MidiGen object.

        Args:
            key_name: The root note of the key, e.g. 'C', 'F#', 'Bb'.
            mode: The mode, e.g. 'major', 'dorian', 'phrygian', 'lydian',
                  'mixolydian', 'aeolian', 'locrian'.

        Example:
            >>> midi.set_mode('D', 'dorian')  # D Dorian mode
            >>> midi.set_mode('A', 'minor')   # A minor (aeolian)
        """
        allowed_modes = [
            "major",
            "minor",
            "dorian",
            "phrygian",
            "lydian",
            "mixolydian",
            "aeolian",
            "locrian",
        ]
        if mode not in allowed_modes:
            raise ValueError(
                f"Invalid mode. Please use a valid mode from the list: {allowed_modes}"
            )

        self.mode = mode
        key = Key(key_name, mode)
        self.set_key_signature(key)

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
        self.midi_file.tracks.clear()
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
        except FileNotFoundError:
            raise ValueError(
                f"Cannot save file: Invalid filename or directory: '{filename}'"
            )
        except PermissionError:
            raise ValueError(
                f"Cannot save file: Permission denied for directory: '{filename}'"
            )
        except Exception as e:
            raise ValueError(f"Cannot save file: Unknown error: {str(e)}")


def find_project_root() -> Path:
    """
    Attempts to locate the project root by ascending until a known marker file is found.
    """
    # Start from the current working directory.
    current_dir = Path.cwd()

    # Traverse up until we find the marker file or the root of the filesystem.
    for parent in current_dir.parents:
        # Check for a common project marker or directory
        if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
            return parent

    # If no marker is found, we just return the current working directory or you could raise an exception
    return current_dir
