from mido import MidiTrack, Message, MetaMessage, bpm2tempo
from typing import List, Dict, Any

from midigen.chord import Chord
from midigen.note import Note
from midigen.key import Key


class Track:
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.program: int = 0  # Default to Acoustic Grand Piano

    def add_program_change(self, program: int):
        """
        Sets the instrument for this track.
        """
        self.program = program

    def add_note(self, note: Note):
        """
        Adds a note to the track by creating note_on and note_off events
        with absolute timestamps.
        """
        if note.velocity > 0:
            self.events.append({
                'type': 'note_on',
                'time': note.time,
                'pitch': note.pitch,
                'velocity': note.velocity
            })
        self.events.append({
            'type': 'note_off',
            'time': note.time + note.duration,
            'pitch': note.pitch,
            'velocity': 0  # Note_off velocity is often 0
        })

    def add_chord(self, chord: Chord):
        """
        Adds a chord to the track.
        """
        for note in chord.get_chord():
            self.add_note(note)

    def compile(self, channel: int, tempo: int, time_signature: tuple, key_signature: Key) -> MidiTrack:
        """
        Builds a Mido MidiTrack from the event list.
        This involves sorting events, adding meta messages, and calculating delta times.
        """
        midi_track = MidiTrack()

        # Add initial meta messages
        midi_track.append(MetaMessage('set_tempo', tempo=bpm2tempo(tempo)))
        midi_track.append(MetaMessage('time_signature', numerator=time_signature[0], denominator=time_signature[1]))
        midi_track.append(MetaMessage('key_signature', key=str(key_signature)))
        
        # Add program change for the instrument
        midi_track.append(Message('program_change', channel=channel, program=self.program, time=0))

        # Sort events by time, then by type (note_off before note_on for same time)
        self.events.sort(key=lambda e: (e['time'], 0 if e['type'] == 'note_off' else 1))

        last_time = 0
        for event in self.events:
            absolute_time = event['time']
            delta_time = absolute_time - last_time

            midi_track.append(Message(
                event['type'],
                note=event['pitch'],
                velocity=event['velocity'],
                time=delta_time,
                channel=channel
            ))
            last_time = absolute_time

        return midi_track
