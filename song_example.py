from midigen import Song, Section, Key, Rhythm, RHYTHM_LIBRARY

# 1. Create a Song
song = Song(key=Key("C", "major"), tempo=120)

# 2. Create a rhythm
# Let's use a simple quarter note rhythm for the verse
verse_rhythm = Rhythm(RHYTHM_LIBRARY["four_on_the_floor"])

# 3. Add sections
# The Verse will have a rhythm, the Chorus will not.
song.add_section(Section(
    name="Verse",
    length=4,
    chord_progression="I-V-vi-IV",
    rhythm=verse_rhythm
))
song.add_section(Section(
    name="Chorus",
    length=4,
    chord_progression="I-V-vi-IV"
))

# 4. Add an instrument
song.add_instrument("Acoustic Grand Piano")

# 5. Generate the song for the instrument
song.generate(instrument_name="Acoustic Grand Piano", octave=4)

# 6. Save the song
song.save("rhythm_song_example.mid")

print("Song 'rhythm_song_example.mid' created successfully.")
