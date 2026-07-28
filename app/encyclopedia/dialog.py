"""The Encyclopedia WINDOW — the shell that holds the three levels.

Owner rework, Session 27 (sealed 2026-07-28). The window itself owns
only what is shared: the breadcrumb, the title row with its VARIANT
switcher, the Home button, the session zoom, and the stack that shows
one of the three screens.

    ⌂ Encyclopedia › The Divine › Greek gods
              ◀   Pantheon   ▶

The variant switcher sits where the owner put it — beside the title,
not down in the page chrome — and only appears for a theme that
actually carries several registers. It is a DIFFERENT control from the
look/finish switcher inside the reader (metals, globe looks, kinship
groups), which is why the two look nothing alike.

Layer: app. Documentation: dialog.md.
"""

import json
from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QToolButton,
    QVBoxLayout,
)

from app.encyclopedia import tree as topic_tree
from app.encyclopedia.cards import row_content_width
from app.encyclopedia.home import HomeScreen
from app.encyclopedia.reader import ReaderScreen
from app.encyclopedia.themes import ThemeScreen
from app.theme import apply_theme
from app.ui_style import style_button
from config import constants, defaults, paths
from config import encyclopedia_tree as tree
from config.ui_text import ui
from data.encyclopedia import EncyclopediaRepository
from data.symbolism import SymbolismRepository

# THE SESSION ZOOM (owner round R8b item 5b): Ctrl+MouseWheel scales
# fonts/images/cards together; module-level so it SURVIVES a Home ->
# reopen within the same app run ("persisted for the session at least")
# — never written to disk, resets on app restart.
_session_zoom = 1.0

_HOME, _THEMES, _READER = 0, 1, 2


class EncyclopediaDialog(QDialog):
    def __init__(
        self,
        translations: dict | None = None,
        hidden_unlocked: bool = False,
        initial_topic: str | None = None,
        initial_entry: int = 0,
        stay_on_top: bool = False,
        travel_date: date | None = None,
    ):
        super().__init__()
        self._overlay = translations or {}
        self._tr = lambda text: ui(self._overlay, text)
        self.setWindowTitle(
            f"{constants.APP_NAME} — {self._tr('Encyclopedia')}"
        )
        # A NORMAL window by default (owner 2026-07-13: no stay-on-top —
        # it must yield to whatever has focus). In "top" z-mode the dial
        # forces itself to the TRUE top of the Z-order, so the reader
        # has to follow it up (owner verdict 2026-07-19).
        if stay_on_top:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, True)
        self.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint, True)
        # NON-MODAL lifecycle (ITEM 1, R4 2026-07-20): the controller
        # `.show()`s this dialog instead of `.exec()`ing it — the dial
        # stays interactive while it is open; WA_DeleteOnClose tears the
        # C++ object down the moment the window closes.
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self._symbolism = SymbolismRepository(overlay=self._overlay)
        self._encyclopedia = EncyclopediaRepository(overlay=self._overlay)
        self._topics = topic_tree.topics(travel_date, self._overlay)
        if hidden_unlocked:
            self._unlock_verses()
        self._zoom = _session_zoom

        # --- the chrome ----------------------------------------------------
        self._home_button = QPushButton("⌂  " + self._tr("Home"))
        self._home_button.clicked.connect(self.show_home)
        style_button(self._home_button, "home")
        self._crumbs = QLabel()
        self._crumbs.setStyleSheet(
            f"color: {defaults.THEME_COLORS['text_secondary']};"
            f"font-size: {defaults.UI_BUTTON_SMALL_FONT_PX}px;"
        )
        self._crumbs.setCursor(Qt.CursorShape.PointingHandCursor)
        self._crumbs.mouseReleaseEvent = self._crumb_clicked
        crumbs_row = QHBoxLayout()
        crumbs_row.addWidget(self._home_button)
        crumbs_row.addWidget(self._crumbs)
        crumbs_row.addStretch(1)

        self._variant_back = QToolButton()
        self._variant_back.setText("◀")
        style_button(self._variant_back, "neutral")
        self._variant_back.clicked.connect(lambda: self._step_variant(-1))
        self._variant_forward = QToolButton()
        self._variant_forward.setText("▶")
        style_button(self._variant_forward, "neutral")
        self._variant_forward.clicked.connect(lambda: self._step_variant(+1))
        self._title = QLabel()
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet(
            f"font-size: {defaults.GUIDE_TITLE_PX}px; font-weight: bold;"
            f"margin: {defaults.GUIDE_SPACING_PX}px;"
        )
        title_row = QHBoxLayout()
        title_row.addStretch(1)
        title_row.addWidget(self._variant_back)
        title_row.addWidget(self._title)
        title_row.addWidget(self._variant_forward)
        title_row.addStretch(1)

        # --- the three screens ---------------------------------------------
        self._home = HomeScreen(self._topics, self._encyclopedia, self._tr)
        self._home.opened.connect(self.show_whole)
        self._themes = ThemeScreen(self._topics, self._encyclopedia, self._tr)
        self._themes.opened.connect(self.show_topic)
        self._reader = ReaderScreen(
            self._topics, self._symbolism, self._encyclopedia, self._tr,
        )
        self._reader.page_changed.connect(self._refresh_header)
        self._reader.zoomed.connect(self._zoom_from_reader)
        self._stack = QStackedWidget()
        for screen in (self._home, self._themes, self._reader):
            self._stack.addWidget(screen)

        layout = QVBoxLayout(self)
        layout.addLayout(crumbs_row)
        layout.addLayout(title_row)
        layout.addWidget(self._stack, stretch=1)

        # THE OPENING SCREEN IS THE MINIMUM (owner spec: "Prvi ekran nema
        # scroll... min size je minimalni zoom out", "1280 x 720p"). The
        # home grid is measured from the viewport, so pinning the window
        # at the owner's own resolution is what makes the no-scroll law
        # geometric. The theme grid's own full row is checked against it
        # too — whichever needs more width wins, so a 4-card row can
        # never spill either.
        min_width = max(
            defaults.ENCYCLOPEDIA_MIN_WIDTH_PX,
            row_content_width(
                defaults.ENCYCLOPEDIA_CARD_MIN_WIDTH_PX,
                defaults.ENCYCLOPEDIA_GALLERY_MAX_COLUMNS,
            ),
        )
        self.setMinimumSize(min_width, defaults.ENCYCLOPEDIA_MIN_HEIGHT_PX)
        self.resize(min_width, defaults.ENCYCLOPEDIA_MIN_HEIGHT_PX)
        apply_theme(self)
        self.show_home()
        # The Spacebar jump (owner 2026-07-16): open straight onto the
        # hovered topic's matching entry, skipping the galleries.
        self.navigate_to(initial_topic, initial_entry)

    # --- the screens (read-only handles for the callers and tests) ----------

    @property
    def reader(self):
        return self._reader

    @property
    def home(self):
        return self._home

    @property
    def themes(self):
        return self._themes

    @property
    def screen(self) -> int:
        """Which level is showing — 0 home, 1 themes, 2 article."""
        return self._stack.currentIndex()

    # --- content ------------------------------------------------------------

    def _unlock_verses(self) -> None:
        """The Four Greetings (owner 2026-07-14): the owner's own verses,
        Serbian in EVERY language, unlocked by the hidden-mode code —
        they close the Trinity topic; a SECOND, shorter reading closes
        the Seasons topic (ROADMAP queue #6)."""
        verses = json.loads(
            (paths.database_dir() / "verses.json").read_text(encoding="utf-8")
        )
        for topic_key, data, plate in (
            ("trinity", verses["trinity"],
             defaults.SCALE_ART_DIR / "primary" / "colored" / "Union.png"),
            ("seasons", verses["seasons"],
             defaults.SEASON_ART_DIR / "Poem.png"),
        ):
            topic = self._topics[topic_key]
            topic["entries"].append({
                "images": (plate,),
                "name": data["title"],
                "article": ("verses", data),
                "poem": True,
            })
            # The unlocked page joins the topic's ONLY variant — the
            # seal ran before this, so the range has to grow with it.
            label, start, _stop = topic["variants"][-1]
            topic["variants"] = topic["variants"][:-1] + (
                (label, start, len(topic["entries"])),
            )

    # --- navigation ---------------------------------------------------------

    @property
    def topic_key(self) -> str | None:
        """The topic the reader is on — None until a page is opened.
        The window's own state lives on the reader; this is the ONE
        place outsiders read it from."""
        return self._reader.topic_key

    @property
    def entry_index(self) -> int:
        return self._reader.entry_index

    def show_home(self) -> None:
        self._stack.setCurrentIndex(_HOME)
        self._title.setText(self._tr("Encyclopedia"))
        self._home_button.hide()
        self._home.fit(self._zoom)
        self._refresh_header()

    def show_whole(self, key: str) -> None:
        self._themes.show_whole(key)
        self._stack.setCurrentIndex(_THEMES)
        self._themes.fit(self._zoom)
        self._refresh_header()

    def show_topic(self, key: str) -> None:
        self._reader.open_topic(key, 0)
        self._stack.setCurrentIndex(_READER)
        self._reader.set_zoom(self._zoom)
        self._refresh_header()

    def navigate_to(self, topic: str | None, entry: int = 0) -> None:
        """Jump this LIVE window to a (topic, entry) target named the
        dial's way — a theme key and a raw page index (see
        `tree.resolve_target`: the merged registers, the Cube's flat
        index and the weekday dual remap all resolve there).
        `topic=None` (the menu's plain "Encyclopedia…" on an already
        open window) leaves the reader where it is."""
        if topic is None:
            return
        target = topic_tree.resolve_target(self._topics, topic, entry)
        if target is None:
            return
        key, index = target
        self._reader.open_topic(key, index)
        self._stack.setCurrentIndex(_READER)
        self._reader.set_zoom(self._zoom)
        self._refresh_header()

    def _crumb_clicked(self, event) -> None:
        """The breadcrumb's middle step leads back to the whole; on the
        theme screen the whole IS the current page, so it does nothing
        there (the ⌂ button is the way home from both)."""
        if self._stack.currentIndex() == _READER and self._reader.topic_key:
            self.show_whole(tree.whole_of(self._reader.topic_key).key)

    # --- the header ---------------------------------------------------------

    def _step_variant(self, delta: int) -> None:
        self._reader.switch_variant(delta)

    def _refresh_header(self) -> None:
        """The breadcrumb, the title and the variant switcher for
        whichever screen is showing."""
        screen = self._stack.currentIndex()
        self._home_button.setVisible(screen != _HOME)
        show_variants = False
        if screen == _HOME:
            self._crumbs.setText("")
            self._title.setText(self._tr("Encyclopedia"))
        elif screen == _THEMES:
            whole = self._themes.whole
            self._crumbs.setText(f"› {self._tr(whole.title)}")
            self._title.setText(self._tr(whole.title))
            self._accent_title(whole.accent)
        else:
            topic = self._reader.topic
            whole = tree.whole_of(self._reader.topic_key)
            title = self._tr(topic["title"])
            variants = topic["variants"]
            position = topic_tree.variant_at(topic, self._reader.entry_index)
            label = variants[position][0]
            show_variants = len(variants) > 1
            # The breadcrumb names the WHOLE only: the title row right
            # under it already carries the theme, and the owner's round
            # R8b complaint was exactly a name printed twice.
            self._crumbs.setText(f"› {self._tr(whole.title)}")
            self._title.setText(
                f"{title} — {self._tr(label)}" if show_variants else title
            )
            self._accent_title(whole.accent)
        self._variant_back.setVisible(show_variants)
        self._variant_forward.setVisible(show_variants)

    def _accent_title(self, accent: str) -> None:
        self._title.setStyleSheet(
            f"font-size: {defaults.GUIDE_TITLE_PX}px; font-weight: bold;"
            f"margin: {defaults.GUIDE_SPACING_PX}px; color: {accent};"
        )

    # --- zoom ---------------------------------------------------------------

    def _zoom_from_reader(self, zoom: float) -> None:
        global _session_zoom
        self._zoom = zoom
        _session_zoom = zoom

    def _apply_zoom_delta(self, angle_delta_y: int) -> None:
        """One Ctrl+wheel notch (owner round R8b item 5b) — Qt reports
        ±120 `angleDelta().y()` per notch. Clamped to
        `ENCYCLOPEDIA_ZOOM_RANGE` and written back to the module-level
        `_session_zoom`, so the next Encyclopedia window this app run
        opens seeds from where this one left off."""
        global _session_zoom
        low, high = constants.ENCYCLOPEDIA_ZOOM_RANGE
        steps = angle_delta_y / 120.0
        self._zoom = max(
            low, min(high, self._zoom + steps * constants.ENCYCLOPEDIA_ZOOM_STEP)
        )
        _session_zoom = self._zoom
        self._apply_zoom()

    def _apply_zoom(self) -> None:
        screen = self._stack.currentIndex()
        if screen == _HOME:
            self._home.fit(self._zoom)
        elif screen == _THEMES:
            self._themes.fit(self._zoom)
        else:
            self._reader.set_zoom(self._zoom)

    def wheelEvent(self, event) -> None:      # noqa: N802 — Qt override
        """Ctrl+MouseWheel zooms the WHOLE encyclopedia when the cursor
        sits over the dialog's own chrome; the reader's viewport
        installs the identical guard as an event filter of its own (Qt
        delivers a wheel event to the widget under the cursor, so both
        paths are needed to cover every cursor position)."""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self._apply_zoom_delta(event.angleDelta().y())
            event.accept()
            return
        super().wheelEvent(event)

    def showEvent(self, event) -> None:       # noqa: N802 — Qt override
        # The galleries are built BEFORE the window has its real
        # geometry — fit once more on the first show (owner bug
        # 2026-07-13: deformed until a manual resize).
        super().showEvent(event)
        self._apply_zoom()
