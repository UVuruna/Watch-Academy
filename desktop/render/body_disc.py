"""THE DISC IS THE MEASURE, THE SHINE IS EXTRA (owner order 2026-08-16).

A weekday plate is stamped to `slot_layout.weekday_body_size`, which
sizes the WHOLE PICTURE. For an ordinary body the two are the same thing
— it fills its frame — but the eclipsed Sun is a small black disc inside
a wide corona, so it drew a body two thirds the size of the Moon beside
it. The disc takes the roundel's dimensions; the corona goes over the
top and may reach across the neighbouring sectors and the hands.

Layer: render. Documentation: __about/body_disc.md.
"""

from functools import lru_cache
from pathlib import Path

import math

from PySide6.QtGui import QImage

from config import dial, paths


# How finely the disc is probed. The rings are what separate a solid
# body from a ring of rays, so they are dense; the radii only need to
# resolve the answer to about a percent of the half-size.
_RINGS = 80
_SAMPLES = 72
# A ring counts as SOLID at this coverage — not 1.0, because an
# antialiased limb and a stray transparent pixel are not a hole.
_SOLID_COVERAGE = 0.98
_OPAQUE = 128


@lru_cache(maxsize=256)
def filled_disc_fraction(asset: Path) -> float:
    """The largest solid disc of opaque pixels in this plate, as a
    fraction of its half-size — the boundary between BODY and SHINE.

    Sampled ring by ring outward from the centre: a ring that is still
    (almost) entirely opaque is body, and the first one that has broken
    into sparse rays ends the disc. No per-file constant to maintain by
    hand, and no assumption that the subject is centred on a square.

    Cached per resolved path for the process lifetime — a plate's
    geometry cannot change while the program runs (THE ONE COPY RULE's
    own pattern). A plate that will not decode answers the REFERENCE
    fill, which makes every correction built on this a no-op rather than
    a guess."""
    image = QImage(str(paths.art_file(asset)))
    if image.isNull():
        return dial.BODY_DISC_REFERENCE_FILL
    width, height = image.width(), image.height()
    if width < 2 or height < 2:
        return dial.BODY_DISC_REFERENCE_FILL
    half = min(width, height) / 2
    cx, cy = width / 2, height / 2
    best = 0.0
    for ring in range(1, _RINGS + 1):
        radius = ring / _RINGS * half
        opaque = 0
        for step in range(_SAMPLES):
            theta = 2 * math.pi * step / _SAMPLES
            x = int(cx + radius * math.cos(theta))
            y = int(cy + radius * math.sin(theta))
            if 0 <= x < width and 0 <= y < height:
                if image.pixelColor(x, y).alpha() > _OPAQUE:
                    opaque += 1
        if opaque / _SAMPLES < _SOLID_COVERAGE:
            break
        best = radius / half
    return best


def disc_match_scale(asset: Path) -> float:
    """How much larger this plate is stamped so its DISC lands at the
    roundel's diameter — 1.0 for every plate the owner has not listed.

    The list (`dial.BODY_DISC_MATCH_PREFIXES`, stem prefixes) is the
    point: an ordinary body already fills its frame, so matching them all
    would resize the whole instrument to fix one plate, and a planet SIGN
    — a thin glyph in a wide frame — would blow up fourfold. Clamped at
    `dial.BODY_DISC_MATCH_MAX`, and never SHRINKS a plate: a body drawn
    smaller than its frame is the defect being corrected, never a target.
    """
    if not asset.stem.startswith(dial.BODY_DISC_MATCH_PREFIXES):
        return 1.0
    filled = filled_disc_fraction(asset)
    if filled <= 0.0:
        return 1.0
    scale = dial.BODY_DISC_REFERENCE_FILL / filled
    return min(max(scale, 1.0), dial.BODY_DISC_MATCH_MAX)
