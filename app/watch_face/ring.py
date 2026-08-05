"""Ring section (R-10/R-13, see ring.md) — preset gallery (thumbnail
tiles, the layout's own face art via `thumbs.art_thumbnail`), letters-
finish pills and the Two-metals/Shine checkboxes — moved verbatim from
`design_window.DesignDialog._ring_tab` (same conditional rules, Rule
#5) — plus R-13's "Custom ring…" button, which opens the EXISTING
Settings dialog's Custom art section rather than duplicating its inline
widgets (see ring.md's Design Decisions).
"""

from PySide6.QtWidgets import (
    QCheckBox, QGridLayout, QHBoxLayout, QPushButton, QVBoxLayout, QWidget,
)

from app.watch_face import thumbs
from app.watch_face.widgets import pill, tile
from config import constants, dial
from data.rings import ring_presets


def build(settings, setters: dict, tr) -> QWidget:
    layout = QVBoxLayout()
    presets = ring_presets(settings.custom_rings)
    layout.addLayout(_preset_gallery(settings, presets, setters, tr))
    layout.addLayout(_finish_row(settings, setters, tr))
    active_card = presets[settings.ring]
    card_layout = constants.RING_LAYOUTS[active_card["layout"]]
    if active_card["triangle"] is not None or card_layout["triangle"]:
        # Same resolution `app.controller._ring_two_metals` uses: the
        # stored per-preset choice, else the owner's documented default,
        # else the layout's own nature.
        two_metals = settings.ring_two_metals.get(
            settings.ring,
            constants.RING_TWO_METALS_DEFAULT.get(
                settings.ring, bool(card_layout["triangle"])
            ),
        )
        checkbox = QCheckBox(tr("Two metals"))
        checkbox.setChecked(two_metals)
        checkbox.toggled.connect(setters["ring_two_metals"])
        layout.addWidget(checkbox)
    if constants.RING_EYE_GLYPH in active_card["letters"]:
        shine = settings.ring_eye_shine.get(
            settings.ring,
            constants.RING_EYE_SHINE_DEFAULT.get(settings.ring, False),
        )
        shine_box = QCheckBox(tr("Shine"))
        shine_box.setChecked(shine)
        shine_box.toggled.connect(setters["ring_eye_shine"])
        layout.addWidget(shine_box)
    layout.addWidget(_custom_ring_button(setters, tr))
    widget = QWidget()
    widget.setLayout(layout)
    return widget


def _preset_gallery(settings, presets: dict, setters, tr) -> QGridLayout:
    grid = QGridLayout()
    for index, name in enumerate(sorted(presets)):
        card = presets[name]
        face = constants.RING_LAYOUTS[card["layout"]]["face"]
        icon = thumbs.art_thumbnail(dial.RING_FACE_DIR / face)
        row, col = divmod(index, 4)
        grid.addWidget(
            tile(
                tr(name), icon, settings.ring == name,
                lambda n=name: setters["ring"](n),
            ),
            row, col,
        )
    return grid


def _finish_row(settings, setters, tr) -> QHBoxLayout:
    row = QHBoxLayout()
    for finish in constants.RING_FINISHES:
        row.addWidget(pill(
            tr(f"{finish.capitalize()} letters"), settings.ring_finish == finish,
            lambda f=finish: setters["ring_finish"](f),
        ))
    return row


def _custom_ring_button(setters, tr) -> QPushButton:
    """R-13: the existing custom-ring flow
    (`app/settings_dialog/custom_art_section.py`) is a plain-Python
    mixin baked onto `SettingsDialog`, not a standalone dialog — this
    button opens THAT dialog, navigated to its Custom art section,
    instead of duplicating its inline widgets."""
    button = QPushButton(tr("Custom ring…"))
    button.clicked.connect(lambda: setters["open_custom_ring"]())
    return button
