# Diagram Bank

**Script:** [Diagram Bank (script)](../diagram_bank.py)

## Purpose
One bank of computed diagrams: a table of drawers, the cache in front of
it, and the two names every reader asks for — `plate(kind, key, size)`
and `kinds()`.

Three modules draw the Encyclopedia's figures, and all three had re-typed
the identical `_CACHE` dict, the identical lookup-draw-store `plate()`
and the identical `kinds()`. That pair was the ONE entry the clone
ratchet held (`clone_ratchet.json`, group C1 of the [OOP
audit](../../../docs/AUDIT-OOP-2026-08-18.md)), with a third near-copy in
`instrument_diagrams.py` that the detector never reached. The drawers
differ; the bank around them never did.

## Connections

### Uses
- `PySide6.QtGui.QPixmap` — the null pixmap is the graceful-absent answer

### Used by
- [Cube Diagrams](cube_diagrams.md) — six kinds, indexed by kind
- [Canon Diagrams](canon_diagrams.md) — five kinds, indexed by kind
- [Instrument Diagrams](instrument_diagrams.md) — twelve figures under
  the single kind `"instrument"`, indexed by KEY
- [Diagrams](diagrams.md) — the facade, which asks each module's
  `kinds()` and routes `plate()` to the first that claims the kind

## Design Decisions
- **Two shapes of bank, one class.** Which half of a page's
  `"diagram": (kind, key)` declaration names the drawer is a
  CONSTRUCTOR argument, not a second class: `key_by="kind"` (the
  default — the module answers several kinds, one drawer each) or
  `key_by="key"` (the module answers one kind and the key names the
  figure). A key-indexed bank must declare `answers=`, because its
  drawer names are figures and would be a lie as kinds; the constructor
  raises rather than let that pass silently.
- **The cache is per bank, never global.** Each module owns its own
  instance, so the three caches stay as separate as the three modules
  were — the key is still `(kind, key, size)` and the eviction policy is
  still "none, the figures are small and the process is one dial".
- **An unknown name returns a null pixmap.** Unchanged behaviour: the
  reader shows the article without a figure, exactly as it does for a
  plate whose art has not landed.
