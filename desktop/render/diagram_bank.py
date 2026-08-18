"""One bank of computed diagrams: a drawer table, a cache, and the two
names every reader asks for.

Three modules draw the Encyclopedia's figures — [Cube
Diagrams](cube_diagrams.md), [Canon Diagrams](canon_diagrams.md),
[Instrument Diagrams](instrument_diagrams.md) — and all three had
re-typed the same `_CACHE` dict, the same `plate()` lookup-draw-store and
the same `kinds()` (clone C1 of the OOP audit, 2026-08-18, the one entry
the clone ratchet held). The DRAWERS differ; the bank around them never
did. Each module now declares its drawers and hands them to one of these.

Two shapes of bank exist, and the difference is which half of a page's
`("diagram": (kind, key))` declaration names the drawer:

* **indexed by KIND** — the module answers several kinds, one drawer per
  kind (cube, canon). `kinds()` is the drawer table's own keys.
* **indexed by KEY** — the module answers ONE kind and the KEY names the
  figure (instrument, twelve figures under `"instrument"`). The kind it
  answers is declared separately.

Layer: render (Qt allowed; no wall clock, no settings). Documentation:
diagram_bank.md.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable

from PySide6.QtGui import QPixmap

Drawer = Callable[[str, int], QPixmap]


class DiagramBank:
    """A table of drawers plus the cache in front of it.

    `drawers` maps a name to `drawer(key, size) -> QPixmap`. `key_by`
    says which half of `(kind, key)` that name is — `"kind"` (the
    default) or `"key"`. `answers` names the kinds the bank claims;
    it defaults to the drawer names, which is right only when
    `key_by == "kind"`, so a key-indexed bank must state it."""

    def __init__(self, drawers: dict[str, Drawer], *,
                 key_by: str = "kind",
                 answers: Iterable[str] | None = None) -> None:
        if key_by not in ("kind", "key"):
            raise ValueError(f"key_by must be 'kind' or 'key', not {key_by!r}")
        if key_by == "key" and answers is None:
            raise ValueError("a key-indexed bank must name the kind(s) it "
                             "answers — the drawer names are figures, not kinds")
        self._drawers = drawers
        self._key_by = key_by
        self._answers = tuple(answers) if answers is not None else tuple(drawers)
        self._cache: dict[tuple[str, str, int], QPixmap] = {}

    def plate(self, kind: str, key: str, size: int) -> QPixmap:
        """The figure for one page, cached per (kind, key, size).
        Drawing is cheap, but the reader re-fits on every resize and
        must never repaint the same figure twice. An unknown name
        returns a null pixmap — the graceful-absent path the facade
        documents."""
        cached = self._cache.get((kind, key, size))
        if cached is None:
            drawer = self._drawers.get(kind if self._key_by == "kind" else key)
            if drawer is None:
                return QPixmap()
            cached = drawer(key, size)
            self._cache[(kind, key, size)] = cached
        return cached

    def kinds(self) -> tuple[str, ...]:
        """Every kind this bank answers — the facade routes on it and
        the coverage test reads it, so a page can never declare a
        diagram nobody draws."""
        return self._answers
