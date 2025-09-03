from typing import List, Tuple

class Rhythm:
    def __init__(self, pattern: str, beat_duration: int = 120):
        """
        Initializes a Rhythm object.

        :param pattern: A string representing the rhythm, e.g., 'x.x.x.x.'.
                        'x' represents a note-on event, '.' represents a rest.
        :param beat_duration: The duration of a single character in the pattern in MIDI ticks.
                              Defaults to 120 (a 16th note if ticks_per_beat is 480).
        """
        self.pattern = pattern
        self.beat_duration = beat_duration

    def get_events(self) -> List[Tuple[bool, int]]:
        """
        Parses the rhythm pattern and returns a list of events.

        :return: A list of tuples, where each tuple is (is_note_on, duration).
                 `is_note_on` is True for a note and False for a rest.
                 `duration` is the duration of the event in MIDI ticks.
        """
        events = []
        if not self.pattern:
            return events

        current_event_is_on = (self.pattern[0] == 'x')
        current_duration = 0

        for char in self.pattern:
            is_on = (char == 'x')
            if is_on == current_event_is_on:
                current_duration += self.beat_duration
            else:
                events.append((current_event_is_on, current_duration))
                current_event_is_on = is_on
                current_duration = self.beat_duration

        events.append((current_event_is_on, current_duration))

        return events

    @property
    def total_duration(self) -> int:
        """
        Calculates the total duration of the rhythm pattern.
        """
        return len(self.pattern) * self.beat_duration

RHYTHM_LIBRARY = {
    "four_on_the_floor": "x...x...x...x...",
    "son_clave": "x..x..x.x..x..x.",
    "tresillo": "x.xx.xx.",
    "eighth_notes": "x.x.x.x.x.x.x.x.",
    "quarter_notes": "x...x...x...x...",
}
