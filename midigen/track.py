from mido import MidiTrack, Message, MetaMessage, bpm2tempo
from typing import List, Tuple
import warnings


from midigen.chord import Chord, ChordProgression, Arpeggio
from midigen.key import Key
from midigen.note import Note
from midigen.drums import DrumKit


MAX_MIDI_TICKS = 32767  # Maximum value for a 15-bit signed integer

# Event ordering constants for stable sort at same tick
# Note-on before note-off ensures zero-duration notes are handled correctly
_EVENT_ORDER_NOTE_ON = 0
_EVENT_ORDER_NOTE_OFF = 1


class Track:
    def __init__(self, channel: int = 0):
        """
        Initialize a new Track instance.

        Args:
            channel: MIDI channel for this track (0-15). Default is 0.
                    Note: Channel 9 is reserved for drums in General MIDI.
        """
        if not isinstance(channel, int) or not 0 <= channel <= 15:
            raise ValueError(f"Channel must be an integer between 0 and 15, got {channel}")

        self._track = MidiTrack()  # Internal track for metadata
        self._channel = channel
        self.notes: List[Note] = []
    
    def __str__(self):
        return f"Track(channel={self._channel}, notes={len(self.notes)})"

    @property
    def track(self) -> MidiTrack:
        """Backward compatibility property. Prefer using compile() for output."""
        return self._track

    @property
    def channel(self) -> int:
        """The MIDI channel for this track."""
        return self._channel

    def get_notes(self) -> List[Note]:
        return self.notes

    def get_track(self) -> MidiTrack:
        """
        Get the raw internal track. For proper MIDI output, use compile() instead.

        Returns:
            The internal MidiTrack with metadata messages only.
        """
        return self._track

    def apply_global_settings(self, tempo, time_signature, key_signature):
        """Apply tempo, time signature, and key signature metadata to the track."""
        self._track.append(MetaMessage('set_tempo', tempo=bpm2tempo(tempo)))
        self._track.append(MetaMessage('time_signature', numerator=time_signature[0], denominator=time_signature[1]))
        self._track.append(MetaMessage('key_signature', key=str(key_signature)))

    def compile(self) -> MidiTrack:
        """
        Compile all notes into a properly formatted MIDI track with correct delta timing.

        This method converts the stored notes into MIDI messages with proper delta times
        (time since previous event) rather than absolute times. This is the correct
        format for MIDI playback.

        The compilation process:
        1. Creates note_on and note_off events with absolute times
        2. Sorts events by time, with note_on before note_off at the same tick
           (ensures zero-duration notes are handled correctly)
        3. Converts absolute times to delta times
        4. Prepends metadata messages (tempo, time signature, key signature)

        Returns:
            A new MidiTrack with properly timed MIDI messages.
        """
        # Collect all note events with absolute times
        # Format: (absolute_time, event_order, event_type, note)
        events: List[Tuple[int, int, str, Note]] = []

        for note in self.notes:
            events.append((note.time, _EVENT_ORDER_NOTE_ON, 'note_on', note))
            events.append((note.time + note.duration, _EVENT_ORDER_NOTE_OFF, 'note_off', note))

        # Sort by absolute time, then by event order (note_on before note_off at same tick)
        events.sort(key=lambda x: (x[0], x[1]))

        # Create the compiled track starting with metadata
        compiled = MidiTrack()

        # Copy metadata messages from internal track (tempo, time sig, key sig, program change)
        for msg in self._track:
            compiled.append(msg.copy())

        # Convert to delta times and append note messages
        last_time = 0
        for abs_time, _, event_type, note in events:
            delta = abs_time - last_time

            # Velocity 0 for note_off is standard practice (some synths prefer this)
            velocity = note.velocity if event_type == 'note_on' else 0

            compiled.append(Message(
                event_type,
                note=note.pitch,
                velocity=velocity,
                channel=self._channel,
                time=delta
            ))
            last_time = abs_time

        # Add end of track marker
        compiled.append(MetaMessage('end_of_track', time=0))

        return compiled

    def add_program_change(self, channel: int = None, program: int = 0) -> None:
        """
        Add a program change (instrument selection) to the MIDI track.

        Args:
            channel (int, optional): The MIDI channel. If None, uses the track's channel.
            program (int): The program number (instrument). Must be 0-127.

        Raises:
            ValueError: If channel or program is outside the valid range.
        """
        if channel is None:
            channel = self._channel

        if not isinstance(channel, int) or not 0 <= channel <= 15:
            raise ValueError(f"Invalid channel value: {channel}. Channel must be an integer between 0 and 15")
        if not isinstance(program, int) or program < 0 or program > 127:
            raise ValueError(f"Invalid program value: {program}. Program must be an integer between 0 and 127")

        self._track.append(Message("program_change", channel=channel, program=program))

    def add_control_change(self, channel: int = None, control: int = 0, value: int = 0, time: int = 0) -> None:
        """
        Add a control change message to the MIDI track.

        Args:
            channel (int, optional): The MIDI channel. If None, uses the track's channel.
            control (int): The controller number to change. Must be between 0 and 119.
            value (int): The value to set the controller to. Must be between 0 and 127.
            time (int): The delta time for the control change. Default is 0.

        Raises:
            ValueError: If channel, control, or value are outside of their respective valid ranges.
        """
        if channel is None:
            channel = self._channel

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

    def add_pitch_bend(self, channel: int = None, value: int = 0, time: int = 0) -> None:
        """
        Add a pitch bend message to the track.

        Args:
            channel (int, optional): The MIDI channel. If None, uses the track's channel.
            value (int): The pitch bend value (-8192 to 8191). 0 is center.
            time (int): The delta time for the pitch bend. Default is 0.

        Raises:
            ValueError: If parameters are outside valid ranges.
        """
        if channel is None:
            channel = self._channel

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
        Add a note to the track.

        Notes are stored internally and converted to MIDI messages when compile() is called.
        This allows proper delta-time calculation across all notes.

        Args:
            note: A Note object with pitch, velocity, duration, and time.
        """
        if not isinstance(note, Note):
            raise TypeError(f"Expected Note object, got {type(note).__name__}")
        self.notes.append(note)

    def add_note_off_messages(self) -> None:
        """
        DEPRECATED: This method is no longer needed.

        Use compile() instead, which properly handles note_on/note_off messages
        with correct delta timing.

        This method is kept for backward compatibility but does nothing.
        """
        warnings.warn(
            "add_note_off_messages() is deprecated and has no effect. "
            "Use compile() for proper MIDI output with correct delta timing.",
            DeprecationWarning,
            stacklevel=2
        )
        # No-op: compile() handles note_off messages correctly

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
        """
        Set or update the tempo for this track.

        Args:
            tempo: Tempo in BPM (beats per minute). Must be a positive integer.

        Raises:
            ValueError: If tempo is not a positive integer.
        """
        if not isinstance(tempo, int) or tempo <= 0:
            raise ValueError("Invalid tempo value: tempo must be a positive integer")

        tempo_meta = bpm2tempo(tempo)
        self._remove_meta_messages('set_tempo')
        self._track.append(MetaMessage('set_tempo', tempo=tempo_meta))

    def set_time_signature(self, numerator: int, denominator: int) -> None:
        """
        Set or update the time signature for this track.

        Args:
            numerator: Top number of time signature (beats per measure).
            denominator: Bottom number (note value that gets one beat).

        Raises:
            ValueError: If values are not positive integers.
        """
        if not (isinstance(numerator, int) and isinstance(denominator, int)) or numerator <= 0 or denominator <= 0:
            raise ValueError("Invalid time signature values: numerator and denominator must be positive integers")

        self._remove_meta_messages('time_signature')
        self._track.append(MetaMessage('time_signature', numerator=numerator, denominator=denominator))

    def set_key_signature(self, key: Key) -> None:
        """
        Set or update the key signature for this track.

        Args:
            key: A Key object representing the key signature.

        Raises:
            ValueError: If key is not a Key object.
        """
        if not isinstance(key, Key):
            raise ValueError("Invalid key signature: must be a Key object")

        self._remove_meta_messages('key_signature')
        self._track.append(MetaMessage('key_signature', key=str(key)))

    def _remove_meta_messages(self, msg_type: str) -> None:
        """
        Remove all meta messages of a specific type from the internal track.

        This preserves the MidiTrack type (avoiding type mutation to list).

        Args:
            msg_type: The type of meta message to remove (e.g., 'set_tempo').
        """
        # Build a new MidiTrack without the specified message type
        new_track = MidiTrack()
        for msg in self._track:
            if msg.type != msg_type:
                new_track.append(msg)
        self._track = new_track
