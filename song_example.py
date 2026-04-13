"""High-level API example — compose with Song and MidiCompiler."""
from midigen import Song, Section, Key, MidiCompiler

song = Song(key=Key("C", "major"), tempo=120)
song.add_section(Section("Intro", 4, "I-V"))
song.add_section(Section("Verse", 8, "I-V-vi-IV"))
song.add_section(Section("Chorus", 8, "IV-I-V-vi"))
song.add_instrument("Acoustic Grand Piano")

MidiCompiler(song).compile().save("my_song.mid")
print("Saved my_song.mid")
