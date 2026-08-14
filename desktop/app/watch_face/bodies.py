"""Hands & Bodies section (owner verdict 2026-08-10, see bodies.md) —
the Watch Face window's "Hands & Bodies" page: the hand-pack gallery
(R-14, moved verbatim from the RETIRED `hands.py`) plus every menu that
decides how the Moon and the Earth are drawn, because the owner ruled
on the rendering-proposals page that "they are what MOVES and points" —
the same family as the hour/minute hands, not scattered across
Pointer/Opacity.

Five named `QGroupBox` groups, each with a one-line explanatory label
above its own gallery (plain language, not the terse constant name):

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
from app.watch_face.widgets import flow_gallery, pill, tile
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


def build(settings, setters: dict, tr) -> QWidget:
    """THE PAGE SPLIT (owner ballot verdict 5D, 2026-08-14): this page
    was the only one running past two screens — Hands/Earth/Moon stay
    here, Eclipses + Stations moved to their own sidebar page
    (`build_eclipses`)."""
    layout = QVBoxLayout()
    layout.addWidget(_hands_group(settings, setters, tr))
    layout.addWidget(_earth_group(settings, setters, tr))
    layout.addWidget(_moon_group(settings, setters, tr))
    widget = QWidget()
    widget.setLayout(layout)
    return widget


def build_eclipses(settings, setters: dict, tr) -> QWidget:
    """The split's second half (verdict 5D): how the two eclipse kinds
    draw, and the Moon/Sun station marks."""
    layout = QVBoxLayout()
    layout.addWidget(_eclipses_group(settings, setters, tr))
    layout.addWidget(_stations_group(settings, setters, tr))
    widget = QWidget()
    widget.setLayout(layout)
    return widget


def _labeled_gallery(column: QVBoxLayout, tr, text: str, tiles) -> None:
    column.addWidget(QLabel(tr(text)))
    column.addWidget(flow_gallery(tiles))


def _hands_group(settings, setters, tr) -> QGroupBox:
    """R-14, moved verbatim from the retired `hands.py`: one LARGE tile
    per hand pack, its OWN hours-hand image as the icon."""
    group = QGroupBox(tr("Hands"))
    column = QVBoxLayout(group)
    packs = hand_packs()
    tiles = [
        tile(
            tr(name),
            thumbs.art_thumbnail(packs[name]["files"]["hours"]),
            settings.hands == name,
            lambda n=name: setters["hands"](n),
        )
        for name in sorted(packs)
    ]
    _labeled_gallery(column, tr, "Which image draws the hour hand.", tiles)
    return group


def _earth_group(settings, setters, tr) -> QGroupBox:
    """R-06, moved verbatim from `pointer.py`'s `_earth_group`, plus the
    position-pointer SHAPE gallery (owner verdict 2026-08-10: the Moon
    and the Earth's own markers are HANDS)."""
    group = QGroupBox(tr("Earth"))
    column = QVBoxLayout(group)
    style_tiles = []
    for style, title in (("clean", "Clean"), ("atmo", "Atmosphere")):
        icon = thumbs.art_thumbnail(
            continents.EARTH_ART_DIR / f"earth_{style}_europe_day.png"
        )
        style_tiles.append(tile(
            tr(title), icon, settings.earth_style == style,
            lambda s=style: setters["earth_style"](s),
        ))
    _labeled_gallery(
        column, tr, "What the Earth marker's globe looks like.", style_tiles
    )
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
    shape_tiles = [
        tile(
            tr(_MARKER_POINTER_SHAPE_TITLES[shape]),
            thumbs.marker_pointer_shape_icon(shape),
            settings.marker_pointer_shape == shape,
            lambda s=shape: setters["marker_pointer_shape"](s),
        )
        for shape in constants.MARKER_POINTER_SHAPES
    ]
    shape_label = QLabel(tr(
        "Shape of the small pointer at the body's own angle "
        "(only while Position pointer is on)."
    ))
    shape_gallery = flow_gallery(shape_tiles)
    shape_label.setEnabled(settings.show_marker_pointer)
    shape_gallery.setEnabled(settings.show_marker_pointer)
    column.addWidget(shape_label)
    column.addWidget(shape_gallery)
    return group


def _moon_group(settings, setters, tr) -> QGroupBox:
    """The unlit-half style, the Earth-crossing style, and the Moon
    Horizon Band (owner verdict 2026-08-09, moved here 2026-08-10 —
    "everything Moon-related in one place")."""
    group = QGroupBox(tr("Moon"))
    column = QVBoxLayout(group)
    dark_tiles = [
        tile(
            tr(_MOON_DARK_TITLES[style]), thumbs.moon_dark_style_icon(style),
            settings.moon_dark_style == style,
            lambda s=style: setters["moon_dark_style"](s),
        )
        for style in constants.MOON_DARK_STYLES
    ]
    _labeled_gallery(
        column, tr, "How the unlit half of the Moon is drawn.", dark_tiles
    )
    # THE CROSSING SWITCHES (owner ballot verdict 2026-08-11, corrected
    # the same day: the ORIGINAL three picture tiles stay — each one
    # behavior — only the one-of rule falls away): every tile is an
    # independent toggle rendered by THE REAL RENDER FUNCTION
    # (`thumbs.moon_transit_style_icon`, the pre-existing icons), any
    # mix may be lit, all three by default; with none lit the plain
    # Moon simply passes over the Earth.
    transit_tiles = [
        tile(
            tr(title), thumbs.moon_transit_style_icon(icon_style),
            getattr(settings, field),
            lambda f=field, was=getattr(settings, field): setters[f](not was),
        )
        for field, icon_style, title in (
            ("transit_shadow", "occultation", "Cast a shadow"),
            ("transit_shrink", "shrink_pass", "Shrink"),
            ("transit_rim", "lane_split", "Ride the rim"),
        )
    ]
    _labeled_gallery(
        column, tr,
        "What happens when the Moon meets the Earth (any mix; none = a plain pass).",
        transit_tiles,
    )
    mode_tiles = [
        tile(
            tr(_MOON_BAND_MODE_TITLES[mode]), thumbs.moon_band_mode_icon(mode),
            settings.moon_band_mode == mode,
            lambda m=mode: setters["moon_band_mode"](m),
        )
        for mode in constants.MOON_BAND_MODES
    ]
    _labeled_gallery(
        column, tr,
        "Whether an arc shows when the Moon stands above the horizon.",
        mode_tiles,
    )
    if settings.moon_band_mode == "horizon":
        style_tiles = [
            tile(
                tr(_MOON_BAND_STYLE_TITLES[style]),
                thumbs.moon_band_style_icon(style),
                settings.moon_band_style == style,
                lambda s=style: setters["moon_band_style"](s),
            )
            for style in constants.MOON_BAND_STYLES
        ]
        _labeled_gallery(
            column, tr, "How the horizon band itself is drawn.", style_tiles
        )
    return group


def _eclipses_group(settings, setters, tr) -> QGroupBox:
    group = QGroupBox(tr("Eclipses"))
    column = QVBoxLayout(group)
    solar_tiles = [
        tile(
            tr(_ECLIPSE_SOLAR_TITLES[style]),
            thumbs.eclipse_solar_style_icon(style),
            settings.eclipse_solar_style == style,
            lambda s=style: setters["eclipse_solar_style"](s),
        )
        for style in constants.ECLIPSE_SOLAR_STYLES
    ]
    _labeled_gallery(
        column, tr, "How a solar eclipse is drawn on the Earth marker.",
        solar_tiles,
    )
    lunar_tiles = [
        tile(
            tr(_ECLIPSE_LUNAR_TITLES[style]),
            thumbs.eclipse_lunar_style_icon(style),
            settings.eclipse_lunar_style == style,
            lambda s=style: setters["eclipse_lunar_style"](s),
        )
        for style in constants.ECLIPSE_LUNAR_STYLES
    ]
    _labeled_gallery(
        column, tr, "How a lunar eclipse is drawn on the Moon marker.",
        lunar_tiles,
    )
    return group


def _stations_group(settings, setters, tr) -> QGroupBox:
    group = QGroupBox(tr("Stations"))
    column = QVBoxLayout(group)
    moon_tiles = [
        tile(
            tr(_MOON_STATION_TITLES[style]),
            thumbs.moon_station_style_icon(style),
            settings.moon_station_style == style,
            lambda s=style: setters["moon_station_style"](s),
        )
        for style in constants.MOON_STATION_STYLES
    ]
    _labeled_gallery(
        column, tr,
        "How the Moon's birth/youth/zenith/age marks are drawn.",
        moon_tiles,
    )
    sun_tiles = [
        tile(
            tr(_SUN_STATION_TITLES[style]),
            thumbs.sun_station_style_icon(style),
            settings.sun_station_style == style,
            lambda s=style: setters["sun_station_style"](s),
        )
        for style in constants.SUN_STATION_STYLES
    ]
    _labeled_gallery(
        column, tr,
        "How the Sun's solstice/equinox life-arc marks are drawn.",
        sun_tiles,
    )
    return group
