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

from PySide6.QtWidgets import QDialogButtonBox, QFrame, QScrollArea, QStyle, QVBoxLayout, QWidget

from app.dialog_base import AcademyDialog
from app.section_host import SCREEN_FLOOR, SectionHost
from app.settings_dialog.custom_art_section import _CustomArtSectionMixin
from app.settings_dialog.language_system_section import (
    _LanguageSystemSectionMixin,
)
from app.settings_dialog.location_section import _LocationSectionMixin
from app.settings_store import Settings, replace
from app.theme import apply_theme, size_to_screen, style_dialog_buttons
from config import defaults
from data.locations import shared_locations


class SettingsDialog(
    AcademyDialog,
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

    # THE WINDOW'S OWN PARTS. The sidebar and the stack are what this
    # dialog's tests and the runtime layout audit have always asked it
    # for; `SectionHost` holds them now, so these two read through — and
    # both stay `None` in the sidebar-less Custom art mode, exactly as
    # the attributes they replace did.
    @property
    def _nav_list(self):
        return None if self._host is None else self._host.nav_list

    @property
    def _stack(self):
        return None if self._host is None else self._host.stack

    def __init__(self, settings: Settings, skin,
                 overlay: dict | None = None, parent=None,
                 initial_section: str | None = None):
        super().__init__("Settings", overlay, stay_on_top=True,
                         parent=parent)
        self._settings = settings
        self._skin = skin
        # THE ONE COPY RULE: the 5.6 MB city tree is shared, and this
        # dialog takes a COUNTED hold on it so a sibling picker closing
        # cannot pull it away (owner bug 2026-08-06).
        self._locations = shared_locations()
        self._locations.acquire()
        # WHERE THIS WATCH IS — one field, seeded from the settings and
        # changed only by `_apply_place`. The combo boxes below are
        # navigation; they are never read back to build the result.
        self._place = settings.place
        # The major-cities suggestions only appear on USER interaction
        # (owner 2026-07-12: the box popped huge on every open although
        # the location is picked once) — armed after construction.
        self._suggestions_armed = False

        # QUICK JUMP CITIES (Session 16, owner slika 12): the working
        # list starts from the saved settings; the group below edits it.
        self._jump_cities = list(settings.jump_cities)

        tr = self._tr
        self._custom_art_only = initial_section == "Custom art"
        if self._custom_art_only:
            # HIDDEN-FROM-SIDEBAR MODE (Phase 6 design decision, see the
            # module docstring): no nav column at all — a single scroll
            # area holding just the Custom ring/hands groups, since the
            # ONLY caller of this mode (the Watch Face Ring section's
            # "Custom ring…" button) always wants exactly this page and
            # nothing else. There is no section list here, so there is no
            # SectionHost either.
            self._host = None
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
            #
            # THE SECTIONS STAY MIXINS (WA-R16, 2026-08-19): each
            # `_build_*_group` writes its widget handles onto `self`,
            # because `result_settings()` reads them back when OK is
            # pressed. A free builder would have to be handed the dialog
            # and hand its widgets back — the back-channel a mixin exists
            # to avoid. What the shared host takes is the BUILT PAGE, so
            # it never needs to know how one was made.
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
            pages = []
            host_sections: list[tuple[str, QWidget]] = []
            for title, groups in sections:
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
                host_sections.append((f"{title}  ▸", page))
            # The sidebar width, the per-page scroll areas and the
            # nav-to-stack wiring are the host's; the measured-width
            # formula it uses is the one this dialog and the Watch Face
            # window each used to write out (see section_host.md).
            self._host = SectionHost(
                host_sections,
                parent=self,
                measure_minimum=False,
            )
            if initial_section in self._SECTION_KEYS:
                self._host.set_current_row(
                    self._SECTION_KEYS.index(initial_section)
                )
            body = self._host
            nav_width = self._host.nav_width

        layout = QVBoxLayout(self)
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
        # THE SPACE & LEGIBILITY LAW: the DECLARED minimum, computed from
        # the content itself — sidebar + the widest panel + its scrollbar
        # across; the tallest panel up to the screen floor down (panels
        # scroll lawfully past it — the window is genuinely full there).
        # Without this the minimum was whatever the layout defaulted to
        # (~290x160), and the window could be shrunk into garbage.
        margins = layout.contentsMargins()
        chrome_h = (margins.top() + margins.bottom() + layout.spacing()
                    + buttons.sizeHint().height())
        if self._host is None:
            scrollbar = self.style().pixelMetric(
                QStyle.PixelMetric.PM_ScrollBarExtent
            )
            floor_w, floor_h = SCREEN_FLOOR
            tallest = max(page.sizeHint().height() for page in pages)
            self.setMinimumSize(
                min(content_width + scrollbar + defaults.SETTINGS_PANEL_CHROME_PX, floor_w),
                min(tallest + chrome_h, floor_h),
            )
        else:
            self.setMinimumSize(
                self._host.measured_minimum(defaults.SETTINGS_PANEL_CHROME_PX, chrome_h)
            )

        if self._custom_art_only:
            # The Custom-art-only page carries no Location widgets at all
            # (see above) — nothing to restore or re-seed.
            return
        # Walk the combo boxes to where the watch IS, so the user opens
        # the dialog looking at their own city. This is presentation
        # only — `self._place` was seeded in __init__ and the cascade
        # cannot touch it (`_on_city` returns until armed, below).
        if settings.place.path:
            self._restore_path(settings.place.path)
        self._tz_label.setText(settings.place.timezone)
        self._latitude.setValue(settings.place.latitude)
        self._longitude.setValue(settings.place.longitude)
        self._results.hide()
        self._suggestions_armed = True   # from here on, changes are the user's
        # Armed LAST, so a hand-tuned coordinate is the user's doing and
        # never the seeding above.
        self._latitude.valueChanged.connect(self._on_coordinate_tuned)
        self._longitude.valueChanged.connect(self._on_coordinate_tuned)

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
            place=self._current_place(),
            language=self._language_combo.currentData(),
            era_notation=self._era_combo.currentData(),
            show_era_suffix=self._era_suffix_check.isChecked(),
            third_era=self._third_era_combo.currentData(),
            jump_cities=tuple(self._jump_cities),
            z_mode=self._z_mode_combo.currentData(),
        )
