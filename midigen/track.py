from mido import MidiTrack, Message, MetaMessage, bpm2tempo
from typing import List


from midigen.chord import Chord, ChordProgression, Arpeggio
from midigen.key import Key
from midigen.note import Note
from midigen.drums import DrumKit


MAX_MIDI_TICKS = 32767  # Maximum value for a 15-bit signed integer


class Track:
    def __init__(self):
        """
        Initialize a new Track instance.
        """
        self.track = MidiTrack()
        self.notes = []
    
    def __str__(self):
        return f"Notes: {self.notes}"
    
    def get_notes(self) -> List[Note]:
        return self.notes

    def get_track(self):
        return self.track
    
    def apply_global_settings(self, tempo, time_signature, key_signature):
        self.track.append(MetaMessage('set_tempo', tempo=bpm2tempo(tempo)))
        self.track.append(MetaMessage('time_signature', numerator=time_signature[0], denominator=time_signature[1]))
        self.track.append(MetaMessage('key_signature', key=str(key_signature)))

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

        self.track.append(Message("program_change", channel=channel, program=program))

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
    
        self.track.append(
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

        self.track.append(
            Message("pitchwheel", channel=channel, pitch=value, time=time)
        )
    
    def add_note(self, note: Note) -> None:
        """
        Add a note to the MIDI track.

        This method adds a note to the MIDI track with the specified velocity and duration, starting at the specified time.

        Raises:
            ValueError: If note, velocity, duration or time is not an integer or outside valid range.
        """
        note_on_msg = Message("note_on", note=note.pitch, velocity=note.velocity, time=note.time)
        self.track.append(note_on_msg)
        self.notes.append(note)
    
    def add_note_off_messages(self) -> None:
        """
        This method is crucial for preventing timing offsets if the sequence 
        of note_on and note_off messages is not properly managed due to the fundamental design of MIDI
        
        Should be called after all notes or chords are added to the track and before the track is saved or further 
        processed. This is especially important in a live setting or when dynamically adding notes to ensure that 
        playback reflects the exact intended timing without any shifts.
        """
        for note in self.notes:
            note_off_msg = Message("note_off", note=note.pitch, velocity=note.velocity, time=(note.time+note.duration))
            self.track.append(note_off_msg)

    def add_rest(self, duration: int, track: int = 0) -> None:
        last_event = self.tracks[track][-1] if self.tracks[track] else None
        if last_event and last_event.type == "note_off":
            last_event.time += duration
        else:
            self.tracks[track].append(Message("note_off", note=0, velocity=0, time=duration))

    def add_chord(self, chord: Chord) -> None:
        """
        Add a chord (simultaneous notes) to the track.

        :param chord: A Chord object.
        """
        for note in chord.get_chord():
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

    
    def set_tempo(self, tempo: int) -> None:
        if not isinstance(tempo, int) or tempo <= 0:
            raise ValueError("Invalid tempo value: tempo must be a positive integer")
        
        tempo_meta = bpm2tempo(tempo)
        self.track = [msg for msg in self.track if msg.type != "set_tempo"]
        self.track.append(MetaMessage('set_tempo', tempo=tempo_meta))

    def set_time_signature(self, numerator: int, denominator: int) -> None:
        if not (isinstance(numerator, int) and isinstance(denominator, int)) or numerator <= 0 or denominator <= 0:
            raise ValueError("Invalid time signature values: numerator and denominator must be positive integers")

        self.track = [msg for msg in self.track if msg.type != "time_signature"]
        self.track.append(MetaMessage('time_signature', numerator=numerator, denominator=denominator))

    def set_key_signature(self, key: Key) -> None:
        if not isinstance(key, Key):
            raise ValueError("Invalid key signature: must be a Key object")

        self.track = [msg for msg in self.track if msg.type != "key_signature"]
        self.track.append(MetaMessage('key_signature', key=str(key)))
