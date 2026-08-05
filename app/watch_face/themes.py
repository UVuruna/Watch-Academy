"""Themes & Slots section (R-17/R-18/R-19/R-20, see themes.md) — the
Watch Face window's FACE LAYOUT row, SLOT PICKER, the content tree
(delegated to `theme_tree.py`), the subdial plate pills and the theme
rotation controls.
"""

from dataclasses import dataclass

from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QGroupBox, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QVBoxLayout, QWidget,
)

from app.settings_store import slot_layout_target
from app.watch_face import theme_tree
from app.watch_face.widgets import pill

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
    root.addWidget(_subdial_plate_group(settings, setters, tr))
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


def _rotation_group(settings, setters, tr) -> QGroupBox:
    """R-20: the interval + follow-ring pair only, moved from
    `app.settings_dialog.themes_section._build_theme_rotation_group`
    (same `theme_rotation_minutes`/`theme_metal_follow_ring` keys) —
    the rotation GROUP picker and the per-theme metal combos stay in
    the old Settings copy until Phase 6."""
    group = QGroupBox(tr("Theme rotation"))
    layout = QVBoxLayout(group)
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
