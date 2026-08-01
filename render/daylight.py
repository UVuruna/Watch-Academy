"""Day, night and twilight geometry — the lit arcs of the dial.

The sunlit regions for a day (including the polar regimes), the border
clips between them, the aurora hue bands over the lit part and the umbra
brightness ladder. The moon's transit opacity lives here too: it is a
function of where the moon stands against the lit day.
"""

import math

from config import dial, palette
from core import angles
from core.sun import DaylightRegime, SunDay
from render.skin_geometry import daylight_active
from skins.manifest import SkinDefinition

def moon_transit_opacity(spec, year_angle: float, moon_angle: float) -> float:
    """Opacity of the Moon marker while the Earth is also shown: when the
    smaller Moon meets the Earth on the shared rim (their discs would
    overlap) it passes OVER the Earth at reduced opacity — an eclipse-like
    transit where both stay visible (owner decision). The caller skips
    this when the Earth element is switched off."""
    delta = abs(year_angle - moon_angle) % 360.0
    delta = min(delta, 360.0 - delta)
    # Angular size at which the two discs touch on the shared orbit.
    touch_deg = math.degrees((spec.scale + spec.moon_scale) / spec.orbit_fraction)
    return 1.0 if delta >= touch_deg else dial.MOON_TRANSIT_OPACITY


def umbra_ladder(shades: int, contrast: str) -> tuple[int, ...]:
    """Shade values, lightest first (owner spec): full contrast runs
    endpoint-inclusive over the whole range (16 shades -> 255..0 step
    17); half contrast takes the CENTERS of N equal bins of the middle
    half [64, 192] (16 -> 188..68 step 8, symmetric about 128)."""
    lightest, darkest = dial.UMBRA_CONTRAST_SPANS[contrast]
    if contrast == "full":
        return tuple(
            round(lightest - k * (lightest - darkest) / (shades - 1))
            for k in range(shades)
        )
    width = lightest - darkest
    return tuple(
        round(lightest - (k + 0.5) * width / shades) for k in range(shades)
    )


def lit_regions(sun: SunDay, spec) -> list[tuple[float, float, float]]:
    """(start, end_unwrapped, hue_alpha) arcs of the SUNLIT part of the day
    in wall-clock dial space — full alpha between sunrise and sunset, the
    twilight alpha over the dawn/dusk bands, nothing at night (the fixed
    gray base shows through). On transitional high-latitude days a
    boundary can be missing even in NORMAL/WHITE_NIGHTS regimes — each
    missing boundary coalesces to its neighbor (the band collapses to zero
    width and is dropped) instead of crashing mid-paint."""

    def arc(a: float, b: float, alpha: float) -> tuple[float, float, float]:
        return (a, b if b > a else b + 360.0, alpha)

    angle = angles.time_to_dial_angle
    regime = sun.regime
    if regime is DaylightRegime.NORMAL:
        rise = angle(sun.sunrise) if sun.sunrise else angle(sun.dawn)
        sets = angle(sun.sunset) if sun.sunset else angle(sun.dusk)
        dawn = angle(sun.dawn) if sun.dawn else rise
        dusk = angle(sun.dusk) if sun.dusk else sets
        regions = [
            arc(dawn, rise, spec.twilight_alpha),
            arc(rise, sets, spec.day_alpha),
            arc(sets, dusk, spec.twilight_alpha),
        ]
        return [region for region in regions if region[0] != region[1]]
    if regime is DaylightRegime.WHITE_NIGHTS:
        if sun.sunrise is None or sun.sunset is None:
            # One-sided transition into/out of polar day: the sun is up
            # nearly the whole day.
            return [(0.0, 360.0, spec.day_alpha)]
        return [
            arc(angle(sun.sunrise), angle(sun.sunset), spec.day_alpha),
            arc(angle(sun.sunset), angle(sun.sunrise), spec.twilight_alpha),
        ]
    if regime is DaylightRegime.TWILIGHT_ONLY:
        if sun.dawn is not None and sun.dusk is not None:
            return [arc(angle(sun.dawn), angle(sun.dusk), spec.twilight_alpha)]
        return [(0.0, 360.0, spec.twilight_alpha)]
    if regime is DaylightRegime.POLAR_DAY:
        return [(0.0, 360.0, spec.day_alpha)]
    return []                                            # POLAR_NIGHT


def border_clips(
    skin: SkinDefinition, sun: SunDay
) -> tuple[tuple[float, float] | None, ...]:
    """Where the drawn wheel's OUTLINE strokes are allowed (owner option
    2026-07-29, `Settings.hide_night_borders`): `(None,)` — the whole
    circle, no clip — is the standing law, and stays the answer whenever
    the daylight law itself is off (the Calendar's and the Rose's
    switch: with the wheel in flat full color EVERYTHING counts as lit).
    With the option on, the SUNLIT arcs alone: the night keeps its fills
    exactly as before but loses the border mesh — on the Rose, where 24
    overlapping rays each carry a lead line, that mesh is what the
    reader sees at night instead of the wheel. Polar night lights
    nothing, so nothing is stroked."""
    if not skin.hide_night_borders or not daylight_active(skin):
        return (None,)
    return tuple(
        (start, end) for start, end, _alpha in lit_regions(sun, skin.star)
    )


def aurora_bands(
    sun: SunDay, palette: tuple, day_alpha: float
) -> tuple[list[tuple[float, float, str, float]], bool]:
    """The AURORA pointer's color bands (owner spec 2026-07-12): the
    five DAY hues spread EVENLY across the actual sunrise-sunset arc —
    every hue visible on the shortest and the longest day alike — with
    the dawn band in the palette's FIRST hue (left, blue) and the dusk
    band in its LAST (right, brown). The twilight bands have NO
    separate opacity (owner: the dedicated dawn/dusk COLORS carry the
    meaning) — everything follows the daylight alpha. Returns (bands,
    solar_frame): bands are (start, end_unwrapped, hue, alpha) in
    wall-clock dial space; solar_frame=True marks the boundary-less
    regimes (polar day, one-sided white nights, boundary-less
    twilight-only) whose bands run midnight-to-midnight in the SOLAR
    frame — the caller rotates them with the star."""
    dawn_hue, day_hues, dusk_hue = palette[0], palette[1:-1], palette[-1]
    twilight_alpha = day_alpha           # one opacity for the whole arc

    def arc(a: float, b: float) -> tuple[float, float]:
        return a, b if b > a else b + 360.0

    def spread(a: float, b: float, alpha: float) -> list:
        step = (b - a) / len(day_hues)
        return [
            (a + k * step, a + (k + 1) * step, hue, alpha)
            for k, hue in enumerate(day_hues)
        ]

    angle = angles.time_to_dial_angle
    regime = sun.regime
    if regime is DaylightRegime.NORMAL:
        rise = angle(sun.sunrise) if sun.sunrise else angle(sun.dawn)
        sets = angle(sun.sunset) if sun.sunset else angle(sun.dusk)
        dawn = angle(sun.dawn) if sun.dawn else rise
        dusk = angle(sun.dusk) if sun.dusk else sets
        bands = []
        if dawn != rise:
            bands.append((*arc(dawn, rise), dawn_hue, twilight_alpha))
        bands.extend(spread(*arc(rise, sets), day_alpha))
        if sets != dusk:
            bands.append((*arc(sets, dusk), dusk_hue, twilight_alpha))
        return bands, False
    if regime is DaylightRegime.WHITE_NIGHTS:
        if sun.sunrise is None or sun.sunset is None:
            return spread(180.0, 540.0, day_alpha), True
        rise, sets = angle(sun.sunrise), angle(sun.sunset)
        bands = spread(*arc(rise, sets), day_alpha)
        night_a, night_b = arc(sets, rise)
        middle = (night_a + night_b) / 2.0
        # The bright night: dusk brown into the sunset half, dawn blue
        # out of the sunrise half.
        bands.append((night_a, middle, dusk_hue, twilight_alpha))
        bands.append((middle, night_b, dawn_hue, twilight_alpha))
        return bands, False
    if regime is DaylightRegime.TWILIGHT_ONLY:
        if sun.dawn is not None and sun.dusk is not None:
            return (
                spread(*arc(angle(sun.dawn), angle(sun.dusk)), twilight_alpha),
                False,
            )
        return spread(180.0, 540.0, twilight_alpha), True
    if regime is DaylightRegime.POLAR_DAY:
        return spread(180.0, 540.0, day_alpha), True
    return [], False                                     # POLAR_NIGHT
