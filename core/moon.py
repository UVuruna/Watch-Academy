"""Moon phase from bundled principal-phase instants.

Linear interpolation of the cycle fraction between bracketing principal
phases (New=0.0, First Quarter=0.25, Full=0.5, Third Quarter=0.75) is
exact at the anchors and matches astral to ~0.0001 of a cycle in
between — while astral.moon.phase() is day-granular on a 28-scale and
off by up to ~0.3 day near the instants, so it is not used here.
"""

import math
from dataclasses import dataclass
from datetime import datetime

from config import constants


@dataclass(frozen=True)
class MoonWindow:
    """Sorted principal-phase events (tz-aware UTC instant, cycle fraction)
    spanning comfortably around the period of interest."""

    events: tuple[tuple[datetime, float], ...]


def phase_fraction(now: datetime, window: MoonWindow) -> float:
    """Cycle fraction at `now`: 0.0 new, 0.25 first quarter, 0.5 full,
    0.75 third quarter. Waxing below 0.5, waning above.

    Raises ValueError when `now` is outside the window span.
    """
    events = window.events
    if not events[0][0] <= now <= events[-1][0]:
        raise ValueError(
            f"{now.isoformat()} is outside the moon window "
            f"({events[0][0].isoformat()} .. {events[-1][0].isoformat()})"
        )
    for (t0, f0), (t1, _) in zip(events, events[1:]):
        if t0 <= now <= t1:
            elapsed = (now - t0) / (t1 - t0)
            return (f0 + elapsed * constants.MOON_CYCLE_QUARTER) % 1.0
    raise ValueError(f"no bracketing phase events around {now.isoformat()}")


def illumination(fraction: float) -> float:
    """Lit fraction of the moon disc (0.0 new .. 1.0 full) from the cycle
    fraction."""
    return (1.0 - math.cos(2.0 * math.pi * fraction)) / 2.0


def phase_name(fraction: float) -> str:
    """English octant name for a cycle fraction (windows of 1/8 centered
    on the four principal anchors and the four intermediate phases)."""
    octant = int(((fraction % 1.0) + 1.0 / 16.0) * 8.0) % 8
    return constants.MOON_PHASE_NAMES[octant]
