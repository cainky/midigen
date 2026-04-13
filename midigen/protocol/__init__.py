"""MIDI protocol layer — depends on theory/, TYPE_CHECKING only for composition/."""

from midigen.protocol.track import Track, MAX_MIDI_TICKS
from midigen.protocol.channel_pool import ChannelPool, ChannelExhaustedError
from midigen.protocol.instruments import INSTRUMENT_MAP
