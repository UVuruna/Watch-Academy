"""Hands & Bodies section (owner verdict 2026-08-10, see bodies.md) —
the Watch Face window's "Hands & Bodies" page: the hand-pack gallery
(R-14, moved verbatim from the RETIRED `hands.py`) plus every menu that
decides how the Moon and the Earth are drawn, because the owner ruled
on the rendering-proposals page that "they are what MOVES and points" —
the same family as the hour/minute hands, not scattered across
Pointer/Opacity.

Since the CardGroup migration (2026-08-14) every gallery here is a
`controls.picture_group` — title, one-sentence description and the
mandatory per-card hover blurb (`_BLURBS`), flowing centered — and the
"Earth"/"Moon" boxes were FLATTENED into one group per gallery, because
a titled box inside a titled box reads as a defect:

- **Hands** — the hand-pack gallery (unchanged from the retired module).
- **Earth** — the style/label/"Position pointer" rows moved verbatim
  from `pointer.py`'s `_earth_group`, plus the position-pointer SHAPE
  gallery (`marker_pointer_shape`), enabled only while "Position
  pointer" is checked — the shape has nothing to preview when no
  pointer is drawn.
- **Moon** — the unlit-half style (`moon_dark_style`), the
  Earth-crossing style (`moon_transit_style`), and the Moon Horizon
  Band's mode + style galleries, moved here from `opacity.py`'s
  `_moon_band_group` (owner: everything Moon-related belongs in one
  place).
- **Eclipses** — the solar (`eclipse_solar_style`) and lunar
  (`eclipse_lunar_style`) treatments.
- **Stations** — the Moon's (`moon_station_style`) and the Sun's
  (`sun_station_style`) four-life-stage marks.

Every tile's icon is THE REAL RENDER FUNCTION at thumbnail scale
(`thumbs.py`'s `moon_dark_style_icon`/`moon_transit_style_icon`/
`marker_pointer_shape_icon`/`eclipse_solar_style_icon`/
`eclipse_lunar_style_icon`/`moon_station_style_icon`/
`sun_station_style_icon`/`moon_band_mode_icon`/`moon_band_style_icon`),
never a redrawn sketch — the same discipline the pre-existing Umbra and
Moon Horizon Band galleries already followed.
"""

from PySide6.QtWidgets import (
    QCheckBox, QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget,
)

from app.watch_face import thumbs
from app.watch_face.controls import picture_group
from app.watch_face.widgets import pill
from config import constants, continents, dial
from data.hands import hand_packs

_MOON_DARK_TITLES = {
    "cut_rim": "Cut, with a silver rim",
    "cut_ghost": "Cut, over a faint ghost disc",
    "opaque": "Solid shadow",
}
_MOON_TRANSIT_TITLES = {
    "lane_split": "Lane split",
    "occultation": "Occultation",
    "shrink_pass": "Shrink & pass",
}
_MARKER_POINTER_SHAPE_TITLES = {
    "triangle": "Triangle",
    "chevron": "Chevron",
    "gem": "Gem",
}
_ECLIPSE_SOLAR_TITLES = {
    "bite": "Bite",
    "magnitude_arc": "Magnitude arc",
    "halo": "Halo only",
    # Owner ballot 2026-08-13 — no painter of their own yet, see
    # `render.eclipse_style.resolve_eclipse_style`.
    "totality_path": "Totality path",
    "type_emblem": "Type emblem",
    "dial_shadow": "Dial shadow",
}
_ECLIPSE_LUNAR_TITLES = {
    "umbra_sweep": "Umbra sweep",
    "horizon_shadow": "On the horizon band",
    "halo": "Halo only",
    # Owner ballot 2026-08-13 — no painter of their own yet, see
    # `render.eclipse_style.resolve_eclipse_style`.
    "blood_moon": "Blood moon",
    "danjon_scale": "Danjon scale",
    "contact_marks": "Contact marks",
}
_MOON_STATION_TITLES = {
    "arc_grammar": "Arc grammar",
    "inner_glow": "Inner glow",
    "uniform": "Uniform halo",
}
_SUN_STATION_TITLES = {
    "arc_grammar": "Arc grammar",
    "uniform_seasonal": "Seasonal halo",
    "day_night_wedge": "Day/night wedge",
    "uniform_gold": "Gold halo",
}
_MOON_BAND_MODE_TITLES = {
    "horizon": "Horizon on the circle",
    "dim_only": "Dim only",
    "always_full": "Always the same moon",
}
_MOON_BAND_STYLE_TITLES = {
    "inverted": "Inverted band",
    "silver_thread": "Silver thread",
    "ticks": "Moon ticks",
    "glow": "Moon glow",
}

# THE HOVER BLURBS (owner order 2026-08-14: "the description is always
# an attribute of the card"). One sentence per option, in the reader's
# own words — what this choice DOES on the dial, never the constant
# name repeated. `OptionCard` requires the argument, so a new option
# cannot ship without one.
_BLURBS = {
    "moon_dark_style": {
        "cut_rim": "The shadowed part is cut away and a thin silver rim keeps the whole disc readable.",
        "cut_ghost": "The shadowed part is cut away over a faint ghost disc, so the full Moon stays visible behind it.",
        "opaque": "The shadowed part is filled solid — the strongest phase contrast.",
    },
    "moon_transit": {
        "transit_shadow": "While crossing the Earth the Moon casts a shadow onto it.",
        "transit_shrink": "The Moon shrinks as it passes so both bodies stay readable.",
        "transit_rim": "The Moon rides the Earth's rim instead of overlapping its face.",
    },
    "marker_pointer_shape": {
        "triangle": "A plain triangle at the body's own angle.",
        "chevron": "An open chevron — lighter on a busy dial.",
        "gem": "A faceted gem, the heaviest of the three.",
    },
    "earth_style": {
        "clean": "The globe as bare land and sea, without an air layer.",
        "atmo": "The globe with its atmosphere — a soft lit halo around the edge.",
    },
    "moon_band_mode": {
        "horizon": "An arc appears while the Moon stands above the horizon.",
        "dim_only": "No arc — the Moon simply dims while it is below the horizon.",
        "always_full": "The Moon is drawn the same way whatever its altitude.",
    },
    "moon_band_style": {
        "inverted": "A filled band drawn inverted against the dial ground.",
        "silver_thread": "A thin silver line — the quietest of the four.",
        "ticks": "Short ticks along the band instead of a continuous line.",
        "glow": "A soft glow spread along the band.",
    },
    "eclipse_solar_style": {
        "bite": "A bite is taken out of the Sun by the Moon's disc.",
        "magnitude_arc": "An arc whose length states how deep the eclipse goes.",
        "halo": "Only the corona halo is drawn, without cutting the disc.",
        "totality_path": "The totality path across the globe (no painter yet — the tile stands for the sealed design).",
        "type_emblem": "A small emblem naming the eclipse type (no painter yet — the tile stands for the sealed design).",
        "dial_shadow": "The whole dial darkens with the eclipse (no painter yet — the tile stands for the sealed design).",
    },
    "eclipse_lunar_style": {
        "umbra_sweep": "The Earth's umbra sweeps visibly across the Moon's face.",
        "horizon_shadow": "The shadow is shown on the horizon band rather than the disc.",
        "halo": "Only a halo marks the eclipse, the disc stays whole.",
        "blood_moon": "The Moon reddens through totality (no painter yet — the tile stands for the sealed design).",
        "danjon_scale": "The Danjon darkness value is stated beside the Moon (no painter yet — the tile stands for the sealed design).",
        "contact_marks": "The four contact moments are marked (no painter yet — the tile stands for the sealed design).",
    },
    "moon_station_style": {
        "arc_grammar": "Each station wears its own arc, so the four read apart at a glance.",
        "inner_glow": "The stations are marked by a glow inside the disc.",
        "uniform": "One identical halo marks every station.",
    },
    "sun_station_style": {
        "arc_grammar": "Each solstice and equinox wears its own arc grammar.",
        "uniform_seasonal": "One halo per station, colored by the season it opens.",
        "day_night_wedge": "A wedge stating the day/night balance at that station.",
        "uniform_gold": "One gold halo for all four, the quietest option.",
    },
}


def build(settings, setters: dict, tr) -> QWidget:
    """THE PAGE SPLIT (owner ballot verdict 5D, 2026-08-14): this page
    was the only one running past two screens — Hands/Earth/Moon stay
    here, Eclipses + Stations moved to their own sidebar page
    (`build_eclipses`)."""
    layout = QVBoxLayout()
    layout.addWidget(_hands_group(settings, setters, tr))
    for group in _earth_groups(settings, setters, tr):
        layout.addWidget(group)
    for group in _moon_groups(settings, setters, tr):
        layout.addWidget(group)
    widget = QWidget()
    widget.setLayout(layout)
    return widget


def build_eclipses(settings, setters: dict, tr) -> QWidget:
    """The split's second half (verdict 5D): how the two eclipse kinds
    draw, and the Moon/Sun station marks."""
    layout = QVBoxLayout()
    for group in (
        _eclipse_groups(settings, setters, tr)
        + _station_groups(settings, setters, tr)
    ):
        layout.addWidget(group)
    widget = QWidget()
    widget.setLayout(layout)
    return widget


def _styles(family: str, keys, titles, icon_of, tr):
    """The `(key, label, blurb, icon)` entries of one style family —
    labels and blurbs both translated, icons from THE REAL RENDER
    FUNCTION (this module's own standing rule)."""
    return [
        (key, tr(titles[key]), tr(_BLURBS[family][key]), icon_of(key))
        for key in keys
    ]


def _hands_group(settings, setters, tr):
    """R-14, moved verbatim from the retired `hands.py`: one LARGE card
    per hand pack, its OWN hours-hand image as the icon."""
    packs = hand_packs()
    entries = [
        (
            name, tr(name),
            tr("The {pack} hand pack — its own hour and minute art.").format(
                pack=name
            ),
            thumbs.art_thumbnail(packs[name]["files"]["hours"]),
        )
        for name in sorted(packs)
    ]
    return picture_group(
        tr("Hands"), tr("Which image draws the hour hand."),
        entries, settings.hands, setters["hands"],
    )


def _earth_groups(settings, setters, tr) -> list:
    """R-06, moved verbatim from `pointer.py`'s `_earth_group`, plus the
    position-pointer SHAPE gallery (owner verdict 2026-08-10: the Moon
    and the Earth's own markers are HANDS).

    FLATTENED by the CardGroup migration (2026-08-14): each titled card
    gallery is now a group of its own instead of a second QGroupBox
    nested inside an "Earth" box — a box inside a box reads as a defect,
    and every CardGroup already carries the title and the sentence the
    inner label used to supply."""
    globe = picture_group(
        tr("Earth globe"), tr("What the Earth marker's globe looks like."),
        [
            (
                style, tr(title), tr(_BLURBS["earth_style"][style]),
                thumbs.art_thumbnail(
                    continents.EARTH_ART_DIR / f"earth_{style}_europe_day.png"
                ),
            )
            for style, title in (("clean", "Clean"), ("atmo", "Atmosphere"))
        ],
        settings.earth_style, setters["earth_style"],
    )
    group = QGroupBox(tr("Earth marker"))
    column = QVBoxLayout(group)
    label_row = QHBoxLayout()
    enabled = settings.diameter >= dial.FULL_TEXT_MIN_DIAMETER
    for mode, title in (
        ("date", "Date"), ("weekday", "Weekday"),
        ("date_weekday", "Date & Weekday"), ("full", "Full Date"),
    ):
        is_active = settings.earth_label == mode
        button = pill(
            tr(title), is_active,
            lambda m=mode, was=is_active: setters["earth_label"](m, not was),
        )
        button.setEnabled(enabled)
        label_row.addWidget(button)
    column.addWidget(QLabel(tr("What text the Earth marker shows.")))
    column.addLayout(label_row)
    pointer_checkbox = QCheckBox(tr("Position pointer"))
    pointer_checkbox.setChecked(settings.show_marker_pointer)
    pointer_checkbox.toggled.connect(setters["show_marker_pointer"])
    column.addWidget(pointer_checkbox)
    shapes = picture_group(
        tr("Position pointer shape"),
        tr("Shape of the small pointer at the body's own angle."),
        _styles(
            "marker_pointer_shape", constants.MARKER_POINTER_SHAPES,
            _MARKER_POINTER_SHAPE_TITLES, thumbs.marker_pointer_shape_icon, tr,
        ),
        settings.marker_pointer_shape, setters["marker_pointer_shape"],
    )
    if not settings.show_marker_pointer:
        # The graceful gate (never hidden, always with its reason) —
        # the pattern `CardGroup.disable_with_reason` was built for.
        shapes.disable_with_reason(tr(
            "There is no pointer to shape while Position pointer is off."
        ))
    return [globe, group, shapes]


def _moon_groups(settings, setters, tr) -> list:
    """The unlit-half style, the Earth-crossing switches, and the Moon
    Horizon Band (owner verdict 2026-08-09, moved here 2026-08-10 —
    "everything Moon-related in one place"), each its own CardGroup
    since the 2026-08-14 migration."""
    groups = [picture_group(
        tr("Moon — unlit half"), tr("How the unlit half of the Moon is drawn."),
        _styles(
            "moon_dark_style", constants.MOON_DARK_STYLES, _MOON_DARK_TITLES,
            thumbs.moon_dark_style_icon, tr,
        ),
        settings.moon_dark_style, setters["moon_dark_style"],
    )]
    # THE CROSSING SWITCHES (owner ballot verdict 2026-08-11, corrected
    # the same day: the ORIGINAL three picture tiles stay — each one
    # behavior — only the one-of rule falls away): every card is an
    # independent SWITCH (green border, the kind's own vocabulary since
    # the classes landed) rendered by THE REAL RENDER FUNCTION, any mix
    # may be lit; with none lit the plain Moon simply passes over.
    groups.append(picture_group(
        tr("Moon — crossing the Earth"),
        tr("What happens when the Moon meets the Earth (any mix; none = a plain pass)."),
        [], None, None,
        switches=[
            (
                field, tr(title), tr(_BLURBS["moon_transit"][field]),
                thumbs.moon_transit_style_icon(icon_style),
                getattr(settings, field),
            )
            for field, icon_style, title in (
                ("transit_shadow", "occultation", "Cast a shadow"),
                ("transit_shrink", "shrink_pass", "Shrink"),
                ("transit_rim", "lane_split", "Ride the rim"),
            )
        ],
        on_toggle=lambda key, on: setters[key](on),
    ))
    groups.append(picture_group(
        tr("Moon — horizon band"),
        tr("Whether an arc shows when the Moon stands above the horizon."),
        _styles(
            "moon_band_mode", constants.MOON_BAND_MODES, _MOON_BAND_MODE_TITLES,
            thumbs.moon_band_mode_icon, tr,
        ),
        settings.moon_band_mode, setters["moon_band_mode"],
    ))
    if settings.moon_band_mode == "horizon":
        groups.append(picture_group(
            tr("Moon — band style"), tr("How the horizon band itself is drawn."),
            _styles(
                "moon_band_style", constants.MOON_BAND_STYLES,
                _MOON_BAND_STYLE_TITLES, thumbs.moon_band_style_icon, tr,
            ),
            settings.moon_band_style, setters["moon_band_style"],
        ))
    return groups


def _eclipse_groups(settings, setters, tr) -> list:
    return [
        picture_group(
            tr("Solar eclipses"),
            tr("How a solar eclipse is drawn on the Earth marker."),
            _styles(
                "eclipse_solar_style", constants.ECLIPSE_SOLAR_STYLES,
                _ECLIPSE_SOLAR_TITLES, thumbs.eclipse_solar_style_icon, tr,
            ),
            settings.eclipse_solar_style, setters["eclipse_solar_style"],
        ),
        picture_group(
            tr("Lunar eclipses"),
            tr("How a lunar eclipse is drawn on the Moon marker."),
            _styles(
                "eclipse_lunar_style", constants.ECLIPSE_LUNAR_STYLES,
                _ECLIPSE_LUNAR_TITLES, thumbs.eclipse_lunar_style_icon, tr,
            ),
            settings.eclipse_lunar_style, setters["eclipse_lunar_style"],
        ),
    ]


def _station_groups(settings, setters, tr) -> list:
    return [
        picture_group(
            tr("Moon stations"),
            tr("How the Moon's birth/youth/zenith/age marks are drawn."),
            _styles(
                "moon_station_style", constants.MOON_STATION_STYLES,
                _MOON_STATION_TITLES, thumbs.moon_station_style_icon, tr,
            ),
            settings.moon_station_style, setters["moon_station_style"],
        ),
        picture_group(
            tr("Sun stations"),
            tr("How the Sun's solstice/equinox life-arc marks are drawn."),
            _styles(
                "sun_station_style", constants.SUN_STATION_STYLES,
                _SUN_STATION_TITLES, thumbs.sun_station_style_icon, tr,
            ),
            settings.sun_station_style, setters["sun_station_style"],
        ),
    ]
