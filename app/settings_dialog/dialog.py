"""M6 settings window — Phase 6 FINAL cleanup reduced it to THREE nav
sections (Location, Language, System): the Display, Colors and Themes
sections' whole content now lives in the Watch Face window
(`app.watch_face`), live-apply instead of on-OK. Location picker
(cascading combos over the bundled 45,650-city database + lat/lng
fine-tune) is what remains reachable from the sidebar.

The location tree loads on open and is released on close (the
repository's documented lifecycle). OK produces a new frozen Settings
via result_settings(); the controller applies and persists it — every
field NOT edited by one of the three remaining sections (or the hidden
Custom art section below) passes through UNCHANGED, so an OK here never
clobbers a pick made live in the Watch Face window.

MIXIN PILOT (God-File Split Phase 2 Step 2, `research/REFACTOR_PLAN.md`
§7; narrowed by Phase 6): this shell owns construction/lifecycle/result
assembly only; each remaining section's own groups and helpers live in
its own plain-Python mixin (never QObject-derived — only this shell
derives from QDialog): [Location Section](location_section.md),
[Custom Art Section](custom_art_section.md), [Language & System
Section](language_system_section.md). See [settings_dialog (folder)]
(___settings_dialog.md) for the full per-group behavioral narrative.

**Custom art stays HIDDEN FROM THE SIDEBAR** (Phase 6 design decision,
see the folder doc): the Watch Face Ring section's "Custom ring…"
button (`app.watch_face.ring`) still opens THIS dialog — the custom-ring/
custom-hands editor is a plain-Python mixin baked onto this shell, not a
standalone dialog, so duplicating its inline widgets elsewhere would
break Rule #5 — but it opens navigated straight to a ONE-PAGE, no-sidebar
view (`initial_section="Custom art"`) instead of the ordinary three-section
list, since nothing else ever routes a user there by browsing.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QListWidget,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.settings_dialog.custom_art_section import _CustomArtSectionMixin
from app.settings_dialog.language_system_section import (
    _LanguageSystemSectionMixin,
)
from app.settings_dialog.location_section import _LocationSectionMixin
from app.settings_store import Settings, replace
from app.theme import apply_theme, size_to_screen, style_dialog_buttons
from config import constants, defaults
from config.ui_text import ui
from data.locations import LocationRepository


class SettingsDialog(
    QDialog,
    _LocationSectionMixin,
    _CustomArtSectionMixin,
    _LanguageSystemSectionMixin,
):
    # THE THREE NAV SECTIONS' plain-English keys, in the same order the
    # `sections` list below builds them — used by `initial_section`
    # ONLY (untranslated, so a caller can jump to a section regardless
    # of the active language; the sidebar itself still shows `tr(title)`).
    # "Custom art" is NOT one of these three — it is a special HIDDEN
    # mode (see the module docstring), never a sidebar row.
    _SECTION_KEYS = ("Location", "Language", "System")

    def __init__(self, settings: Settings, skin,
                 overlay: dict | None = None, parent=None,
                 initial_section: str | None = None):
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
        # The major-cities suggestions only appear on USER interaction
        # (owner 2026-07-12: the box popped huge on every open although
        # the location is picked once) — armed after construction.
        self._suggestions_armed = False

        # QUICK JUMP CITIES (Session 16, owner slika 12): the working
        # list starts from the saved settings; the group below edits it.
        self._jump_cities = [dict(city) for city in settings.jump_cities]

        tr = self._tr
        self._custom_art_only = initial_section == "Custom art"
        if self._custom_art_only:
            # HIDDEN-FROM-SIDEBAR MODE (Phase 6 design decision, see the
            # module docstring): no nav column at all — a single scroll
            # area holding just the Custom ring/hands groups, since the
            # ONLY caller of this mode (the Watch Face Ring section's
            # "Custom ring…" button) always wants exactly this page and
            # nothing else.
            self._nav_list = None
            self._stack = None
            page = QWidget()
            page_layout = QVBoxLayout(page)
            page_layout.setContentsMargins(0, 0, 0, 0)
            page_layout.addWidget(self._build_custom_ring_group())
            page_layout.addWidget(self._build_custom_hands_group())
            page_layout.addStretch(1)
            pages: list[QWidget] = [page]
            body: QWidget = QScrollArea()
            body.setWidgetResizable(True)
            body.setFrameShape(QFrame.Shape.NoFrame)
            body.setWidget(page)
            nav_width = 0
        else:
            # THE NAVIGATION (owner ROADMAP 15h item 1, 2026-07-18; Phase
            # 6 FINAL cleanup narrowed the sidebar to three sections — the
            # Display/Colors/Themes sections' whole content now lives in
            # the Watch Face window instead): a left column of SECTION
            # TITLES (each with a right arrow ▸), clicking a title shows
            # THAT section's panel on the right. Each panel keeps its OWN
            # scroll area (owner: "keep the scroll cap for tall panels").
            sections: list[tuple[str, list]] = [
                (tr("Location"), [
                    self._build_location_group(),
                    (self._build_jump_cities_group(), 1),
                ]),
                (tr("Language"), [
                    self._build_language_group(), self._build_era_group(),
                ]),
                (tr("System"), [self._build_system_group()]),
            ]
            self._nav_list = QListWidget()
            self._nav_list.setFixedWidth(defaults.SETTINGS_NAV_WIDTH_PX)
            self._stack = QStackedWidget()
            pages = []
            for title, groups in sections:
                self._nav_list.addItem(f"{title}  ▸")
                page = QWidget()
                page_layout = QVBoxLayout(page)
                page_layout.setContentsMargins(0, 0, 0, 0)
                has_stretchy_group = False
                for entry in groups:
                    group, stretch = (
                        entry if isinstance(entry, tuple) else (entry, 0)
                    )
                    page_layout.addWidget(group, stretch)
                    has_stretchy_group = has_stretchy_group or stretch > 0
                # A page with its own stretchy group (R-29) already claims
                # all leftover space; the trailing spacer would otherwise
                # split it with a competing stretch factor.
                if not has_stretchy_group:
                    page_layout.addStretch(1)
                pages.append(page)
                panel_scroll = QScrollArea()
                panel_scroll.setWidgetResizable(True)
                panel_scroll.setFrameShape(QFrame.Shape.NoFrame)
                panel_scroll.setWidget(page)
                self._stack.addWidget(panel_scroll)
            self._nav_list.currentRowChanged.connect(self._stack.setCurrentIndex)
            self._nav_list.setCurrentRow(0)
            if initial_section in self._SECTION_KEYS:
                self._nav_list.setCurrentRow(
                    self._SECTION_KEYS.index(initial_section)
                )
            body = QHBoxLayout()
            body.addWidget(self._nav_list)
            body.addWidget(self._stack, stretch=1)
            nav_width = defaults.SETTINGS_NAV_WIDTH_PX

        layout = QVBoxLayout(self)
        if isinstance(body, QHBoxLayout):
            layout.addLayout(body, stretch=1)
        else:
            layout.addWidget(body, stretch=1)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        style_dialog_buttons(buttons)
        layout.addWidget(buttons)
        apply_theme(self)
        # OPENING SIZE (owner DESIGN #1, R4): square (1:1) at 50% of the
        # screen's available height — the dialog's own CONTENT floor
        # (nav column + widest panel, each panel already scrolling
        # vertically on its own) still wins when it is the wider of the
        # two (`size_to_screen`'s documented resolution, the same
        # "whichever is larger wins" rule the Encyclopedia's gallery
        # min-width applies), so a busy panel never needs a horizontal
        # scrollbar just to satisfy the square shape.
        content_width = max(page.sizeHint().width() for page in pages)
        min_width = content_width + nav_width + 64
        size_to_screen(
            self, 1, 1, defaults.DIALOG_SQUARE_HEIGHT_FRACTION,
            min_width=min_width,
        )

        if self._custom_art_only:
            # The Custom-art-only page carries no Location widgets at all
            # (see above) — nothing to restore or re-seed.
            return
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

    def result_settings(self) -> Settings:
        """Phase 6 FINAL cleanup: every field this dialog no longer
        edits (Opacity/Sizes/Archetype, Palette/Ring tint/Saturation,
        Theme rotation/Artwork/Subdial set/Metal shades — all now
        LIVE-APPLY in the Watch Face window) is simply OMITTED from
        `replace()` below, so it passes through UNCHANGED from
        `self._settings` — an OK here can never clobber a pick already
        applied live through the Watch Face window."""
        if self._custom_art_only:
            # The hidden Custom-art-only page edits exactly one field —
            # everything else (including every Watch-Face-owned field)
            # passes through untouched.
            return replace(
                self._settings, custom_rings=tuple(self._custom_rings),
            )
        return replace(
            self._settings,
            city_name=self._city_name,
            city_path=self._current_path(),
            latitude=round(self._latitude.value(), 4),
            longitude=round(self._longitude.value(), 4),
            timezone=self._timezone,
            language=self._language_combo.currentData(),
            era_notation=self._era_combo.currentData(),
            show_era_suffix=self._era_suffix_check.isChecked(),
            third_era=self._third_era_combo.currentData(),
            jump_cities=tuple(self._jump_cities),
            z_mode=self._z_mode_combo.currentData(),
        )
