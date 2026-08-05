"""Hands section (R-14, see hands.md) — a gallery of hand packs, each
tile's hours-hand image LARGE (the image dominates the tile, the name
sits under it) — the same data `design_window.DesignDialog._hands_tab`
reads, through `thumbs.art_thumbnail`'s disk-cached source instead of a
raw `QIcon(path)` load.
"""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QGridLayout, QWidget

from app.watch_face import thumbs
from app.watch_face.widgets import tile
from data.hands import hand_packs

# Deliberately larger than the Ring/Pointer gallery tiles (owner spec:
# "image dominates, name under it") — still well under
# `thumbs.THUMB_SOURCE_PX`, so the cached 256px source stays sharp.
_TILE_ICON_PX = 128


def build(settings, setters: dict, tr) -> QWidget:
    grid = QGridLayout()
    packs = hand_packs()
    for index, name in enumerate(sorted(packs)):
        icon = thumbs.art_thumbnail(packs[name]["files"]["hours"])
        button = tile(
            tr(name), icon, settings.hands == name,
            lambda n=name: setters["hands"](n),
        )
        button.setIconSize(QSize(_TILE_ICON_PX, _TILE_ICON_PX))
        row, col = divmod(index, 4)
        grid.addWidget(button, row, col)
    widget = QWidget()
    widget.setLayout(grid)
    return widget
