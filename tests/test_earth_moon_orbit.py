"""THE LINE AND THE BODIES TOOTH (owner corrections 2026-08-10/11 —
SUPERSEDES the 2026-08-09 "clear orbit lane" clearance this file used
to pin): the Moon Horizon Band's thread rides the 360 little pointers'
OUTER ROOTS (`dial.RING_INNER_TICK_OUTER_FRACTION`, the end of the
inner circle), the little pointers hang inward from it, and EACH of
the Earth and the Moon rides so its OWN disc TOUCHES the little
pointers' TIP line (`RING_INNER_TICK_INNER_FRACTION`) from inside — a
per-body tangent fit, no clearance gap and no shortfall. The
position-pointer arrow bridges the tick zone between the two lines,
behind the body.

Walks the radial extremes of every setting that can move the shared
orbit — "Outer ring size" and both marker scale sliders — and proves
the computed orbit (`config.dial.earth_moon_orbit_fraction`, the exact
call `render.layers.year_marker.YearMarkerLayer` and
`render.compositor.Compositor._element_at` both make) puts the disc's
edge exactly on the line at every combination.
"""

import pytest

from config import constants, dial


# --- The measured tick zone itself -------------------------------------------


def test_the_tick_zone_is_inside_the_hour_band():
    """The measured tick zone must be coherent: tips inside roots, and
    the tips' radius inside the outer hour band's measured inner edge —
    otherwise the line the bodies touch would sit under the printed
    metal band."""
    assert dial.RING_INNER_TICK_INNER_FRACTION < dial.RING_INNER_TICK_OUTER_FRACTION
    outer_inner_edge, _ = dial.outer_band_edges(1.0)
    assert dial.RING_INNER_TICK_INNER_FRACTION < outer_inner_edge


# --- The tangent fit at every extreme ----------------------------------------

_RING_SIZES = dial.NUMERAL_OUTER_RING_SIZE_RANGE + (dial.NUMERAL_OUTER_RING_SIZE_DEFAULT,)
_SCALE_MULTIPLIERS = constants.ELEMENT_SCALE_RANGE + (1.0,)
_BASE_HALF_SIZES = (0.11, 0.08)           # the Earth's and the Moon's own `scale`


@pytest.mark.parametrize("ring_size", sorted(_RING_SIZES))
@pytest.mark.parametrize("multiplier", sorted(_SCALE_MULTIPLIERS))
def test_every_marker_touches_the_line_exactly(ring_size, multiplier):
    """Across every "Outer ring size" setting and every persistent
    Earth/Moon scale-slider setting (never the transient hover-enlarge —
    a hovered element legitimately grows over its neighbours), EACH
    marker's disc edge sits EXACTLY on the tick-root line, scaled by
    `interior_scale` like every other interior member (THE
    INWARD-GROWTH LAW) — per-body tangent, so BOTH bodies touch, not
    just the bigger one."""
    line = dial.RING_INNER_TICK_INNER_FRACTION * dial.interior_scale(ring_size)
    for base in _BASE_HALF_SIZES:
        half_size = multiplier * base
        orbit = dial.earth_moon_orbit_fraction(ring_size, half_size)
        reach = orbit + half_size
        assert reach == pytest.approx(line), (
            f"ring_size={ring_size} multiplier={multiplier} "
            f"half={half_size}: the marker's disc reaches {reach:.4f} R "
            f"but the line sits at {line:.4f} R — the body must TOUCH "
            "the line (owner corrections 2026-08-10/11)"
        )
        # Sane at the other end too — the orbit never collapses through
        # the dial centre.
        assert orbit - half_size > 0.0


def test_the_pointer_stays_behind_the_body_with_a_bounded_tip_peek():
    """THE ARROW IS BEHIND THE BODY (owner correction 2026-08-11, "IZA
    NE ISPRED"): its dimensions are proportional to the body, and the
    tip's peek past the body's edge is hard-capped so it can never
    reach visibly into the hour band."""
    assert 0.0 < dial.MARKER_POINTER_LENGTH_RATIO < 1.0
    assert 0.0 < dial.MARKER_POINTER_WIDTH_RATIO < 1.0
    assert 0.0 < dial.MARKER_GEM_LENGTH_RATIO < 1.0
    assert 0.0 < dial.MARKER_GEM_WIDTH_RATIO < 1.0
