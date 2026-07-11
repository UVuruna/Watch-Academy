# Compositor

**Script:** [Compositor (script)](compositor.py)

## Purpose
Owns the layer stack and the cadence-driven cache: STATIC+DAILY layers
render into one pixmap at device resolution (rebuilt when the day
context, size or DPI changes); each minute-paint blits the cache and
draws the MINUTE layers (hands, year marker) live.

## Connections

### Uses
- [Layers](layers.md), [Assets](assets.md),
  [Clock State](../core/clock_state.md), [Skins (folder)](../skins/___skins.md)

### Used by
- [Clock Widget](../app/widget.md) — `paintEvent` delegate
- [App Controller](../app/controller.md) — `set_day()` / `invalidate()`
- [Tests (folder)](../tests/___tests.md) — `render_offscreen()`

## Classes

### Compositor
- `set_day(day)`: new day context, drops the composite
- `invalidate()`: size/DPI/screen change — drops composite AND rasterized assets
- `paint(painter, size, dpr, tick)`: blit composite + MINUTE layers;
  raises if called before the first day context (startup order is a
  controller guarantee)
- `render_offscreen(size, dpr, day, tick) -> QImage`: same path, headless
- `set_hover(x, y, size) -> bool`: tracks the element under the cursor
  for the HOVER-ENLARGE effect (owner EXTRAS — one shared factor draws
  it larger); True = target changed, the widget repaints (weekday
  bodies live in the DAILY composite, so one rebuild per change).
  `_element_at()` is the ONE geometry shared with the tooltips
  (body/octa slot/moon/earth, in hover priority); legend off or a
  factor of 1.0 keeps the dial inert
- `tooltip_at(x, y, size) -> str | None`: hover text at every dial size
  (the owner's hover-rework formats: raised `<sup>` ordinal suffixes,
  hyphens instead of long dashes), in priority order — the WEEKDAY
  BODIES (every visible body within its image region: the entity's
  NAME as a bigger bold title — Odin, Farmer, Islam… (owner spec
  2026-07-11, `defaults.ARTICLE_TITLE_PX`) — the active day adds
  "Thursday, 9th July 2026" beneath it, then the LEFT-aligned
  article — base + the active pointer/palette combination paragraph,
  the entity art on top). In every article the canon terms POP
  (owner spec 2026-07-12, `_highlight_terms`): virtues bold blue,
  vices bold red, moods bold yellow, color words in their own hue
  (`defaults.LEGEND_*` rules, English + Serbian originals), and hex
  notes like "(#F8E600)" are stripped from display. Then the octa
  info slot; the
  Moon marker (phase — with the exact principal instant in parentheses
  while its name holds — Illumination to one decimal, the
  moonrise-moonset span, the cycle day); the Earth marker (ordinal
  date, Nth Day - Nth Week, the season row "Summer 18th of 94 Days" —
  southern hemisphere flips the name — and the zodiac span, plus the
  season event name while it glows); the twilight bands; the STAR ARMS
  (hexa diamonds carry BOTH their signs, each a header with its span
  plus the sign's full article from the
  [Symbolism Repository](../data/symbolism.md); trio arms give their
  theological theme, day third and weekday pair; cross/octa cardinals
  give the exact event instant plus that day's length "15h 23min", the
  cross appending its METEOROLOGICAL season block — From/To at the
  halfway instants; octa diagonals describe their season with "(N.N
  Days)" and "Heart:" as the midpoint label — a trailing * flags
  solar-rotation imprecision); and LAST the wheel itself — the sunlit
  arc answers with the day duration and both spans (sun and
  twilight-extended), the dark with the night duration and its bounds.
  With `legend` off, tooltip_at returns None for EVERYTHING — combined
  with click-through the dial has zero interaction (owner spec). A
  switched-off Element answers no hovers either: weekday off silences
  the body spots, pointer off the arm regions and the octa slot,
  earth/moon off their markers

The layer stack follows `skin.z_order`, skipping the layers of
switched-off Elements (star, weekday set, year marker when both
markers are off, the seconds hand); the current day's center body
(and, on the octa pointer, the bottom-arm info slot) are appended LAST
so they draw above the hands (owner spec). `_rotation()` feeds the
shared Star/Aura/Umbra/slot rotation into every RenderContext: the
solar offset, or 0 with solar rotation off (upright mode).
