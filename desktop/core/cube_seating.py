"""The Character Cube's pure geometry and the two seatings solved with
it (CUBE.md §The Seatings, Session 26).

The ONE-GRADE LAW rules both wheels: two cells are kin when they differ
in exactly one coordinate by exactly one grade, so one step around a
wheel changes exactly ONE axis by ONE grade. Everything else — families,
indices, ray hues, the whole Calendar-12 — is derived from coordinates
(root Rule 19); only the Rose-24 ring, the survivor of an exhaustive
search, is recorded in config and re-proved by `solve_rose_seating()`.

`cell_color()` and `find_pole()` (Session 28, the 3D Preview exporter)
are the SAME derivations `render.cube_diagrams` already drew with —
extracted here, Qt-free, so the 2D diagrams and the 3D model export
read one computation instead of two (root Rule #5).
"""

from dataclasses import dataclass

from config import cube, palette

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
    """The three families the twelve human axes fall into, by how many
    axes each commits: PRIMARY (3 face axes), SECONDARY (6 edge axes),
    TERTIARY (3 human vertex axes). 3 + 6 + 3 is what makes the symmetry
    law possible — two opposed triangles with a hexagon between them."""
    return {1: "primary", 2: "secondary", 3: "tertiary"}[rank(axis.warm.coords)]


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


# --- the symmetry law -----------------------------------------------------------
# THE OWNER'S FIRST LAW (2026-07-28): symmetry decides which KIND of axis
# stands where; symbolism only decides which axis of that kind. On the
# Rose the three face axes take the hexagram rays (12h-24h, 4h-16h,
# 20h-8h — the owner's own three pairs), the three human vertex axes take
# the opposite hexagram, and the six edge axes fill the odd rays.
RANK_BY_RAY = {0: 1, 2: 3}          # ray % 4 -> required rank; else 2, an edge


def required_rank(ray: int) -> int:
    return RANK_BY_RAY.get(ray % 4, 2)


def is_symmetric(ring: tuple[Coords, ...]) -> bool:
    return all(rank(cell) == required_rank(ray) for ray, cell in enumerate(ring))


# --- the exhaustive search ------------------------------------------------------
def antipodal_rings(symmetric: bool = True) -> list[tuple[Coords, ...]]:
    """Every seating of the 24 human cells on the 24 rays that obeys the
    hard laws: the one-grade law around the whole ring, the antipodal law
    (ray k and ray k+12 end one axis) and — unless `symmetric` is off, as
    the tests do to measure what symmetry costs — the symmetry law. Ray
    k+12 is forced to be ray k's antipode, so the search only walks rays
    0..11 and closes the ring against the first ray's antipode."""
    rings: list[tuple[Coords, ...]] = []
    cells = sorted(HUMAN_CELLS)

    def walk(path: list[Coords], axes: set[Coords]) -> None:
        if len(path) == HALF_TURN:
            if is_kin(path[-1], antipode(path[0])):
                rings.append(tuple(path) + tuple(antipode(c) for c in path))
            return
        ray = len(path)
        for cell in cells:
            key = axis_key(cell)
            if key in axes or (path and not is_kin(path[-1], cell)):
                continue
            if symmetric and rank(cell) != required_rank(ray):
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
    own hue is one of the poles its seat carries. Red and blue are not
    cube hues, so only a cell that reaches them by its own poles can make
    those six rays sing."""
    return sum(1 for ray, cell in enumerate(ring)
               if ray_hue_index(ray) in pole_hues(cell))


# The two symbolism choices, as coordinates. THE CROWN ON THE RULER:
# Sunday's two seats are the Ruler on red 18h and the Servant on blue
# 06h, and the corner axis the symmetry law puts there is Crown ↔ Shield
# — so the Wise Statesman (the crown) takes the Ruler and the Sacrificial
# Protector (the shield) the Servant. THE THRONE AT NOON: Loyalty crowns
# 12h in yellow and Integrity roots 24h in purple, which is the Rose's own
# sealed sentence about its two ends.
_CROWN = (-1, -1, 1)                # Wise Statesman
_LOYALTY = (0, 1, 0)


def solve_rose_seating() -> list[tuple[Coords, ...]]:
    """The laws in order of authority — symmetry and kinship first, then
    colour, then symbolism. Returns every ring that survives — one."""
    rings = antipodal_rings()                               # symmetry + kinship
    best = [r for r in rings if diagonals_held(r) == 3]     # the colour law
    top = max(poles_oriented(r) for r in best)
    best = [r for r in best if poles_oriented(r) == top]
    best = [r for r in best if r[6] == _CROWN]              # the crown on the Ruler
    best = [r for r in best if r[0] == _LOYALTY]            # the throne at noon
    # Of the two that remain, one seats the Activation households on the
    # two Sunday hues as well as their own — so the doubling falls on the
    # axis that already carries the honest miss, instead of muddying a
    # second axis. That one is the seating.
    return [r for r in best
            if len({c[0] for ray, c in enumerate(r) if ray_hue_index(ray) == 2}) == 1]


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
    family: str
    axis: cube.CubeAxis
    inner: cube.CubeCell
    outer: cube.CubeCell

    @property
    def angle_deg(self) -> float:
        """The Almanac wedge's centre — June's wedge is centred on top."""
        return self.wedge * 30.0

    @property
    def hour(self) -> int:
        return (12 + 2 * self.wedge) % 24


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


def calendar_seating(inverted: bool = False) -> tuple[CalendarArm, ...]:
    """The Calendar-12. THE SYMMETRY LAW picks the arms: the three face
    axes take one equilateral triangle of wedges, the three vertex axes
    the opposite triangle, the six edge axes the hexagon between them —
    the hexagram. `inverted` swaps the two triangles (the owner's second
    version: the poles move off the pure-colour arms onto the mixed
    ones). Only WHICH axis of a family takes which of its own arms is
    symbolism, and that order lives in config."""
    wedges = dict(cube.CALENDAR_WEDGES_BY_FAMILY)
    if inverted:
        wedges["primary"], wedges["tertiary"] = (wedges["tertiary"],
                                                 wedges["primary"])
    arms = []
    for family, names in cube.CALENDAR_AXIS_ORDER.items():
        for wedge, name in zip(wedges[family], names):
            axis = next(a for a in HUMAN_AXES if a.name == name)
            outer = _outward(axis)
            inner = axis.cold if outer is axis.warm else axis.warm
            arms.append(CalendarArm(
                month=(wedge + 5) % 12 + 1, wedge=wedge, family=family,
                axis=axis, inner=inner, outer=outer,
            ))
    return tuple(sorted(arms, key=lambda arm: arm.wedge))


# --- colour and pole lookup (shared by the 2D diagrams and the 3D export) -------
def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


def _rgb_to_hex(red: int, green: int, blue: int) -> str:
    return f"#{red:02X}{green:02X}{blue:02X}"


def cell_color(coords: Coords) -> str:
    """A cell's own hex colour, pure hex arithmetic (Qt-free): the six
    face poles wear their sealed Rose hue (`cube.ROSE_POLE_HUE`), the
    centre wears the dial's accent, every other cell is the average of
    the poles it stands between — computed, so a re-tuned palette moves
    the whole cube (both its 2D diagrams and its 3D model) at once."""
    if coords == (0, 0, 0):
        return palette.THEME_COLORS["accent"]
    index = cube.ROSE_POLE_HUE.get(coords)
    if index is not None:
        return palette.ROSE_PALETTE[index]
    channels = [0, 0, 0]
    count = 0
    for axis, value in enumerate(coords):
        if value == 0:
            continue
        pole = [0, 0, 0]
        pole[axis] = value
        pole_index = cube.ROSE_POLE_HUE.get(tuple(pole))
        if pole_index is None:
            continue
        for component, channel in enumerate(_hex_to_rgb(palette.ROSE_PALETTE[pole_index])):
            channels[component] += channel
        count += 1
    if not count:
        return palette.THEME_COLORS["accent"]
    return _rgb_to_hex(*(channel // count for channel in channels))


def find_pole(name: str) -> tuple[cube.CubeAxis, cube.CubeCell] | None:
    """The axis and the ONE end whose luminous name is `name` — e.g.
    `find_pole("Composure")` returns (the Activation axis, its cold
    end) — or None when no cell carries that name."""
    return next(
        ((axis, end) for axis in cube.AXES for end in (axis.cold, axis.warm)
         if end.luminous == name),
        None,
    )
