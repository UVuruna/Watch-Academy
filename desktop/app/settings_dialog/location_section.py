"""Location Section — `_LocationSectionMixin`: the Location group
(cascading Continent/Subregion/Country/Region/City combos over the
45,650-city database, live search, lat/lng fine-tune) and the Quick
Jump cities group (Session 16, owner slika 12). Plain-Python mixin
(no base class — composed onto `dialog.SettingsDialog`'s `QDialog`
shell, `research/REFACTOR_PLAN.md` §7). See
[Location Section](location_section.md) for the full behavioral
narrative.
"""

import dataclasses

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
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
    QSizePolicy,
)

from config import constants
from data.locations import Place, fold_name

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
        self._latitude.setValue(self._place.latitude)
        self._longitude = QDoubleSpinBox()
        self._longitude.setDecimals(4)
        self._longitude.setRange(*constants.LONGITUDE_RANGE)
        self._longitude.setValue(self._place.longitude)
        form.addRow(tr("Latitude"), self._latitude)
        form.addRow(tr("Longitude"), self._longitude)
        self._tz_label = QLabel(self._place.timezone)
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
        """A city seat in the cascade became current. Only a USER pick
        counts — during construction the cascade settles on whatever is
        alphabetically first (Africa ▸ Eastern Africa ▸ Burundi ▸
        Bubanza), and that arbitrary landing spot must never become this
        watch's place. `_suggestions_armed` is that line."""
        if not self._suggestions_armed:
            return
        name = self._city.currentText()
        if not name:
            return
        node = next(
            (
                child
                for child in self._locations.children(self._group_path())
                if child.name == name and child.is_city
            ),
            None,
        )
        if node is None:
            return                       # combos mid-rebuild
        self._apply_place(node.record)

    def _apply_place(self, place: Place) -> None:
        """THE ONE place a picked location lands on this dialog — the
        combo picker (`_on_city`), the live search (through the combos)
        and a DOUBLE-CLICK on a saved Quick Jump city all funnel here,
        and each of them hands over a WHOLE `Place`.

        `self._place` is the dialog's answer on OK. The combo boxes are
        navigation and nothing else: they are never read back to build
        the result. That is the whole cure for "BELGRADE BURUNDI" —
        before this, `result_settings()` took the name from the settings
        and the PATH from wherever the combos happened to sit."""
        self._place = place
        self._tz_label.setText(place.timezone)
        # Signals blocked: writing the picked record's own coordinates
        # into the spin boxes is NOT the user tuning them by hand, and
        # `_on_coordinate_tuned` would otherwise drop the path we just
        # received.
        for box, value in (
            (self._latitude, place.latitude),
            (self._longitude, place.longitude),
        ):
            box.blockSignals(True)
            box.setValue(value)
            box.blockSignals(False)
        # THE STAR FOLLOWS (owner sheet 2026-08-16): the watch's place is
        # always in the Quick Jump list and always the starred row, so a
        # pick in the combos above moves the star here too. Guarded for
        # the build order — the Location group is constructed before the
        # Quick Jump group exists.
        if hasattr(self, "_jump_list"):
            self._refresh_jump_list()

    def _restore_path(self, path: tuple[str, ...]) -> None:
        """Walk the combo boxes to the stored place so the user opens
        the dialog looking at where the watch IS. Unknown segments are
        ignored (a database update must not break the dialog) — and now
        that costs nothing, because a half-walked cascade can no longer
        be mistaken for a location: `self._place` already holds it."""
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
        index = self._city.findText(path[-1])
        if index >= 0:
            self._city.setCurrentIndex(index)

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
        # The frame is the WIDGET's own, not a guessed +10: the themed
        # QSS gives this list a 7px frame per side, so a single 40px row
        # needed 54px and the hard-coded arithmetic handed it 50 — four
        # px of its only row cut off (ALG-1 state matrix, 2026-08-09).
        frame = 2 * self._results.frameWidth()
        self._results.setFixedHeight(min(120, rows * row_height + frame))  # layout-law: exempt - live-search dropdown computed from its own rows and frame; scrolls only past 120px of results
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

    def _on_coordinate_tuned(self) -> None:
        """The user typed a coordinate by hand. It is still ONE place —
        the name and the zone are kept, but the PATH is dropped: these
        coordinates are no longer the database record that path names,
        and a path that no longer describes its own place is exactly the
        lie this whole design exists to make unwritable. The crown then
        falls back to the zone's region, honestly."""
        self._place = dataclasses.replace(
            self._place,
            path=(),
            latitude=round(self._latitude.value(), 4),
            longitude=round(self._longitude.value(), 4),
        )

    def _current_place(self) -> Place:
        """This dialog's answer on OK — the whole place, from the one
        field that holds it. Never assembled from the combo boxes."""
        return self._place

    def _build_jump_cities_group(self) -> QGroupBox:
        """The user's own places for the Quick Jump ▸ Location submenu.

        THE STARRED CITY (owner sheet 2026-08-16, his second screenshot).
        The rules are his, and they are one mechanism, not three:

          * The list may hold many cities, but it always holds AT LEAST
            ONE, and exactly one of them wears the star: that is the
            place the watch is showing right now.
          * A city is ADDED from the Location picker ABOVE — "there is
            no second search box; this list is where the picked city
            gets written". So the Add row is a BUTTON, not a search
            field, and the picker above is the one way into it.
          * "Make Main" selects which of them the watch displays.
          * Remove takes one away, except the last one and except the
            starred one — the invariant above forbids both.

        The star is not a flag stored beside the list: `self._place` IS
        the starred city (`_is_main` compares them), so there is exactly
        one answer to "where is this watch" and the list renders it
        rather than duplicating it."""
        tr = self._tr
        group = QGroupBox(tr("Quick Jump cities"))
        group.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
        )
        form = QFormLayout(group)
        # ADD COMES FROM ABOVE (his order): the button takes whatever the
        # Location picker currently shows. A second live-search box used
        # to sit here, over the same 45k cities and the same folding —
        # two ways to name a city, on one page, one of which silently did
        # NOT move the watch. Gone.
        self._jump_add = QPushButton(tr("Add the city above"))
        self._jump_add.clicked.connect(self._add_jump_city)
        form.addRow(tr("Add"), self._jump_add)
        self._jump_list = QListWidget()
        # R-29: no height cap — the Location page gives this GROUP a
        # stretch factor (`dialog.py`'s section table) so the list is
        # free to consume every pixel of vertical space left below the
        # Location group instead of sitting capped in a mostly-empty
        # page.
        self._jump_list.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
        )
        # Expanding gives it every SPARE pixel; it does not stop the
        # layout from crushing it when there are none. At the latitude
        # slider's own extreme the rows above grow and this list was
        # squeezed to 50px while needing 72 (ALG-1 state matrix, picker
        # driver 2026-08-09 — a South Pole observer reaches it). Fixed
        # POLICY, not a fixed number: three of its OWN rows plus frame,
        # so the floor follows the theme's metrics.
        self._jump_list.setMinimumHeight(
            3 * self._jump_list.fontMetrics().height() + 4 * 6
        )
        # R-32: double-click is the same thing "Make Main" does — one
        # body (`_make_main`), two ways to reach it.
        self._jump_list.itemDoubleClicked.connect(
            self._apply_jump_city_as_location
        )
        self._jump_list.currentRowChanged.connect(
            lambda _row: self._refresh_jump_buttons()
        )
        form.addRow(tr("Cities"), self._jump_list)
        buttons = QHBoxLayout()
        self._jump_main = QPushButton(tr("Make Main"))
        self._jump_main.clicked.connect(self._make_main_selected)
        self._jump_remove = QPushButton(tr("Remove selected"))
        self._jump_remove.clicked.connect(self._remove_jump_city)
        buttons.addWidget(self._jump_main)
        buttons.addWidget(self._jump_remove)
        form.addRow("", buttons)
        note = QLabel(
            tr(
                "The starred city is the one this watch shows. The rest "
                "appear in Quick Jump ▸ Location and move the observer "
                "there — the traveled moment stays."
            )
        )
        note.setWordWrap(True)
        form.addRow(note)
        self._refresh_jump_list()
        return group

    def _is_main(self, city: Place) -> bool:
        """Is this the STARRED city — the one the watch shows? There is
        no stored flag: `self._place` is the answer, so the star cannot
        drift away from the place the way `city_path` once drifted away
        from `city_name`."""
        return city == self._place

    def _add_jump_city(self) -> None:
        """Add the city the Location picker above currently shows (owner
        order 2026-08-16: "ADD City goes through the Location above —
        this is where the added city gets written")."""
        if self._place not in self._jump_cities:
            self._jump_cities.append(self._place)
        # Pressing Add is the user KEEPING this city: it stops being the
        # replaceable seed slot above, so the next navigation cannot
        # overwrite it.
        self._seeded_place = None
        self._refresh_jump_list()

    def _remove_jump_city(self) -> None:
        """Take a city off the list — never the starred one, and never
        the last one. His invariant: at least one city, and the starred
        one is where the watch stands; removing it would leave the watch
        somewhere the list does not admit to."""
        row = self._jump_list.currentRow()
        if not 0 <= row < len(self._jump_cities):
            return
        if len(self._jump_cities) <= 1 or self._is_main(self._jump_cities[row]):
            return
        del self._jump_cities[row]
        self._refresh_jump_list()

    def _make_main_selected(self) -> None:
        """"Make Main": the selected city becomes the one the watch
        shows. Same body as the double-click (Rule #5)."""
        row = self._jump_list.currentRow()
        if 0 <= row < len(self._jump_cities):
            self._make_main(self._jump_cities[row])

    def _apply_jump_city_as_location(self, item: QListWidgetItem) -> None:
        """R-32: double-click a saved city to make it the main one."""
        self._make_main(self._jump_cities[self._jump_list.row(item)])

    def _make_main(self, city: Place) -> None:
        """The star moves. `_apply_place` is the ONE door a location
        goes through, so this is a starred-city move and a location
        change in a single act rather than two states to keep in step."""
        self._apply_place(city)
        self._refresh_jump_list()

    def _refresh_jump_list(self) -> None:
        """Repaint the list, and hold his invariant while doing it: the
        watch's own place is ALWAYS in the list, so an empty list (a
        fresh install, or an older settings file that never had one)
        seeds itself from the place instead of showing him nothing.

        THE SEED IS ONE SLOT, NOT A GROWING TAIL (owner bug 2026-08-16).
        Walking the combos to a searched city passes THROUGH every
        intermediate seat (`_restore_search` sets five combos, and each
        one fires `_on_city` ▸ `_apply_place` ▸ here). When this method
        merely inserted, one click on "Munich" wrote Andorra la Vella,
        Abensberg and Berlin into his list on the way. So the seed is
        remembered: a place that is only here because the watch stands
        on it is REPLACED by the next such place, and only a city the
        user ADDED (or loaded from settings) keeps its row."""
        if self._place not in self._jump_cities:
            seed = getattr(self, "_seeded_place", None)
            if seed is not None and seed in self._jump_cities:
                self._jump_cities[self._jump_cities.index(seed)] = self._place
            else:
                self._jump_cities.insert(0, self._place)
            self._seeded_place = self._place
        row = self._jump_list.currentRow()
        self._jump_list.clear()
        # THE STAR RIDES THE ICON SLOT, not a run of spaces. Spaces were
        # the first attempt and the independent grader caught them: four
        # spaces are not the width of "★ ", so the unstarred names
        # started a few pixels left of the starred one and the column
        # read as broken. Qt's icon slot is a FIXED column — a blank
        # pixmap of the same size holds it open — so every city name
        # begins at the identical x whether it wears the star or not.
        for city in self._jump_cities:
            item = QListWidgetItem(f"{city.name}  —  {city.timezone}")
            item.setIcon(
                self._star_icon() if self._is_main(city) else self._blank_icon()
            )
            self._jump_list.addItem(item)
        if 0 <= row < len(self._jump_cities):
            self._jump_list.setCurrentRow(row)
        self._refresh_jump_buttons()

    def _star_icon(self) -> QIcon:
        """The star that marks the city this watch shows, drawn at the
        list's own text height so it scales with the theme's metrics
        rather than with a pixel constant."""
        if getattr(self, "_star_pixmap", None) is None:
            side = self._jump_list.fontMetrics().height()
            pixmap = QPixmap(side, side)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
            painter.setPen(self._jump_list.palette().text().color())
            painter.drawText(
                pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "★"
            )
            painter.end()
            self._star_pixmap = pixmap
        return QIcon(self._star_pixmap)

    def _blank_icon(self) -> QIcon:
        """The star's column, held open on a city that does not wear it
        — the whole reason the names line up."""
        if getattr(self, "_blank_pixmap", None) is None:
            side = self._jump_list.fontMetrics().height()
            pixmap = QPixmap(side, side)
            pixmap.fill(Qt.GlobalColor.transparent)
            self._blank_pixmap = pixmap
        return QIcon(self._blank_pixmap)

    def _refresh_jump_buttons(self) -> None:
        """Both buttons say what they can do BEFORE they are pressed —
        a Remove that silently declines is the "dead pill" defect this
        project has already paid for twice."""
        row = self._jump_list.currentRow()
        selected = 0 <= row < len(self._jump_cities)
        city = self._jump_cities[row] if selected else None
        self._jump_main.setEnabled(selected and not self._is_main(city))
        self._jump_remove.setEnabled(
            selected and not self._is_main(city) and len(self._jump_cities) > 1
        )
