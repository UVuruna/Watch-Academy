"""The Seating geometry (WORKPLAN Session 26, CUBE.md §The Seatings):
the Calendar-12 arm-per-axis wheel and the Rose-24 seat-per-ray ring.

THE OWNER'S FIRST LAW (2026-07-28): *"Primarna je simetrija, sekundarna
je simbolika."* Symmetry decides which KIND of axis stands where;
symbolism only decides which axis of that kind. Both wheels are pinned
golden, and the Rose's ring is not merely compared against the sealed
constant — the whole exhaustive search is RE-RUN here, law by law, so the
constant can never drift away from the argument that produced it.
"""

from itertools import permutations, product

import pytest

from config import cube
from core import cube_seating as seating


# --- the canon table ------------------------------------------------------------
def test_the_table_is_the_65_sealed_terms():
    assert len(cube.AXES) == 13
    ends = [end for axis in cube.AXES for end in (axis.cold, axis.warm)]
    assert len(ends) == 26
    terms = ({axis.name for axis in cube.AXES}
             | {end.luminous for end in ends} | {end.fallen for end in ends})
    assert len(terms) == 65
    assert all(end.luminous and end.fallen for end in ends)
    assert cube.THE_ONE.fallen == ""            # no fall touches the centre


def test_every_cell_of_the_cube_is_seated_exactly_once():
    coords = [end.coords for axis in cube.AXES for end in (axis.cold, axis.warm)]
    assert len(set(coords)) == 26
    assert set(coords) == {c for c in product((-1, 0, 1), repeat=3) if any(c)}
    for axis in cube.AXES:
        assert seating.antipode(axis.cold.coords) == axis.warm.coords


def test_the_sacred_axis_is_the_one_the_geometry_names():
    # The Sacred Axis is DERIVED, not declared: it is the only vertex axis
    # with no odd-signed coordinate, which is why its ends leave the ring.
    assert seating.SACRED_AXIS.name == "The Sacred Axis"
    assert seating.SACRED_AXIS.cold.coords == (-1, -1, -1)
    assert len(seating.HUMAN_AXES) == 12
    assert len(seating.HUMAN_CELLS) == 24


def test_the_families_count_three_six_three():
    """3 + 6 + 3 is what makes the symmetry law possible at all: two
    opposed equilateral triangles with a regular hexagon between them."""
    families = {}
    for axis in seating.HUMAN_AXES:
        families.setdefault(seating.family_of(axis), []).append(axis)
    assert {name: len(group) for name, group in families.items()} == {
        "primary": 3, "secondary": 6, "tertiary": 3}


# --- the parity theorem ---------------------------------------------------------
def test_no_ring_can_seat_all_twenty_six_cells():
    """Every kinship step changes the nonzero-count by one, so a closed
    ring must alternate between the two sides — and they are not equal."""
    cells = [c for c in product((-1, 0, 1), repeat=3) if any(c)]
    odd = [c for c in cells if seating.rank(c) % 2]
    assert (len(odd), len(cells) - len(odd)) == (14, 12)     # cannot alternate

    human = list(seating.HUMAN_CELLS)
    odd = [c for c in human if seating.rank(c) % 2]
    assert (len(odd), len(human) - len(odd)) == (12, 12)     # can


# --- the symmetry law -----------------------------------------------------------
def test_the_symmetry_law_is_the_owners_own_hexagram_pairs():
    """'iz primarne idu 12-24, 4-16, 20-8 (hexa pozicije)' — the three
    face axes on one hexagram, the three corner axes on the other, the
    six edge axes on the hexagon between."""
    poles = [ray for ray in range(24) if seating.required_rank(ray) == 1]
    corners = [ray for ray in range(24) if seating.required_rank(ray) == 3]
    edges = [ray for ray in range(24) if seating.required_rank(ray) == 2]
    assert [seating.ray_hour(ray) for ray in poles] == [12, 16, 20, 0, 4, 8]
    assert [seating.ray_hour(ray) for ray in corners] == [14, 18, 22, 2, 6, 10]
    assert len(edges) == 12
    # each family's rays are exactly evenly spaced
    for group, step in ((poles, 4), (corners, 4), (edges, 2)):
        assert all(b - a == step for a, b in zip(group, group[1:]))


def test_symmetry_is_compatible_with_kinship():
    """The owner's demand costs nothing structural: 48 of the 1056 rings
    that obey the two hard laws obey the symmetry law too."""
    assert len(seating.antipodal_rings(symmetric=False)) == 1056
    assert len(seating.antipodal_rings()) == 48


# --- the exhaustive search ------------------------------------------------------
@pytest.fixture(scope="module")
def rings():
    return seating.antipodal_rings()


def test_every_ring_obeys_the_three_hard_laws(rings):
    for ring in rings:
        assert len(set(ring)) == 24
        assert seating.is_symmetric(ring)
        for ray in range(24):
            assert seating.is_kin(ring[ray], ring[(ray + 1) % 24])
            assert ring[(ray + 12) % 24] == seating.antipode(ring[ray])


def test_the_six_poles_can_never_all_wear_their_sealed_hue(rings):
    """The honest miss: four of six is the ceiling, and the two that miss
    are always one axis's own pair — exactly the Prophecy wheel's case."""
    assert max(seating.poles_oriented(r) for r in rings) == 4


def test_the_laws_leave_exactly_one_seating(rings):
    held = [r for r in rings if seating.diagonals_held(r) == 3]
    assert len(held) == 8                     # all three axes on their diagonals
    oriented = [r for r in held if seating.poles_oriented(r) == 4]
    assert len(oriented) == 4
    crown = [r for r in oriented if r[6] == (-1, -1, 1)]
    assert len(crown) == 2                    # the crown on the Ruler's red 18h
    assert all(r[0] == (0, 1, 0) for r in oriented)     # Loyalty crowns 12h always
    solved = seating.solve_rose_seating()
    assert len(solved) == 1
    assert solved[0] == cube.ROSE_24_SEATING


# --- the Rose-24 ----------------------------------------------------------------
def test_rose_seating_obeys_every_law():
    seats = seating.rose_seating()
    assert len(seats) == 24
    assert {s.cell.coords for s in seats} == set(seating.HUMAN_CELLS)
    for seat in seats:
        nxt = seats[(seat.ray + 1) % 24]
        assert seating.is_kin(seat.cell.coords, nxt.cell.coords)
        opposite = seats[(seat.ray + 12) % 24]
        assert opposite.cell.coords == seating.antipode(seat.cell.coords)
        assert opposite.axis is seat.axis
        assert seating.rank(seat.cell.coords) == seating.required_rank(seat.ray)


def test_rose_golden_seats():
    by_hour = {s.hour: s for s in seating.rose_seating()}
    # the poles, on the owner's three hexagram pairs
    assert by_hour[12].cell.luminous == "Loyalty"        # yellow crowns 12h
    assert by_hour[0].cell.luminous == "Integrity"       # purple roots 24h
    assert by_hour[16].cell.luminous == "Composure"
    assert by_hour[4].cell.luminous == "Vigor"
    assert by_hour[20].cell.luminous == "Dignity"
    assert by_hour[8].cell.luminous == "Humility"
    # the corners, on the opposite hexagram — the crown on Sunday's Ruler,
    # the shield on Sunday's Servant
    assert by_hour[18].cell.luminous == "Wise Statesman"
    assert by_hour[6].cell.luminous == "Sacrificial Protector"
    assert by_hour[18].axis.name == "Crown ↔ Shield"
    assert by_hour[14].cell.luminous == "Steady Guardian"
    assert by_hour[2].cell.luminous == "Principled Reformer"
    assert by_hour[22].cell.luminous == "Visionary Founder"
    assert by_hour[10].cell.luminous == "Quiet Devotee"


def test_the_three_primary_axes_stand_at_a_hundred_and_twenty_degrees():
    seats = {s.cell.coords: s for s in seating.rose_seating()}
    angles = sorted(seats[pole].angle_deg for pole in cube.ROSE_POLE_HUE)
    assert angles == [0.0, 60.0, 120.0, 180.0, 240.0, 300.0]
    for axis in seating.HUMAN_AXES:
        if seating.family_of(axis) != "primary":
            continue
        gap = abs(seats[axis.warm.coords].angle_deg
                  - seats[axis.cold.coords].angle_deg)
        assert gap == 180.0


def test_every_hue_triple_is_a_pencil_of_one_pole():
    """Each hue owns three neighbouring rays, and the seating gives each
    triple three cells sharing ONE coordinate — a pole and its household."""
    seats = seating.rose_seating()
    for hue in range(8):
        trio = [s.cell.coords for s in seats if s.hue_index == hue]
        assert len(trio) == 3
        shared = [i for i in range(3)
                  if len({c[i] for c in trio}) == 1 and trio[0][i]]
        assert shared, f"hue {hue} is not a pencil"


def test_the_honest_miss_is_the_whole_activation_pencil():
    """One axis wears its two hues the other way round — and canon's own
    precedent puts the miss on X, the axis a flat dial cannot show. The
    two Sunday hues become Activation's SECOND household, so the doubling
    falls on the axis that already carries the miss."""
    seats = seating.rose_seating()
    at = {s.cell.coords: s.hue_index for s in seats}
    assert at[(-1, 0, 0)] == 1 and at[(1, 0, 0)] == 5        # cyan <-> orange
    for pole in ((0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
        assert at[pole] == cube.ROSE_POLE_HUE[pole]
    for hue, sign in ((2, -1), (6, 1)):                      # red, blue
        assert {s.cell.coords[0] for s in seats if s.hue_index == hue} == {sign}
    assert seating.rays_singing(cube.ROSE_24_SEATING) == 12


# --- the Calendar-12 ------------------------------------------------------------
def test_calendar_seating_is_one_axis_per_month():
    arms = seating.calendar_seating()
    assert len(arms) == 12
    assert sorted(a.month for a in arms) == list(range(1, 13))
    assert [a.wedge for a in arms] == list(range(12))
    assert len({a.axis.name for a in arms}) == 12
    for arm in arms:
        assert arm.wedge == (arm.month - 6) % 12            # the Almanac wheel
        assert {arm.inner, arm.outer} == {arm.axis.cold, arm.axis.warm}


def test_calendar_symmetry_is_the_owners_own_arms():
    """'PRIMARNE 12h, 20h, 4h (standard green, red, blue)' — the three
    face axes on the pure-colour arms, exactly 120° apart; the corners on
    the opposite triangle; the edges on the hexagon between."""
    arms = seating.calendar_seating()
    by_family = {}
    for arm in arms:
        by_family.setdefault(arm.family, []).append(arm.hour)
    assert by_family["primary"] == [12, 20, 4]
    assert by_family["tertiary"] == [16, 0, 8]
    assert by_family["secondary"] == [14, 18, 22, 2, 6, 10]
    for family, step in (("primary", 120.0), ("tertiary", 120.0),
                         ("secondary", 60.0)):
        angles = sorted(a.angle_deg for a in arms if a.family == family)
        assert all(round(b - a, 6) == step for a, b in zip(angles, angles[1:]))


def test_the_inverted_calendar_swaps_the_two_triangles():
    """The owner's second version: the poles move onto the mixed-primary
    arms (cyan, magenta, yellow) and the corners take the pure ones."""
    arms = seating.calendar_seating(inverted=True)
    by_family = {}
    for arm in arms:
        by_family.setdefault(arm.family, []).append(arm.hour)
    assert by_family["primary"] == [16, 0, 8]
    assert by_family["tertiary"] == [12, 20, 4]
    assert by_family["secondary"] == [14, 18, 22, 2, 6, 10]


def test_calendar_golden_arms():
    by_month = {a.month: a for a in seating.calendar_seating()}
    assert by_month[6].axis.name == "Moral Scope"               # June, green
    assert by_month[10].axis.name == "Self-Regard"              # October, red
    assert by_month[2].axis.name == "Activation"                # February, blue
    assert by_month[8].axis.name == "Crown ↔ Shield"            # August, yellow
    assert by_month[12].axis.name == "Vow ↔ Vision"             # December, magenta
    assert by_month[4].axis.name == "Preservation ↔ Revolution"  # April, cyan
    assert by_month[7].axis.name == "Person ↔ Cause"
    assert by_month[9].axis.name == "Servant ↔ Sovereign"
    assert by_month[11].axis.name == "Pragmatism ↔ Idealism"
    assert by_month[1].axis.name == "Hearth ↔ Desert"
    assert by_month[3].axis.name == "Lion ↔ Lamb"
    assert by_month[5].axis.name == "Reason ↔ Emotion"


def test_the_radial_law_puts_restraint_at_the_axle():
    """Activation is the arm's own depth: the axis the flat dial cannot
    show becomes the radius. Where X is silent, Z decides, then Y."""
    by_month = {a.month: a for a in seating.calendar_seating()}
    assert by_month[2].inner.luminous == "Composure"
    assert by_month[2].outer.luminous == "Vigor"
    assert by_month[12].inner.luminous == "Quiet Devotee"        # vow in
    assert by_month[12].outer.luminous == "Visionary Founder"    # vision out
    assert by_month[4].inner.luminous == "Steady Guardian"       # preserve in
    assert by_month[4].outer.luminous == "Principled Reformer"   # revolt out
    assert by_month[8].inner.luminous == "Wise Statesman"        # crown in
    assert by_month[8].outer.luminous == "Sacrificial Protector"  # shield out
    assert by_month[10].inner.luminous == "Humility"             # X silent -> Z
    assert by_month[6].inner.luminous == "Integrity"             # X and Z silent
    for arm in seating.calendar_seating():
        first = next(v for v in (arm.outer.coords[0], arm.outer.coords[2],
                                 arm.outer.coords[1]) if v)
        assert first == 1


# --- the rotation <-> hour question ---------------------------------------------
def _rotations():
    for perm in permutations(range(3)):
        for signs in product((-1, 1), repeat=3):
            m = tuple(tuple((1 if perm[i] == j else 0) * signs[i]
                            for j in range(3)) for i in range(3))
            det = (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
                   - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
                   + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))
            if det == 1:
                yield m


def test_no_rotation_steps_the_hours():
    """Why the rotation<->hour rule does NOT fall out: the cube stands in
    24 ways, but its rotation group has no element of order 24, so no
    single turn can walk the day one hour at a time."""
    rotations = list(_rotations())
    assert len(rotations) == 24
    identity = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    orders = set()
    for m in rotations:
        cur, n = m, 1
        while cur != identity:
            cur = tuple(tuple(sum(cur[i][k] * m[k][j] for k in range(3))
                              for j in range(3)) for i in range(3))
            n += 1
        orders.add(n)
    assert orders == {1, 2, 3, 4}
    assert 24 not in orders


def test_the_dials_half_turn_is_the_inversion_not_a_rotation():
    """Twelve hours across the dial is c -> -c, whose determinant is -1:
    the antipodal law is realised by passing THROUGH the centre, never by
    turning the cube."""
    inversion = ((-1, 0, 0), (0, -1, 0), (0, 0, -1))
    assert inversion not in list(_rotations())
    seats = seating.rose_seating()
    for seat in seats:
        assert seats[(seat.ray + 12) % 24].cell.coords == tuple(
            -v for v in seat.cell.coords)
