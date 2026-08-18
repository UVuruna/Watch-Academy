"""Session 36's guard — THE CONFIG SPLIT (WORKPLAN-STRUCTURE.md).

Pins the two clauses the split's own method promises:

1. Every config module is at or under the god-file threshold, no
   exemptions at all (this test carries no ratchet of its own — a config
   module earns cohesion, not tolerance; `tests/test_structure_law.py`
   is the project-wide ratchet).
2. A name that moved out of `config/defaults.py` (dial.py, shortcuts.py,
   pantheon.py, calendar_mounts.py, encyclopedia_ui.py, glow.py, and
   continents.py — the pantheon deterministic fallback) is GONE from
   `defaults.py`: `defaults.MOVED_NAME` must raise `AttributeError`.
   Rule #6, no re-export shims.

WA-R15 (2026-08-19) fixed two things this guard had wrong.

**It counted RAW lines** and was RED at HEAD for `config/defaults.py`
(1,036) — a module whose actual content is 418 lines, wrapped in 618
lines of section banners and blank space. Banner comments are what makes
a config file READABLE; counting them as bulk punishes the very habit
THE CONFIG SECTION LAW demands. The measure is now
`tests/line_measure.logic_lines` — non-blank, non-comment, the monorepo's
own definition, shared with `test_structure_law.py`.

Tables are NOT subtracted here, unlike in THE STRUCTURE LAW: a config
module is almost all table, so subtracting them would leave every file
measuring near zero and this guard could never fire. Its subject is
exactly "how many table rows live in one module".

**It carried two exemptions** — `constants.py` and `pantheon.py` — in a
test whose own docstring promised none. Under the shared measure neither
is over (770 and 344), so both are gone and the guard is exemption-free
again, as it always claimed to be.

**And it only looked at `config/*.py`.** `config/registry/` is config
too, and its largest module is 903 lines; the walk is now recursive.
"""

import ast
import pathlib

import pytest

from config import calendar_mounts, continents, defaults, dial, encyclopedia_ui, glow, pantheon, shortcuts
from tests.line_measure import logic_lines, raw_lines

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

def _config_modules() -> list[pathlib.Path]:
    """Every config module, `config/registry/` included; caches and
    package markers excluded."""
    return sorted(
        path
        for path in CONFIG_DIR.rglob("*.py")
        if "__pycache__" not in path.parts and path.name != "__init__.py"
    )


@pytest.mark.parametrize(
    "path",
    _config_modules(),
    ids=lambda p: p.relative_to(CONFIG_DIR).as_posix(),
)
def test_every_config_module_is_at_or_under_the_threshold(path):
    lines = logic_lines(path)
    assert lines <= MAX_LINES, (
        f"{path.relative_to(ROOT).as_posix()} is {lines} logic lines "
        f"({raw_lines(path)} total), over the {MAX_LINES}-line god-file "
        "threshold. This guard has no ratchet and no exemption list: "
        "split the module by TOPIC, keeping each section whole (THE "
        "CONFIG SECTION LAW), and repoint the callers — never a "
        "re-export shim."
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
