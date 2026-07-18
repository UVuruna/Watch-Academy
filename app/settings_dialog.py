"""M6 settings window: location picker (cascading combos over the
bundled 45,650-city database + lat/lng fine-tune), Star/Aura opacity
sliders and the palette chip editor for the active (pointer, style).

The location tree loads on open and is released on close (the
repository's documented lifecycle). OK produces a new frozen Settings
via result_settings(); the controller applies and persists it.
"""

import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.settings_store import Settings, replace
from config import constants, defaults
from config.ui_text import ui
from data.locations import LocationRepository, fold_name

_NO_REGION = "—"                       # the country's direct cities


class SettingsDialog(QDialog):
    def __init__(self, settings: Settings, skin,
                 overlay: dict | None = None, parent=None):
        super().__init__(parent)
        self._overlay = overlay or {}
        self.setWindowTitle(
            f"{constants.APP_NAME} — {self._tr('Settings')}"
        )
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self._settings = settings
        self._skin = skin
        self._locations = LocationRepository()
        self._timezone = settings.timezone
        self._city_name = settings.city_name
        self._star_override = settings.star_alpha is not None
        self._aura_day_override = settings.aura_day_alpha is not None
        self._aura_twilight_override = settings.aura_twilight_alpha is not None
        # The major-cities suggestions only appear on USER interaction
        # (owner 2026-07-12: the box popped huge on every open although
        # the location is picked once) — armed after construction.
        self._suggestions_armed = False
        self._palette_key = f"{settings.pointer}_{settings.palette_style}"
        self._preset = defaults.PALETTE_PRESETS[
            (settings.pointer, settings.palette_style)
        ]
        self._hues = list(
            settings.palettes.get(self._palette_key, self._preset)
        )
        self._ring_tint = settings.ring_tint

        # QUICK JUMP CITIES (Session 16, owner slika 12): the working
        # list starts from the saved settings; the group below edits it.
        self._jump_cities = [dict(city) for city in settings.jump_cities]

        # THE NAVIGATION REWORK (owner ROADMAP 15h item 1, 2026-07-18):
        # a left column of SECTION TITLES (each with a right arrow ▸)
        # replaces the old one-long-scroll layout — clicking a title
        # shows THAT section's panel on the right. Related groups SHARE
        # one title exactly where the owner's own example applies (the
        # Pointer palette and the Clock/ring tint are both COLOR); every
        # existing control moves into one section or another, none are
        # dropped, `result_settings()` is untouched. Each panel keeps
        # its OWN scroll area (owner: "keep the scroll cap for tall
        # panels") — only ONE panel is visible at a time now, so the cap
        # moved from the whole dialog onto each panel individually.
        tr = self._tr
        sections: list[tuple[str, list[QGroupBox]]] = [
            (tr("Location"), [
                self._build_location_group(), self._build_jump_cities_group(),
            ]),
            (tr("Display"), [
                self._build_opacity_group(), self._build_sizes_group(),
                self._build_archetype_group(),
            ]),
            (tr("Colors"), [
                self._build_palette_group(), self._build_ring_tint_group(),
                self._build_saturation_group(),
            ]),
            (tr("Custom art"), [
                self._build_custom_ring_group(), self._build_custom_hands_group(),
            ]),
            (tr("Themes"), [
                self._build_theme_rotation_group(), self._build_artwork_group(),
            ]),
            (tr("Language"), [
                self._build_language_group(), self._build_era_group(),
            ]),
            (tr("System"), [self._build_system_group()]),
        ]
        self._nav_list = QListWidget()
        self._nav_list.setFixedWidth(defaults.SETTINGS_NAV_WIDTH_PX)
        self._stack = QStackedWidget()
        pages: list[QWidget] = []
        for title, groups in sections:
            self._nav_list.addItem(f"{title}  ▸")
            page = QWidget()
            page_layout = QVBoxLayout(page)
            page_layout.setContentsMargins(0, 0, 0, 0)
            for group in groups:
                page_layout.addWidget(group)
            page_layout.addStretch(1)
            pages.append(page)
            panel_scroll = QScrollArea()
            panel_scroll.setWidgetResizable(True)
            panel_scroll.setFrameShape(QFrame.Shape.NoFrame)
            panel_scroll.setWidget(page)
            self._stack.addWidget(panel_scroll)
        self._nav_list.currentRowChanged.connect(self._stack.setCurrentIndex)
        self._nav_list.setCurrentRow(0)

        layout = QVBoxLayout(self)
        body = QHBoxLayout()
        body.addWidget(self._nav_list)
        body.addWidget(self._stack, stretch=1)
        layout.addLayout(body, stretch=1)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        screen = QApplication.primaryScreen().availableGeometry()
        content_width = max(page.sizeHint().width() for page in pages)
        content_height = max(page.sizeHint().height() for page in pages)
        self.resize(
            min(
                content_width + defaults.SETTINGS_NAV_WIDTH_PX + 64,
                screen.width() - 80,
            ),
            min(content_height + 96, round(screen.height() * 0.92)),
        )

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
        self._results.hide()
        self._suggestions_armed = True   # from here on, changes are the user's

    def _tr(self, text: str) -> str:
        """The active language's form of a chrome string (Phase 2)."""
        return ui(self._overlay, text)

    def done(self, result: int) -> None:
        self._locations.release()
        super().done(result)

    # --- Location -----------------------------------------------------------------

    def _build_location_group(self) -> QGroupBox:
        tr = self._tr
        group = QGroupBox(tr("Location"))
        form = QFormLayout(group)

        self._search = QLineEdit()
        self._search.setPlaceholderText(tr("City name…"))
        self._search.textChanged.connect(self._filter_cities)
        self._search_status = QLabel("")
        search_row = QHBoxLayout()
        search_row.addWidget(self._search)
        search_row.addWidget(self._search_status)
        form.addRow(tr("Search"), search_row)
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
        form.addRow(tr("Continent"), self._continent)
        form.addRow(tr("Subregion"), self._subregion)
        form.addRow(tr("Country"), self._country)
        form.addRow(tr("Region"), self._region)
        form.addRow(tr("City"), self._city)

        self._latitude = QDoubleSpinBox()
        self._latitude.setDecimals(4)
        self._latitude.setRange(*constants.LATITUDE_RANGE)
        self._latitude.setValue(self._settings.latitude)
        self._longitude = QDoubleSpinBox()
        self._longitude.setDecimals(4)
        self._longitude.setRange(*constants.LONGITUDE_RANGE)
        self._longitude.setValue(self._settings.longitude)
        form.addRow(tr("Latitude"), self._latitude)
        form.addRow(tr("Longitude"), self._longitude)
        self._tz_label = QLabel(self._timezone)
        form.addRow(tr("Timezone"), self._tz_label)

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

        if not self._suggestions_armed:
            return                       # dialog construction, not the user
        try:
            walk(country_path)
        except KeyError:
            return                       # combos mid-rebuild
        self._results.clear()
        for name, path in sorted(majors):
            item = QListWidgetItem(f"★ {name}")
            item.setData(Qt.ItemDataRole.UserRole, path)
            self._results.addItem(item)
        self._fit_results()

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
            self._tr("not found")
            if not matches
            else self._tr("{n} found").format(n=len(matches))
        )
        self._fit_results()

    def _fit_results(self) -> None:
        """The suggestion box wraps its rows instead of holding a huge
        fixed area (owner 2026-07-12: one city does not need a field)."""
        rows = self._results.count()
        if not rows:
            self._results.hide()
            return
        row_height = self._results.sizeHintForRow(0)
        self._results.setFixedHeight(min(120, rows * row_height + 10))
        self._results.show()

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

    # --- Quick Jump cities (Session 16, owner slika 12) -------------------------

    def _build_jump_cities_group(self) -> QGroupBox:
        """The user's own places for the Quick Jump ▸ Location submenu:
        a search box over the SAME 45k-city machinery as the location
        picker (fold_name matching, the same results list), but a pick
        here ADDS to the jump list instead of touching the home
        location — navigating the home combos to add a jump city would
        silently change home on OK."""
        tr = self._tr
        group = QGroupBox(tr("Quick Jump cities"))
        form = QFormLayout(group)
        self._jump_search = QLineEdit()
        self._jump_search.setPlaceholderText(tr("City name…"))
        self._jump_search.textChanged.connect(self._filter_jump_cities)
        form.addRow(tr("Add"), self._jump_search)
        self._jump_results = QListWidget()
        self._jump_results.setMaximumHeight(120)
        self._jump_results.hide()
        self._jump_results.itemClicked.connect(self._add_jump_city)
        form.addRow("", self._jump_results)
        self._jump_list = QListWidget()
        self._jump_list.setMaximumHeight(120)
        form.addRow(tr("Cities"), self._jump_list)
        remove = QPushButton(tr("Remove selected"))
        remove.clicked.connect(self._remove_jump_city)
        form.addRow("", remove)
        note = QLabel(
            tr(
                "Each city appears in Quick Jump ▸ Location and moves "
                "the observer there — the traveled moment stays."
            )
        )
        note.setWordWrap(True)
        form.addRow(note)
        self._refresh_jump_list()
        return group

    def _filter_jump_cities(self, text: str) -> None:
        """The same live search as the home picker, feeding the jump
        results list (Rule #5: one city collection, one folding)."""
        text = text.strip()
        if len(text) < 2:
            self._jump_results.hide()
            return
        if self._all_cities is None:
            self._all_cities = self._locations.all_cities()
        wanted = fold_name(text)
        matches = [
            (display, path)
            for folded, display, path in self._all_cities
            if wanted in folded
        ]
        matches.sort(key=lambda m: (not fold_name(m[0]).startswith(wanted), m[0]))
        self._jump_results.clear()
        for display, path in matches[:30]:
            item = QListWidgetItem(f"{display}  —  {' / '.join(path[:-1])}")
            item.setData(Qt.ItemDataRole.UserRole, path)
            self._jump_results.addItem(item)
        self._jump_results.setVisible(bool(matches))

    def _add_jump_city(self, item: QListWidgetItem) -> None:
        path = tuple(item.data(Qt.ItemDataRole.UserRole))
        node = next(
            (
                child for child in self._locations.children(path[:-1])
                if child.is_city and child.name == path[-1]
            ),
            None,
        )
        if node is None:
            return
        record = node.record
        city = {
            "name": record.name,
            "latitude": record.latitude,
            "longitude": record.longitude,
            "timezone": record.timezone,
        }
        if city not in self._jump_cities:
            self._jump_cities.append(city)
            self._refresh_jump_list()
        self._jump_results.hide()
        self._jump_search.clear()

    def _remove_jump_city(self) -> None:
        row = self._jump_list.currentRow()
        if 0 <= row < len(self._jump_cities):
            del self._jump_cities[row]
            self._refresh_jump_list()

    def _refresh_jump_list(self) -> None:
        self._jump_list.clear()
        for city in self._jump_cities:
            self._jump_list.addItem(
                f"{city['name']}  —  {city['timezone']}"
            )

    # --- Opacity --------------------------------------------------------------------

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

    # --- Archetype (owner 2026-07-18, Session 21-C) ----------------------------------

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

    # --- Element sizes (owner EXTRAS) ------------------------------------------------

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

    # --- Saturation (owner 2026-07-18, Session 21-D — moved out of ----------------
    # Element sizes into its OWN Colors group beside Palette + Ring tint,
    # split into two independent 0-100% sliders) --------------------------------

    def _build_saturation_group(self) -> QGroupBox:
        """TWO independent saturation sliders (owner verdict: Saturation
        does not belong in Element sizes — Colors is where Palette and
        Ring tint already live). POINTER (`pointer_saturation`, renamed
        from "palette_saturation") scales the Star+Aura palette's HSV
        saturation at `render.layers.palette_for` — the star diamonds
        and the Aura wedges move together. RING (`ring_saturation`, new)
        scales the ring band art's (plate + letter overlay) saturation
        at `render.layers.RingLayer`, after the ring_tint recolor. Both
        0-100%, default 100% (unchanged); "Default" resets each to 100."""
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
            tr("Pointer"), "pointer_saturation",
            constants.POINTER_SATURATION_RANGE,
            constants.POINTER_SATURATION_SLIDER_STEP,
        )
        self._ring_saturation_slider = add_row(
            tr("Ring"), "ring_saturation",
            constants.RING_SATURATION_RANGE,
            constants.RING_SATURATION_SLIDER_STEP,
        )
        return group

    # --- Palette --------------------------------------------------------------------

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

    # --- Ring tint ------------------------------------------------------------------

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

    # --- Custom ring (owner spec) -----------------------------------------------------

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

    # --- Custom hands (owner spec 2026-07-12) -----------------------------------------

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

    # --- Theme rotation (owner spec 2026-07-12) ----------------------------------------

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

    # --- System (autostart) -------------------------------------------------------------

    def _build_system_group(self) -> QGroupBox:
        """Start with Windows (owner spec 2026-07-12): a standard-user
        HKCU Run entry — the registry is the store, read live here and
        applied by the controller on OK. Plus the VISIBILITY Z mode
        (owner 2026-07-17, ROADMAP 15d): below all windows (default) or
        always on top."""
        from app import native

        tr = self._tr
        group = QGroupBox(tr("System"))
        form = QFormLayout(group)
        self._autostart_check = QCheckBox(tr("Start with Windows"))
        self._autostart_check.setChecked(native.autostart_enabled())
        form.addRow(self._autostart_check)
        self._z_mode_combo = QComboBox()
        for mode in constants.Z_MODES:
            self._z_mode_combo.addItem(tr(constants.Z_MODE_TITLES[mode]), mode)
        index = self._z_mode_combo.findData(self._settings.z_mode)
        if index >= 0:
            self._z_mode_combo.setCurrentIndex(index)
        form.addRow(tr("Visibility"), self._z_mode_combo)
        return group

    def _build_era_group(self) -> QGroupBox:
        """THE YEAR LINE (Session 16, owner amendment 2026-07-17): the
        Anno Lucis year always accompanies the official year — here the
        user picks the OFFICIAL labels (BCE/CE vs BC/AD), whether
        positive years carry the suffix (default bare), and the
        optional THIRD calendar on the line. Placed under Language —
        the documented call."""
        tr = self._tr
        group = QGroupBox(tr("Calendar eras"))
        form = QFormLayout(group)
        self._era_combo = QComboBox()
        for notation in constants.ERA_NOTATIONS:
            self._era_combo.addItem(
                constants.ERA_NOTATION_TITLES[notation], notation
            )
        index = self._era_combo.findData(self._settings.era_notation)
        if index >= 0:
            self._era_combo.setCurrentIndex(index)
        form.addRow(tr("Era labels"), self._era_combo)
        self._era_suffix_check = QCheckBox(
            tr("Write the era after positive years too (2026 CE)")
        )
        self._era_suffix_check.setChecked(self._settings.show_era_suffix)
        form.addRow("", self._era_suffix_check)
        self._third_era_combo = QComboBox()
        for era in constants.THIRD_ERAS:
            self._third_era_combo.addItem(
                tr(constants.THIRD_ERA_TITLES[era]), era
            )
            note = constants.THIRD_ERA_NOTES.get(era)
            if note:
                # Epoch fine print (owner amendment: tooltip ONLY).
                self._third_era_combo.setItemData(
                    self._third_era_combo.count() - 1, tr(note),
                    Qt.ItemDataRole.ToolTipRole,
                )
        index = self._third_era_combo.findData(self._settings.third_era)
        if index >= 0:
            self._third_era_combo.setCurrentIndex(index)
        form.addRow(tr("Third calendar"), self._third_era_combo)
        note = QLabel(
            tr(
                "Years in legends read as official · Anno Lucis (A.L. = "
                "CE + 4079, the measured light era) — the third "
                "calendar joins that line."
            )
        )
        note.setWordWrap(True)
        form.addRow(note)
        return group

    def autostart_selected(self) -> bool:
        return self._autostart_check.isChecked()

    # --- Language (owner spec: translate once via the keyless endpoint) --------------

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

    def _build_language_group(self) -> QGroupBox:
        tr = self._tr
        group = QGroupBox(tr("Language"))
        row = QHBoxLayout(group)
        self._language_combo = QComboBox()
        # The ORIGINALS ride the top (owner spec 2026-07-11): English
        # and Serbian Latin ship hand-written in the app; everything
        # below the separator machine-translates on first pick.
        originals = [
            (code, constants.TRANSLATION_LANGUAGES[code])
            for code in constants.TRANSLATION_ORIGINALS
        ]
        rest = sorted(
            (
                (code, name)
                for code, name in constants.TRANSLATION_LANGUAGES.items()
                if code not in constants.TRANSLATION_ORIGINALS
            ),
            key=lambda item: item[1],
        )
        for code, name in originals:
            self._language_combo.addItem(
                tr("{name} — original").format(name=name), code
            )
        self._language_combo.insertSeparator(len(originals))
        for code, name in rest:
            self._language_combo.addItem(name, code)
        index = self._language_combo.findData(self._settings.language)
        if index >= 0:
            self._language_combo.setCurrentIndex(index)
        row.addWidget(self._language_combo)
        # One-click way back to the shipped originals (owner spec
        # 2026-07-11): jump the combo to English.
        default = QPushButton(tr("Default"))
        default.setToolTip(tr("Back to English — the shipped original texts"))
        default.clicked.connect(
            lambda: self._language_combo.setCurrentIndex(
                self._language_combo.findData("en")
            )
        )
        row.addWidget(default)
        note = QLabel(
            tr(
                "The originals above the line ship inside the app. Any "
                "other language translates itself in the background on "
                "first pick (internet needed once) and then works offline."
            )
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
            moon_hidden_alpha=self._moon_alpha_slider.value() / 100,
            theme_rotation_group=self._rotation_group.currentData(),
            theme_rotation_minutes=(
                self._rotation_amount.value()
                * self._rotation_unit.currentData()
            ),
            theme_rotation_themes=tuple(
                key
                for key, box in self._rotation_checks.items()
                if box.isChecked()
            ) or constants.WEEKDAY_THEMES,
            theme_metals={
                theme: combo.currentData()
                for theme, combo in self._metal_combos.items()
            },
            theme_metal_follow_ring=self._metal_follow_ring.isChecked(),
            palettes=palettes,
            ring_tint=self._ring_tint,
            custom_rings=tuple(self._custom_rings),
            language=self._language_combo.currentData(),
            era_notation=self._era_combo.currentData(),
            show_era_suffix=self._era_suffix_check.isChecked(),
            third_era=self._third_era_combo.currentData(),
            jump_cities=tuple(self._jump_cities),
            art_source=self._art_source_combo.currentData(),
            z_mode=self._z_mode_combo.currentData(),
            diameter=self._diameter_slider.value(),
            archetype_names=self._archetype_names_check.isChecked(),
            pointer_saturation=self._pointer_saturation_slider.value() / 100,
            ring_saturation=self._ring_saturation_slider.value() / 100,
            **{
                key: slider.value() / 100
                for key, slider in self._size_sliders.items()
            },
        )
