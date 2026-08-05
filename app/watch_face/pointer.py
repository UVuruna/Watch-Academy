"""Pointer section (R-04/R-05/R-06, see pointer.md) — the Watch Face
window's Pointer page: pointer-variant gallery (icon =
`thumbs.pointer_swatch_icon`'s palette-wheel swatch, the honest fallback
documented in thumbs.md), the wheel/palette-style pills, the
shape/curvature/edge rows and "Hide night borders" — moved verbatim from
`design_window.DesignDialog._pointer_tab` (same conditional rules, Rule
#5), plus R-05's "Daylight - Night" checkbox (moved here from
`app/settings_dialog/display_section.py`'s Archetype group — the OLD
copy stays there until Phase 6, both wire the SAME `daylight` setting)
and R-06's Earth group (moved from `design_window.DesignDialog.
_earth_tab` — sizes do NOT live here, see size.py).
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QGridLayout, QHBoxLayout, QLabel, QSlider, QVBoxLayout, QWidget,
)

from app.watch_face import thumbs
from app.watch_face.widgets import pill, tile
from config import constants, continents, dial
from render.skin_geometry import daylight_active


def build(settings, setters: dict, tr) -> QWidget:
    layout = QVBoxLayout()
    layout.addLayout(_pointer_gallery(settings, setters, tr))
    layout.addLayout(_palette_style_row(settings, setters, tr))
    if settings.pointer != "aurora":
        _add_shape_rows(layout, settings, setters, tr)
        _add_night_borders(layout, settings, setters, tr)
    _add_daylight_switch(layout, settings, setters, tr)
    layout.addWidget(_earth_group(settings, setters, tr))
    widget = QWidget()
    widget.setLayout(layout)
    return widget


def _pointer_gallery(settings, setters, tr) -> QGridLayout:
    grid = QGridLayout()
    variants = sorted(
        constants.POINTER_DIAL_COUNTS.items(), key=lambda item: item[1]
    )
    for index, (variant, count) in enumerate(variants):
        title = f"{constants.POINTER_DISPLAY_NAMES[variant]} ({count})"
        style = (
            settings.palette_style if variant == settings.pointer else "primary"
        )
        icon = thumbs.pointer_swatch_icon(variant, style)
        row, col = divmod(index, 3)
        grid.addWidget(
            tile(
                tr(title), icon, settings.pointer == variant,
                lambda v=variant: setters["pointer"](v),
            ),
            row, col,
        )
    return grid


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


def _earth_group(settings, setters, tr) -> QWidget:
    """R-06: moved verbatim from `design_window.DesignDialog.
    _earth_tab` — sizes do NOT live here (see `size.py`'s Earth/Moon
    scale sliders)."""
    layout = QVBoxLayout()
    style_row = QHBoxLayout()
    for style, title in (("clean", "Clean"), ("atmo", "Atmosphere")):
        icon = thumbs.art_thumbnail(
            continents.EARTH_ART_DIR / f"earth_{style}_europe_day.png"
        )
        style_row.addWidget(tile(
            tr(title), icon, settings.earth_style == style,
            lambda s=style: setters["earth_style"](s),
        ))
    layout.addLayout(style_row)
    label_row = QHBoxLayout()
    enabled = settings.diameter >= dial.FULL_TEXT_MIN_DIAMETER
    for mode, title in (
        ("date", "Date"), ("weekday", "Weekday"),
        ("date_weekday", "Date & Weekday"), ("full", "Full Date"),
    ):
        is_active = settings.earth_label == mode
        button = pill(
            tr(title), is_active,
            lambda m=mode, was=is_active: setters["earth_label"](m, not was),
        )
        button.setEnabled(enabled)
        label_row.addWidget(button)
    layout.addLayout(label_row)
    group = QWidget()
    group.setLayout(layout)
    return group
