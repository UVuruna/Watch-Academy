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
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
)

from app.watch_face import tint_picker
from config import constants, dial, palette


class _ColorsSectionMixin:
    def _build_saturation_group(self) -> QGroupBox:
        """TWO independent saturation sliders (owner verdict: Saturation
        does not belong in Element sizes — Colors is where Palette and
        Ring tint already live). AURA (`pointer_saturation`, storage key
        unchanged — RE-SCOPED and RELABELED fix round E, 2026-07-19,
        slika 2: the label reads "Aura" now, and the slider scales only
        the colored period wedges behind/around the diamonds via
        `render.skin_geometry.aura_palette_for` — the star diamonds themselves
        no longer move with it, `render.skin_geometry.palette_for` stays raw).
        RING (`ring_saturation`) scales the ring band art's (plate +
        letter overlay) saturation at `render.layers.ring.RingLayer`, after
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
        style = self._palette_style       # normalized in the dialog shell
        group = QGroupBox(
            self._tr("Palette — {pointer} {style}").format(
                pointer=constants.POINTER_DISPLAY_NAMES[pointer],
                style=style.capitalize(),
            )
        )
        column = QVBoxLayout(group)
        chips_row = QHBoxLayout()
        # The Genesis wheel's inverted arms speak their own seats
        # (Bottom / Left / Right) — palette.pointer_arm_labels.
        self._arm_labels = palette.pointer_arm_labels(pointer, style)
        self._chips: list[QPushButton] = []
        for index, hue in enumerate(self._hues):
            chip = QPushButton()
            self._round_swatch(chip, hue, dial.PALETTE_SWATCH_PX)
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
        """Delegates to the shared builder (Watch Face Phase 4, Rule
        #5) — `app.watch_face.tint_picker.round_swatch`, extracted from
        here so the live-apply Watch Face Colors section draws the
        SAME swatch."""
        tint_picker.round_swatch(chip, hue, size, selected)

    def _paint_chip(self, chip: QPushButton, hue: str, index: int) -> None:
        self._round_swatch(chip, hue, dial.PALETTE_SWATCH_PX)
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
        presets (palette.RING_TINT_GROUPS, owner-tunable) show as TWO
        labeled Paint-style grids — Lighter and Darker (owner
        2026-07-15: the one flat palette read too light) — the name in
        the tooltip, the active swatch ringed white — plus a free
        color picker."""
        tr = self._tr
        group = QGroupBox(tr("Clock tint — dial, hands and Umbra (letters excluded)"))
        column = QVBoxLayout(group)
        # Delegates to the shared builder (Watch Face Phase 4, Rule #5):
        # `app.watch_face.tint_picker.build_preset_grids`, extracted
        # from here so the live-apply Watch Face Colors section's Ring
        # tint group draws the SAME grids.
        grids, self._tint_swatches = tint_picker.build_preset_grids(
            tr, palette.RING_TINT_GROUPS, self._ring_tint,
            self._set_ring_tint, palette.RING_TINT_NONE_SWATCH,
        )
        column.addLayout(grids)
        row = tint_picker.build_custom_row(
            tr, self._ring_tint, palette.RING_TINT_PICKER_SEED,
            self._set_ring_tint, "Pick the ring tint",
        )
        self._ring_tint_label = QLabel()
        row.addWidget(self._ring_tint_label)
        column.addLayout(row)
        self._show_ring_tint()
        return group

    def _set_ring_tint(self, hue: str | None) -> None:
        self._ring_tint = hue
        self._show_ring_tint()

    def _show_ring_tint(self) -> None:
        # Delegates to the shared builders (Watch Face Phase 4, Rule
        # #5) — the label reads like the hover (owner 2026-07-15): the
        # preset's NAME beside the hex, "Gray (default)" for None.
        self._ring_tint_label.setText(
            tint_picker.tint_label_text(
                self._tr, self._ring_tint, palette.RING_TINT_GROUPS,
                "Gray (default)",
            )
        )
        tint_picker.repaint_selection(
            self._tint_swatches, self._ring_tint, palette.RING_TINT_NONE_SWATCH,
        )
