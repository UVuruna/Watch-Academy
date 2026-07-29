"""Exports DOMY's Character Cube canon as a MODEL for the sibling 3D
Preview gadget (`Gadgets/3D Preview`, WORKPLAN Session 28).

A model is renderer-neutral JSON — axes, the seats they point at, what
each seat says in each register, and the views that pick who speaks
(the gadget's own `MODELS.md` §A MODEL). **One source of truth (root
Rule #19): every direction, position, colour and name below comes from
`config.cube` / `config.palette` / `core.cube_seating` — nothing is
retyped from the canon.** This module is pure Python — no Qt, no gadget
import at all — so it builds and is testable whether or not the gadget
folder exists on this machine, matching the gadget's own convention
("the model layer imports no Qt at all, so a consumer's exporter script
needs no GUI"). Validating the OUTPUT against the gadget's schema is the
job of whoever imports the gadget — `render.cube_preview3d` (the guarded
bridge) and this project's own tests.

## The direction grammar

A cube coordinate `(x, y, z)` with components in {-1, 0, 1} already IS
the gadget's own direction token, letter for letter: a nonzero x is an
`x` letter, its sign is the letter's sign, and the letters are always
written x, y, z — exactly `config.cube`'s own axis order ("X
Activation, Y Moral Scope, Z Self-Regard") and exactly the gadget's
`axisLetters` order. So `(1, 1, 1)` -> `"+x+y+z"`, `(0, 1, -1)` ->
`"+y-z"`, with no lookup table in between.

## The four registers

The gadget's schema fixes the register vocabulary to exactly `canon` /
`myth` / `historical` / `movie` (`shared/spec.json`'s own switcher
list) — DOMY's own three FIGURE_SETS plus the canon term itself map
onto it with no invented vocabulary:

| Gadget register | DOMY source |
|---|---|
| `canon`      | `CubeCell.luminous` / `.fallen` — the abstract term itself |
| `myth`       | `cube.roster(coords, "archetypal")` — biblical/mythic/classical figures |
| `historical` | `cube.roster(coords, "historical")` — real persons |
| `movie`      | `cube.roster(coords, "modern")` — fantasy/film/comics figures |

## The centre and the two sacred vertices

Doctrine is explicit (CUBE.md §The Sacred Axis / §The Rosters) that
**no persona ever holds the centre, in any register** ("every human
exemplar is ruled by something, The One by nothing"), and that the two
sacred vertices carry exactly ONE named figure each across historical/
modern echoes (Jesus Christ / Maximilian Kolbe / Aslan; The Devil /
Nero / Sauron) — never a second, "fallen-Jesus" or "luminous-Devil"
figure at the same seat. So for these three seats, the figure registers
repeat the ONE name in both the luminous and fallen slots: a true
statement ("this seat's identity does not split by reading"), not a
fabrication, and the only way to satisfy the schema's non-empty-string
rule without inventing a name doctrine never gives.

## Views

The four owner models (primary / secondary / tertiary / cube axes —
WORKPLAN's amended Session 28 page list) mirror
`preview3d.cube_model.DEFAULT_VIEWS` verbatim (documented, not
imported, so this module stays gadget-free — see the comment on
`_OWNER_VIEWS`). On top of them this exporter COMPUTES one solo view
per axis (`axis:<name>`) and one per pole (`pole:<luminous name>`) —
the 3D analogue of `render.cube_diagrams.axis()` / `.pole()`: the
target axis and its seat(s) at full opacity, the rest at the same
`CUBE_DIAGRAM_DIM_OPACITY` the 2D drawer already uses (Rule #5), the
glass shell hidden. A camera perpendicular to the axis keeps it from
foreshortening to a point — the same principle the gadget's own
tertiary view applies to the sacred diagonal.
"""

from config import cube, encyclopedia_ui, palette
from core import cube_seating

MODEL_NAME = "domy-character-cube"
MODEL_LABEL = "The Character Cube"
REGISTERS: tuple[str, ...] = ("canon", "myth", "historical", "movie")

# gadget register -> DOMY's own figure-set name (config.cube.FIGURE_SETS).
_DOMY_SET_FOR_REGISTER = {"myth": "archetypal", "historical": "historical", "movie": "modern"}

_LETTERS = ("x", "y", "z")
_KIND_BY_RANK = {1: "face", 2: "edge", 3: "vertex"}
_KIND_GROUP = {"face": "faces", "edge": "edges", "vertex": "vertices", "centre": "centre"}
_TIER_ORDER = ("primary", "secondary", "tertiary", "sacred")

_SACRED_AXIS = cube_seating.SACRED_AXIS
_SACRED_COLD = _SACRED_AXIS.cold.coords
_SACRED_WARM = _SACRED_AXIS.warm.coords
_SACRED_SEAT_AT = {_SACRED_COLD: "Jesus Christ", _SACRED_WARM: "The Devil"}

# The six poles, in the order `shared/spec.json`'s own `faceOrder` names —
# DOMY's real pole hues dressing the glass shell, instead of the gadget's
# generic demo palette (root Rule #19: palette-derived, never invented).
_FACE_ORDER: tuple[tuple[int, int, int], ...] = (
    (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1),
)


# ---- the direction grammar ---------------------------------------------------


def _token(coords: tuple[int, int, int]) -> str:
    """A coordinate to the gadget's own direction token — see the module
    docstring: DOMY's (x, y, z) order already IS the gadget's letter
    order, so this is a straight transcription, never a lookup table."""
    return "".join(
        f"{'+' if value > 0 else '-'}{letter}"
        for letter, value in zip(_LETTERS, coords)
        if value
    )


def _is_positive(coords: tuple[int, int, int]) -> bool:
    """Whether this end is the one an axis's id is named after — the
    gadget's own convention: the first nonzero letter, in x/y/z order,
    is written positive."""
    return next(value for value in coords if value) > 0


def _positive_coords(axis: cube.CubeAxis) -> tuple[int, int, int]:
    return axis.cold.coords if _is_positive(axis.cold.coords) else axis.warm.coords


def _tier_of(axis: cube.CubeAxis) -> str:
    return "sacred" if axis is _SACRED_AXIS else cube_seating.family_of(axis)


# ---- names --------------------------------------------------------------------


def _figure_names(coords: tuple[int, int, int]) -> dict[str, tuple[str, str]]:
    """register -> (luminous, fallen) FIGURE names, for the three
    figure-set registers only (canon is handled in `_seat_names`)."""
    sacred_seat = _SACRED_SEAT_AT.get(coords)
    if coords == (0, 0, 0) or sacred_seat is not None:
        # The centre and the two sacred vertices: one persona per seat,
        # repeated in both slots — see the module docstring.
        result: dict[str, tuple[str, str]] = {}
        for register, domy_set in _DOMY_SET_FOR_REGISTER.items():
            name = (
                cube.sacred_figure(sacred_seat, domy_set)
                if sacred_seat is not None
                else cube.THE_ONE_SEAT
            )
            result[register] = (name, name)
        return result
    return {
        register: cube.roster(coords, domy_set)
        for register, domy_set in _DOMY_SET_FOR_REGISTER.items()
    }


def _seat_names(coords: tuple[int, int, int]) -> dict[str, dict[str, str]]:
    """register -> {luminous, fallen} for one of the model's 27 cells —
    shared by both `axes[].ends[].names` and `cells[].names`, since an
    axis end and its cell are the same seat (Rule #5, one computation)."""
    cell = cube_seating.CELL_BY_COORDS.get(coords)
    canon_luminous = cell.luminous if cell is not None else cube.THE_ONE.luminous
    # The One's own fallen reading is empty by doctrine ("no fall
    # touches him") — the schema demands a non-empty string, so the
    # honest fill is the SAME name repeated, not an invented word.
    canon_fallen = (cell.fallen if cell is not None else "") or canon_luminous
    names = {"canon": {"luminous": canon_luminous, "fallen": canon_fallen}}
    for register, (luminous, fallen) in _figure_names(coords).items():
        names[register] = {"luminous": luminous, "fallen": fallen}
    return names


# ---- axes and cells -------------------------------------------------------------


def _end(coords: tuple[int, int, int]) -> dict:
    return {
        "direction": _token(coords),
        "color": cube_seating.cell_color(coords),
        "names": _seat_names(coords),
    }


def _axis_entry(axis: cube.CubeAxis) -> dict:
    positive = _positive_coords(axis)
    negative = tuple(-component for component in positive)
    return {
        "id": _token(positive),
        "tier": _tier_of(axis),
        "name": axis.name,
        "ends": [_end(positive), _end(negative)],
    }


def _cell_entry(coords: tuple[int, int, int], half: float) -> dict:
    kind = _KIND_BY_RANK[sum(1 for value in coords if value)]
    return {
        "id": _token(coords),
        "kind": kind,
        "position": [component * half for component in coords],
        "color": cube_seating.cell_color(coords),
        "names": _seat_names(coords),
    }


def _cell_entries(size: float) -> list[dict]:
    half = size / 2
    entries = [
        _cell_entry(end.coords, half)
        for axis in cube.AXES
        for end in (axis.cold, axis.warm)
    ]
    entries.append({
        "id": "centre",
        "kind": "centre",
        "position": [0.0, 0.0, 0.0],
        "color": cube_seating.cell_color((0, 0, 0)),
        "names": _seat_names((0, 0, 0)),
    })
    return entries


# ---- views ------------------------------------------------------------------
# Full group PATHS as the gadget's own scene tree documents them
# (MODELS.md §The Tree a Model Becomes) — hardcoded from that written
# contract rather than imported, so this module stays gadget-free.

_GROUP_PATH: dict[str, str] = {
    **{tier: f"axes/{tier}" for tier in _TIER_ORDER},
    **{kind: f"cells/{group}" for kind, group in _KIND_GROUP.items()},
    "glass": "glass",
}


def _expand(name: str, label: str, camera, groups: dict[str, float]) -> dict:
    """Short group-name opacities -> every group's full path, explicitly
    (a group this view does not mention is set to 0 rather than left
    out, so switching views never leaves one lit from the view before
    it — the same rule the gadget's own `_expand_view` follows)."""
    opacity = {path: 0.0 for path in _GROUP_PATH.values()}
    for group, alpha in groups.items():
        opacity[_GROUP_PATH[group]] = float(alpha)
    return {"name": name, "label": label, "camera": camera, "opacity": opacity}


# The four owner models. These numbers MIRROR
# `preview3d.cube_model.DEFAULT_VIEWS` verbatim (the gadget's own demo
# view weights) — transcribed rather than imported so this module needs
# no gadget/Qt dependency; re-compare the two if the gadget's demo view
# weights ever change.
_OWNER_VIEWS: tuple[dict, ...] = (
    _expand("primary", "Primary Axes", "+x+y+z", {"primary": 1.0}),
    _expand("secondary", "Secondary Axes", "+x+y+z",
            {"primary": 0.18, "secondary": 1.0}),
    _expand("tertiary", "Tertiary Axes", "-x+y",
            {"primary": 0.15, "tertiary": 1.0, "sacred": 1.0,
             "vertex": 0.85, "centre": 1.0}),
    _expand("cube", "The Cube", "+x+y+z", {
        "primary": 0.55, "secondary": 0.5, "tertiary": 0.5, "sacred": 0.85,
        "face": 1.0, "edge": 1.0, "vertex": 1.0, "centre": 1.0,
        "glass": encyclopedia_ui.CUBE_MODEL_GLASS_OPACITY,
    }),
)


def _cross(a: tuple[float, float, float], b: tuple[float, float, float]) -> list[float]:
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def _side_camera(coords: tuple[int, int, int]) -> list[float]:
    """A camera direction perpendicular to `coords` — an axis read
    side-on shows its true length instead of foreshortening to a point,
    the same principle the gadget's own tertiary view applies to the
    sacred diagonal."""
    direction = tuple(float(value) for value in coords)
    # (0,1,0) is parallel to the Moral Scope axis alone; every other
    # axis is safely crossed against it.
    reference = (1.0, 0.0, 0.0) if direction[0] == 0.0 and direction[2] == 0.0 else (0.0, 1.0, 0.0)
    return _cross(direction, reference)


def _lit_view(name: str, camera, axis: cube.CubeAxis, lit: frozenset) -> dict:
    """One axis and its lit seat(s) at full opacity, the other twelve
    axes and the other 25 cells faint (`CUBE_DIAGRAM_DIM_OPACITY`, the
    SAME constant the 2D `axis()`/`pole()` drawers dim by), the glass
    shell hidden — the 3D analogue of those two drawers."""
    dim = encyclopedia_ui.CUBE_DIAGRAM_DIM_OPACITY
    opacity = {"glass": 0.0}
    for other in cube.AXES:
        path = f"{_GROUP_PATH[_tier_of(other)]}/axis:{_token(_positive_coords(other))}"
        opacity[path] = 1.0 if other is axis else dim
    for other_axis in cube.AXES:
        for end in (other_axis.cold, other_axis.warm):
            kind = _KIND_BY_RANK[sum(1 for value in end.coords if value)]
            path = f"{_GROUP_PATH[kind]}/cell:{_token(end.coords)}"
            opacity[path] = 1.0 if end.coords in lit else dim
    opacity[f"{_GROUP_PATH['centre']}/cell:centre"] = 1.0
    return {"name": name, "camera": camera, "opacity": opacity}


def _axis_solo_view(axis: cube.CubeAxis) -> dict:
    lit = frozenset({axis.cold.coords, axis.warm.coords})
    camera = _side_camera(_positive_coords(axis))
    return _lit_view(f"axis:{axis.name}", camera, axis, lit)


def _pole_solo_views(axis: cube.CubeAxis) -> list[dict]:
    return [
        _lit_view(f"pole:{end.luminous}", _side_camera(end.coords), axis,
                  frozenset({end.coords}))
        for end in (axis.cold, axis.warm)
    ]


def _views() -> list[dict]:
    views = list(_OWNER_VIEWS)
    views.extend(_axis_solo_view(axis) for axis in cube.AXES)
    for axis in cube.AXES:
        views.extend(_pole_solo_views(axis))
    return views


# ---- the model ----------------------------------------------------------------


def build_model(size: float = 1.0) -> dict:
    """The Character Cube as a gadget-schema MODEL dict — 13 axes, 26
    seats + the centre, `REGISTERS` × two readings each, and one view
    per owner model plus one solo view per axis/pole. Not validated
    here (this module stays gadget-free) — the caller validates against
    `shared/model_schema.json` (`render.cube_preview3d` does, guarded;
    so does this project's own test)."""
    return {
        "name": MODEL_NAME,
        "label": MODEL_LABEL,
        "root": "model",
        "size": float(size),
        "registers": list(REGISTERS),
        "sacred": _token(_positive_coords(_SACRED_AXIS)),
        "axes": [_axis_entry(axis) for axis in cube.AXES],
        "cells": _cell_entries(size),
        "glass": {
            "opacity": encyclopedia_ui.CUBE_MODEL_GLASS_OPACITY,
            "colors": [cube_seating.cell_color(coords) for coords in _FACE_ORDER],
        },
        "views": _views(),
    }
