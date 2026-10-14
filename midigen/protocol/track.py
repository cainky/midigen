from __future__ import annotations

import math
import warnings

from mido import MidiTrack, Message, MetaMessage, bpm2tempo
from typing import Any, List, Tuple, TYPE_CHECKING

from midigen.theory.key import Key
from midigen.theory.note import Note

if TYPE_CHECKING:
    from midigen.composition.chord import Chord
    from midigen.composition.progression import ChordProgression
    from midigen.composition.arpeggio import Arpeggio
    from midigen.composition.drums import DrumKit
    from midigen.composition.melody import Melody


MAX_MIDI_TICKS = 32767  # Maximum value for a 15-bit signed integer

DRUM_CHANNEL = 9

# Event ordering at the same tick (lower first):
# meta messages, then notes that end here (so a repeated pitch is released
# before it is struck again), then channel messages (program/CC/pitch bend),
# then notes that start here, then the note_off of zero-length notes.
_EVENT_ORDER_META = 0
_EVENT_ORDER_NOTE_OFF = 1
_EVENT_ORDER_CHANNEL = 2
_EVENT_ORDER_NOTE_ON = 3
_EVENT_ORDER_ZERO_LENGTH_OFF = 4

# Keys that Key accepts but mido's key_signature does not, mapped to the
# enharmonic spelling mido accepts (same pitch class and mode).
_MIDO_KEY_SPELLING = {
    "A#": "Bb",
    "D#": "Eb",
    "G#": "Ab",
    "Fb": "E",
    "Cbm": "Bm",
    "Dbm": "C#m",
    "Fbm": "Em",
    "Gbm": "F#m",
}


def _mido_key_name(key) -> str:
    name = str(key)
    return _MIDO_KEY_SPELLING.get(name, name)


def _validate_time_signature(numerator, denominator) -> None:
    if (
        not (isinstance(numerator, int) and isinstance(denominator, int))
        or numerator <= 0
        or denominator <= 0
        or denominator & (denominator - 1)
    ):
        raise ValueError(
            f"Invalid time signature {numerator}/{denominator}: numerator must be a positive integer "
            "and denominator a power of 2 (1, 2, 4, 8, 16, ...)"
        )


class Track:
    def __init__(self, channel: int = 0):
        """
        Initialize a new Track instance.

        Args:
            channel: MIDI channel for this track (0-15). Default is 0.
                    Note: Channel 9 is reserved for drums in General MIDI.
        """
        if not isinstance(channel, int) or not 0 <= channel <= 15:
            raise ValueError(
                f"Channel must be an integer between 0 and 15, got {channel}"
            )

        self._track = MidiTrack()  # Internal track for metadata
        self._channel = channel
        self.notes: List[Note] = []

    def __str__(self):
        return f"Track(channel={self._channel}, notes={len(self.notes)})"

    __repr__ = __str__

    def __iter__(self):
        """Iterate over the compiled MIDI messages (lets mido's MidiFile helpers read the track)."""
        return iter(self.compile())

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
        self._track.append(MetaMessage("set_tempo", tempo=bpm2tempo(tempo)))
        self._track.append(
            MetaMessage(
                "time_signature",
                numerator=time_signature[0],
                denominator=time_signature[1],
            )
        )
        self._track.append(
            MetaMessage("key_signature", key=_mido_key_name(key_signature))
        )

    def compile(self) -> MidiTrack:
        """
        Compile all notes into a properly formatted MIDI track with correct delta timing.

        Notes are stored with absolute start times; MIDI files need delta times
        (ticks since the previous event). The compilation process:
        1. Collects note_on/note_off events for every note, plus the messages in the
           internal track (metadata, program changes, control changes, pitch bends).
           The ``time`` of those messages is treated as an absolute tick.
        2. Sorts everything by tick. At the same tick: meta messages, then note_offs,
           then channel messages, then note_ons, then the note_off of zero-length notes.
           Releasing before striking keeps repeated pitches audible.
        3. Converts absolute times to delta times and appends end_of_track.

        Returns:
            A new MidiTrack with properly timed MIDI messages.
        """
        # (absolute_time, order, sequence, message or (type, pitch, velocity) for notes)
        events: List[Tuple[int, int, int, Any]] = []

        for msg in self._track:
            if msg.type == "end_of_track":
                continue
            order = _EVENT_ORDER_META if msg.is_meta else _EVENT_ORDER_CHANNEL
            events.append((msg.time, order, len(events), msg))

        # Note messages are built once, after sorting, when their delta time is known
        for note in self.notes:
            events.append(
                (
                    note.time,
                    _EVENT_ORDER_NOTE_ON,
                    len(events),
                    ("note_on", note.pitch, note.velocity),
                )
            )
            off_order = (
                _EVENT_ORDER_ZERO_LENGTH_OFF
                if note.duration == 0
                else _EVENT_ORDER_NOTE_OFF
            )
            # Velocity 0 for note_off is standard practice (some synths prefer this)
            events.append(
                (
                    note.time + note.duration,
                    off_order,
                    len(events),
                    ("note_off", note.pitch, 0),
                )
            )

        events.sort(key=lambda event: event[:3])

        compiled = MidiTrack()
        last_time = 0
        for abs_time, _, _, item in events:
            delta = abs_time - last_time
            if isinstance(item, tuple):
                kind, pitch, velocity = item
                compiled.append(
                    Message(
                        kind,
                        note=pitch,
                        velocity=velocity,
                        channel=self._channel,
                        time=delta,
                    )
                )
            else:
                compiled.append(item.copy(time=delta))
            last_time = abs_time

        compiled.append(MetaMessage("end_of_track", time=0))
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
            raise ValueError(
                f"Invalid channel value: {channel}. Channel must be an integer between 0 and 15"
            )
        if not isinstance(program, int) or program < 0 or program > 127:
            raise ValueError(
                f"Invalid program value: {program}. Program must be an integer between 0 and 127"
            )

        self._track.append(Message("program_change", channel=channel, program=program))

    def add_control_change(
        self, channel: int = None, control: int = 0, value: int = 0, time: int = 0
    ) -> None:
        """
        Add a control change message to the MIDI track.

        Args:
            channel (int, optional): The MIDI channel. If None, uses the track's channel.
            control (int): The controller number to change. Must be between 0 and 119.
            value (int): The value to set the controller to. Must be between 0 and 127.
            time (int): Absolute time in ticks (same timeline as note times). Default is 0.

        Raises:
            ValueError: If channel, control, value, or time are outside of their respective valid ranges.
        """
        if channel is None:
            channel = self._channel

        if not isinstance(channel, int) or not 0 <= channel <= 15:
            raise ValueError(
                f"Invalid channel value: {channel}. Channel must be an integer between 0 and 15"
            )
        if not isinstance(control, int) or not 0 <= control <= 119:
            raise ValueError(
                f"Invalid control value: {control}. Control must be an integer between 0 and 119"
            )
        if not isinstance(value, int) or not 0 <= value <= 127:
            raise ValueError(
                f"Invalid value: {value}. Value must be between 0 and 127."
            )
        if not isinstance(time, int) or time < 0:
            raise ValueError(
                f"Invalid time value: {time}. Time must be a non-negative integer"
            )

        self._track.append(
            Message(
                "control_change",
                channel=channel,
                control=control,
                value=value,
                time=time,
            )
        )

    def add_pitch_bend(
        self, channel: int = None, value: int = 0, time: int = 0
    ) -> None:
        """
        Add a pitch bend message to the track.

        Args:
            channel (int, optional): The MIDI channel. If None, uses the track's channel.
            value (int): The pitch bend value (-8192 to 8191). 0 is center.
            time (int): Absolute time in ticks (same timeline as note times). Default is 0.

        Raises:
            ValueError: If parameters are outside valid ranges.
        """
        if channel is None:
            channel = self._channel

        if not isinstance(channel, int) or not 0 <= channel <= 15:
            raise ValueError(
                "Invalid channel value: channel must be an integer between 0 and 15"
            )
        if not isinstance(value, int) or value < -8192 or value > 8191:
            raise ValueError(
                "Invalid value: value must be an integer between -8192 and 8191"
            )
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

    def add_chord(self, chord: Chord) -> None:
        """
        Add a chord (simultaneous notes) to the track.

        :param chord: A Chord object.
        """
        for note in chord.get_chord():
            self.add_note(note)

    def add_chord_progression(self, chord_progression: ChordProgression):
        """
        Add a chord progression to the track. Each chord keeps its own start time.

        :param chord_progression: A ChordProgression object.
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

    def add_melody(self, melody: Melody) -> None:
        """
        Add a melody's notes to the track.

        :param melody: A Melody object.
        """
        for note in melody.get_notes():
            self.add_note(note)

    def add_drum_kit(self, drum_kit: DrumKit) -> None:
        """
        Add a drum kit to the track.

        General MIDI only plays drum sounds on channel 9 (channel 10 in 1-based
        numbering), so use a track created with ``Track(channel=9)`` or
        ``MidiGen.add_track(channel=9)``. On any other channel the drum notes play
        as pitched notes of that channel's instrument, and a warning is issued.

        :param drum_kit: A DrumKit object.
        """
        if self._channel != DRUM_CHANNEL:
            warnings.warn(
                f"Adding drums to a track on channel {self._channel}; General MIDI drums only "
                f"sound on channel {DRUM_CHANNEL}. Use add_track(channel={DRUM_CHANNEL}).",
                UserWarning,
                stacklevel=2,
            )
        for drum in drum_kit.get_drums():
            self.add_note(drum)

    def quantize(self, time_value: int, quantization_value: int) -> int:
        """
        Quantize a time value to the nearest multiple of the quantization value.

        A value exactly halfway between two multiples rounds up.

        :param time_value: The time value to quantize.
        :param quantization_value: The quantization step size.
        :return: The quantized time value.
        """

        if time_value < 0:
            raise ValueError("Time value must be non-negative.")
        if quantization_value <= 0:
            raise ValueError("Quantization value must be positive.")

        if quantization_value > MAX_MIDI_TICKS:
            raise ValueError(
                f"Quantization value must not exceed maximum MIDI ticks: {MAX_MIDI_TICKS}"
            )

        # floor(x + 0.5) rather than round(), which sends ties to the even multiple (240 -> 0 but 720 -> 960)
        return math.floor(time_value / quantization_value + 0.5) * quantization_value

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
        self._remove_meta_messages("set_tempo")
        self._track.append(MetaMessage("set_tempo", tempo=tempo_meta))

    def set_time_signature(self, numerator: int, denominator: int) -> None:
        """
        Set or update the time signature for this track.

        Args:
            numerator: Top number of time signature (beats per measure).
            denominator: Bottom number (note value that gets one beat).

        Raises:
            ValueError: If values are not positive integers or the denominator is not a power of 2.
        """
        _validate_time_signature(numerator, denominator)

        self._remove_meta_messages("time_signature")
        self._track.append(
            MetaMessage("time_signature", numerator=numerator, denominator=denominator)
        )

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

        self._remove_meta_messages("key_signature")
        self._track.append(MetaMessage("key_signature", key=_mido_key_name(key)))

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
