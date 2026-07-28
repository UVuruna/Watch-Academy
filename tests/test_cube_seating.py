"""The Seating geometry (WORKPLAN Session 26, CUBE.md §The Seatings):
the Calendar-12 arm-per-axis wheel and the Rose-24 seat-per-ray ring.

Every seat is pinned golden, and the Rose's ring is not merely compared
against the sealed constant — the whole exhaustive search is RE-RUN here,
law by law, so the constant can never drift away from the argument that
produced it.
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


def test_the_twelve_human_axes_fall_into_four_families_of_three():
    families = {}
    for axis in seating.HUMAN_AXES:
        families.setdefault(seating.family_of(axis), []).append(axis)
    assert sorted(families) == ["concord", "discord", "primary", "tertiary"]
    assert all(len(group) == 3 for group in families.values())
    # and each family carries one axis per index — the 4 x 3 grid
    for group in families.values():
        assert sorted(seating.index_of(a) for a in group) == ["x", "y", "z"]


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


# --- the exhaustive search ------------------------------------------------------
@pytest.fixture(scope="module")
def rings():
    return seating.antipodal_rings()


def test_the_search_finds_twenty_two_distinct_cycles(rings):
    assert len(rings) == 1056                # 22 cycles x 24 rotations x 2 ways
    assert len(rings) % 48 == 0
    for ring in rings:
        assert len(set(ring)) == 24
        for ray in range(24):
            assert seating.is_kin(ring[ray], ring[(ray + 1) % 24])
            assert ring[(ray + 12) % 24] == seating.antipode(ring[ray])


def test_the_six_poles_can_never_all_wear_their_sealed_hue(rings):
    """The honest miss: four of six is the ceiling, and the two that miss
    are always one axis's own pair — exactly the Prophecy wheel's case."""
    assert max(seating.poles_oriented(r) for r in rings) == 4
    assert {seating.poles_oriented(r) for r in rings} <= {0, 2, 4}


def test_the_five_laws_leave_exactly_one_seating(rings):
    held = [r for r in rings if seating.diagonals_held(r) == 3]
    assert len(held) == 28                    # all three axes on their diagonals
    oriented = [r for r in held if seating.poles_oriented(r) == 4]
    assert len(oriented) == 14
    sunday = [r for r in oriented if r[6] == (-1, 0, 1)]
    assert len(sunday) == 2                   # the Sovereign on the Ruler's red
    solved = seating.solve_rose_seating()
    assert len(solved) == 1
    assert solved[0] == cube.ROSE_24_SEATING


def test_a_perfect_singing_ring_exists_but_costs_a_sealed_table(rings):
    """Recorded so no later session re-opens it: 6 rings make every ray
    sing, and every one of them pays by moving a primary axis ONTO the
    Sabbath diagonal, which CUBE.md §The Sabbath axis forbids."""
    perfect = [r for r in rings if seating.rays_singing(r) == 18]
    assert len(perfect) == 6
    assert all(seating.diagonals_held(r) < 3 for r in perfect)


# --- the Rose-24 ----------------------------------------------------------------
def test_rose_seating_obeys_both_hard_laws():
    seats = seating.rose_seating()
    assert len(seats) == 24
    assert {s.cell.coords for s in seats} == set(seating.HUMAN_CELLS)
    for seat in seats:
        nxt = seats[(seat.ray + 1) % 24]
        assert seating.is_kin(seat.cell.coords, nxt.cell.coords)
        opposite = seats[(seat.ray + 12) % 24]
        assert opposite.cell.coords == seating.antipode(seat.cell.coords)
        assert opposite.axis is seat.axis
        assert seat.hour == (12 + seat.ray) % 24


def test_rose_seating_golden_seats():
    by_hour = {s.hour: s for s in seating.rose_seating()}
    assert by_hour[12].cell.luminous == "Steadfastness"      # the Judge's noon
    assert by_hour[12].cell.fallen == "Machination"
    assert by_hour[0].cell.luminous == "Reform"              # the Creator's midnight
    assert by_hour[18].cell.luminous == "Self-Mastery"       # SUN Ruler, red
    assert by_hour[6].cell.luminous == "Diligence"           # SUN Servant, blue
    assert by_hour[18].axis.name == "Servant ↔ Sovereign"
    assert by_hour[15].cell.luminous == "Composure"
    assert by_hour[3].cell.luminous == "Vigor"
    assert by_hour[21].cell.luminous == "Dignity"
    assert by_hour[9].cell.luminous == "Humility"
    assert by_hour[11].cell.luminous == "Loyalty"
    assert by_hour[23].cell.luminous == "Integrity"


def test_the_rose_ring_alternates_edge_and_pole_or_corner():
    """The parity theorem, seen on the dial: every other ray is an
    edge-person — six is man's number."""
    seats = seating.rose_seating()
    ranks = [seating.rank(s.cell.coords) for s in seats]
    assert all(r == 2 for i, r in enumerate(ranks) if not i % 2)
    assert all(r in (1, 3) for i, r in enumerate(ranks) if i % 2)
    assert ranks.count(2) == 12                 # twelve edge-people


def test_every_hue_triple_is_a_pencil_of_one_pole():
    """Each hue owns three neighbouring rays, and the seating gives each
    triple three cells sharing ONE coordinate — the six cube hues hold
    their own pole with its two neighbours, the Sabbath's red and blue an
    edge with its two corners."""
    seats = seating.rose_seating()
    for hue in range(8):
        trio = [s.cell.coords for s in seats if s.hue_index == hue]
        assert len(trio) == 3
        shared = [i for i in range(3)
                  if len({c[i] for c in trio}) == 1 and trio[0][i]]
        assert shared, f"hue {hue} is not a pencil"


def test_the_honest_miss_is_the_whole_activation_pencil():
    """One axis wears its two hues the other way round — and canon's own
    precedent puts the miss on X, the axis a flat dial cannot show."""
    seats = seating.rose_seating()
    at = {s.cell.coords: s.hue_index for s in seats}
    assert at[(-1, 0, 0)] == 1 and at[(1, 0, 0)] == 5        # cyan <-> orange
    for pole in ((0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
        assert at[pole] == cube.ROSE_POLE_HUE[pole]
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


def test_opposite_months_carry_dual_families_at_the_same_index():
    """June faces December and March faces September: face against
    vertex (the cube's own duality), concord against discord."""
    by_wedge = {a.wedge: a for a in seating.calendar_seating()}
    duals = {("primary", "tertiary"), ("concord", "discord")}
    for wedge in range(6):
        here, across = by_wedge[wedge], by_wedge[wedge + 6]
        assert here.index == across.index
        assert frozenset({here.family, across.family}) in {
            frozenset(pair) for pair in duals}


def test_calendar_golden_arms():
    by_month = {a.month: a for a in seating.calendar_seating()}
    assert by_month[6].axis.name == "Vow ↔ Vision"              # summer solstice
    assert by_month[7].axis.name == "Preservation ↔ Revolution"
    assert by_month[8].axis.name == "Crown ↔ Shield"
    assert by_month[9].axis.name == "Servant ↔ Sovereign"       # autumn equinox
    assert by_month[10].axis.name == "Person ↔ Cause"
    assert by_month[11].axis.name == "Pragmatism ↔ Idealism"
    assert by_month[12].axis.name == "Moral Scope"              # winter solstice
    assert by_month[1].axis.name == "Activation"
    assert by_month[2].axis.name == "Self-Regard"
    assert by_month[3].axis.name == "Lion ↔ Lamb"               # spring equinox
    assert by_month[4].axis.name == "Hearth ↔ Desert"
    assert by_month[5].axis.name == "Reason ↔ Emotion"


def test_the_radial_law_puts_restraint_at_the_axle():
    """Activation is the arm's own depth: the axis the flat dial cannot
    show becomes the radius. Where X is silent, Z decides, then Y."""
    by_month = {a.month: a for a in seating.calendar_seating()}
    assert by_month[1].inner.luminous == "Composure"
    assert by_month[1].outer.luminous == "Vigor"
    assert by_month[6].inner.luminous == "Quiet Devotee"         # vow in
    assert by_month[6].outer.luminous == "Visionary Founder"     # vision out
    assert by_month[7].inner.luminous == "Steady Guardian"       # preserve in
    assert by_month[7].outer.luminous == "Principled Reformer"   # revolt out
    assert by_month[8].inner.luminous == "Wise Statesman"        # crown in
    assert by_month[8].outer.luminous == "Sacrificial Protector"  # shield out
    assert by_month[2].inner.luminous == "Humility"              # X silent -> Z
    assert by_month[12].inner.luminous == "Integrity"            # X and Z silent
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
