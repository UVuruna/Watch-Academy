"""THE DIAL EXTREME CONTAINMENT TOOTH (owner order 2026-08-09: "ako je
settings neki raspon proveriš minimum i maksimum i onda bi video da RING
iskače iz okvira").

The failure it pins: at "Outer ring size" above 1.0 the hour band used
to grow OUTWARD past the dial circle and the clip sliced it into an
octagon — visible on the owner's own live screenshot, invisible to every
existing test because none ever rendered the dial at a range's extremes.
THE INWARD-GROWTH LAW (owner verdict, same day) replaced the outward
rule; this tooth renders the REAL compositor at the extreme corners of
every radial size range and asserts the full frame stays inside the
window the widget would actually create (dial square + the live margin
`defaults.dial_window_margin_fraction` reserves).

Offscreen (Silent Audits law), on a generous apron so nothing is clipped
before it can be measured.
"""

from dataclasses import replace
from datetime import datetime
from zoneinfo import ZoneInfo

import astral
import pytest
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QApplication

from app.skin_builder import build_skin
from app.settings_store import Settings
from config import constants, defaults, dial
from core.clock_state import build_day_context, build_tick_state
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from render.assets import shared_cache
from render.compositor import Compositor


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture(scope="module")
def moment():
    now = datetime(2026, 6, 20, 12, 35, tzinfo=ZoneInfo("Europe/Belgrade"))
    observer = astral.Observer(latitude=44.8, longitude=20.5)
    day = build_day_context(
        now, observer, SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    return day, build_tick_state(now, day)


def _painted_bounds(settings: Settings, moment) -> tuple[int, int, int, int]:
    """Paint the real compositor on an aproned canvas; return how far
    the ink reaches beyond the dial square on each side (positive =
    outside the square; the window margin is judged by the caller)."""
    day, tick = moment
    skin = build_skin(settings)
    compositor = Compositor(skin, shared_cache())
    compositor.set_day(day)
    size = float(settings.diameter)
    pad = int(size)
    canvas = QImage(
        int(size) + 2 * pad, int(size) + 2 * pad,
        QImage.Format.Format_ARGB32_Premultiplied,
    )
    canvas.fill(0)
    painter = QPainter(canvas)
    painter.translate(pad, pad)
    try:
        compositor.paint(painter, size, 1.0, tick)
    finally:
        painter.end()
    left = top = 10 ** 9
    right = bottom = -1
    step = 2                       # every other pixel — bounds, not art
    for y in range(0, canvas.height(), step):
        for x in range(0, canvas.width(), step):
            if canvas.pixelColor(x, y).alpha() > 8:
                left = min(left, x)
                right = max(right, x)
                top = min(top, y)
                bottom = max(bottom, y)
    return (
        pad - left, pad - top,
        right - (pad + int(size)), bottom - (pad + int(size)),
    )


def _window_margin(settings: Settings) -> int:
    return round(
        settings.diameter
        * defaults.dial_window_margin_fraction(build_skin(settings))
    )


_EXTREMES = {
    "max radial sizes": dict(
        numeral_outer_size=dial.NUMERAL_SIZE_RANGE[1],
        numeral_outer_ring_size=dial.NUMERAL_OUTER_RING_SIZE_RANGE[1],
        minutes_size=dial.NUMERAL_SIZE_RANGE[1],
        ring_jewels_scale=constants.ELEMENT_SCALE_RANGE[1],
        crown_text_scale=constants.ELEMENT_SCALE_RANGE[1],
    ),
    "min radial sizes": dict(
        numeral_outer_size=dial.NUMERAL_SIZE_RANGE[0],
        numeral_outer_ring_size=dial.NUMERAL_OUTER_RING_SIZE_RANGE[0],
        minutes_size=dial.NUMERAL_SIZE_RANGE[0],
        ring_jewels_scale=constants.ELEMENT_SCALE_RANGE[0],
        crown_text_scale=constants.ELEMENT_SCALE_RANGE[0],
    ),
    "max marker scales": dict(
        earth_scale=constants.ELEMENT_SCALE_RANGE[1],
        moon_scale=constants.ELEMENT_SCALE_RANGE[1],
        hover_enlarge=constants.HOVER_ENLARGE_RANGE[1],
    ),
}


@pytest.mark.parametrize("label", sorted(_EXTREMES))
def test_the_dial_never_escapes_its_window_at_range_extremes(
    app, moment, label,
):
    settings = replace(Settings(), **_EXTREMES[label])
    margin = _window_margin(settings)
    overflow = _painted_bounds(settings, moment)
    escaped = [side - margin for side in overflow]
    assert all(side <= 0 for side in escaped), (
        f"{label}: ink escapes the real window by {escaped} px "
        "(L, T, R, B) — the margin law or a radial clamp is broken"
    )


def test_default_render_is_untouched_by_the_inward_growth_law(app, moment):
    """At the DEFAULT band width the law is a strict no-op: interior
    scale 1.0, band edges exactly the measured plate — pinned so the
    fix for the extremes can never silently move the default dial."""
    from render import numeral_bands

    assert numeral_bands.interior_scale(1.0) == 1.0
    assert numeral_bands.band_ride_shift(1.0) == 0.0
    inner, outer = numeral_bands.outer_band_edges(1.0)
    assert outer == pytest.approx(
        dial.NUMERAL_OUTER_RADIUS_FRACTION
        + dial.NUMERAL_OUTER_BAND_WIDTH_FRACTION / 2.0
    )
    assert inner == pytest.approx(
        dial.NUMERAL_OUTER_RADIUS_FRACTION
        - dial.NUMERAL_OUTER_BAND_WIDTH_FRACTION / 2.0
    )


# --- THE CROSSED CORNERS (opus verification F9/F11, 2026-08-09) ---------------
# The first tooth paired every slider's MIN with every OTHER slider's
# MIN — the combinations that exposed the bottom end (a THIN band with a
# LARGE numeral size / large jewels) were structurally unreachable, and
# clipping INSIDE the band plate (whose canvas IS the dial square) never
# "escapes the window" at all. This half probes the PLATE itself.

import math

from render.layers.numerals import band_spec
from render.numeral_bands import band_plate


def _max_solid_reach(settings: Settings) -> float:
    """The farthest radius (fraction of R) any SOLID ink (alpha > 200)
    of the OUTER band's plate reaches. The plate canvas IS the dial
    square, so "content stays inside the dial circle" is exactly
    `reach <= 1.0 + eps` — measured RADIALLY, immune to the rim's own
    tangency pixels that a naive edge-touch test miscounts (the first
    cut of this tooth flagged the rim arc itself)."""
    skin = build_skin(settings)

    class _Ctx:
        radius = 600.0
        dpr = 1.0
        world_offset = 0.0

    # A fresh build, not a cache hit: the process-wide plate cache can
    # hold a same-key plate built by an earlier test module under a
    # different (monkeypatched/font-warmup) environment.
    from render import numeral_bands as _nb
    _nb._PLATES.clear()
    plate = band_plate(band_spec(skin, "outer", _Ctx))
    size = plate.width()
    centre = (size - 1) / 2.0
    worst = 0.0
    for y in range(0, size, 2):
        for x in range(0, size, 2):
            if plate.pixelColor(x, y).alpha() > 200:
                reach = math.hypot(x - centre, y - centre) / (size / 2.0)
                if reach > worst:
                    worst = reach
    return worst


_CORNERS = {
    "thin band, max numerals": dict(
        numeral_outer_ring_size=dial.NUMERAL_OUTER_RING_SIZE_RANGE[0],
        numeral_outer_size=dial.NUMERAL_SIZE_RANGE[1],
    ),
    "wide band, max numerals": dict(
        numeral_outer_ring_size=dial.NUMERAL_OUTER_RING_SIZE_RANGE[1],
        numeral_outer_size=dial.NUMERAL_SIZE_RANGE[1],
    ),
    "default band, max numerals": dict(
        numeral_outer_size=dial.NUMERAL_SIZE_RANGE[1],
    ),
}


def _real_glyphs_available() -> bool:
    """Whether the numeral face resolves to REAL glyph outlines in this
    process. The offscreen platform's font database is EMPTY on Windows
    (the tofu root cause — tests/offscreen_fonts.py; the "WatchController
    degrades the roster" reading of 2026-08-09 was a confound and is
    CORRECTED there), so under a guard run everything used to probe as
    .notdef boxes, wider than any real digit. conftest now provisions
    the machine's fonts into the empty database, and the instrument
    tooth below fails LOUDLY if that ever stops working — this probe
    stays as the tier chooser so a half-broken environment still gets a
    live bound instead of a silent skip."""
    from render.numeral_relief import glyph_path
    from render.numeral_fonts import numeral_font

    try:
        font = numeral_font("outer", Settings().numeral_face, 100.0)
    except Exception:
        return False
    path = glyph_path("8", font)
    box = path.boundingRect()
    # A real '8' is clearly taller than wide; a .notdef box is not.
    return box.height() > box.width() * 1.15


def test_the_suite_measures_with_real_glyphs(app):
    """THE INSTRUMENT TOOTH (2026-08-09): the corner teeth below carry
    a two-tier bound so a font-less environment can never silently skip
    them — but the REAL tier is the one the product is judged by, and
    this test is what keeps it engaged. It fails the suite the moment
    font provisioning stops turning the offscreen platform's empty
    database into real families, instead of letting every glyph
    measurement quietly loosen to the tofu tier."""
    from tests.offscreen_fonts import provision

    assert provision(), (
        "no real font families are available in this process — "
        "tests/offscreen_fonts.py could not fill the platform database"
    )
    assert _real_glyphs_available(), (
        "the numeral face still probes as .notdef boxes with a "
        "populated font database — the tofu root cause has a new shape"
    )


@pytest.mark.parametrize("label", sorted(_CORNERS))
def test_the_band_plate_never_cuts_its_own_ink_at_slider_corners(
    app, moment, label,
):
    settings = replace(Settings(), **_CORNERS[label])
    reach = _max_solid_reach(settings)
    # Two-tier bound, NEVER a silent skip (the F12 lesson): with real
    # glyphs the clamp holds everything to the rim; under a degraded
    # tofu-font roster the boxes run wider, so the bound loosens but
    # stays live — the owner's original octagon overflow was ~1.11 R
    # and still fails either tier.
    limit = 1.006 if _real_glyphs_available() else 1.02
    assert reach <= 1.0 + (limit - 1.0), (
        f"{label}: solid band ink reaches {reach:.4f} R (limit {limit})"
        " — content leaves the dial circle and the plate canvas cuts "
        "it (the owner's octagon defect class)"
    )


def test_a_thin_band_with_max_jewels_stays_inside_the_window(app, moment):
    """Opus F10's exact repro: ring_size at MIN slides nothing outward
    any more (the two-direction law) and the margin's jewel term reads
    the LIVE centreline — the combination that once cut a jewel's
    shadow on a crown-less ring must stay contained."""
    settings = replace(
        Settings(),
        numeral_outer_ring_size=dial.NUMERAL_OUTER_RING_SIZE_RANGE[0],
        ring_jewels_scale=constants.ELEMENT_SCALE_RANGE[1],
        earth_scale=constants.ELEMENT_SCALE_RANGE[0],
        moon_scale=constants.ELEMENT_SCALE_RANGE[0],
    )
    margin = _window_margin(settings)
    escaped = [side - margin for side in _painted_bounds(settings, moment)]
    assert all(side <= 0 for side in escaped), (
        f"ink escapes the real window by {escaped} px (L, T, R, B)"
    )
