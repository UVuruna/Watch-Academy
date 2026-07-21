"""Colors Section — `_ColorsSectionMixin`: the Saturation, Palette and
Clock (ring) tint groups. Plain-Python mixin (no base class — composed
onto `dialog.SettingsDialog`'s `QDialog` shell, `research/
REFACTOR_PLAN.md` §7). See [Colors Section](colors_section.md) for the
full behavioral narrative.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
)

from config import constants, defaults


class _ColorsSectionMixin:
    def _build_saturation_group(self) -> QGroupBox:
        """TWO independent saturation sliders (owner verdict: Saturation
        does not belong in Element sizes — Colors is where Palette and
        Ring tint already live). AURA (`pointer_saturation`, storage key
        unchanged — RE-SCOPED and RELABELED fix round E, 2026-07-19,
        slika 2: the label reads "Aura" now, and the slider scales only
        the colored period wedges behind/around the diamonds via
        `render.layers.aura_palette_for` — the star diamonds themselves
        no longer move with it, `render.layers.palette_for` stays raw).
        RING (`ring_saturation`) scales the ring band art's (plate +
        letter overlay) saturation at `render.layers.RingLayer`, after
        the ring_tint recolor. Both 0-100%, default 100% (unchanged);
        "Default" resets each to 100."""
        tr = self._tr
        group = QGroupBox(tr("Saturation"))
        form = QFormLayout(group)

        def add_row(title: str, value_attr: str, range_const, step_const):
            low, high = range_const
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(round(low * 100), round(high * 100))
            slider.setSingleStep(step_const)
            value = round(getattr(self._settings, value_attr) * 100)
            slider.setValue(value)
            label = QLabel(f"{value}%")
            slider.valueChanged.connect(
                lambda new_value, lab=label: lab.setText(f"{new_value}%")
            )
            reset = QPushButton(tr("Default"))
            reset.clicked.connect(lambda checked, s=slider: s.setValue(100))
            row = QHBoxLayout()
            row.addWidget(slider)
            row.addWidget(label)
            row.addWidget(reset)
            form.addRow(title, row)
            return slider

        self._pointer_saturation_slider = add_row(
            tr("Aura"), "pointer_saturation",
            constants.POINTER_SATURATION_RANGE,
            constants.POINTER_SATURATION_SLIDER_STEP,
        )
        self._ring_saturation_slider = add_row(
            tr("Ring"), "ring_saturation",
            constants.RING_SATURATION_RANGE,
            constants.RING_SATURATION_SLIDER_STEP,
        )
        return group

    def _build_palette_group(self) -> QGroupBox:
        """The active (pointer, style) hues as BIG color circles (owner
        spec 2026-07-11) — hovering one names the arm position it colors
        (Top / Bottom Left / North-East…); clicking opens the picker."""
        pointer = self._settings.pointer
        style = self._settings.palette_style
        group = QGroupBox(
            self._tr("Palette — {pointer} {style}").format(
                pointer=constants.POINTER_DISPLAY_NAMES[pointer],
                style=style.capitalize(),
            )
        )
        column = QVBoxLayout(group)
        chips_row = QHBoxLayout()
        self._arm_labels = constants.POINTER_ARM_LABELS[pointer]
        self._chips: list[QPushButton] = []
        for index, hue in enumerate(self._hues):
            chip = QPushButton()
            self._round_swatch(chip, hue, defaults.PALETTE_SWATCH_PX)
            chip.setToolTip(f"{self._tr(self._arm_labels[index])} — {hue}")
            chip.clicked.connect(lambda checked, i=index: self._pick_color(i))
            self._chips.append(chip)
            chips_row.addWidget(chip)
        chips_row.addStretch(1)
        reset = QPushButton(self._tr("Reset to preset"))
        reset.clicked.connect(self._reset_palette)
        chips_row.addWidget(reset)
        column.addLayout(chips_row)
        return group

    @staticmethod
    def _round_swatch(
        chip: QPushButton, hue: str, size: int, selected: bool = False
    ) -> None:
        """Paint-style color circle (owner spec): a plain filled round
        button; the selected ring-tint swatch wears a white ring."""
        border = "2px solid #FFFFFF" if selected else "1px solid #666"
        chip.setFixedSize(size, size)
        chip.setStyleSheet(
            f"background-color: {hue}; border: {border};"
            f"border-radius: {size // 2}px;"
        )

    def _paint_chip(self, chip: QPushButton, hue: str, index: int) -> None:
        self._round_swatch(chip, hue, defaults.PALETTE_SWATCH_PX)
        chip.setToolTip(f"{self._tr(self._arm_labels[index])} — {hue}")

    def _pick_color(self, index: int) -> None:
        chosen = QColorDialog.getColor(
            QColor(self._hues[index]), self, "Pick a hue"
        )
        if not chosen.isValid():
            return
        self._hues[index] = chosen.name().upper()
        self._paint_chip(self._chips[index], self._hues[index], index)

    def _reset_palette(self) -> None:
        self._hues = list(self._preset)
        for index, (chip, hue) in enumerate(zip(self._chips, self._hues)):
            self._paint_chip(chip, hue, index)

    def _build_ring_tint_group(self) -> QGroupBox:
        """One hue recolors the whole clock body — ring art, hands and
        Umbra (channel multiply; the letter art stays untouched). The
        presets (defaults.RING_TINT_GROUPS, owner-tunable) show as TWO
        labeled Paint-style grids — Lighter and Darker (owner
        2026-07-15: the one flat palette read too light) — the name in
        the tooltip, the active swatch ringed white — plus a free
        color picker."""
        tr = self._tr
        group = QGroupBox(tr("Clock tint — dial, hands and Umbra (letters excluded)"))
        column = QVBoxLayout(group)
        self._tint_swatches: list[tuple[QPushButton, str | None]] = []
        per_row = defaults.RING_TINT_SWATCHES_PER_ROW
        for title, presets in defaults.RING_TINT_GROUPS.items():
            label = QLabel(tr(title))
            label.setStyleSheet("font-weight: bold;")
            column.addWidget(label)
            grid = QGridLayout()
            grid.setHorizontalSpacing(4)
            grid.setVerticalSpacing(4)
            for index, (name, hue) in enumerate(presets.items()):
                chip = QPushButton()
                chip.setToolTip(
                    f"{tr(name)} — {hue}"
                    if hue
                    else f"{tr(name)} — {tr('the untouched art')}"
                )
                chip.clicked.connect(
                    lambda checked, chosen=hue: self._set_ring_tint(chosen)
                )
                self._tint_swatches.append((chip, hue))
                grid.addWidget(chip, index // per_row, index % per_row)
            grid.setColumnStretch(per_row, 1)
            column.addLayout(grid)
        row = QHBoxLayout()
        custom = QPushButton(tr("Custom…"))
        custom.clicked.connect(self._pick_ring_tint)
        row.addWidget(custom)
        row.addStretch(1)
        self._ring_tint_label = QLabel()
        row.addWidget(self._ring_tint_label)
        column.addLayout(row)
        self._show_ring_tint()
        return group

    def _set_ring_tint(self, hue: str | None) -> None:
        self._ring_tint = hue
        self._show_ring_tint()

    def _pick_ring_tint(self) -> None:
        chosen = QColorDialog.getColor(
            QColor(self._ring_tint or "#808080"), self, "Pick the ring tint"
        )
        if not chosen.isValid():
            return
        self._set_ring_tint(chosen.name().upper())

    def _show_ring_tint(self) -> None:
        # The label speaks like the hover (owner 2026-07-15): the
        # preset's NAME beside the hex; a custom hue shows bare hex.
        name = next(
            (
                preset_name
                for presets in defaults.RING_TINT_GROUPS.values()
                for preset_name, hue in presets.items()
                if hue == self._ring_tint and hue is not None
            ),
            None,
        )
        if self._ring_tint is None:
            text = self._tr("Gray (default)")
        elif name is not None:
            text = f"{self._tr(name)} — {self._ring_tint}"
        else:
            text = self._ring_tint
        self._ring_tint_label.setText(text)
        # Repaint every swatch — the one matching the active tint is
        # ringed white ("Gray"/None shows as the bare art gray).
        for chip, hue in self._tint_swatches:
            self._round_swatch(
                chip,
                hue or "#9A9A9A",
                defaults.RING_TINT_SWATCH_PX,
                selected=(hue == self._ring_tint),
            )
