"""Themes Section — `_ThemesSectionMixin`: the Theme rotation, Artwork,
Subdial plate and Metal shades groups. Plain-Python mixin (no base
class — composed onto `dialog.SettingsDialog`'s `QDialog` shell,
`research/REFACTOR_PLAN.md` §7). See
[Themes Section](themes_section.md) for the full behavioral narrative.
"""

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from config import constants, defaults


class _ThemesSectionMixin:
    def _build_theme_rotation_group(self) -> QGroupBox:
        """Cycle the CHECKED weekday themes every N minutes/hours
        instead of wearing one forever."""
        tr = self._tr
        group = QGroupBox(tr("Theme rotation"))
        column = QVBoxLayout(group)
        # The GROUP dropdown (owner 2026-07-14): None (the canon — no
        # rotation), one kinship family from the Weekday menu
        # grouping, or Custom (the checkbox grid). No Enabled checkbox
        # — None IS off.
        self._rotation_group = QComboBox()
        self._rotation_group.addItem(tr("None"), "none")
        for title, _ in defaults.WEEKDAY_MENU_GROUPS:
            self._rotation_group.addItem(tr(title), title)
        self._rotation_group.addItem(tr("Custom"), "custom")
        index = self._rotation_group.findData(
            self._settings.theme_rotation_group
        )
        if index >= 0:
            self._rotation_group.setCurrentIndex(index)
        column.addWidget(self._rotation_group)
        self._rotation_grid_host = QWidget()
        grid = QGridLayout(self._rotation_grid_host)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(24)
        self._rotation_checks: dict[str, QCheckBox] = {}
        for index, (key, label) in enumerate(
            defaults.WEEKDAY_THEME_TITLES.items()
        ):
            box = QCheckBox(tr(label))
            box.setChecked(key in self._settings.theme_rotation_themes)
            box.toggled.connect(lambda _checked: self._refresh_rotation_ui())
            self._rotation_checks[key] = box
            grid.addWidget(box, index // 4, index % 4)
        column.addWidget(self._rotation_grid_host)
        row = QHBoxLayout()
        row.addWidget(QLabel(tr("Every")))
        self._rotation_amount = QSpinBox()
        self._rotation_amount.setRange(1, 999)
        minutes = self._settings.theme_rotation_minutes
        self._rotation_unit = QComboBox()
        self._rotation_unit.addItem(tr("minutes"), 1)
        self._rotation_unit.addItem(tr("hours"), 60)
        if minutes % 60 == 0:
            self._rotation_amount.setValue(minutes // 60)
            self._rotation_unit.setCurrentIndex(1)
        else:
            self._rotation_amount.setValue(minutes)
        row.addWidget(self._rotation_amount)
        row.addWidget(self._rotation_unit)
        row.addStretch(1)
        column.addLayout(row)
        # The METAL each bronze-plate theme wears (owner 2026-07-12;
        # colored is the canon default 2026-07-14): per theme — or one
        # checkbox to follow the ring finish everywhere. Only the
        # metal themes INSIDE the current rotation selection show
        # their combos (owner 2026-07-14).
        metal_row = QHBoxLayout()
        self._metal_combos: dict[str, QComboBox] = {}
        self._metal_labels: dict[str, QLabel] = {}
        for theme in constants.METAL_THEMES:
            # planets_art has no top-level menu title (owner 2026-07-18:
            # it nests as the Planets "Art" look) — it never gets an
            # independent rotation row here.
            if theme not in defaults.WEEKDAY_THEME_TITLES:
                continue
            label = QLabel(tr(defaults.WEEKDAY_THEME_TITLES[theme]))
            self._metal_labels[theme] = label
            metal_row.addWidget(label)
            combo = QComboBox()
            for metal in constants.theme_metals(theme):
                combo.addItem(tr(metal.capitalize()), metal)
            combo.setCurrentIndex(
                combo.findData(
                    self._settings.theme_metals.get(theme, "colored")
                )
            )
            self._metal_combos[theme] = combo
            metal_row.addWidget(combo)
        metal_row.addStretch(1)
        column.addLayout(metal_row)
        self._metal_follow_ring = QCheckBox(tr("Follow ring color"))
        self._metal_follow_ring.setChecked(
            self._settings.theme_metal_follow_ring
        )
        self._metal_follow_ring.toggled.connect(
            lambda checked: [
                combo.setEnabled(not checked)
                for combo in self._metal_combos.values()
            ]
        )
        for combo in self._metal_combos.values():
            combo.setEnabled(not self._settings.theme_metal_follow_ring)
        column.addWidget(self._metal_follow_ring)
        self._rotation_group.currentIndexChanged.connect(
            lambda _index: self._refresh_rotation_ui()
        )
        self._refresh_rotation_ui()
        return group

    def _rotation_selection(self) -> tuple[str, ...]:
        """The themes the CURRENT dialog state would rotate."""
        group_key = self._rotation_group.currentData()
        if group_key == "custom":
            return tuple(
                key for key, box in self._rotation_checks.items()
                if box.isChecked()
            )
        for title, keys in defaults.WEEKDAY_MENU_GROUPS:
            if title == group_key:
                return keys
        return ()

    def _refresh_rotation_ui(self) -> None:
        """The checkbox grid shows only for Custom; each metal combo
        shows only while its theme is IN the selection (owner
        2026-07-14: 'ako smo odabrali animals dobijamo samo ta 3')."""
        group_key = self._rotation_group.currentData()
        self._rotation_grid_host.setVisible(group_key == "custom")
        selected = set(self._rotation_selection())
        for theme in self._metal_labels:
            visible = theme in selected
            self._metal_labels[theme].setVisible(visible)
            self._metal_combos[theme].setVisible(visible)

    def _build_artwork_group(self) -> QGroupBox:
        """The ART SOURCE pick (owner 2026-07-14): the Gemini and
        ChatGPT generations coexist — one combo switches every plate,
        emblem and badge; files missing in the chosen source fall back
        to the other."""
        tr = self._tr
        group = QGroupBox(tr("Artwork"))
        row = QHBoxLayout(group)
        self._art_source_combo = QComboBox()
        for source in constants.ART_SOURCES:
            self._art_source_combo.addItem(
                constants.ART_SOURCE_TITLES[source], source
            )
        index = self._art_source_combo.findData(self._settings.art_source)
        if index >= 0:
            self._art_source_combo.setCurrentIndex(index)
        row.addWidget(self._art_source_combo)
        row.addStretch(1)
        return group

    def _build_subdial_set_group(self) -> QGroupBox:
        """The SUBDIAL PLATE SET pick (owner decree 2026-07-21, Rsub
        round — retires the Rule #19 one-master-per-source model):
        five hand-picked plates — four full hand-drawn looks plus a
        fifth (Solo) whose silver is hand-drawn and gold/bronze are
        the algorithmic recolor (`render.asset_variants.subdial_plate_file`).
        The active letter finish (ring_finish, picked in the tray
        Design menu) still decides WHICH color draws within the
        chosen set — this combo only picks the set."""
        tr = self._tr
        group = QGroupBox(tr("Subdial plate"))
        row = QHBoxLayout(group)
        self._subdial_set_combo = QComboBox()
        for name in constants.SUBDIAL_SETS:
            self._subdial_set_combo.addItem(
                tr(constants.SUBDIAL_SET_TITLES[name]), name
            )
        index = self._subdial_set_combo.findData(self._settings.subdial_set)
        if index >= 0:
            self._subdial_set_combo.setCurrentIndex(index)
        row.addWidget(self._subdial_set_combo)
        row.addStretch(1)
        return group

    def _build_metal_shade_group(self) -> QGroupBox:
        """THE METAL SHADES (R8a round, owner spec 2026-07-21 night —
        the retry after the adaptive-percentile attempt was reverted
        for flattening relief): one combo per metal picks its shade
        (gold's five bands sampled off the owner's palette strip,
        bronze/silver three-step ramps) — the SAME (hue, saturation,
        reference value) recipe recolors ring letters everywhere and
        badge medallions wherever gold/silver is chosen (bronze
        medallions stay the art as drawn, unaffected by the bronze
        shade pick — out of this round's scope, documented in
        render.assets.md)."""
        tr = self._tr
        group = QGroupBox(tr("Metal shades"))
        form = QFormLayout(group)
        self._metal_shade_combos: dict[str, QComboBox] = {}
        titles = {"gold": tr("Gold"), "bronze": tr("Bronze"), "silver": tr("Silver")}
        current = {
            "gold": self._settings.metal_shade_gold,
            "bronze": self._settings.metal_shade_bronze,
            "silver": self._settings.metal_shade_silver,
        }
        for metal in ("gold", "bronze", "silver"):
            combo = QComboBox()
            for shade in constants.METAL_SHADE_NAMES[metal]:
                combo.addItem(tr(constants.METAL_SHADE_TITLES[shade]), shade)
            index = combo.findData(current[metal])
            if index >= 0:
                combo.setCurrentIndex(index)
            self._metal_shade_combos[metal] = combo
            form.addRow(titles[metal], combo)
        return group
