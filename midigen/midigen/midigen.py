from typing import List, Tuple
import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage
from .key import Key
from music21 import scale as m21_scale


class MidiGen:
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
        self._midi_file = MidiFile()
        self._track = MidiTrack()
        self._midi_file.tracks.append(self._track)
        self.set_tempo(tempo)
        self.set_time_signature(*time_signature)
        if key_signature is None:
            key_signature = Key("C")
        self.set_key_signature(key_signature)

    def __str__(self):
        """
        Return a string representation of the MidiGen object.
        :return: A string with the track, tempo, time signature, and key signature of the MidiGen object.
        """
        return str(
            f"Track: {self._track}\nTempo: {self.tempo}\n \
            Time Signature: {self.time_signature}\nKey Signature: {self.key_signature}"
        )

    def set_mode(self, key_signature: Key, mode: str):
        """
        Set the mode of the MidiGen object.

        :param key_signature: The key signature, e.g. 'C'.
        :param mode: The mode, e.g. 'major', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'aeolian', 'locrian'.
        """
        self.mode = mode
        scale_degree = m21_scale.scale_degrees_to_key(key_signature, mode)
        self.set_key_signature(scale_degree)

    def set_tempo(self, tempo: int):
        """
        Set the tempo of the MIDI file.

        :param bpm: The tempo in BPM.
        """

        # Remove existing 'set_tempo' messages
        self._track = [msg for msg in self._track if msg.type != "set_tempo"]
        self.tempo = mido.bpm2tempo(tempo)
        self._track.append(MetaMessage("set_tempo", tempo=self.tempo))

    def set_time_signature(self, numerator: int, denominator: int):
        """
        Set the time signature of the MIDI file.

        :param numerator: The numerator of the time signature.
        :param denominator: The denominator of the time signature.
        """
        if not (isinstance(numerator, int) and isinstance(denominator, int)):
            raise ValueError(
                "Invalid time signature value: both numerator and denominator must be integers"
            )

        if numerator <= 0 or denominator <= 0:
            raise ValueError(
                "Invalid time signature value: both numerator and denominator must be positive integers"
            )

        # Remove existing 'time_signature' messages
        self._track = [msg for msg in self._track if msg.type != "time_signature"]

        self.time_signature = MetaMessage(
            "time_signature", numerator=numerator, denominator=denominator
        )
        self._track.append(self.time_signature)

    def set_key_signature(self, key: Key):
        """
        Set the key signature of the MIDI file.

        :param key: An instance of the Key class representing the key signature.
        """
        self.key_signature = key
        self._track.append(MetaMessage("key_signature", key=str(key)))

    def add_note(self, note: int, velocity: int, duration: int, time: int = 0):
        """
        Add a note to the MIDI file.

        :param note: The MIDI note number to add.
        :param duration: The duration of the note in ticks.
        :param velocity: The velocity of the note. Default is 64.
        :param time: The time at which to add the note. Default is 0.
        """
        self._track.append(Message("note_on", note=note, velocity=velocity, time=time))
        self._track.append(
            Message("note_off", note=note, velocity=velocity, time=duration)
        )

    def add_program_change(self, channel: int, program: int):
        """
        Add a program change message to the track.

        :param channel: The MIDI channel for the program change.
        :param program: The program number to change to.
        """
        self._track.append(Message("program_change", channel=channel, program=program))

    def add_control_change(self, channel: int, control: int, value: int, time: int = 0):
        """
        Add a control change message to the track.

        :param channel: The MIDI channel for the control change.
        :param control: The control number to change.
        :param value: The value to set the control to.
        :param time: Optional, the time to schedule the control change. Default is 0.
        """
        self._track.append(
            Message(
                "control_change",
                channel=channel,
                control=control,
                value=value,
                time=time,
            )
        )

    def add_pitch_bend(self, channel: int, value: int, time: int = 0):
        """
        Add a pitch bend message to the track.

        :param channel: The MIDI channel for the pitch bend.
        :param value: The pitch bend value.
        :param time: Optional, the time to schedule the pitch bend. Default is 0.
        """
        self._track.append(
            Message("pitchwheel", channel=channel, pitch=value, time=time)
        )

    def add_chord(self, notes: List[int], velocity: int, duration: int, time: int = 0):
        """
        Add a chord (simultaneous notes) to the track.

        :param notes: A list of note values for the chord.
        :param velocity: The velocity of the notes.
        :param duration: The duration of the notes.
        :param time: Optional, the time to schedule the chord. Default is 0.
        """
        for note in notes:
            self.add_note(note, velocity, duration, time)
            time = 0

    def add_arpeggio(
        self,
        notes: List[int],
        velocity: int,
        duration: int,
        arp_duration: int,
        time: int = 0,
    ):
        """
        Add an arpeggio (sequence of notes) to the track.

        :param notes: A list of note values for the arpeggio.
        :param velocity: The velocity of the notes.
        :param duration: The duration of each individual note.
        :param arp_duration: The time between the start of each note in the arpeggio.
        :param time: Optional, the time to schedule the arpeggio. Default is 0.
        """
        for note in notes:
            self.add_note(note, velocity, duration, time)
            time = arp_duration

    def quantize(self, time_value: int, quantization_value: int):
        """
        Quantize a time value to the nearest multiple of the quantization value.

        :param time_value: The time value to quantize.
        :param quantization_value: The quantization step size.
        :return: The quantized time value.
        """
        return round(time_value / quantization_value) * quantization_value

    def load_midi_file(self, filename: str):
        """
        Load a MIDI file into the MidiGen instance.

        :param filename: The path to the MIDI file to load.
        """
        self._midi_file = MidiFile(filename)
        self._track = self._midi_file.tracks[0]
        return self._midi_file

    @property
    def track(self):
        """
        Get the track of the MIDI file.

        :return: The track of the MIDI file.
        """
        return self._track

    @property
    def midi_file(self):
        """
        Get the MIDI file.

        :return: The MIDI file.
        """
        return self._midi_file

    def save(self, filename: str):
        """
        Save the MIDI file to the specified path.

        :param filename: The path where the MIDI file should be saved.
        """
        self._midi_file.save(filename)
