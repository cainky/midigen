from typing import List, Tuple
import os, time
from music21 import scale as m21_scale
from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo
from midigen.key import Key, VALID_KEYS
from midigen.chord import Chord, ChordProgression, Arpeggio
from midigen.scale import Scale
from midigen.note import Note
from midigen.drums import DrumKit

MAX_MIDI_TICKS = 32767  # Maximum value for a 15-bit signed integer


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
        return (
            f"Track: {self._track}\nTempo: {self.tempo}\n \
            Time Signature: {self.time_signature}\nKey Signature: {self.key_signature}"
        )

    def set_mode(self, key_signature: Key, mode: str) -> None:
        """
        Set the mode of the MidiGen object.

        :param key_signature: The key signature, e.g. 'C'.
        :param mode: The mode, e.g. 'major', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'aeolian', 'locrian'.
        """
        allowed_modes = ['major', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'aeolian', 'locrian']
        if mode not in allowed_modes:
            raise ValueError(f"Invalid mode. Please use a valid mode from the list: {allowed_modes}")
    
        self.mode = mode
        scale_degree = m21_scale.scale_degrees_to_key(key_signature, mode)
        key = Key(scale_degree, mode)
        self.set_key_signature(key)

    def set_tempo(self, tempo: int) -> None:
        """
        Set the tempo for the MIDI file.

        Args:
            bpm (int): Beats per minute. Must be an integer greater than 0.

        Raises:
            ValueError: If bpm is not an integer or is less than or equal to 0.
        """
        if not isinstance(tempo, int) or tempo <= 0:
            raise ValueError("Invalid tempo value: tempo must be a positive integer")
   
        # Remove existing 'set_tempo' messages
        self._track = [msg for msg in self._track if msg.type != "set_tempo"]
        self.tempo = bpm2tempo(tempo)
        self._track.append(MetaMessage("set_tempo", tempo=self.tempo))

    def set_time_signature(self, numerator: int, denominator: int) -> None:
        """
        Set the time signature for the MIDI file.

        Args:
            numerator (int): The numerator of the time signature. Must be an integer greater than 0.
            denominator (int): The denominator of the time signature. Must be an integer greater than 0.

        Raises:
            ValueError: If numerator or denominator is not an integer or is less than or equal to 0.
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

    def set_key_signature(self, key: Key) -> None:
        """
        Set the key signature for the MIDI file.

        Args:
            key (Key): The key signature. Must be a valid key signature (see Key class).

        Raises:
            ValueError: If key is not a valid key signature string.
        """
        self.key_signature = key
        self._track.append(MetaMessage("key_signature", key=str(key)))

    def add_program_change(self, channel: int, program: int) -> None:
        """
        Add a program change to the MIDI file.

        Args:
            channel (int): The MIDI channel for the program change. Must be an integer between 0 and 15 inclusive.
            program (int): The program number. Must be an integer between 0 and 127 inclusive.

        Raises:
            ValueError: If channel or program is not an integer or is outside the valid range.
        """

        if not isinstance(channel, int) or not 0 <= channel <= 15:
            raise ValueError(f"Invalid channel value: {channel}. Channel must be an integer between 0 and 15")
        if not isinstance(program, int) or program < 0 or program > 127:
            raise ValueError(f"Invalid program value: {program}. Program must be an integer between 0 and 127")

        self._track.append(Message("program_change", channel=channel, program=program))

    def add_control_change(self, channel: int, control: int, value: int, time: int = 0) -> None:
        """
        Add a control change message to the MIDI track.

        Args:
            channel (int): The MIDI channel to send the message to. Must be between 0 and 15.
            control (int): The controller number to change. Must be between 0 and 127.
            value (int): The value to set the controller to. Must be between 0 and 127.
            time (int): The time at which to add the control change. Default is 0.

        Raises:
            ValueError: If channel, control, or value are outside of their respective valid ranges.
        """
        if not isinstance(channel, int) or not 0 <= channel <= 15:
            raise ValueError(f"Invalid channel value: {channel}. Channel must be an integer between 0 and 15")
        if not isinstance(control, int) or not 0 <= control <= 119:
            raise ValueError(f"Invalid control value: {control}. Control must be an integer between 0 and 119")
        if not isinstance(value, int) or not 0 <= value <= 127:
            raise ValueError(f"Invalid value: {value}. Value must be between 0 and 127.")
    
        self._track.append(
            Message(
                "control_change",
                channel=channel,
                control=control,
                value=value,
                time=time,
            )
        )

    def add_pitch_bend(self, channel: int, value: int, time: int = 0) -> None:
        """
        Add a pitch bend message to the track.

        :param channel: The MIDI channel for the pitch bend.
        :param value: The pitch bend value.
        :param time: Optional, the time to schedule the pitch bend. Default is 0.
        """
        
        if not isinstance(channel, int) or not 0 <= channel <= 15:
            raise ValueError("Invalid channel value: channel must be an integer between 0 and 15")
        if not isinstance(value, int) or value < -8192 or value > 8191:
            raise ValueError("Invalid value: value must be an integer between -8192 and 8191")
        if not isinstance(time, int) or time < 0:
            raise ValueError("Invalid time value: time must be a non-negative integer")

        self._track.append(
            Message("pitchwheel", channel=channel, pitch=value, time=time)
        )
    
    def add_note(self, note: Note) -> None:
        """
        Add a note to the MIDI track.

        This method adds a note to the MIDI track with the specified velocity and duration, starting at the specified time.

        Raises:
            ValueError: If note, velocity, duration or time is not an integer or outside valid range.
        """
        self._track.append(Message("note_on", note=note.pitch, velocity=note.velocity, time=note.time))
        self._track.append(
            Message("note_off", note=note.pitch, velocity=note.velocity, time=(note.time+note.duration))
        )

    def add_rest(self, duration: int, track: int = 0) -> None:
        last_event = self._tracks[track][-1] if self._tracks[track] else None
        if last_event and last_event.type == "note_off":
            last_event.time += duration
        else:
            self._tracks[track].append(Message("note_off", note=0, velocity=0, time=duration))

    def add_chord(self, chord: Chord) -> None:
        """
        Add a chord (simultaneous notes) to the track.

        :param chord: A Chord object.
        :param velocity: The velocity of the notes.
        :param duration: The duration of the notes.
        :param time: Optional, the time to schedule the chord.
        """
        for note in chord.get_notes():
            self.add_note(note)

    def add_chord_progression(self, chord_progression: ChordProgression):
        """
        Add a chord progression to the MIDI file.

        :param chord_progression: A ChordProgression object.
        :param time: The time at which to start the chord progression.
        """
        for chord in chord_progression.get_progression():
            self.add_chord(chord)

    def add_arpeggio(
        self,
        arpeggio: Arpeggio,
    ) -> None:
        """
        Add an arpeggio (sequence of notes) to the track.
        """
        for note in arpeggio.get_sequential_notes():
            self.add_note(note)

    def add_drum_kit(self, drum_kit: DrumKit) -> None:
        """
        Add a drum kit to the MIDI file.

        :param drum_kit: A DrumKit object.
        """
        for drum in drum_kit.get_drums():
            self.add_note(drum)
            

    def quantize(self, time_value: int, quantization_value: int) -> int:
        """
        Quantize a time value to the nearest multiple of the quantization value.

        :param time_value: The time value to quantize.
        :param quantization_value: The quantization step size.
        :return: The quantized time value.
        """

        if quantization_value < 0 or time_value < 0:
            raise ValueError("Time value and quantization value must be non-negative.")

        if quantization_value > MAX_MIDI_TICKS:
            raise ValueError(f"Quantization value must not exceed maximum MIDI ticks: {MAX_MIDI_TICKS}")
        
        return round(time_value / quantization_value) * quantization_value

    def load_midi_file(self, filename: str) -> MidiFile:
        """
        Load a MIDI file into the MidiGen instance.

        :param filename: The path to the MIDI file to load.
        """
        if not filename:
            raise ValueError("Filename cannot be empty.")
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"No such file or directory: '{filename}'")
        
        self._midi_file = MidiFile(filename)
        self._track = self._midi_file.tracks[0]
        return self._midi_file

    @property
    def track(self) -> MidiTrack:
        """
        Get the track of the MIDI file.

        :return: The track of the MIDI file.
        """
        return self._track

    @property
    def midi_file(self) -> MidiFile:
        """
        Get the MIDI file.

        :return: The MIDI file.
        """
        return self._midi_file

    def save(self, filename: str) -> None:
        """
        Save the MIDI file to the specified path.

        :param filename: The path where the MIDI file should be saved.
        """
        if os.path.exists(filename):
            # Generate a unique filename by appending the current Unix time
            base, ext = os.path.splitext(filename)
            filename = f"{base}_{int(time.time())}{ext}"
        try:
            self._midi_file.save(filename)
        except FileNotFoundError:
            raise ValueError(f"Cannot save file: Invalid filename or directory: '{filename}'")
        except PermissionError:
            raise ValueError(f"Cannot save file: Permission denied for directory: '{filename}'")
        except Exception as e:
            raise ValueError(f"Cannot save file: Unknown error: {str(e)}")
