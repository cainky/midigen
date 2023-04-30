
from midigen.MidiGen import MidiGen

def gen_example():
    # Usage example
    midi_gen = MidiGen(tempo=120, time_signature=(4, 4), key_signature=0)

    note_data = [
        (60, 64, 500),
        (62, 64, 500),
        (64, 64, 500),
        (65, 64, 500),
        (67, 64, 500),
        (69, 64, 500),
        (71, 64, 500),
        (72, 64, 1000),
    ]

    midi_gen.add_program_change(channel=0, program=0)

    for note, velocity, duration in note_data:
        midi_gen.add_note(note, velocity, duration)

    midi_gen.add_chord(notes=[72, 76, 79], velocity=64, duration=1000)
    midi_gen.add_arpeggio(notes=[60, 64, 67, 72], velocity=64, duration=250, arp_duration=125)

    midi_gen.save('output.mid')



if __name__ == "__main__":
    gen_example()