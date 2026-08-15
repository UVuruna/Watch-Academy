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


def _clear(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            # UNPARENT, then delete. `deleteLater` alone leaves the
            # widget a visible child of the page until the event loop
            # gets around to it, and a widget no layout owns keeps its
            # old geometry — so the rebuilt rows were painted ON TOP of
            # the ones they replaced (caught on the live-profile audit
            # shot, 2026-08-14; it only became visible once the rows
            # were widgets rather than nested layouts).
            widget.setParent(None)
            widget.deleteLater()
        elif item.layout() is not None:
            _clear(item.layout())


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
    root.addWidget(_subdial_plate_group(settings, setters, tr))
    artwork = _artwork_group(settings, setters, tr)
    if artwork is not None:                  # verdict 8A — see the builder
        root.addWidget(artwork)
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


def _artwork_group(settings, setters, tr) -> QGroupBox | None:
    """The ART SOURCE pick — ONE card per source, each carrying that
    source's Sun plate AND (when the theme has one) its Sunday dual in
    the SAME image, exactly the way the Subdial plate set card carries
    three plates (owner order 2026-08-15).

    Returns None — and the caller prints NOTHING — when the theme has
    only one cast on disk. That is ballot verdict 8A applied to its
    first real case: Planets Photo has a single set of plates, so the
    group used to offer four cards that all resolved to the same
    picture. A row with nothing to choose is STRUCTURE, not state, so
    it is absent rather than greyed (a greyed row is for an option that
    exists but cannot be taken right now)."""
    theme = settings.weekday_theme
    sources = theme_thumbs.theme_art_sources(theme)
    if not sources:
        return None
    roster = settings.weekday_roster
    entries = []
    for source in sources:
        title = constants.ART_SOURCE_TITLES[source]
        entries.append((
            source, tr(title),
            tr("The {source} cast of this theme's plates — its Sunday "
               "dual included, when the theme carries one.").format(
                source=title
            ),
            theme_thumbs.art_source_icon(source, theme, roster),
        ))
    return picture_group(
        tr("Artwork"),
        tr("Which cast of plates the weekday bodies wear."),
        entries, settings.art_source, setters["art_source"],
    )


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
    # REFLOW, not one endless strip (Space & Legibility ladder step 2,
    # Zubi fix round 2026-08-09): with a whole kinship family selected
    # this row once asked ~5,600px of width in a 1280px window — every
    # label squeezed and clipped. A grid wraps label+combo pairs at
    # three per row; each label keeps its measured width.
    metal_grid = QGridLayout()
    metal_grid.setHorizontalSpacing(12)
    pairs_per_row = 3
    slot = 0
    for theme in constants.METAL_THEMES:
        if theme not in pantheon.WEEKDAY_THEME_TITLES or theme not in selected:
            continue
        combo = QComboBox()
        for metal in constants.theme_metals(theme):
            combo.addItem(tr(metal.capitalize()), metal)
        combo.setCurrentIndex(
            combo.findData(settings.theme_metals.get(theme, "colored"))
        )
        combo.setEnabled(not settings.theme_metal_follow_ring)
        # KNAP + COLORED (owner review 2026-08-09, slika 5): the combo
        # hugs its content and wears the SAME fill vocabulary the
        # Encyclopedia's look chips wear, keyed by the selection.
        combo.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToContents
        )
        _paint_metal_combo(combo)
        combo.currentIndexChanged.connect(
            lambda _i, c=combo, t=theme: (
                setters["theme_metal"](t, c.currentData()),
                _paint_metal_combo(c),
            )
        )
        row, pair = divmod(slot, pairs_per_row)
        metal_grid.addWidget(
            QLabel(tr(pantheon.WEEKDAY_THEME_TITLES[theme])), row, pair * 2
        )
        metal_grid.addWidget(combo, row, pair * 2 + 1)
        slot += 1
    metal_grid.setColumnStretch(pairs_per_row * 2, 1)
    layout.addLayout(metal_grid)
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


def _paint_metal_combo(combo: QComboBox) -> None:
    """The rotation metal combo's FILL — the Encyclopedia look-chip
    vocabulary (`ui_style._LOOK_FILLS` colors, Rule #5: same metals,
    same hexes) applied to the combo itself so the selection reads at a
    glance. Text color is derived from the fill's own luminance, never
    hand-picked (the `readable_on_dark`/`_readable_text` law)."""
    from app.ui_style import _LOOK_FILLS, _readable_text

    pick = (combo.currentData() or "").capitalize()
    fill = _LOOK_FILLS.get(pick)
    if fill is None:
        combo.setStyleSheet("")
        return
    if isinstance(fill, tuple):
        background = (
            "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            f"stop:0 {fill[0]}, stop:1 {fill[1]})"
        )
    else:
        background = fill
    combo.setStyleSheet(
        f"QComboBox {{ background: {background};"
        f" color: {_readable_text(fill)}; font-weight: 600;"
        " padding: 3px 10px; }"
    )
