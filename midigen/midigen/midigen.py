import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage


class MidiGen:
    def __init__(self, tempo=120, time_signature=(4, 4), key_signature="C"):
        self._midi_file = MidiFile()
        self._track = MidiTrack()
        self._midi_file.tracks.append(self._track)
        self.set_tempo(tempo)
        self.set_time_signature(*time_signature)
        self.set_key_signature(key_signature)

    def __str__(self):
        return str(
            f"Track: {self._track}\nTempo: {self.tempo}\n \
            Time Signature: {self.time_signature}\nKey Signature: {self.key_signature}"
        )

    def set_tempo(self, tempo):
        # Remove existing 'set_tempo' messages
        self._track = [msg for msg in self._track if msg.type != "set_tempo"]
        self.tempo = mido.bpm2tempo(tempo)
        self._track.append(MetaMessage("set_tempo", tempo=self.tempo))

    def set_time_signature(self, numerator: int, denominator: int):
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

    def set_key_signature(self, key):
        valid_keys = [
            "A",
            "A#m",
            "Ab",
            "Abm",
            "Am",
            "B",
            "Bb",
            "Bbm",
            "Bm",
            "C",
            "C#",
            "C#m",
            "Cb",
            "Cm",
            "D",
            "D#m",
            "Db",
            "Dm",
            "E",
            "Eb",
            "Ebm",
            "Em",
            "F",
            "F#",
            "F#m",
            "Fm",
            "G",
            "G#m",
            "Gb",
            "Gm",
        ]
        if key not in valid_keys:
            raise ValueError(
                "Invalid key. Please use a valid key from the list: {}".format(
                    valid_keys
                )
            )
        self.key_signature = key
        self._track.append(MetaMessage("key_signature", key=key))

    def add_program_change(self, channel, program):
        self._track.append(Message("program_change", channel=channel, program=program))

    def add_note(self, note, velocity, duration, time=0):
        self._track.append(Message("note_on", note=note, velocity=velocity, time=time))
        self._track.append(
            Message("note_off", note=note, velocity=velocity, time=duration)
        )

    def add_control_change(self, channel, control, value, time=0):
        self._track.append(
            Message(
                "control_change",
                channel=channel,
                control=control,
                value=value,
                time=time,
            )
        )

    def add_pitch_bend(self, channel, value, time=0):
        self._track.append(
            Message("pitch_bend", channel=channel, pitch=value, time=time)
        )

    def add_chord(self, notes, velocity, duration, time=0):
        for note in notes:
            self.add_note(note, velocity, duration, time)
            time = 0

    def add_arpeggio(self, notes, velocity, duration, arp_duration, time=0):
        for note in notes:
            self.add_note(note, velocity, duration, time)
            time = arp_duration

    def quantize(self, time_value, quantization_value):
        return round(time_value / quantization_value) * quantization_value

    def load_midi_file(self, filename: str):
        self._midi_file = MidiFile(filename)
        self._track = self._midi_file.tracks[0]
        return self._midi_file

    @property
    def track(self):
        return self._track

    @property
    def midi_file(self):
        return self._midi_file

    def save(self, filename):
        self._midi_file.save(filename)
