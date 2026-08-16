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

from app import rebuild
from app.settings_store import slot_layout_target
from app.watch_face import theme_tree, theme_variants
from app.ui_style import tooltip_wrap
from app.watch_face import theme_thumbs, thumbs
from app.watch_face.controls import picture_group
from app.watch_face.widgets import flow_row, pill
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


# ONE DOOR, not a private twin: this helper stood here and in
# `theme_tree.py` byte for byte, and both spelled a teardown that made a
# top-level window flash open mid-screen. The rule and the measurement
# live in `app.rebuild` — hide BEFORE unparenting.
_clear = rebuild.clear_layout


def build(settings, setters: dict, tr) -> QWidget:
    root = QVBoxLayout()
    # NO DEAD BAND BETWEEN GROUPS (runtime audit ALG-7, 2026-08-15):
    # the default inter-widget spacing plus each group's own top margin
    # left a full-width strip of bare background between the Theme
    # families card and the Subdial plate group — space bought with
    # nothing, which is precisely what the ladder's first step forbids.
    # The groups carry their own internal padding already, so the page
    # does not need to add a second gap on top of it.
    root.setSpacing(4)
    widget = QWidget()

    def rebuild() -> None:
        _clear(root)
        _populate(root, settings, setters, tr, rebuild)

    rebuild()
    widget.setLayout(root)
    return widget


def _populate(root, settings, setters, tr, rebuild) -> None:
    root.addWidget(_face_layout_row(settings, setters, tr))
    descriptors = setters["slot_descriptors"]()
    enabled = [d for d in descriptors if d.enabled_value]
    full_face = not enabled
    if _nav.active_slot not in {d.index for d in descriptors}:
        _nav.active_slot = descriptors[0].index
    active = next(d for d in descriptors if d.index == _nav.active_slot)
    slot_off = not active.enabled_value and not full_face
    # The Names switch rides the SLOT ROW's free tail instead of a row
    # of its own: a lone checkbox left a whole band mostly empty while
    # the galleries continued below it (ALG-7, real-font audit
    # 2026-08-09 — reflow before stacking into height).
    names = None
    if not slot_off:
        content_source = active if not full_face else descriptors[0]
        names = _names_checkbox(content_source, settings, setters, tr)
    root.addWidget(_slot_picker_row(descriptors, tr, rebuild, names))
    if slot_off:
        note = QLabel(tr("This Slot is off — Ctrl+N cycles the visible Slots."))
        note.setWordWrap(True)
        root.addWidget(note)
    else:
        # At FULL FACE every descriptor reads `enabled_value=False`, so
        # the content tree binds to descriptor 1's data regardless of
        # which medal is "active" (all three are grayed) — see
        # themes.md's Design Decisions.
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
    # THE VARIANT PANEL (verdicts 3A + 8A) takes the place the Artwork
    # group used to hold alone. Artwork was only ever ONE of the four
    # scattered "variant" mechanisms; the panel gathers all four — style,
    # metal, source, roster — and prints only the rows this theme can
    # actually offer. It sits directly under the content tree, because
    # what it varies is the theme the tree just picked.
    variants = theme_variants.build(active, settings, setters, tr)
    if variants is not None:                 # verdict 8A — see the builder
        root.addWidget(variants)
    root.addWidget(_subdial_plate_group(settings, setters, tr))
    root.addWidget(_subdial_set_group(settings, setters, tr))
    root.addWidget(_rotation_group(settings, setters, tr))


def _face_layout_row(settings, setters, tr) -> QWidget:
    current = slot_layout_target(settings)
    return flow_row(
        pill(
            tr(title), current == target,
            lambda t=target: setters["slot_layout"](t),
        )
        for target, title in enumerate(_FACE_LAYOUT_TITLES)
    )


def _slot_picker_row(descriptors, tr, rebuild, names=None) -> QWidget:
    members = []
    for descriptor in descriptors:
        button = QPushButton(f"{_MEDALS[descriptor.index]} {tr(descriptor.title)}")
        button.setCheckable(True)
        button.setChecked(descriptor.index == _nav.active_slot)
        button.setEnabled(descriptor.enabled_value)
        if not descriptor.enabled_value:
            button.setToolTip(tooltip_wrap(tr(
                "This Slot is off — Ctrl+N cycles the visible Slots."
            )))
        button.clicked.connect(
            lambda checked=False, i=descriptor.index: _select_slot(i, rebuild)
        )
        members.append(button)
    if names is not None:
        # The Names switch still rides this row's free tail (ALG-7,
        # 2026-08-09) — it now WRAPS with it instead of being cut.
        members.append(names)
    return flow_row(members)


def _select_slot(index: int, rebuild) -> None:
    _nav.active_slot = index
    rebuild()


def _names_checkbox(active, settings, setters, tr) -> QCheckBox:
    """THE UNIFIED NAMES SWITCH (owner review 2026-08-09): one Names
    checkbox now speaks for BOTH rosters that can carry a name — the
    day name on the weekday bodies (the slot's own `set_names`, as
    before) AND the figure name on the archetype wheel
    (`archetype_names`, previously reachable only through the classic
    right-click menu). The two stored keys stay separate — the menu's
    per-key toggles still work — this switch simply sets both."""
    checkbox = QCheckBox(tr("Names"))
    checkbox.setChecked(active.names_value or settings.archetype_names)

    def apply(checked: bool) -> None:
        active.set_names(checked)
        setters["archetype_names"](checked)

    checkbox.setToolTip(tooltip_wrap(tr(
        "The day name written on the weekday bodies — and the figure "
        "name on the archetype wheel, when a pointer archetype is on."
    )))
    checkbox.toggled.connect(apply)
    return checkbox


def _calendar_mount_group(settings, setters, tr) -> QWidget:
    """The Calendar mount gallery — `build_calendar_mount_grid` is the
    SAME gallery the retired Pointer Theme window built (Rule #5, no
    second copy). The extra QGroupBox this used to wrap it in fell away
    with the CardGroup migration (2026-08-14): the gallery carries its
    own title and sentence now, and a box around a box reads as a
    defect."""
    return build_calendar_mount_grid(
        settings.calendar_mount, setters["calendar_mount"], tr,
    )


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


def _subdial_set_group(settings, setters, tr) -> QGroupBox:
    """The SUBDIAL PLATE SET pick (owner decree 2026-07-21, Rsub round,
    ported verbatim from
    `app.settings_dialog.themes_section._build_subdial_set_group`,
    Phase 6 FINAL cleanup) — NOT the same setting as the Subdial plate
    pills above (`subdial_style`, theme/black background): this picks
    WHICH of the five hand-picked plate looks draws (`settings.
    subdial_set`); the active jewel finish still decides which color
    draws within it."""
    return picture_group(
        tr("Subdial plate set"),
        tr("Which hand-picked plate look the subdials wear — the active "
           "jewel finish still decides which metal draws within it."),
        [
            (
                name, tr(constants.SUBDIAL_SET_TITLES[name]),
                tr("The {name} subdial plates.").format(
                    name=constants.SUBDIAL_SET_TITLES[name]
                ),
                theme_thumbs.subdial_set_icon(name),
            )
            for name in constants.SUBDIAL_SETS
        ],
        settings.subdial_set, setters["subdial_set"],
    )


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
    # VERDICT 5E (2026-08-15): the per-theme METAL combos are GONE from
    # here. They never belonged: a setting reachable only while its
    # theme happened to be in the rotation is a setting hidden behind an
    # unrelated choice, which is exactly what the owner reported. They
    # live in the Variant panel above now, beside the theme they vary,
    # and this group keeps only what rotation actually is — which themes
    # rotate, how often, and whether the ring colour drives the metal.
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


