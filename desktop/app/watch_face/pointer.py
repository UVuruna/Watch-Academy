"""Pointer section (R-04/R-05, see pointer.md) — the Watch Face
window's Pointer page: pointer-variant gallery (icon =
`thumbs.pointer_swatch_icon`'s palette-wheel swatch, the honest fallback
documented in thumbs.md), the wheel/palette-style pills, the
shape/curvature/edge rows and "Hide night borders" — moved verbatim from
the RETIRED `design_window.DesignDialog._pointer_tab` (same conditional
rules, Rule #5; Phase 6 FINAL cleanup deleted that window outright), plus
R-05's "Daylight - Night" checkbox (moved here from the also-RETIRED
`app/settings_dialog/display_section.py`'s Archetype group — same
`daylight` setting, now with only ONE reader/writer).

R-06's Earth group (moved here from `design_window.DesignDialog.
_earth_tab`) MOVED AGAIN, 2026-08-10: the owner ruled on the
rendering-proposals page that the Moon and the Earth are part of the
HANDS system — "they are what MOVES and points" — so the whole group,
plus the position-pointer SHAPE gallery, now lives in `bodies.py`'s
"Earth" group beside the Hands gallery. This module keeps only the
pointer VARIANT itself (the star/polygon/aurora/etc. shape the HOUR/
MINUTE hands ride).
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QGroupBox, QHBoxLayout, QLabel, QSlider, QVBoxLayout, QWidget,
)

from app.watch_face import thumbs
from app.watch_face.widgets import flow_gallery, pill, tile
from config import constants
from render.skin_geometry import daylight_active


def build(settings, setters: dict, tr) -> QWidget:
    """Named groups since the 2026-08-06 design pass: the gallery, the
    palette pills and the shape rows each sit under their own heading —
    bare rows floating in the column read as anonymous buttons."""
    layout = QVBoxLayout()
    layout.addWidget(_pointer_gallery(settings, setters, tr))
    palette_group = QGroupBox(tr("Palette"))
    palette_group.setLayout(_palette_style_row(settings, setters, tr))
    layout.addWidget(palette_group)
    layout.addWidget(_palette_hues_group(settings, setters, tr))
    if settings.pointer != "aurora":
        shape_group = QGroupBox(tr("Shape"))
        shape_layout = QVBoxLayout(shape_group)
        _add_shape_rows(shape_layout, settings, setters, tr)
        _add_night_borders(shape_layout, settings, setters, tr)
        layout.addWidget(shape_group)
    _add_daylight_switch(layout, settings, setters, tr)
    widget = QWidget()
    widget.setLayout(layout)
    return widget


def _palette_hues_group(settings, setters, tr) -> QGroupBox:
    """The pointer hue chips, MOVED here from the Colors page (owner
    ballot verdict 5B, 2026-08-14): the group changes with the pointer
    picked right above it, so it lives beside that pick. R-21 item 2's
    LIVE-APPLY law is unchanged — `setters["palettes"]` stores the
    WHOLE hue tuple at once, preset-equals-no-override."""
    from PySide6.QtGui import QColor
    from PySide6.QtWidgets import QColorDialog, QPushButton

    from app.ui_style import tooltip_wrap
    from app.watch_face import tint_picker
    from config import dial, palette

    pointer_key = settings.pointer
    style = palette.effective_palette_style(pointer_key, settings.palette_style)
    key = f"{pointer_key}_{style}"
    preset = palette.PALETTE_PRESETS[(pointer_key, style)]
    hues = list(settings.palettes.get(key, preset))
    arm_labels = palette.pointer_arm_labels(pointer_key, style)
    group = QGroupBox(
        tr("Palette — {pointer} {style}").format(
            pointer=constants.POINTER_DISPLAY_NAMES[pointer_key],
            style=style.capitalize(),
        )
    )
    column = QVBoxLayout(group)
    row = QHBoxLayout()

    def pick(index: int) -> None:
        chosen = QColorDialog.getColor(QColor(hues[index]), None, "Pick a hue")
        if not chosen.isValid():
            return
        new_hues = list(hues)
        new_hues[index] = chosen.name().upper()
        setters["palettes"](pointer_key, style, tuple(new_hues))

    for index, hue in enumerate(hues):
        chip = QPushButton()
        tint_picker.round_swatch(chip, hue, dial.PALETTE_SWATCH_PX)
        chip.setToolTip(tooltip_wrap(f"{tr(arm_labels[index])} — {hue}"))
        chip.clicked.connect(lambda checked, i=index: pick(i))
        row.addWidget(chip)
    row.addStretch(1)
    # ALG-5: "Reset to preset" keeps its own row (a text button is not a
    # sibling of twelve identical circles).
    reset = QPushButton(tr("Reset to preset"))
    reset.clicked.connect(
        lambda: setters["palettes"](pointer_key, style, tuple(preset))
    )
    reset_row = QHBoxLayout()
    reset_row.addWidget(reset)
    reset_row.addStretch(1)
    column.addLayout(row)
    column.addLayout(reset_row)
    return group


def _pointer_gallery(settings, setters, tr) -> QWidget:
    """Width-aware flow since the owner's 2026-08-09 review caught the
    fixed 3-column wrap leaving the row half empty (his "3-3-2 kad ima
    prostora za 4-3") — `widgets.flow_gallery`, the one gallery shape."""
    variants = sorted(
        constants.POINTER_DIAL_COUNTS.items(), key=lambda item: item[1]
    )
    tiles = []
    for variant, count in variants:
        title = f"{constants.POINTER_DISPLAY_NAMES[variant]} ({count})"
        style = (
            settings.palette_style if variant == settings.pointer else "primary"
        )
        icon = thumbs.pointer_swatch_icon(variant, style)
        tiles.append(tile(
            tr(title), icon, settings.pointer == variant,
            lambda v=variant: setters["pointer"](v),
        ))
    return flow_gallery(tiles)


def _palette_style_row(settings, setters, tr) -> QHBoxLayout:
    row = QHBoxLayout()
    labels = constants.POINTER_PALETTE_LABELS.get(
        settings.pointer, constants.POINTER_PALETTE_LABELS["default"]
    )
    for style, label in zip(
        constants.palette_styles_for(settings.pointer), labels
    ):
        row.addWidget(pill(
            tr(label), settings.palette_style == style,
            lambda s=style: setters["palette_style"](s),
        ))
    return row


def _add_shape_rows(layout: QVBoxLayout, settings, setters, tr) -> None:
    shape_row = QHBoxLayout()
    for shape in constants.POINTER_SHAPES:
        shape_row.addWidget(pill(
            tr(shape.capitalize()), settings.pointer_shape == shape,
            lambda s=shape: setters["pointer_shape"](s),
        ))
    layout.addLayout(shape_row)
    if not (
        settings.pointer in constants.POLYGON_POINTERS
        and settings.pointer_shape == "polygon"
    ):
        return
    low, high = constants.POLYGON_CURVATURE_RANGE
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setRange(int(low * 100), int(high * 100))
    slider.setValue(int(round(settings.polygon_curvature * 100)))
    percent_label = QLabel(f"{slider.value()}%")
    slider.valueChanged.connect(
        lambda value, label=percent_label: label.setText(f"{value}%")
    )
    slider.sliderReleased.connect(
        lambda: setters["polygon_curvature"](slider.value() / 100.0)
    )
    curvature_row = QHBoxLayout()
    curvature_row.addWidget(QLabel(tr("Curvature")))
    curvature_row.addWidget(slider)
    curvature_row.addWidget(percent_label)
    layout.addLayout(curvature_row)
    edge_row = QHBoxLayout()
    for edge, title in (("smooth", "Smooth concave"), ("notched", "V-notched")):
        edge_row.addWidget(pill(
            tr(title), settings.polygon_edge == edge,
            lambda e=edge: setters["polygon_edge"](e),
        ))
    layout.addLayout(edge_row)


def _add_night_borders(layout: QVBoxLayout, settings, setters, tr) -> None:
    checkbox = QCheckBox(tr("Hide night borders"))
    checkbox.setChecked(settings.hide_night_borders)
    checkbox.setEnabled(daylight_active(settings))
    checkbox.toggled.connect(setters["hide_night_borders"])
    layout.addWidget(checkbox)


def _add_daylight_switch(layout: QVBoxLayout, settings, setters, tr) -> None:
    """R-05: moved here from Settings' Archetype group
    (`display_section._build_archetype_group`) — same stored `daylight`
    key, only the location changed. Enabled only on the pointers that
    actually carry the switch (`constants.DAYLIGHT_SWITCH_POINTERS`, the
    SAME set `daylight_active` reads) — an intentional tightening over
    the old Settings copy (always enabled there), since this copy now
    sits beside the pointer picker it gates on."""
    checkbox = QCheckBox(tr("Daylight - Night"))
    checkbox.setChecked(settings.daylight)
    checkbox.setEnabled(settings.pointer in constants.DAYLIGHT_SWITCH_POINTERS)
    checkbox.toggled.connect(lambda value: setters["daylight"](value))
    layout.addWidget(checkbox)
