"""Custom Art Section — `_CustomArtSectionMixin`: the Custom ring and
Custom hands builders. Plain-Python mixin (no base class — composed
onto `dialog.SettingsDialog`'s `QDialog` shell, `research/
REFACTOR_PLAN.md` §7). See [Custom Art Section](custom_art_section.md)
for the full behavioral narrative.
"""

import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from config import constants, defaults


class _CustomArtSectionMixin:
    def _build_custom_ring_group(self) -> QGroupBox:
        """The ring card builder: pick a layout (Flame / Chalice /
        Seal), a library letter per position and a unique name — the
        new card joins Theme ▸ Ring with the gold/silver metal rules."""
        tr = self._tr
        self._custom_rings = list(self._settings.custom_rings)
        group = QGroupBox(tr("Custom ring"))
        column = QVBoxLayout(group)
        top = QHBoxLayout()
        self._ring_layout_combo = QComboBox()
        layout_labels = {
            "flame": "Flame — Masculine ({n} letters)",
            "chalice": "Chalice — Feminine ({n} letters)",
            "seal": "Seal — Union ({n} letters)",
        }
        for key, layout in constants.RING_LAYOUTS.items():
            self._ring_layout_combo.addItem(
                tr(layout_labels[key]).format(n=len(layout["positions"])),
                key,
            )
        self._ring_layout_combo.currentIndexChanged.connect(
            self._rebuild_ring_slots
        )
        top.addWidget(self._ring_layout_combo)
        self._ring_name_edit = QLineEdit()
        self._ring_name_edit.setPlaceholderText(tr("Unique name"))
        top.addWidget(self._ring_name_edit)
        add = QPushButton(tr("Add ring"))
        add.clicked.connect(self._add_custom_ring)
        top.addWidget(add)
        column.addLayout(top)
        self._ring_slot_row = QHBoxLayout()
        column.addLayout(self._ring_slot_row)
        self._ring_slot_combos: dict[int, QComboBox] = {}
        self._custom_ring_status = QLabel(
            tr("{n} custom ring(s) saved").format(n=len(self._custom_rings))
        )
        column.addWidget(self._custom_ring_status)
        self._rebuild_ring_slots()
        return group

    def _rebuild_ring_slots(self) -> None:
        while self._ring_slot_row.count():
            item = self._ring_slot_row.takeAt(0)
            if item.widget() is not None:
                item.widget().deleteLater()
            elif item.layout() is not None:
                while item.layout().count():
                    inner = item.layout().takeAt(0)
                    if inner.widget() is not None:
                        inner.widget().deleteLater()
        self._ring_slot_combos = {}
        layout_key = self._ring_layout_combo.currentData()
        for position in constants.RING_LAYOUTS[layout_key]["positions"]:
            cell = QVBoxLayout()
            cell.addWidget(QLabel(f"{position}h"))
            combo = self._letter_combo(position)
            cell.addWidget(combo)
            self._ring_slot_combos[position] = combo
            self._ring_slot_row.addLayout(cell)

    def _letter_combo(self, position: int) -> QComboBox:
        """The letter library GROUPED into sections (owner spec
        2026-07-11): Latin / Greek / Numbers / Symbols — the section
        headers are visible in the dropdown but not selectable. A
        NUMBER only fits its own hour (owner rule 2026-07-12), so the
        Numbers section offers at most the position's own number."""
        combo = QComboBox()
        model = QStandardItemModel(combo)
        for group, glyphs in constants.RING_LETTER_GROUPS.items():
            if group == "Numbers":
                glyphs = tuple(g for g in glyphs if int(g) == position)
                if not glyphs:
                    continue             # 24h has no number — Ω's seat
            header = QStandardItem(f"— {self._tr(group)} —")
            header.setFlags(Qt.ItemFlag.NoItemFlags)
            model.appendRow(header)
            for glyph in glyphs:
                model.appendRow(QStandardItem(glyph))
        combo.setModel(model)
        combo.setCurrentIndex(1)         # the first real glyph, not a header
        return combo

    def _add_custom_ring(self) -> None:
        from data.rings import ring_presets, validate_preset

        layout_key = self._ring_layout_combo.currentData()
        entry = {
            "name": self._ring_name_edit.text().strip(),
            "positions": list(constants.RING_LAYOUTS[layout_key]["positions"]),
            "letters": [
                combo.currentText()
                for combo in self._ring_slot_combos.values()
            ],
        }
        try:
            card = validate_preset(entry)
            ring_presets(tuple(self._custom_rings) + (entry,))  # name clash?
        except ValueError as error:
            self._custom_ring_status.setText(str(error))
            return
        self._custom_rings.append(
            {
                "name": card["name"],
                "positions": list(card["positions"]),
                "letters": list(card["letters"]),
            }
        )
        self._custom_ring_status.setText(
            self._tr(
                "Added '{name}' — OK saves it; find it under Design ▸ Ring"
            ).format(name=card["name"])
        )
        self._ring_name_edit.clear()

    def _build_custom_hands_group(self) -> QGroupBox:
        """The hand-pack builder: three PNGs pointing UP, a pivot per
        hand (x from the left, 'center' by default; y in pixels from
        the bottom), a bottom-up z-order and a unique name. Add writes
        the pack folder immediately (files, not settings) — it appears
        under Design ▸ Hands."""
        from data.hands import HAND_NAMES, hand_packs

        tr = self._tr
        group = QGroupBox(tr("Custom hands"))
        column = QVBoxLayout(group)
        note = QLabel(tr(
            "PNG images pointing UP. Colored art grays out so the clock "
            "tint can recolor it; the tip-to-pivot length sets every "
            "size automatically."
        ))
        note.setWordWrap(True)
        column.addWidget(note)
        self._hand_files: dict[str, str | None] = {h: None for h in HAND_NAMES}
        self._hand_pivots: dict[str, tuple[QSpinBox, QSpinBox]] = {}
        labels = {"hours": "Hours", "minutes": "Minutes", "seconds": "Seconds"}
        for hand in HAND_NAMES:
            row = QHBoxLayout()
            row.addWidget(QLabel(tr(labels[hand])))
            pick = QPushButton(tr("Browse…"))
            pick.clicked.connect(lambda checked, h=hand: self._pick_hand(h))
            row.addWidget(pick, stretch=1)
            row.addWidget(QLabel(tr("Pivot X")))
            x_spin = QSpinBox()
            x_spin.setRange(-1, 8192)
            x_spin.setValue(-1)
            x_spin.setSpecialValueText(tr("center"))
            x_spin.setToolTip(tr(
                "Rotation center from the LEFT edge in pixels of your "
                "image — leave 'center' for symmetric hands."
            ))
            row.addWidget(x_spin)
            row.addWidget(QLabel(tr("Pivot Y")))
            y_spin = QSpinBox()
            y_spin.setRange(0, 8192)
            y_spin.setValue(15)
            y_spin.setToolTip(tr(
                "Rotation center ABOVE the image bottom in pixels — the "
                "hand must point UP."
            ))
            row.addWidget(y_spin)
            self._hand_pivots[hand] = (x_spin, y_spin)
            self._hand_buttons = getattr(self, "_hand_buttons", {})
            self._hand_buttons[hand] = pick
            column.addLayout(row)
        bottom = QHBoxLayout()
        bottom.addWidget(QLabel(tr("Z-order (bottom → top)")))
        self._hand_z_combo = QComboBox()
        import itertools
        for order in itertools.permutations(HAND_NAMES):
            self._hand_z_combo.addItem(
                " · ".join(tr(labels[h]) for h in order), list(order)
            )
        bottom.addWidget(self._hand_z_combo, stretch=1)
        self._hand_name_edit = QLineEdit()
        self._hand_name_edit.setPlaceholderText(tr("Unique name"))
        bottom.addWidget(self._hand_name_edit)
        add = QPushButton(tr("Add hands"))
        add.clicked.connect(self._add_custom_hands)
        bottom.addWidget(add)
        column.addLayout(bottom)
        user_count = sum(
            1 for pack in hand_packs().values()
            if pack["dir"].parent != defaults.paths.assets_dir() / "hands"
        )
        self._custom_hands_status = QLabel(
            tr("{n} hand set(s) saved").format(n=user_count)
        )
        column.addWidget(self._custom_hands_status)
        return group

    def _pick_hand(self, hand: str) -> None:
        from PySide6.QtWidgets import QFileDialog

        path, _ = QFileDialog.getOpenFileName(
            self, self._tr("Browse…"), "", "PNG (*.png)"
        )
        if not path:
            return
        self._hand_files[hand] = path
        self._hand_buttons[hand].setText(Path(path).name)

    def _add_custom_hands(self) -> None:
        import shutil

        from data.hands import HAND_NAMES, hand_packs, user_hands_dir

        tr = self._tr
        name = self._hand_name_edit.text().strip()
        missing = [h for h in HAND_NAMES if not self._hand_files[h]]
        if not name or missing or any(
            name.lower() == existing.lower() for existing in hand_packs()
        ):
            self._custom_hands_status.setText(tr("Unique name"))
            return
        target = user_hands_dir() / name
        target.mkdir(parents=True, exist_ok=True)
        meta = {"name": name, "pivot": {}, "z_order": self._hand_z_combo.currentData()}
        for hand in HAND_NAMES:
            shutil.copyfile(self._hand_files[hand], target / f"{hand}.png")
            x_spin, y_spin = self._hand_pivots[hand]
            meta["pivot"][hand] = {
                "x": None if x_spin.value() < 0 else x_spin.value(),
                "y": y_spin.value(),
            }
        (target / "hands.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        self._custom_hands_status.setText(
            tr("Added '{name}' — find it under Design ▸ Hands").format(name=name)
        )
        self._hand_name_edit.clear()
