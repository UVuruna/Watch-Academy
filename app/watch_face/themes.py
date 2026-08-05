"""Themes & Slots section (R-17/R-18/R-19/R-20, Phase 6 FINAL cleanup,
see themes.md) — the Watch Face window's FACE LAYOUT row, SLOT PICKER,
the content tree (delegated to `theme_tree.py`), the subdial plate
pills, the Artwork/Subdial-set picks and the theme rotation controls
(the interval pair PLUS, since Phase 6, the rotation GROUP picker and
the per-theme metal combos — R-20 had deferred those two to "the old
Settings copy until Phase 6"; Phase 6 retires that copy, so they move
here verbatim instead of being dropped).
"""

from dataclasses import dataclass

from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QVBoxLayout, QWidget,
)

from app.settings_store import slot_layout_target
from app.watch_face import theme_tree
from app.watch_face.widgets import pill
from app.weekday_theme_grid import build_calendar_mount_grid
from config import constants, pantheon

_MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}
_FACE_LAYOUT_TITLES = ("Full face", "1 subdial", "2 subdials", "3 subdials")


@dataclass
class _Nav:
    """Which slot's medal is selected — module-level for the SAME
    reason `theme_tree._nav` is (see themes.md Design Decisions): a
    medal click is pure navigation, never a setter, so it survives the
    window's live-apply rebuild without living on a widget instance
    that rebuild discards."""

    active_slot: int = 1


_nav = _Nav()


def reset_navigation() -> None:
    """Test-only reset — production code never calls this."""
    global _nav
    _nav = _Nav()


def _clear(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        elif item.layout() is not None:
            _clear(item.layout())


def build(settings, setters: dict, tr) -> QWidget:
    root = QVBoxLayout()
    widget = QWidget()

    def rebuild() -> None:
        _clear(root)
        _populate(root, settings, setters, tr, rebuild)

    rebuild()
    widget.setLayout(root)
    return widget


def _populate(root, settings, setters, tr, rebuild) -> None:
    root.addLayout(_face_layout_row(settings, setters, tr))
    descriptors = setters["slot_descriptors"]()
    enabled = [d for d in descriptors if d.enabled_value]
    full_face = not enabled
    if _nav.active_slot not in {d.index for d in descriptors}:
        _nav.active_slot = descriptors[0].index
    active = next(d for d in descriptors if d.index == _nav.active_slot)
    root.addLayout(_slot_picker_row(descriptors, tr, rebuild))
    if not active.enabled_value and not full_face:
        note = QLabel(tr("This Slot is off — Ctrl+N cycles the visible Slots."))
        note.setWordWrap(True)
        root.addWidget(note)
    else:
        # At FULL FACE every descriptor reads `enabled_value=False`, so
        # the content tree binds to descriptor 1's data regardless of
        # which medal is "active" (all three are grayed) — see
        # themes.md's Design Decisions.
        content_source = active if not full_face else descriptors[0]
        root.addWidget(_names_checkbox(content_source, tr))
        root.addWidget(theme_tree.build(
            content_source, full_face, settings.pointer,
            settings.pointer_shape, tr,
        ))
    if settings.pointer == "calendar":
        # THE CALENDAR MOUNT (owner decree 2026-07-29, ported from the
        # retired Pointer Theme window's second tab, Phase 6 FINAL
        # cleanup): WHICH roster rides the twelve wedges — only the
        # Calendar pointer has wedges to mount one on.
        root.addWidget(_calendar_mount_group(settings, setters, tr))
    root.addWidget(_subdial_plate_group(settings, setters, tr))
    root.addWidget(_artwork_group(settings, setters, tr))
    root.addWidget(_subdial_set_group(settings, setters, tr))
    root.addWidget(_rotation_group(settings, setters, tr))


def _face_layout_row(settings, setters, tr) -> QHBoxLayout:
    row = QHBoxLayout()
    current = slot_layout_target(settings)
    for target, title in enumerate(_FACE_LAYOUT_TITLES):
        row.addWidget(pill(
            tr(title), current == target,
            lambda t=target: setters["slot_layout"](t),
        ))
    return row


def _slot_picker_row(descriptors, tr, rebuild) -> QHBoxLayout:
    row = QHBoxLayout()
    for descriptor in descriptors:
        button = QPushButton(f"{_MEDALS[descriptor.index]} {tr(descriptor.title)}")
        button.setCheckable(True)
        button.setChecked(descriptor.index == _nav.active_slot)
        button.setEnabled(descriptor.enabled_value)
        if not descriptor.enabled_value:
            button.setToolTip(tr(
                "This Slot is off — Ctrl+N cycles the visible Slots."
            ))
        button.clicked.connect(
            lambda checked=False, i=descriptor.index: _select_slot(i, rebuild)
        )
        row.addWidget(button)
    return row


def _select_slot(index: int, rebuild) -> None:
    _nav.active_slot = index
    rebuild()


def _names_checkbox(active, tr) -> QCheckBox:
    checkbox = QCheckBox(tr("Names"))
    checkbox.setChecked(active.names_value)
    checkbox.setToolTip(tr("The day name written on the weekday bodies."))
    checkbox.toggled.connect(active.set_names)
    return checkbox


def _calendar_mount_group(settings, setters, tr) -> QGroupBox:
    """The Calendar mount gallery, wrapped in its own group box —
    `build_calendar_mount_grid` is the SAME gallery the retired Pointer
    Theme window built (Rule #5, no second copy)."""
    group = QGroupBox(tr("Calendar mount"))
    layout = QVBoxLayout(group)
    layout.addWidget(build_calendar_mount_grid(
        settings.calendar_mount, setters["calendar_mount"], tr,
    ))
    return group


def _subdial_plate_group(settings, setters, tr) -> QGroupBox:
    """R-20: moved from `design_window.DesignDialog._complications_tab`
    — `settings.subdial_style` unchanged."""
    group = QGroupBox(tr("Subdial plate"))
    row = QHBoxLayout(group)
    for style, title in (
        ("theme", "Theme background"), ("black", "Classic black"),
    ):
        row.addWidget(pill(
            tr(title), settings.subdial_style == style,
            lambda s=style: setters["subdial_style"](s),
        ))
    return group


def _artwork_group(settings, setters, tr) -> QGroupBox:
    """The ART SOURCE pick (owner 2026-07-14, ported verbatim from
    `app.settings_dialog.themes_section._build_artwork_group`, Phase 6
    FINAL cleanup): the Gemini and ChatGPT generations coexist — one
    combo switches every plate, emblem and badge; files missing in the
    chosen source fall back to the other. LIVE-APPLY here (the old
    Settings copy only ever applied it on OK)."""
    group = QGroupBox(tr("Artwork"))
    row = QHBoxLayout(group)
    combo = QComboBox()
    for source in constants.ART_SOURCES:
        combo.addItem(constants.ART_SOURCE_TITLES[source], source)
    index = combo.findData(settings.art_source)
    if index >= 0:
        combo.setCurrentIndex(index)
    combo.currentIndexChanged.connect(
        lambda _i: setters["art_source"](combo.currentData())
    )
    row.addWidget(combo)
    row.addStretch(1)
    return group


def _subdial_set_group(settings, setters, tr) -> QGroupBox:
    """The SUBDIAL PLATE SET pick (owner decree 2026-07-21, Rsub round,
    ported verbatim from
    `app.settings_dialog.themes_section._build_subdial_set_group`,
    Phase 6 FINAL cleanup) — NOT the same setting as the Subdial plate
    pills above (`subdial_style`, theme/black background): this picks
    WHICH of the five hand-picked plate looks draws (`settings.
    subdial_set`); the active letter finish still decides which color
    draws within it."""
    group = QGroupBox(tr("Subdial plate set"))
    row = QHBoxLayout(group)
    combo = QComboBox()
    for name in constants.SUBDIAL_SETS:
        combo.addItem(tr(constants.SUBDIAL_SET_TITLES[name]), name)
    index = combo.findData(settings.subdial_set)
    if index >= 0:
        combo.setCurrentIndex(index)
    combo.currentIndexChanged.connect(
        lambda _i: setters["subdial_set"](combo.currentData())
    )
    row.addWidget(combo)
    row.addStretch(1)
    return group


def _rotation_selection(group_key: str, custom_themes: tuple) -> tuple:
    """The themes the CURRENT rotation pick would rotate (ported
    verbatim from
    `app.settings_dialog.themes_section._SectionMixin._rotation_
    selection`, Phase 6 FINAL cleanup)."""
    if group_key == "custom":
        return custom_themes
    for title, keys in pantheon.WEEKDAY_MENU_GROUPS:
        if title == group_key:
            return keys
    return ()


def _rotation_group(settings, setters, tr) -> QGroupBox:
    """Cycle the CHECKED weekday themes every N minutes/hours instead
    of wearing one forever. R-20 shipped the interval + follow-ring
    pair alone (`theme_rotation_minutes`/`theme_metal_follow_ring`);
    Phase 6 FINAL cleanup adds the rotation GROUP picker (None / one
    kinship family / Custom) and the per-theme metal combos, ported
    verbatim from `app.settings_dialog.themes_section.
    _build_theme_rotation_group` — LIVE-APPLY here instead of the old
    copy's on-OK commit."""
    group = QGroupBox(tr("Theme rotation"))
    layout = QVBoxLayout(group)
    group_combo = QComboBox()
    group_combo.addItem(tr("None"), "none")
    for title, _keys in pantheon.WEEKDAY_MENU_GROUPS:
        group_combo.addItem(tr(title), title)
    group_combo.addItem(tr("Custom"), "custom")
    index = group_combo.findData(settings.theme_rotation_group)
    if index >= 0:
        group_combo.setCurrentIndex(index)
    group_combo.currentIndexChanged.connect(
        lambda _i: setters["theme_rotation_group"](group_combo.currentData())
    )
    layout.addWidget(group_combo)
    if settings.theme_rotation_group == "custom":
        grid = QGridLayout()
        grid.setHorizontalSpacing(24)
        for index, (key, label) in enumerate(
            pantheon.WEEKDAY_THEME_TITLES.items()
        ):
            box = QCheckBox(tr(label))
            box.setChecked(key in settings.theme_rotation_themes)
            box.toggled.connect(
                lambda checked, k=key: setters["theme_rotation_themes"](
                    tuple(sorted(
                        (set(settings.theme_rotation_themes) | {k})
                        if checked
                        else (set(settings.theme_rotation_themes) - {k})
                    ))
                )
            )
            grid.addWidget(box, index // 4, index % 4)
        layout.addLayout(grid)
    selected = set(_rotation_selection(
        settings.theme_rotation_group, settings.theme_rotation_themes
    ))
    metal_row = QHBoxLayout()
    for theme in constants.METAL_THEMES:
        if theme not in pantheon.WEEKDAY_THEME_TITLES or theme not in selected:
            continue
        metal_row.addWidget(QLabel(tr(pantheon.WEEKDAY_THEME_TITLES[theme])))
        combo = QComboBox()
        for metal in constants.theme_metals(theme):
            combo.addItem(tr(metal.capitalize()), metal)
        combo.setCurrentIndex(
            combo.findData(settings.theme_metals.get(theme, "colored"))
        )
        combo.setEnabled(not settings.theme_metal_follow_ring)
        combo.currentIndexChanged.connect(
            lambda _i, c=combo, t=theme: setters["theme_metal"](
                t, c.currentData()
            )
        )
        metal_row.addWidget(combo)
    metal_row.addStretch(1)
    layout.addLayout(metal_row)
    row = QHBoxLayout()
    row.addWidget(QLabel(tr("Every")))
    minutes = settings.theme_rotation_minutes
    amount = QSpinBox()
    amount.setRange(1, 999)
    unit = QComboBox()
    unit.addItem(tr("minutes"), 1)
    unit.addItem(tr("hours"), 60)
    if minutes % 60 == 0:
        amount.setValue(minutes // 60)
        unit.setCurrentIndex(1)
    else:
        amount.setValue(minutes)

    def apply_interval() -> None:
        factor = unit.currentData()
        setters["theme_rotation_minutes"](amount.value() * factor)

    amount.editingFinished.connect(apply_interval)
    unit.currentIndexChanged.connect(lambda _index: apply_interval())
    row.addWidget(amount)
    row.addWidget(unit)
    row.addStretch(1)
    layout.addLayout(row)
    follow_ring = QCheckBox(tr("Follow ring color"))
    follow_ring.setChecked(settings.theme_metal_follow_ring)
    follow_ring.toggled.connect(setters["theme_metal_follow_ring"])
    layout.addWidget(follow_ring)
    return group
