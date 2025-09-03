from typing import Tuple
import os
from music21 import scale as m21_scale
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
        self.midi_file = MidiFile()
        self.tracks: list[Track] = []
        self.active_track_index: int | None = None

        self.tempo = tempo
        self.time_signature = time_signature
        self.key_signature = key_signature if key_signature else Key("C")

        # Automatically add a default track
        self.add_track()

    def __str__(self):
        return f"Tracks: {len(self.tracks)}\nTempo: {self.tempo}\n" \
               f"Time Signature: {self.time_signature}\nKey Signature: {self.key_signature}"

    def add_track(self):
        new_track = Track()
        self.tracks.append(new_track)
        self.active_track_index = len(self.tracks) - 1
        return new_track

    def get_active_track(self):
        if not self.tracks:
            raise ValueError("No tracks available in the MIDI file.")
        if self.active_track_index is None:
            return self.tracks[0]
        return self.tracks[self.active_track_index]

    def set_active_track(self, track_index):
        if not 0 <= track_index < len(self.tracks):
            raise IndexError("Track index out of range.")
        self.active_track_index = track_index

    def set_mode(self, key_signature: Key, mode: str):
        # This method might need reconsideration, as key signature is now a track-level concern
        # For now, we'll just update the default key_signature for new tracks
        allowed_modes = ["major", "dorian", "phrygian", "lydian", "mixolydian", "aeolian", "locrian"]
        if mode not in allowed_modes:
            raise ValueError(f"Invalid mode. Please use a valid mode from the list: {allowed_modes}")

        # music21 can be particular about key names
        key_name = key_signature.name.replace('b', '-')
        scale_degree = m21_scale.scale_degrees_to_key(key_name, mode)
        self.key_signature = Key(scale_degree.name.replace('-', 'b'), mode)


    def save(self, filename: str) -> str:
        self.midi_file.tracks.clear()
        for i, track in enumerate(self.tracks):
            channel = i
            compiled_track = track.compile(
                channel=channel,
                tempo=self.tempo,
                time_signature=self.time_signature,
                key_signature=self.key_signature
            )
            self.midi_file.tracks.append(compiled_track)

        project_root = find_project_root()
        output_dir = os.path.join(project_root, "generate", "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        filepath = os.path.join(output_dir, filename)

        try:
            self.midi_file.save(filename=filepath)
            return filepath
        except Exception as e:
            raise IOError(f"Cannot save file: {str(e)}")


def find_project_root() -> Path:
    current_dir = Path.cwd()
    for parent in current_dir.parents:
        if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
            return parent
    return current_dir
