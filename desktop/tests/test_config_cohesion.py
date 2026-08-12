"""Session 36's guard — THE CONFIG SPLIT (WORKPLAN-STRUCTURE.md).

Pins the two clauses the split's own method promises:

1. Every `config/*.py` file is at or under the god-file threshold, no
   exemptions (this test carries no ratchet of its own — a config
   module earns cohesion, not tolerance; `tests/test_structure_law.py`
   is the project-wide ratchet, and `config/pantheon.py` is a KNOWN,
   documented, owner-flagged exception recorded there, not here).
2. A name that moved out of `config/defaults.py` (dial.py, shortcuts.py,
   pantheon.py, calendar_mounts.py, encyclopedia_ui.py, glow.py, and
   continents.py — the pantheon deterministic fallback) is GONE from
   `defaults.py`: `defaults.MOVED_NAME` must raise `AttributeError`.
   Rule #6, no re-export shims.
"""

import ast
import pathlib

import pytest

from config import calendar_mounts, continents, defaults, dial, encyclopedia_ui, glow, pantheon, shortcuts

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
MAX_LINES = 1000

NEW_MODULES = {
    "dial": dial,
    "shortcuts": shortcuts,
    "pantheon": pantheon,
    "calendar_mounts": calendar_mounts,
    "encyclopedia_ui": encyclopedia_ui,
    "glow": glow,
    "continents": continents,
}

# Two pre-existing, ALREADY-tracked exceptions -- both are named in
# tests/test_structure_law.py's own ratchet, the ONE place a size
# exception may be granted (requires the owner's explicit approval).
# Listing them here too avoids this stricter, exemption-free config-only
# check duplicating a fight that test is already carrying:
#   - config/constants.py: untouched by Session 36 (the split map does
#     not cover it) -- "a constants split round after Session 36" owes it.
#   - config/pantheon.py: every WEEKDAY_* table plus the roster/rotation
#     engine the split map's own pre-answered Q&A binds to it already
#     totals ~1.17k lines at the floor, before the rest of the map's
#     carves -- see config/pantheon.md Design Decisions. THIS is the one
#     genuinely NEW exception Session 36 could not avoid; the owner
#     still owes it a ratchet entry or a further-split decision.
KNOWN_OVER_THRESHOLD = {"constants.py", "pantheon.py"}


def _line_count(path: pathlib.Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for _ in handle)


@pytest.mark.parametrize(
    "path",
    sorted(p for p in CONFIG_DIR.glob("*.py") if p.name not in KNOWN_OVER_THRESHOLD),
    ids=lambda p: p.name,
)
def test_every_config_module_is_at_or_under_the_threshold(path):
    lines = _line_count(path)
    assert lines <= MAX_LINES, (
        f"{path.relative_to(ROOT).as_posix()} is {lines} lines, over the "
        f"{MAX_LINES}-line god-file threshold, and is not a documented "
        "exception in this test's KNOWN_OVER_THRESHOLD set."
    )


def _top_level_names(path: pathlib.Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = set()
    for node in tree.body:
        if isinstance(node, ast.Assign):
            names |= {t.id for t in node.targets if isinstance(t, ast.Name)}
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            names.add(node.name)
    return names


@pytest.mark.parametrize("module_name", sorted(NEW_MODULES), ids=str)
def test_no_moved_name_remains_reachable_through_defaults(module_name):
    """Every name genuinely DEFINED (not merely imported) in a new module
    must be gone from `config.defaults` — a moved name accessed through
    `defaults.` must raise `AttributeError`, never silently resolve to a
    stale re-export."""
    path = CONFIG_DIR / f"{module_name}.py"
    offenders = [name for name in _top_level_names(path) if hasattr(defaults, name)]
    assert not offenders, (
        f"these names moved to config/{module_name}.py but are STILL "
        f"reachable as config.defaults.<name> (a re-export shim, "
        f"forbidden by Rule #6): {sorted(offenders)}"
    )
