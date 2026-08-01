# Manifest

**Script:** [Manifest (script)](../manifest.py) · **Flow:** [diagram](../__flow/manifest.md)

## Purpose

Typed, Qt-free render configuration — the six unit specs (background,
star, ring, weekday_set, year_marker, hands) plus `SkinDefinition`'s
user-overridable display scalars. Pure dataclasses with no I/O:
`config.defaults.DEFAULT_SKIN` is the one canonical instance; the app
controller's `build_skin` overlays the ring PRESET (DOMY/PILOT are ring
preset NAMES — nothing more) and the user's display choices onto it at
build time.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `constants` (default
  values: `POINTER_SHAPE_DEFAULT`, `POLYGON_CURVATURE_DEFAULT`,
  `POLYGON_EDGE_DEFAULT`), `palette`, `paths` (`DisplayContext`,
  `DEFAULT_DISPLAY`)

### Used by
- [Config (folder)](../../config/___config.md) — `DEFAULT_SKIN` is built
  from these dataclasses (`config/defaults.py`)
- [Render (folder)](../../render/___render.md) — `compositor.py` and
  `layers.py` read `SkinDefinition`/`HandSpec` at render time
- [Watch Controller](../../app/__about/controller.md) — `build_skin` assembles
  the active skin; `missing_assets` is checked at startup

## Classes

### `BackgroundSpec`
The two background wheels: the UMBRA (gray brightness wheel) and the
AURA (transparent period-hue wedges over the sunlit part of the day);
both rotate with the star. `base_asset=None` draws the 30-section Umbra
procedurally — single lightest/darkest sections centered on noon/midnight.
#### Attributes
- `base_asset: Path | None` — custom Umbra art; `None` -> procedural
- `day_alpha`, `twilight_alpha: float` — Aura opacity, sunlit arc / dawn-dusk bands
- `umbra_radius_fraction`, `aura_radius_fraction: float` — of the dial radius

### `StarSpec`
Procedural N-diamond star (owner decision: simple geometry drawn at
runtime, not shipped as an image). Fills appear only where the sun is
up; the colored borders run the full circle so night diamonds stay
recognizable.
#### Attributes
- `day_alpha`, `twilight_alpha`, `border_alpha: float`
- `border_width_fraction`, `radius_fraction: float` — of the dial radius

### `RingSpec`
The dial ring: a full image, or a procedural fallback with per-hour
letter substitutions.
#### Attributes
- `asset: Path | None` — full ring image; `None` -> procedural
- `fill`, `text_color`, `letter_color: str`
- `width_fraction: float` — ring thickness, of the dial radius
- `letters: dict[int, str]` — hour -> letter replacing the numeral
- `letter_art: dict[int, Path]` — hour -> the GOLD master letter file
  (built by `build_skin`; the ring tint never touches it)
- `letter_metal: dict[int, str]` — hour -> active finish
  (`"gold"`/`"silver"`/`"bronze"`); silver/bronze are derived from the
  gold master at load time (`render.asset_recolor.letter_metal_file`)
- `letter_zoom: dict[int, float]` — hour -> height multiplier (absent =
  1.0) for seats whose art pads the glyph with extra rays (e.g. the
  Eye's shine masters)
- `letter_legend: dict[int, dict]` — hour -> `{name, reading}`, the
  per-letter hover legend (empty for presets that carry none)
- `motto: tuple[dict, ...]` — the outer motto arc: one
  `{"text", "glyphs": ((asset, angle), ...), "words": [...]}` entry per
  preset that has one, built by `build_skin` from the preset's `motto`
  card field; empty for presets without one
- `motto_metal: str = "gold"` — the single finish every motto glyph wears

### `WeekdaySpec`
One weekday theme's seven bodies.
#### Attributes
- `bodies: dict[str, Path | None]` — body name -> image, `None` -> procedural disc
- `body_names: dict[str, str]` — display names for hover
- `body_colors: dict[str, str]` — procedural disc colors
- `display_mode: str` — `"ghost"` | `"center_only"`
- `ghost_opacity`, `center_scale`, `diamond_scale`, `orbit_fraction: float`
- `metal: str | None = None` — theme metal swap (bronze-plate themes
  only): `"gold"`/`"silver"` run the hue-selective recolor at render
  (only the warm bronze pixels change); `None` = bronze as drawn
- `dual_asset: Path | None = None` — the theme's Sunday SERVANT face,
  resolved with the metal in `apply_display_settings`
- `article_set: str | None = None` — hover article set name (roster override)
- `body_articles: dict | None = None` — per-body `(set, body)` override
  for seats that fell back to a planetary figure
- `dual_names: tuple | None = None` — the Sunday pair's hover names

### `YearMarkerSpec`
Date markers on the inside of the dial: Earth rides the solstice-
calibrated year wheel; the Moon rides its own cycle (new moon at top,
full moon at bottom, clockwise). Which is drawn comes from the Elements
switches (`show_earth` / `show_moon`).
#### Attributes
- `variants: dict[str, Path]` — e.g. `"europe_day"`/`"europe_night"` -> image
- `default_variant: str`
- `day_color`, `night_color: str` — procedural Earth fallbacks
- `orbit_fraction`, `scale: float` — Earth orbit / size
- `moon_asset: Path | None`, `moon_lit_color`, `moon_dark_color: str`
- `moon_shadow_alpha: float` — darkness of the unlit part over the image
- `moon_orbit_fraction`, `moon_scale: float` — smaller than the Earth (~72%)
- `moon_hidden_alpha: float = 0.5` — marker opacity while below the horizon

### `HandSpec`
One hand image pointing UP with its rotation pivot, both in the image's
own units (pixels, or viewBox units for SVG).
#### Attributes
- `asset: Path`
- `natural_height: float` — full image height
- `pivot_y: float` — rotation center above the image bottom
- `pivot_x_fraction: float | None = None` — of the width; `None` = centered

### `HandsSpec`
A hand pack resolved for the renderer. Sizing uses TIP-TO-PIVOT lengths
only: the seconds tip reaches `second_reach_fraction` of the dial
radius, minutes `minute_reach_fraction`, hours follow the pack's own
hour/minute tip ratio.
#### Attributes
- `hour`, `minute: HandSpec`
- `minute_reach_fraction`, `second_reach_fraction: float`
- `second: HandSpec | None = None`
- `z_order: tuple[str, ...] = ("hours", "minutes", "seconds")` — bottom-up
- `desaturate: bool = False` — gray colored user art so the clock tint can recolor it

### `SkinDefinition`
The whole skin: the six specs above, plus every user-overridable display
scalar (tray/settings always win over whatever the pack declares — the
controller's `_apply_display_settings`). Structural fields: `z_order`,
`background`, `star`, `ring`, `weekday_set`, `year_marker`, `hands`. The
display scalars, grouped by concern (see the [schema tree](../__flow/manifest.md)
for the full field-by-field default/meaning table):

- **Pointer & palette** — `pointer` (which of the 7 wheels:
  `config.constants.POINTER_POINTS`), `pointer_shape`, `polygon_curvature`,
  `polygon_edge`, `palette_style`, `cube_look`, `daylight`,
  `hide_night_borders`, `solar_rotation`, `archetype_mode`,
  `archetype_names`, `pointer_saturation`, `ring_saturation`,
  `calendar_mount`
- **Umbra** — `umbra_form` (`"fine"` 30-section | `"coarse"` 24-section |
  `"gradient"`), `umbra_contrast` (`"full"` | `"half"` shade span)
- **Slots** — `octa_slot`, `day_slot_style`/`info_slot_style`/`third_slot_style`,
  `info_slot_theme`/`third_slot_theme`, `info_slot_metal`/`third_slot_metal`,
  `info_slot_roster`/`third_slot_roster`, `weekday_slot`, `third_slot`,
  `show_third_slot`, `show_octa_slot`
- **Elements switches** — `show_earth`, `show_moon`, `show_weekday`,
  `show_pointer`, `show_seconds`, `colorful`, `earth_style`,
  `earth_label`, `weekday_theme`, `show_weekday_names`,
  `show_info_slot_names`, `legend`
- **Ring** — `ring_tint`, `ring_finish`, `ring_letter_scale`, `subdial_style`
- **Year line** — `era_notation`, `show_era_suffix`, `third_era`
  (consumed by `core.deep_time.format_year_line`/`format_official`)
- **Display context & runtime-only** — `display: paths.DisplayContext`
  (this watch's own art source, subdial plate set and metal shades;
  installed via `with paths.display(skin.display)` before any art
  resolves — owner bug 2026-07-28, multi-watch color leak),
  `hover_enlarge`, `palette_override` (the user's custom hues; never
  serialized to `skin.json`)

## Functions

### `missing_assets(skin) -> list[Path]`
Every asset the skin references (background, ring, moon, hands, ring
letter art and motto glyphs, weekday bodies, year-marker variants) that
does not exist on disk, resolved through the active art source
(`paths.art_file`). The caller must surface a non-empty result visibly —
a missing asset would otherwise fail inside `paintEvent`, where Qt
swallows the exception and leaves a silently broken dial.
