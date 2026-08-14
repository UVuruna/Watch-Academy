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
    QFrame, QGroupBox, QLabel, QToolButton, QVBoxLayout, QWidget,
)

from app.ui_style import tooltip_wrap, uniform_width
from app.watch_face.widgets import FlowLayout, TILE_ICON_PX, literal
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
# pictures (the ballot's min/max seal; TILE_ICON_PX stays the ceiling).
MIN_ICON_PX = 64


class OptionCard(QToolButton):
    """One choice with (or without) a picture — see controls.md.

    `blurb` is REQUIRED (owner order: the hover description always
    exists); an intentionally empty blurb is passed explicitly."""

    def __init__(
        self, key: str, label: str, blurb: str, icon: QIcon | None = None,
        kind: CardKind = CardKind.RADIO, compact: bool = False,
        min_icon_px: int = MIN_ICON_PX, max_icon_px: int = TILE_ICON_PX,
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
                placeholder = QPixmap(max_icon_px, max_icon_px)
                placeholder.fill(Qt.GlobalColor.transparent)
                icon = QIcon(placeholder)
            self.setIcon(icon)
            self.setIconSize(QSize(max_icon_px, max_icon_px))
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
        self._column = QVBoxLayout(self)
        self._description: QLabel | None = None
        if description:
            self._description = QLabel(description)
            self._description.setWordWrap(True)
            self._column.addWidget(self._description)
        self._card_flow = FlowLayout()
        self._card_host = QWidget()
        self._card_host.setLayout(self._card_flow)
        self._column.addWidget(self._card_host)
        self._divider: QFrame | None = None
        self._switch_flow = FlowLayout()
        self._switch_host = QWidget()
        self._switch_host.setLayout(self._switch_flow)
        self._column.addWidget(self._switch_host)

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
