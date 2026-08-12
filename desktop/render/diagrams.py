"""The ONE door to every computed diagram.

Three modules draw them — [Cube Diagrams](cube_diagrams.md) for the
Cube's geometry, [Canon Diagrams](canon_diagrams.md) for the journeys
and the tables, [Instrument Diagrams](instrument_diagrams.md) for the
clock explaining itself — and a page must not have to know which. It
declares `"diagram": (kind, key)`; this facade finds the drawer.

Layer: render. Documentation: diagrams.md.
"""

from PySide6.QtGui import QPixmap

from render import canon_diagrams, cube_diagrams, instrument_diagrams

_MODULES = (cube_diagrams, canon_diagrams, instrument_diagrams)


def plate(kind: str, key: str, size: int) -> QPixmap:
    """The figure for one page. An unknown kind returns a null pixmap —
    the reader then simply shows the article, exactly as it does for a
    plate whose art has not landed (graceful-absent, Rule #1's
    documented path)."""
    for module in _MODULES:
        if kind in module.kinds():
            return module.plate(kind, key, size)
    return QPixmap()


def kinds() -> tuple:
    """Every kind the program can draw — the coverage test reads this,
    so a page can never name a drawer nobody wrote."""
    return tuple(
        kind for module in _MODULES for kind in module.kinds()
    )
