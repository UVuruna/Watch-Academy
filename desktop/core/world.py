"""THE TWO WORLD-MODES — which of the two turns, and by how much.

The whole of [the ring rework ledger](../research/ring_rework.md) §1 that
can be written as a number. NOON_UP is the dial every release before
this one drew: the observer stands still and the sun travels, so the
STAR rotates toward true solar noon and the hour band never moves.
SKY_UP stands the star still and turns the WORLD beneath it, and
turns it over again at night — so the source of light, the Sun by day and
the Moon by night, is always overhead.

THE NAMES WERE SWAPPED UNTIL 2026-08-13 (owner verdict, option B). These
two modes used to be called `geocentric` and `heliocentric`, and each
carried the OTHER's meaning: the mode that keeps the light source
overhead is the GEOCENTRIC experience — the observer stands still and the
heavens wheel around him — while the mode that keeps noon overhead, with
the sun as the fixed reference, is the HELIOCENTRIC frame. The keys now
name the BEHAVIOUR, so the code cannot be read backwards again, and the
astronomical term rides in the label (`dial.WORLD_MODE_LABELS`) where it
is finally the right way round. A settings file written before that day
is translated by `app.settings_fields.load_world_mode`, never reset.

Two numbers come out of here and the render layer places every rotating
element with one of them:

    pointer_rotation_deg   the star/pointer, its arms and diamond seats,
                           the umbra, the aura's own wedges
    world_offset_deg       the outer numeral band, the ring jewels, the
                           crown text, the daylight arcs, the eclipse
                           body at its hour, the Moon Horizon Band and
                           its eclipse segment, the hour hand, every
                           hover hit zone that reads the dial band

THE HOUR FRAME RULE (owner order 2026-08-13) decides that list, and it
is a rule about UNITS, never about where on the dial a thing is drawn:
what shows something happening in HOURS belongs to the outer circle's
frame and takes the offset; what shows a position in the CALENDAR does
not. The inner minute band, the year wheel and the moon cycle are the
exempt three (`render.layers.year_marker.earth_marker_angle`). The
Moon Horizon Band is the case that proved the rule needed writing
down: it is painted at the INNER circle's radius for a purely
geometric reason and an earlier round read that as membership, so a
turned face showed the Moon's up-hours on the wrong seats.

They cannot drift apart: NOON_UP pins the world offset at exactly 0
and leaves the pointer rotation bit-for-bit what it always was, while
SKY_UP gives the world `-star_rotation` and the pointer nothing —
the two cancel, so true solar noon stands under the pointer's own top
arm in both modes.

THE PHASE IS THE SUN'S ACTUAL STATE, never a count of "two flips a day":
above the horizon = DAYLIGHT, below = NIGHT. The caller reads that fact
off `core.clock_state.TickState.is_daylight`, so an ordinary day has two
genuine transitions and polar day / polar night have ZERO for months —
Tromsø stands in its phase and nothing fires.

No Qt, no wall clock (`tests/test_purity.py` enforces both): the moment
arrives as `elapsed_s`.
"""

import math

from config import dial
from core.numerals import fold_angle


def night_phase_deg(is_daylight: bool) -> float:
    """The PHASE part of every offset below: nothing by day, half a
    circle by night (ledger §1 — "NIGHT: everything moved 180 deg, 0h on
    top, noon at the bottom")."""
    return 0.0 if is_daylight else dial.WORLD_NIGHT_PHASE_DEG


def solar_part_deg(star_rotation: float, solar_rotation: bool) -> float:
    """The SOLAR part: `-star_rotation` while the Solar Rotation switch
    is on, 0 while it is off.

    The MINUS is the entire sign derivation, and it is forced by the
    existing convention rather than chosen: `core.angles.star_rotation_deg`
    answers the dial ANGLE AT WHICH true solar noon stands (positive =
    clockwise = solar noon later than 12:00 — a city west in its zone, or
    DST). A band that must bring that angle to the top therefore turns by
    the NEGATIVE of it. Belgrade's own golden pair proves it: the star at
    +10.76 deg puts the hour-12 numeral (seat 0) at -10.76 deg, and the
    star at -4.17 deg puts it at +4.17 deg."""
    return -float(star_rotation) if solar_rotation else 0.0


def _check_mode(mode: str) -> None:
    if mode not in dial.WORLD_MODES:
        raise ValueError(f"unknown world mode {mode!r}")


def world_offset_deg(
    mode: str, star_rotation: float, solar_rotation: bool, phase_deg: float,
) -> float:
    """How far the WORLD has turned under the pointer.

    Exactly 0 in NOON_UP — the mode is a no-op there by construction,
    not by a chain of conditionals scattered through the render layer.
    In SKY_UP it is the solar part plus the phase, so with Solar
    Rotation ON and the sun up the numeral of true solar noon stands at
    the dial top, and at night the numeral of true solar MIDNIGHT stands
    there instead (the same formula, once the phase is added)."""
    _check_mode(mode)
    if mode == "noon_up":
        return 0.0
    return (
        solar_part_deg(star_rotation, solar_rotation) + float(phase_deg)
    ) % 360.0


def pointer_rotation_deg(
    mode: str, star_rotation: float, solar_rotation: bool, phase_deg: float,
) -> float:
    """How far the POINTER has turned — the star, its arms, the seats
    riding them, the umbra's brightness wheel.

    NOON_UP is today's answer untouched: the solar offset, or 0 with
    the switch off. SKY_UP gives it the PHASE alone — the star
    stands upright and never tilts toward noon again, because the world
    already carried noon under it. At night it takes the same half-turn
    everything else takes, which is what re-seats the weekday bodies
    while the (symmetric) star itself still reads upright."""
    _check_mode(mode)
    if mode == "noon_up":
        return float(star_rotation) if solar_rotation else 0.0
    return float(phase_deg) % 360.0


# --- THE ARC READING LAW ----------------------------------------------------------
# Ledger §1: "Every member re-seats READABLY at its new position, with
# its new angle and its new arc — NOTHING IS MIRRORED."
#
# A single glyph obeys that from `core.angles.readable_rotation_deg`
# alone. A WORD does not. A text arc reads left to right only because
# dial-x is monotonic in OPPOSITE senses across the two halves of the
# circle (`core.crown_text`): increasing theta moves screen-x left to
# right over the TOP and right to left under the BOTTOM, so a top arc is
# laid out clockwise and a bottom arc counter-clockwise. Move a top arc
# to the bottom by adding the offset alone and every letter stands
# upright while the WORD reads backwards — observed on the real dial,
# 2026-08-06: DOMY's ANGER came up as "REGNA" in the night phase.
#
# The cure is one reflection: when the offset carries an arc across the
# horizon, its glyphs are mirrored about the arc's OWN new centre, which
# reverses the run's direction without moving the arc itself. Being a
# plain affine map on angles, it applies unchanged to a WORD's hover
# centre, so the hit zones follow the jewels exactly.


def arc_centre_deg(angles) -> float:
    """The circular mean of a text arc's glyph seats — the axis the
    reflection below turns about. Circular, not arithmetic: an arc
    straddling 0 deg (every TOP arc does) would otherwise average to the
    bottom of the dial."""
    seats = tuple(angles)
    if not seats:
        raise ValueError("an arc needs at least one glyph to have a centre")
    x = sum(math.cos(math.radians(seat)) for seat in seats)
    y = sum(math.sin(math.radians(seat)) for seat in seats)
    return math.degrees(math.atan2(y, x)) % 360.0


def arc_crosses_horizon(centre: float, offset_deg: float) -> bool:
    """True when moving an arc centred at `centre` by `offset_deg`
    carries it between the dial's upper and lower half — the only case
    that needs the reflection."""
    return (abs(fold_angle(centre)) > 90.0) != (
        abs(fold_angle(centre + offset_deg)) > 90.0
    )


def arc_seat_deg(theta: float, centre: float, offset_deg: float) -> float:
    """One glyph (or one word's hover centre) of a text arc, moved by
    the world offset — and MIRRORED about the arc's own new centre when
    the move crossed the horizon, so the word still reads left to right
    at its new seat."""
    if arc_crosses_horizon(centre, offset_deg):
        return (2.0 * centre + offset_deg - theta) % 360.0
    return (theta + offset_deg) % 360.0


def arc_seats(angles, offset_deg: float) -> tuple[float, ...]:
    """A whole arc's glyph seats after the world offset, reading order
    preserved — the centre is the run's own (`arc_centre_deg`), so every
    glyph of one arc is mapped by the SAME reflection."""
    seats = tuple(angles)
    if not seats:
        return ()
    centre = arc_centre_deg(seats)
    return tuple(arc_seat_deg(seat, centre, offset_deg) for seat in seats)


def flip_eased(progress: float) -> float:
    """The smoothstep the turning move runs on — exactly 0 and exactly 1
    at the ends, symmetric, no overshoot (an overshooting curve would
    turn the dial PAST its target and back, which on a 180 deg flip
    reads as a stumble)."""
    p = min(1.0, max(0.0, float(progress)))
    return p * p * (3.0 - 2.0 * p)


def flip_phase_deg(
    start_deg: float, target_deg: float, elapsed_s: float,
    duration_s: float | None = None,
) -> float:
    """The phase `elapsed_s` into a flip from `start_deg` to
    `target_deg`.

    `target_deg` exactly once the duration is reached — and IMMEDIATELY
    for a zero or negative duration, which is the SNAP a clock
    correction takes (owner bug 2026-08-06: a WM_TIMECHANGE is not a
    sunset, so it must never animate)."""
    duration = (
        dial.WORLD_FLIP_DURATION_S if duration_s is None else float(duration_s)
    )
    if duration <= 0.0 or elapsed_s >= duration:
        return float(target_deg)
    if elapsed_s <= 0.0:
        return float(start_deg)
    return float(start_deg) + (
        float(target_deg) - float(start_deg)
    ) * flip_eased(elapsed_s / duration)
