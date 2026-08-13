"""THE FIGURE TAKES THE FREE SPACE — the Encyclopedia reader's own
half of THE SPACE & LEGIBILITY LAW.

The defect this pins (graded 6/10 at 1280x720, 2026-08-13): every
computed figure was boxed into a SQUARE whose side was 35% of the
viewport HEIGHT, so the wide row figures — the ring presets, the
pointers, the two world modes — arrived on screen 208 px wide inside a
1123 px text column. 915 px of that column stood empty while the
figure's own caption line was too small to read: rung 1 of the ladder
("the starving element takes the free space") skipped outright.

Two things are asserted here, and they pull against each other on
purpose, which is what makes them a tooth rather than a wish:

1. a ROW figure USES the width it is given, and
2. NO figure — row or square — exceeds the height ceiling, so the
   article it explains is still readable underneath it without
   scrolling.

Layer: tests.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.encyclopedia.dialog import EncyclopediaDialog
from config import encyclopedia_ui
from render.instrument_diagrams import INSTRUMENT_FIGURES

# The three ROW figures (`encyclopedia_ui.INSTRUMENT_DIAGRAM_GRIDS`) —
# one wide row of tiles each, and the three pages the owner rejected.
ROW_FIGURES = tuple(encyclopedia_ui.INSTRUMENT_DIAGRAM_GRIDS)

# WHY 0.75, and not a rounder number. At the 1280x720 floor the reader's
# viewport is 1248x595 and the article's text block is
# ENCYCLOPEDIA_TEXT_WIDTH_FRACTION of it — 1123 px. A row figure is
# bound by whichever of the two limits bites first: the WIDEST of them
# (pointers, aspect 5.9) is width-bound and reaches the full 1123, the
# narrowest (world_modes, aspect 4.0) is height-bound and reaches 1072,
# i.e. 95%. 0.75 therefore passes every shipped aspect down to about
# 3.15 with room to spare, while the defect that started this —
# 208/1123 = 18.5% — fails it by a factor of four. A tighter number
# would break on the next honest reshape; a looser one would have let
# the defect through.
MIN_WIDTH_SHARE = 0.75


@pytest.fixture
def app():
    return QApplication.instance() or QApplication([])


def _drawn(dialog, index):
    """The figure's pixmap on Instrument page `index`, plus the viewport
    it was fitted into."""
    dialog.navigate_to("instrument", index)
    QApplication.processEvents()
    reader = dialog.reader
    labels = reader._diagram_labels
    assert labels, f"Instrument page {index} draws no figure at all"
    (label, (_kind, key)), = labels
    return key, label.pixmap(), reader._scroll.viewport()


@pytest.fixture
def reader_at_the_floor(app):
    """The reader open at the owner's own opening screen — 1280x720, the
    minimum every window in this project must fit."""
    dialog = EncyclopediaDialog()
    # THE SILENT AUDITS LAW: never on the owner's screen.
    dialog.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
    dialog.resize(encyclopedia_ui.ENCYCLOPEDIA_MIN_WIDTH_PX,
                  encyclopedia_ui.ENCYCLOPEDIA_MIN_HEIGHT_PX)
    dialog.show()
    app.processEvents()
    yield dialog
    dialog.deleteLater()


def test_a_row_figure_uses_the_width_it_is_given(reader_at_the_floor):
    """Rung 1 of the ladder, measured: a wide figure fills the article's
    own column instead of floating in the middle of it."""
    dialog = reader_at_the_floor
    block = round(dialog.reader._scroll.viewport().width()
                  * encyclopedia_ui.ENCYCLOPEDIA_TEXT_WIDTH_FRACTION)
    seen = []
    for index, figure in enumerate(INSTRUMENT_FIGURES):
        if figure not in ROW_FIGURES:
            continue
        key, pixmap, _viewport = _drawn(
            dialog, _page_index(dialog, figure))
        seen.append(key)
        assert pixmap.width() >= block * MIN_WIDTH_SHARE, (
            f"{key} drawn {pixmap.width()}px wide in a {block}px column "
            f"— the figure is starving beside empty space"
        )
    assert sorted(seen) == sorted(ROW_FIGURES)


def test_no_figure_ever_exceeds_the_height_ceiling(reader_at_the_floor):
    """The other side of the same coin: taking the width must never
    become taking the PAGE. Every figure the Instrument draws — the
    three wide rows and the nine squares alike — stays inside the
    ceiling, so the article's title and its first paragraph are on
    screen without a scroll."""
    dialog = reader_at_the_floor
    entries = dialog.reader._topics["instrument"]["entries"]
    pages = [index for index, entry in enumerate(entries)
             if entry.get("diagram")]
    assert len(pages) == len(INSTRUMENT_FIGURES) - 1   # oscillations
    #                                        lives in the Observatory
    for index in pages:
        key, pixmap, viewport = _drawn(dialog, index)
        ceiling = round(
            viewport.height()
            * encyclopedia_ui.READER_DIAGRAM_MAX_HEIGHT_FRACTION
        )
        assert pixmap.height() <= ceiling + 1, (
            f"{key} is {pixmap.height()}px tall against a {ceiling}px "
            f"ceiling — it is pushing its own article off the screen"
        )


def test_the_height_ceiling_still_leaves_the_article_room(app):
    """The ceiling is a NUMBER, and a number can be raised until the
    page is nothing but picture. Half the viewport is the line: above
    it, a square figure plus the title plus a subheading leaves no
    paragraph."""
    assert encyclopedia_ui.READER_DIAGRAM_MAX_HEIGHT_FRACTION <= 0.5


def _page_index(dialog, figure: str) -> int:
    """The Instrument page that draws `figure` — read from the built
    tree, never a hand-kept second list (the topic also carries pages
    that hold real art, so the two orders are not the same)."""
    entries = dialog.reader._topics["instrument"]["entries"]
    for index, entry in enumerate(entries):
        if entry.get("diagram") == ("instrument", figure):
            return index
    raise AssertionError(f"no Instrument page draws {figure}")
