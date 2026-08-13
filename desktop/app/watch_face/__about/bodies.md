# Hands & Bodies Section

**Script:** [Hands & Bodies Section (script)](../bodies.py) · **Flow:** [diagram](../__flow/bodies.md)

## Purpose
The Watch Face window's "Hands & Bodies" page (owner verdict 2026-08-10,
ruling on the rendering-proposals page): the Moon and the Earth are
part of the HANDS system — "they are what MOVES and points" — so every
menu about how they are drawn is presented here, beside the hand-pack
gallery, instead of scattered through Pointer/Opacity. Replaces the
RETIRED `hands.py` (R-14's gallery moved here verbatim) and absorbs the
Earth group out of `pointer.py` and the Moon Horizon Band out of
`opacity.py`.

Five named `QGroupBox` groups, each gallery under its own one-line
plain-language `QLabel`:

- **Hands** — the hand-pack gallery, unchanged from the retired module.
- **Earth** — the style/label/"Position pointer" rows moved verbatim
  from `pointer.py`'s `_earth_group`, plus the position-pointer SHAPE
  gallery (`marker_pointer_shape`, `constants.MARKER_POINTER_SHAPES`),
  enabled only while "Position pointer" is checked.
- **Moon** — the unlit-half style (`moon_dark_style`), the
  Earth-crossing style (`moon_transit_style`), and the Moon Horizon
  Band's mode + style galleries, moved from `opacity.py`'s
  `_moon_band_group`.
- **Eclipses** — the solar (`eclipse_solar_style`) and lunar
  (`eclipse_lunar_style`) treatments; 6 names each since the owner's
  2026-08-13 ballot, three per kind with no painter of their own yet
  (see [Eclipse Style Door](../../../render/__about/eclipse_style.md)).
- **Stations** — the Moon's (`moon_station_style`) and the Sun's
  (`sun_station_style`) four-life-stage marks.

Every tile's icon is THE REAL RENDER FUNCTION at thumbnail scale
(`thumbs.py`) — never a redrawn sketch, the same discipline the
pre-existing Umbra and Moon Horizon Band galleries already followed.

## Connections

### Uses
- [Watch Face Thumbnails](thumbs.md) — `art_thumbnail` (hand packs,
  Earth style tiles), `moon_dark_style_icon`, `moon_transit_style_icon`,
  `marker_pointer_shape_icon`, `eclipse_solar_style_icon`,
  `eclipse_lunar_style_icon`, `moon_station_style_icon`,
  `sun_station_style_icon`, `moon_band_mode_icon`, `moon_band_style_icon`
- [Watch Face Shared Widgets](widgets.md) — `tile`, `pill`, `flow_gallery`
- [Hands (data)](../../../data/__about/hands.md) — `hand_packs`
- [Config (folder)](../../../config/___config.md) — `constants.
  MOON_DARK_STYLES`, `MOON_TRANSIT_STYLES`, `MARKER_POINTER_SHAPES`,
  `ECLIPSE_SOLAR_STYLES`, `ECLIPSE_LUNAR_STYLES`, `MOON_STATION_STYLES`,
  `SUN_STATION_STYLES`, `MOON_BAND_MODES`, `MOON_BAND_STYLES`;
  `continents.EARTH_ART_DIR`; `dial.FULL_TEXT_MIN_DIAMETER`

### Used by
- `app.watch_face.window` — registered as the Hands & Bodies section's
  builder

## Design Decisions
- **Every scalar pick** routes through the controller's shared
  `_set_display_choice(key, value)` via `constants.MOVING_BODY_MENUS`'
  roster (Rule #5) — this module never writes a setter method of its
  own for any of the seven moving-body menus.
- **The position-pointer shape gallery is disabled, not hidden**, while
  "Position pointer" is off — the owner's own "greyed out" convention
  used elsewhere (e.g. `opacity.py`'s Crown Text row) rather than a
  layout that reflows every time the checkbox toggles.
