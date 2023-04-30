import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage

class MidiGen:
    def __init__(self, tempo=120, time_signature=(4, 4), key_signature=0):
        self._midi_file = MidiFile()
        self._track = MidiTrack()
        self._midi_file.tracks.append(self._track)
        self.set_tempo(tempo)
        self.set_time_signature(*time_signature)
        self.set_key_signature(key_signature)

    def set_tempo(self, tempo):
        self._track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(tempo)))
        return self

    def set_time_signature(self, numerator, denominator):
        self._track.append(MetaMessage('time_signature', numerator=numerator, denominator=denominator))
        return self

    def set_key_signature(self, key_signature):
        self._track.append(MetaMessage('key_signature', key=key_signature))
        return self

    def add_program_change(self, channel, program):
        self._track.append(Message('program_change', channel=channel, program=program))
        return self

    def add_note(self, note, velocity, duration, time=0):
        self._track.append(Message('note_on', note=note, velocity=velocity, time=time))
        self._track.append(Message('note_off', note=note, velocity=velocity, time=duration))
        return self

    def add_control_change(self, channel, control, value, time=0):
        self._track.append(Message('control_change', channel=channel, control=control, value=value, time=time))
        return self

    def add_pitch_bend(self, channel, value, time=0):
        self._track.append(Message('pitch_bend', channel=channel, pitch=value, time=time))
        return self

    def add_chord(self, notes, velocity, duration, time=0):
        for note in notes:
            self.add_note(note, velocity, duration, time)
            time = 0
        return self

    def add_arpeggio(self, notes, velocity, duration, arp_duration, time=0):
        for note in notes:
            self.add_note(note, velocity, duration, time)
            time = arp_duration
        return self

    def quantize(self, time_value, quantization_value):
        return round(time_value / quantization_value) * quantization_value

    def load_midi_file(self, filename):
        self._midi_file = MidiFile(filename)
        self._track = self._midi_file.tracks[0]
        
    @property
    def track(self):
        return self._track

    @property
    def midi_file(self):
        return self._midi_file

    def save(self, filename):
        self._midi_file.save(filename)
