"""Year-marker angle: piecewise-linear between real season instants.

Anchored so the summer solstice sits exactly at the dial top (0 deg) and
the winter solstice at the bottom (180 deg), with the equinoxes exactly
at 90/270 deg. Plain linear interpolation over the whole tropical year
is NOT equivalent — it puts the autumn equinox at ~92.3 deg, a visible
error; the golden tests reject it.
"""

import bisect
from dataclasses import dataclass
from datetime import datetime

from config import constants


@dataclass(frozen=True)
class YearAnchors:
    """Six season instants bracketing one calendar year, paired with their
    unwrapped dial angles (config.constants.YEAR_ANCHOR_ANGLES).

    instants[0] is the December solstice BEFORE the year, instants[5] the
    spring equinox AFTER it — any timestamp inside the calendar year falls
    between two anchors without stitching neighbor years.
    """

    year: int
    instants: tuple[datetime, ...]   # strictly increasing, tz-aware UTC
    angles: tuple[float, ...] = constants.YEAR_ANCHOR_ANGLES


def year_marker_angle(now: datetime, anchors: YearAnchors) -> float:
    """Dial angle of the year marker (degrees, clockwise, 0 = top).

    Raises ValueError when `now` is outside the anchor span — that means
    the anchors were built for the wrong year and must be visible, not
    interpolated blindly.
    """
    instants = anchors.instants
    if not instants[0] <= now <= instants[-1]:
        raise ValueError(
            f"{now.isoformat()} is outside the anchor span of year "
            f"{anchors.year} ({instants[0].isoformat()} .. {instants[-1].isoformat()})"
        )
    hi = bisect.bisect_right(instants, now)
    if hi == len(instants):  # now == last anchor exactly
        return anchors.angles[-1] % 360.0
    lo = hi - 1
    t0, t1 = instants[lo], instants[hi]
    a0, a1 = anchors.angles[lo], anchors.angles[hi]
    fraction = (now - t0) / (t1 - t0)
    return (a0 + fraction * (a1 - a0)) % 360.0
