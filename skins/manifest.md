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
  `pointer` ("hexa" | "cross" | "octa" | "trio" | "rose" | "aurora" |
  "calendar" — "rose" is the seventh, three octa stars 15° apart, owner
  2026-07-27, CUBE.md §The Rose), `umbra_form` ("fine" |
  "coarse" | "gradient"), `umbra_contrast` ("full" | "half"),
  `palette_style` ("primary" | "secondary" | "tertiary" — the third is the Cube
  canon's wheel, Genesis/Council/Character on trio/hexa/octa ONLY
  (owner seal 2026-07-26, CUBE.md; `defaults.effective_palette_style`
  normalizes it away elsewhere); on the Calendar pointer the style
  PICKS THE WHEEL: paint = Zodiac, light = Almanac, owner 2026-07-16),
  `cube_look` (the Diamond/Cube display toggle, CUBE.md §Display laws
  — the Double-Trinity family wheels render as the corner-view cube
  when True; `render.layers.cube_look_active`/`arm_half_deg`),
  `daylight` (owner 2026-07-27, CUBE.md §The Rose — the Calendar and
  the Rose may stand in flat full colour instead of the day/night
  law; inert on the other five, `render.layers.daylight_active`),
  `pointer_shape` ("star" | "polygon", Pointers REWORK phase 1, owner
  sheet 2026-07-29 — the drawn wheel is the diamond star or the plain
  polygon of the same arms; see
  [The Pointer Shapes](../render/layers.md#the-pointer-shapes)),
  `polygon_curvature` (0.0–1.0) and `polygon_edge` ("smooth" |
  "notched") — the outer edges' inward pull and its two forms, read
  only on the four TRUE polygons (`render.layers.polygon_curvature`),
  `hide_night_borders` (False — the arm/polygon outline strokes drawn
  over the sunlit arcs only, `render.layers.border_clips`),
  `calendar_mount` ("off" or any `defaults.CALENDAR_MOUNTS` key — WHICH
  roster rides the Calendar's twelve wedges; its `calendar_lighting`
  sibling was DELETED with the lit-wedge feature, owner decree
  2026-07-29),
  `archetype_mode` (owner sealed package 2026-07-16 — the active
  (pointer, palette_style) shows ITS archetype: figures in the
  diamonds, the hour hand lighting the current hour-space, the weekday
  model and all three slots overridden OFF at the RENDER level so the
  slot fields below keep the user's choices) and `earth_label`
  (owner 2026-07-18, ROADMAP 15h — the Earth marker's label MODE,
  `constants.EARTH_LABEL_MODES`: "off" | "date" | "weekday" |
  "date_weekday" | "full", default "date"; replaces the old
  `show_earth_date`/`earth_weekday` bool pair — a GENERAL Earth option,
  working in BOTH normal and archetype mode),
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
  TINT never touches the letters; `letter_legend` (hour → {name,
  reading}) the per-letter hover legend text (the Dollar, DOMY and
  PILOT today — CROSS-WORDS round, owner UV inbox 2026-07-27);
  `letter_zoom` (hour → height multiplier, same round): the Eye's
  shine masters pad the triangle with rays, so build_skin stamps the
  measured `constants.RING_EYE_SHINE_ENLARGE[source]` and the triangle
  draws the no-light size; `motto`/`motto_metal` (TASK 1, owner "može
  radi" 2026-07-19)
  the outer arc text — a tuple of {"text", "glyphs":
  (asset, angle) pairs, "words": per-word hover geometry (center,
  half-span, seat — WORD-HOVER round, owner 2026-07-27; the
  compositor answers a word hover with its seat's legend)} built by
  build_skin from the preset's own `motto` card field: the Dollar's
  two pinned Great Seal mottos, and DOMY's/PILOT's four centered
  cross-station words (CROSS-WORDS round); empty for The One/Templar
  and custom rings; see
  [Ring Presets](../data/rings.md) and [Layers](../render/layers.md)
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
