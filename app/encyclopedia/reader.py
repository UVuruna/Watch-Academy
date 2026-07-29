"""The Encyclopedia's ARTICLE screen — level three.

One page at a time: the entry's image row (or grid), its bold name, the
full article, the look/finish switcher and the pager. Everything that
sizes an article — the block-width formula, the em-like font growth,
the image-height ceiling, the lazy decode cache, THE INVISIBLE CLIPPER
fix — moved here VERBATIM from the old `app/encyclopedia.py`: the
Session 27 rework changed how pages are REACHED, never how a page is
drawn, and this layout carries a long tail of ground-truthed owner bug
fixes that must not be re-derived.

What is NEW here is only the variant step: `switch_variant` walks the
theme's registers keeping the reader's position inside the block (the
owner's own law — Monday stays Monday), replacing the retired
Pantheon/Planetary roster button, which knew how to do this for exactly
four themes and nothing else.

Layer: app. Documentation: reader.md.
"""

import html as _html
import shutil
from pathlib import Path

from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.encyclopedia import tree as topic_tree
from app.encyclopedia.text import article_text, entry_name, flow_html, image_tooltip
from app.ui_style import style_button, style_look_chip
from config import constants, defaults, encyclopedia_ui, paths
from render.asset_recolor import ensure_variant, variant_pending
from render import cube_preview3d, diagrams
from render.asset_variants import scaled_variant_file
from render.compositor import _HEX_NOTE, _SUBHEAD


class ReaderScreen(QWidget):
    """The article slider for one topic."""

    page_changed = Signal()
    zoomed = Signal(float)

    def __init__(self, topics: dict, symbolism, encyclopedia, tr):
        super().__init__()
        self._topics = topics
        self._symbolism = symbolism
        self._encyclopedia = encyclopedia
        self._tr = tr
        self._topic_key: str | None = None
        self._entry_index = 0
        self._zoom = 1.0
        self._cells: list[dict] = []
        self._blocks: list[QWidget] = []
        self._text_labels: list[QLabel] = []
        self._name_labels: list[QLabel] = []
        # THE COMPUTED PAGES (owner verdict 2026-07-29): a page may name
        # a DRAWER instead of a file — (label, (kind, key)) pairs, re-fit
        # on every resize from one cached master (Rule #19: one master,
        # transformed, never a plate per size).
        self._diagram_labels: list = []
        # THE 3D SWAP (Session 28): the Cube family's eligible kinds get a
        # live `render.cube_preview3d` panel instead, built ONCE per
        # `_show_entry()` (never per resize) and only ever resized here —
        # `_preview3d_widgets` stays empty whenever the gadget is absent,
        # so this is a pure addition, never a replacement of the fallback
        # path above.
        self._preview3d_widgets: list = []
        self._pixmap_cache: dict[str, QPixmap] = {}
        # FINISH PERSISTENCE (owner INSTRUCTION #3): once picked, a
        # look/finish (e.g. Bronze) rides EVERY following entry that
        # offers it — never resets to the topic's own default on a page
        # turn or a topic change. `None` = no preference set yet.
        self._preferred_look_label: str | None = None
        self._look_state: dict | None = None

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        # THE NO-X-SCROLL LAW (owner, Session 27: "X scroll nikada ne
        # sme"): the article block is already clamped to the viewport by
        # `_block_width`, and the bar itself is switched OFF so no future
        # widget can smuggle one in.
        self._scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._scroll.viewport().installEventFilter(self)

        self._look_back = QToolButton()
        self._look_back.setText("◀")
        style_button(self._look_back, "neutral", small=True)
        self._look_back.clicked.connect(lambda: self._cycle_look(-1))
        self._look_caption = QLabel()
        self._look_caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._look_caption.setMinimumWidth(120)
        self._look_forward = QToolButton()
        self._look_forward.setText("▶")
        style_button(self._look_forward, "neutral", small=True)
        self._look_forward.clicked.connect(lambda: self._cycle_look(1))
        self._counter = QLabel()
        self._counter.setStyleSheet(
            f"font-size: {encyclopedia_ui.UI_BUTTON_FONT_PX}px; font-weight: bold;"
        )
        self._previous = QPushButton(self._tr("← Previous"))
        self._previous.clicked.connect(lambda: self.step(-1))
        style_button(self._previous, "previous")
        self._next = QPushButton(self._tr("Next →"))
        self._next.clicked.connect(lambda: self.step(+1))
        style_button(self._next, "next")

        # The LOOK switcher alone now — ⬇ Download moved up into the
        # dialog's one header row (owner 2026-07-29), so this row is a
        # plain centred trio.
        looks = QHBoxLayout()
        looks.addStretch(1)
        looks.addWidget(self._look_back)
        looks.addWidget(self._look_caption)
        looks.addWidget(self._look_forward)
        looks.addStretch(1)
        pager = QHBoxLayout()
        pager.addStretch(1)
        pager.addWidget(self._previous)
        pager.addWidget(self._counter)
        pager.addWidget(self._next)
        pager.addStretch(1)
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.addLayout(looks)
        column.addWidget(self._scroll, stretch=1)
        column.addLayout(pager)

    # --- state -------------------------------------------------------------

    @property
    def topic_key(self) -> str | None:
        return self._topic_key

    @property
    def entry_index(self) -> int:
        return self._entry_index

    @property
    def topic(self) -> dict:
        return self._topics[self._topic_key]

    @property
    def look_state(self) -> dict | None:
        """The OPEN page's look/finish state — None when the page has
        only one look and the switcher is hidden."""
        return self._look_state

    def open_topic(self, key: str, index: int = 0) -> None:
        """Open `key` at `index`, clamped to the topic's own length."""
        self._topic_key = key
        entries = self._topics[key]["entries"]
        self._entry_index = max(0, min(index, len(entries) - 1))
        self._show_entry()

    def step(self, delta: int) -> None:
        """← Previous / Next → — wraps around like the Guide pages."""
        entries = self._topics[self._topic_key]["entries"]
        self._entry_index = (self._entry_index + delta) % len(entries)
        self._show_entry()

    def switch_variant(self, delta: int) -> None:
        """◀ / ▶ beside the title: the next register of the SAME theme,
        the reader's position inside the block kept (Monday stays
        Monday) and clamped when the next register is shorter — the law
        itself lives in `tree.switch_variant`, pure and tested without
        a widget in sight."""
        self._entry_index = topic_tree.switch_variant(
            self.topic, self._entry_index, delta
        )
        self._show_entry()

    def set_zoom(self, zoom: float) -> None:
        self._zoom = zoom
        self._rescale()

    # --- the page ----------------------------------------------------------

    def _entry_name(self, entry: dict) -> str:
        return entry_name(entry, self._symbolism, self._encyclopedia, self._tr)

    def _article_text(self, ref: tuple) -> str:
        return article_text(ref, self._symbolism, self._encyclopedia, self._tr)

    def _show_entry(self) -> None:
        """The current entry's PAGE: the images row (the Astrology pair
        sits side by side), the bold name and the text, all inside ONE
        block (owner: center the whole object, never the text lines)."""
        topic = self._topics[self._topic_key]
        entries = topic["entries"]
        entry = entries[self._entry_index]
        self._counter.setText(f"{self._entry_index + 1} / {len(entries)}")
        pager = len(entries) > 1
        self._previous.setVisible(pager)
        self._counter.setVisible(pager)
        self._next.setVisible(pager)
        self._cells = []
        self._blocks = []
        self._text_labels = []
        self._name_labels = []
        self._diagram_labels = []
        self._preview3d_widgets = []
        content = QWidget()
        column = QVBoxLayout(content)
        column.setSpacing(defaults.GUIDE_SPACING_PX * 3)
        block = QWidget()
        cell = QVBoxLayout(block)
        cell.setContentsMargins(0, 0, 0, 0)
        cell.setSpacing(defaults.GUIDE_SPACING_PX)
        # LOOKS (owner 2026-07-13): every look is a tuple of ROWS — the
        # Sunday pairs stand side by side; the arrows page through
        # kinship groups or metal finishes. Only PATHS are kept here —
        # the pixmaps decode lazily in _render_cell (owner 2026-07-13:
        # The Week opened far too slowly when every look of every entry
        # loaded upfront).
        looks = entry.get("looks") or (
            ("", (tuple(entry.get("images", ())),)),
        )
        # Resolve through the active ART SOURCE here (owner 2026-07-14:
        # Gemini vs ChatGPT with per-file fallback). A `variant_pending`
        # path counts as PRESENT (owner order 2026-07-26): its source is
        # on disk and `_pixmap` builds the pixels on first display.
        look_rows = [
            [
                [
                    resolved
                    for resolved in (
                        paths.art_file(path) for path in row
                        if path is not None
                    )
                    if resolved.exists() or variant_pending(resolved)
                ]
                for row in rows
            ]
            for _, rows in looks
        ]
        titles = [label for label, _ in looks]
        keep = [index for index, rows in enumerate(look_rows) if any(rows)]
        look_rows = [look_rows[index] for index in keep]
        titles = [titles[index] for index in keep]
        start_index = 0
        if self._preferred_look_label in titles:
            start_index = titles.index(self._preferred_look_label)
        state = {
            "container": None,
            "looks": look_rows,
            "titles": titles,
            "index": start_index,
        }
        if look_rows:
            container = QWidget()
            state["container"] = container
            cell.addWidget(container, alignment=Qt.AlignmentFlag.AlignHCenter)
            self._cells.append(state)
        self._look_state = state if len(look_rows) > 1 else None
        multi_look = self._look_state is not None
        self._look_back.setVisible(multi_look)
        self._look_caption.setVisible(multi_look)
        self._look_forward.setVisible(multi_look)
        if multi_look:
            self._update_look_caption()
        diagram = entry.get("diagram")
        if diagram:
            kind, key = diagram
            # THE FALLBACK LAW: `build_widget` answers None for every
            # reason the gadget might be unusable, and that is exactly
            # when this page keeps its computed 2D plate below — the
            # widget is built lazily, HERE, only because this entry is
            # actually being shown (never at dialog-open).
            panel = cube_preview3d.build_widget(kind, key)
            if panel is not None:
                self._preview3d_widgets.append(panel)
                cell.addWidget(panel, alignment=Qt.AlignmentFlag.AlignHCenter)
            else:
                plate = QLabel()
                plate.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self._diagram_labels.append((plate, diagram))
                cell.addWidget(plate, alignment=Qt.AlignmentFlag.AlignHCenter)
        name = QLabel(f"<b>{self._entry_name(entry)}</b>")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._name_labels.append(name)
        cell.addWidget(name)
        if entry.get("poem"):
            # The Four Greetings page: CENTERED italic stanzas with
            # their line breaks kept, the reading justified below.
            data = entry["article"][1]
            gap = encyclopedia_ui.GREETINGS_STANZA_GAP_PX
            stanzas = "".join(
                f"<p align='center' style='margin-top:{gap}px;"
                f"margin-bottom:{gap}px'><i>"
                + "<br/>".join(
                    _html.escape(line) for line in stanza.split("\n")
                )
                + "</i></p>"
                for stanza in data["verses"].split("\n\n")
            )
            text = QLabel(stanzas + flow_html(
                data["explanation"] + "\n\n" + data["commentary"]
            ))
        else:
            text = QLabel(
                flow_html(self._article_text(entry["article"]), tr=self._tr)
            )
        text.setWordWrap(True)
        text.setTextFormat(Qt.TextFormat.RichText)
        text.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._text_labels.append(text)
        cell.addWidget(text)
        self._blocks.append(block)
        # The block sits CENTERED with even side margins (owner
        # 2026-07-14: "ravnomerno po sredini").
        column.addWidget(block, alignment=Qt.AlignmentFlag.AlignHCenter)
        column.addStretch(1)
        # THE INVISIBLE CLIPPER (owner bug, "Nevidljivi element seče
        # pasus The Lesson" — root cause found fix round R3): fit the
        # block's width/font/pixmaps BEFORE `setWidget` ever hands this
        # widget to the scroll area. QScrollArea's widgetResizable path
        # sizes a FRESH widget to the viewport on its first pass and only
        # grows it to the true heightForWidth sizeHint on a SECOND pass —
        # but Next/Previous never yield to the event loop, so the single
        # frame the user sees is the too-short guess: the tail of the
        # article is clipped AND the scrollbar range comes back 0.
        self._rescale()
        self._scroll.setWidget(content)
        self._scroll.verticalScrollBar().setValue(0)
        self.page_changed.emit()

    # --- geometry ----------------------------------------------------------

    def _block_width(self) -> int:
        """The article block's width — ONE formula (Rule #5: `_rescale`
        and `_cycle_look` both need it, and used to drift when each
        computed it separately): the configured fraction of the
        viewport, `self._zoom` scaling it further but NEVER past the
        viewport itself (no horizontal scrollbar, ever)."""
        viewport = max(320, self._scroll.viewport().width())
        return min(
            viewport,
            round(
                viewport * encyclopedia_ui.ENCYCLOPEDIA_TEXT_WIDTH_FRACTION
                * self._zoom
            ),
        )

    def _rescale(self) -> None:
        """Everything follows the window: each entry BLOCK spans the
        configured width fraction, the images share the block, and the
        font grows with the width at the gentle em-like coefficient.
        `self._zoom` (Ctrl+wheel) then scales the RESULT on top."""
        viewport = max(320, self._scroll.viewport().width())
        block_width = self._block_width()
        for block in self._blocks:
            block.setFixedWidth(block_width)
        font_px = min(
            encyclopedia_ui.ENCYCLOPEDIA_MAX_FONT_PX,
            max(
                encyclopedia_ui.ENCYCLOPEDIA_BASE_FONT_PX,
                round(
                    encyclopedia_ui.ENCYCLOPEDIA_BASE_FONT_PX
                    + (viewport - encyclopedia_ui.ENCYCLOPEDIA_FONT_BASE_WIDTH)
                    * encyclopedia_ui.ENCYCLOPEDIA_FONT_GROWTH
                ),
            ),
        )
        font_px = max(1, round(font_px * self._zoom))
        for label in self._text_labels:
            # A real QFont (owner bug fix round R3, THE INVISIBLE
            # CLIPPER): `setStyleSheet` routes a font-size change through
            # Qt's CSS engine, which only takes effect on the widget's
            # NEXT style polish — a rich-text QLabel's `heightForWidth`
            # queried before that polish still measures the OLD font, so
            # the label is allocated a shorter box than the new font
            # needs and the tail of the article is silently clipped.
            font = label.font()
            font.setPixelSize(font_px)
            label.setFont(font)
            # RESERVE the article's full height: now that the font is
            # final, `heightForWidth` measures true.
            label.setFixedHeight(label.heightForWidth(block_width))
        for label in self._name_labels:
            font = label.font()
            font.setPixelSize(font_px + 3)
            label.setFont(font)
        diagram_side = self._diagram_side(block_width)
        for label, (kind, key) in self._diagram_labels:
            # ONE master per figure, scaled to the page — the same
            # ceiling the art images obey, so a diagram can never push
            # the article off screen.
            master = diagrams.plate(
                kind, key, encyclopedia_ui.CUBE_DIAGRAM_SIDE_PX,
            )
            if master.isNull():
                continue
            label.setPixmap(master.scaled(
                diagram_side, diagram_side,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ))
            label.setFixedSize(diagram_side, diagram_side)
        for panel in self._preview3d_widgets:
            # Re-fit on every resize, same ceiling as the 2D plates
            # above — the SAME square a page would show either way.
            panel.set_square_size(diagram_side)
        for state in self._cells:
            # First pass builds the grid; resizes only re-fit pixmaps.
            if "cells" in state:
                self._resize_cell(state, block_width)
            else:
                self._render_cell(state, block_width)

    def _diagram_side(self, block_width: int) -> int:
        """The square a computed diagram (2D plate or 3D panel alike)
        fits inside — the same height ceiling the art images obey, so
        neither can ever push the article off screen."""
        return max(120, min(
            block_width,
            round(
                self._scroll.viewport().height()
                * encyclopedia_ui.READER_IMAGE_MAX_HEIGHT_FRACTION * self._zoom
            ),
        ))

    def _pixmap(self, path) -> QPixmap:
        """The decoded-image cache behind the lazy looks (owner
        2026-07-13: The Week opened far too slowly). Three laws (owner
        order 2026-07-26, "entering the Encyclopedia must never block or
        crash"): a still-missing metal variant MATERIALIZES now
        (`ensure_variant`); the pre-warmed downscale is read when it
        exists (`build=False` — never a cold downscale on the GUI
        thread); and whatever is decoded is BOUNDED to the reader's
        decode ceiling."""
        key = str(path)
        pixmap = self._pixmap_cache.get(key)
        if pixmap is None:
            ceiling = encyclopedia_ui.ENCYCLOPEDIA_READER_DECODE_CEILING_PX
            source = ensure_variant(path)
            ready = scaled_variant_file(source, ceiling, build=False)
            image = QImage(str(ready))
            if image.width() > ceiling:
                image = image.scaledToWidth(
                    ceiling, Qt.TransformationMode.SmoothTransformation
                )
            pixmap = QPixmap.fromImage(image)
            self._pixmap_cache[key] = pixmap
        return pixmap

    def _render_cell(self, state: dict, block_width: int) -> None:
        """Build the cell's image GRID for its current look — ONCE per
        look. Window resizes only RE-SCALE the pixmaps in place
        (`_resize_cell`): tearing the grid down on every resize left
        half-deleted labels painting as ghosts and stale container
        heights CLIPPING the art (owner bug 2026-07-14)."""
        container = state["container"]
        if container is None:
            return
        old = container.layout()
        if old is not None:
            while old.count():
                item = old.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                    widget.deleteLater()
            QWidget().setLayout(old)     # detach so a fresh grid can bind
        grid = QGridLayout(container)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(defaults.GUIDE_SPACING_PX)
        rows = state["looks"][state["index"]]
        columns = max((len(row) for row in rows), default=0)
        state["cells"] = []
        state["rows"] = sum(1 for row in rows if row)
        if not columns:
            return
        for row_index, row in enumerate(rows):
            offset = (columns - len(row)) // 2    # center shorter rows
            for col_index, path in enumerate(row):
                art = self._pixmap(path)
                label = QLabel()
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                # IMAGE HOVER (owner spec: critical on multi-image pages
                # like the era calendars — "Byzantine").
                label.setToolTip(image_tooltip(path))
                state["cells"].append((label, art, columns))
                grid.addWidget(
                    label, row_index, offset + col_index,
                    alignment=Qt.AlignmentFlag.AlignCenter,
                )
        self._resize_cell(state, block_width)

    def _resize_cell(self, state: dict, block_width: int) -> None:
        """Fit the look's images to the block width — the columns split
        it and every image shrinks as far as needed — AND to the height
        ceiling (owner imperative 2026-07-14: the WHOLE image grid never
        eats more than READER_IMAGE_MAX_HEIGHT_FRACTION of the page, so
        the text stays on screen). `self._zoom` scales the ceiling
        itself; WIDTH stays bounded by `block_width` alone, so zooming in
        only ever grows the page taller, never wider."""
        rows = max(1, state.get("rows", 1))
        ceiling = round(
            self._scroll.viewport().height()
            * encyclopedia_ui.READER_IMAGE_MAX_HEIGHT_FRACTION
            * self._zoom
        )
        max_height = max(
            24, (ceiling - defaults.GUIDE_SPACING_PX * (rows - 1)) // rows,
        )
        for label, art, columns in state.get("cells", ()):
            if art.isNull():
                continue
            share = block_width // columns - defaults.GUIDE_SPACING_PX * 2
            width = max(24, min(share, art.width()))
            pixmap = art.scaledToWidth(
                width, Qt.TransformationMode.SmoothTransformation
            )
            if pixmap.height() > max_height:
                pixmap = art.scaledToHeight(
                    max_height, Qt.TransformationMode.SmoothTransformation,
                )
            label.setPixmap(pixmap)
            # RESERVE the image's full rectangle (owner REPEAT complaint
            # 2026-07-16: the title above and the nav row below cut into
            # the art): fixing the label to the pixmap makes the whole
            # grid's minimum size equal the scaled image.
            label.setFixedSize(pixmap.size())

    # --- the look switcher --------------------------------------------------

    def _cycle_look(self, step: int) -> None:
        """The ◀ / ▶ LOOK switcher — the next look of this entry, a
        metal finish or a kinship group. Every pick becomes the
        session's PREFERRED finish (owner INSTRUCTION #3: it rides every
        following entry that offers the same look, never a silent
        reset). Distinct from the VARIANT switcher beside the title,
        which changes WHICH REGISTER of the theme is being read."""
        state = self._look_state
        if state is None:
            return
        state["index"] = (state["index"] + step) % len(state["looks"])
        self._preferred_look_label = state["titles"][state["index"]]
        self._update_look_caption()
        self._render_cell(state, self._block_width())

    def _update_look_caption(self) -> None:
        """Restyle the caption to the OPEN entry's CURRENT look — a
        FILLED pill in the finish/globe-look's own color (owner round
        R8b item 4), or the neutral chip for a kinship-group switcher."""
        state = self._look_state
        if state is None:
            return
        label = state["titles"][state["index"]]
        self._look_caption.setText(self._tr(label))
        style_look_chip(self._look_caption, label)

    # --- download -----------------------------------------------------------

    def download_entry(self) -> None:
        """⬇ Download (owner 2026-07-14): save the OPEN entry — the
        current look's image(s) and the article text (headings kept as
        [Label] lines) — into a folder the user picks. PUBLIC because
        the button itself sits in the dialog's header row; the deed
        stays here, where the open page lives."""
        entry = self._topics[self._topic_key]["entries"][self._entry_index]
        target = QFileDialog.getExistingDirectory(self, self._tr("Download"))
        if not target:
            return
        name = self._entry_name(entry)
        safe = "".join(
            ch if ch.isalnum() or ch in " ·-_()" else "_" for ch in name
        ).strip()
        lines = [name, ""]
        text = _HEX_NOTE.sub("", self._article_text(entry["article"]))
        for paragraph in text.split("\n\n"):
            match = _SUBHEAD.match(paragraph)
            if match:
                lines.append(f"[{self._tr(match.group(1))}]")
                paragraph = paragraph[match.end():]
            lines += [paragraph, ""]
        (Path(target) / f"{safe}.txt").write_text(
            "\n".join(lines), encoding="utf-8"
        )
        state = self._cells[0] if self._cells else None
        if state is not None:
            rows = state["looks"][state["index"]]
            images = [path for row in rows for path in row]
            for index, path in enumerate(images, start=1):
                suffix = f"_{index}" if len(images) > 1 else ""
                # A pending metal variant materializes before the copy
                # (lazy looks, owner order 2026-07-26).
                shutil.copyfile(
                    ensure_variant(path), Path(target) / f"{safe}{suffix}.png"
                )

    # --- events -------------------------------------------------------------

    def resizeEvent(self, event) -> None:      # noqa: N802 — Qt override
        super().resizeEvent(event)
        self._rescale()

    def eventFilter(self, obj, event) -> bool:  # noqa: N802 — Qt override
        """Ctrl+wheel over the article viewport zooms the whole
        Encyclopedia; a plain wheel is NEVER touched — it falls through
        and scrolls exactly as before."""
        if (
            obj is self._scroll.viewport()
            and event.type() == QEvent.Type.Wheel
            and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            low, high = constants.ENCYCLOPEDIA_ZOOM_RANGE
            steps = event.angleDelta().y() / 120.0
            self._zoom = max(low, min(
                high, self._zoom + steps * constants.ENCYCLOPEDIA_ZOOM_STEP
            ))
            self.zoomed.emit(self._zoom)
            self._rescale()
            return True
        return super().eventFilter(obj, event)
