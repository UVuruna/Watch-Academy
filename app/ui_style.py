"""Shared modern-button styling (owner 2026-07-14: "veći,
upečatljiviji, življih boja — ne kao app iz 1990-e").

One QSS builder for every reader-dialog button: a vivid vertical
gradient pill with bold white text. The role picks its (top, bottom)
gradient pair from `defaults.UI_BUTTON_COLORS`; hover lightens and
pressed darkens the same pair, so a new role needs only two hex
values.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from config import defaults


def _stops(top: str, bottom: str, factor: int = 100) -> str:
    """The two gradient stops, lightened (>100) or darkened (<100)."""
    a = QColor(top).lighter(factor) if factor >= 100 else QColor(
        top).darker(200 - factor)
    b = QColor(bottom).lighter(factor) if factor >= 100 else QColor(
        bottom).darker(200 - factor)
    return (
        "qlineargradient(x1:0, y1:0, x2:0, y2:1, "
        f"stop:0 {a.name()}, stop:1 {b.name()})"
    )


def _qss(role: str, small: bool) -> str:
    top, bottom = defaults.UI_BUTTON_COLORS[role]
    font = (
        defaults.UI_BUTTON_SMALL_FONT_PX if small
        else defaults.UI_BUTTON_FONT_PX
    )
    pad_v, pad_h = (
        defaults.UI_BUTTON_SMALL_PADDING_PX if small
        else defaults.UI_BUTTON_PADDING_PX
    )
    base = (
        "color: white; font-weight: bold;"
        f"font-size: {font}px;"
        f"padding: {pad_v}px {pad_h}px;"
        f"border-radius: {defaults.UI_BUTTON_RADIUS_PX}px;"
        "border: 1px solid rgba(0, 0, 0, 130);"
    )
    return (
        f"QPushButton, QToolButton {{ {base}"
        f"background: {_stops(top, bottom)}; }}"
        "QPushButton:hover, QToolButton:hover {"
        f"background: {_stops(top, bottom, 120)}; }}"
        "QPushButton:pressed, QToolButton:pressed {"
        f"background: {_stops(top, bottom, 80)}; }}"
    )


def style_button(button, role: str, small: bool = False) -> None:
    """Dress a QPushButton / QToolButton as the role's gradient pill."""
    button.setStyleSheet(_qss(role, small))
    button.setCursor(Qt.CursorShape.PointingHandCursor)


def style_finish_frame(label, finish: str) -> None:
    """The FINISH SWITCHER's caption (owner fix round R3, Color
    Switcher.png): a border-only frame in the finish's own color — NO
    fill, so it reads as a selector chip rather than another solid
    button. "Colored" wears a two-stop gradient border (owner
    correction 2026-07-21: blue on the left flowing to red) — QSS has
    no gradient BORDER property, so the gradient is faked the standard
    Qt way: the OUTER widget paints the gradient as its background and
    the inset padding shows through as a colored "border ring" around
    the INNER text (owner's `background-clip` trick made portable) —
    here the label draws directly on the dialog surface, so the ring
    shows the gradient itself with the surface color inset instead.
    NOT every topic's arrow-cycle is a metal finish (Planets/Signs/Art,
    the Week's kinship groups, Astrology's Logo & Constellation/Colored/
    Sign) — anything outside the four finish names wears the neutral
    accent border, never the gradient (that reads specifically as
    "every color", reserved for the actual Colored finish)."""
    if finish == "Colored":
        stops = defaults.ENCYCLOPEDIA_FINISH_GRADIENT
        step = 1 / max(1, len(stops) - 1)
        stops_css = ", ".join(
            f"stop:{round(i * step, 3)} {hue}" for i, hue in enumerate(stops)
        )
        border = (
            "3px solid transparent; border-image: none; "
            "border-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            f"{stops_css}) 1"
        )
    else:
        solid = defaults.ENCYCLOPEDIA_FINISH_BORDER_COLORS.get(
            finish, defaults.THEME_COLORS["accent"]
        )
        border = f"3px solid {solid}"
    label.setStyleSheet(
        f"color: {defaults.THEME_COLORS['text_primary']};"
        "font-weight: bold;"
        f"font-size: {defaults.UI_BUTTON_SMALL_FONT_PX}px;"
        f"padding: {defaults.UI_BUTTON_SMALL_PADDING_PX[0]}px "
        f"{defaults.UI_BUTTON_SMALL_PADDING_PX[1]}px;"
        f"border-radius: {defaults.UI_BUTTON_RADIUS_PX}px;"
        "background: transparent;"
        f"border: {border};"
    )
