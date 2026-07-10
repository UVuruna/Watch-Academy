"""M6 settings window: location picker (cascading combos over the
bundled 45,650-city database + lat/lng fine-tune), Star/Aura opacity
sliders and the palette chip editor for the active (pointer, style).

The location tree loads on open and is released on close (the
repository's documented lifecycle). OK produces a new frozen Settings
via result_settings(); the controller applies and persists it.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSlider,
    QVBoxLayout,
)

from app.settings_store import Settings, replace
from config import constants, defaults
from data.locations import LocationRepository, fold_name

_NO_REGION = "—"                       # the country's direct cities


class SettingsDialog(QDialog):
    def __init__(self, settings: Settings, skin, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DOMY Watch Settings")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self._settings = settings
        self._skin = skin
        self._locations = LocationRepository()
        self._timezone = settings.timezone
        self._city_name = settings.city_name
        self._star_override = settings.star_alpha is not None
        self._aura_day_override = settings.aura_day_alpha is not None
        self._aura_twilight_override = settings.aura_twilight_alpha is not None
        self._palette_key = f"{settings.pointer}_{settings.palette_style}"
        self._preset = defaults.PALETTE_PRESETS[
            (settings.pointer, settings.palette_style)
        ]
        self._hues = list(
            settings.palettes.get(self._palette_key, self._preset)
        )
        self._ring_tint = settings.ring_tint

        layout = QVBoxLayout(self)
        layout.addWidget(self._build_location_group())
        layout.addWidget(self._build_opacity_group())
        layout.addWidget(self._build_sizes_group())
        layout.addWidget(self._build_palette_group())
        layout.addWidget(self._build_ring_tint_group())
        layout.addWidget(self._build_custom_ring_group())
        layout.addWidget(self._build_language_group())
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if settings.city_path:
            self._restore_path(settings.city_path)
        # Re-seed the ACTIVE location from the settings AFTER the combo
        # cascade (review finding): building the combos fires _on_city
        # with whatever city is alphabetically first, silently clobbering
        # the real location on first run — and the user's fine-tuned
        # lat/lng even with a stored path. The settings always win here;
        # the combos are only navigation.
        self._city_name = settings.city_name
        self._timezone = settings.timezone
        self._tz_label.setText(settings.timezone)
        self._latitude.setValue(settings.latitude)
        self._longitude.setValue(settings.longitude)

    def done(self, result: int) -> None:
        self._locations.release()
        super().done(result)

    # --- Location -----------------------------------------------------------------

    def _build_location_group(self) -> QGroupBox:
        group = QGroupBox("Location")
        form = QFormLayout(group)

        self._search = QLineEdit()
        self._search.setPlaceholderText("City name…")
        self._search.textChanged.connect(self._filter_cities)
        self._search_status = QLabel("")
        search_row = QHBoxLayout()
        search_row.addWidget(self._search)
        search_row.addWidget(self._search_status)
        form.addRow("Search", search_row)
        # Live filter results (owner spec, FINAL.txt #1): typing shows
        # the matching cities immediately — you always know whether the
        # city exists. Click a result to jump the combos to it.
        self._results = QListWidget()
        self._results.setMaximumHeight(120)
        self._results.hide()
        self._results.itemClicked.connect(self._pick_result)
        form.addRow("", self._results)
        self._all_cities: list[tuple[str, str, tuple[str, ...]]] | None = None

        self._continent = QComboBox()
        self._subregion = QComboBox()
        self._country = QComboBox()
        self._region = QComboBox()
        self._city = QComboBox()
        form.addRow("Continent", self._continent)
        form.addRow("Subregion", self._subregion)
        form.addRow("Country", self._country)
        form.addRow("Region", self._region)
        form.addRow("City", self._city)

        self._latitude = QDoubleSpinBox()
        self._latitude.setDecimals(4)
        self._latitude.setRange(*constants.LATITUDE_RANGE)
        self._latitude.setValue(self._settings.latitude)
        self._longitude = QDoubleSpinBox()
        self._longitude.setDecimals(4)
        self._longitude.setRange(*constants.LONGITUDE_RANGE)
        self._longitude.setValue(self._settings.longitude)
        form.addRow("Latitude", self._latitude)
        form.addRow("Longitude", self._longitude)
        self._tz_label = QLabel(self._timezone)
        form.addRow("Timezone", self._tz_label)

        self._fill(self._continent, ())
        self._continent.currentTextChanged.connect(lambda _: self._on_level(1))
        self._subregion.currentTextChanged.connect(lambda _: self._on_level(2))
        self._country.currentTextChanged.connect(lambda _: self._on_level(3))
        self._region.currentTextChanged.connect(lambda _: self._on_level(4))
        self._city.currentTextChanged.connect(lambda _: self._on_city())
        self._on_level(1)
        return group

    def _fill(self, combo: QComboBox, path: tuple[str, ...], cities: bool = False) -> None:
        combo.blockSignals(True)
        combo.clear()
        children = self._locations.children(path)
        combo.addItems(
            sorted(child.name for child in children if child.is_city == cities)
        )
        combo.blockSignals(False)

    def _group_path(self) -> tuple[str, ...]:
        """The navigable path up to (and including) the Region combo."""
        path = (
            self._continent.currentText(),
            self._subregion.currentText(),
            self._country.currentText(),
        )
        region = self._region.currentText()
        return path if region in ("", _NO_REGION) else path + (region,)

    def _on_level(self, level: int) -> None:
        """Repopulate everything below the changed combo."""
        if level <= 1:
            self._fill(self._subregion, (self._continent.currentText(),))
        if level <= 2:
            self._fill(
                self._country,
                (self._continent.currentText(), self._subregion.currentText()),
            )
        if level <= 3:
            country_path = (
                self._continent.currentText(),
                self._subregion.currentText(),
                self._country.currentText(),
            )
            children = self._locations.children(country_path)
            admins = sorted(c.name for c in children if not c.is_city)
            direct = any(c.is_city for c in children)
            self._region.blockSignals(True)
            self._region.clear()
            if direct:
                self._region.addItem(_NO_REGION)
            self._region.addItems(admins)
            self._region.blockSignals(False)
        self._fill(self._city, self._group_path(), cities=True)
        if level <= 3:
            self._show_major_cities()
        self._on_city()

    def _show_major_cities(self) -> None:
        """Pin the country's MAJOR cities into the results list on
        country change (agent finding: a city named like the last
        segment of its own IANA timezone is that zone's canonical city —
        it flags London for the UK for free). Click jumps the combos."""
        country_path = (
            self._continent.currentText(),
            self._subregion.currentText(),
            self._country.currentText(),
        )
        majors: list[tuple[str, tuple[str, ...]]] = []

        def walk(path: tuple[str, ...]) -> None:
            for child in self._locations.children(path):
                if child.is_city:
                    reference = (
                        child.record.timezone.rsplit("/", 1)[-1].replace("_", " ")
                    )
                    if fold_name(child.name) == fold_name(reference):
                        majors.append((child.name, path + (child.name,)))
                else:
                    walk(path + (child.name,))

        try:
            walk(country_path)
        except KeyError:
            return                       # combos mid-rebuild
        self._results.clear()
        for name, path in sorted(majors):
            item = QListWidgetItem(f"★ {name}")
            item.setData(Qt.ItemDataRole.UserRole, path)
            self._results.addItem(item)
        self._results.setVisible(bool(majors))

    def _on_city(self) -> None:
        name = self._city.currentText()
        if not name:
            return
        node = next(
            child
            for child in self._locations.children(self._group_path())
            if child.name == name and child.is_city
        )
        record = node.record
        self._city_name = record.name
        self._timezone = record.timezone
        self._tz_label.setText(record.timezone)
        self._latitude.setValue(record.latitude)
        self._longitude.setValue(record.longitude)

    def _restore_path(self, path: tuple[str, ...]) -> None:
        """Re-select the stored city path: (continent, subregion,
        country[, admin], city). Unknown segments are ignored (database
        updates must not break the dialog)."""
        try:
            combos = [self._continent, self._subregion, self._country]
            for combo, segment in zip(combos, path):
                index = combo.findText(segment)
                if index < 0:
                    return
                combo.setCurrentIndex(index)
            tail = path[3:]
            if len(tail) == 2:                     # (admin, city)
                index = self._region.findText(tail[0])
                if index < 0:
                    return
                self._region.setCurrentIndex(index)
            city = path[-1]
            index = self._city.findText(city)
            if index >= 0:
                self._city.setCurrentIndex(index)
        finally:
            # The stored fine-tuned values win over the combo defaults.
            self._latitude.setValue(self._settings.latitude)
            self._longitude.setValue(self._settings.longitude)
            self._timezone = self._settings.timezone
            self._city_name = self._settings.city_name
            self._tz_label.setText(self._timezone)

    def _filter_cities(self, text: str) -> None:
        """Live search (owner spec): filter all 45k cities as you type,
        show the matches in the dropdown list below."""
        text = text.strip()
        if len(text) < 2:
            self._results.hide()
            self._search_status.setText("")
            return
        if self._all_cities is None:
            self._all_cities = self._locations.all_cities()
        wanted = fold_name(text)
        matches = [
            (display, path)
            for folded, display, path in self._all_cities
            if wanted in folded
        ]
        # Exact and prefix matches first, then the rest, alphabetical.
        matches.sort(key=lambda m: (not fold_name(m[0]).startswith(wanted), m[0]))
        self._results.clear()
        for display, path in matches[:30]:
            item = QListWidgetItem(f"{display}  —  {' / '.join(path[:-1])}")
            item.setData(Qt.ItemDataRole.UserRole, path)
            self._results.addItem(item)
        self._search_status.setText(
            "not found" if not matches else f"{len(matches)} found"
        )
        self._results.setVisible(bool(matches))

    def _pick_result(self, item: QListWidgetItem) -> None:
        path = tuple(item.data(Qt.ItemDataRole.UserRole))
        self._restore_search(path)
        self._results.hide()

    def _restore_search(self, path: tuple[str, ...]) -> None:
        """Walk the combos to a found city — its record fills lat/lng."""
        record_path = path
        combos = [self._continent, self._subregion, self._country]
        for combo, segment in zip(combos, record_path):
            index = combo.findText(segment)
            if index < 0:
                return
            combo.setCurrentIndex(index)
        tail = record_path[3:]
        if len(tail) == 2:
            index = self._region.findText(tail[0])
            if index < 0:
                return
            self._region.setCurrentIndex(index)
        index = self._city.findText(record_path[-1])
        if index >= 0:
            self._city.setCurrentIndex(index)

    def _current_path(self) -> tuple[str, ...]:
        return self._group_path() + (self._city.currentText(),)

    # --- Opacity --------------------------------------------------------------------

    def _build_opacity_group(self) -> QGroupBox:
        group = QGroupBox("Opacity")
        form = QFormLayout(group)

        def initial(override: float | None, skin_value: float) -> tuple[int, int]:
            default = round(skin_value * 100)
            value = round(override * 100) if override is not None else default
            return value, default

        value, default = initial(self._settings.star_alpha, self._skin.star.day_alpha)
        self._star_slider, star_row = self._slider_row(value, default, "star")
        form.addRow("Star", star_row)
        # The Aura's sunlight and twilight opacities are INDEPENDENT
        # sliders (owner spec).
        value, default = initial(
            self._settings.aura_day_alpha, self._skin.background.day_alpha
        )
        self._aura_day_slider, day_row = self._slider_row(value, default, "aura_day")
        form.addRow("Aura — sunlight", day_row)
        value, default = initial(
            self._settings.aura_twilight_alpha, self._skin.background.twilight_alpha
        )
        self._aura_twilight_slider, twilight_row = self._slider_row(
            value, default, "aura_twilight"
        )
        form.addRow("Aura — twilight", twilight_row)
        return group

    def _slider_row(self, value: int, default: int, which: str):
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(value)
        label = QLabel(f"{value}%")
        reset = QPushButton("Skin default")

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

    # --- Element sizes (owner EXTRAS) ------------------------------------------------

    def _build_sizes_group(self) -> QGroupBox:
        """Per-element size multipliers plus the shared hover-enlarge
        factor (the element under the cursor grows by it; 100% = off)."""
        group = QGroupBox("Element sizes")
        form = QFormLayout(group)
        self._size_sliders: dict[str, QSlider] = {}
        rows = [
            ("earth_scale", "Earth", constants.ELEMENT_SCALE_RANGE, 100),
            ("moon_scale", "Moon", constants.ELEMENT_SCALE_RANGE, 100),
            ("weekday_scale", "Weekday", constants.ELEMENT_SCALE_RANGE, 100),
            ("octa_slot_scale", "Octa slot", constants.ELEMENT_SCALE_RANGE, 100),
            ("ring_letter_scale", "Ring letters", constants.ELEMENT_SCALE_RANGE, 100),
            ("hover_enlarge", "Hover enlarge", constants.HOVER_ENLARGE_RANGE, 120),
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
            reset = QPushButton("Default")
            reset.clicked.connect(
                lambda checked, s=slider, d=default: s.setValue(d)
            )
            row = QHBoxLayout()
            row.addWidget(slider)
            row.addWidget(label)
            row.addWidget(reset)
            self._size_sliders[key] = slider
            form.addRow(title, row)
        return group

    # --- Palette --------------------------------------------------------------------

    def _build_palette_group(self) -> QGroupBox:
        pointer = self._settings.pointer
        style = self._settings.palette_style
        group = QGroupBox(
            f"Palette — {pointer.capitalize()} {style.capitalize()}"
        )
        column = QVBoxLayout(group)
        chips_row = QHBoxLayout()
        self._chips: list[QPushButton] = []
        for index, hue in enumerate(self._hues):
            chip = QPushButton()
            chip.setFixedSize(36, 24)
            self._paint_chip(chip, hue)
            chip.clicked.connect(lambda checked, i=index: self._pick_color(i))
            self._chips.append(chip)
            chips_row.addWidget(chip)
        chips_row.addStretch(1)
        reset = QPushButton("Reset to preset")
        reset.clicked.connect(self._reset_palette)
        chips_row.addWidget(reset)
        column.addLayout(chips_row)
        return group

    @staticmethod
    def _paint_chip(chip: QPushButton, hue: str) -> None:
        chip.setStyleSheet(
            f"background-color: {hue}; border: 1px solid #666;"
        )
        chip.setToolTip(hue)

    def _pick_color(self, index: int) -> None:
        chosen = QColorDialog.getColor(
            QColor(self._hues[index]), self, "Pick a hue"
        )
        if not chosen.isValid():
            return
        self._hues[index] = chosen.name().upper()
        self._paint_chip(self._chips[index], self._hues[index])

    def _reset_palette(self) -> None:
        self._hues = list(self._preset)
        for chip, hue in zip(self._chips, self._hues):
            self._paint_chip(chip, hue)

    # --- Ring tint ------------------------------------------------------------------

    def _build_ring_tint_group(self) -> QGroupBox:
        """One hue recolors the whole clock body — ring art, hands and
        Umbra (channel multiply; the letter art stays untouched). Preset
        chips come from defaults.RING_TINT_PRESETS (owner-tunable),
        plus a free color picker."""
        group = QGroupBox("Ring tint — whole clock body (letters excluded)")
        row = QHBoxLayout(group)
        for name, hue in defaults.RING_TINT_PRESETS.items():
            chip = QPushButton(name)
            if hue is not None:
                chip.setStyleSheet(
                    f"background-color: {hue}; border: 1px solid #666;"
                )
            chip.setToolTip(hue or "the untouched gray art")
            chip.clicked.connect(
                lambda checked, chosen=hue: self._set_ring_tint(chosen)
            )
            row.addWidget(chip)
        custom = QPushButton("Custom…")
        custom.clicked.connect(self._pick_ring_tint)
        row.addWidget(custom)
        row.addStretch(1)
        self._ring_tint_label = QLabel()
        self._show_ring_tint()
        row.addWidget(self._ring_tint_label)
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
        self._ring_tint_label.setText(self._ring_tint or "Gray (default)")

    # --- Custom ring (owner spec) -----------------------------------------------------

    def _build_custom_ring_group(self) -> QGroupBox:
        """The ring card builder: pick a layout (Flame / Chalice /
        Seal), a library letter per position and a unique name — the
        new card joins Theme ▸ Ring with the gold/silver metal rules."""
        self._custom_rings = list(self._settings.custom_rings)
        group = QGroupBox("Custom ring")
        column = QVBoxLayout(group)
        top = QHBoxLayout()
        self._ring_layout_combo = QComboBox()
        for key, layout in constants.RING_LAYOUTS.items():
            self._ring_layout_combo.addItem(
                f"{key.capitalize()} — {layout['theme']} "
                f"({len(layout['positions'])} letters)",
                key,
            )
        self._ring_layout_combo.currentIndexChanged.connect(
            self._rebuild_ring_slots
        )
        top.addWidget(self._ring_layout_combo)
        self._ring_name_edit = QLineEdit()
        self._ring_name_edit.setPlaceholderText("Unique name")
        top.addWidget(self._ring_name_edit)
        add = QPushButton("Add ring")
        add.clicked.connect(self._add_custom_ring)
        top.addWidget(add)
        column.addLayout(top)
        self._ring_slot_row = QHBoxLayout()
        column.addLayout(self._ring_slot_row)
        self._ring_slot_combos: dict[int, QComboBox] = {}
        self._custom_ring_status = QLabel(
            f"{len(self._custom_rings)} custom ring(s) saved"
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
            combo = QComboBox()
            combo.addItems(list(constants.RING_LETTER_FILES))
            cell.addWidget(combo)
            self._ring_slot_combos[position] = combo
            self._ring_slot_row.addLayout(cell)

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
            f"Added {card['name']!r} — OK saves it; find it under "
            f"Theme ▸ Ring"
        )
        self._ring_name_edit.clear()

    # --- Language (owner spec: translate once via the keyless endpoint) --------------

    def _build_language_group(self) -> QGroupBox:
        group = QGroupBox("Language")
        row = QHBoxLayout(group)
        self._language_combo = QComboBox()
        for code, name in sorted(
            constants.TRANSLATION_LANGUAGES.items(), key=lambda item: item[1]
        ):
            self._language_combo.addItem(name, code)
            if code == self._settings.language:
                self._language_combo.setCurrentIndex(
                    self._language_combo.count() - 1
                )
        row.addWidget(self._language_combo)
        note = QLabel(
            "First pick translates all texts in the background "
            "(internet needed once) and caches them — afterwards the "
            "language works offline."
        )
        note.setWordWrap(True)
        row.addWidget(note, stretch=1)
        return group

    # --- Result ---------------------------------------------------------------------

    def result_settings(self) -> Settings:
        palettes = dict(self._settings.palettes)
        if tuple(self._hues) != self._preset:
            palettes[self._palette_key] = tuple(self._hues)
        else:
            palettes.pop(self._palette_key, None)
        return replace(
            self._settings,
            city_name=self._city_name,
            city_path=self._current_path(),
            latitude=round(self._latitude.value(), 4),
            longitude=round(self._longitude.value(), 4),
            timezone=self._timezone,
            star_alpha=(
                self._star_slider.value() / 100 if self._star_override else None
            ),
            aura_day_alpha=(
                self._aura_day_slider.value() / 100
                if self._aura_day_override
                else None
            ),
            aura_twilight_alpha=(
                self._aura_twilight_slider.value() / 100
                if self._aura_twilight_override
                else None
            ),
            palettes=palettes,
            ring_tint=self._ring_tint,
            custom_rings=tuple(self._custom_rings),
            language=self._language_combo.currentData(),
            **{
                key: slider.value() / 100
                for key, slider in self._size_sliders.items()
            },
        )
