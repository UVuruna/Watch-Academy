"""THE ONE ARITHMETIC — what "a line" means to every size guard here.

WA-R15 (2026-08-19) exists because this project measured a file's size
three different ways and two guards disagreed about the same file:

* `rules/tools/structure_guard.py` (the monorepo tool wired into
  `run_guards.py` FULL, and the one other tools read) counts **non-blank,
  non-comment** lines. It read `app/controller.py` as 899.
* `tests/test_structure_law.py` counted **total lines minus declarative
  tables** — comments included. It read the same file as 1,218 and kept
  it on the ratchet a whole refactor after it had earned its way off.
* `tests/test_config_cohesion.py` counted **raw lines**, and was RED at
  HEAD for `config/defaults.py` (1,036) — a file whose real content is
  418 lines with 618 lines of banner comments and blanks around them.

A law whose guards cannot agree on the number is not enforced, it is
argued about. So both project guards now read this module, and it starts
from the monorepo's definition.

## `logic_lines(path)`
Non-blank, non-comment lines — byte-for-byte the monorepo tool's rule
(docstrings count: they are read). This is the number the JSON ratchet
`tests/structure_ratchet.json` holds, so the project can never again
tolerate a file the shared tool rejects.

## `declarative_lines(path)`
The subset of those lines spanned by top-level DECLARATIVE data — a
module-level assignment whose value is a literal dict/list/tuple/set,
plus the module docstring. **This is the owner's ruling of 2026-08-05,
kept whole:** the law exists so nobody has to hold a thousand lines of
BEHAVIOUR in their head at once; a registry is a DIRECTORY — thirty-five
sibling entries of one kind, read by looking one up, never top to
bottom. Splitting such a table across files makes one subject live in
eight places. A literal that CALLS anything, or a comprehension, is not
declarative and is not subtracted: the moment a table computes, it is
logic again.

## Which guard uses which
* **THE STRUCTURE LAW** (`test_structure_law.py`) measures
  `logic_lines - declarative_lines`. It is about behaviour, and the
  owner's 2026-08-05 ruling says a table is not behaviour. It can
  therefore never be STRICTER than the shared tool — so a file the
  shared tool rejects still fails `run_guards` FULL through the JSON
  ratchet, and the two can never disagree in the direction where
  "fine" wins.
* **CONFIG COHESION** (`test_config_cohesion.py`) measures
  `logic_lines` alone, tables included. Its subject IS how many table
  rows live in one module: subtracting the tables would leave every
  config file measuring near zero, and a guard that cannot fire is
  worse than none.
"""

from __future__ import annotations

import ast
from pathlib import Path


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def logic_lines(path: Path) -> int:
    """Non-blank, non-comment lines — the monorepo's own measure
    (`rules/tools/structure_guard.py`)."""
    return sum(
        1
        for line in _text(path).splitlines()
        if line.strip() and not line.strip().startswith("#")
    )


def declarative_lines(path: Path) -> int:
    """How many of `logic_lines` are top-level declarative data.

    Counted the same way `logic_lines` counts, so the subtraction is
    always well defined: a blank line or a comment INSIDE a table was
    never in the total to begin with.
    """
    source = _text(path)
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return 0
    lines = source.splitlines()
    total = 0
    for node in tree.body:
        value = None
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            value = node.value                      # the module docstring
        if value is None or not isinstance(
            value, (ast.Dict, ast.List, ast.Tuple, ast.Set, ast.Constant)
        ):
            continue
        if any(
            isinstance(child, (ast.Call, ast.comprehension, ast.Lambda))
            for child in ast.walk(value)
        ):
            continue                                # it computes — that is logic
        for line in lines[node.lineno - 1:node.end_lineno]:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                total += 1
    return total


def behaviour_lines(path: Path) -> int:
    """What THE STRUCTURE LAW measures: logic that is not a directory."""
    return logic_lines(path) - declarative_lines(path)


def raw_lines(path: Path) -> int:
    """Every line in the file — reported beside a verdict, never the
    verdict itself."""
    return len(_text(path).splitlines())
