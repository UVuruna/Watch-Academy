"""The Slot Theme mini window — R5 MENU REWORK item 3C: replaces the
three old 1st/2nd/3rd Slot submenu chains with one window, three medal
icons picking which slot is being edited.
"""

from dataclasses import dataclass
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.theme import apply_theme, size_to_screen
from app.ui_style import style_button
from app.weekday_theme_grid import build_weekday_theme_grid
from config import constants, defaults
from config.ui_text import ui

_MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}
_ZODIAC_STYLES = constants.ZODIAC_SLOT_STYLES + ("text",)
_CHINESE_STYLES = constants.CHINESE_SLOT_STYLES + ("text",)


@dataclass
class SlotDescriptor:
    """One slot's full config + its OWN setter callables — the SAME
    shape the old `build_slot_menu` closure held (Rule #5), now handed
    across a module boundary instead of staying local."""

    index: int
    title: str
    mode_value: str
    style_value: str
    theme_value: str
    roster_value: str
    names_value: bool
    enabled_value: bool
    set_mode: Callable[[str], None]
    set_style_mode: Callable[[str, str], None]
    set_weekday: Callable[..., None]
    set_names: Callable[[bool], None]


def _clear(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        elif item.layout() is not None:
            _clear(item.layout())


class SlotThemeDialog(QDialog):
    """Non-modal, LIVE-APPLY (see slot_theme.md): every pick calls its
    descriptor's setter immediately — there is nothing to commit, so no
    OK/Cancel."""

    def __init__(
        self, descriptors: tuple, overlay: dict | None = None,
        stay_on_top: bool = False, parent=None,
    ):
        super().__init__(parent)
        self._tr = lambda text: ui(overlay or {}, text)  # noqa: E731
        self.setWindowTitle(
            f"{constants.APP_NAME} — {self._tr('Slot Theme')}"
        )
        if stay_on_top:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self._descriptors = descriptors
        self._active_index = next(
            (d.index for d in descriptors if d.enabled_value), 1
        )
        layout = QVBoxLayout(self)
        self._gate_label = QLabel()
        self._gate_label.setWordWrap(True)
        self._gate_label.setStyleSheet(
            f"color: {defaults.TIME_TRAVEL_WARNING_COLOR};"
        )
        self._gate_label.hide()
        layout.addWidget(self._gate_label)
        self._icon_row = QHBoxLayout()
        layout.addLayout(self._icon_row)
        self._content_host = QVBoxLayout()
        layout.addLayout(self._content_host)
        apply_theme(self)
        self._build()
        size_to_screen(self, 1, 1, defaults.DIALOG_SQUARE_HEIGHT_FRACTION)

    # --- Rebuild ------------------------------------------------------------

    def _descriptor(self, index: int) -> SlotDescriptor:
        return next(d for d in self._descriptors if d.index == index)

    def _select(self, index: int) -> None:
        self._active_index = index
        self._build()

    def _build(self) -> None:
        _clear(self._icon_row)
        for descriptor in self._descriptors:
            button = QPushButton(
                f"{_MEDALS[descriptor.index]} {self._tr(descriptor.title)}"
            )
            style_button(
                button,
                "next" if descriptor.index == self._active_index else "neutral",
                small=True,
            )
            button.setEnabled(descriptor.enabled_value)
            if not descriptor.enabled_value:
                button.setToolTip(self._tr(
                    "This Slot is off — Ctrl+N cycles the visible Slots."
                ))
            button.clicked.connect(
                lambda checked=False, i=descriptor.index: self._select(i)
            )
            self._icon_row.addWidget(button)
        _clear(self._content_host)
        active = self._descriptor(self._active_index)
        if not active.enabled_value:
            note = QLabel(self._tr(
                "This Slot is off — Ctrl+N cycles the visible Slots."
            ))
            note.setWordWrap(True)
            self._content_host.addWidget(note)
            return
        self._content_host.addWidget(self._build_tabs(active))

    def _build_tabs(self, active: SlotDescriptor) -> QTabWidget:
        tabs = QTabWidget()
        tabs.addTab(
            build_weekday_theme_grid(
                active.theme_value if active.mode_value == "weekday" else "",
                lambda theme, a=active: a.set_weekday(theme),
                self._tr,
            ),
            self._tr("Weekday"),
        )
        tabs.addTab(self._complications_tab(active), self._tr("Complications"))
        tabs.addTab(
            self._style_tab(active, "zodiac", _ZODIAC_STYLES),
            self._tr("Astrology"),
        )
        tabs.addTab(
            self._style_tab(active, "ascendant", _ZODIAC_STYLES),
            self._tr("Ascendant"),
        )
        tabs.addTab(
            self._style_tab(active, "chinese", _CHINESE_STYLES),
            self._tr("Chinese zodiac"),
        )
        names = QCheckBox(self._tr("Names"))
        names.setChecked(active.names_value)
        names.setToolTip(
            self._tr("The day name written on the weekday bodies.")
        )
        names.toggled.connect(active.set_names)
        wrapper = QWidget()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addWidget(tabs)
        wrapper_layout.addWidget(names)
        return wrapper

    def _pill(self, label: str, checked: bool, on_pick) -> QPushButton:
        button = QPushButton(label)
        style_button(button, "next" if checked else "neutral", small=True)
        button.clicked.connect(lambda checked=False: on_pick())
        return button

    def _complications_tab(self, active: SlotDescriptor) -> QWidget:
        grid = QGridLayout()
        for index, (mode, title) in enumerate(
            constants.SLOT_COMPLICATION_TITLES.items()
        ):
            row, col = divmod(index, 2)
            grid.addWidget(
                self._pill(
                    self._tr(title), active.mode_value == mode,
                    lambda m=mode, a=active: a.set_mode(m),
                ),
                row, col,
            )
        widget = QWidget()
        widget.setLayout(grid)
        return widget

    def _style_tab(
        self, active: SlotDescriptor, family: str, styles: tuple[str, ...],
    ) -> QWidget:
        grid = QGridLayout()
        for index, style in enumerate(styles):
            row, col = divmod(index, 3)
            checked = active.mode_value == family and active.style_value == style
            grid.addWidget(
                self._pill(
                    self._tr(style.capitalize()), checked,
                    lambda f=family, s=style, a=active: a.set_style_mode(f, s),
                ),
                row, col,
            )
        widget = QWidget()
        widget.setLayout(grid)
        return widget

    # --- Controller-facing API -----------------------------------------------

    def refresh(self, descriptors: tuple) -> None:
        """Re-supplies the triple after a pick applies (owner spec: a
        live picker, not a transactional dialog) — called by the
        controller."""
        self._descriptors = descriptors
        self._build()

    def set_gate(self, available: bool, reason: str) -> None:
        """Live gray-out while the window is already open and the LAST
        slot turns off underneath it — the primary gate is the
        top-level menu entry; this is the belt to that suspender. Reads
        each descriptor's OWN `enabled_value` (never a widget's current
        `isEnabled()`, which this method itself may have already
        flipped) so a later `set_gate(True, ...)` restores exactly the
        right icons instead of getting stuck disabled."""
        for descriptor, index in zip(
            self._descriptors, range(self._icon_row.count())
        ):
            widget = self._icon_row.itemAt(index).widget()
            if widget is not None:
                widget.setEnabled(available and descriptor.enabled_value)
        for index in range(self._content_host.count()):
            widget = self._content_host.itemAt(index).widget()
            if widget is not None:
                widget.setEnabled(available)
        self._gate_label.setText(reason)
        self._gate_label.setVisible(not available)
