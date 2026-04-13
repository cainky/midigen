class Scale:
    """
    Utility class for generating various musical scales.
    All methods return a list of MIDI note numbers.
    """

    # Interval patterns (in semitones)
    # W = Whole step (2 semitones), H = Half step (1 semitone)

    # Basic scales
    MAJOR_INTERVALS = [2, 2, 1, 2, 2, 2, 1]  # W W H W W W H
    MINOR_INTERVALS = [2, 1, 2, 2, 1, 2, 2]  # W H W W H W W (Natural minor)
    HARMONIC_MINOR_INTERVALS = [2, 1, 2, 2, 1, 3, 1]  # W H W W H WH H
    MELODIC_MINOR_INTERVALS = [2, 1, 2, 2, 2, 2, 1]  # W H W W W W H (ascending)

    # Pentatonic scales
    MAJOR_PENTATONIC_INTERVALS = [2, 2, 3, 2, 3]  # W W m3 W m3
    MINOR_PENTATONIC_INTERVALS = [3, 2, 2, 3, 2]  # m3 W W m3 W

    # Blues scale
    BLUES_INTERVALS = [3, 2, 1, 1, 3, 2]  # m3 W H H m3 W

    # Modes (derived from major scale)
    IONIAN_INTERVALS = [2, 2, 1, 2, 2, 2, 1]  # Same as major
    DORIAN_INTERVALS = [2, 1, 2, 2, 2, 1, 2]  # Minor scale with raised 6th
    PHRYGIAN_INTERVALS = [1, 2, 2, 2, 1, 2, 2]  # Minor scale with lowered 2nd
    LYDIAN_INTERVALS = [2, 2, 2, 1, 2, 2, 1]  # Major scale with raised 4th
    MIXOLYDIAN_INTERVALS = [2, 2, 1, 2, 2, 1, 2]  # Major scale with lowered 7th
    AEOLIAN_INTERVALS = [2, 1, 2, 2, 1, 2, 2]  # Same as natural minor
    LOCRIAN_INTERVALS = [1, 2, 2, 1, 2, 2, 2]  # Minor scale with lowered 2nd and 5th

    # Other scales
    WHOLE_TONE_INTERVALS = [2, 2, 2, 2, 2, 2]  # All whole steps
    CHROMATIC_INTERVALS = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # All half steps

    # ===== Basic Scales =====

    @staticmethod
    def major(root):
        """Generate a major scale from the given root note."""
        return Scale._generate_scale(root, Scale.MAJOR_INTERVALS)

    @staticmethod
    def minor(root):
        """Generate a natural minor scale from the given root note."""
        return Scale._generate_scale(root, Scale.MINOR_INTERVALS)

    @staticmethod
    def harmonic_minor(root):
        """Generate a harmonic minor scale from the given root note."""
        return Scale._generate_scale(root, Scale.HARMONIC_MINOR_INTERVALS)

    @staticmethod
    def melodic_minor(root):
        """Generate a melodic minor scale (ascending) from the given root note."""
        return Scale._generate_scale(root, Scale.MELODIC_MINOR_INTERVALS)

    # ===== Pentatonic Scales =====

    @staticmethod
    def major_pentatonic(root):
        """Generate a major pentatonic scale from the given root note."""
        return Scale._generate_scale(root, Scale.MAJOR_PENTATONIC_INTERVALS)

    @staticmethod
    def minor_pentatonic(root):
        """Generate a minor pentatonic scale from the given root note."""
        return Scale._generate_scale(root, Scale.MINOR_PENTATONIC_INTERVALS)

    # ===== Blues Scale =====

    @staticmethod
    def blues(root):
        """Generate a blues scale from the given root note."""
        return Scale._generate_scale(root, Scale.BLUES_INTERVALS)

    # ===== Modes =====

    @staticmethod
    def ionian(root):
        """Generate an Ionian mode (same as major) from the given root note."""
        return Scale._generate_scale(root, Scale.IONIAN_INTERVALS)

    @staticmethod
    def dorian(root):
        """Generate a Dorian mode from the given root note."""
        return Scale._generate_scale(root, Scale.DORIAN_INTERVALS)

    @staticmethod
    def phrygian(root):
        """Generate a Phrygian mode from the given root note."""
        return Scale._generate_scale(root, Scale.PHRYGIAN_INTERVALS)

    @staticmethod
    def lydian(root):
        """Generate a Lydian mode from the given root note."""
        return Scale._generate_scale(root, Scale.LYDIAN_INTERVALS)

    @staticmethod
    def mixolydian(root):
        """Generate a Mixolydian mode from the given root note."""
        return Scale._generate_scale(root, Scale.MIXOLYDIAN_INTERVALS)

    @staticmethod
    def aeolian(root):
        """Generate an Aeolian mode (same as natural minor) from the given root note."""
        return Scale._generate_scale(root, Scale.AEOLIAN_INTERVALS)

    @staticmethod
    def locrian(root):
        """Generate a Locrian mode from the given root note."""
        return Scale._generate_scale(root, Scale.LOCRIAN_INTERVALS)

    # ===== Other Scales =====

    @staticmethod
    def whole_tone(root):
        """Generate a whole tone scale from the given root note."""
        return Scale._generate_scale(root, Scale.WHOLE_TONE_INTERVALS)

    @staticmethod
    def chromatic(root):
        """Generate a chromatic scale from the given root note."""
        return Scale._generate_scale(root, Scale.CHROMATIC_INTERVALS)

    # ===== Helper Method =====

    @staticmethod
    def _generate_scale(root, intervals):
        """
        Generate a scale from a root note and interval pattern.

        Args:
            root: MIDI note number (0-127)
            intervals: List of semitone intervals

        Returns:
            List of MIDI note numbers representing the scale
        """
        if not isinstance(root, int) or root < 0 or root > 127:
            raise ValueError("Root must be an integer between 0 and 127 inclusive")
        scale = [root]
        for interval in intervals:
            next_note = scale[-1] + interval
            if next_note > 127:
                break  # Stop if we exceed MIDI range
            scale.append(next_note)
        return scale
