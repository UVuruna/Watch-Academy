# Manifest

**Script:** [Manifest (script)](manifest.py)

## Purpose
The typed render configuration — six unit specs (background, star,
ring, weekday_set, year_marker, hands). Pure dataclasses with no I/O:
`DEFAULT_SKIN` in config is the one instance; the controller overlays
the ring preset and the user's display choices onto it at build time.

## Connections

### Uses
- Nothing (stdlib dataclasses only — importable from anywhere)

### Used by
- [Config (folder)](../config/___config.md) — `DEFAULT_SKIN`
- [Render (folder)](../render/___render.md) — layers read the specs

## Classes

- `SkinDefinition` — `z_order`, one spec per unit, plus the
  user-overridable display scalars (the tray choice always wins):
  `pointer` ("hexa" | "cross" | "octa" | "trio" | "aurora" |
  "calendar"), `umbra_form` ("fine" |
  "coarse" | "gradient"), `umbra_contrast` ("full" | "half"),
  `palette_style` ("paint" | "light" — on the Calendar pointer it PICKS
  THE WHEEL: paint = Zodiac, light = Almanac, owner 2026-07-16),
  `calendar_lighting` ("hour" the shichen | "year" the month/sign wedge),
  `archetype_mode` (owner sealed package 2026-07-16 — the active
  (pointer, palette_style) shows ITS archetype: figures in the
  diamonds, the hour hand lighting the current hour-space, the weekday
  model and all three slots overridden OFF at the RENDER level so the
  slot fields below keep the user's choices) and `earth_weekday`
  (the optional abbreviated day under the Earth marker's date — a
  GENERAL Earth option since 2026-07-17, working in BOTH normal and
  archetype mode; renamed from `archetype_earth_day`, default False),
  `solar_rotation` (False →
  Star/Aura/Umbra stand upright), `octa_slot` (one of
  `OCTA_SLOT_MODES`: time/date/day length, tropical zodiac as
  text/sign/logo/constellation, Chinese zodiac as text/logo),
  `earth_style` ("clean" | "atmo") and the six Elements switches
  (`show_earth`, `show_moon`, `show_weekday`, `show_pointer`,
  `colorful` — off draws the Aura as plain white transparency —
  and `show_seconds`), the ring recolor pair: `ring_tint`
  (#RRGGBB multiplying ring art + hands + Umbra; None = gray art) and
  `ring_finish` ("gold" | "silver" | "bronze" letter art — the layout
  triangle wears the finish, the accent letter the opposite metal,
  bronze's accent silver), the seated slots' own looks
  (`info_slot_theme`/`info_slot_metal`/`info_slot_roster` and the
  `third_slot_*` mirror — the roster is PER SLOT, owner 2026-07-15:
  "planetary" | "pantheon" picked in the theme's own dropdown, so the
  same theme can sit twice with two casts), the YEAR LINE trio
  (Session 16, owner amendment 2026-07-17): `era_notation` /
  `show_era_suffix` / `third_era` — consumed by
  `core.deep_time.format_year_line` (hovers pair the official year
  with Anno Lucis) and `format_official` (the compact dial texts),
  plus `octa_slot_scale` and `hover_enlarge` (owner EXTRAS; the
  Earth/Moon/Weekday size multipliers scale their spec values in
  apply_display_settings instead)
- `BackgroundSpec` — the Umbra (custom art, or None for the procedural
  30-section wheel: single lightest/darkest sections centered on
  noon/midnight) + the Aura (transparent period hues from the palette
  preset, drawn only over the sunlit arc; day/twilight alphas)
- `StarSpec` — PROCEDURAL N-diamond star (owner decision: simple
  geometry is drawn at runtime, no image file): day/twilight alphas,
  full-circle border alpha/width, tip radius; colors come from the
  palette preset shared with the Aura
- `RingSpec` — full ring image (numerals baked in) or procedural
  fallback with per-hour letter substitutions (M-12, D-4, Ω-0, Y-20);
  `letter_art` (hour → resolved gold/silver/bronze PNG, built by
  build_skin for the active finish) is overlaid on the art so the ring
  TINT never touches the letters
- `WeekdaySpec` — body images/colors, white weekday label on top,
  display mode (ghost / center_only), ghost opacity, sizes, orbit,
  and the theme `metal` (owner 2026-07-12: "gold"/"silver" run the
  hue-SELECTIVE swap at render — only the warm bronze pixels change,
  the gray stone and engravings stay; None = bronze, as drawn); the
  PANTHEON roster dress adds `article_set`, `body_articles` (body →
  (set, body) the hover reads, so fallen-back seats keep planetary
  text) and `dual_names` (the Sunday pair as seated)
- `YearMarkerSpec` — Earth day+night variants per continent on the year
  wheel; Moon on its own cycle (new at top, full at bottom) with the
  unlit part shadowed; separate orbits. Which marker is drawn comes
  from the Elements switches (`show_earth` / `show_moon`)
- `HandSpec` / `HandsSpec` — hand canvases at their exact designed sizes
  (hub 15 design units above the bottom), ONE shared reach scale

## Functions

- `missing_assets(skin)`: referenced-but-absent files (surfaced visibly
  at startup — a miss inside paintEvent would be swallowed by Qt)
