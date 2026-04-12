"""
MIDI Channel Pool Manager.

MIDI has 16 channels (0-15). Channel 9 is reserved for percussion
per General MIDI specification. This module manages channel allocation
to prevent channel overflow and ensure correct drum channel usage.
"""

from typing import Set, Dict, Optional


class ChannelExhaustedError(Exception):
    """Raised when no MIDI channels are available for allocation."""
    pass


class ChannelPool:
    """
    Manages MIDI channel allocation for instruments.

    MIDI has 16 channels (0-15). Channel 9 is reserved for percussion
    per General MIDI specification. This pool manages melodic channel
    allocation and provides the drum channel separately.

    Example:
        >>> pool = ChannelPool()
        >>> piano_ch = pool.allocate("Piano")  # Returns 0
        >>> bass_ch = pool.allocate("Bass")    # Returns 1
        >>> drums_ch = pool.allocate_drums()   # Returns 9
        >>> pool.release("Piano")              # Channel 0 available again
    """

    DRUM_CHANNEL = 9
    MAX_CHANNELS = 16
    MELODIC_CHANNELS = set(range(MAX_CHANNELS)) - {DRUM_CHANNEL}

    def __init__(self):
        """Initialize the channel pool with all melodic channels available."""
        self._available: Set[int] = self.MELODIC_CHANNELS.copy()
        self._allocated: Dict[str, int] = {}  # instrument_name -> channel
        self._drums_allocated: bool = False

    def allocate(self, instrument_name: str) -> int:
        """
        Allocate a channel for an instrument.

        If the instrument has already been allocated a channel, returns
        the same channel (idempotent).

        Args:
            instrument_name: Unique name/identifier for the instrument.

        Returns:
            Channel number (0-15, excluding 9).

        Raises:
            ChannelExhaustedError: If all 15 melodic channels are in use.

        Example:
            >>> pool = ChannelPool()
            >>> pool.allocate("Acoustic Grand Piano")
            0
            >>> pool.allocate("Electric Bass")
            1
        """
        # Return existing allocation if instrument already has a channel
        if instrument_name in self._allocated:
            return self._allocated[instrument_name]

        if not self._available:
            raise ChannelExhaustedError(
                f"All {len(self.MELODIC_CHANNELS)} melodic channels exhausted. "
                f"MIDI supports max 15 melodic instruments + 1 drum channel. "
                f"Currently allocated: {list(self._allocated.keys())}"
            )

        # Prefer lower channels for predictability
        channel = min(self._available)
        self._available.remove(channel)
        self._allocated[instrument_name] = channel
        return channel

    def allocate_drums(self) -> int:
        """
        Return the drum channel (always 9).

        The drum channel is separate from the melodic pool and can be
        allocated independently.

        Returns:
            The drum channel (9).

        Example:
            >>> pool = ChannelPool()
            >>> pool.allocate_drums()
            9
        """
        self._drums_allocated = True
        return self.DRUM_CHANNEL

    def release(self, instrument_name: str) -> None:
        """
        Release a channel back to the pool.

        Args:
            instrument_name: The instrument to release.

        Note:
            Releasing an unallocated instrument is a no-op.
        """
        if instrument_name in self._allocated:
            channel = self._allocated.pop(instrument_name)
            self._available.add(channel)

    def release_drums(self) -> None:
        """Release the drum channel."""
        self._drums_allocated = False

    def get_channel(self, instrument_name: str) -> Optional[int]:
        """
        Get the channel allocated to an instrument without allocating.

        Args:
            instrument_name: The instrument to look up.

        Returns:
            The channel number, or None if not allocated.
        """
        return self._allocated.get(instrument_name)

    def is_allocated(self, instrument_name: str) -> bool:
        """Check if an instrument has been allocated a channel."""
        return instrument_name in self._allocated

    def is_drums_allocated(self) -> bool:
        """Check if the drum channel has been allocated."""
        return self._drums_allocated

    @property
    def available_count(self) -> int:
        """Number of melodic channels still available."""
        return len(self._available)

    @property
    def allocated_count(self) -> int:
        """Number of melodic channels currently allocated."""
        return len(self._allocated)

    @property
    def allocated_instruments(self) -> Dict[str, int]:
        """Copy of the instrument -> channel mapping."""
        return self._allocated.copy()

    def reset(self) -> None:
        """Reset the pool to initial state (all channels available)."""
        self._available = self.MELODIC_CHANNELS.copy()
        self._allocated.clear()
        self._drums_allocated = False

    def __repr__(self) -> str:
        return (
            f"ChannelPool(available={self.available_count}, "
            f"allocated={self.allocated_count}, "
            f"drums={'allocated' if self._drums_allocated else 'free'})"
        )
