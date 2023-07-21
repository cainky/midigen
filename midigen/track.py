from mido import MidiTrack, Message
from midigen.note import Note, NOTE_ON, NOTE_OFF
from typing import List

class Track:
    def __init__(self):
        """
        Initialize a new Track instance.
        """
        self._track = MidiTrack()
        self._notes = []
    
    def get_notes(self) -> List[Note]:
        return self._notes

    def get_track(self):
        return self._track

    def add_note(self, note: Note) -> None:
        """
        Add a note to the MIDI track.

        This method adds a note to the MIDI track with the specified velocity and duration, starting at the specified time.
        """
        self._notes.append(note)
        self._track.append(Message(NOTE_ON, note=note.pitch, velocity=note.velocity, time=note.time))
        self._track.append(Message(NOTE_OFF, note=note.pitch, velocity=note.velocity, time=note.duration))
    
    
