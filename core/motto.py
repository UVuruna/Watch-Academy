"""The outer Great Seal motto arc — pure per-glyph angle math.

TASK 1 (owner "može radi" 2026-07-19, CANON.md §The Banknote): while
the MASON G ring preset is active, the two Great Seal mottos render as
curved text OUTSIDE the ring band, laid out so specific KEY LETTERS
land exactly on the ring's own six hexagram seats — MASON outside, G
inside, the dollar-bill mechanic on our dial. Given a motto string and
its PINNED letter -> ring-position constraints, `motto_glyph_angles`
solves every character's dial angle: pinned characters land exactly on
their seat, and the run of characters between two consecutive pins is
spaced EVENLY across the angular gap between them (owner spec: "even
letter spacing between the pinned letters"). Pure math — no Qt, no
wall clock (core purity, tests/test_purity.py); render.layers.RingLayer
draws the result, data.rings.validate_preset calls this at LOAD time so
a broken pin config (a typo'd occurrence, an out-of-order pin) fails
loudly there, never mid-paint.
"""

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


def motto_glyph_angles(
    text: str, pins: tuple[tuple[str, int, int], ...]
) -> tuple[float, ...]:
    """One dial angle (degrees, clockwise from the top, UNWRAPPED so the
    sweep direction stays obvious — may exceed 360) per CHARACTER of
    `text`, spaces included (a space still consumes one evenly-spaced
    slot, so word gaps read naturally; the caller skips drawing them).

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

    Consecutive pins must read CLOCKWISE (owner spec: "both mottos read
    continuously clockwise") — each pin's angle is unwrapped (+360 as
    many times as needed) to exceed the previous one, then every
    character strictly between two pins is the EVEN linear
    interpolation of the two pinned angles."""
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
    angles = [0.0] * len(text)
    prev_index, prev_angle = resolved[0][0], ring_position_angle(resolved[0][1])
    angles[prev_index] = prev_angle
    for index, position in resolved[1:]:
        angle = ring_position_angle(position)
        while angle <= prev_angle:
            angle += 360.0
        step = (angle - prev_angle) / (index - prev_index)
        for k in range(prev_index + 1, index + 1):
            angles[k] = prev_angle + step * (k - prev_index)
        prev_index, prev_angle = index, angle
    return tuple(angles)
