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
    """THE SEATING LAW (ledger §4, amended by the owner 2026-08-11 —
    THE FLOWING SIDES, both bands: "6 and 18 behave exactly like 45 and
    15"; the old side-square-stands-upright rule is REMOVED everywhere).

    `arc` — only the TOP and BOTTOM seats (0 and 180) stand upright.
    Every other numeral takes the angle it sits on, and the lower half
    turns a further 180 deg so nothing ever reads upside down — on BOTH
    signs of the fold (the -91..-179 lower-left quadrant is lower half
    too; a 2026-08-11 cut wrote the test as `folded >= 90` and shipped
    the third quadrant upside down — the owner's own screenshot is the
    record). The SIDE squares FLOW with the half they open clockwise:
    the +90 seat (minute 15, hour 18) turns with the lower-half
    numerals that follow it (20, 25, ...), the -90 seat (minute 45,
    hour 6) with the upper-half ones (50, 55, ...). `upright` — 0
    everywhere.

    The returned value is NOT re-folded: `rot(170) == 350` and
    `rot(-170) == 10` are the same physical rotation, and the raw form
    is what the ledger's own table states."""
    if seating == "upright":
        return 0.0
    if seating != "arc":
        raise ValueError(f"unknown numeral seating {seating!r}")
    folded = fold_angle(deg)
    if folded == 0.0 or abs(folded) == 180.0:
        return 0.0
    if abs(folded) > 90.0 or folded == 90.0:
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


def ink_arc_half_deg(
    width: float, height: float, radius: float, tilt_deg: float = 0.0,
) -> float:
    """Half the arc a rectangle of INK occupies on a band, in degrees —
    the shared geometry behind BOTH halves of the wedge (owner order
    2026-08-13, THE INK WEDGE).

    `width` and `height` are the ink's own extents and `radius` the
    band radius it is centred on, all in ONE unit (this project counts
    fractions of the dial DIAMETER). `tilt_deg` is how far the ink's own
    frame is turned away from the TANGENT — 0 for anything seated along
    the band (every jewel, every `arc`-seated numeral), and the seat's
    own negative angle for an `upright` numeral, which stands level with
    the screen while the band curves away under it.

    The answer is the widest angular reach of the rectangle's four
    CORNERS, not of its centreline: a tall glyph's corner leans further
    around the dial than its middle does, and the corner is what
    actually touches a neighbour. `radius + v <= 0` means the ink
    swallows the dial centre — geometrically it then covers every
    direction, so the answer is the honest 180."""
    if radius <= 0.0:
        raise ValueError("band radius must be positive")
    tilt = math.radians(tilt_deg)
    cos_t, sin_t = math.cos(tilt), math.sin(tilt)
    reach = 0.0
    for along in (-width / 2.0, width / 2.0):
        for across in (-height / 2.0, height / 2.0):
            # Into the band's own frame: `u` runs along the arc, `v`
            # outward from the dial centre.
            u = along * cos_t - across * sin_t
            v = along * sin_t + across * cos_t
            if radius + v <= 0.0:
                return 180.0
            reach = max(reach, abs(math.degrees(math.atan2(u, radius + v))))
    return reach


def jewel_arc_half_deg(
    ring_size: float = 1.0, jewels_scale: float = 1.0,
    aspect: float = 1.0, zoom: float = 1.0,
) -> float:
    """Half the arc ONE ring jewel occupies on the outer band, in
    degrees — THE ANGULAR WEDGE's jewel half (owner ballot verdict
    2026-08-13).

    Derived from the ring's OWN seating data, never from a magic
    number: `dial.RING_JEWEL_ART_SCALE * jewels_scale * zoom` is the
    height `render.layers.ring.RingLayer._draw_jewels` stamps the plate
    at (a fraction of the dial DIAMETER), and `dial.outer_centreline` is
    the radius it stamps it on — the same terms, read from the same
    place, so the wedge cannot drift away from what is drawn.

    THE GAP THE OWNER CLOSED (2026-08-13): `aspect` is the plate's own
    width-over-height, and the default 1.0 is the SQUARE ASSUMPTION this
    rule shipped with. It was never true of the art — `M.png` is 750 x
    512 and `I.png` is 287 x 512 on the same masters — so the wedge was
    at once too narrow for a wide letter and far too wide for a narrow
    one. The caller that knows the picture (`render.layers.numerals.
    jewel_ink_halves`, which reads the size out of the asset index
    without opening the file) passes the real number; the default
    survives for callers with no picture to measure, and for the tests
    that pin the old worked example.
    """
    radius = dial.outer_centreline(ring_size) / 2.0   # of the DIAMETER
    height = dial.RING_JEWEL_ART_SCALE * float(jewels_scale) * float(zoom)
    return ink_arc_half_deg(height * float(aspect), height, radius)


def numeral_arc_half_deg() -> float:
    """Half the arc ONE hour numeral is ASSUMED to occupy when nobody
    measured it — its whole SEAT WEDGE, half of
    `dial.NUMERAL_HOUR_STEP_DEG`.

    THE OWNER'S CORRECTION (2026-08-13), because this number is the
    reason he saw holes: a numeral claiming its entire 7.5-degree half
    seat is claiming far more than its ink. With the jewel's own half
    the reach came to 12.06 degrees against a 15-degree seat pitch, so a
    jewel took TWO numerals with it unless it stood within 2.94 degrees
    of a seat — most of the time, and visibly on his hexagram, where all
    six numbers could have been drawn.

    The live path therefore measures (`render.numeral_bands.
    numeral_ink_halves`, the ink the chosen face actually paints at the
    chosen size). This stays as the fallback for a caller with no font
    in hand, and it stays deliberately GENEROUS: where nothing is
    measured, hiding a numeral beats printing half of one under a
    letter.
    """
    return dial.NUMERAL_HOUR_STEP_DEG / 2.0


def _half_at(halves, hour: int, fallback: float) -> float:
    """One seat's half-wedge out of either a single number (every seat
    alike) or a per-hour mapping (every seat its own ink) — THE ONE DOOR
    both halves of the rule below read through, so a measured caller and
    a plain-number caller share one loop."""
    if halves is None:
        return float(fallback)
    if isinstance(halves, dict):
        return float(halves.get(hour, fallback))
    return float(halves)


def occluded_numeral_hours(
    jewel_hours, offset_deg: float, jewel_half_deg,
    numeral_half_deg=None,
) -> tuple[int, ...]:
    """THE ANGULAR WEDGE (owner ballot verdict 2026-08-13) — which hour
    numerals a set of FIXED jewels covers once the band has turned by
    `offset_deg`, and which are therefore not drawn at all.

    Pure geometry, no Qt: each jewel occupies the arc
    `[j - jewel_half, j + jewel_half]` at its UNROTATED seat (fixed
    jewels never take the world offset), each numeral the arc
    `[n - numeral_half, n + numeral_half]` at its ROTATED seat. Any
    overlap at all hides the numeral — never half a numeral under a
    letter. Touching arcs (delta exactly equal to the sum of the halves)
    do not overlap and the numeral stands.

    EITHER HALF MAY BE A MAPPING (owner order 2026-08-13): pass a plain
    number to give every seat the same wedge, or `{hour: half}` to give
    every seat its OWN measured ink — `jewel_half_deg` keyed by the
    jewel's folded hour, `numeral_half_deg` by the numeral's. Mixing is
    allowed, and a hour missing from a mapping falls back to the wedge
    it would have had before. The loop below does not care which it got,
    so the measured path and the plain path cannot diverge.

    THE TWO-NUMERAL CASE IS NOT A SPECIAL RULE. The owner's own words
    for it, kept verbatim so the rule cannot be re-derived wrongly:
    # lang-ok: the owner's ruling, quoted; translating it would lose the record
    "ako znak sece oba slova delimicno oba izostaviti sa kruznice" — a
    jewel standing between two seats overlaps both wedges, so both fall
    out of this loop with no branch of their own. And no more than two
    can ever fall: the seats are 15 degrees apart, so the third-nearest
    seat is at least 15 degrees beyond the nearer of the two, past any
    reach these halves can sum to at ordinary jewel scales.

    `jewel_hours` arrives in the ring's own 1..24 counting (midnight =
    24) and is folded to the band's 0..23 here, the same fold
    `numeral_hours` performs — one counting meets the other in this
    module and nowhere else. The result is the hours' own numbers, so
    seat 24 comes back as 0 and is drawn with the label "0".
    """
    default_numeral = numeral_arc_half_deg()
    seats = {
        hour: (
            hour_angle(hour, offset_deg),
            _half_at(numeral_half_deg, hour, default_numeral),
        )
        for hour in range(dial.NUMERAL_HOUR_COUNT)
    }
    hidden = set()
    for jewel in jewel_hours:
        seated = jewel % dial.NUMERAL_HOUR_COUNT
        jewel_angle = hour_angle(seated)
        jewel_half = _half_at(jewel_half_deg, seated, 0.0)
        for hour, (seat, numeral_half) in seats.items():
            if abs(fold_angle(seat - jewel_angle)) < jewel_half + numeral_half:
                hidden.add(hour)
    return tuple(sorted(hidden))


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


def crown_advance_angles(
    advances_deg: tuple[float, ...], orientation: str,
) -> tuple[float, ...]:
    """THE CROWN ADVANCE LAW (owner defect 2026-08-07): one dial angle
    per glyph, where each glyph occupies its OWN angular width
    `advances_deg[i]` and the whole run is CENTERED on the top
    (`"top"`) or bottom (`"bottom"`) anchor.

    The fixed-step layout this replaces (`crown_arc_angles`) gave the
    colon — 0.22 glyph-heights of ink — exactly as much arc as an M at
    1.45, which is what read as "scattered" on the owner's own
    screenshot of The One. Here every glyph is centred in its own slot,
    so a run of digits closes up and the colon takes only the room it
    needs.

    Direction follows the same rule as every other crown arc: "top"
    reads clockwise (left-to-right over the top), "bottom" reads
    counter-clockwise (left-to-right under the bottom), because dial-x
    is monotonic in OPPOSITE senses across the two halves. Feeding a
    run of EQUAL advances reproduces `crown_arc_angles` exactly, which
    is how `tests/test_numerals.py` pins the two against each other."""
    if orientation not in ("top", "bottom"):
        raise ValueError(f"crown orientation {orientation!r} must be top/bottom")
    if not advances_deg:
        raise ValueError("a live crown needs at least one glyph")
    sign = 1.0 if orientation == "top" else -1.0
    anchor = 0.0 if orientation == "top" else 180.0
    total = sum(advances_deg)
    cursor = -total / 2.0
    seats = []
    for advance in advances_deg:
        seats.append(anchor + sign * (cursor + advance / 2.0))
        cursor += advance
    return tuple(seats)


def arc_degrees(length: float, radius: float) -> float:
    """`length` (any unit) as degrees of arc on a circle of `radius`
    (the same unit) — the one place the crown's PIXEL widths become
    ANGLES. Pure geometry, so it stays in core beside the law that
    consumes it."""
    if radius <= 0.0:
        raise ValueError("arc radius must be positive")
    return 360.0 * length / (2.0 * math.pi * radius)


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
