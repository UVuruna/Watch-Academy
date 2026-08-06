"""Size section (see size.md) — the diameter slider + spinbox + Default
+ the five `dial.SIZE_PRESETS` buttons (the two-way slider/spinbox sync
`display_section._build_sizes_group` uses, plus `design_window.
DesignDialog._size_tab`'s preset row) and every element scale slider —
Earth, Moon, Complications (`slot_scale`), Indices (`ring_letter_scale`),
Crown Text (`crown_text_scale`), Hover enlarge — wired to the SAME stored
setting keys the Settings dialog's "Element sizes" group uses (Rule #5;
only the on-screen labels differ, per the owner's Watch Face naming).

CROWN TEXT (R-24/Phase-6-debt correction, owner 2026-08-05: "Crown
tekst je onaj tekst koji piše oko sata — faith, hope, suffering") — the
outer Great Seal crown text arc IS this element
(`skins.manifest.SkinDefinition.crown_text_scale`,
`render.layers.ring.RingLayer._draw_crown_text`); it multiplies ON TOP of
`ring_letter_scale` (unaffected). Its row greys out with a tooltip when
the active ring preset carries no crown text
(`setters["ring_has_crown_text"]`) — the one row in `_SCALE_ROWS` that is
not always meaningful, so `_scale_form` special-cases it by key rather
than widening every row's shape for one exception.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QSpinBox,
    QVBoxLayout, QWidget,
)

from app.watch_face.widgets import pill
from config import constants, dial

# (setting key, on-screen label, (low, high) range, default*100)
_SCALE_ROWS = (
    ("earth_scale", "Earth", constants.ELEMENT_SCALE_RANGE, 100),
    ("moon_scale", "Moon", constants.ELEMENT_SCALE_RANGE, 100),
    ("slot_scale", "Complications", constants.ELEMENT_SCALE_RANGE, 100),
    ("ring_letter_scale", "Indices", constants.ELEMENT_SCALE_RANGE, 100),
    ("crown_text_scale", "Crown Text", constants.ELEMENT_SCALE_RANGE, 100),
    ("hover_enlarge", "Hover enlarge", constants.HOVER_ENLARGE_RANGE, 120),
)


def build(settings, setters: dict, tr) -> QWidget:
    layout = QVBoxLayout()
    layout.addLayout(_diameter_row(settings, setters, tr))
    layout.addLayout(_scale_form(settings, setters, tr))
    widget = QWidget()
    widget.setLayout(layout)
    return widget


def _diameter_row(settings, setters, tr) -> QVBoxLayout:
    column = QVBoxLayout()
    preset_row = QHBoxLayout()
    for preset in dial.SIZE_PRESETS:
        preset_row.addWidget(_preset_pill(preset, settings, setters, tr))
    column.addLayout(preset_row)

    low, high = dial.SIZE_PRESETS[0], dial.SIZE_PRESETS[-1]
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setRange(low, high)
    slider.setSingleStep(dial.MENU_SIZE_SLIDER_STEP)
    slider.setPageStep(dial.MENU_SIZE_SLIDER_STEP * 5)
    slider.setValue(settings.diameter)
    value_label = QLabel(f"{settings.diameter} px")
    spin = QSpinBox()
    spin.setRange(low, high)
    spin.setValue(settings.diameter)
    spin.setSuffix(" px")

    def sync_spin(value: int) -> None:
        value_label.setText(f"{value} px")
        if spin.value() != value:
            spin.blockSignals(True)
            spin.setValue(value)
            spin.blockSignals(False)

    def sync_slider(value: int) -> None:
        if slider.value() != value:
            slider.blockSignals(True)
            slider.setValue(value)
            slider.blockSignals(False)
        value_label.setText(f"{value} px")

    slider.valueChanged.connect(sync_spin)
    spin.valueChanged.connect(sync_slider)
    slider.sliderReleased.connect(lambda: setters["diameter"](slider.value()))
    spin.editingFinished.connect(lambda: setters["diameter"](spin.value()))
    reset = QPushButton(tr("Default"))
    reset.clicked.connect(
        lambda: setters["diameter"](dial.DEFAULT_DIAL_DIAMETER)
    )
    row = QHBoxLayout()
    row.addWidget(slider)
    row.addWidget(value_label)
    row.addWidget(spin)
    row.addWidget(reset)
    column.addLayout(row)
    return column


def _preset_pill(preset: int, settings, setters, tr):
    return pill(
        f"{preset} px", settings.diameter == preset,
        lambda p=preset: setters["diameter"](p),
    )


def _scale_form(settings, setters, tr) -> QFormLayout:
    form = QFormLayout()
    for key, title, (low, high), default in _SCALE_ROWS:
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(round(low * 100), round(high * 100))
        value = round(getattr(settings, key) * 100)
        slider.setValue(value)
        label = QLabel(f"{value}%")
        slider.valueChanged.connect(
            lambda new_value, lab=label: lab.setText(f"{new_value}%")
        )
        slider.sliderReleased.connect(
            lambda s=slider, k=key: setters[k](s.value() / 100.0)
        )
        reset = QPushButton(tr("Default"))
        reset.clicked.connect(_make_reset(slider, key, default, setters))
        # CROWN TEXT (owner correction 2026-08-05): the one row that is
        # not always meaningful — greyed out with a tooltip when the
        # active ring preset carries no crown text (module docstring).
        if key == "crown_text_scale" and not setters["ring_has_crown_text"]():
            slider.setEnabled(False)
            reset.setEnabled(False)
            tooltip = tr(
                "The active ring preset carries no Crown Text (Great Seal inscription)."
            )
            slider.setToolTip(tooltip)
            reset.setToolTip(tooltip)
        row = QHBoxLayout()
        row.addWidget(slider)
        row.addWidget(label)
        row.addWidget(reset)
        form.addRow(tr(title), row)
    return form


def _make_reset(slider: QSlider, key: str, default: int, setters: dict):
    """A live-apply Default (unlike the Settings dialog's transactional
    one, which only resets the widget — here the reset also commits
    immediately, since this window has no OK to commit on later)."""
    def reset() -> None:
        slider.setValue(default)
        setters[key](default / 100.0)
    return reset
