"""Shared layout VOCABULARY for the Watch Face sections (see
widgets.md) — the width-aware flow (`FlowLayout`/`FlowContent`), the
row shapes built on it (`flow_row`), the pill, the label escape and the
slider row. A fixed column count can never satisfy both ALG-7 (fill the
row) and the window minimum (no horizontal scroll); the owner's own
review caught the 3-3-1 wrap the fixed grids produced, and one
vocabulary means no gallery can fork its own wrap again.

THE GALLERY GRAMMAR MOVED OUT (2026-08-14): `tile` and `flow_gallery`
are gone, replaced by `app.watch_face.controls`'s OptionCard/CardGroup
and its `picture_group` door — which owns the reserved selection
border, the uniform width, the mandatory hover blurb and the icon
growth this module's tile builder used to carry alone. Two tile
builders would mean a section could fork back to the blurb-less one, so
there is exactly one.
"""

from PySide6.QtCore import QEvent, QPoint, QRect, QSize, Qt
from PySide6.QtWidgets import QLayout, QPushButton, QSizePolicy, QWidget

from app.ui_style import style_button, uniform_width
from config import defaults

# The ONE gallery icon size (owner instruction 2026-08-08: every picker
# shows WHAT IT PICKS at a readable size, the Hands gallery being the
# model). It lives in the tile builder itself so no gallery can forget
# it — the defect behind the owner's six screenshots was nine call
# sites each relying on Qt's ~16px default while only Hands set its
# own. Still under `thumbs.THUMB_SOURCE_PX` (256), so every disk-cached
# source stays sharp at this display size.
TILE_ICON_PX = 128


class FlowLayout(QLayout):
    """CENTERED, width-aware tile flow. Tiles keep their own size; the
    wrap point follows the REAL width, so a narrow window wraps sooner
    instead of growing a horizontal scrollbar and a wide one fills the
    row instead of stacking rows (ALG-7; port of Qt's canonical
    FlowLayout example, trimmed). Rows were LEFT-packed from the
    2026-08-06 reading-edge decree until 2026-08-14, when the owner
    sealed CENTER alignment together with the no-pinned-width law: with
    the content column now following the real viewport width, a
    left-packed two-tile gallery left the whole right half of a wide
    window empty (independent grader's 7/10, this session) — each row
    now centers its leftover space instead."""

    #: The widest a justified row may push its members apart.
    MAX_JUSTIFY_GAP_PX = 64

    def __init__(self, spacing: int | None = None):
        super().__init__()
        self._items = []
        self._gap = defaults.GUIDE_SPACING_PX if spacing is None else spacing

    def addItem(self, item) -> None:              # noqa: N802 — Qt API
        self._items.append(item)

    def count(self) -> int:
        return len(self._items)

    def itemAt(self, index):                      # noqa: N802 — Qt API
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index):                      # noqa: N802 — Qt API
        return self._items.pop(index) if 0 <= index < len(self._items) else None

    def expandingDirections(self):                # noqa: N802 — Qt API
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:          # noqa: N802 — Qt API
        return True

    def heightForWidth(self, width: int) -> int:  # noqa: N802 — Qt API
        return self._arrange(QRect(0, 0, width, 0), apply_geometry=False)

    def setGeometry(self, rect: QRect) -> None:   # noqa: N802 — Qt API
        super().setGeometry(rect)
        self._arrange(rect, apply_geometry=True)

    def sizeHint(self) -> QSize:                  # noqa: N802 — Qt API
        return self.minimumSize()

    def minimumSize(self) -> QSize:               # noqa: N802 — Qt API
        # Stays SHRINKABLE below one full row — one tile is the floor,
        # or the window minimum inflates past the screen floor.
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        return size

    def _columns(self, rect: QRect) -> int | None:
        """How many EQUAL items per row, or None when the items differ
        in width (then the greedy wrap below is the only sane answer).

        THE LONELY TAIL (audit 2026-08-14): greedy wrapping put nine
        equal cards at 4-4-1, and that last band's right half stood
        wholly empty while the page continued below it (ALG-7). The
        owner's own rule is FILL THE ROW — his "3-3-2 kad ima prostora
        za 4-3" — so a tail of at least half a row keeps the greedy
        answer untouched; only a tail thinner than that is rebalanced
        (9 -> 3-3-3), which fills every band instead of one and a
        remainder."""
        items = self._items
        if len(items) < 3:
            return None
        widths = {item.sizeHint().expandedTo(item.minimumSize()).width()
                  for item in items}
        if len(widths) != 1:
            return None
        width = widths.pop()
        capacity = max(1, (rect.width() + self._gap) // (width + self._gap))
        if capacity >= len(items):
            return None
        tail = len(items) % capacity
        if tail == 0 or tail * 2 >= capacity:
            return None
        rows = -(-len(items) // capacity)
        return -(-len(items) // rows)

    def _arrange(self, rect: QRect, apply_geometry: bool) -> int:
        # Two passes per row: measure the row first, then place it with
        # the leftover space split evenly left and right (CENTER).
        y, row_height = rect.y(), 0
        row: list = []
        row_width = 0

        def item_size(item) -> QSize:
            # The hint EXPANDED to the item's own minimum: ALG-5 states
            # a row's uniform width through `setMinimumWidth`, and a
            # placement that only read `sizeHint()` silently ignored it
            # — three medal buttons stayed 90/95/92px wide with the
            # uniform minimum already set on them (audit, 2026-08-14).
            return item.sizeHint().expandedTo(item.minimumSize())

        def place() -> None:
            # JUSTIFY, THEN CENTER. A row of equal cards that leaves the
            # window's right half bare fails ALG-7 even when it is
            # perfectly centered, so the leftover is first spent WIDENING
            # THE GAPS (up to `MAX_JUSTIFY_GAP_PX`, past which a row of
            # three would read as three unrelated things); whatever is
            # left over after that is split evenly at the ends, which is
            # the CENTER alignment the owner sealed on 2026-08-14.
            if not apply_geometry or not row:
                return
            gap = self._gap
            leftover = rect.width() - row_width
            if len(row) > 1 and leftover > 0:
                gap = min(
                    self.MAX_JUSTIFY_GAP_PX,
                    self._gap + leftover // (len(row) - 1),
                )
            spread = row_width + (gap - self._gap) * (len(row) - 1)
            x = rect.x() + max(0, (rect.width() - spread) // 2)
            for item in row:
                size = item_size(item)
                item.setGeometry(QRect(QPoint(x, y), size))
                x += size.width() + gap

        columns = self._columns(rect)
        for item in self._items:
            hint = item_size(item)
            width_if_added = row_width + (self._gap if row else 0) + hint.width()
            if row and (rect.x() + width_if_added > rect.right() + 1
                        or (columns is not None and len(row) >= columns)):
                place()
                y += row_height + self._gap
                row, row_width, row_height = [], 0, 0
            row.append(item)
            row_width = width_if_added if row_width else hint.width()
            row_height = max(row_height, hint.height())
        place()
        return y + row_height - rect.y()


class FlowContent(QWidget):
    """A flow-hosting content widget whose height follows its WIDTH —
    and which SAYS so: size-policy heightForWidth flag, plus an honest
    self-published minimum height on every resize, because QScrollArea's
    widgetResizable path sizes pages from plain minimum hints and never
    consults heightForWidth (measured on the owner's live profile,
    where the widgets under a gallery compressed to 10px without it).

    A RESIZE IS NOT THE ONLY WAY CONTENT GROWS (measured 2026-08-13 on
    the owner's live profile): republishing only from `resizeEvent` left
    the minimum STALE whenever the content changed at an unchanged width
    — switching stack pages in the Watch Face window did exactly that,
    and the page holder kept a 971px minimum against a real 984px need,
    so the Ring page's "Inner (minute track)" group was handed 375px
    against its own 388px minimum and lost its bottom margin. Qt already
    announces that moment: a `LayoutRequest` is delivered whenever a
    child layout changes, so the minimum is republished from there too."""

    def __init__(self):
        super().__init__()
        policy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        policy.setHeightForWidth(True)
        self.setSizePolicy(policy)

    def hasHeightForWidth(self) -> bool:          # noqa: N802 — Qt API
        return True

    def heightForWidth(self, width: int) -> int:  # noqa: N802 — Qt API
        layout = self.layout()
        return layout.heightForWidth(width) if layout is not None else -1

    def _publish_minimum(self) -> None:
        """Re-state the honest minimum for the width this widget HAS."""
        layout = self.layout()
        if layout is None or not layout.hasHeightForWidth():
            return
        needed = layout.heightForWidth(self.width())
        if needed >= 0 and needed != self.minimumHeight():
            self.setMinimumHeight(needed)
            # Tell the ancestors in the same breath. `setMinimumHeight`
            # invalidates this widget alone, so a page holding a group
            # holding a flow learned the new height only on the NEXT
            # event pass and was laid out a few pixels short in between
            # (measured 2026-08-14, one level deeper than the 2026-08-13
            # case above).
            self.updateGeometry()

    def minimumSizeHint(self) -> QSize:           # noqa: N802 — Qt override
        """The hint QScrollArea actually reads.

        `setMinimumHeight` alone is not enough: the widgetResizable path
        sizes the held widget from `minimumSizeHint()`, which Qt computes
        from the layout's plain minimum and never from heightForWidth. So
        the height a flow only knows once it has a width is folded in
        HERE, where the scroll area will see it."""
        hint = super().minimumSizeHint()
        layout = self.layout()
        if layout is None or not layout.hasHeightForWidth() or self.width() <= 0:
            return hint
        needed = layout.heightForWidth(self.width())
        return QSize(hint.width(), max(hint.height(), needed))

    def resizeEvent(self, event) -> None:         # noqa: N802 — Qt override
        super().resizeEvent(event)
        self._publish_minimum()

    def event(self, incoming) -> bool:            # noqa: N802 — Qt override
        handled = super().event(incoming)
        if incoming.type() == QEvent.Type.LayoutRequest:
            self._publish_minimum()
        return handled


class FlowRow(FlowContent):
    """A wrapping row that keeps its same-kind members the SAME width.

    The equalizing happens on SHOW, not at build time: a button that has
    not been polished by its window's stylesheet yet hints at the bare
    application font, so a build-time pass measured three medal buttons
    at one width and the shown row wore another (90/95/92px against a
    minimum computed from the unstyled hints — audit finding,
    2026-08-14). Grouping by exact class keeps a lone checkbox riding
    the row's tail from being stretched to a button's width: it is not
    that button's sibling (ALG-5 groups by kind for the same reason)."""

    #: How far a member may be stretched past its natural width to fill
    #: the line (ALG-7 row occupancy). Twice is enough to close a real
    #: gap and little enough that a wide window never grows a row of
    #: absurd slabs — past that the row simply centers, the alignment
    #: the owner sealed on 2026-08-14.
    FILL_FACTOR = 2.0

    def _equalize(self) -> None:
        layout = self.layout()
        if layout is None:
            return
        members = []
        by_kind: dict = {}
        for index in range(layout.count()):
            item = layout.itemAt(index)
            widget = item.widget() if item is not None else None
            if widget is None:
                continue
            widget.ensurePolished()
            members.append(widget)
            by_kind.setdefault(type(widget), []).append(widget)
        for kin in by_kind.values():
            if len(kin) > 1:
                uniform_width(kin)
        if not members:
            return
        # ONLY THE ROW'S OWN KIND IS FILLED. The spread hands its members
        # an equal share, which is right for a row of pills and wrong for
        # the lone Names checkbox riding the slot row's tail — stretched
        # to a button's width it would read as a button (2026-08-14). The
        # most numerous class is the row; anything else keeps its size.
        members = max(by_kind.values(), key=len)
        # ALG-7 ROW OCCUPANCY: a single-line row spreads to FILL the
        # width instead of leaving its right half empty while content
        # continues below (the finding the reflow itself uncovered on
        # the Themes & Slots page — the clipped rows had merely HIDDEN
        # it). Only while everything still fits on one line; a wrapped
        # row is already as full as its content makes it.
        others = sum(
            w.sizeHint().width() + layout._gap
            for kin in by_kind.values() if kin is not members
            for w in kin
        )
        widest = max(w.sizeHint().width() for w in members)
        available = self.width() - others
        gap = layout._gap
        # How many fit on ONE line at their natural width — the row is
        # filled per LINE, not only when everything fits on a single one:
        # five kind tabs wrapping 3-2 left the second line's right half
        # bare, which is the very finding this pass answers.
        per_line = max(1, (available + gap) // (widest + gap))
        per_line = min(per_line, len(members))
        share = (available - gap * (per_line - 1)) // per_line
        # ONE ceiling for the whole row, taken from the WIDEST member:
        # a per-widget ceiling would hand each button a different target
        # and break the uniformity the pass above just established.
        target = min(share, int(widest * self.FILL_FACTOR))
        for widget in members:
            widget.setMinimumWidth(max(target, widget.minimumWidth()))

    def showEvent(self, event) -> None:           # noqa: N802 — Qt override
        super().showEvent(event)
        self._equalize()
        self._publish_minimum()

    def resizeEvent(self, event) -> None:         # noqa: N802 — Qt override
        super().resizeEvent(event)
        # EQUALIZE FIRST, THEN PUBLISH. Widening the members changes
        # where the row wraps, so a height published before that pass
        # described a row that no longer exists — on the owner's live
        # profile the five kind tabs wrapped onto a second line inside a
        # one-line-tall widget, and the pills below were drawn straight
        # over them (audit shot, 2026-08-14).
        self._equalize()
        self._publish_minimum()


def flow_row(members) -> QWidget:
    """A row of pills/buttons that WRAPS instead of running off the page.

    THE SPACE & LEGIBILITY LADDER, step 2 (reflow): a plain `QHBoxLayout`
    of pills has no wrap point, so once the labels outgrow the viewport
    the last pill is simply cut by the right edge — measured on the
    Themes & Slots page at the declared 1280x720 minimum (the face-layout
    row and the content-kind tabs both clipped, and the same capture at
    the previous commit proves it predates the CardGroup migration).
    The gallery flow already solved exactly this problem; a row of
    buttons is the same problem with smaller items."""
    content = FlowRow()
    flow = FlowLayout()
    members = list(members)
    for member in members:
        flow.addWidget(member)
    # UNIFORM SIBLINGS, here rather than at ten call sites (runtime audit
    # ALG-5, 2026-08-15): a wrapping pill row had no uniform width at
    # all, so 'Silver jewels' stood 122px beside 'Thematic jewels' at
    # 136px and 'Date' 108 beside 'Date & Weekday' 137. It went unseen
    # while the window's minimum was wide enough to keep these rows on
    # one line; compacting the Colors page dropped that minimum and the
    # audit caught them immediately. `uniform_width` is the one
    # implementation of the rule (app.ui_style) — this is simply the
    # place every wrapping row passes through. Checkboxes riding a row's
    # free tail are NOT buttons of the same kind and keep their own size.
    uniform_width([m for m in members if isinstance(m, QPushButton)])
    content.setLayout(flow)
    return content


def literal(label: str) -> str:
    """A button label Qt will show EXACTLY as written.

    Qt reads `&` in button text as a mnemonic marker and eats it,
    underlining the next character instead. So "Date & Weekday" reached
    the owner's screen as "Date _Weekday" and "Shrink & pass" as
    "Shrink _pass" — caught on a capture, never by a test, because the
    stored string was right and only the PAINTED text was wrong. Doubling
    the ampersand is Qt's own escape. This lives in the tile/pill builder
    so no gallery can forget it (the same "one chokepoint" fix the icon
    size got in 2026-08-08)."""
    return label.replace("&", "&&")


def pill(label: str, checked: bool, on_click) -> QPushButton:
    button = QPushButton(literal(label))
    style_button(button, "next" if checked else "neutral", small=True)
    button.clicked.connect(lambda checked=False: on_click())
    return button


def number_row(
    tr, settings, setters, key: str, low: float, high: float, title: str,
    form, decimals: int = 0,
):
    """A numeric slider row in the ledger's own UNITS (numerals ledger
    §8: lengths share the numeral's own units so a setting survives any
    change of dial resolution). Shared by the Numerals section's relief
    rows and the Size section's band-size rows (ALG-9 moved the three
    size sliders there, owner order 2026-08-09) — one row shape, one
    definition (Rule #5)."""
    from PySide6.QtWidgets import QHBoxLayout, QLabel, QSlider

    steps = 10 ** decimals
    value = getattr(settings, key)
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setRange(round(low * steps), round(high * steps))
    slider.setValue(round(value * steps))
    label = QLabel(f"{value:.{decimals}f}")
    slider.valueChanged.connect(
        lambda v, lab=label: lab.setText(f"{v / steps:.{decimals}f}")
    )
    slider.sliderReleased.connect(
        lambda: setters[key](
            slider.value() / steps if decimals else slider.value()
        )
    )
    row = QHBoxLayout()
    row.addWidget(slider)
    row.addWidget(label)
    form.addRow(tr(title), row)
    return slider
