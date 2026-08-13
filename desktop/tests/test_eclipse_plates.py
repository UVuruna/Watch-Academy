"""THE OWNER'S TWO ECLIPSE BODY PLATES — measured, and the composition
that rides them (his art and his rule, 2026-08-13).

Three claims live here and each one has already been wrong once in this
project's history, in one form or another:

1. **The measurement is real.** `render.solar_eclipse` derives every
   eclipse dimension from four fractions read off his two PNGs. A
   constant that was measured once and then drifted from the file is a
   silent lie, so this module RE-MEASURES the files and requires the
   constants to match. Change the art, and the numbers must be taken
   again — the test says so out loud instead of the dial quietly
   growing a mismatched rim.
2. **The plates load at all.** A missing plate must RAISE (THE ONE
   PLATE LAW): a whole missing digit alphabet once shipped as font-drawn
   text with every test green, because the fallback was silent.
3. **The dark disc never eats the rays.** His single composition rule.
   It is enforced by a clip in `solar_eclipse._bite`, and proved here on
   the rendered pixels rather than on the intent.

Layer: tests.
"""

import math
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QApplication

from config import defaults
from render import marker_marks, solar_eclipse

# The measuring instrument: how many points are sampled around each
# radius ring, and how far apart two radius rings are. 1/1000 of the
# half-size is finer than any constant is stated to.
RING_SAMPLES = 1440
RING_STEPS = 1000
SOLID_ALPHA = 200           # "ink is really there", not an antialiased edge
FAINT_ALPHA = 20            # "any ink at all"
BLACK_LUMA = 4              # PURE black: the Moon's body, before his rim glow


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _rings(path):
    """(fraction of half-size, solid share, any-ink share, black share)
    for every radius ring of an art file — the same scan the constants
    in `render.solar_eclipse` were read off."""
    image = QImage(str(path))
    assert not image.isNull(), f"the eclipse body plate {path} does not load"
    image = image.convertToFormat(QImage.Format.Format_ARGB32)
    width, height = image.width(), image.height()
    centre_x, centre_y = (width - 1) / 2.0, (height - 1) / 2.0
    half = min(width, height) / 2.0
    rows = []
    for step in range(1, RING_STEPS + 1):
        fraction = step / RING_STEPS
        radius = fraction * half * 0.999
        solid = faint = black = 0
        for index in range(RING_SAMPLES):
            theta = 2 * math.pi * index / RING_SAMPLES
            x = min(width - 1, max(0, round(centre_x + radius * math.cos(theta))))
            y = min(height - 1, max(0, round(centre_y + radius * math.sin(theta))))
            colour = image.pixelColor(x, y)
            if colour.alpha() > SOLID_ALPHA:
                solid += 1
                if (colour.red() + colour.green() + colour.blue()) / 3 < BLACK_LUMA:
                    black += 1
            if colour.alpha() > FAINT_ALPHA:
                faint += 1
        rows.append((
            fraction, solid / RING_SAMPLES,
            faint / RING_SAMPLES, black / RING_SAMPLES,
        ))
    return rows


def _last(rows, column):
    """The outermost ring whose share on `column` is still complete."""
    return max(f for f, *shares in rows if shares[column] >= 0.999)


def _outermost(rows, column):
    return max(f for f, *shares in rows if shares[column] > 0.02)


def test_the_sun_plate_measures_what_the_constants_claim(app):
    """His Sun: a solid yellow DISC, then the ink breaks into sparse
    spokes that run out to the ray tips. Both radii are stated in
    `solar_eclipse` and both are read back off the file here."""
    rows = _rings(defaults.ECLIPSE_BODY_SUN_ART)
    disc = _last(rows, 0)
    rays = _outermost(rows, 1)
    assert disc == pytest.approx(solar_eclipse._SUN_PLATE_DISC_FRACTION, abs=0.005), (
        f"the Sun plate's solid disc now ends at {disc:.3f} of its "
        f"half-size, not the {solar_eclipse._SUN_PLATE_DISC_FRACTION} "
        "the composition is built on — re-measure and restate it"
    )
    assert rays == pytest.approx(solar_eclipse._SUN_PLATE_RAY_FRACTION, abs=0.005), (
        f"the Sun plate's rays now reach {rays:.3f} of its half-size, "
        f"not {solar_eclipse._SUN_PLATE_RAY_FRACTION}"
    )
    # And the two are genuinely different things: past the disc the ink
    # must be SPARSE, or "clip the dark disc to the yellow disc" would
    # be describing a boundary that is not there.
    beyond = [share for f, share, *_ in rows if f > disc + 0.05]
    assert max(beyond) < 0.9, "the Sun plate has no ray zone at all"


def test_the_moon_plate_measures_what_the_constants_claim(app):
    """His Moon: pure black out to its limb, then a rim glow that runs
    to the frame edge and is cut there."""
    rows = _rings(defaults.ECLIPSE_BODY_MOON_ART)
    black = _last(rows, 2)
    edge = _outermost(rows, 1)
    assert black == pytest.approx(solar_eclipse._MOON_PLATE_DISC_FRACTION, abs=0.005), (
        f"the Moon plate's black body now ends at {black:.3f} of its "
        f"half-size, not the {solar_eclipse._MOON_PLATE_DISC_FRACTION} "
        "the occulter is scaled by"
    )
    assert edge == pytest.approx(solar_eclipse._MOON_PLATE_GLOW_FRACTION, abs=0.005), (
        "the Moon plate's rim glow no longer reaches its own frame edge"
    )


def _render(state, magnitude, radius=100.0, size=400):
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    try:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.translate(size / 2.0, size / 2.0)
        marker_marks.draw_solar_eclipse(
            painter, "bite", radius, state, magnitude, "#FFD34D",
        )
    finally:
        # ALWAYS end the painter, even when the paint RAISES. A QImage
        # destroyed with a painter still active aborts the interpreter,
        # which is how the missing-plate test below took the whole
        # suite down instead of reporting a failure.
        painter.end()
    return image


def _ink_share(image, inner, outer, radius=100.0):
    """The share of an annulus (in body radii) carrying any ink."""
    centre = image.width() / 2.0
    hits = total = 0
    for index in range(RING_SAMPLES):
        theta = 2 * math.pi * index / RING_SAMPLES
        for step in range(24):
            reach = radius * (inner + (outer - inner) * (step + 0.5) / 24)
            x = round(centre + reach * math.cos(theta))
            y = round(centre + reach * math.sin(theta))
            total += 1
            if image.pixelColor(x, y).alpha() > FAINT_ALPHA:
                hits += 1
    return hits / total


def test_the_plates_are_actually_drawn(app):
    """The composition renders his art, not an empty frame — the whole
    style is two pixmaps, so "it drew nothing" is the failure mode."""
    for state, magnitude in (
        ("solar_partial", 0.62), ("solar_annular", 0.94),
        ("solar_total", 1.05), ("solar_hybrid", 1.00),
    ):
        image = _render(state, magnitude)
        assert _ink_share(image, 0.0, 0.9) > 0.9, (
            f"{state} drew no body at all in the bite style"
        )
        assert _ink_share(image, 1.0, 1.3) > 0.02, (
            f"{state} drew no rays — his plate is not being drawn"
        )


def test_a_missing_plate_raises_rather_than_falling_back(app, monkeypatch):
    """THE ONE PLATE LAW. A plate that cannot be found must stop the
    paint, never quietly leave the Sun bare."""
    monkeypatch.setattr(
        defaults, "ECLIPSE_BODY_SUN_ART",
        defaults.ECLIPSE_BODY_SUN_ART.with_name("no_such_plate.png"),
    )
    with pytest.raises(ValueError):
        _render("solar_partial", 0.62)


def test_the_hybrid_ghost_ring_is_a_trace_not_the_annular_ring(app):
    """HYBRID IS TOTAL AT ITS EPICENTRE, plus one thin faint ring of
    fire on the dark limb (owner reasoning 2026-08-13). The mark must be
    THERE — it is the only thing separating hybrid from total once both
    cover the disc — and must stay a TRACE: measurably weaker than the
    annular eclipse's own ring, or it stops meaning "elsewhere along
    this path" and starts claiming the wrong type."""
    radius = 100.0
    hybrid = _render("solar_hybrid", 1.00, radius=radius)
    total = _render("solar_total", 1.05, radius=radius)

    def warm_band(image):
        """How many pixels of warm light the limb carries along the +x
        radius, INSIDE the Sun's own disc. Outside it every type carries
        the same yellow rays, so a band reaching past the limb would
        score the same for all three and prove nothing. WIDTH is the
        measure rather than peak brightness: what makes the ghost a
        trace is that it is a hairline, not that it is dim — a dim wide
        ring would read as a real ring of fire behind cloud."""
        centre = image.width() / 2.0
        warm = 0
        for step in range(0, 500):
            reach = 100.0 * (0.50 + step / 1000.0)
            colour = image.pixelColor(round(centre + reach), round(centre))
            if colour.red() * colour.alphaF() > 128:
                warm += 1
        return warm

    ghost, dark = warm_band(hybrid), warm_band(total)
    # Tenths of a pixel: 500 samples across half a body radius.
    expected = 10 * radius * (
        solar_eclipse._MOON_PLATE_GLOW_FRACTION
        - solar_eclipse._MOON_PLATE_DISC_FRACTION
    )
    ring_of_fire = 10 * radius * (1.0 - solar_eclipse._ANNULAR_SHRINK)
    assert dark < 10, (
        "a total eclipse must leave no warm light on the disc beyond the "
        f"limb's own antialiasing (found {dark} tenths of a pixel)"
    )
    assert ghost > dark + 20, (
        "the hybrid's ghost ring is not being drawn — it would be the "
        "same picture as a total eclipse"
    )
    assert ghost == pytest.approx(expected, abs=25), (
        f"the ghost ring is {ghost / 10:.1f} px wide, not the "
        f"{expected / 10:.1f} px his own Moon plate's rim glow measures"
    )
    assert ghost < 0.7 * ring_of_fire, (
        f"the ghost ring is {ghost / 10:.1f} px against the annular ring "
        f"of fire's {ring_of_fire / 10:.1f} px — it must read as a trace "
        "of one, not as the thing itself"
    )


def test_the_dark_disc_never_covers_the_rays(app):
    """HIS ONE COMPOSITION RULE (owner 2026-08-13): the dark disc may
    cover the Sun's yellow disc and nothing beyond it.

    Measured where it can actually be broken — TOTALITY, the one case
    where the Moon is larger than the Sun (size ratio 1.05) and would
    reach 5 % into the ray zone if it were not clipped. The ray band
    just outside the disc must carry as much ink at totality as it does
    with no eclipse geometry over it at all."""
    total = _render("solar_total", 1.05)
    partial = _render("solar_partial", 0.0)      # tangency: nothing covered
    for inner, outer in ((1.01, 1.10), (1.10, 1.30)):
        eclipsed = _ink_share(total, inner, outer)
        bare = _ink_share(partial, inner, outer)
        assert eclipsed >= bare - 0.01, (
            f"the dark disc ate the rays between {inner} and {outer} body "
            f"radii ({eclipsed:.3f} of the ink left, against {bare:.3f} "
            "with nothing covering the Sun)"
        )
    # And it DID cover the disc — otherwise the test above would pass on
    # a composition that simply never draws the Moon.
    assert _ink_share(total, 0.0, 0.9) > 0.9
    assert total.pixelColor(200, 200).red() < 40, (
        "totality must leave the yellow disc completely covered"
    )


def test_the_occulter_sits_at_the_measured_disc_radius(app):
    """The Moon plate is scaled so its measured BLACK BODY equals the
    occulter radius `solar_occulter_geometry` returns — not its frame,
    not its glow. Proved by walking out along the line of centres at a
    partial eclipse and finding where the black ends."""
    radius = 100.0
    occulter, distance = marker_marks.solar_occulter_geometry(
        "solar_partial", radius, 0.62
    )
    image = _render("solar_partial", 0.62, radius=radius)
    centre = image.width() / 2.0
    # Walk BACK from the Sun's own limb toward the Moon's centre: the
    # last dark pixel is the Moon's limb on that side, at distance -
    # occulter from the Moon's centre... which for this geometry lies
    # inside the Sun, where the clip cannot interfere.
    edge = None
    for step in range(0, 1400):
        x = distance - occulter + step / 10.0
        colour = image.pixelColor(round(centre + x), round(centre))
        if (colour.red() + colour.green() + colour.blue()) / 3 < BLACK_LUMA:
            edge = x
            break
    assert edge is not None, "no dark body was drawn at all"
    assert edge == pytest.approx(distance - occulter, abs=2.0), (
        f"the occulter's limb is at {edge:.1f} px, not the "
        f"{distance - occulter:.1f} px the geometry says"
    )
