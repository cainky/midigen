from mido import MidiTrack, Message
from midigen.note import Note, NOTE_ON, NOTE_OFF

class Track:
    def __init__(self):
        """
        Initialize a new Track instance.
        """
        self._track = MidiTrack()
        self._notes = []

    def add_note(self, note: Note) -> None:
        """
        Add a note to the MIDI track.

        This method adds a note to the MIDI track with the specified velocity and duration, starting at the specified time.
        """
        self._notes.append(note)
        self._track.append(Message("note_on", note=note.pitch, velocity=note.velocity, time=note.time))
        self._track.append(Message("note_off", note=note.pitch, velocity=note.velocity, time=note.duration))

    # Add more methods as needed, for example add_chord, add_arpeggio, etc.

    def get_midi_track(self):
        return self._track
