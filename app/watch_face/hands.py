"""Hands section (R-14, see hands.md) — a gallery of hand packs, each
tile's hours-hand image LARGE (the image dominates the tile, the name
sits under it) — the same data `design_window.DesignDialog._hands_tab`
reads, through `thumbs.art_thumbnail`'s disk-cached source instead of a
raw `QIcon(path)` load. The icon size is the shared
`widgets.TILE_ICON_PX` (2026-08-08): this gallery's "image dominates"
look was promoted to EVERY gallery, so its private size constant moved
into the tile builder itself.
"""

from PySide6.QtWidgets import QWidget

from app.watch_face import thumbs
from app.watch_face.widgets import flow_gallery, tile
from data.hands import hand_packs


def build(settings, setters: dict, tr) -> QWidget:
    packs = hand_packs()
    return flow_gallery([
        tile(
            tr(name),
            thumbs.art_thumbnail(packs[name]["files"]["hours"]),
            settings.hands == name,
            lambda n=name: setters["hands"](n),
        )
        for name in sorted(packs)
    ])
