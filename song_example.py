from midigen import Song, Section, Key

# 1. Create a Song
song = Song(key=Key("C", "major"), tempo=120)

# 2. Add sections
song.add_section(Section(name="Verse", length=8, chord_progression="I-V-vi-IV"))
song.add_section(Section(name="Chorus", length=8, chord_progression="I-V-vi-IV"))

# 3. Add an instrument
song.add_instrument("Acoustic Grand Piano")

# 4. Generate the song for the instrument
song.generate(instrument_name="Acoustic Grand Piano", octave=4, duration=480)

# 5. Save the song
song.save("my_song.mid")

print("Song 'my_song.mid' created successfully.")
