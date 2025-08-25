from midigen.midigen import MidiGen
from midigen.section import Section
from midigen.key import Key
from midigen.chord import ChordProgression
from midigen.instruments import INSTRUMENT_MAP


class Song:
    def __init__(self, tempo: int = 120, key: Key = Key("C")):
        self.tempo = tempo
        self.key = key
        self.sections = []
        self.midigen = MidiGen(tempo=self.tempo, key_signature=self.key)
        self.instruments = {}

    def add_section(self, section: Section):
        self.sections.append(section)

    def add_instrument(self, name: str, track_index: int = -1):
        program = INSTRUMENT_MAP.get(name)
        if program is None:
            raise ValueError(f"Instrument '{name}' not found.")

        if track_index == -1:
            track_index = len(self.midigen.tracks)
            self.midigen.add_track()

        self.midigen.set_active_track(track_index)
        track = self.midigen.get_active_track()
        # The channel should ideally match the track index for clarity
        track.add_program_change(channel=track_index, program=program)
        self.instruments[name] = track_index

    def generate(self, instrument_name: str, octave: int = 4, duration: int = 480):
        if instrument_name not in self.instruments:
            raise ValueError(f"Instrument '{instrument_name}' has not been added to the song.")

        track_index = self.instruments[instrument_name]
        track = self.midigen.tracks[track_index]
        current_time = 0

        for section in self.sections:
            progression = ChordProgression.from_roman_numerals(
                key=self.key,
                progression_string=section.chord_progression,
                octave=octave,
                duration=duration,
                time_per_chord=duration  # each chord lasts for `duration` ticks
            )

            for chord in progression.get_progression():
                # Adjust chord's start time
                for note in chord.get_chord():
                    note.time += current_time
                track.add_chord(chord)
                current_time += duration

    def save(self, filename: str):
        self.midigen.save(filename)
