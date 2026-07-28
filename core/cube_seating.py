"""The Character Cube's pure geometry and the two seatings solved with
it (CUBE.md §The Seatings, Session 26).

The ONE-GRADE LAW rules both wheels: two cells are kin when they differ
in exactly one coordinate by exactly one grade, so one step around a
wheel changes exactly ONE axis by ONE grade. Everything else — families,
indices, ray hues, the whole Calendar-12 — is derived from coordinates
(root Rule 19); only the Rose-24 ring, the survivor of an exhaustive
search, is recorded in config and re-proved by `solve_rose_seating()`.
"""

from dataclasses import dataclass

from config import cube

Coords = tuple[int, int, int]

RAY_COUNT = 24
RAY_STEP_DEG = 360.0 / RAY_COUNT        # the three octa stars, 15° apart
HALF_TURN = RAY_COUNT // 2              # ray k and ray k+12 are antipodes
STAR_OF_RAY = ("0", "+15", "-15")       # ray % 3 -> which star owns it
AXIS_LETTERS = "xyz"


# --- cells and axes ------------------------------------------------------------
def antipode(cell: Coords) -> Coords:
    return (-cell[0], -cell[1], -cell[2])


def axis_key(cell: Coords) -> Coords:
    """The unsigned direction — the axis a cell ends."""
    return min(cell, antipode(cell))


def is_kin(a: Coords, b: Coords) -> bool:
    """THE ONE-GRADE LAW: one coordinate moves, and only by one grade."""
    return sorted(abs(a[i] - b[i]) for i in range(3)) == [0, 0, 1]


def rank(cell: Coords) -> int:
    """1 face, 2 edge, 3 vertex — the count of committed axes."""
    return sum(1 for v in cell if v)


def family_of(axis: cube.CubeAxis) -> str:
    """The four families of three the twelve human axes fall into:
    PRIMARY (the bare face axes), CONCORD and DISCORD (edge axes joining
    like-signed and opposite-signed poles), TERTIARY (vertex axes)."""
    cell = axis.warm.coords
    if rank(cell) == 1:
        return "primary"
    if rank(cell) == 3:
        return "tertiary"
    return "concord" if sum(cell) != 0 else "discord"


def index_of(axis: cube.CubeAxis) -> str:
    """The coordinate that NAMES an axis — its own for a face axis, the
    silent one for an edge axis, the odd-signed one for a vertex axis.
    The Sacred Axis is the vertex axis with no odd coordinate, which is
    why it alone returns "" and leaves the human circle."""
    cell = axis.warm.coords
    if rank(cell) == 1:
        return AXIS_LETTERS[next(i for i, v in enumerate(cell) if v)]
    if rank(cell) == 2:
        return AXIS_LETTERS[next(i for i, v in enumerate(cell) if not v)]
    odd = [i for i in range(3) if cell[i] != cell[(i + 1) % 3]
           and cell[i] != cell[(i + 2) % 3]]
    return AXIS_LETTERS[odd[0]] if odd else ""


SACRED_AXIS = next(a for a in cube.AXES if index_of(a) == "")
HUMAN_AXES: tuple[cube.CubeAxis, ...] = tuple(
    a for a in cube.AXES if a is not SACRED_AXIS
)
HUMAN_CELLS: tuple[Coords, ...] = tuple(
    end.coords for axis in HUMAN_AXES for end in (axis.cold, axis.warm)
)
CELL_BY_COORDS = {
    end.coords: end for axis in cube.AXES for end in (axis.cold, axis.warm)
}
AXIS_BY_KEY = {axis_key(a.warm.coords): a for a in cube.AXES}


# --- the Rose's rays -----------------------------------------------------------
def ray_hour(ray: int) -> int:
    """Ray 0 points at 12h and every ray is 15° clockwise of the last —
    the dial convention (noon top, midnight bottom)."""
    return (12 + ray) % 24


def ray_star(ray: int) -> str:
    return STAR_OF_RAY[ray % 3]


def ray_hue_index(ray: int) -> int:
    """The Rose is three identical octa stars 15° apart, each wearing the
    same eight hues, so every hue owns a TRIPLE of neighbouring rays —
    its own star-0 arm and the two rays beside it."""
    arm = {0: ray // 3, 1: (ray - 1) // 3, 2: (ray + 1) // 3}[ray % 3]
    return arm % 8


def pole_hues(cell: Coords) -> set[int]:
    """The hues of the poles this cell carries — one for a face, two for
    an edge, three for a vertex."""
    return {cube.ROSE_POLE_HUE[tuple(v if i == j else 0 for j in range(3))]
            for i, v in enumerate(cell) if v}


# --- the exhaustive search ------------------------------------------------------
def antipodal_rings() -> list[tuple[Coords, ...]]:
    """Every seating of the 24 human cells on the 24 rays that obeys BOTH
    hard laws: the one-grade law around the whole ring, and the antipodal
    law (ray k and ray k+12 end one axis). Ray k+12 is forced to be ray
    k's antipode, so the search only walks rays 0..11 and closes the ring
    against the first ray's antipode."""
    rings: list[tuple[Coords, ...]] = []
    cells = sorted(HUMAN_CELLS)

    def walk(path: list[Coords], axes: set[Coords]) -> None:
        if len(path) == HALF_TURN:
            if is_kin(path[-1], antipode(path[0])):
                rings.append(tuple(path) + tuple(antipode(c) for c in path))
            return
        for cell in cells:
            key = axis_key(cell)
            if key in axes or (path and not is_kin(path[-1], cell)):
                continue
            path.append(cell)
            axes.add(key)
            walk(path, axes)
            path.pop()
            axes.remove(key)

    walk([], set())
    return rings


def diagonals_held(ring: tuple[Coords, ...]) -> int:
    """How many of the three primary axes hold their own sealed hue PAIR
    (the two poles may still be the wrong way round)."""
    at = {cell: ray for ray, cell in enumerate(ring)}
    held = 0
    for pole, hue in cube.ROSE_POLE_HUE.items():
        if pole > antipode(pole):
            continue
        wanted = {hue, cube.ROSE_POLE_HUE[antipode(pole)]}
        if {ray_hue_index(at[pole]), ray_hue_index(at[antipode(pole)])} == wanted:
            held += 1
    return held


def poles_oriented(ring: tuple[Coords, ...]) -> int:
    """How many of the six poles sit on exactly their own sealed hue."""
    at = {cell: ray for ray, cell in enumerate(ring)}
    return sum(1 for pole, hue in cube.ROSE_POLE_HUE.items()
               if ray_hue_index(at[pole]) == hue)


def rays_singing(ring: tuple[Coords, ...]) -> int:
    """The Prophecy wheel's second wish, generalised: a ray SINGS when its
    own hue is one of the poles its seat carries. The six Sabbath rays
    (red and blue) are not cube hues and can never sing, so 18 is the
    ceiling."""
    return sum(1 for ray, cell in enumerate(ring)
               if ray_hue_index(ray) in pole_hues(cell))


# The Sunday law and the cross doctrine, as coordinates: the Sovereign
# (Self-Mastery) on the Ruler's red 18h, and Machination — the plot
# exposed before the Judge — on the Judge's own noon.
_SOVEREIGN = (-1, 0, 1)
_MACHINATION = (-1, 1, 0)


def solve_rose_seating() -> list[tuple[Coords, ...]]:
    """The five laws applied in order of authority. Returns every ring
    that survives all of them — one."""
    rings = antipodal_rings()
    best = [r for r in rings if diagonals_held(r) == 3]
    top = max(poles_oriented(r) for r in best)
    best = [r for r in best if poles_oriented(r) == top]
    best = [r for r in best if r[6] == _SOVEREIGN]          # the Sunday law
    return [r for r in best if r[0] == _MACHINATION]        # the cross doctrine


# --- the two seatings -----------------------------------------------------------
@dataclass(frozen=True)
class RoseSeat:
    """One ray of the Rose-24."""

    ray: int
    hour: int
    star: str
    hue_index: int
    cell: cube.CubeCell
    axis: cube.CubeAxis

    @property
    def angle_deg(self) -> float:
        return self.ray * RAY_STEP_DEG

    @property
    def sings(self) -> bool:
        return self.hue_index in pole_hues(self.cell.coords)


@dataclass(frozen=True)
class CalendarArm:
    """One arm of the Calendar-12 — a whole axis, its two ends by radius."""

    month: int
    wedge: int
    season: int
    family: str
    index: str
    axis: cube.CubeAxis
    inner: cube.CubeCell
    outer: cube.CubeCell

    @property
    def angle_deg(self) -> float:
        """The Almanac wedge's centre — June's wedge is centred on top."""
        return self.wedge * 30.0


def rose_seating() -> tuple[RoseSeat, ...]:
    """The sealed Rose-24 (config.cube.ROSE_24_SEATING) as seats."""
    return tuple(
        RoseSeat(ray, ray_hour(ray), ray_star(ray), ray_hue_index(ray),
                 CELL_BY_COORDS[coords], AXIS_BY_KEY[axis_key(coords)])
        for ray, coords in enumerate(cube.ROSE_24_SEATING)
    )


def _outward(axis: cube.CubeAxis) -> cube.CubeCell:
    """THE RADIAL LAW: Activation is the arm's own depth — the axis the
    flat dial cannot show becomes the radius, Restraint at the axle and
    Mobilization at the rim. Where X is silent, Z decides (Self-Effacement
    in, Self-Exaltation out), then Y."""
    for i in (0, 2, 1):
        if axis.warm.coords[i]:
            return axis.warm if axis.warm.coords[i] > 0 else axis.cold
    raise ValueError(f"{axis.name} has no direction")     # only The One


def calendar_seating() -> tuple[CalendarArm, ...]:
    """The Calendar-12, computed from the two laws in config: the family
    picks the season, the index the month within it."""
    arms = []
    for axis in HUMAN_AXES:
        family = family_of(axis)
        index = index_of(axis)
        season = cube.CALENDAR_SEASON_BY_FAMILY[family]
        wedge = season * 3 + cube.CALENDAR_POSITION_BY_INDEX[index]
        outer = _outward(axis)
        inner = axis.cold if outer is axis.warm else axis.warm
        arms.append(CalendarArm(
            month=(wedge + 5) % 12 + 1, wedge=wedge, season=season,
            family=family, index=index, axis=axis, inner=inner, outer=outer,
        ))
    return tuple(sorted(arms, key=lambda arm: arm.wedge))
