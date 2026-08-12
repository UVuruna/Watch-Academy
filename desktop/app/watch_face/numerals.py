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
darkness, contact blur, border) plus the live crown's own face and time
format.

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
    layout.addWidget(_crown_group(settings, setters, tr))
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
    combo = QComboBox()
    current = getattr(settings, key)
    for value in choices:
        combo.addItem(tr((labels or {}).get(value, value)), value)
    combo.setCurrentIndex(max(0, list(choices).index(current)))
    combo.currentIndexChanged.connect(
        lambda index: setters[key](combo.itemData(index))
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
        "Geocentric: the observer stands still and the sun travels — the "
        "pointer turns toward true solar noon and 12 stays on top. "
        "Heliocentric: the sun stands still and the world turns — the hour "
        "band carries solar noon to the top, and the whole dial turns over "
        "at night, 0h on top and noon at the bottom."
    )))
    note = QLabel(tr(
        "The hands and the minute ring always show ordinary zone time — "
        "the mode moves only what is drawn."
    ))
    note.setWordWrap(True)
    form.addRow(note)
    return group


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
    _number_row(
        tr, settings, setters, "numeral_depth", *dial.NUMERAL_DEPTH_RANGE,
        "Depth", form, decimals=1,
    )
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
    _number_row(
        tr, settings, setters, "numeral_darkness",
        *dial.NUMERAL_DARKNESS_RANGE, "Darkness", form, decimals=2,
    )
    _number_row(
        tr, settings, setters, "numeral_contact_blur",
        *dial.NUMERAL_CONTACT_BLUR_RANGE, "Contact blur", form, decimals=1,
    )
    _number_row(
        tr, settings, setters, "numeral_border", *dial.NUMERAL_BORDER_RANGE,
        "Border", form, decimals=1,
    )
    return group


def _crown_group(settings, setters, tr) -> QGroupBox:
    group = QGroupBox(tr("The live crown"))
    form = QFormLayout(group)
    # NO FACE PICKER (THE ONE PLATE LAW, owner decree 2026-08-07): the
    # crown draws the owner's letter plates, exactly like the jewels and
    # the crown text beside it, so there is no font left to pick. The row
    # that used to stand here chose the face for the font-drawn digits.
    _choice_row(
        tr, settings, setters, "crown_time_format", dial.CROWN_TIME_FORMATS,
        "Time format", form,
        labels={"hh:mm": "12:35", "12h 35min": "12h 35min"},
    )
    live = QLabel(tr(
        "Only the presets that keep a time in their arc use these — "
        "The One (this watch's own hour) and Templar (the hour of "
        "Jerusalem)."
    ))
    live.setWordWrap(True)
    form.addRow(live)
    return group
