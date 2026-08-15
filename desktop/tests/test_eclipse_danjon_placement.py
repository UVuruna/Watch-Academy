"""THE GAUGE LEAVES THE MOON'S SHADOW (owner order 2026-08-15): the
Danjon ladder used to hang fixed BELOW the body regardless of where on
the dial the body stood, which only ever looked right for a Moon
sitting at the top. `render.eclipse_danjon._gauge_placement` is the
tooth that pins the fix — a PURE function (no QPainter, no Qt painting
at all) that derives where the ladder's own centre sits and how far it
is rotated, from ONE angle: the Moon's own dial angle.

The owner named four cardinal consequences of one rule ("standardno
racuna se ugao na kruznici i tako se pozicionira taj pravougaonik da
bude paralelan sa tangentom na kruznici" — the angle on the circle is
computed as usual, and the rectangle is positioned parallel to the
circle's own tangent there). lang-ok: the owner's own ballot sentence,
quoted so the requirement cannot be re-derived wrongly. Four hard-coded
cardinal cases would be the exact defect he warned against, so this
file also pins two off-cardinal angles (45 deg, 200 deg) and a
counter-proof that a broken (unrotated) placement fails the very same
assertions.

Layer: tests.
"""

import math

import pytest

from render.eclipse_danjon import _GAUGE_CENTER_DISTANCE, _gauge_placement

# render.painting.dial_point's own convention, restated here rather than
# imported, so this test does not (accidentally) become circular with
# the thing it is meant to be checking against: 0 deg is dial-top, and
# angle grows CLOCKWISE. The unit vector from a body standing at `theta`
# back to the dial's own centre is exactly this direction rotated by
# `theta` — see `_gauge_placement`'s own docstring for why that is the
# same rotation the ladder itself is drawn under.
def _inward_unit(theta_deg: float) -> tuple[float, float]:
    theta = math.radians(theta_deg)
    return (-math.sin(theta), math.cos(theta))


def _radial_unit(theta_deg: float) -> tuple[float, float]:
    """The direction from the dial's centre OUT to the body at
    `theta_deg` — dial_point's own convention, restated for the
    perpendicularity check below."""
    theta = math.radians(theta_deg)
    return (math.sin(theta), -math.cos(theta))


CARDINALS = {
    "north (top)": 0.0,
    "east (right)": 90.0,
    "south (bottom)": 180.0,
    "west (left)": 270.0,
}


@pytest.mark.parametrize("name,angle", list(CARDINALS.items()))
def test_gauge_sits_on_the_inward_side_at_every_cardinal(name, angle):
    """The ladder's own centre must lie TOWARD the dial's centre, never
    away from it — checked by the sign of each axis against the inward
    unit vector for that angle, which is what the owner's four examples
    (ladder above at south, below at north, left at east, right at
    west) all reduce to."""
    dx, dy, _rotation = _gauge_placement(100.0, angle)
    inward_x, inward_y = _inward_unit(angle)
    # A near-zero inward component is a real "no opinion" at that axis
    # (e.g. dx at north/south), not a sign mismatch — only compare signs
    # where the inward direction actually commits to one.
    if abs(inward_x) > 1e-9:
        assert (dx > 0) == (inward_x > 0), f"{name}: x offset on the wrong side"
    else:
        assert dx == pytest.approx(0.0, abs=1e-6), f"{name}: x should be centred"
    if abs(inward_y) > 1e-9:
        assert (dy > 0) == (inward_y > 0), f"{name}: y offset on the wrong side"
    else:
        assert dy == pytest.approx(0.0, abs=1e-6), f"{name}: y should be centred"


def test_gauge_offset_magnitude_is_the_same_at_every_cardinal():
    """The ladder is always the SAME distance from the Moon's own centre
    — only the DIRECTION changes with the angle, never the reach."""
    radius = 137.0
    magnitudes = [
        math.hypot(*_gauge_placement(radius, angle)[:2])
        for angle in CARDINALS.values()
    ]
    expected = radius * _GAUGE_CENTER_DISTANCE
    for magnitude in magnitudes:
        assert magnitude == pytest.approx(expected, rel=1e-9)


@pytest.mark.parametrize("name,angle", list(CARDINALS.items()))
def test_owners_four_named_pictures(name, angle):
    """The four consequences stated verbatim in the order: north (top)
    -> ladder below (dy > 0, dx == 0); south (bottom) -> ladder above
    (dy < 0, dx == 0); east (right) -> ladder left (dx < 0, dy == 0);
    west (left) -> ladder right (dx > 0, dy == 0)."""
    dx, dy, _rotation = _gauge_placement(100.0, angle)
    if angle == 0.0:
        assert dy > 0 and dx == pytest.approx(0.0, abs=1e-6)
    elif angle == 180.0:
        assert dy < 0 and dx == pytest.approx(0.0, abs=1e-6)
    elif angle == 90.0:
        assert dx < 0 and dy == pytest.approx(0.0, abs=1e-6)
    elif angle == 270.0:
        assert dx > 0 and dy == pytest.approx(0.0, abs=1e-6)


@pytest.mark.parametrize(
    "angle", [0.0, 90.0, 180.0, 270.0, 45.0, 200.0],
)
def test_rotation_keeps_the_ladders_long_axis_on_the_tangent(angle):
    """THE PART FOUR HARD-CODED CASES WOULD MISS: the ladder's own long
    (width) axis, carried through the rotation `_gauge_placement`
    returns, must stay PERPENDICULAR to the radius at every angle — not
    only the four cardinals, which a four-case implementation could
    special-case into looking right by accident. 45 deg and 200 deg have
    no cardinal counterpart at all."""
    _dx, _dy, rotation = _gauge_placement(100.0, angle)
    theta = math.radians(rotation)
    # The ladder's own local width axis (1, 0) carried through the same
    # clockwise, y-down rotation `QPainter.rotate` applies.
    axis_x = math.cos(theta)
    axis_y = math.sin(theta)
    radial_x, radial_y = _radial_unit(angle)
    dot = axis_x * radial_x + axis_y * radial_y
    assert dot == pytest.approx(0.0, abs=1e-9), (
        f"angle {angle}: ladder axis is not parallel to the tangent"
    )


def _broken_rotation_only(radius: float, dial_angle_deg: float) -> float:
    """THE COUNTER-PROOF (dropping the rotation, keeping only the
    translation): if the real implementation ever regressed to this, the
    tangent check above must go RED. Proven directly below rather than
    asserted about — this function is never called by product code."""
    return 0.0


@pytest.mark.parametrize("angle", [45.0, 90.0, 200.0, 270.0])
def test_counter_proof_dropping_the_rotation_fails_the_tangent_check(angle):
    """Without the rotation, the ladder's width axis stays fixed at
    (1, 0) regardless of the Moon's angle — which is NOT perpendicular
    to the radius at these angles, so the very assertion
    `test_rotation_keeps_the_ladders_long_axis_on_the_tangent` makes must
    fail here. This is the red half of the red/green proof; the green
    half is that same test passing against the real
    `_gauge_placement` above."""
    broken_rotation = _broken_rotation_only(100.0, angle)
    theta = math.radians(broken_rotation)
    axis_x, axis_y = math.cos(theta), math.sin(theta)
    radial_x, radial_y = _radial_unit(angle)
    dot = axis_x * radial_x + axis_y * radial_y
    assert dot != pytest.approx(0.0, abs=1e-9), (
        "the counter-proof itself is broken: the unrotated axis "
        "happened to be perpendicular by coincidence at this angle"
    )
