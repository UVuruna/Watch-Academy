"""Size section (see size.md) — migrated to THE ELEMENT CLASSES (owner
ballot verdicts 2026-08-14, classes phase): every size control is now a
VALUE KNOB in the size family's blue ring. The dial diameter is the one
K-270 (no default notch — the five `dial.SIZE_PRESETS` pills above it
are the factory voices; double-click enters an exact px value, taking
the retired spinbox's job); every element scale and the three
numeral-band sizes are K-270D with the green default notch (verdict
7A). Stored keys are unchanged from the slider era (Rule #5).

CROWN TEXT (R-24/Phase-6-debt correction, owner 2026-08-05) keeps its
graceful-truth gate: the one knob that is not always meaningful greys
out with a tooltip when the active ring preset carries no crown text
(`setters["ring_has_crown_text"]`).
"""

from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout, QWidget

from app.ui_style import tooltip_wrap
from app.watch_face.controls import KnobKind, ValueKnob, ValueUnit, knob_row
from app.watch_face.widgets import FlowLayout, pill
from config import constants, dial

# (setting key, on-screen label, (low, high) range, default*100, blurb)
_SCALE_ROWS = (
    ("earth_scale", "Earth", constants.ELEMENT_SCALE_RANGE, 100,
     "The Earth marker's size."),
    ("moon_scale", "Moon", constants.ELEMENT_SCALE_RANGE, 100,
     "The Moon marker's size."),
    ("slot_scale", "Complications", constants.ELEMENT_SCALE_RANGE, 100,
     "The subdial complications' size."),
    ("ring_jewels_scale", "Jewels", constants.ELEMENT_SCALE_RANGE, 100,
     "The ring jewels' size."),
    ("crown_text_scale", "Crown Text", constants.ELEMENT_SCALE_RANGE, 100,
     "The Great Seal inscription's size — multiplies on top of Jewels."),
    ("hover_enlarge", "Hover enlarge", constants.HOVER_ENLARGE_RANGE, 120,
     "How much a hovered body grows."),
)


def build(settings, setters: dict, tr) -> QWidget:
    layout = QVBoxLayout()
    layout.addWidget(_diameter_group(settings, setters, tr))
    layout.addWidget(_scale_group(settings, setters, tr))
    layout.addWidget(_numeral_bands_group(settings, setters, tr))
    widget = QWidget()
    widget.setLayout(layout)
    return widget


def _flow(knobs) -> QWidget:
    host = QWidget()
    flow = FlowLayout()
    for knob in knobs:
        flow.addWidget(knob_row(knob))
    host.setLayout(flow)
    return host


def _diameter_group(settings, setters, tr) -> QGroupBox:
    group = QGroupBox(tr("Dial size"))
    column = QVBoxLayout(group)
    preset_row = QHBoxLayout()
    for preset in dial.SIZE_PRESETS:
        preset_row.addWidget(pill(
            f"{preset} px", settings.diameter == preset,
            lambda p=preset: setters["diameter"](p),
        ))
    column.addLayout(preset_row)
    low, high = dial.SIZE_PRESETS[0], dial.SIZE_PRESETS[-1]
    knob = ValueKnob(
        "diameter", tr("Diameter"),
        tr("The watch window's size on the desktop — double-click for an exact value."),
        unit=ValueUnit.PIXEL, low=low, high=high, family="window",
        kind=KnobKind.K270,
        on_change=lambda value: setters["diameter"](round(value)),
    )
    knob.set_value(settings.diameter)
    column.addWidget(_flow((knob,)))
    return group


def _scale_group(settings, setters, tr) -> QGroupBox:
    group = QGroupBox(tr("Element sizes"))
    column = QVBoxLayout(group)
    knobs = []
    for key, title, (low, high), default, blurb in _SCALE_ROWS:
        knob = ValueKnob(
            key, tr(title), tr(blurb),
            unit=ValueUnit.PERCENT, low=round(low * 100),
            high=round(high * 100), family="size", default_value=default,
            on_change=lambda value, k=key: setters[k](value / 100.0),
        )
        knob.set_value(round(getattr(settings, key) * 100))
        if key == "crown_text_scale" and not setters["ring_has_crown_text"]():
            knob.setEnabled(False)
            knob.setToolTip(tooltip_wrap(tr(
                "The active ring preset carries no Crown Text (Great Seal inscription)."
            )))
        knobs.append(knob)
    column.addWidget(_flow(knobs))
    return group


def _numeral_bands_group(settings, setters, tr) -> QGroupBox:
    """The three numeral-band SIZE knobs (ALG-9 SECTION TAXONOMY, owner
    order 2026-08-09: every size control lives in Size; the bands'
    FACES stay in Numerals)."""
    group = QGroupBox(tr("Numeral bands"))
    column = QVBoxLayout(group)
    outer = ValueKnob(
        "numeral_outer_size", tr("Numerals size"),
        tr("The hour numerals' height, in the numeral's own units."),
        unit=ValueUnit.PLAIN, low=dial.NUMERAL_SIZE_RANGE[0],
        high=dial.NUMERAL_SIZE_RANGE[1], family="size",
        default_value=dial.NUMERAL_OUTER_SIZE_DEFAULT,
        on_change=lambda value: setters["numeral_outer_size"](round(value)),
    )
    outer.set_value(settings.numeral_outer_size)
    ring = ValueKnob(
        "numeral_outer_ring_size", tr("Outer ring size"),
        tr("The outer band's scale factor."),
        unit=ValueUnit.FACTOR, low=dial.NUMERAL_OUTER_RING_SIZE_RANGE[0],
        high=dial.NUMERAL_OUTER_RING_SIZE_RANGE[1], family="size",
        default_value=dial.NUMERAL_OUTER_RING_SIZE_DEFAULT, decimals=2,
        on_change=setters["numeral_outer_ring_size"],
    )
    ring.set_value(settings.numeral_outer_ring_size)
    minutes = ValueKnob(
        "minutes_size", tr("Minutes size"),
        tr("The minute band's height, in the numeral's own units."),
        unit=ValueUnit.PLAIN, low=dial.NUMERAL_SIZE_RANGE[0],
        high=dial.NUMERAL_SIZE_RANGE[1], family="size",
        default_value=dial.MINUTES_SIZE_DEFAULT,
        on_change=lambda value: setters["minutes_size"](round(value)),
    )
    minutes.set_value(settings.minutes_size)
    column.addWidget(_flow((outer, ring, minutes)))
    return group
