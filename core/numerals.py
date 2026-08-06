"""The dial numerals — pure seating, light and relief mathematics.

Everything [The Dial Numerals](../research/hour_numerals.md) settles that
can be expressed as a number lives here: where a numeral sits, how far it
turns so it still reads, which way its relief is thrown, how many copies
that relief is, which colour role it wears, and which glyphs the live
crown needs in which order. No Qt, no wall clock (`tests/test_purity.py`
enforces both by AST) — `render/numeral_*.py` turns these numbers into
pixels.

Angles are the project's own convention throughout: degrees CLOCKWISE
from the dial top (`core.angles`), folded into (-180, 180] so "the lower
half" is simply `abs(deg) > 90`.

Design note — why the outer band is computed at all: a preset ring of
hour markers would do for a clock whose 12 never moves. DOMY's does. In
the Heliocentric mode the hour band rotates so true solar noon stands at
the top, so a numeral's seat belongs to the ANGLE it lands on, never to
the hour it carries; `hour_angle`'s `offset_deg` is the one parameter
that carries that rotation, and it is threaded through every band key so
a changed offset simply re-renders the band.
"""

import math
from datetime import datetime

from config import dial

# The relief copy's own role — a SHADE copy is the dark side wall, a LIT
# copy is the emboss recipe's bright rim on the opposite side.
SHADE = "shade"
LIT = "lit"


def fold_angle(deg: float) -> float:
    """`deg` folded into (-180, 180] — the one normalization every
    seating and light decision below is written against. -180 folds UP
    to +180 so the bottom of the dial has exactly one name (the seating
    law's `deg mod 90 == 0` branch must fire there, not the lower-half
    one)."""
    folded = ((deg + 180.0) % 360.0) - 180.0
    return 180.0 if folded == -180.0 else folded


def hour_labels() -> tuple[str, ...]:
    """`("0", "1", ... "23")` — bare labels, no leading zero (ledger
    §4)."""
    return tuple(str(hour) for hour in range(dial.NUMERAL_HOUR_COUNT))


def minute_labels() -> tuple[str, ...]:
    """`("0", "5", ... "55")` — the inner band labels every fifth
    minute (ledger §4)."""
    return tuple(
        str(minute)
        for minute in range(0, 60, dial.NUMERAL_MINUTE_LABEL_STEP)
    )


def hour_angle(hour: int, offset_deg: float = 0.0) -> float:
    """Dial angle of hour `hour` on the OUTER band: `(h - 12) * 15`,
    plus the band's own rotation, folded into (-180, 180].

    `offset_deg` is the Heliocentric solar offset plus the night
    inversion (ledger §2/§4). It is 0.0 today — wave 4 plugs the live
    value in — but it is threaded through every band cache key from the
    start, so turning the band on changes no caller's shape."""
    return fold_angle((hour - 12) * dial.NUMERAL_HOUR_STEP_DEG + offset_deg)


def minute_angle(minute: int) -> float:
    """Dial angle of a minute on the INNER band. The inner band NEVER
    rotates, in either mode (ledger §2) — it is a plain clock face and
    its hands read ordinary zone time — so this takes no offset at
    all."""
    return fold_angle(minute * dial.NUMERAL_MINUTE_STEP_DEG)


def seat_rotation(deg: float, seating: str = "arc") -> float:
    """THE SEATING LAW (ledger §4), written exactly as the ledger writes
    it.

    `arc` — a numeral standing on a SQUARE angle (0, 90, 180, 270)
    stands upright; every other numeral takes the angle it sits on, and
    the lower half turns a further 180 deg so nothing ever reads upside
    down. `upright` — 0 everywhere.

    With the ring square-on this stands 12, 18, 0 and 6 up. The moment
    the ring turns, those four ride the arc like everyone else and
    whichever numerals have landed on the square angles stand up in
    their place — which is the whole reason the band is computed rather
    than drawn.

    The returned value is NOT re-folded: `rot(170) == 350` and
    `rot(-170) == 10` are the same physical rotation, and the raw form
    is what the ledger's own table states."""
    if seating == "upright":
        return 0.0
    if seating != "arc":
        raise ValueError(f"unknown numeral seating {seating!r}")
    folded = fold_angle(deg)
    if folded % 90.0 == 0.0:
        return 0.0
    if abs(folded) > 90.0:
        return folded + 180.0
    return folded


def light_offset(
    deg: float,
    depth: float,
    light: str = "radial",
    fixed: tuple[float, float] = (0.0, 0.0),
) -> tuple[float, float]:
    """THE LIGHT LAW (ledger §6) — the relief's throw at seat `deg`,
    with **y counted positive UPWARD**.

    `radial` is one lamp at the centre of the dial, so every numeral
    throws its shadow straight outward:
    `offset(deg) = depth * (sin deg, cos deg)`. The four square angles
    must come out exactly `(0, +d)` at the top, `(+d, 0)` at the right,
    `(0, -d)` at the bottom and `(-d, 0)` at the left — the table the
    settings panel prints live and `tests/test_numerals.py` pins.

    `fixed` is one lamp somewhere off the dial: the typed X/Y offset IS
    the throw, X positive right and Y positive up, and `depth` says
    nothing (for `extrude` the step count then comes from the offset's
    own length — see `relief_offsets`)."""
    if light == "fixed":
        return (float(fixed[0]), float(fixed[1]))
    if light != "radial":
        raise ValueError(f"unknown numeral light {light!r}")
    radians = math.radians(deg)
    return (depth * math.sin(radians), depth * math.cos(radians))


def extrude_step_count(depth: float) -> int:
    """`N = round(depth)` (ledger §5), floored at one copy: an extrude
    of depth 0.4 is still a numeral with a wall, just a very short
    one."""
    return max(1, round(abs(depth)))


def relief_offsets(
    style: str, depth: float, throw: tuple[float, float],
) -> tuple[tuple[float, float, str], ...]:
    """THE RELIEF MODEL (ledger §5) as `(dx, dy, role)` triples in PAGE
    SPACE, y positive up, ordered far-end FIRST so a painter drawing
    them in order lays the wall down from the far end back to the
    numeral.

    ```
    cast     glyph + 1 copy at  depth
    extrude  glyph + N copies at depth/N, 2*depth/N ... depth  (N = round(depth))
    emboss   glyph + 1 dark copy at depth, 1 white copy at -0.6*depth
    ```

    `cast` leaves the gap open, so the numeral reads as a thin plate
    FLOATING above the ring; `extrude` welds its copies into a solid
    side wall, so the numeral becomes a block STANDING on it; `emboss`
    is a dark copy one way and a lit rim the other — pressed metal
    rather than cast metal.

    `throw` is `light_offset`'s output, so in `fixed` light the step
    count comes from the offset's OWN length rather than from `depth`
    (which says nothing in that mode)."""
    dx, dy = throw
    if style == "cast":
        return ((dx, dy, SHADE),)
    if style == "emboss":
        lit = dial.NUMERAL_EMBOSS_LIT_FACTOR
        return ((dx, dy, SHADE), (lit * dx, lit * dy, LIT))
    if style != "extrude":
        raise ValueError(f"unknown numeral relief style {style!r}")
    steps = extrude_step_count(depth if depth else math.hypot(dx, dy))
    return tuple(
        (dx * step / steps, dy * step / steps, SHADE)
        for step in range(steps, 0, -1)
    )


def parity_role(label: str) -> str:
    """THE COLOUR PARITY (ledger §3): `"even"` — a white plate laid on
    the ring — or `"odd"` — a cut-out, the ring seen through the
    numeral. Rule B has no body of its own, so at border 0 an odd
    numeral is exactly ring colour on ring colour and exists ONLY
    through its relief. That is deliberate: the odd hours recede, the
    even hours advance, and the dial gains depth without gaining
    ink."""
    return "even" if int(label) % 2 == 0 else "odd"


def numeral_hours(jewel_hours) -> tuple[int, ...]:
    """THE COMPOSITION LAW (the Fidelity Ruling, ring_rework.md §2): the
    hours of the OUTER band that carry a NUMERAL — every hour except the
    ones the preset seats a LETTER on.

    One seat, one content: an Ω and a 0 never stand on the same hour
    again, which is the defect the ruling was issued for. `jewel_hours`
    arrives in the ring's own 1..24 counting (`config.constants.
    RING_OUTERS[...]["positions"]`, where MIDNIGHT is 24), so 24 folds
    to the band's own 0 here — the one place the two countings meet."""
    seated = {hour % dial.NUMERAL_HOUR_COUNT for hour in jewel_hours}
    return tuple(
        hour for hour in range(dial.NUMERAL_HOUR_COUNT) if hour not in seated
    )


def inner_composition(variant: str) -> dict:
    """One inner variant's own composition — `{"base", "numbers"}`, the
    numberless plate of the owner's that carries its ticks and arrows,
    and the five-minute seats that carry a live NUMBER.

    An unknown variant composes as the bare plate it names with no
    numbers at all: a custom ring may point at any inner file, and a
    band with no numbers is a legitimate band (`simple` is one), never
    a reason to fail a render."""
    entry = dial.RING_INNER_COMPOSITION.get(variant)
    if entry is None:
        return {"base": variant, "numbers": ()}
    return entry


def inner_number_seats(variant: str) -> tuple[tuple[str, float], ...]:
    """`(label, dial angle)` for every NUMBER the inner band composes —
    the ledger's bare labels (`"5"`, `"10"` ... no leading zero) at the
    minute's own angle. Empty for every numberless variant."""
    return tuple(
        (str(minute), minute_angle(minute))
        for minute in inner_composition(variant)["numbers"]
    )


def crown_glyph_alphabet() -> tuple[str, ...]:
    """The glyphs the LIVE CROWN renders ONCE per settings change
    (ring_rework §3): the ten digits, the colon, and the three
    lowercase letters the `"12h 35min"` format spells its unit words
    with. The digits-and-colon ELEVEN are the standard set; the small
    cut adds `h`, `m`, `i`, `n` and a space is never drawn — so the
    unit LETTERS are computed from the shipped formats themselves
    rather than typed out (Rule #5), while the DIGITS are always the
    whole ten, never only the ones one sample rendering happens to
    show: the crown must be able to say every minute, not just
    12:35."""
    glyphs = list(crown_digits_and_colon())
    for fmt in dial.CROWN_TIME_FORMATS:
        for glyph in crown_sequence(12, 35, fmt):
            if glyph != " " and glyph not in glyphs:
                glyphs.append(glyph)
    return tuple(glyphs)


def crown_digits_and_colon() -> tuple[str, ...]:
    """The ELEVEN — digits 0-9 and the colon — the ledger's own count
    for the default `hh:mm` crown."""
    return tuple("0123456789:")


def crown_sequence(hour: int, minute: int, fmt: str) -> tuple[str, ...]:
    """The glyph sequence the crown composes for one minute.

    `"hh:mm"` (the standard default) is the five glyphs `1 2 : 3 5`,
    zero-padded on both fields like every clock. `"12h 35min"` writes
    the hour BARE (no leading zero — the same rule the hour band
    follows) and the minute zero-padded, with `h` and `min` in the
    small cut; the space between the two words consumes a slot exactly
    as it does in every other crown arc (`core.crown_text`), and the
    caller skips drawing it."""
    if fmt == "hh:mm":
        return tuple(f"{hour:02d}:{minute:02d}")
    if fmt != "12h 35min":
        raise ValueError(f"unknown crown time format {fmt!r}")
    return tuple(f"{hour}h {minute:02d}min")


def crown_small_cut(glyphs: tuple[str, ...]) -> tuple[bool, ...]:
    """Which glyphs of a `crown_sequence` are drawn in the SMALL CUT —
    the `h`/`min` unit words of the `"12h 35min"` format (ring_rework
    §3: "its h/min in a small font cut"). Digits, the colon and the
    space keep the full crown size."""
    return tuple(not glyph.isdigit() and glyph not in ":. " for glyph in glyphs)


def crown_arc_angles(
    count: int, orientation: str, step_deg: float | None = None,
) -> tuple[float, ...]:
    """One dial angle per glyph of a live crown, the whole sequence
    CENTERED on the dial's top (`"top"`) or bottom (`"bottom"`) anchor
    at a fixed per-glyph step.

    The same geometry `core.crown_text.free_arc_angles` uses for a
    typed crown, and for the same reason: "top" reads clockwise
    (left-to-right over the top) while "bottom" reads counter-clockwise
    (left-to-right under the bottom), because dial-x is monotonic in
    OPPOSITE senses across the two halves of the circle. The step is
    the crown text's own `dial.RING_CROWN_TEXT_LETTER_STEP_DEG` unless
    a caller overrides it (a wider face needs more room per glyph)."""
    if orientation not in ("top", "bottom"):
        raise ValueError(f"crown orientation {orientation!r} must be top/bottom")
    if count <= 0:
        raise ValueError("a live crown needs at least one glyph")
    step = dial.RING_CROWN_TEXT_LETTER_STEP_DEG if step_deg is None else step_deg
    if orientation == "bottom":
        step = -step
    anchor = 0.0 if orientation == "top" else 180.0
    start = anchor - step * (count - 1) / 2.0
    return tuple(start + step * index for index in range(count))


def crown_zone_hm(now_local: datetime, zones: dict[str, str | None]) -> dict:
    """`zone key -> "HH:MM"` for every zone a live crown may keep
    (`dial.RING_LIVE_CROWN`'s own zone names, resolved once per minute
    tick in `core.clock_state.build_tick_state`).

    A None zone means THIS watch's own civil time — the moment is
    already local, so it is read straight off. A named zone (Templar's
    `Asia/Jerusalem`) is the same instant converted through `tzdata`;
    the instant must be timezone-aware, which every moment on the tick
    path is. Pure: the moment arrives as an argument, never from the
    wall clock."""
    from zoneinfo import ZoneInfo

    result = {}
    for key, zone in zones.items():
        moment = now_local if zone is None else now_local.astimezone(ZoneInfo(zone))
        result[key] = f"{moment.hour:02d}:{moment.minute:02d}"
    return result
