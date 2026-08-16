"""THE EAGER LOOKUP TOOTH (owner bug 2026-08-16).

The per-section Reset learns which settings a page owns by recording the
keys the page's BUILD asked for (`app.watch_face.section_reset.
RecordingSetters`). That design has one silent failure mode, and it shipped:
a builder that writes `setters["diameter"]` INSIDE a lambda never performs
the lookup while it builds — it performs it on the user's click, long after
the Reset button was wired. The key is therefore absent from the recording,
and the Reset walks straight past that setting.

The owner found it on the Size page, whose Reset moved exactly ONE knob
(`numeral_outer_ring_size` — the single key that happened to be bound
eagerly) and left the other eight where he had dragged them. Eight pages
carried the same shape.

So the rule, enforced here: in a watch-face section module, a `setters[...]`
subscript may not appear inside a lambda or a nested function. Look the
setter up in the builder's own body, into a local name, and let the callback
close over that name.

Exempt keys are the ones the Reset would drop anyway — the multi-argument
setters (`section_reset._takes_one_value`) and the data PROVIDERS that are
not `Settings` fields at all.
"""

import ast
import dataclasses
from pathlib import Path

import pytest

from app.settings_store import Settings

_PAGES = Path(__file__).resolve().parents[1] / "app" / "watch_face"

#: Setters that take a target plus a value, or are not settings at all —
#: `section_reset` already refuses to reset these, so a deferred lookup of
#: one costs nothing.
_ARITY_EXEMPT = frozenset({
    "earth_label", "palettes", "theme_metal", "open_custom_ring",
})

#: `section_reset.py` IS the reset — its own `setters[key]` inside `apply`
#: is the mechanism, not a mistake.
_SKIP_FILES = frozenset({"section_reset.py"})

_SETTINGS_FIELDS = frozenset(f.name for f in dataclasses.fields(Settings))


def _deferred_setter_reads(tree: ast.AST) -> list[tuple[int, str]]:
    """Every `setters[...]` subscript that sits inside a lambda or a
    nested function, as (line, key-or-'<computed>')."""
    findings: list[tuple[int, str]] = []

    class Walker(ast.NodeVisitor):
        def __init__(self) -> None:
            self.depth = 0

        def _nested(self, node) -> None:
            self.depth += 1
            self.generic_visit(node)
            self.depth -= 1

        visit_Lambda = _nested

        def visit_FunctionDef(self, node) -> None:
            # A module-level `def` is a builder, not a callback; only a
            # `def` nested inside another one defers its lookups.
            if self.depth == 0 and getattr(node, "_top_level", False):
                self.generic_visit(node)
            else:
                self._nested(node)

        def visit_Subscript(self, node) -> None:
            if (
                self.depth > 0
                and isinstance(node.value, ast.Name)
                and node.value.id == "setters"
            ):
                key = (
                    node.slice.value
                    if isinstance(node.slice, ast.Constant)
                    else "<computed>"
                )
                if key not in _ARITY_EXEMPT:
                    findings.append((node.lineno, str(key)))
            self.generic_visit(node)

    for node in ast.walk(tree):
        if isinstance(node, ast.Module):
            for child in node.body:
                if isinstance(child, ast.FunctionDef):
                    child._top_level = True
    Walker().visit(tree)
    return findings


@pytest.mark.parametrize(
    "path",
    sorted(p for p in _PAGES.glob("*.py") if p.name not in _SKIP_FILES),
    ids=lambda p: p.name,
)
def test_setters_are_looked_up_eagerly(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    deferred = _deferred_setter_reads(tree)
    assert not deferred, (
        f"{path.name}: setter lookup deferred into a callback — the "
        "per-section Reset records only what the BUILD asks for, so these "
        "settings would never be reset. Bind them to a local name in the "
        "builder's body: "
        + ", ".join(f"line {line}: setters[{key!r}]" for line, key in deferred)
    )


def test_exempt_keys_are_genuinely_not_resettable() -> None:
    """The allowlist must stay honest: an exempt key that IS a plain
    one-value `Settings` field would be a hole in the tooth above."""
    plain = _ARITY_EXEMPT & _SETTINGS_FIELDS
    assert plain <= {"earth_label", "palettes"}, (
        f"exempt keys that are ordinary Settings fields: {sorted(plain)} — "
        "either bind them eagerly or prove they take more than one value."
    )
