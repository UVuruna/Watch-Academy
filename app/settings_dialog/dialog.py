"""M6 settings window: location picker (cascading combos over the
bundled 45,650-city database + lat/lng fine-tune), Star/Aura opacity
sliders and the palette chip editor for the active (pointer, style).

The location tree loads on open and is released on close (the
repository's documented lifecycle). OK produces a new frozen Settings
via result_settings(); the controller applies and persists it.

MIXIN PILOT (God-File Split Phase 2 Step 2, `research/REFACTOR_PLAN.md`
§7): the dialog already self-organizes into SEVEN nav sections — the
cleanest split boundary in the plan (UI-given, not inferred). This
shell owns construction/lifecycle/result assembly only; every
section's own groups and helpers moved verbatim into its own
plain-Python mixin (never QObject-derived — only this shell derives
from QDialog): [Location Section](location_section.md), [Display
Section](display_section.md), [Colors Section](colors_section.md),
[Custom Art Section](custom_art_section.md), [Themes Section]
(themes_section.md), [Language & System Section]
(language_system_section.md). See [settings_dialog (folder)]
(___settings_dialog.md) for the full per-group behavioral narrative.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QListWidget,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.settings_dialog.colors_section import _ColorsSectionMixin
from app.settings_dialog.custom_art_section import _CustomArtSectionMixin
from app.settings_dialog.display_section import _DisplaySectionMixin
from app.settings_dialog.language_system_section import (
    _LanguageSystemSectionMixin,
)
from app.settings_dialog.location_section import _LocationSectionMixin
from app.settings_dialog.themes_section import _ThemesSectionMixin
from app.settings_store import Settings, replace
from app.theme import apply_theme, size_to_screen, style_dialog_buttons
from config import constants, defaults
from config.ui_text import ui
from data.locations import LocationRepository


class SettingsDialog(
    QDialog,
    _LocationSectionMixin,
    _DisplaySectionMixin,
    _ColorsSectionMixin,
    _CustomArtSectionMixin,
    _ThemesSectionMixin,
    _LanguageSystemSectionMixin,
):
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
                self._build_subdial_set_group(), self._build_metal_shade_group(),
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
        min_width = content_width + defaults.SETTINGS_NAV_WIDTH_PX + 64
        size_to_screen(
            self, 1, 1, defaults.DIALOG_SQUARE_HEIGHT_FRACTION,
            min_width=min_width,
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
            subdial_set=self._subdial_set_combo.currentData(),
            metal_shade_gold=self._metal_shade_combos["gold"].currentData(),
            metal_shade_bronze=self._metal_shade_combos["bronze"].currentData(),
            metal_shade_silver=self._metal_shade_combos["silver"].currentData(),
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
