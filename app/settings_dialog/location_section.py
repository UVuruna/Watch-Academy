"""Location Section — `_LocationSectionMixin`: the Location group
(cascading Continent/Subregion/Country/Region/City combos over the
45,650-city database, live search, lat/lng fine-tune) and the Quick
Jump cities group (Session 16, owner slika 12). Plain-Python mixin
(no base class — composed onto `dialog.SettingsDialog`'s `QDialog`
shell, `research/REFACTOR_PLAN.md` §7). See
[Location Section](location_section.md) for the full behavioral
narrative.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
)

from config import constants
from data.locations import fold_name

_NO_REGION = "—"                       # the country's direct cities


class _LocationSectionMixin:
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
