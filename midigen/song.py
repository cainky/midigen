from midigen.midigen import MidiGen
from midigen.section import Section
from midigen.key import Key
from midigen.chord import Chord, ChordProgression
from midigen.note import Note
from midigen.instruments import INSTRUMENT_MAP
from midigen.rhythm import Rhythm


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

        track = self.midigen.tracks[track_index]
        track.add_program_change(program=program)
        self.instruments[name] = track_index

    def generate(self, instrument_name: str, octave: int = 4):
        if instrument_name not in self.instruments:
            raise ValueError(f"Instrument '{instrument_name}' has not been added to the song.")

        track_index = self.instruments[instrument_name]
        track = self.midigen.tracks[track_index]
        current_time = 0
        TICKS_PER_BEAT = 480  # Standard ticks per beat

        for section in self.sections:
            # Assuming each chord in the progression lasts for 4 beats (a whole note)
            # unless a rhythm specifies otherwise.
            chord_duration = 4 * TICKS_PER_BEAT

            progression = ChordProgression.from_roman_numerals(
                key=self.key,
                progression_string=section.chord_progression,
                octave=octave,
                duration=chord_duration,
                time_per_chord=0 # time is handled by current_time
            )

            if section.rhythm:
                for chord in progression.get_progression():
                    rhythm_events = section.rhythm.get_events()
                    # Apply the rhythm over the duration of one chord
                    for is_on, event_duration in rhythm_events:
                        if is_on:
                            rhythmic_notes = []
                            for base_note in chord.get_chord():
                                rhythmic_notes.append(Note(
                                    pitch=base_note.pitch,
                                    velocity=base_note.velocity,
                                    time=current_time,
                                    duration=event_duration
                                ))
                            if rhythmic_notes:
                                track.add_chord(Chord(rhythmic_notes))
                        current_time += event_duration
            else:
                # Corrected non-rhythmic logic
                for chord in progression.get_progression():
                    notes_for_chord = []
                    for base_note in chord.get_chord():
                        notes_for_chord.append(Note(
                            pitch=base_note.pitch,
                            velocity=base_note.velocity,
                            time=current_time,
                            duration=chord_duration
                        ))
                    if notes_for_chord:
                        track.add_chord(Chord(notes_for_chord))
                    current_time += chord_duration

    def save(self, filename: str):
        self.midigen.save(filename)
