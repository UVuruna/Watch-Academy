"""THE SPACE & LEGIBILITY LAW — the runtime audit (rules/GUI.md).

Expanded 2026-08-06 (owner order, after the Watch Face rework shipped a
window whose sections overflow even a 4K screen): the registry now holds
EVERY top-level window of the project, the checks are the reference set
from Vibe Coder's audit (OVERLAP and ITEM CUT included — sizes can all
be green while two cells are painted over each other), and every window
is screenshotted at its minimum for the DESIGN REVIEW gate
(`.claude/shots/`, graded >= 8/10 in `.claude/layout-proof.md`).

Checked, on a REAL constructed window at its declared minimum AND larger:

  A. CLIPPED      — a widget got less room than it minimally needs
  B. ELIDED       — text does not fit its own element
  C. SCROLL+SLACK — something scrolls while a spacer in the same window
                    holds unused space; and a visible bar with an empty
                    range (a bar over content that already fits)
  D. ITEM CUT     — a list/table row wider than the column it sits in
                    (item views truncate silently; items are not widgets)
  E. OVERLAP      — two cells of one layout drawn on the same pixels

plus the two preconditions the law puts on every window:

  - a DECLARED minimum size, COMPUTED from real content, and
  - that minimum FITS THE SCREEN FLOOR 1280x720 — a window demanding a
    screen the user does not have is the absurd-minimum bug; the answer
    is REFLOW, never widen (`.claude/layout-frame.json` may raise the
    floor, with a written reason).

Windows NOT in the registry, and why:
  - ClockWidget — the frameless transparent dial itself; its size is the
    user-chosen dial diameter plus a computed margin, there is no text
    layout to starve (hover text lives in LegendPopup, which IS audited).
  - _EnlargeDialog (observatory) — a child that fits one chart to the
    screen; it holds exactly one stretched chart and no prose.
  - FastTravelFlash — a transient frameless flash overlay, shown for
    milliseconds during a jump; nothing on it is read.

The platform: native when a desktop exists (real fonts, real DPI — the
Vibe Coder lesson: offscreen's substitute fonts measured a different
window than the one the owner photographed), offscreen as the headless
fallback. Windows are shown with WA_DontShowOnScreen, so a guard run
never flashes windows across the owner's screen.

Zubi v2 (rules/GUI.md -> Zubi v2, installed 2026-08-08): `layout_checks_qt.py`
beside this file is the rules/templates/ check library, copied verbatim
(the ALG-1..ALG-9 algorithmic teeth) - `_audit()` below folds its checks in
beside the reference-set ones above, ALG-1 (`check_extreme_states`) is driven
with THIS project's own combined invariants, ALG-7 (`check_row_occupancy`)
only at the minimum size per the rulebook, and ALG-8 (`live_profile_source`,
wired to watch 1's real settings.json) runs every window a second time.
ALG-9 (`check_section_taxonomy`) is fed separately, from SettingsDialog's own
nav structure, in `test_section_taxonomy` below - it is not part of the
generic walk (see the check's own docstring). First-run findings are recorded
verbatim, NOT fixed, in `.claude/zubi-v2-findings.md` per the owner's boundary
("ne popravljaj postojeće stanje, samo ugrađuj pravila za buduće agente").
"""

from __future__ import annotations

import json
import math
import os
import re
import sys
from dataclasses import replace
from pathlib import Path

import pytest
from PySide6.QtCore import QPoint, QSize, Qt
from PySide6.QtWidgets import (
    QAbstractScrollArea,
    QApplication,
    QCheckBox,
    QHeaderView,
    QLabel,
    QLayout,
    QLineEdit,
    QListWidget,
    QPushButton,
    QSpacerItem,
    QTableWidget,
    QWidget,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:      # standalone report mode (main())
    sys.path.insert(0, str(PROJECT_ROOT))
TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:         # layout_checks_qt.py lives here
    sys.path.insert(0, str(TESTS_DIR))
# THE THREE-FOLDER MIGRATION (2026-08-12): .claude/ is agent tooling, not
# bundled app data — it stays at the TRUE repo root, one level above the
# desktop Python root this file now lives under.
REPO_ROOT = PROJECT_ROOT.parent

from layout_drive_qt import check_extreme_states              # noqa: E402
from layout_checks_qt import (                               # noqa: E402
    _fits_its_own_content, _window_image, active_profile, check_contrast,
    check_outside_window, check_radius, check_row_occupancy,
    check_section_taxonomy, check_space_ceiling, check_tooltips,
    check_uniform_siblings, live_profile_copy, live_profile_source)

# px of slack tolerated before a spacer counts as "unused space"
SLACK_TOLERANCE = 24

# px of padding assumed between a framed element's frame and its text
TEXT_PADDING = 8

# The screen every window must survive. Raising it needs
# `.claude/layout-frame.json` = {"width": W, "height": H, "reason": "..."}.
_FRAME_FILE = REPO_ROOT / ".claude" / "layout-frame.json"
FLOOR_WIDTH, FLOOR_HEIGHT = 1280, 720
if _FRAME_FILE.is_file():
    _frame = json.loads(_FRAME_FILE.read_text(encoding="utf-8"))
    if _frame.get("reason"):
        FLOOR_WIDTH = int(_frame.get("width", FLOOR_WIDTH))
        FLOOR_HEIGHT = int(_frame.get("height", FLOOR_HEIGHT))

# The DESIGN REVIEW shots: one per window state, at the declared minimum.
# In a TOPIC subfolder (rules/GUI.md -> "Screenshots live in TOPIC
# folders", GATE): the audit's own design-review shots are one story —
# loose files in the shots ROOT block the session's end, and this
# writer used to recreate them on every full guard run.
SHOT_DIR = REPO_ROOT / ".claude" / "shots" / "layout-audit"

#: The larger size every window is audited at besides its minimum.
_LARGER = (1400, 900)


@pytest.fixture(scope="module")
def app():
    return _make_app()


def _make_app() -> QApplication:
    """Native platform first (real fonts, real DPI), offscreen only when
    there is no desktop to talk to. Either way the audit measures REAL
    glyphs: in a guard run an earlier module has already flipped the
    process to offscreen, whose platform font database is EMPTY (the
    tofu-shot root cause — tests/offscreen_fonts.py), so the machine's
    fonts are provisioned into it before any window is measured."""
    from tests.offscreen_fonts import provision

    existing = QApplication.instance()
    if existing is not None:
        provision()
        return existing
    try:
        app = QApplication([])
    except Exception:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        app = QApplication([])
    provision()
    return app


def _settle(window: QWidget, width: int, height: int) -> None:
    window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
    window.resize(width, height)
    window.show()
    QApplication.processEvents()
    # A second pass: the first installs the layout, the second lets the
    # scroll areas react to the geometry it produced. A THIRD since
    # 2026-08-14: the gallery grammar added one more dependent level
    # (card flow -> CardGroup -> page -> scroll area), and each level's
    # height is only knowable once the level above has a width, so Qt
    # needs one settling pass per level. This changes WHEN the audit
    # measures, never WHAT it accepts — the state measured here is the
    # one Qt paints, which is the state the law is about (the design
    # shots this same function writes show it).
    QApplication.processEvents()
    QApplication.processEvents()


# --- the checks (reference set — Vibe Coder's audit) -----------------------


def _walk(window: QWidget):
    yield window
    for child in window.findChildren(QWidget):
        if child.isVisible():
            yield child


def check_declared_minimum(window: QWidget) -> list[str]:
    minimum = window.minimumSize()
    if minimum.width() <= 0 or minimum.height() <= 0:
        return ["no declared minimum size - the law requires one, COMPUTED "
                "from the longest real content (setMinimumSize)"]
    if minimum.width() > FLOOR_WIDTH or minimum.height() > FLOOR_HEIGHT:
        return [f"ABSURD MINIMUM {minimum.width()}x{minimum.height()} - it "
                f"does not fit the screen floor {FLOOR_WIDTH}x{FLOOR_HEIGHT}: "
                "the window demands a screen the user does not have. REFLOW "
                "it (ladder step 2); widening your way out is the bug itself"]
    return []


def _layout_cells(layout: QLayout, path: str = ""):
    """Every cell a layout hands out, recursing into nested layouts —
    a row inside a column is where colliding siblings actually live."""
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item is None:
            continue
        child = item.layout()
        if child is not None:
            yield from _layout_cells(child, f"{path}/layout{i}")
            continue
        widget = item.widget()
        if widget is None or widget.isHidden():
            continue
        name = widget.objectName() or widget.__class__.__name__
        yield f"{path}/{name}", item.geometry()


def check_overlap(window: QWidget) -> list[str]:
    """E. OVERLAP — every other check asks whether an element got its own
    SIZE; this one asks where it was PUT. Qt does not clip a layout short
    of space — it overlaps it, so sizes stay green while two cells paint
    the same pixels."""
    problems = []
    for widget in _walk(window):
        layout = widget.layout()
        if layout is None:
            continue
        cells = list(_layout_cells(layout))
        for i, (name_a, rect_a) in enumerate(cells):
            for name_b, rect_b in cells[i + 1:]:
                if rect_a.intersects(rect_b):
                    hit = rect_a.intersected(rect_b)
                    problems.append(
                        f"OVERLAP in "
                        f"{widget.objectName() or widget.__class__.__name__}: "
                        f"'{name_a}' {rect_a.x()},{rect_a.y()} "
                        f"{rect_a.width()}x{rect_a.height()} is drawn over "
                        f"'{name_b}' {rect_b.x()},{rect_b.y()} "
                        f"{rect_b.width()}x{rect_b.height()} "
                        f"({hit.width()}x{hit.height()} px shared)")
    return problems


def check_clipping(window: QWidget) -> list[str]:
    problems = []
    for widget in _walk(window):
        if isinstance(widget, QHeaderView):
            # Qt returns an orientation-blind SQUARE for a header's
            # minimumSizeHint — only the header's own axis is meaningful.
            hint = widget.sizeHint()
            if widget.orientation() == Qt.Orientation.Horizontal:
                need = QSize(widget.width(),
                             max(hint.height(), widget.fontMetrics().height()))
            else:
                need = QSize(max(hint.width(), 8), widget.height())
        elif (widget.minimumSize() == widget.maximumSize()
                and widget.minimumSize().width() > 0):
            # A deliberately FIXED widget (setFixedSize: min == max — the
            # 22px round color swatches). Qt's minimumSizeHint for e.g. a
            # QPushButton quotes text margins the swatch never uses; the
            # static law's exemption line governs these, and the elision/
            # overlap checks still see them.
            continue
        else:
            need = widget.minimumSizeHint()
            if (need.height() > widget.height()
                    and widget.minimumHeight() == widget.maximumHeight()
                    and _fits_its_own_content(widget)):
                # A deliberately FIXED HEIGHT that still shows all its own
                # content. Qt hands every item view a generic 72px
                # minimumSizeHint with nothing to do with what is in it, so
                # a live-search dropdown sized to its one row read as
                # clipped while showing that row whole (ALG-1 state matrix,
                # 2026-08-09). The same state matrix DID find a real 4px
                # cut behind it, which is why this judges CONTENT rather
                # than exempting fixed heights outright.
                need = QSize(need.width(), widget.height())
            layout = widget.layout()
            if layout is not None and layout.hasHeightForWidth():
                # A container of WRAPPING children has no single minimum
                # height — heightForWidth at the width it ACTUALLY has is
                # the honest question.
                need = QSize(
                    need.width(),
                    max(need.height(), layout.heightForWidth(widget.width())))
        if need.width() > widget.width() or need.height() > widget.height():
            problems.append(
                f"CLIPPED {widget.__class__.__name__} "
                f"'{widget.objectName() or '-'}': has "
                f"{widget.width()}x{widget.height()}, needs at least "
                f"{need.width()}x{need.height()}")
    return problems


def _visible_text(widget: QWidget) -> str:
    if isinstance(widget, (QLabel, QPushButton, QCheckBox)):
        return widget.text()
    if isinstance(widget, QLineEdit):
        return widget.text() or widget.placeholderText()
    return ""


def check_elision(window: QWidget) -> list[str]:
    problems = []
    for widget in _walk(window):
        text = _visible_text(widget)
        if not text:
            continue
        metrics = widget.fontMetrics()
        # A QLabel paints straight into its contentsRect; framed controls
        # lose their frame plus padding.
        padding = 0 if isinstance(widget, QLabel) else TEXT_PADDING
        available = widget.contentsRect().width() - padding
        if isinstance(widget, QLabel) and widget.wordWrap():
            wanted = metrics.boundingRect(
                0, 0, max(available, 1), 10_000, 0x1000, text).height()
            if wanted > widget.contentsRect().height():
                problems.append(
                    f"ELIDED (wrapped text taller than its element) "
                    f"{widget.__class__.__name__} '{text[:40]}': needs "
                    f"{wanted}px height, has {widget.contentsRect().height()}")
            continue
        wanted = metrics.horizontalAdvance(text)
        if wanted > available:
            problems.append(
                f"ELIDED {widget.__class__.__name__} '{text[:40]}': text "
                f"needs {wanted}px, element offers {available}px")
    return problems


def check_item_views(window: QWidget) -> list[str]:
    """D. ITEM CUT — item views truncate silently; an item is not a
    QWidget, so the widget checks above never see its text. The needed
    width is Qt's OWN sizeHintForColumn, never a hand-rolled estimate."""
    problems = []
    for widget in _walk(window):
        if isinstance(widget, QTableWidget):
            for col in range(widget.columnCount()):
                wanted = widget.sizeHintForColumn(col)
                if wanted > widget.columnWidth(col):
                    texts = [widget.item(r, col).text()
                             for r in range(widget.rowCount())
                             if widget.item(r, col) is not None]
                    longest = max(texts, key=len, default="")
                    problems.append(
                        f"ITEM CUT {widget.__class__.__name__} column {col} "
                        f"(longest '{longest[:40]}'): needs {wanted}px, "
                        f"column offers {widget.columnWidth(col)}px")
        elif isinstance(widget, QListWidget) and widget.count():
            wanted = widget.sizeHintForColumn(0)
            if wanted > widget.viewport().width():
                longest = max(
                    (widget.item(r).text() for r in range(widget.count())),
                    key=len, default="")
                problems.append(
                    f"ITEM CUT {widget.__class__.__name__} "
                    f"'{widget.objectName() or '-'}' "
                    f"(longest '{longest[:40]}'): needs {wanted}px, list "
                    f"offers {widget.viewport().width()}px")
    return problems


def _ancestor_spacer_slack(widget: QWidget, window: QWidget,
                           vertical: bool) -> list[str]:
    """Spacers between `widget` and `window` that were handed real space
    ON THE SCROLLED AXIS — a 600x0 spacer holds no vertical space, so it
    is no excuse for a vertical scrollbar and no fault beside one."""
    slack = []
    node = widget.parentWidget()
    while node is not None:
        layout = node.layout()
        if layout is not None:
            for index in range(layout.count()):
                item = layout.itemAt(index)
                if isinstance(item, QSpacerItem):
                    geometry = item.geometry()
                    held = geometry.height() if vertical else geometry.width()
                    if held > SLACK_TOLERANCE:
                        slack.append(
                            f"{node.__class__.__name__}"
                            f"'{node.objectName() or '-'}' holds a spacer "
                            f"of {geometry.width()}x{geometry.height()}px")
        if node is window:
            break
        node = node.parentWidget()
    return slack


def check_scroll_with_free_space(window: QWidget) -> list[str]:
    problems = []
    for widget in _walk(window):
        if not isinstance(widget, QAbstractScrollArea):
            continue
        for axis, vertical, bar in (
                ("vertically", True, widget.verticalScrollBar()),
                ("horizontally", False, widget.horizontalScrollBar())):
            if bar is None:
                continue
            if bar.isVisible() and bar.maximum() <= bar.minimum():
                problems.append(
                    f"SCROLLBAR OVER FITTING CONTENT "
                    f"{widget.__class__.__name__} "
                    f"'{widget.objectName() or '-'}': {axis} bar visible "
                    "with an empty range - the content already fits")
                continue
            if bar.maximum() <= 0:
                continue
            slack = _ancestor_spacer_slack(widget, window, vertical)
            if slack:
                problems.append(
                    f"SCROLL+SLACK {widget.__class__.__name__} "
                    f"'{widget.objectName() or '-'}' scrolls {axis} while "
                    f"the same window holds unused space: "
                    + "; ".join(slack)
                    + " - ladder step 1: the starving element takes the "
                      "free space before any scrollbar appears")
    return problems


def _state_invariants(window: QWidget) -> list[str]:
    """The geometric checks that must hold in EVERY state - the reference
    set above (overlap/clipping/elision/item-cut/scroll) plus the Zubi v2
    ALG-1 invariant (nothing paints outside the window rect). This is what
    ALG-1's `check_extreme_states` re-runs after every slider/checkbox/combo
    move, and what the per-state loop below runs at the default position."""
    return (check_overlap(window)
            + check_clipping(window)
            + check_elision(window)
            + check_item_views(window)
            + check_scroll_with_free_space(window)
            + check_outside_window(window))


def _audit(window: QWidget, image=None, at_minimum: bool = False) -> list[str]:
    """The reference-set invariants (`_state_invariants`) plus the Zubi v2
    ALG checks that are not part of the extreme-state matrix itself:
    ALG-2 contrast, ALG-3 tooltips, ALG-4 space ceiling, ALG-5 uniform
    siblings, ALG-6 radius, ALG-7 row occupancy (minimum size only, per the
    rulebook), and ALG-1 (`check_extreme_states`) driven by the invariants
    above so an extreme state is judged by the SAME rules as the default
    one - overlap and item-cut included, not just the template's base A/B/C."""
    problems = (_state_invariants(window)
                + check_contrast(window, image)
                + check_tooltips(window)
                + check_space_ceiling(window)
                + check_uniform_siblings(window)
                + check_radius(window))
    if at_minimum:
        problems += check_row_occupancy(window, image)
    problems += check_extreme_states(window, invariants=_state_invariants)
    return problems


# --- the window registry ----------------------------------------------------
#
# Every factory builds its window in the FULLEST realistic state it will
# ever show — an empty window passes any audit and proves nothing.


def _one_value_noop(_value) -> None:
    """A stub setter with the REAL arity of an ordinary settings setter —
    see `_AuditSetters.__missing__`."""


def _noop(*_args, **_kwargs) -> None:
    return None


class _AuditSetters(dict):
    """The Watch Face `setters` contract without a live controller: every
    unknown key is a no-op callable; the three DATA PROVIDERS the section
    builders actually read are seeded with real values below."""

    def __missing__(self, _key):
        # ONE required value, not `*args` (owner bug 2026-08-16): the
        # per-section Reset only claims a setter whose signature takes
        # exactly one value (`section_reset._takes_one_value`), so a
        # `*args` stub made every page look unresettable and NO audit
        # shot ever contained the Reset row the owner sees. A guard blind
        # to the widget it is supposed to guard is not a guard.
        return _one_value_noop


def _audit_settings():
    from app.settings_store import Settings, SettingsStore

    # ALG-8 LIVE PROFILE (rules/GUI.md -> Zubi v2): during the live-profile
    # pass, active_profile() is a read-only COPY of the owner's real
    # settings.json (layout_checks_qt.live_profile_source, published by
    # live_profile_copy()) - SettingsStore takes an explicit path and does
    # not itself honour an env override, so this is the one place that
    # reads it. Falls through to the pristine default otherwise.
    profile = active_profile()
    if profile is not None:
        return SettingsStore(profile).load()

    # pointer="calendar" is the FULLEST Themes & Slots section: only the
    # Calendar pointer mounts a roster on its wedges, so this state shows
    # every group the section can hold.
    return replace(Settings(), pointer="calendar")


def _audit_setters(settings) -> _AuditSetters:
    from app.controller import build_skin
    from app.slot_descriptor import SlotDescriptor

    skin = build_skin(settings)
    descriptors = (
        SlotDescriptor(
            index=1, title="1st Slot",
            mode_value=settings.weekday_slot,
            style_value=settings.day_slot_style,
            theme_value=settings.weekday_theme,
            roster_value=settings.weekday_roster,
            names_value=settings.show_weekday_names,
            enabled_value=settings.show_weekday,
            set_mode=_noop, set_style_mode=_noop,
            set_weekday=_noop, set_names=_noop,
        ),
        SlotDescriptor(
            index=2, title="2nd Slot",
            mode_value=settings.octa_slot,
            style_value=settings.info_slot_style,
            theme_value=settings.info_slot_theme,
            roster_value=settings.info_slot_roster,
            names_value=settings.show_info_slot_names,
            enabled_value=settings.show_octa_slot,
            set_mode=_noop, set_style_mode=_noop,
            set_weekday=_noop, set_names=_noop,
        ),
        SlotDescriptor(
            index=3, title="3rd Slot",
            mode_value=settings.third_slot,
            style_value=settings.third_slot_style,
            theme_value=settings.third_slot_theme,
            roster_value=settings.third_slot_roster,
            names_value=settings.show_info_slot_names,
            enabled_value=settings.show_third_slot,
            set_mode=_noop, set_style_mode=_noop,
            set_weekday=_noop, set_names=_noop,
        ),
    )
    setters = _AuditSetters()
    setters["slot_descriptors"] = lambda: descriptors
    setters["ring_has_crown_text"] = lambda: bool(skin.ring.crown_text)
    setters["opacity_skin_defaults"] = lambda: {
        "star_alpha": skin.star.day_alpha,
        "aura_day_alpha": skin.background.day_alpha,
        "aura_twilight_alpha": skin.background.twilight_alpha,
        "moon_transit_alpha": skin.year_marker.transit_alpha,
        "ghost_alpha": skin.weekday_set.ghost_opacity,
    }
    return setters


def make_watch_face() -> QWidget:
    from app.watch_face.window import WatchFaceDialog

    settings = _audit_settings()
    return WatchFaceDialog(settings, _audit_setters(settings))


def make_settings_dialog() -> QWidget:
    from app.controller import build_skin
    from app.settings_dialog.dialog import SettingsDialog
    from app.settings_store import Settings

    settings = Settings()
    return SettingsDialog(settings, build_skin(settings))


def make_encyclopedia() -> QWidget:
    """Session zoom pinned to 1.0 — it is a module-level global two
    sibling suites leave at 2.5, and an audit whose subject depends on
    test ORDER measures nothing (the zoom defect itself stays pinned by
    its own test below)."""
    from app.encyclopedia import dialog as dialog_module
    from app.encyclopedia.dialog import EncyclopediaDialog

    dialog_module._session_zoom = 1.0
    return EncyclopediaDialog()


def make_observatory() -> QWidget:
    from datetime import datetime
    from zoneinfo import ZoneInfo

    import astral

    from app.observatory import ObservatoryDialog
    from config import defaults

    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    return ObservatoryDialog(
        datetime.now(tz),
        astral.Observer(latitude=city["latitude"],
                        longitude=city["longitude"]),
        tz,
    )


def make_report() -> QWidget:
    """FULLEST state: the profiling registry seeded with real-shaped rows
    (long dotted names, spread durations) so the table, the bar chart and
    the sparkline all carry content — an empty report measures nothing."""
    from app.report import ReportDialog
    from config import profiling

    profiling.reset()
    for name in ("compositor.paint_full_face",
                 "watch_manager.rebuild_day_context_after_clock_jump",
                 "encyclopedia.warm_hover_articles",
                 "observatory.recompute_year_charts"):
        for _ in range(7):
            with profiling.measure(name):
                math.sqrt(12345.6789)
    dialog = ReportDialog()
    dialog._refresh()
    return dialog


def make_shortcuts() -> QWidget:
    from app.shortcuts_window import ShortcutsDialog

    return ShortcutsDialog()


def make_time_travel() -> QWidget:
    from datetime import datetime, timezone

    from app.time_travel import TimeTravelDialog
    from config import defaults

    city = defaults.DEFAULT_CITY
    return TimeTravelDialog(
        city["latitude"], city["longitude"],
        initial_moment=datetime(2026, 6, 20, 12, 0, tzinfo=timezone.utc),
        coverage=(1900, 2100), core_coverage=(1600, 2400),
        era_notation="bce_ce", show_era_suffix=True,
        deep_pack=True, jump_callback=_noop,
    )


def make_legend_popup() -> QWidget:
    """The hover legend, with a real long article blurb — its width is
    computed from the measured text, and that computation is what gets
    audited here."""
    from app.legend_popup import LegendPopup

    popup = LegendPopup()
    popup.show_html(
        "<b>Tuesday — Mars, the Red Wanderer</b><br>"
        "The third body of the week wears the red of iron oxide and war: "
        "a full-length hover paragraph, long enough to exercise the "
        "measured-width path and the wrap cap both, exactly as the "
        "longest bundled blurb does in the running dial.",
        QPoint(0, 0),
    )
    return popup


def _nav_states(window: QWidget):
    """One state per sidebar section of a list+stack dialog — the stack
    shows ONE page at a time, so a single-state audit would measure only
    whichever page happens to be current."""
    nav = window._nav_list
    return [(nav.item(i).text(), (lambda i=i: nav.setCurrentRow(i)))
            for i in range(nav.count())]


def _encyclopedia_states(window: QWidget):
    return [
        ("Home", window.show_home),
        ("Reader", lambda: window.navigate_to("instrument", 0)),
    ]


# (name, factory, states) — states(window) -> [(label, activate)] or None
WINDOWS = (
    ("WatchFaceDialog", make_watch_face, _nav_states),
    ("SettingsDialog", make_settings_dialog, _nav_states),
    ("EncyclopediaDialog", make_encyclopedia, _encyclopedia_states),
    ("ObservatoryDialog", make_observatory, None),
    ("ReportDialog", make_report, None),
    ("ShortcutsDialog", make_shortcuts, None),
    ("TimeTravelDialog", make_time_travel, None),
    ("LegendPopup", make_legend_popup, None),
)


def _shot_name(label: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in label).strip("_") + ".png"


def _effective_minimum(window: QWidget) -> tuple[int, int]:
    """The declared minimum when there is one, else the layout's own hint
    — the audit still MEASURES an undeclared window (and separately fails
    it for not declaring), so the fix list carries real numbers."""
    minimum = window.minimumSize()
    if minimum.width() > 0 and minimum.height() > 0:
        return minimum.width(), minimum.height()
    hint = window.minimumSizeHint()
    return max(hint.width(), 1), max(hint.height(), 1)


def audit_window(name: str, factory, states, profile: str = "") -> list[str]:
    window: QWidget = factory()
    window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
    window.show()
    QApplication.processEvents()

    tag = f"{name} ({profile})" if profile else name
    problems = [f"[{tag}] {p}" for p in check_declared_minimum(window)]
    width, height = _effective_minimum(window)
    state_list = states(window) if states else [("", None)]
    for label, activate in state_list:
        if activate is not None:
            activate()
        full = f"{tag} - {label}" if label else tag
        for size_label, w, h in (("minimum", width, height),
                                 ("minimum+50%", int(width * 1.5),
                                  int(height * 1.5))):
            _settle(window, w, h)
            image = _window_image(window)
            problems += [f"[{full} @ {size_label} {w}x{h}] {p}"
                         for p in _audit(window, image,
                                         at_minimum=(size_label == "minimum"))]
            if size_label == "minimum":
                # The DESIGN REVIEW shot: the window at the size the
                # grade has to hold at, written by the audit itself so
                # the picture can never be of a different build than the
                # one just measured.
                SHOT_DIR.mkdir(parents=True, exist_ok=True)
                shot = name if not profile else f"{name}-live"
                window.grab().save(
                    str(SHOT_DIR / _shot_name(
                        f"{shot} - {label}" if label else shot)), "PNG")

    if hasattr(window, "done"):
        window.done(0)      # a QDialog: releases held repositories too
    else:
        window.close()
    return problems


# --- THE ZUBI BASELINE RATCHET (owner approval 2026-08-09, in-session) ----
#
# The first Zubi v2 run recorded 1667 findings which the owner ordered
# left unfixed at install time ("ne popravljaj postojeće stanje") — yet
# this test sits in the Stop guard, so every session's end was red on
# frozen debt it was forbidden to touch. The owner's verdict (option 1,
# 2026-08-09): the audit fails ONLY on findings whose normalized key is
# NOT in `tests/zubi_baseline.json`; the baseline is a RATCHET — entries
# may only be REMOVED (as findings are fixed in the owed fix round),
# never added without the owner's explicit in-session approval, exactly
# like THE STRUCTURE LAW's ratchet. Keys are digit-normalized so a
# finding does not fork into a "new" one when content shifts a pixel.
_BASELINE_PATH = Path(__file__).resolve().parent / "zubi_baseline.json"


def _finding_key(problem: str) -> str:
    # Hex colours are sampled from the RENDERED window, so they shift
    # with platform/DPI — normalize them before the digit pass, or a
    # baseline key forks on every environment change. The "(live
    # profile)" tag is dropped too: the owner's settings file changes
    # under his hands, and a finding KIND the default pass already
    # carries must not re-fail as "new" whenever his profile shifts a
    # widget by a pixel — a kind absent from the default baseline still
    # fails the live pass, which is all ALG-8 asks.
    text = problem.replace(" (live profile)", "")
    text = re.sub(r"#[0-9a-fA-F]{3,8}\b", "#HEX", text)
    return re.sub(r"\d+", "#", text)


def _baseline() -> dict:
    if not _BASELINE_PATH.is_file():
        return {}
    data = json.loads(_BASELINE_PATH.read_text(encoding="utf-8"))
    return {name: set(keys) for name, keys in data.items()
            if not name.startswith("_")}


@pytest.mark.parametrize("name,factory,states", WINDOWS,
                         ids=[w[0] for w in WINDOWS])
def test_layout_audit(app, name, factory, states):
    problems = audit_window(name, factory, states)

    # ALG-8 LIVE PROFILE (rules/GUI.md -> Zubi v2): the same walk again, on
    # a read-only copy of watch 1's real settings.json. "That is the
    # environment, not this change" is not a legal sentence in any proof
    # file - a failure under the owner's real profile is this session's.
    source = live_profile_source()
    if source is not None:
        if not Path(source).is_file():
            problems.append(
                f"[{name}] ALG-8 LIVE PROFILE (rules/GUI.md -> Zubi v2): "
                f"live_profile_source() points at {source}, which does not "
                "exist - return None when the owner's profile is absent, or "
                "fix the path; a silently skipped live pass is the hole "
                "this rule closes")
        else:
            with live_profile_copy():
                problems += audit_window(name, factory, states,
                                         profile="live profile")

    # REBASELINE mode (the ratchet's one legal writer): re-records this
    # window's keys IN THE SAME ENVIRONMENT the guard measures in. It
    # refuses to ADD keys unless DOMY_ZUBI_REBASELINE=force — and force
    # is legal only with the owner's explicit in-session approval
    # (first freeze: owner verdict of 2026-08-09, option 1).
    rebase = os.environ.get("DOMY_ZUBI_REBASELINE")
    if rebase:
        keys = sorted({_finding_key(p) for p in problems})
        data = (json.loads(_BASELINE_PATH.read_text(encoding="utf-8"))
                if _BASELINE_PATH.is_file() else {"_comment": (
                    "THE ZUBI BASELINE RATCHET (owner approval "
                    "2026-08-09): the owner-frozen pre-existing findings "
                    "(zubi-v2-findings.md), digit/hex-normalized. "
                    "test_layout_audit fails ONLY on findings not in "
                    "here. Entries may only be REMOVED; adding one "
                    "needs the owner's explicit in-session approval "
                    "(DOMY_ZUBI_REBASELINE=force).")})
        grew = set(keys) - set(data.get(name, []))
        if grew and rebase != "force":
            pytest.fail(
                f"rebaseline would ADD {len(grew)} keys to {name} — the "
                "ratchet only shrinks; owner approval + "
                "DOMY_ZUBI_REBASELINE=force required")
        data[name] = keys
        _BASELINE_PATH.write_text(
            json.dumps(data, indent=1, ensure_ascii=False) + "\n",
            encoding="utf-8")
        return

    known = _baseline().get(name, set())
    fresh = [p for p in problems if _finding_key(p) not in known]
    if known:
        seen = {_finding_key(p) for p in problems}
        stale = known - seen
        if stale:
            print(f"[{name}] baseline ratchet: {len(stale)} baseline "
                  "entries no longer occur — remove them from "
                  "tests/zubi_baseline.json (the ratchet only shrinks)")
    assert not fresh, (
        "THE SPACE & LEGIBILITY LAW (rules/GUI.md) - runtime audit "
        "failed on NEW findings (not in the owner-frozen baseline, "
        "tests/zubi_baseline.json):\n  " + "\n  ".join(fresh)
        + "\nLadder: (1) the starving element takes the free space, "
          "(2) reflow into more rows, (3) raise the window minimum, "
          "(4) scroll only when the window is genuinely full."
          "\nZubi v2 (rules/GUI.md -> Zubi v2): an ALG- finding is measured, "
          "not felt - the message says what to change. Fix the new "
          "finding; NEVER add it to the baseline without the owner's "
          "explicit in-session approval."
    )


def test_section_taxonomy(app):
    """ALG-9 SECTION TAXONOMY (rules/GUI.md -> Zubi v2): fed from
    SettingsDialog's own nav structure - not part of the generic walk (see
    check_section_taxonomy's own docstring), so every project wires it from
    its own nav/stack, exactly as this one does here."""
    window = make_settings_dialog()
    window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
    _settle(window, *_effective_minimum(window))
    sections: dict[str, list[str]] = {}
    for row in range(window._nav_list.count()):
        window._nav_list.setCurrentRow(row)
        QApplication.processEvents()
        title = window._nav_list.item(row).text().strip(" ▸")
        page = window._stack.currentWidget()
        sections[title] = [label.text() for label in page.findChildren(QLabel)
                           if label.text().strip()]
    window.done(0)
    problems = check_section_taxonomy(sections)
    assert not problems, (
        "ALG-9 SECTION TAXONOMY (rules/GUI.md -> Zubi v2) failed:\n  "
        + "\n  ".join(problems)
    )


def test_section_taxonomy_watch_face(app):
    """ALG-9 for the WATCH FACE window too (owner order 2026-08-09:
    "kako su te zubi pustili da numerals size ostane van SIZE
    kategorije" — the taxonomy tooth was wired only to SettingsDialog,
    so a size slider living in the Numerals section passed every gate).
    Same harvest as `test_section_taxonomy`: section title -> the
    labels its page carries."""
    window = make_watch_face()
    window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
    _settle(window, *_effective_minimum(window))
    sections: dict[str, list[str]] = {}
    for row in range(window._nav_list.count()):
        window._nav_list.setCurrentRow(row)
        QApplication.processEvents()
        title = window._nav_list.item(row).text().strip(" ▸")
        page = window._stack.currentWidget()
        sections[title] = [label.text() for label in page.findChildren(QLabel)
                           if label.text().strip()]
    window.done(0)
    problems = check_section_taxonomy(sections)
    assert not problems, (
        "ALG-9 SECTION TAXONOMY (rules/GUI.md -> Zubi v2) failed on the "
        "Watch Face window:\n  " + "\n  ".join(problems)
    )


def test_the_audit_actually_inspects_something(app):
    """A green audit that measured nothing is worse than no audit: pin
    that the walked windows really present text, scroll areas and a
    non-trivial widget count to the checks above."""
    window = make_watch_face()
    window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
    labels = areas = widgets = 0
    for label, activate in _nav_states(window):
        activate()
        _settle(window, *_effective_minimum(window))
        labels += sum(1 for w in window.findChildren(QLabel)
                      if w.isVisible() and w.text().strip())
        areas += sum(1 for w in window.findChildren(QAbstractScrollArea)
                     if w.isVisible())
        widgets += sum(1 for w in window.findChildren(QWidget)
                       if w.isVisible())
    window.done(0)
    assert labels, "no visible text — the elision check would be vacuous"
    assert areas, "no scroll area — the scrollbar check would be vacuous"
    assert widgets > 30, f"only {widgets} widgets laid out"


@pytest.mark.xfail(
    reason="STALE PIN, recorded in .claude/zubi-v2-findings.md (2026-08-08):"
           " its second assertion (roomy == []) now finds 5 elision hits at"
           " the larger size that were never pinned. Part of the owner-frozen"
           " Zubi backlog (baseline ratchet, owner approval 2026-08-09) —"
           " re-pin or flip in the owed fix round.",
    strict=False,
)
def test_the_encyclopedia_cards_outgrow_their_box_when_zoomed(app):
    """A REAL, PRE-EXISTING defect the first audit uncovered, kept
    visible rather than quietly skipped (owner report pending).

    `app/encyclopedia/cards.py` `CardGrid.fit` grows the FONT with the
    session zoom but clamps the CARD to the unzoomed width, so at any
    zoom above 1.0, at the minimum window width, the home cards'
    subtitles are cut — exactly what the law forbids. This test PINS THE
    CURRENT BEHAVIOUR so the finding cannot be lost. When the owner
    picks a remedy (the law's order: free space, reflow to fewer
    columns, raised minimum, scroll), it flips to asserting no faults."""
    from app.encyclopedia import dialog as dialog_module
    from app.encyclopedia.dialog import EncyclopediaDialog

    previous = dialog_module._session_zoom
    try:
        dialog_module._session_zoom = 2.0
        dialog = EncyclopediaDialog()
        dialog.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
        _settle(dialog, *_effective_minimum(dialog))
        cramped = check_elision(dialog)
        _settle(dialog, *_LARGER)
        roomy = check_elision(dialog)
        dialog.close()
    finally:
        dialog_module._session_zoom = previous

    assert cramped, "the zoom defect is gone — flip this test to assert []"
    assert roomy == [], "wider than the minimum it must still hold"


def main() -> int:
    """Report mode: measure EVERY window, print every problem, never stop
    at the first — the fix list of MIGRATE-LAYOUT.md step 4."""
    _make_app()
    failed = False
    for name, factory, states in WINDOWS:
        try:
            problems = audit_window(name, factory, states)
        except Exception as error:      # a factory that cannot build is a finding too
            print(f"{name}: BROKEN FACTORY - {error!r}", file=sys.stderr)
            failed = True
            continue
        if problems:
            failed = True
            print(f"{name}: FAIL ({len(problems)} findings)", file=sys.stderr)
            for p in problems:
                print("  " + p, file=sys.stderr)
        else:
            print(f"{name}: PASS (audited at minimum and +50%)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
