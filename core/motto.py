"""The outer Great Seal motto arc — pure per-glyph angle math.

TASK 1 (owner "može radi" 2026-07-19, CANON.md §The Banknote): while
the Mason ring preset is active (renamed from "MASON G", TASK 2,
MASON/ICONS round), the two Great Seal mottos render as curved text
OUTSIDE the ring band, laid out so specific KEY LETTERS land exactly on
the ring's own six hexagram seats — MASON outside, G inside, the
dollar-bill mechanic on our dial. Given a motto string and
its PINNED letter -> ring-position constraints, `motto_glyph_angles`
solves every character's dial angle: pinned characters land exactly on
their seat, and the run of characters between two consecutive pins is
spaced EVENLY across the angular gap between them (owner spec: "even
letter spacing between the pinned letters"). Pure math — no Qt, no
wall clock (core purity, tests/test_purity.py); render.layers.RingLayer
draws the result, data.rings.validate_preset calls this at LOAD time so
a broken pin config (a typo'd occurrence, an out-of-order pin) fails
loudly there, never mid-paint.

MOTO-FIX round (owner correction 2026-07-19, the dollar's Great Seal
reference image — the first layout was "katastrofa", both mottos
sweeping the SAME overlapping top-heavy arc at two radii): the two
mottos now sit on DISJOINT arcs, exactly like the real seal — ANNUIT
COEPTIS over the TOP (8h -> 16h through noon), NOVUS ORDO SECLORUM
under the BOTTOM (4h -> 20h through the bottom/24h) — sharing ONE
radius. The new `clockwise` parameter picks the arc: the top arc reads
increasing angle, the bottom arc DEcreasing (`clockwise=False`) — both
read left-to-right to a viewer despite the opposite angle direction,
since dial-x is monotonic in opposite senses across the top and bottom
halves (see the function's own docstring). No separate orientation
flag is needed for the GLYPH rotation itself —
`core.angles.readable_rotation_deg` already derives tops-outward (top
half) or tops-inward (bottom half) purely from the angle, unchanged by
this round.

ANNUIT WORD-GAP round (owner correction 2026-07-19, third batch — "the
letters should sit TIGHT... and the leftover slack becomes ONE BIG WORD
GAP"): a motto pinned ONLY at its first and last character (ANNUIT
COEPTIS's own 2 pins, A and S) no longer spreads its 13 character-steps
EVENLY across the whole 120 deg span — that read too wide next to NOVUS
ORDO SECLORUM's own tight look. NOVUS's 3 pins already happen to divide
its two segments into 9 steps of exactly `defaults.
RING_MOTTO_LETTER_STEP_DEG` each (60 deg / 9 chars) — this round makes
that step a named config constant and reuses it explicitly for the
2-pin case: letters advance inward from BOTH pins at that fixed step,
and whatever angular slack remains lands as one big gap at the motto's
own (single) interior space — the eye/G area breathes like the Great
Seal's own gap over the eye. `_tight_two_pin_angles` is the new
2-pin-only code path; NOVUS's 3-pin case is untouched (its own even
per-segment interpolation already produces the tight look by
construction).
"""

from config import defaults
from core.angles import ring_position_angle


def _occurrence_index(text: str, letter: str, occurrence: int) -> int:
    """0-based index of the `occurrence`-th (1-based) appearance of
    `letter` in `text` — e.g. `_occurrence_index("NOVUS ORDO SECLORUM",
    "O", 3)` is the O ENDING "ORDO" (that word's own last letter), not
    NOVUS's own O or SECLORUM's. Raises if `text` does not contain that
    many (Rule #1: a config typo must fail at load, not silently draw a
    letter at the wrong seat)."""
    seen = 0
    for index, char in enumerate(text):
        if char == letter:
            seen += 1
            if seen == occurrence:
                return index
    raise ValueError(
        f"{letter!r} does not appear {occurrence} time(s) in {text!r} "
        f"(found {seen})"
    )


def _tight_two_pin_angles(
    text: str,
    resolved: list[tuple[int, int]],
    clockwise: bool,
) -> tuple[float, ...]:
    """ANNUIT WORD-GAP round (owner correction 2026-07-19, third batch):
    the layout for a motto pinned ONLY at its first and last character —
    "a pinned two-word motto" (ANNUIT COEPTIS today). Every letter
    advances from BOTH pins INWARD at the fixed
    `defaults.RING_MOTTO_LETTER_STEP_DEG` step (the same tight
    per-character spacing NOVUS ORDO SECLORUM's own 3-pin segments
    already produce), instead of spreading the whole span evenly across
    every character (the previous round's "too wide" look). Whatever
    angular slack is left over lands entirely on the motto's own single
    INTERIOR SPACE — centered between its two flanking letters, since a
    space never draws (`RingLayer`'s draw loop skips it) so its own
    angle is otherwise inconsequential. Requires exactly one interior
    space: a "pinned two-word motto" is the only shape this ever draws
    (Rule #7) — a future 2-pin motto of a different shape fails loudly
    here rather than silently drawing pins that never meet the gap."""
    (index_a, position_a), (index_b, position_b) = resolved
    angle_a = ring_position_angle(position_a)
    angle_b = ring_position_angle(position_b)
    step = defaults.RING_MOTTO_LETTER_STEP_DEG
    if clockwise:
        while angle_b <= angle_a:
            angle_b += 360.0
    else:
        while angle_b >= angle_a:
            angle_b -= 360.0
        step = -step
    spaces = [index for index, char in enumerate(text) if char == " "]
    if len(spaces) != 1:
        raise ValueError(
            f"motto {text!r}: the tight two-pin layout needs exactly one "
            f"interior word gap (found {len(spaces)})"
        )
    gap = spaces[0]
    angles = [0.0] * len(text)
    angles[index_a] = angle_a
    for k in range(index_a + 1, gap):
        angles[k] = angle_a + step * (k - index_a)
    angles[index_b] = angle_b
    for k in range(index_b - 1, gap, -1):
        angles[k] = angle_b - step * (index_b - k)
    angles[gap] = (angles[gap - 1] + angles[gap + 1]) / 2.0
    return tuple(angles)


def motto_glyph_angles(
    text: str,
    pins: tuple[tuple[str, int, int], ...],
    clockwise: bool = True,
) -> tuple[float, ...]:
    """One dial angle (degrees, clockwise from the top, UNWRAPPED so the
    sweep direction stays obvious — may exceed 360 or go negative) per
    CHARACTER of `text`, spaces included (a space still consumes one
    evenly-spaced slot, so word gaps read naturally; the caller skips
    drawing them).

    `pins` is `(letter, occurrence, ring_position)` triples — e.g.
    `("N", 1, 4)` pins the first "N" in `text` to the 4h ring seat.
    Order within the tuple does not matter (resolved indices are
    sorted), but the FIRST pin (by resolved index) must land on text's
    own first character and the LAST on its own last character — every
    glyph belongs to some interior segment; no floating, unpinned
    lead/tail. Both Great Seal mottos pin their own first and last
    letter, so this is never a real limitation for today's two mottos;
    a future preset that violates it fails loudly here rather than
    silently drawing a lopsided arc (Rule #7 — no defensive handling for
    a scenario our own data never produces).

    `clockwise` (MOTO-FIX round, owner correction 2026-07-19, the
    dollar's Great Seal reference image) picks which of the two arcs
    this text draws. True (the default) is the TOP-arc reading — each
    next pin's angle is unwrapped (+360 as many times as needed) to
    EXCEED the previous one, so the text sweeps clockwise over the top
    (ANNUIT COEPTIS's own arc, 8h -> 16h through noon). False is the
    BOTTOM-arc reading — each next pin's angle is unwrapped (-360 as
    many times as needed) to stay BELOW the previous one, so the text
    sweeps counterclockwise under the bottom (NOVUS ORDO SECLORUM's own
    arc, 4h -> 20h through the bottom/24h). Both directions read
    left-to-right to a VIEWER (never mirrored) even though the angle
    moves opposite ways, because dial-x (`render.layers.dial_point`'s
    `distance * sin(theta)`) is monotonic in OPPOSITE senses across the
    two halves of the circle: increasing theta moves screen-x
    left-to-right over the top but right-to-left under the bottom, so
    the bottom arc must DEcrease theta to still read left-to-right. The
    per-glyph tangential ROTATION (`core.angles.readable_rotation_deg`)
    needs no matching flag — it already derives tops-outward (top half)
    or tops-inward (bottom half) from the angle alone, so feeding it
    either direction's angles draws every glyph upright automatically.

    With exactly 2 pins (a motto pinned only at its own first and last
    character, e.g. ANNUIT COEPTIS) the ANNUIT WORD-GAP layout applies
    (`_tight_two_pin_angles`, owner correction 2026-07-19, third batch):
    every letter advances at the fixed `defaults.
    RING_MOTTO_LETTER_STEP_DEG` step from BOTH pins inward, and the
    leftover slack becomes one big gap at the motto's own single
    interior space. With 3+ pins (NOVUS ORDO SECLORUM's own 3) every
    character strictly between two consecutive pins is instead the EVEN
    linear interpolation of that segment's own two pinned angles —
    unchanged by this round, since NOVUS's own segments already land on
    the tight step by construction."""
    if len(pins) < 2:
        raise ValueError("motto_glyph_angles needs at least 2 pins to interpolate")
    resolved = sorted(
        (_occurrence_index(text, letter, occurrence), position)
        for letter, occurrence, position in pins
    )
    for (index_a, _), (index_b, _) in zip(resolved, resolved[1:]):
        if index_a == index_b:
            raise ValueError(
                f"motto pins for {text!r} collide at character index {index_a}"
            )
    if resolved[0][0] != 0 or resolved[-1][0] != len(text) - 1:
        raise ValueError(
            f"motto pins for {text!r} must cover index 0 and "
            f"{len(text) - 1} (resolved to {[index for index, _ in resolved]})"
        )
    if len(resolved) == 2:
        return _tight_two_pin_angles(text, resolved, clockwise)
    angles = [0.0] * len(text)
    prev_index, prev_angle = resolved[0][0], ring_position_angle(resolved[0][1])
    angles[prev_index] = prev_angle
    for index, position in resolved[1:]:
        angle = ring_position_angle(position)
        if clockwise:
            while angle <= prev_angle:
                angle += 360.0
        else:
            while angle >= prev_angle:
                angle -= 360.0
        step = (angle - prev_angle) / (index - prev_index)
        for k in range(prev_index + 1, index + 1):
            angles[k] = prev_angle + step * (k - prev_index)
        prev_index, prev_angle = index, angle
    return tuple(angles)
