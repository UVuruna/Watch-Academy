"""Ring section (R-10/R-13, see ring.md) — THE COMPOSITIONAL RING MODEL
(owner decree 2026-08-05): a preset gallery (thumbnail tiles of the
LOCKED outer — the tooltip states the lock), an INNER gallery (eight
tiles, applies to the active preset — user-changeable independent of
the outer's lock), the letters-finish pills, the Two-metals/Shine
checkboxes (unchanged, R-10/TASK 3/DOLLAR-EYE) and R-13's "Custom
ring…" button, which opens the custom-ring flow's outer/letter/crown
builder in the Settings dialog rather than duplicating its inline
widgets (see ring.md's Design Decisions).
"""

from PySide6.QtWidgets import (
    QCheckBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QWidget,
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
    outer = constants.RING_OUTERS[active_card["outer"]]
    if active_card["triangle"] is not None or outer["triangle"]:
        # Same resolution `app.controller._ring_two_metals` uses: the
        # stored per-preset choice, else the owner's documented default,
        # else the outer's own nature.
        two_metals = settings.ring_two_metals.get(
            settings.ring,
            constants.RING_TWO_METALS_DEFAULT.get(
                settings.ring, bool(outer["triangle"])
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
    layout.addWidget(_inner_group(settings, setters, tr))
    layout.addWidget(_crown_text_group(settings, active_card, setters, tr))
    layout.addWidget(_custom_ring_button(setters, tr))
    widget = QWidget()
    widget.setLayout(layout)
    return widget


def _preset_gallery(settings, presets: dict, setters, tr) -> QGridLayout:
    """One tile per preset, thumbnailed off its LOCKED outer's own art
    (`constants.RING_OUTER_LOCK`) — the tooltip states which outer the
    preset is locked to (owner decree 2026-08-05: every bundled preset
    is locked to exactly one outer; only the INNER stays changeable)."""
    grid = QGridLayout()
    for index, name in enumerate(sorted(presets)):
        card = presets[name]
        outer_name = card["outer"]
        face = constants.RING_OUTERS[outer_name]["file"]
        icon = thumbs.art_thumbnail(dial.RING_OUTER_ART_DIR / face)
        row, col = divmod(index, 4)
        preset_tile = tile(
            tr(name), icon, settings.ring == name,
            lambda n=name: setters["ring"](n),
        )
        preset_tile.setToolTip(
            tr("Locked outer: {outer}").format(outer=outer_name)
        )
        grid.addWidget(preset_tile, row, col)
    return grid


def _finish_row(settings, setters, tr) -> QHBoxLayout:
    row = QHBoxLayout()
    for finish in constants.RING_FINISHES:
        row.addWidget(pill(
            tr(f"{finish.capitalize()} letters"), settings.ring_finish == finish,
            lambda f=finish: setters["ring_finish"](f),
        ))
    return row


def _inner_group(settings, setters, tr) -> QGroupBox:
    """THE INNER GALLERY (owner decree 2026-08-05): eight tiles, one per
    `constants.RING_INNERS` variant — applies to the ACTIVE preset (or
    the active custom ring), stored per-preset-name exactly like
    `ring_two_metals`/`ring_eye_shine` (`Settings.ring_inner`,
    `app.controller._resolve_ring_inner`)."""
    group = QGroupBox(tr("Inner (minute track)"))
    grid = QGridLayout(group)
    default = constants.RING_INNER_PRESET_DEFAULT.get(
        settings.ring, constants.RING_INNER_DEFAULT
    )
    active = settings.ring_inner.get(settings.ring, default)
    for index, inner in enumerate(constants.RING_INNERS):
        icon = thumbs.art_thumbnail(dial.RING_INNER_ART_DIR / f"{inner}.png")
        row, col = divmod(index, 4)
        grid.addWidget(
            tile(
                tr(inner.replace("_", " ").title()), icon, active == inner,
                lambda i=inner: setters["ring_inner"](i),
            ),
            row, col,
        )
    return group


def _crown_text_group(settings, card: dict, setters, tr) -> QGroupBox:
    """CROWN TEXT (owner decree 2026-08-05): the bundled presets show
    their existing motto text read-only (Dollar's Great Seal, DOMY/
    PILOT's cross words); a custom ring may TYPE its own text and pick
    an orientation (top/bottom)."""
    group = QGroupBox(tr("Crown text"))
    column = QVBoxLayout(group)
    if settings.ring in constants.RING_OUTER_LOCK:
        texts = " · ".join(entry["text"] for entry in card["motto"]) or tr("(none)")
        column.addWidget(QLabel(texts))
        return group
    edit = QLineEdit()
    edit.setPlaceholderText(tr("Custom crown text"))
    edit.setText(settings.custom_ring_crown_text.get(settings.ring, ""))
    edit.editingFinished.connect(
        lambda: setters["custom_ring_crown_text"](edit.text())
    )
    column.addLayout(_labeled(tr("Text"), edit))
    orient_row = QHBoxLayout()
    current = settings.custom_ring_crown_orientation.get(settings.ring, "top")
    for orientation in ("top", "bottom"):
        orient_row.addWidget(pill(
            tr(orientation.capitalize()), current == orientation,
            lambda o=orientation: setters["custom_ring_crown_orientation"](o),
        ))
    column.addLayout(orient_row)
    return group


def _labeled(text: str, widget) -> QHBoxLayout:
    row = QHBoxLayout()
    row.addWidget(QLabel(text))
    row.addWidget(widget, stretch=1)
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
