"""Numerals section — the Watch Face window's page for the two
LIVE-RENDERED numeral bands (research/hour_numerals.md §8 +
research/ring_rework.md §5).

The page opens with the MODE (§1) — Geocentric (Ptolemy) or Heliocentric
(Copernicus), the one pick that says whether the hour band is a fixed
ring or a turning world — and then the bands themselves.

Four groups, in the order the reader meets them on the dial: the OUTER
band (its face, its numeral size, the width of the band the jewels and
numbers stand in, and the seating law), MINUTES — the inner minute band
(its own face and size — the ledger settles that nothing else about it
is user-changeable: it never rotates and it follows the outer band's
seating), and the RELIEF the outer numerals wear (style, depth, light,
darkness, contact blur, border).

THE CROWN'S TIME FORMAT MOVED OUT (ballot verdict 5C, 2026-08-15): the
live crown's Time format pick joined the rest of "the crown" — its
text, Location, color, size and opacity — on the Ring page's Crown
group (`app.watch_face.ring._crown_time_format_row`). This page no
longer builds a crown group at all.

LIVE-APPLY like every other Watch Face section: each pick calls its
setter immediately through `setters`, and the window rebuilds this page
fresh on the next pick — so nothing here holds state of its own.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QSlider,
    QVBoxLayout, QWidget,
)

from app.ui_style import tooltip_wrap
from app.watch_face.widgets import number_row as _number_row
from config import dial


def build(settings, setters: dict, tr) -> QWidget:
    layout = QVBoxLayout()
    layout.addWidget(_mode_group(settings, setters, tr))
    layout.addWidget(_outer_group(settings, setters, tr))
    layout.addWidget(_inner_group(settings, setters, tr))
    layout.addWidget(_relief_group(settings, setters, tr))
    layout.addStretch(1)
    widget = QWidget()
    widget.setLayout(layout)
    return widget


def _choice_row(
    tr, settings, setters, key: str, choices, title: str, form: QFormLayout,
    labels: dict | None = None,
) -> QComboBox:
    """A closed-vocabulary row. `choices` is the vocabulary in its own
    documented order (the first entry of a roster is that band's SETTLED
    default), so the combo can never offer a value the store would call
    corrupt."""
    # BOUND NOW, not at change time: a lookup deferred into a lambda is
    # a lookup the per-section Reset never records (see section_reset.py).
    apply_value = setters[key]
    combo = QComboBox()
    current = getattr(settings, key)
    for value in choices:
        combo.addItem(tr((labels or {}).get(value, value)), value)
    combo.setCurrentIndex(max(0, list(choices).index(current)))
    combo.currentIndexChanged.connect(
        lambda index: apply_value(combo.itemData(index))
    )
    form.addRow(tr(title), combo)
    return combo


def _mode_group(settings, setters, tr) -> QGroupBox:
    """THE TWO WORLD-MODES (ring_rework.md §1) — the one setting that
    decides whether the hour band below is a fixed ring of markers or a
    world that turns. It leads this page for that reason: everything
    under it describes the band, and this says whether the band moves.

    Solar Rotation is NOT here — it is its own independent switch in the
    right-click menu, exactly as before, and it keeps meaning the same
    thing in both modes (whether the solar offset is taken at all)."""
    group = QGroupBox(tr("Mode — which one turns"))
    form = QFormLayout(group)
    mode = _choice_row(
        tr, settings, setters, "world_mode", dial.WORLD_MODES, "Mode", form,
        labels=dial.WORLD_MODE_LABELS,
    )
    mode.setToolTip(tooltip_wrap(tr(
        "Noon Stays Up: noon is the fixed point. The observer stands "
        "still, the sun travels, the pointer turns toward true solar noon "
        "and 12 keeps the top all day and all night. This is the ordinary "
        "watch face, and the sun spends the night below you.\n\n"
        "Sky Follows You: the light is the fixed point. The hour band "
        "carries true solar noon to the top, and the whole dial turns over "
        "at night — so the Sun is overhead by day and the Moon is overhead "
        "by night, the way the sky looks to someone standing under it."
    )))
    scope = _choice_row(
        tr, settings, setters, "world_rotation_scope",
        dial.WORLD_ROTATION_SCOPES, "What turns", form,
        labels=dial.WORLD_ROTATION_SCOPE_LABELS,
    )
    scope.setToolTip(tooltip_wrap(tr(
        "Everything Turns: the numerals, the jewels and the crown ride "
        "the rotation together, so a jewel always keeps its own seat and "
        "the seats it stands on never carry a number.\n\n"
        "Numerals Turn: the jewels and the crown hold their place on "
        "screen and the numerals slide underneath them. A numeral a jewel "
        "would cover is left off the ring entirely — never drawn half "
        "under a letter — and the seats the jewels vacate finally carry "
        "their numbers, midnight reading 0."
    )))
    note = QLabel(tr(
        "The hands and the minute ring always show ordinary zone time, and "
        "the year wheel keeps the summer solstice due north — the mode "
        "turns the hour band, and What turns says whether the jewels and "
        "the crown go with it."
    ))
    note.setWordWrap(True)
    form.addRow(note)
    # WHAT TURNS IS A NOON-UP NO-OP (owner question 2026-08-13, and he
    # was right): `core.world.world_offset_deg` is exactly 0.0 in
    # `noon_up`, so `render.layers.numerals.jewel_offset` hands back the
    # same number for both scopes and the occlusion at offset 0 hides
    # precisely the seats `all_turn` skips by composition — the two
    # picks draw a bit-for-bit identical dial there. Offering a live
    # choice that changes nothing is the defect; the row is therefore
    # DISABLED rather than hidden (hiding it would jump the form and
    # lose the explanation) and his stored pick is never touched, so it
    # is waiting for him the moment he goes back to Sky Follows You.
    _follow_mode(mode, scope, form, tr)
    return group


def _follow_mode(mode: QComboBox, scope: QComboBox, form: QFormLayout, tr):
    """Grey the What-turns row out for as long as the mode is the one it
    cannot affect, label and all, and say why in the tooltip."""
    disabled_hint = tooltip_wrap(tr(
        "What turns applies in Sky Follows You only. In Noon Stays Up "
        "the hour band does not turn at all, so the jewels and the crown "
        "have nothing to ride and both picks draw the same dial. Your "
        "choice is kept and comes back with the other mode."
    ))
    live_hint = scope.toolTip()
    label = form.labelForField(scope)

    def apply() -> None:
        turning = mode.currentData() != "noon_up"
        scope.setEnabled(turning)
        scope.setToolTip(live_hint if turning else disabled_hint)
        if label is not None:
            label.setEnabled(turning)
            label.setToolTip(scope.toolTip())

    mode.currentIndexChanged.connect(lambda _index: apply())
    apply()


def _outer_group(settings, setters, tr) -> QGroupBox:
    """FACE and SEATING only — the three band SIZE sliders moved to the
    Size section (ALG-9 SECTION TAXONOMY, owner order 2026-08-09: when
    a Size category exists, EVERY size control lives there)."""
    group = QGroupBox(tr("Numerals"))
    form = QFormLayout(group)
    _choice_row(
        tr, settings, setters, "numeral_face",
        tuple(dial.NUMERAL_OUTER_FACES), "Numerals face", form,
    )
    seating = _choice_row(
        tr, settings, setters, "numeral_seating", dial.NUMERAL_SEATINGS,
        "Seating", form,
        labels={"arc": "Arc — follow the circle", "upright": "Upright"},
    )
    seating.setToolTip(tooltip_wrap(tr(
        "Arc: a numeral on a square angle stands upright, every other takes "
        "the angle it sits on, and the lower half turns 180° so nothing "
        "reads upside down."
    )))
    return group


def _inner_group(settings, setters, tr) -> QGroupBox:
    group = QGroupBox(tr("Minutes"))
    form = QFormLayout(group)
    _choice_row(
        tr, settings, setters, "minutes_face",
        tuple(dial.MINUTES_FACES), "Minutes face", form,
    )
    note = QLabel(tr(
        "The inner band never rotates, and it follows the hour ring's "
        "seating — only its face is picked here."
    ))
    note.setWordWrap(True)
    form.addRow(note)
    return group


def _relief_group(settings, setters, tr) -> QGroupBox:
    group = QGroupBox(tr("Relief"))
    form = QFormLayout(group)
    style = _choice_row(
        tr, settings, setters, "numeral_relief", dial.NUMERAL_RELIEF_STYLES,
        "Relief style", form,
        labels={
            "cast": "Cast — a plate floating above the ring",
            "extrude": "Extrude — a block standing on the ring",
            "emboss": "Emboss — pressed metal",
        },
    )
    style.setToolTip(tooltip_wrap(tr(
        "Cast leaves the gap open; Extrude welds its copies into a side "
        "wall; Emboss adds a lit rim the other way."
    )))
    light = _choice_row(
        tr, settings, setters, "numeral_light", dial.NUMERAL_LIGHTS,
        "Light", form,
        labels={
            "radial": "Radial — one lamp at the centre",
            "fixed": "Fixed — one lamp off the dial",
        },
    )
    light.setToolTip(tooltip_wrap(tr(
        "Radial: every numeral throws its relief straight outward — "
        "(0, +d) at the top, (+d, 0) at the right, (0, −d) at the bottom, "
        "(−d, 0) at the left."
    )))
    # THE RELIEF KNOBS (classes phase, owner verdicts 2026-08-14): the
    # four number rows became a row of small K-270D knobs in the relief
    # family's teal ring — the combos above keep the form shape.
    from app.watch_face.controls import ValueKnob, ValueUnit, knob_row
    from app.watch_face.widgets import FlowLayout

    flow = FlowLayout()
    for key, title, (low, high), default, decimals, blurb in (
        ("numeral_depth", "Depth", dial.NUMERAL_DEPTH_RANGE,
         dial.NUMERAL_DEPTH_DEFAULT, 1, "How far the relief throws."),
        ("numeral_darkness", "Darkness", dial.NUMERAL_DARKNESS_RANGE,
         dial.NUMERAL_DARKNESS_DEFAULT, 2, "The shadow copies' darkness."),
        ("numeral_contact_blur", "Contact blur",
         dial.NUMERAL_CONTACT_BLUR_RANGE, dial.NUMERAL_CONTACT_BLUR_DEFAULT,
         1, "The soft edge where the relief meets the ring."),
        ("numeral_border", "Border", dial.NUMERAL_BORDER_RANGE,
         dial.NUMERAL_BORDER_DEFAULT, 1, "The outline around each numeral."),
    ):
        knob = ValueKnob(
            key, tr(title), tr(blurb),
            unit=ValueUnit.FACTOR if decimals else ValueUnit.PLAIN,
            low=low, high=high, family="relief", default_value=default,
            decimals=decimals, on_change=setters[key], diameter_px=80,
        )
        knob.set_value(getattr(settings, key))
        flow.addWidget(knob_row(knob))
    host = QWidget()
    host.setLayout(flow)
    form.addRow(host)
    return group
