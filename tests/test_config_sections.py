"""THE CONFIG SECTION LAW's guard (owner decree 2026-08-01).

Root `rules/CODE.md` -> THE CONFIG SECTION LAW: config files and data
tables are STRUCTURES, not notebooks. The canonical failure it kills:
a config defines POINTER shapes with their colour variants, and a later
session — never looking where shapes live — dumps the new colour at the
end of the file as `POINTER_SHAPES["arrow"]["colors"]["crimson"] = ...`.

Three assertions over every file in `CONFIG_FILES`:

1. **No post-definition patching.** At module level, no `X[...] = ...`
   and no `X.update(...)` against a name defined earlier in the file.
   A variant is added by editing the EXISTING structure in place.
2. **No duplicate dict keys.** Two identical literal keys in one dict
   means one silently wins — always a merge accident.
3. **Defined once, whole, in its section.** Every top-level definition
   sits BELOW a named section banner:

       # ============================ POINTER SHAPES ====================

   (the project writes the banner rule with box-drawing `=` runs; any
   comment line carrying a run of at least `MIN_BANNER_RUN` `=` or `-`
   box characters counts as a banner).

`CONFIG_FILES` is every module under `config/` — the folder whose whole
job is tables. It grows when a new config module is born; it never
shrinks to silence a violation.
"""

import ast
import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"

# Every config module carries the law. `__init__.py` is a trivial package
# marker with no tables of its own and is the ONE exemption.
CONFIG_FILES: tuple[str, ...] = tuple(
    sorted(
        path.relative_to(PROJECT_ROOT).as_posix()
        for path in CONFIG_DIR.glob("*.py")
        if path.name != "__init__.py"
    )
)

MIN_BANNER_RUN = 8
_BANNER = re.compile(r"^\s*#.*?([═─=\-]{%d,})" % MIN_BANNER_RUN)

# THE PATCHING RATCHET — like THE STRUCTURE LAW's, it may only SHRINK,
# and an entry needs the owner's explicit approval.
#
# `config/pantheon.py` builds `WEEKDAY_THEME_FILES` by folding every
# display name into a file stem, then patches ~30 exceptions onto the
# derived table (whole-theme replacements for greek/norse/japan/bible/...
# and single-key fixes for profession/wolf/bee/corporate/alchemy/...).
# The law-abiding shape is one `_FILE_STEM_OVERRIDES` table merged INSIDE
# the comprehension — a real refactor with two traps a docs/split session
# must not spring blind: a whole-theme replacement that lists fewer bodies
# than the fold produces would MERGE instead of REPLACE, and per-theme key
# ORDER would change. Both need a before/after equality proof and the
# owner's eyes.
#
# OWED: a `config/pantheon.py` restructuring round — the same round that
# owes its god-file split (it is also in tests/test_structure_law.py's
# RATCHET at 1,549 lines). Added 2026-08-01 by the docs-migration session,
# WITHOUT the owner's prior approval, because the alternative was a red
# guard blocking every session's Stop hook. The owner must rule on it.
PATCHING_RATCHET: dict[str, str] = {
    "config/pantheon.py": (
        "~30 documented exceptions patched onto the derived "
        "WEEKDAY_THEME_FILES table; folding them into the comprehension "
        "changes merge-vs-replace and key order — owner ruling needed"
    ),
}


def _tree(rel: str) -> tuple[ast.Module, list[str]]:
    path = PROJECT_ROOT / rel
    source = path.read_text(encoding="utf-8")
    return ast.parse(source, filename=rel), source.splitlines()


def _banner_lines(lines: list[str]) -> list[int]:
    """1-based line numbers of every section banner comment."""
    return [n for n, line in enumerate(lines, 1) if _BANNER.match(line)]


def _defined_names_before(tree: ast.Module, lineno: int) -> set[str]:
    names: set[str] = set()
    for node in tree.body:
        if node.lineno >= lineno:
            break
        if isinstance(node, ast.Assign):
            names |= {t.id for t in node.targets if isinstance(t, ast.Name)}
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
    return names


def _root_name(node: ast.AST) -> str | None:
    """The base Name of a subscript/attribute chain: `A["x"]["y"]` -> "A"."""
    while isinstance(node, (ast.Subscript, ast.Attribute)):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


@pytest.mark.parametrize("rel", CONFIG_FILES, ids=lambda r: Path(r).name)
def test_no_post_definition_patching(rel):
    """No `TABLE[...] = ...` / `TABLE.update(...)` at module level against
    a table defined earlier in the same file."""
    if rel in PATCHING_RATCHET:
        pytest.skip(f"PATCHING_RATCHET: {PATCHING_RATCHET[rel]}")
    tree, _ = _tree(rel)
    offenders = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if not isinstance(target, ast.Subscript):
                    continue
                name = _root_name(target)
                if name and name in _defined_names_before(tree, node.lineno):
                    offenders.append(f"line {node.lineno}: {name}[...] = ...")
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            func = node.value.func
            if isinstance(func, ast.Attribute) and func.attr in {"update", "setdefault"}:
                name = _root_name(func.value)
                if name and name in _defined_names_before(tree, node.lineno):
                    offenders.append(f"line {node.lineno}: {name}.{func.attr}(...)")
    assert not offenders, (
        f"THE CONFIG SECTION LAW (rules/CODE.md): {rel} patches an earlier "
        "table after its definition — write the entry INSIDE the structure, "
        "in its own section:\n  " + "\n  ".join(offenders)
    )


def test_the_patching_ratchet_only_shrinks():
    """A file that healed must LEAVE the ratchet — the list never holds a
    file that no longer patches anything."""
    stale = []
    for rel in PATCHING_RATCHET:
        if not (PROJECT_ROOT / rel).exists():
            stale.append(f"{rel} (file no longer exists)")
            continue
        tree, _ = _tree(rel)
        patches = False
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Subscript)
                and _root_name(t) in _defined_names_before(tree, node.lineno)
                for t in node.targets
            ):
                patches = True
        if not patches:
            stale.append(f"{rel} (healed — delete the entry)")
    assert not stale, (
        "THE CONFIG SECTION LAW ratchet must SHRINK: " + ", ".join(sorted(stale))
    )


@pytest.mark.parametrize("rel", CONFIG_FILES, ids=lambda r: Path(r).name)
def test_no_duplicate_dict_keys(rel):
    """A literal key written twice in one dict — one of them silently wins."""
    tree, _ = _tree(rel)
    offenders = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        seen: dict[object, int] = {}
        for key in node.keys:
            if not isinstance(key, ast.Constant):
                continue                       # **spread or computed key
            marker = (type(key.value).__name__, key.value)
            if marker in seen:
                offenders.append(
                    f"line {key.lineno}: duplicate key {key.value!r} "
                    f"(first at line {seen[marker]})"
                )
            else:
                seen[marker] = key.lineno
    assert not offenders, (
        f"THE CONFIG SECTION LAW (rules/CODE.md): {rel} has duplicate dict "
        "keys — the later one silently wins:\n  " + "\n  ".join(offenders)
    )


@pytest.mark.parametrize("rel", CONFIG_FILES, ids=lambda r: Path(r).name)
def test_every_top_level_definition_sits_under_a_section_banner(rel):
    """Defined once, whole, IN ITS SECTION — nothing dangles above the
    first banner or outside the banner structure."""
    tree, lines = _tree(rel)
    banners = _banner_lines(lines)
    assert banners, (
        f"THE CONFIG SECTION LAW (rules/CODE.md): {rel} carries no section "
        "banner at all. Organize it under named banners, e.g.\n"
        "    # ===================== POINTER SHAPES ====================="
    )
    first_banner = banners[0]

    homeless = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue                            # module docstring
        if not isinstance(
            node,
            (ast.Assign, ast.AnnAssign, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
        ):
            continue
        start = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
        if start < first_banner:
            name = getattr(node, "name", None) or ast.unparse(
                node.targets[0] if isinstance(node, ast.Assign) else node.target
            )
            homeless.append(f"line {start}: {name}")
    assert not homeless, (
        f"THE CONFIG SECTION LAW (rules/CODE.md): {rel} defines these above "
        "its first section banner — every definition belongs inside a named "
        "section:\n  " + "\n  ".join(homeless)
    )
