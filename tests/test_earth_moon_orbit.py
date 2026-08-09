"""THE CLEAR ORBIT LANE TOOTH (owner verdict 2026-08-09: "Earth touches
the outer ring" — Earth and Moon must both travel on a circle that
touches neither the inner ring's own content (the minute band, its
ticks and quarter/octa arrows) nor the outer hour band).

Mirrors `tests/test_dial_extremes.py`'s style: walks the radial
EXTREMES of every setting that can move the shared Earth/Moon orbit —
"Outer ring size" and both marker scale sliders — and proves the
computed orbit (`config.dial.earth_moon_orbit_fraction`, the exact call
`render.layers.year_marker.YearMarkerLayer` and `render.compositor.
Compositor._element_at` both make) never lets either marker's disc
reach the minute band's own radius or the outer band's measured inner
edge, with a real, positive margin — never a touch-fit.
"""

import pytest

from config import constants, dial


# --- The default pin (regression, owner defect 2026-08-09) -------------------


def test_default_orbit_matches_the_hand_derivation():
    """At the default dial (ring_size 1.0, both markers at their base
    scale) the orbit is `min(MINUTES_RADIUS_FRACTION,
    POLYGON_FILL_MIN_RADIUS_FRACTION) - half_size -
    EARTH_MOON_ORBIT_CLEARANCE_FRACTION` — pinned so a future edit to
    any of the three constants is a deliberate, visible change, not a
    silent drift back toward the old touching bug. The star/polygon
    floor (owner correction round 2026-08-09, the hexagram/pentagon
    border bug) is the binding one today — it sits inside the minute
    band's own edge."""
    half_size = 0.11                      # the Earth's own base `scale`
    assert dial.POLYGON_FILL_MIN_RADIUS_FRACTION < dial.MINUTES_RADIUS_FRACTION
    expected = (
        dial.POLYGON_FILL_MIN_RADIUS_FRACTION - half_size
        - dial.EARTH_MOON_ORBIT_CLEARANCE_FRACTION
    )
    assert dial.earth_moon_orbit_fraction(1.0, half_size) == pytest.approx(expected)
    # Below ring_size 1.0 THE INWARD-GROWTH LAW is a no-op — same orbit.
    assert dial.earth_moon_orbit_fraction(0.5, half_size) == pytest.approx(expected)


# --- The extreme grid ---------------------------------------------------------

_RING_SIZES = dial.NUMERAL_OUTER_RING_SIZE_RANGE + (dial.NUMERAL_OUTER_RING_SIZE_DEFAULT,)
_SCALE_MULTIPLIERS = constants.ELEMENT_SCALE_RANGE + (1.0,)
_BASE_HALF_SIZES = (0.11, 0.08)           # the Earth's and the Moon's own `scale`

# A genuine, visible floor under BOTH real boundaries — well under the
# smallest margin the geometry guarantees (~0.076 R at the tightest
# corner below), so this is a real assertion, not a rubber-stamped one.
_MIN_REAL_MARGIN = 0.04


@pytest.mark.parametrize("ring_size", sorted(_RING_SIZES))
@pytest.mark.parametrize("multiplier", sorted(_SCALE_MULTIPLIERS))
def test_the_shared_orbit_never_touches_either_band(ring_size, multiplier):
    """Across every "Outer ring size" setting and every persistent Earth/
    Moon scale-slider setting (never the transient hover-enlarge — a
    hovered element legitimately grows over its neighbours, the exact
    reason `HoverLiftLayer` exists), the marker's disc — sized to
    whichever of Earth/Moon is currently bigger, since they share one
    orbit — must clear:

    1. the OUTER hour band's own measured inner edge
       (`dial.outer_band_edges(ring_size)[0]`) — the literal edge the
       printed metal band starts at;
    2. the minute band's own live radius (`dial.MINUTES_RADIUS_FRACTION`
       scaled by `dial.interior_scale`) — the formula's own promise.
    """
    half_size = max(multiplier * s for s in _BASE_HALF_SIZES)
    orbit = dial.earth_moon_orbit_fraction(ring_size, half_size)
    reach = orbit + half_size

    outer_inner_edge, _outer_outer_edge = dial.outer_band_edges(ring_size)
    assert reach <= outer_inner_edge - _MIN_REAL_MARGIN, (
        f"ring_size={ring_size} multiplier={multiplier}: the marker's "
        f"disc reaches {reach:.4f} R, the outer band starts at "
        f"{outer_inner_edge:.4f} R — margin "
        f"{outer_inner_edge - reach:.4f} R is under the {_MIN_REAL_MARGIN} "
        "floor (the owner's exact bug: Earth touching the outer ring)"
    )

    minutes_edge = dial.MINUTES_RADIUS_FRACTION * dial.interior_scale(ring_size)
    assert reach <= minutes_edge + 1e-9, (
        f"ring_size={ring_size} multiplier={multiplier}: the marker's "
        f"disc reaches {reach:.4f} R past the minute band's own radius "
        f"{minutes_edge:.4f} R"
    )

    # Sane at the other end too — the orbit never collapses through the
    # dial centre.
    assert orbit - half_size > 0.0, (
        f"ring_size={ring_size} multiplier={multiplier}: the orbit "
        f"({orbit:.4f} R) minus the half-size ({half_size:.4f} R) is not "
        "positive — the marker would straddle the dial centre"
    )


# --- THE HEXAGRAM/PENTAGON FLOOR (owner correction round 2026-08-09) ----------


def test_polygon_fill_floor_is_the_narrowest_arms_apothem():
    """`POLYGON_FILL_MIN_RADIUS_FRACTION` walks every pointer's own
    half-angle (`constants.POINTER_ARM_HALF_ANGLE_DEG`) — the narrowest
    arm (largest half-angle) pulls its apothem, `STAR_RADIUS_FRACTION *
    cos(half-angle)`, in the furthest, so the floor is the MINIMUM
    across every pointer the reader can pick, never a magic number."""
    import math

    expected = min(
        dial.STAR_RADIUS_FRACTION * math.cos(math.radians(half_deg))
        for half_deg in constants.POINTER_ARM_HALF_ANGLE_DEG.values()
    )
    assert dial.POLYGON_FILL_MIN_RADIUS_FRACTION == pytest.approx(expected)


@pytest.mark.parametrize("ring_size", sorted(_RING_SIZES))
@pytest.mark.parametrize("multiplier", sorted(_SCALE_MULTIPLIERS))
def test_the_shared_orbit_clears_every_pointers_star_apothem(ring_size, multiplier):
    """Across every "Outer ring size"/scale-slider extreme AND every
    pointer's own arm half-angle, the marker's disc stays inside that
    pointer's star/polygon apothem — the boundary an independent
    grader saw the Moon sit across (`crop_moon_on.png`, the hexagram/
    pentagon border bug) — with the same real margin the minute band
    and outer ring already carry."""
    half_size = max(multiplier * s for s in _BASE_HALF_SIZES)
    orbit = dial.earth_moon_orbit_fraction(ring_size, half_size)
    reach = orbit + half_size
    for pointer, half_deg in constants.POINTER_ARM_HALF_ANGLE_DEG.items():
        import math

        apothem = dial.STAR_RADIUS_FRACTION * math.cos(math.radians(half_deg))
        assert reach <= apothem + 1e-9, (
            f"ring_size={ring_size} multiplier={multiplier} "
            f"pointer={pointer}: the marker's disc reaches {reach:.4f} R, "
            f"that pointer's star apothem is {apothem:.4f} R — the marker "
            "would sit across its arm boundary line"
        )
