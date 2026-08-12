"""THE COLOUR LAW — pinned (owner verdict 2026-07-29).

The owner went looking for a colour in `config/defaults.py` and found a
catastrophe: 77 colour-bearing names scattered between line 48 and line
3526, interleaved with window sizes and timer intervals, with no rule
whatsoever — the PRISM pointer declared its primary and secondary
wheels in one place and its THIRD wheel, the Council, 36 lines further
down inside ANOTHER pointer's block. His words: *"radimo kao idioti...
kada se implementira nova funkcionalnost svakoga bole kurac kako je to
prethodno i ne prati nikakvu strukturu nego samo nabaci novu
promenljivu."*

`config/palette.py` is the fix. This file is what stops it coming back
— because a rule nobody enforces is a rule that lasts one session:

1. **Every colour lives in `config/palette.py`.** No hex literal and no
   literal CSS `rgba(...)` anywhere else in the program.
2. **`PALETTE_PRESETS` holds no colour of its own** — only names. A
   wheel is declared once, above, where it can be read and reviewed.
3. **A pointer's wheels never separate.** Every pointer's entries form
   ONE contiguous run in `PALETTE_PRESETS` — the exact defect the owner
   found, made mechanically impossible.
"""

import ast
import pathlib
import re

import pytest

from config import palette

ROOT = pathlib.Path(__file__).resolve().parent.parent
#: The program itself. `tests/` is exempt: a test may name a colour as a
#: fixture (a probe pixmap's fill), which is data, not a design choice.
SOURCE_DIRS = ("app", "config", "core", "data", "render", "skins")
THE_ONE_FILE = ROOT / "config" / "palette.py"

HEX_LITERAL = re.compile(r"^#[0-9A-Fa-f]{3,8}$")
CSS_COLOR_LITERAL = re.compile(r"\brgba?\(\s*\d")


def _source_files():
    for directory in SOURCE_DIRS:
        for path in sorted((ROOT / directory).rglob("*.py")):
            if path != THE_ONE_FILE:
                yield path


def _string_constants(path: pathlib.Path):
    """Every LITERAL string in the file, with its line. An f-string's
    interpolated parts are NOT literals — `f"rgba({c.red()}, ...)"`
    composes a colour from a value, which is exactly what a caller
    should do."""
    tree = ast.parse(path.read_text(encoding="utf8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            yield node.lineno, node.value


@pytest.mark.parametrize("path", list(_source_files()), ids=lambda p: p.name)
def test_no_colour_literal_outside_the_palette(path):
    """Clause 1. A colour is a design decision; it belongs where the
    other design decisions are, not inline three thousand lines from
    its siblings."""
    offenders = [
        f"{path.relative_to(ROOT).as_posix()}:{line} -> {value!r}"
        for line, value in _string_constants(path)
        if HEX_LITERAL.match(value.strip()) or CSS_COLOR_LITERAL.search(value)
    ]
    assert not offenders, (
        "colour literals must live in config/palette.py:\n  "
        + "\n  ".join(offenders)
    )


def _presets_node() -> ast.Dict:
    tree = ast.parse(THE_ONE_FILE.read_text(encoding="utf8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "PALETTE_PRESETS"
            for t in node.targets
        ):
            assert isinstance(node.value, ast.Dict)
            return node.value
    raise AssertionError("PALETTE_PRESETS is not a top-level dict any more")


def test_the_preset_table_names_its_wheels_and_spells_out_none():
    """Clause 2. Every value is a bare NAME. The moment a tuple of hues
    is inlined here again, a wheel has two homes and the file starts
    drifting back into the state the owner found."""
    inlined = [
        ast.unparse(value)
        for value in _presets_node().values
        if not isinstance(value, ast.Name)
    ]
    assert not inlined, (
        "PALETTE_PRESETS must reference named wheels, never spell hues "
        f"out: {inlined}"
    )


def test_every_pointer_keeps_its_wheels_in_one_run():
    """Clause 3 — THE regression. PRISM's primary and secondary sat at
    one place in the old table and its tertiary (the Council) far below,
    inside the trio's block. Whatever order the pointers come in, each
    one's entries must be CONSECUTIVE."""
    pointers = [key.elts[0].value for key in _presets_node().keys]
    runs = []
    for pointer in pointers:
        if not runs or runs[-1] != pointer:
            runs.append(pointer)
    assert len(runs) == len(set(runs)), (
        "a pointer's wheels are split across the table — every pointer "
        f"must own ONE contiguous run: {runs}"
    )


def test_the_wheels_a_pointer_declares_are_the_ones_it_serves():
    """The table and the pointer roster agree: no wheel nobody can
    select, no selectable style with no wheel behind it."""
    from config import constants

    declared: dict[str, set] = {}
    for pointer, style in palette.PALETTE_PRESETS:
        declared.setdefault(pointer, set()).add(style)
    for pointer, styles in declared.items():
        assert styles == set(constants.palette_styles_for(pointer)), pointer
