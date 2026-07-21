"""Shared modern-button styling (owner 2026-07-14: "veći,
upečatljiviji, življih boja — ne kao app iz 1990-e").

One QSS builder for every reader-dialog button: a vivid vertical
gradient pill with bold white text. The role picks its (top, bottom)
gradient pair from `defaults.UI_BUTTON_COLORS`; hover lightens and
pressed darkens the same pair, so a new role needs only two hex
values.

A second builder, `style_look_chip` (owner round R8b item 4), dresses
the Encyclopedia's look/finish switcher CAPTION the same filled-pill
way — metal finishes, the continents globe looks and every kinship-
group switcher all read through the ONE function, `_LOOK_FILLS` naming
the palette and `_readable_text` deriving light/dark text from each
fill's own luminance.
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


# THE LOOK-SWITCHER FILL PALETTE (owner round R8b item 4: "jel me
# stvarno zezas da ne mozes da napravis gradient button" — the R3
# border-gradient chip (`style_finish_frame`, retired below) FAILED
# visually: QSS has no real gradient-BORDER primitive, so a
# `border-color` gradient only ever paints the four corner miters, never
# a smooth sweep. Every switcher option now wears a FILL instead, same
# recipe as the reader buttons above. Colored keeps the owner's blue-
# left/red-right sweep (`defaults.ENCYCLOPEDIA_FINISH_GRADIENT`, reused
# — Rule #5), now filling the whole chip; Bronze/Gold/Silver reuse their
# own existing border hex (`defaults.ENCYCLOPEDIA_FINISH_BORDER_COLORS`)
# as a SOLID fill. The continents GLOBE looks are new this round — the
# owner's own four suggested words ("atmosphere = sky-blue gradient,
# clean = deep ocean blue, day = warm gold, night = navy") realized as
# one coherent family: Atmosphere leads sky-blue and ends warm gold (the
# DAY pairing), Atmosphere · Night leads navy and ends the SAME blue the
# Colored gradient uses (family cohesion across the whole palette),
# Clean is a solid ocean teal by day and the SAME navy by night. Text
# color is NEVER hand-picked (`_readable_text`, YIQ luminance per fill)
# so a future palette retune can never silently go illegible.
_LOOK_FILLS: dict[str, str | tuple[str, str]] = {
    "Bronze": defaults.ENCYCLOPEDIA_FINISH_BORDER_COLORS["Bronze"],
    "Gold": defaults.ENCYCLOPEDIA_FINISH_BORDER_COLORS["Gold"],
    "Silver": defaults.ENCYCLOPEDIA_FINISH_BORDER_COLORS["Silver"],
    "Colored": defaults.ENCYCLOPEDIA_FINISH_GRADIENT,
    "Atmosphere": ("#4FC3F7", "#FFB74D"),
    "Atmosphere · Night": ("#0B1F3A", "#3B5FE0"),
    "Clean": "#0E6B8C",
    "Clean · Night": "#0B1F3A",
}


def _yiq(hex_color: str) -> float:
    """The standard YIQ perceived-brightness estimate (0..255) — one
    formula, reused for every fill so "readable" is derived, never
    hand-guessed per color (Rule #4)."""
    color = QColor(hex_color)
    return (color.red() * 299 + color.green() * 587 + color.blue() * 114) / 1000


def _readable_text(fill) -> str:
    """Light text on a dark fill, dark text on a light one — checked
    against EVERY stop of a gradient fill, so a two-tone sweep only
    gets white text when BOTH ends are dark enough to carry it."""
    stops = fill if isinstance(fill, tuple) else (fill,)
    dark_fill = all(_yiq(stop) < 128 for stop in stops)
    return (
        defaults.THEME_COLORS["text_primary"] if dark_fill
        else defaults.THEME_COLORS["surface_0"]
    )


def style_look_chip(label, look_label: str) -> None:
    """The look/finish switcher's caption (owner fix round R8b, item 4)
    — every option wears a FILL now (`_LOOK_FILLS` above), not the R3
    border-only frame it replaces (`style_finish_frame`, retired: the
    gradient-BORDER trick never rendered as a real sweep). A
    `look_label` outside that table — a kinship-group switcher never
    meant to read as a metal or a globe look (Planets/Signs/Art, the
    Week's Canon/Gods/Religions/Themes/Animals, Astrology's Logo &
    Constellation/Colored/Sign) — wears a neutral dark chip instead,
    the SAME dialog-surface tone `app.theme` already uses, always
    readable with light text (Rule #5: no second hand-picked neutral)."""
    fill = _LOOK_FILLS.get(look_label)
    if fill is None:
        background = defaults.THEME_COLORS["surface_3"]
        text = defaults.THEME_COLORS["text_primary"]
    elif isinstance(fill, tuple):
        background = (
            "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            f"stop:0 {fill[0]}, stop:1 {fill[1]})"
        )
        text = _readable_text(fill)
    else:
        background = fill
        text = _readable_text(fill)
    label.setStyleSheet(
        f"color: {text}; font-weight: bold;"
        f"font-size: {defaults.UI_BUTTON_SMALL_FONT_PX}px;"
        f"padding: {defaults.UI_BUTTON_SMALL_PADDING_PX[0]}px "
        f"{defaults.UI_BUTTON_SMALL_PADDING_PX[1]}px;"
        f"border-radius: {defaults.UI_BUTTON_RADIUS_PX}px;"
        f"background: {background};"
        "border: 1px solid rgba(0, 0, 0, 130);"
    )
