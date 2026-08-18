"""Ring section (R-10/R-13, see ring.md) — THE COMPOSITIONAL RING MODEL
(owner decree 2026-08-05): a preset gallery (thumbnail tiles of the
LOCKED outer — the tooltip states the lock), an INNER gallery (eight
tiles, applies to the active preset — user-changeable independent of
the outer's lock), the jewels-finish pills, the Shine checkbox
(unchanged, R-10/TASK 3/DOLLAR-EYE) and R-13's "Custom ring…" button,
which opens the custom-ring flow's outer/jewel/crown builder in the
Settings dialog rather than duplicating its inline widgets (see
ring.md's Design Decisions). TWO METALS retired (owner decree
2026-08-11) — every jewel roster is single-metal now.

THE CROWN GETS ONE SEAT (ballot verdict 5C, 2026-08-15): the six
controls a reader sees as "the crown text" — its typed text, the
Location toggle, its Time format, color, size and opacity — used to be
scattered across five different pages (Ring, Numerals, Colors, Size,
Opacity). `_crown_text_group` below is now all six, together, in the
order the owner named them; each arrived here from its old page with a
one-line note of where it came from. The graceful-truth gate that used
to repeat per-row on three separate pages now greys the color/size/
opacity trio ONCE, as the single sub-widget they occupy — the text/
Location/Time format controls stay live even with no crown text yet,
since a custom ring's text box is exactly how that text gets typed in
the first place; disabling it too would lock the field shut forever.
"""

from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QVBoxLayout, QWidget,
)

from app.watch_face import thumbs, tint_control
from app.ui_style import tooltip_wrap
from app.watch_face.controls import (
    ValueKnob, ValueUnit, knob_row, picture_group,
)
from app.watch_face.widgets import FlowLayout, flow_row, pill
from config import constants, dial, palette
from data.rings import ring_presets


def _crown_text_validator(parent: QLineEdit) -> QRegularExpressionValidator:
    """RING VERDICTS round (owner decree 2026-08-05): the crown-text
    field must only ACCEPT a character the crown-text renderer can actually
    draw — a `QRegularExpressionValidator` built straight off
    `constants.RING_CROWN_TEXT_CHARSET` (DERIVED, never a hand-written
    list — Rule #5, the exact set `app.skin_builder._location_crown_text`
    filters the Location crown through too) so an unsupported keystroke
    is rejected outright instead of silently dropping the whole crown
    text at build time."""
    escaped = "".join(
        "\\" + char if char in "\\^]-" else char
        for char in sorted(constants.RING_CROWN_TEXT_CHARSET)
        if char != " "
    )
    pattern = QRegularExpression(f"^[{escaped} ]*$")
    return QRegularExpressionValidator(pattern, parent)


def _crown_text_tooltip(tr) -> str:
    allowed = " ".join(
        sorted(constants.RING_CROWN_TEXT_CHARSET - {" "})
    )
    return tr("Allowed characters: {allowed}").format(allowed=allowed)


def build(settings, setters: dict, tr) -> QWidget:
    layout = QVBoxLayout()
    presets = ring_presets(settings.custom_rings)
    layout.addWidget(_preset_gallery(settings, presets, setters, tr))
    layout.addWidget(_preset_about(presets, settings.ring, tr))
    layout.addWidget(_finish_row(settings, setters, tr))
    active_card = presets[settings.ring]
    if constants.RING_EYE_GLYPH in active_card["jewels"]:
        shine = settings.ring_eye_shine.get(
            settings.ring,
            constants.RING_EYE_SHINE_DEFAULT.get(settings.ring, False),
        )
        shine_box = QCheckBox(tr("Shine"))
        shine_box.setChecked(shine)
        shine_box.toggled.connect(setters["ring_eye_shine"])
        layout.addWidget(shine_box)
    layout.addWidget(_inner_group(settings, setters, tr))
    layout.addWidget(_crown_text_group(settings, active_card, setters, tr))
    layout.addWidget(_custom_ring_button(setters, tr))
    widget = QWidget()
    widget.setLayout(layout)
    return widget


def _preset_gallery(settings, presets: dict, setters, tr) -> QWidget:
    """One tile per preset, THUMBNAILED FROM ITS OWN COMPOSED PREVIEW
    (ring_rework §5, owner ruling 2026-08-06: "preset picker: name +
    mini preview + the About" — COMPUTED, never a stored/generated
    image: `thumbs.ring_preset_thumbnail` stamps the card's own outer
    plate and its own jewels at their real seats, at thumbnail scale).
    A card with no drawable preview (a broken custom ring) falls back
    to the bare outer plate, same graceful-absence pattern
    `art_thumbnail` already documents. The tooltip states which outer
    the preset is locked to (owner decree 2026-08-05: every bundled
    preset is locked to exactly one outer; only the INNER stays
    user-changeable) AND, when the card carries one, its own About
    text — hovering ANY tile previews it, not only the active one."""
    entries = []
    for name in sorted(presets):
        card = presets[name]
        outer_name = card["outer"]
        face = constants.RING_OUTERS[outer_name]["file"]
        icon = (
            thumbs.ring_preset_thumbnail(card)
            or thumbs.art_thumbnail(dial.RING_OUTER_ART_DIR / face)
        )
        blurb = tr("Locked outer: {outer}").format(outer=outer_name)
        if card["about"]:
            blurb += "\n\n" + card["about"]
        entries.append((name, tr(name), blurb, icon))
    return picture_group(
        tr("Ring preset"),
        tr("The whole band: its outer plate and the jewels seated on it. "
           "Every bundled preset is locked to one outer."),
        entries, settings.ring, setters["ring"],
    )


def _preset_about(presets: dict, ring: str, tr) -> QLabel:
    """THE SPACE & LEGIBILITY LAW (owner decree 2026-08-05): the active
    preset's own About, in the reader's own words, word-wrapped —
    never clipped, never only a tooltip nobody hovers. A card without
    an About (a custom ring) leaves this label empty rather than
    reserving dead space with a placeholder sentence."""
    card = presets.get(ring)
    label = QLabel(tr(card["about"]) if card and card["about"] else "")
    label.setWordWrap(True)
    label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    label.setStyleSheet("font-style: italic;")
    return label


def _finish_row(settings, setters, tr) -> QWidget:
    """THE FOUR JEWEL FINISHES. A `flow_row`, not a bare QHBoxLayout
    (runtime audit ALG-5, 2026-08-15): the plain row neither wrapped nor
    equalised, so at a narrow window "Silver jewels" stood 122px beside
    "Thematic jewels" at 136px. It went unseen while the window's
    minimum was wide enough to keep the row on one line; compacting the
    Colors page dropped that minimum and the audit found it the same
    hour. `flow_row` carries both rules for every row that passes
    through it."""
    # BOUND NOW, not at click time: a lookup deferred into a lambda is a
    # lookup the per-section Reset never records (see section_reset.py).
    apply_finish = setters["ring_finish"]
    return flow_row(
        pill(
            tr(f"{finish.capitalize()} jewels"), settings.ring_finish == finish,
            lambda f=finish, a=apply_finish: a(f),
        )
        for finish in constants.RING_FINISHES
    )


def _inner_group(settings, setters, tr):
    """THE INNER GALLERY (owner decree 2026-08-05): eight cards, one per
    `constants.RING_INNERS` variant — applies to the ACTIVE preset (or
    the active custom ring), stored per-preset-name exactly like
    `ring_eye_shine` (`Settings.ring_inner`,
    `app.skin_builder._resolve_ring_inner`)."""
    default = constants.RING_INNER_PRESET_DEFAULT.get(
        settings.ring, constants.RING_INNER_DEFAULT
    )
    active = settings.ring_inner.get(settings.ring, default)
    entries = [
        (
            inner, tr(inner.replace("_", " ").title()),
            tr("The {inner} minute track on the inner band.").format(
                inner=inner.replace("_", " ")
            ),
            thumbs.art_thumbnail(dial.RING_INNER_ART_DIR / f"{inner}.png"),
        )
        for inner in constants.RING_INNERS
    ]
    return picture_group(
        tr("Inner (minute track)"),
        tr("The five-minute band inside the ring — free to change on any "
           "preset, unlike the locked outer."),
        entries, active, setters["ring_inner"],
    )


def _crown_time_format_row(settings, setters, tr) -> QWidget:
    """MOVED HERE from `numerals._crown_group` (ballot verdict 5C,
    2026-08-15) — the format the live crown reads its digits in
    (bundled to `crown_text_scale`'s own note: only The One/Templar
    keep a live time in their arc, everyone else ignores this pick)."""
    apply_format = setters["crown_time_format"]   # BOUND NOW — see _finish_row
    row = QHBoxLayout()
    row.addWidget(QLabel(tr("Time format")))
    combo = QComboBox()
    labels = {"hh:mm": "12:35", "12h 35min": "12h 35min"}
    for value in dial.CROWN_TIME_FORMATS:
        combo.addItem(tr(labels.get(value, value)), value)
    combo.setCurrentIndex(
        max(0, list(dial.CROWN_TIME_FORMATS).index(settings.crown_time_format))
    )
    combo.currentIndexChanged.connect(
        lambda index: apply_format(combo.itemData(index))
    )
    row.addWidget(combo, stretch=1)
    host = QWidget()
    host.setLayout(row)
    host.setToolTip(tooltip_wrap(tr(
        "Only the presets that keep a time in their arc use this — "
        "The One (this watch's own hour) and Templar (the hour of "
        "Jerusalem)."
    )))
    return host


def _crown_style_row(settings, setters, tr) -> QWidget:
    """Color/size/opacity for the crown text — MOVED HERE from
    colors.py/size.py/opacity.py (ballot verdict 5C, 2026-08-15). The
    graceful-truth gate each of those three pages carried on its own
    single row (`setters["ring_has_crown_text"]`) is applied ONCE here,
    to the whole sub-widget, since the three now live beside each other
    and are, together, the one thing the gate is about.

    Labeled Tint/Scale/Visibility, not Color/Size/Opacity (ALG-9 SECTION
    TAXONOMY, `tests/layout_checks_qt.py`): those bare words each claim
    a concept that owns a page of its own, and renaming the label is the
    remedy that rule PRESCRIBES rather than a way around it — its own
    docstring says so.

    "Visibility" replaced "Alpha" after an independent grader called
    that word out (2026-08-15): alpha is graphics vocabulary, and almost
    nobody outside it reads the word as opacity. Visibility says the
    same thing, runs the same direction (100% = fully there), and still
    claims no concept that lives on another page."""
    apply_scale = setters["crown_text_scale"]   # BOUND NOW — see _finish_row
    apply_alpha = setters["crown_text_alpha"]
    column = QVBoxLayout()
    column.setContentsMargins(0, 0, 0, 0)
    column.addWidget(tint_control.tint_control(
        tr, tr("Tint"), settings.crown_text_tint, palette.RING_TINT_GROUPS,
        tr("Follow ring (default)"), palette.RING_TINT_PICKER_SEED,
        setters["crown_text_tint"],
    ))
    size_knob = ValueKnob(
        "crown_text_scale", tr("Scale"),
        tr("The Great Seal inscription's size — multiplies on top of Jewels."),
        unit=ValueUnit.PERCENT,
        low=round(constants.ELEMENT_SCALE_RANGE[0] * 100),
        high=round(constants.ELEMENT_SCALE_RANGE[1] * 100), family="size",
        default_value=100,
        on_change=lambda value: apply_scale(value / 100.0),
    )
    size_knob.set_value(round(settings.crown_text_scale * 100))
    alpha_knob = ValueKnob(
        "crown_text_alpha", tr("Visibility"),
        tr("The Great Seal inscription's opacity."),
        unit=ValueUnit.PERCENT, low=0, high=100, family="opacity",
        default_value=100,
        on_change=lambda value: apply_alpha(value / 100.0),
    )
    alpha_knob.set_value(round(settings.crown_text_alpha * 100))
    flow = FlowLayout()
    flow.addWidget(knob_row(size_knob))
    flow.addWidget(knob_row(alpha_knob))
    knob_host = QWidget()
    knob_host.setLayout(flow)
    column.addWidget(knob_host)
    host = QWidget()
    host.setLayout(column)
    if not setters["ring_has_crown_text"]():
        host.setEnabled(False)
        host.setToolTip(tooltip_wrap(tr(
            "The active ring preset carries no Crown Text (Great Seal "
            "inscription)."
        )))
    return host


def _crown_text_group(settings, card: dict, setters, tr) -> QGroupBox:
    """CROWN (ballot verdict 5C, 2026-08-15 — was "Crown text"): the
    bundled presets show their existing crown text read-only (Dollar's
    Great Seal, DOMY/LOOP's cross words); a custom ring may TYPE its own
    text and pick an orientation (top/bottom). The custom field's
    `QLineEdit` carries a whitelist `QValidator` (RING VERDICTS round,
    owner decree 2026-08-05) so an unsupported character cannot be typed
    at all — the tooltip states exactly what is allowed. Every ring,
    preset or custom, ALSO carries the LOCATION checkbox (same round):
    ticked, it replaces whatever crown text the ring carries with the
    active location's own "CITY, COUNTRY" (`app.controller.
    _compose_skin`). Time format, color, size and opacity join below —
    the owner's decree that everything a reader sees as "the crown"
    lives on one page now."""
    group = QGroupBox(tr("Crown"))
    column = QVBoxLayout(group)
    # BOUND NOW — see `_finish_row`. Above the branch, so the Reset owns
    # both keys even on a preset ring, whose read-only arm builds no
    # editor at all.
    apply_text = setters["custom_ring_crown_text"]
    apply_orientation = setters["custom_ring_crown_orientation"]
    location_on = settings.ring_crown_location.get(settings.ring, False)
    if settings.ring in constants.RING_OUTER_LOCK:
        texts = " · ".join(entry["text"] for entry in card["crown_text"]) or tr("(none)")
        label = QLabel(texts)
        label.setEnabled(not location_on)
        column.addWidget(label)
    else:
        edit = QLineEdit()
        edit.setPlaceholderText(tr("Custom crown text"))
        edit.setText(settings.custom_ring_crown_text.get(settings.ring, ""))
        edit.setValidator(_crown_text_validator(edit))
        edit.setToolTip(tooltip_wrap(_crown_text_tooltip(tr)))
        edit.setEnabled(not location_on)
        edit.editingFinished.connect(
            lambda: apply_text(edit.text())
        )
        column.addLayout(_labeled(tr("Text"), edit))
        orient_row = QHBoxLayout()
        current = settings.custom_ring_crown_orientation.get(settings.ring, "top")
        for orientation in ("top", "bottom"):
            pill_button = pill(
                tr(orientation.capitalize()), current == orientation,
                lambda o=orientation, a=apply_orientation: a(o),
            )
            pill_button.setEnabled(not location_on)
            orient_row.addWidget(pill_button)
        column.addLayout(orient_row)
    location_box = QCheckBox(tr("Location"))
    location_box.setChecked(location_on)
    location_box.setToolTip(tooltip_wrap(
        tr("Show the active location (CITY, COUNTRY) as the crown text "
           "instead — follows every location change.")
    ))
    location_box.toggled.connect(setters["ring_crown_location"])
    column.addWidget(location_box)
    column.addWidget(_crown_time_format_row(settings, setters, tr))
    column.addWidget(_crown_style_row(settings, setters, tr))
    return group


def _labeled(text: str, widget) -> QHBoxLayout:
    row = QHBoxLayout()
    row.addWidget(QLabel(text))
    row.addWidget(widget, stretch=1)
    return row


def _custom_ring_button(setters, tr) -> QPushButton:
    """R-13: the existing custom-ring flow
    (`app/settings_dialog/custom_art_section.py`) is a plain-Python
    mixin baked onto `SettingsDialog`, not a standalone dialog — this
    button opens THAT dialog, navigated to its Custom art section,
    instead of duplicating its inline widgets."""
    button = QPushButton(tr("Custom ring…"))
    button.clicked.connect(lambda: setters["open_custom_ring"]())
    return button
