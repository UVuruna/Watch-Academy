"""The Design mini window — R5 MENU REWORK item 3D: replaces the old
Design submenu's deep chain (Pointer / Ring / Umbra / Complications /
Hands / Earth / Size) with one tabbed window, images where real preview
art exists (see design_window.md's asset-honesty note for what does
not).
"""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.theme import apply_theme, size_to_screen
from app.ui_style import style_button
from config import constants, defaults, paths
from config.ui_text import ui
from data.hands import hand_packs
from data.rings import ring_presets


def _clear(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        elif item.layout() is not None:
            _clear(item.layout())


class DesignDialog(QDialog):
    """Non-modal, LIVE-APPLY (see design_window.md): every tab's pick
    calls its setter immediately — there is nothing to commit, so no
    OK/Cancel."""

    def __init__(
        self, settings, setters: dict, overlay: dict | None = None,
        stay_on_top: bool = False, parent=None,
    ):
        super().__init__(parent)
        self._tr = lambda text: ui(overlay or {}, text)  # noqa: E731
        self.setWindowTitle(f"{constants.APP_NAME} — {self._tr('Design')}")
        if stay_on_top:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self._settings = settings
        self._setters = setters
        self._layout = QVBoxLayout(self)
        self._host = QVBoxLayout()
        self._layout.addLayout(self._host)
        self._tabs: QTabWidget | None = None
        apply_theme(self)
        self._build()
        size_to_screen(self, 1, 1, defaults.DIALOG_SQUARE_HEIGHT_FRACTION)

    def refresh(self, settings, setters: dict) -> None:
        """Re-supplies the live settings after a pick applies (owner
        spec: a live picker, not a transactional dialog) — called by
        the controller."""
        self._settings = settings
        self._setters = setters
        self._build()

    def _build(self) -> None:
        # KEEP THE OPEN TAB across live-pick rebuilds (owner fix
        # 2026-07-26: changing a value on any tab other than Pointer
        # bounced the window back to the FIRST tab — every pick routes
        # through the controller's refresh(), which rebuilds this
        # QTabWidget from scratch, and a fresh QTabWidget always opens
        # at index 0).
        previous = self._tabs.currentIndex() if self._tabs is not None else 0
        _clear(self._host)
        tabs = QTabWidget()
        tabs.addTab(self._pointer_tab(), self._tr("Pointer"))
        tabs.addTab(self._ring_tab(), self._tr("Ring"))
        tabs.addTab(self._umbra_tab(), self._tr("Umbra"))
        tabs.addTab(self._complications_tab(), self._tr("Complications"))
        tabs.addTab(self._hands_tab(), self._tr("Hands"))
        tabs.addTab(self._earth_tab(), self._tr("Earth"))
        tabs.addTab(self._size_tab(), self._tr("Size"))
        tabs.setCurrentIndex(max(0, min(previous, tabs.count() - 1)))
        self._host.addWidget(tabs)
        self._tabs = tabs

    # --- Shared tile/pill builders -----------------------------------------

    def _pill(self, label: str, checked: bool, on_click) -> QPushButton:
        button = QPushButton(label)
        style_button(button, "next" if checked else "neutral", small=True)
        button.clicked.connect(lambda checked=False: on_click())
        return button

    def _tile(
        self, label: str, icon_path: Path | None, checked: bool, on_click,
    ) -> QToolButton:
        button = QToolButton()
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        button.setText(label)
        if icon_path is not None and Path(icon_path).exists():
            button.setIcon(QIcon(str(icon_path)))
        if checked:
            button.setStyleSheet(
                f"border: 2px solid {defaults.THEME_COLORS['accent']};"
                "border-radius: 8px;"
            )
        button.clicked.connect(lambda checked=False: on_click())
        return button

    # --- Tabs -----------------------------------------------------------------

    def _pointer_tab(self) -> QWidget:
        settings = self._settings
        layout = QVBoxLayout()
        grid = QGridLayout()
        # EVERY pointer names its own count, and the count is what the
        # reader sees on the glass, not the palette size (owner
        # 2026-07-28: the Rose shows 24, the Calendar 12). One ascending
        # row, 3 → 24, so the pills read as a scale.
        variants = sorted(
            constants.POINTER_DIAL_COUNTS.items(), key=lambda item: item[1]
        )
        for index, (variant, count) in enumerate(variants):
            title = f"{constants.POINTER_DISPLAY_NAMES[variant]} ({count})"
            row, col = divmod(index, 3)
            grid.addWidget(
                self._pill(
                    self._tr(title), settings.pointer == variant,
                    lambda v=variant: self._setters["pointer"](v),
                ),
                row, col,
            )
        layout.addLayout(grid)
        labels = constants.POINTER_PALETTE_LABELS.get(
            settings.pointer, constants.POINTER_PALETTE_LABELS["default"]
        )
        # The wheel row (owner seal 2026-07-26, CUBE.md): the Cube
        # pointers carry a THIRD pill — Genesis / Council / Character —
        # `palette_styles_for` names which styles this pointer serves.
        style_row = QHBoxLayout()
        for style, label in zip(
            constants.palette_styles_for(settings.pointer), labels
        ):
            style_row.addWidget(self._pill(
                self._tr(label), settings.palette_style == style,
                lambda s=style: self._setters["palette_style"](s),
            ))
        layout.addLayout(style_row)
        if settings.pointer == "calendar":
            lighting_row = QHBoxLayout()
            for mode, title in (
                ("hour", "Light the hour (shichen)"),
                ("year", "Light the month/sign"),
            ):
                lighting_row.addWidget(self._pill(
                    self._tr(title), settings.calendar_lighting == mode,
                    lambda m=mode: self._setters["calendar_lighting"](m),
                ))
            layout.addLayout(lighting_row)
            # THE 12-SET MOUNT (DESIGN ZODIAC law, R9a round): twelve
            # marks at CALENDAR_MOUNT_RADIUS_FRACTION — the Calendar
            # pointer's OWN options row, right beside its lighting mode
            # (owner spec: "put it where the Calendar pointer's own
            # options already live").
            mount_row = QHBoxLayout()
            for mode, title in (
                ("off", "No 12-set mount"),
                ("zodiac", "Mount zodiac signs"),
                ("months", "Mount Slavic months"),
                ("chinese", "Mount Chinese zodiac"),
            ):
                mount_row.addWidget(self._pill(
                    self._tr(title), settings.calendar_mount == mode,
                    lambda m=mode: self._setters["calendar_mount"](m),
                ))
            layout.addLayout(mount_row)
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def _ring_tab(self) -> QWidget:
        settings = self._settings
        layout = QVBoxLayout()
        grid = QGridLayout()
        presets = ring_presets(settings.custom_rings)
        for index, name in enumerate(sorted(presets)):
            card = presets[name]
            face = constants.RING_LAYOUTS[card["layout"]]["face"]
            icon = paths.art_file(defaults.RING_FACE_DIR / face)
            row, col = divmod(index, 4)
            grid.addWidget(
                self._tile(
                    self._tr(name), icon, settings.ring == name,
                    lambda n=name: self._setters["ring"](n),
                ),
                row, col,
            )
        layout.addLayout(grid)
        finish_row = QHBoxLayout()
        for finish in constants.RING_FINISHES:
            finish_row.addWidget(self._pill(
                self._tr(f"{finish.capitalize()} letters"),
                settings.ring_finish == finish,
                lambda f=finish: self._setters["ring_finish"](f),
            ))
        layout.addLayout(finish_row)
        active_card = presets[settings.ring]
        card_layout = constants.RING_LAYOUTS[active_card["layout"]]
        if active_card["triangle"] is not None or card_layout["triangle"]:
            # The SAME resolution `app.controller._ring_two_metals` uses
            # (Rule #5's intent honored without a controller->window
            # import, which would create a cycle) — the stored per-preset
            # choice, else the owner's documented per-preset default,
            # else the layout's own nature (ENLARGE/THEMATIC round,
            # owner 2026-07-27: flame/chalice presets — DOMY/PILOT —
            # are eligible too now, default ON).
            two_metals = settings.ring_two_metals.get(
                settings.ring,
                constants.RING_TWO_METALS_DEFAULT.get(
                    settings.ring, bool(card_layout["triangle"])
                ),
            )
            checkbox = QCheckBox(self._tr("Two metals"))
            checkbox.setChecked(two_metals)
            checkbox.toggled.connect(self._setters["ring_two_metals"])
            layout.addWidget(checkbox)
        if constants.RING_EYE_GLYPH in active_card["letters"]:
            # The Eye's rays (DOLLAR/EYE round, owner decree 2026-07-27)
            # — same per-preset resolution as "Two metals" above
            # (`app.controller._ring_eye_shine`); only presets seating
            # the ADAPTIVE eye glyph show the toggle, a custom ring's
            # explicit eye variant has its rays baked in.
            shine = settings.ring_eye_shine.get(
                settings.ring,
                constants.RING_EYE_SHINE_DEFAULT.get(settings.ring, False),
            )
            shine_box = QCheckBox(self._tr("Shine"))
            shine_box.setChecked(shine)
            shine_box.toggled.connect(self._setters["ring_eye_shine"])
            layout.addWidget(shine_box)
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def _umbra_tab(self) -> QWidget:
        settings = self._settings
        layout = QVBoxLayout()
        form_row = QHBoxLayout()
        for form, title in (
            ("fine", "Fine (16 shades)"), ("coarse", "Coarse (13 shades)"),
            ("gradient", "Gradient"),
        ):
            form_row.addWidget(self._pill(
                self._tr(title), settings.umbra_form == form,
                lambda f=form: self._setters["umbra_form"](f),
            ))
        layout.addLayout(form_row)
        contrast_row = QHBoxLayout()
        for variant in constants.UMBRA_CONTRAST_VARIANTS:
            contrast_row.addWidget(self._pill(
                self._tr(f"{variant.capitalize()} contrast"),
                settings.umbra_contrast == variant,
                lambda v=variant: self._setters["umbra_contrast"](v),
            ))
        layout.addLayout(contrast_row)
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def _complications_tab(self) -> QWidget:
        settings = self._settings
        layout = QHBoxLayout()
        for style, title in (
            ("theme", "Theme background"), ("black", "Classic black"),
        ):
            layout.addWidget(self._pill(
                self._tr(title), settings.subdial_style == style,
                lambda s=style: self._setters["subdial_style"](s),
            ))
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def _hands_tab(self) -> QWidget:
        settings = self._settings
        grid = QGridLayout()
        packs = hand_packs()
        for index, name in enumerate(sorted(packs)):
            icon = paths.art_file(packs[name]["files"]["hours"])
            row, col = divmod(index, 4)
            grid.addWidget(
                self._tile(
                    self._tr(name), icon, settings.hands == name,
                    lambda n=name: self._setters["hands"](n),
                ),
                row, col,
            )
        widget = QWidget()
        widget.setLayout(grid)
        return widget

    def _earth_tab(self) -> QWidget:
        settings = self._settings
        layout = QVBoxLayout()
        style_row = QHBoxLayout()
        for style, title in (("clean", "Clean"), ("atmo", "Atmosphere")):
            icon = paths.art_file(
                defaults.EARTH_ART_DIR / f"earth_{style}_europe_day.png"
            )
            style_row.addWidget(self._tile(
                self._tr(title), icon, settings.earth_style == style,
                lambda s=style: self._setters["earth_style"](s),
            ))
        layout.addLayout(style_row)
        label_row = QHBoxLayout()
        enabled = settings.diameter >= defaults.FULL_TEXT_MIN_DIAMETER
        for mode, title in (
            ("date", "Date"), ("weekday", "Weekday"),
            ("date_weekday", "Date & Weekday"), ("full", "Full Date"),
        ):
            is_active = settings.earth_label == mode
            button = self._pill(
                self._tr(title), is_active,
                lambda m=mode, was=is_active:
                self._setters["earth_label"](m, not was),
            )
            button.setEnabled(enabled)
            label_row.addWidget(button)
        layout.addLayout(label_row)
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def _size_tab(self) -> QWidget:
        settings = self._settings
        layout = QVBoxLayout()
        preset_row = QHBoxLayout()
        for preset in defaults.SIZE_PRESETS:
            preset_row.addWidget(self._pill(
                f"{preset} px", settings.diameter == preset,
                lambda p=preset: self._setters["diameter"](p),
            ))
        layout.addLayout(preset_row)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(defaults.SIZE_PRESETS[0], defaults.SIZE_PRESETS[-1])
        slider.setSingleStep(defaults.MENU_SIZE_SLIDER_STEP)
        slider.setPageStep(defaults.MENU_SIZE_SLIDER_STEP * 5)
        slider.setValue(settings.diameter)
        value_label = QLabel(f"{settings.diameter} px")
        slider.valueChanged.connect(
            lambda value, label=value_label: label.setText(f"{value} px")
        )
        slider.sliderReleased.connect(
            lambda: self._setters["diameter"](slider.value())
        )
        slider_row = QHBoxLayout()
        slider_row.addWidget(slider)
        slider_row.addWidget(value_label)
        layout.addLayout(slider_row)
        widget = QWidget()
        widget.setLayout(layout)
        return widget
