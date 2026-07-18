"""Rule #16 POLISH round (2026-07-18): one dark QSS theme for dialog
chrome — replaces the default gray Qt widget look with the palette
from monorepo DESIGN.md, anchored on the dial's own slate/gold
identity. Every color and radius comes from `config/defaults.py`
(`THEME_COLORS`, `THEME_RADIUS_*`) — this module only builds the QSS
string and applies it; a widget's OWN `setStyleSheet` (the palette/
ring-tint color chips, the ui_style gradient buttons) still wins over
these general rules, so nothing that already carries a deliberate
per-instance color is touched.
"""

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QDialogButtonBox, QWidget

from config import defaults

_C = defaults.THEME_COLORS
_RADIUS_CONTROL = defaults.THEME_RADIUS_CONTROL_PX
_RADIUS_CARD = defaults.THEME_RADIUS_CARD_PX
_RADIUS_PILL = defaults.THEME_RADIUS_PILL_PX


def _shade(hex_color: str, factor: int) -> str:
    """Lighten (factor > 100) or darken (factor < 100) a hex color."""
    color = QColor(hex_color)
    shaded = (
        color.lighter(factor) if factor >= 100 else color.darker(200 - factor)
    )
    return shaded.name()


_ACCENT_HOVER = _shade(_C["accent"], 115)
_ACCENT_PRESSED = _shade(_C["accent"], 85)
_SURFACE_HOVER = _shade(_C["surface_2"], 130)

_QSS = f"""
QDialog {{
    background: {_C['surface_0']};
    color: {_C['text_primary']};
}}
QLabel {{
    background: transparent;
    color: {_C['text_primary']};
}}

/* --- Group-box cards: flat, rounded, no default etched frame --- */
QGroupBox {{
    background: {_C['surface_1']};
    border: 1px solid {_C['border']};
    border-radius: {_RADIUS_CARD}px;
    margin-top: 14px;
    padding: 16px 12px 12px 12px;
    font-weight: 600;
    color: {_C['text_primary']};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: {_C['accent']};
}}

/* --- Nav column: comfortable rows, rounded selection pill --- */
QListWidget {{
    background: {_C['surface_2']};
    border: 1px solid {_C['border']};
    border-radius: {_RADIUS_CARD}px;
    padding: 6px;
    outline: none;
    color: {_C['text_secondary']};
}}
QListWidget::item {{
    padding: 10px 12px;
    margin: 2px 0;
    border-radius: {_RADIUS_PILL}px;
}}
QListWidget::item:hover {{
    background: {_C['surface_3']};
    color: {_C['text_primary']};
}}
QListWidget::item:selected {{
    background: {_C['accent']};
    color: {_C['surface_0']};
    font-weight: 600;
}}

/* --- Inputs: combos, spin boxes, line edits --- */
QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {{
    background: {_C['surface_2']};
    border: 1px solid {_C['border']};
    border-radius: {_RADIUS_CONTROL}px;
    padding: 5px 8px;
    color: {_C['text_primary']};
    selection-background-color: {_C['accent']};
}}
QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover, QLineEdit:hover {{
    border: 1px solid {_C['accent']};
}}
QComboBox::drop-down {{
    border: none;
    width: 22px;
}}
QComboBox QAbstractItemView {{
    background: {_C['surface_2']};
    border: 1px solid {_C['border']};
    color: {_C['text_primary']};
    selection-background-color: {_C['accent']};
    selection-color: {_C['surface_0']};
    outline: none;
}}

/* --- Checkboxes --- */
QCheckBox {{
    spacing: 8px;
    color: {_C['text_primary']};
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {_C['border']};
    border-radius: 4px;
    background: {_C['surface_2']};
}}
QCheckBox::indicator:checked {{
    background: {_C['accent']};
    border: 1px solid {_C['accent']};
}}

/* --- Sliders --- */
QSlider::groove:horizontal {{
    height: 4px;
    background: {_C['surface_3']};
    border-radius: 2px;
}}
QSlider::sub-page:horizontal {{
    background: {_C['accent']};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
    background: {_C['accent']};
    border: 2px solid {_C['surface_0']};
}}
QSlider::handle:horizontal:hover {{
    background: {_ACCENT_HOVER};
}}

/* --- Plain buttons (Default / Skin default / Remove / Add…) --- */
QPushButton {{
    background: {_C['surface_2']};
    border: 1px solid {_C['border']};
    border-radius: {_RADIUS_CONTROL}px;
    padding: 6px 14px;
    color: {_C['text_primary']};
}}
QPushButton:hover {{
    background: {_SURFACE_HOVER};
    border: 1px solid {_C['accent']};
}}
QPushButton:pressed {{
    background: {_C['surface_1']};
}}
QPushButton:disabled {{
    color: {_C['text_secondary']};
}}

/* --- OK / Cancel, tagged by style_dialog_buttons() --- */
QPushButton#primaryButton {{
    background: {_C['accent']};
    border: 1px solid {_C['accent']};
    color: {_C['surface_0']};
    font-weight: 600;
}}
QPushButton#primaryButton:hover {{
    background: {_ACCENT_HOVER};
}}
QPushButton#primaryButton:pressed {{
    background: {_ACCENT_PRESSED};
}}
QPushButton#secondaryButton {{
    background: transparent;
}}
QPushButton#secondaryButton:hover {{
    background: {_C['surface_2']};
}}

/* --- Tables (Report dialog) --- */
QTableWidget {{
    background: {_C['surface_1']};
    border: 1px solid {_C['border']};
    border-radius: {_RADIUS_CARD}px;
    gridline-color: {_C['border']};
    color: {_C['text_primary']};
    selection-background-color: {_C['accent']};
    selection-color: {_C['surface_0']};
}}
QHeaderView::section {{
    background: {_C['surface_2']};
    color: {_C['text_secondary']};
    border: none;
    border-bottom: 1px solid {_C['border']};
    padding: 6px 8px;
    font-weight: 600;
}}

/* --- Scroll areas: no seam between panel and dialog background --- */
QScrollArea {{
    background: transparent;
    border: none;
}}
QScrollArea > QWidget > QWidget {{
    background: transparent;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {_C['surface_3']};
    border-radius: 5px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {_C['accent']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
"""


def apply_theme(widget: QWidget) -> None:
    """Apply the shared dark theme to `widget` and its whole subtree
    (QSS cascades to every descendant of the widget it's set on)."""
    widget.setStyleSheet(_QSS)


def style_dialog_buttons(box: QDialogButtonBox) -> None:
    """Tag the OK button as the primary (solid accent) action and
    every other standard button as secondary (quiet outline) — QSS
    alone cannot select "the OK button" out of a QDialogButtonBox by
    role, so this names them for the shared stylesheet."""
    ok = box.button(QDialogButtonBox.StandardButton.Ok)
    if ok is not None:
        ok.setObjectName("primaryButton")
    for button in box.buttons():
        if button is not ok:
            button.setObjectName("secondaryButton")
