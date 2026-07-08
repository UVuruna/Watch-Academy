# Manifest

**Script:** [Manifest (script)](manifest.py)

## Purpose
The typed skin definition — six overridable units (background, hexagram,
ring, weekday_set, year_marker, hands) plus the noon marker. Pure
dataclasses with no I/O: `DEFAULT_SKIN` in config is an instance of these,
and M5's `skin.json` loading/validation targets the same types, so
extraction is serialization, not redesign.

## Connections

### Uses
- Nothing (stdlib dataclasses only — importable from anywhere)

### Used by
- [Config (folder)](../config/___config.md) — `DEFAULT_SKIN`
- [Render (folder)](../render/___render.md) — layers read the specs

## Classes

- `SkinDefinition` — name, `z_order`, one spec per unit
- `BackgroundSpec` — fixed base wheel asset (32-section gray) + 6
  transparent hues that rotate WITH the hexagram, drawn only over the
  sunlit arc (day/twilight alphas)
- `HexagramSpec` — PROCEDURAL six-diamond star (owner decision: simple
  geometry is drawn at runtime, no image file): 6 colors, neutral night
  color, day/twilight/night alphas, tip radius
- `NoonMarkerSpec` — asset-or-procedural triangle
- `RingSpec` — full ring image (numerals/letters baked in) or procedural
  fallback with per-hour letter substitutions (M-12, D-4, Ω-0, Y-20)
- `WeekdaySpec` — body images/colors, white weekday SHORT label on top,
  display mode (ghost / center_only), ghost opacity, sizes, orbit
- `YearMarkerSpec` — mode earth / moon / both; Earth day+night variants
  per continent on the year wheel; Moon on its own cycle (new at top,
  full at bottom) with the unlit part shadowed; separate orbits
- `HandSpec` / `HandsSpec` — asset, MANDATORY pivot fractions, reach

## Functions

- `missing_assets(skin)`: referenced-but-absent files (surfaced visibly
  at startup — a miss inside paintEvent would be swallowed by Qt)
