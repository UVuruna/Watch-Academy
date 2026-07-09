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
  `pointer` ("hexa" | "cross" | "octa" | "trio"), `umbra_form` ("fine" |
  "coarse" | "gradient"), `umbra_contrast` ("full" | "half"),
  `palette_style` ("paint" | "light"), `solar_rotation` (False →
  Star/Aura/Umbra stand upright), `octa_slot` (one of
  `OCTA_SLOT_MODES`: time/date/day length, tropical zodiac as
  text/sign/logo/constellation, Chinese zodiac as text/logo),
  `earth_style` ("clean" | "atmo") and the six Elements switches
  (`show_earth`, `show_moon`, `show_weekday`, `show_pointer`,
  `colorful` — off draws the Aura as plain white transparency —
  and `show_seconds`)
- `BackgroundSpec` — the Umbra (custom art, or None for the procedural
  30-section wheel: single lightest/darkest sections centered on
  noon/midnight) + the Aura (transparent period hues from the palette
  preset, drawn only over the sunlit arc; day/twilight alphas)
- `StarSpec` — PROCEDURAL N-diamond star (owner decision: simple
  geometry is drawn at runtime, no image file): day/twilight alphas,
  full-circle border alpha/width, tip radius; colors come from the
  palette preset shared with the Aura
- `RingSpec` — full ring image (numerals/letters baked in) or procedural
  fallback with per-hour letter substitutions (M-12, D-4, Ω-0, Y-20)
- `WeekdaySpec` — body images/colors, white weekday label on top,
  display mode (ghost / center_only), ghost opacity, sizes, orbit
- `YearMarkerSpec` — Earth day+night variants per continent on the year
  wheel; Moon on its own cycle (new at top, full at bottom) with the
  unlit part shadowed; separate orbits. Which marker is drawn comes
  from the Elements switches (`show_earth` / `show_moon`)
- `HandSpec` / `HandsSpec` — hand canvases at their exact designed sizes
  (hub 15 design units above the bottom), ONE shared reach scale

## Functions

- `missing_assets(skin)`: referenced-but-absent files (surfaced visibly
  at startup — a miss inside paintEvent would be swallowed by Qt)
