"""Display Section — `_DisplaySectionMixin`: the Opacity, Element
sizes and Archetype groups. Plain-Python mixin (no base class —
composed onto `dialog.SettingsDialog`'s `QDialog` shell, `research/
REFACTOR_PLAN.md` §7). See [Display Section](display_section.md) for
the full behavioral narrative.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
)

from config import constants, defaults


class _DisplaySectionMixin:
    def _build_opacity_group(self) -> QGroupBox:
        tr = self._tr
        group = QGroupBox(tr("Opacity"))
        form = QFormLayout(group)

        def initial(override: float | None, skin_value: float) -> tuple[int, int]:
            default = round(skin_value * 100)
            value = round(override * 100) if override is not None else default
            return value, default

        value, default = initial(self._settings.star_alpha, self._skin.star.day_alpha)
        self._star_slider, star_row = self._slider_row(value, default, "star")
        form.addRow(tr("Star"), star_row)
        # The Aura's sunlight and twilight opacities are INDEPENDENT
        # sliders (owner spec).
        value, default = initial(
            self._settings.aura_day_alpha, self._skin.background.day_alpha
        )
        self._aura_day_slider, day_row = self._slider_row(value, default, "aura_day")
        form.addRow(tr("Aura — sunlight"), day_row)
        value, default = initial(
            self._settings.aura_twilight_alpha, self._skin.background.twilight_alpha
        )
        self._aura_twilight_slider, twilight_row = self._slider_row(
            value, default, "aura_twilight"
        )
        form.addRow(tr("Aura — twilight"), twilight_row)
        if self._settings.pointer == "aurora":
            # Aurora has no separate twilight opacity (owner 2026-07-12:
            # the dedicated dawn/dusk COLORS carry the meaning — the
            # whole arc follows the daylight opacity).
            self._aura_twilight_slider.setEnabled(False)
        # The Moon marker DIMS below the horizon (owner spec
        # 2026-07-12) — a plain scale, not an override.
        self._moon_alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self._moon_alpha_slider.setRange(0, 100)
        moon_value = round(self._settings.moon_hidden_alpha * 100)
        self._moon_alpha_slider.setValue(moon_value)
        moon_label = QLabel(f"{moon_value}%")
        self._moon_alpha_slider.valueChanged.connect(
            lambda new_value: moon_label.setText(f"{new_value}%")
        )
        moon_reset = QPushButton(tr("Default"))
        moon_reset.clicked.connect(
            lambda: self._moon_alpha_slider.setValue(50)
        )
        moon_row = QHBoxLayout()
        moon_row.addWidget(self._moon_alpha_slider)
        moon_row.addWidget(moon_label)
        moon_row.addWidget(moon_reset)
        form.addRow(tr("Moon — below horizon"), moon_row)
        return group

    def _slider_row(self, value: int, default: int, which: str):
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(value)
        label = QLabel(f"{value}%")
        reset = QPushButton(self._tr("Skin default"))

        def on_moved(new_value: int) -> None:
            label.setText(f"{new_value}%")
            setattr(self, f"_{which}_override", True)

        def on_reset() -> None:
            slider.setValue(default)
            label.setText(f"{default}%")
            setattr(self, f"_{which}_override", False)

        slider.valueChanged.connect(on_moved)
        reset.clicked.connect(on_reset)
        row = QHBoxLayout()
        row.addWidget(slider)
        row.addWidget(label)
        row.addWidget(reset)
        return slider, row

    def _build_archetype_group(self) -> QGroupBox:
        """The archetype figures' names, ON/OFF (owner: "nemoj ispod
        nego u Settings — ON/OFF, spreman sam za predloge") — an
        INDEPENDENT switch from the weekday bodies' own Names option;
        the owner is open to a richer dropdown here later."""
        tr = self._tr
        group = QGroupBox(tr("Archetype"))
        form = QFormLayout(group)
        self._archetype_names_check = QCheckBox(tr("Archetype names"))
        self._archetype_names_check.setChecked(self._settings.archetype_names)
        form.addRow(self._archetype_names_check)
        return group

    def _build_sizes_group(self) -> QGroupBox:
        """Per-element size multipliers plus the shared hover-enlarge
        factor (the element under the cursor grows by it; 100% = off)."""
        tr = self._tr
        group = QGroupBox(tr("Element sizes"))
        form = QFormLayout(group)
        self._size_sliders: dict[str, QSlider] = {}
        rows = [
            ("earth_scale", tr("Earth"), constants.ELEMENT_SCALE_RANGE, 100),
            ("moon_scale", tr("Moon"), constants.ELEMENT_SCALE_RANGE, 100),
            ("slot_scale", tr("Slot"), constants.ELEMENT_SCALE_RANGE, 100),
            ("ring_letter_scale", tr("Ring letters"),
             constants.ELEMENT_SCALE_RANGE, 100),
            ("hover_enlarge", tr("Hover enlarge"),
             constants.HOVER_ENLARGE_RANGE, 120),
        ]
        for key, title, (low, high), default in rows:
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(round(low * 100), round(high * 100))
            value = round(getattr(self._settings, key) * 100)
            slider.setValue(value)
            label = QLabel(f"{value}%")
            slider.valueChanged.connect(
                lambda new_value, lab=label: lab.setText(f"{new_value}%")
            )
            reset = QPushButton(tr("Default"))
            reset.clicked.connect(
                lambda checked, s=slider, d=default: s.setValue(d)
            )
            row = QHBoxLayout()
            row.addWidget(slider)
            row.addWidget(label)
            row.addWidget(reset)
            self._size_sliders[key] = slider
            form.addRow(title, row)
        # The custom DIAMETER slider (owner 2026-07-17, ROADMAP 15e): any
        # value between the smallest and largest menu presets applies
        # exactly like a preset pick (the fixed presets stay in the menu).
        low, high = defaults.SIZE_PRESETS[0], defaults.SIZE_PRESETS[-1]
        self._diameter_slider = QSlider(Qt.Orientation.Horizontal)
        self._diameter_slider.setRange(low, high)
        self._diameter_slider.setValue(min(max(self._settings.diameter, low), high))
        diameter_label = QLabel(f"{self._diameter_slider.value()} px")
        # The exact numeric input (owner ROADMAP 15h item 12b): a spinbox
        # synced TWO-WAY with the slider — either one moves the other,
        # both stay in step, applied together on OK.
        self._diameter_spin = QSpinBox()
        self._diameter_spin.setRange(low, high)
        self._diameter_spin.setValue(self._diameter_slider.value())
        self._diameter_spin.setSuffix(" px")

        def sync_spin(value: int) -> None:
            diameter_label.setText(f"{value} px")
            if self._diameter_spin.value() != value:
                self._diameter_spin.blockSignals(True)
                self._diameter_spin.setValue(value)
                self._diameter_spin.blockSignals(False)

        def sync_slider(value: int) -> None:
            if self._diameter_slider.value() != value:
                self._diameter_slider.blockSignals(True)
                self._diameter_slider.setValue(value)
                self._diameter_slider.blockSignals(False)
            diameter_label.setText(f"{value} px")

        self._diameter_slider.valueChanged.connect(sync_spin)
        self._diameter_spin.valueChanged.connect(sync_slider)
        diameter_reset = QPushButton(tr("Default"))
        diameter_reset.clicked.connect(
            lambda checked: self._diameter_slider.setValue(
                defaults.DEFAULT_DIAL_DIAMETER
            )
        )
        diameter_row = QHBoxLayout()
        diameter_row.addWidget(self._diameter_slider)
        diameter_row.addWidget(diameter_label)
        diameter_row.addWidget(self._diameter_spin)
        diameter_row.addWidget(diameter_reset)
        form.addRow(tr("Diameter"), diameter_row)
        return group
