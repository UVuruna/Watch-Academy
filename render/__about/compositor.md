# Compositor

**Script:** [Compositor (script)](../compositor.py) · **Flow:** [diagram](../__flow/compositor.md)

## Purpose
`Compositor` builds the Z-ordered layer stack from the skin's own
`z_order`, paints it every frame, and answers every hover question
(hit-testing, the hover-enlarge target, and the rich-text tooltip under
the cursor). It is the one object `app.widget`'s `paintEvent` delegates
to and the controller feeds a day/tick into.

**Cadence-driven caching (owner 2026-07-17, ROADMAP 15f):** the stack
is partitioned into paint STEPS — each maximal run of hover-INVARIANT
STATIC/DAILY layers becomes ONE cached pixmap; MINUTE layers and
HOVER-VARIABLE layers (the weekday bodies, the archetype figures) paint
LIVE every frame, so a hover enter/leave or an Omega reveal rebuilds
NOTHING. `render_offscreen()` reuses the exact same `paint()` path for
tests and the settings preview.

## THIS FILE IS A DOCUMENTED GOD-FILE (3,311 lines)

It carries THREE separate responsibilities in one class, and is named
in `tests/test_structure_law.py`'s RATCHET allowlist. `render/layers.py`
— the sibling god-file the ratchet used to name alongside this one —
has since left the ratchet, split into [Layers
(subfolder)](../layers/___layers.md); the ratchet's owed split for THIS
file is now scoped precisely: lift the free HTML helpers to
`render/article_html.py` first, then the tooltip bank into a
`TooltipComposer`, then hit-testing:

1. **Layer stacking + cached compositing** (`__init__`, `_plan_steps`,
   `paint`, `_render_group`, `render_offscreen`, `set_day`,
   `invalidate`, `_rotation`) — roughly the first 700 lines.
2. **Hit-testing** (`_element_at`, `set_hover`, `hit_omega`,
   `_weekday_body_at`, `_arm_angle_at`, `encyclopedia_target` and its
   `_*_encyclopedia_target` family) — the geometry that answers "what
   is under the cursor", shared between the hover-enlarge effect and
   the Spacebar Encyclopedia jump.
3. **The tooltip / article HTML bank** — by far the largest slice
   (~2,500 of 3,311 lines): `tooltip_at`/`_tooltip_at` dispatch to
   dozens of `_*_tooltip`/`_*_text`/`_*_html` methods, one per dial
   element (weekday bodies, archetypes, the ring, calendar wedges and
   mounts, seasons, moon, eclipses, the Earth marker, the thirteenth
   plate, …), each building small HTML fragments through the shared
   `_centered`/`_highlight_terms` helpers.

This doc describes the file HONESTLY as it stands; splitting it is a
separate, not-yet-scheduled session (see the ratchet entry above) —
this migration changes documentation only, never code (Rule #20 is
violated in the code, not papered over here).

## Connections

### Uses
- [Layers (subfolder)](../layers/___layers.md) — every concrete `Layer`
  subclass, stacked by `_build_layers`
- [Context](context.md) — `Cadence`, `Layer`, `RenderContext`
- [Assets](assets.md), [Asset Recolor](asset_recolor.md), [Asset
  Variants](asset_variants.md) — `AssetCache`, `metal_variant_file`,
  `eclipse_solar_type_icon`, `scaled_variant_file`
- [Archetype Geometry](archetype_geometry.md), [Calendar
  Mount](calendar_mount.md), [Ninths](ninths.md), [Painting](painting.md),
  [Shapes](shapes.md), [Skin Geometry](skin_geometry.md), [Slot
  Layout](slot_layout.md) — every geometry function the paint pass AND
  the hover pass share (Rule #5 — one source of truth per question)
- `data.encyclopedia.EncyclopediaRepository`,
  `data.symbolism.SymbolismRepository` — the hover/article text corpus,
  overlay-translated
- [Core (folder)](../../core/___core.md) — `angles`, `continents`,
  `DayContext`, `TickState`, `deep_time`, `moon`, `year_wheel`
- [Config (folder)](../../config/___config.md) — `archetypes`,
  `calendar_mounts`, `constants`, `defaults`, `dial`,
  `encyclopedia_ui`, `glow`, `palette`, `pantheon`, `paths`, `profiling`,
  `ui_text`

### Used by
- `app.widget` — `paintEvent` delegates to `paint()`; hover events call
  `set_hover()`/`tooltip_at()`
- `app.controller` — feeds `set_day()`/invalidation, owns the instance
- [Tests (folder)](../../tests/___tests.md) — `render_offscreen()`
  drives the golden-pixel and hover-text suites

## Classes

### Compositor
- `paint(painter, size, dpr, tick)`: the per-frame entry — blits each
  cached group, paints each live layer, honors the reveal window's
  hidden hands.
- `set_hover(x, y, size)` / `hit_omega(x, y, size)` /
  `trigger_reveal_week(now=None)`: cursor/click interaction, returning
  whether a repaint is needed.
- `tooltip_at(x, y, size)`: the rich-text hover tooltip under the
  cursor, or `None`.
- `encyclopedia_target(x, y, size)`: the `(topic, index)` the Spacebar
  jump opens for whatever is under the cursor.
- `render_offscreen(size, dpr, day, tick)`: a full frame into a
  `QImage` — tests and the settings preview.

## Design Decisions
- **The composite key is size/DPI + the day alone** — never hover, never
  reveal. That is the entire point of the 15f cache split: those two
  states live only in the LIVE layers, so toggling them never triggers
  "Composite rebuild".
- **Hit-testing and painting read the SAME geometry functions**, never
  a parallel hand-measured copy — a hover disc and a hover-enlarged
  drawn element can therefore never drift apart.
