"""THE ELEMENT CLASSES (owner ballot verdicts 2026-08-14, see
controls.md) — OptionCard + CardGroup, the grammar over `widgets.py`'s
vocabulary: RADIO exclusivity lives on the group, the selection border
is always reserved and only changes color (amber = radio pick, green =
switch on), every card carries a mandatory hover blurb, rows flow
CENTERED, and icons grow toward their maximum as the viewport widens.
"""

from enum import Enum

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QFrame, QGroupBox, QLabel, QSizePolicy, QToolButton, QVBoxLayout, QWidget,
)

from app.ui_style import tooltip_wrap, uniform_width
from app.watch_face.widgets import (
    FlowContent, FlowLayout, TILE_ICON_PX, literal,
)
from config import palette


class CardKind(Enum):
    RADIO = "radio"      # one pick per group — amber selection border
    SWITCH = "switch"    # independent on/off — green selection border


# The selection border hues — existing pledges only, no new hex enters
# the program (Rule #4): amber is the window's own accent, green is the
# "next"/on pill's light stop.
_BORDER_BY_KIND = {
    CardKind.RADIO: palette.THEME_COLORS["accent"],
    CardKind.SWITCH: palette.UI_BUTTON_COLORS["next"][0],
}
# The icon growth floor: below this a row wraps instead of starving the
# pictures (the ballot's min/max seal).
MIN_ICON_PX = 64
#: The growth CEILING — the shared gallery size stays it. Raising it to
#: 192px was measured on 2026-08-14 and REVERTED: bigger cards pushed
#: the Colors page's own galleries past their host and the audit read
#: three fresh clippings, so the ladder's remedy here is spacing, not
#: size.
MAX_ICON_PX = TILE_ICON_PX


class OptionCard(QToolButton):
    """One choice with (or without) a picture — see controls.md.

    `blurb` is REQUIRED (owner order: the hover description always
    exists); an intentionally empty blurb is passed explicitly."""

    def __init__(
        self, key: str, label: str, blurb: str, icon: QIcon | None = None,
        kind: CardKind = CardKind.RADIO, compact: bool = False,
        min_icon_px: int = MIN_ICON_PX, max_icon_px: int = MAX_ICON_PX,
    ):
        super().__init__()
        self.key = key
        self.kind = kind
        self.compact = compact
        self.min_icon_px = min_icon_px
        self.max_icon_px = max_icon_px
        self._checked = False
        self.setText(literal(label))
        if blurb:
            self.setToolTip(tooltip_wrap(blurb))
        if compact:
            # The pill shape: text only, no icon box reserved.
            self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        else:
            self.setToolButtonStyle(
                Qt.ToolButtonStyle.ToolButtonTextUnderIcon
            )
            if icon is None:
                # An honest blank field the same size as its siblings
                # (ALG-5) — never a shrunken tile, never invented art.
                placeholder = QPixmap(TILE_ICON_PX, TILE_ICON_PX)
                placeholder.fill(Qt.GlobalColor.transparent)
                icon = QIcon(placeholder)
            self.setIcon(icon)
            # Starts at the shared gallery size and GROWS from there
            # (`CardGroup.resizeEvent`) — it never starts at the ceiling.
            self.setIconSize(QSize(TILE_ICON_PX, TILE_ICON_PX))
        self._paint_border()

    def is_checked(self) -> bool:
        return self._checked

    def set_checked(self, on: bool) -> None:
        """Colors the border, never moves the box (the reserved-border
        law from `widgets.tile`)."""
        self._checked = bool(on)
        self._paint_border()

    def set_icon_px(self, px: int) -> None:
        """The group's resize hand — clamped to the card's own range."""
        if self.compact:
            return
        px = max(self.min_icon_px, min(self.max_icon_px, int(px)))
        if self.iconSize().width() != px:
            self.setIconSize(QSize(px, px))

    def _paint_border(self) -> None:
        border = (
            _BORDER_BY_KIND[self.kind] if self._checked else "transparent"
        )
        self.setStyleSheet(
            f"QToolButton {{ border: 2px solid {border};"
            "border-radius: 8px; padding: 3px; }"
        )


class CardGroup(QGroupBox):
    """Title + description + a CENTER-flowing card gallery — the
    grammar (see controls.md): RADIO exclusivity enforced here, the
    switch subset separated by a divider line whenever both kinds meet
    inside one group (owner order 2026-08-14).

    `on_pick(key)` fires on a radio pick; `on_toggle(key, on)` on a
    switch flip — both LIVE-APPLY, same as every section setter."""

    def __init__(
        self, title: str, description: str = "",
        on_pick=None, on_toggle=None,
    ):
        super().__init__(title)
        self.on_pick = on_pick
        self.on_toggle = on_toggle
        self._cards: dict[str, OptionCard] = {}
        self._switches: dict[str, OptionCard] = {}
        policy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        policy.setHeightForWidth(True)
        self.setSizePolicy(policy)
        # A GROUP MUST READ AS A GROUP. The box drew in the page's own
        # ground with a hairline nobody could see, and the runtime audit
        # put a number on what the eye already said: at the audit's own
        # 12-per-channel tolerance `surface_1` is NOT distinguishable
        # from `surface_0`, so the whole content area measured as bare
        # background. `surface_2` is — one step up the same ladder, an
        # existing pledge, no new hex (Rule #4).
        self.setStyleSheet(
            "CardGroup { background: %s; border: 1px solid %s;"
            " border-radius: 10px; margin-top: 8px; padding-top: 10px; }"
            "CardGroup::title { subcontrol-origin: margin;"
            " subcontrol-position: top left; left: 10px; padding: 0 4px;"
            " color: %s; }" % (
                palette.THEME_COLORS["surface_2"],
                palette.THEME_COLORS["surface_3"],
                palette.THEME_COLORS["accent"],
            )
        )
        self._column = QVBoxLayout(self)
        # THE SIDE MARGINS ARE THE GALLERY'S WIDTH. The box's own frame
        # already separates the group visually, so the default side
        # padding buys nothing and costs a whole card per row: at the
        # 1280x720 minimum the theme families sat 3-per-row with room
        # for 4, and the leftover read as an empty right half (ALG-7,
        # audit 2026-08-14). The top/bottom margins stay as Qt set them
        # — that is where the title lives.
        margins = self._column.contentsMargins()
        self._column.setContentsMargins(4, margins.top(), 4, margins.bottom())
        self._description: QLabel | None = None
        if description:
            self._description = QLabel(description)
            self._description.setWordWrap(True)
            self._column.addWidget(self._description)
        # FlowContent, never a bare QWidget: a flow only knows its
        # height once it has a width, and `QScrollArea`'s widgetResizable
        # path sizes pages from plain minimum hints — the measured
        # failure `widgets.FlowContent` documents (galleries compressed
        # to 10px on the owner's live profile). The gallery host must
        # publish that height or a wrapped group starves inside the
        # page's scroll area.
        self._card_flow = FlowLayout()
        self._card_host = FlowContent()
        self._card_host.setLayout(self._card_flow)
        self._column.addWidget(self._card_host)
        self._divider: QFrame | None = None
        self._switch_flow = FlowLayout()
        self._switch_host = FlowContent()
        self._switch_host.setLayout(self._switch_flow)
        self._column.addWidget(self._switch_host)
        # AN EMPTY HOST IS NOT SPACE. A group with no switches (most of
        # them) still held a zero-height FlowContent plus the column's
        # spacing around it — enough to leave the group a few pixels
        # short of its own content and to have the audit report a
        # zero-height widget "drawn over" its sibling. Each host appears
        # when its first member does.
        self._card_host.setVisible(False)
        self._switch_host.setVisible(False)

    # ── membership ────────────────────────────────────────────────────
    def add_card(
        self, key: str, label: str, blurb: str, icon: QIcon | None = None,
        compact: bool = False,
    ) -> OptionCard:
        card = OptionCard(
            key, label, blurb, icon, CardKind.RADIO, compact=compact
        )
        card.clicked.connect(lambda checked=False, k=key: self._pick(k))
        self._cards[key] = card
        self._card_host.setVisible(True)
        self._card_flow.addWidget(card)
        self._refresh_divider()
        return card

    def add_switch(
        self, key: str, label: str, blurb: str, icon: QIcon | None = None,
        compact: bool = False,
    ) -> OptionCard:
        card = OptionCard(
            key, label, blurb, icon, CardKind.SWITCH, compact=compact
        )
        card.clicked.connect(lambda checked=False, k=key: self._flip(k))
        self._switches[key] = card
        self._switch_host.setVisible(True)
        self._switch_flow.addWidget(card)
        self._refresh_divider()
        return card

    def finish(self) -> None:
        """Uniform member widths (ALG-5), called once after the last
        add — the widest label decides for all members of each subset."""
        if self._cards:
            uniform_width(list(self._cards.values()))
        if self._switches:
            uniform_width(list(self._switches.values()))

    # ── state ─────────────────────────────────────────────────────────
    def value(self) -> str | None:
        """The RADIO pick (None until one is set)."""
        for key, card in self._cards.items():
            if card.is_checked():
                return key
        return None

    def values(self) -> frozenset:
        """The set of switched-on keys."""
        return frozenset(
            key for key, card in self._switches.items() if card.is_checked()
        )

    def set_value(self, key: str | None) -> None:
        for card_key, card in self._cards.items():
            card.set_checked(card_key == key)

    def set_switch(self, key: str, on: bool) -> None:
        self._switches[key].set_checked(on)

    def disable_with_reason(self, reason: str) -> None:
        """Grayed, never hidden — the graceful-truth pattern the Aura
        group proved (an honest gate, not a dead or vanishing control)."""
        self.setEnabled(False)
        self.setToolTip(tooltip_wrap(reason))

    # ── behavior ──────────────────────────────────────────────────────
    def _pick(self, key: str) -> None:
        # Radio law: the pick moves, it never empties — clicking the
        # checked card keeps it checked and fires nothing.
        if self._cards[key].is_checked():
            self._cards[key].set_checked(True)
            return
        self.set_value(key)
        if self.on_pick is not None:
            self.on_pick(key)

    def _flip(self, key: str) -> None:
        card = self._switches[key]
        card.set_checked(not card.is_checked())
        if self.on_toggle is not None:
            self.on_toggle(key, card.is_checked())

    def _refresh_divider(self) -> None:
        """The DIVIDER (owner order 2026-08-14): a thin line separates
        the radio and switch subsets whenever BOTH exist in one group."""
        needed = bool(self._cards) and bool(self._switches)
        if needed and self._divider is None:
            self._divider = QFrame()
            self._divider.setFrameShape(QFrame.Shape.HLine)
            self._divider.setFrameShadow(QFrame.Shadow.Plain)
            index = self._column.indexOf(self._switch_host)
            self._column.insertWidget(index, self._divider)
        elif not needed and self._divider is not None:
            self._column.removeWidget(self._divider)
            self._divider.deleteLater()
            self._divider = None

    def hasHeightForWidth(self) -> bool:  # noqa: N802 — Qt API
        """A group whose cards WRAP is a height-for-width widget, and it
        must say so: told once, the parent layout sizes it correctly in
        the SAME pass instead of learning the true height only from a
        minimum republished a frame later (the 4px-short group the audit
        measured on 2026-08-14)."""
        return True

    def heightForWidth(self, width: int) -> int:  # noqa: N802 — Qt API
        return self._column_height(width)

    def _column_height(self, width: int) -> int:
        """What the group's own column needs at `width` — content plus
        the column's margins, which is where a QGroupBox pays for its
        title and frame."""
        margins = self._column.contentsMargins()
        inner = max(1, width - margins.left() - margins.right())
        needed = self._column.heightForWidth(inner)
        return -1 if needed < 0 else needed

    def sizeHint(self) -> QSize:  # noqa: N802 — Qt override
        hint = super().sizeHint()
        needed = self._column_height(self.width()) if self.width() > 0 else -1
        if needed < 0:
            return hint
        return QSize(hint.width(), max(hint.height(), needed))

    def minimumSizeHint(self) -> QSize:  # noqa: N802 — Qt override
        """The height a WRAPPED gallery really needs at this width — and
        NOT a pixel more.

        Two failures meet here. `QGroupBox` computes its minimum from
        the layout's PLAIN minimum, which for a flow is one row, so a
        group whose cards wrapped into three rows asked far too little.
        But its generic frame allowance also runs a few pixels ABOVE what
        the column margins actually consume, and asking for those was
        just as bad: the parent grants the column's honest number and the
        group then reads as permanently 4px clipped against its own
        inflated claim (audit, 2026-08-14). So the answer is the
        column's own arithmetic, which is what the layout will hand
        out."""
        hint = super().minimumSizeHint()
        # Before the group has a width there is nothing to wrap against,
        # so the column's PLAIN minimum is the honest answer — falling
        # back to the QGroupBox hint there re-imported its inflated
        # frame allowance and the page inherited the same 4px phantom.
        needed = (
            self._column_height(self.width()) if self.width() > 0
            else self._column.minimumSize().height()
        )
        if needed < 0:
            return hint
        return QSize(hint.width(), needed)

    def resizeEvent(self, event) -> None:  # noqa: N802 — Qt override
        """ICON GROWTH (the wide-window remedy, owner-approved): icons
        grow toward `max_icon_px` when the row has width to spare, and
        clamp at `min_icon_px` so a narrow window wraps instead of
        starving the pictures. The group is the one who knows the width
        budget; cards clamp to their own range."""
        super().resizeEvent(event)
        for flow, members in (
            (self._card_flow, self._cards), (self._switch_flow, self._switches),
        ):
            visual = [c for c in members.values() if not c.compact]
            if not visual:
                continue
            gap = flow._gap
            margins = self._column.contentsMargins()
            available = self.width() - margins.left() - margins.right()
            count = len(visual)
            per_card = (available - (count - 1) * gap) // count
            # ~22px of card chrome around the icon: 2px border + 3px
            # padding per side, plus the label's breathing room.
            for card in visual:
                card.set_icon_px(per_card - 22)


def divider_present(group: CardGroup) -> bool:
    """Test hook: whether the radio/switch divider line is drawn."""
    return group._divider is not None


def picture_group(
    title: str, description: str, entries, current, on_pick,
    *, switches=(), on_toggle=None, compact: bool = False,
) -> CardGroup:
    """THE ONE DOOR every picture gallery now walks through (the
    CardGroup migration, 2026-08-14) — the shape that replaced
    `QGroupBox(title) + QLabel(sentence) + widgets.flow_gallery([tile,
    ...])`, which every section used to assemble by hand.

    `entries` are `(key, label, blurb, icon)` radio cards, `switches`
    are `(key, label, blurb, icon, on)` independent toggles; a group
    carrying both grows the divider line by itself. `on_pick(key)` and
    `on_toggle(key, on)` are the section's own live-apply setters — the
    caller no longer binds one lambda per tile, so a gallery can no
    longer forget the reserved border, the uniform width, the hover
    blurb or the centered flow."""
    group = CardGroup(
        title, description, on_pick=on_pick, on_toggle=on_toggle
    )
    for key, label, blurb, icon in entries:
        group.add_card(key, label, blurb, icon, compact=compact)
    for key, label, blurb, icon, on in switches:
        group.add_switch(key, label, blurb, icon, compact=compact)
        group.set_switch(key, on)
    if current is not None:
        group.set_value(current)
    group.finish()
    return group


# ═══════════════════════════ THE VALUE KNOBS ═══════════════════════════
# Owner verdicts 2026-08-14: taxonomy 7 (K-360 full circle / K-270 arc /
# K-270D arc with the default notch), 7A (the notch REPLACES the Default
# button — click it, or double-click the disc for exact entry) and 7C
# (kin families wear kin ring hues, `palette.KNOB_FAMILY_COLORS`; the
# notch is always the "next" green — one language for "factory").

class KnobKind(Enum):
    K360 = "k360"     # full circle, no ends — the value IS an angle
    K270 = "k270"     # arc, min bottom-left, max bottom-right
    K270D = "k270d"   # K-270 plus the default notch


class ValueUnit(Enum):
    PERCENT = "percent"
    PIXEL = "pixel"
    FACTOR = "factor"
    PLAIN = "plain"


# The arc geometry every K-270 shares: 270 degrees of travel starting
# at the bottom-left (225 deg in math CCW terms), sweeping CLOCKWISE to
# the bottom-right — the owner's own SVG Styler layout.
_ARC_START_DEG = 225.0
_ARC_SPAN_DEG = 270.0
#: How close (px) a click must land to the notch to count as a reset.
_NOTCH_HIT_PX = 12.0


class ValueKnob(QWidget):
    """One circular value control (see controls.md) — value + unit in
    the disc's center, the family-colored progress ring around it, and
    (K-270D) the green default notch on the arc.

    LIVE label while dragging, COMMIT (`on_change`) on release / wheel /
    exact entry — the same commit rhythm `widgets.number_row` had."""

    def __init__(
        self, key: str, title: str, blurb: str, *, unit: ValueUnit,
        low: float, high: float, family: str,
        kind: KnobKind = KnobKind.K270D, default_value: float | None = None,
        decimals: int = 0, on_change=None, on_reset=None,
        diameter_px: int = 96,
    ):
        super().__init__()
        if kind is KnobKind.K270D and default_value is None:
            raise ValueError(
                f"{key}: a K-270D knob carries the default notch — pass "
                "default_value, or choose KnobKind.K270"
            )
        self.key = key
        self.title = title
        self.unit = unit
        self.low = float(low)
        self.high = float(high)
        self.family = family
        self.ring_color = palette.KNOB_FAMILY_COLORS[family]
        self.kind = kind
        self.default_value = default_value
        self.decimals = decimals
        self.on_change = on_change
        self.on_reset = on_reset
        self._value = self.low
        self._dragging = False
        self.setFixedSize(diameter_px, diameter_px)  # layout-law: exempt - a knob is a fixed circular instrument like an icon; rows of knobs wrap by count (FlowLayout), the disc itself never stretches
        if blurb:
            self.setToolTip(tooltip_wrap(blurb))

    # ── value plumbing ────────────────────────────────────────────────
    def value(self) -> float:
        return self._value

    def set_value(self, value: float) -> None:
        if self.kind is KnobKind.K360:
            value = value % 360.0
        else:
            value = max(self.low, min(self.high, float(value)))
        changed = value != self._value
        self._value = value
        if changed:
            self.update()

    def reset(self) -> None:
        """The notch's job (7A): back to factory, committed. An
        `on_reset` hook REPLACES the plain commit — the override rows'
        "Skin default" semantics, where reset stores None so the render
        side genuinely stops overriding (opacity.py's own law)."""
        if self.default_value is None:
            return
        self.set_value(self.default_value)
        if self.on_reset is not None:
            self.on_reset()
        else:
            self._commit()

    def value_text(self) -> str:
        if self.unit is ValueUnit.PERCENT:
            return f"{round(self._value)}%"
        if self.unit is ValueUnit.FACTOR:
            return f"{self._value:.{max(1, self.decimals)}f}"
        if self.kind is KnobKind.K360:
            return f"{round(self._value)}\N{DEGREE SIGN}"
        return f"{self._value:.{self.decimals}f}" if self.decimals else f"{round(self._value)}"

    def fraction(self) -> float:
        """Progress along the travel, 0..1."""
        if self.kind is KnobKind.K360:
            return (self._value % 360.0) / 360.0
        if self.high == self.low:
            return 0.0
        return (self._value - self.low) / (self.high - self.low)

    def _commit(self) -> None:
        if self.on_change is not None:
            self.on_change(self._value)

    # ── geometry ──────────────────────────────────────────────────────
    def _fraction_to_math_deg(self, fraction: float) -> float:
        return _ARC_START_DEG - _ARC_SPAN_DEG * fraction

    def _pos_to_value(self, x: float, y: float) -> float | None:
        """Map a widget-local point to a value along the travel; None in
        the dead wedge under a K-270 arc."""
        import math

        cx, cy = self.width() / 2.0, self.height() / 2.0
        math_deg = math.degrees(math.atan2(cy - y, x - cx)) % 360.0
        if self.kind is KnobKind.K360:
            return (90.0 - math_deg) % 360.0  # 12 o'clock = 0, clockwise
        travelled = (_ARC_START_DEG - math_deg) % 360.0
        if travelled > _ARC_SPAN_DEG:
            return None
        return self.low + (self.high - self.low) * (travelled / _ARC_SPAN_DEG)

    def _notch_point(self):
        import math

        if self.default_value is None:
            return None
        if self.high == self.low:
            return None
        fraction = (self.default_value - self.low) / (self.high - self.low)
        deg = math.radians(self._fraction_to_math_deg(fraction))
        cx, cy = self.width() / 2.0, self.height() / 2.0
        radius = min(cx, cy) - 5.0
        return cx + radius * math.cos(deg), cy - radius * math.sin(deg)

    # ── interaction ───────────────────────────────────────────────────
    def wheelEvent(self, event) -> None:  # noqa: N802 — Qt override
        span = 360.0 if self.kind is KnobKind.K360 else (self.high - self.low)
        step = span / 100.0 if self.decimals else max(1.0, span / 100.0)
        direction = 1.0 if event.angleDelta().y() > 0 else -1.0
        self.set_value(self._value + direction * step)
        self._commit()

    def mousePressEvent(self, event) -> None:  # noqa: N802 — Qt override
        position = event.position()
        notch = self._notch_point()
        if self.kind is KnobKind.K270D and notch is not None:
            dx, dy = position.x() - notch[0], position.y() - notch[1]
            if (dx * dx + dy * dy) ** 0.5 <= _NOTCH_HIT_PX:
                self.reset()
                return
        value = self._pos_to_value(position.x(), position.y())
        if value is not None:
            self._dragging = True
            self.set_value(value)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802 — Qt override
        if not self._dragging:
            return
        position = event.position()
        value = self._pos_to_value(position.x(), position.y())
        if value is not None:
            self.set_value(value)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802 — Qt override
        if self._dragging:
            self._dragging = False
            self._commit()

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: N802 — Qt override
        """Exact entry (the SVG Styler's hidden `exact-value`, made
        visible): a modal spin dialog, committed on OK."""
        from PySide6.QtWidgets import QInputDialog

        low = 0.0 if self.kind is KnobKind.K360 else self.low
        high = 360.0 if self.kind is KnobKind.K360 else self.high
        value, ok = QInputDialog.getDouble(
            self, self.title, self.title, self._value, low, high,
            max(self.decimals, 0),
        )
        if ok:
            self.set_value(value)
            self._commit()

    # ── painting ──────────────────────────────────────────────────────
    def paintEvent(self, event) -> None:  # noqa: N802 — Qt override
        from PySide6.QtCore import QRectF
        from PySide6.QtGui import (
            QColor, QConicalGradient, QPainter, QPen,
        )

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        ring = 6.0
        rect = QRectF(
            ring / 2 + 2, ring / 2 + 2,
            self.width() - ring - 4, self.height() - ring - 4,
        )
        track = QPen(QColor(palette.THEME_COLORS["surface_3"]), ring)
        track.setCapStyle(Qt.PenCapStyle.RoundCap)
        progress = QPen(QColor(self.ring_color), ring)
        progress.setCapStyle(Qt.PenCapStyle.RoundCap)
        if self.kind is KnobKind.K360:
            # The full-circle ring is the whole scale at once (the hue
            # rainbow for the color picker); the center text is the value.
            gradient = QConicalGradient(rect.center(), 90.0)
            for stop in range(7):
                gradient.setColorAt(
                    stop / 6.0, QColor.fromHsv(int(360 * stop / 6) % 360, 220, 235)
                )
            painter.setPen(QPen(gradient, ring))
            painter.drawArc(rect, 0, 360 * 16)
        else:
            painter.setPen(track)
            painter.drawArc(
                rect, int(_ARC_START_DEG * 16), int(-_ARC_SPAN_DEG * 16)
            )
            painter.setPen(progress)
            painter.drawArc(
                rect, int(_ARC_START_DEG * 16),
                int(-_ARC_SPAN_DEG * 16 * self.fraction()),
            )
            notch = self._notch_point()
            if self.kind is KnobKind.K270D and notch is not None:
                pen = QPen(QColor(_BORDER_BY_KIND[CardKind.SWITCH]), 3.0)
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                painter.setPen(pen)
                cx, cy = self.width() / 2.0, self.height() / 2.0
                towards = (
                    cx + (notch[0] - cx) * 0.86, cy + (notch[1] - cy) * 0.86
                )
                painter.drawLine(
                    int(towards[0]), int(towards[1]),
                    int(notch[0]), int(notch[1]),
                )
        painter.setPen(QColor(palette.THEME_COLORS["text_primary"]))
        font = painter.font()
        font.setPointSize(11)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(
            self.rect(), Qt.AlignmentFlag.AlignCenter, self.value_text()
        )
        painter.end()


def knob_row(knob: ValueKnob) -> QWidget:
    """The knob with its centered title beneath — the mockup's shape,
    packaged so sections place ONE widget per value."""
    holder = QWidget()
    column = QVBoxLayout(holder)
    column.setContentsMargins(0, 0, 0, 0)
    column.addWidget(knob, alignment=Qt.AlignmentFlag.AlignHCenter)
    title = QLabel(knob.title)
    title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    if knob.toolTip():
        title.setToolTip(knob.toolTip())
    column.addWidget(title)
    return holder
