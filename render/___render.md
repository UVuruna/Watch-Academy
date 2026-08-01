# render/

Everything QPainter. Consumes `DayContext`/`TickState` (from core) and
a `SkinDefinition` (from skins) — computes no astronomy itself. All
layers paint in a center-origin coordinate system with dial angles
(degrees clockwise from top) converted to Qt's conventions only inside
[Painting](__about/painting.md)'s helpers.

**Post-split architecture (since commit 0.14.688 — the 3,881-line
`layers.py` god-file is GONE):** [Context](__about/context.md) is the
layer PROTOCOL (`Cadence`, `RenderContext`, the `Layer` ABC); the
geometry/painting modules beside it ([Painting](__about/painting.md),
[Shapes](__about/shapes.md), [Skin Geometry](__about/skin_geometry.md),
[Slot Layout](__about/slot_layout.md), [Daylight](__about/daylight.md),
[Subdial](__about/subdial.md), [Calendar
Mount](__about/calendar_mount.md), [Archetype
Geometry](__about/archetype_geometry.md), [Ninths](__about/ninths.md),
[Weekday Body](__about/weekday_body.md), [Eclipse
Glow](__about/eclipse_glow.md)) are the shared VOCABULARY every layer
and the compositor read from; [Layers (subfolder)](layers/___layers.md)
holds one module per Z-ordered paint layer (`BackgroundLayer`,
`StarLayer`, `RingLayer`, `WeekdayLayer`, `CenterBodyLayer`,
`SlotLayer`, `YearMarkerLayer`, `HandLayer`, `ArchetypeLayer`,
`ArchetypeCenterLayer`, `HoverLiftLayer`); and
[Compositor](__about/compositor.md) stacks them, caches the
hover-invariant groups, and answers every hit-test/tooltip question.

## Files

| File | Tier | One line |
|------|------|----------|
| `context.py` | Algorithmic | the render protocol — `Cadence`, `RenderContext`, `Layer` — [about](__about/context.md) · [flow](__flow/context.md) |
| `painting.py` | Algorithmic | shared QPainter primitives, the ONE dial-to-Qt angle conversion — [about](__about/painting.md) · [flow](__flow/painting.md) |
| `skin_geometry.py` | Algorithmic | every "what does this skin say" query — palettes, arms, duality, daylight — [about](__about/skin_geometry.md) · [flow](__flow/skin_geometry.md) |
| `shapes.py` | Algorithmic | star/polygon/arm path geometry — [about](__about/shapes.md) · [flow](__flow/shapes.md) |
| `slot_layout.py` | Algorithmic | the slot position matrix and seat geometry — [about](__about/slot_layout.md) · [flow](__flow/slot_layout.md) |
| `daylight.py` | Algorithmic | day/night/twilight arcs, the Umbra ladder — [about](__about/daylight.md) · [flow](__flow/daylight.md) |
| `subdial.py` | Algorithmic | the complication roundels, their shadow and fitted text — [about](__about/subdial.md) · [flow](__flow/subdial.md) |
| `calendar_mount.py` | Algorithmic | the Calendar wheel and the 12-set pointer mounts — [about](__about/calendar_mount.md) · [flow](__flow/calendar_mount.md) |
| `archetype_geometry.py` | Algorithmic | archetype hour-space lighting, THE TWO-TYPE sizing law — [about](__about/archetype_geometry.md) · [flow](__flow/archetype_geometry.md) |
| `ninths.py` | Algorithmic | the Ninth and thirteenth plate resolution, the center face — [about](__about/ninths.md) · [flow](__flow/ninths.md) |
| `weekday_body.py` | Algorithmic | one weekday body + its set-uniform label — [about](__about/weekday_body.md) · [flow](__flow/weekday_body.md) |
| `eclipse_glow.py` | Algorithmic | eclipse render state, glow strength, the radial halo — [about](__about/eclipse_glow.md) · [flow](__flow/eclipse_glow.md) |
| `compositor.py` | Algorithmic | Z-ordered stack, cached compositing, hit-testing, the tooltip HTML bank — GOD-FILE, ratcheted — [about](__about/compositor.md) · [flow](__flow/compositor.md) |
| `assets.py` | Algorithmic | `AssetCache` — rasterize/tint/metal-swap, the working set — [about](__about/assets.md) · [flow](__flow/assets.md) |
| `asset_recolor.py` | Algorithmic | disk-cached metal finishes, the lazy variant ledger — [about](__about/asset_recolor.md) · [flow](__flow/asset_recolor.md) |
| `asset_variants.py` | Algorithmic | moon render, subdial plate resolver, computed icons — [about](__about/asset_variants.md) · [flow](__flow/asset_variants.md) |
| `art_warm.py` | Algorithmic | drains the metal-recolor ledger off the GUI thread — [about](__about/art_warm.md) · [flow](__flow/art_warm.md) |
| `instrument_diagrams.py` | Algorithmic | the clock explaining itself, 8 computed pages — [about](__about/instrument_diagrams.md) · [flow](__flow/instrument_diagrams.md) |
| `canon_diagrams.py` | Algorithmic | the doctrine's journeys and tables, computed — [about](__about/canon_diagrams.md) · [flow](__flow/canon_diagrams.md) |
| `cube_diagrams.py` | Algorithmic | the Character Cube's isometric compositions — [about](__about/cube_diagrams.md) · [flow](__flow/cube_diagrams.md) |
| `cube_preview3d.py` | Algorithmic | guarded bridge to the 3D Preview gadget, graceful 2D fallback — [about](__about/cube_preview3d.md) · [flow](__flow/cube_preview3d.md) |
| `diagrams.py` | Standard | the one door to the three diagram modules — [about](__about/diagrams.md) |
| `__init__.py` | Trivial | docstring only, no code |

[Layers (subfolder)](layers/___layers.md) holds the Z-ordered paint
layer classes themselves — owned and documented by its own session.

## Connections

### Uses
- [Core (folder)](../core/___core.md) — `DayContext`, `TickState`,
  angle mapping, sun/moon/deep-time/year-wheel facts
- [Skins (folder)](../skins/___skins.md) — `SkinDefinition`
- [Config (folder)](../config/___config.md) — dial constants, slot
  angles, palettes, the archetype/calendar-mount/doctrine/cube tables
- [Data (folder)](../data/___data.md) — `EncyclopediaRepository`,
  `SymbolismRepository` (hover/article text), `cube_model_export`,
  `observatory` (the La2004 envelope)
- [Recolor (folder)](../recolor/___recolor.md) — the Qt-free metal
  transform `assets.py` adapts

### Used by
- `app` (top level, not yet migrated) — the widget's `paintEvent`
  delegates to the compositor; the controller feeds day/tick and
  invalidations; the Encyclopedia reader asks `diagrams.py`/
  `cube_preview3d.py` for a page's plate/panel
- [Tests (folder)](../tests/___tests.md) — offscreen smoke tests and
  golden-pixel/hover-text suites drive `render_offscreen()`

## Design Decisions
- **One shared vocabulary, not one shared base class per concern.** The
  split kept `Layer`/`Cadence`/`RenderContext` as the ONE protocol
  (root Rule #5) while every geometry question — arm angles, seat
  layout, daylight arcs, archetype sizing — moved to a plain-function
  module named for what it answers, not for which layer happens to ask
  it first; both the paint pass and the compositor's hit-test/hover
  read the SAME functions, so they can never disagree.
- **Compute, never generate (root Rule #19).** The Cube/Canon/Instrument
  diagram modules, the calendar wheel icon, and the moon-phase render
  all draw live from the same numbers the dial itself reads, so a
  changed constant can never leave a stale illustration on an
  Encyclopedia page.
- **Recolors are disk-cached and built lazily, off the GUI thread**
  ([Asset Recolor](__about/asset_recolor.md), [Art
  Warm](__about/art_warm.md)) — a paint never pays for a metal swap;
  the first frame shows the gold master and repaints in its real finish
  once the background drain catches up.
- **`compositor.py` remains a documented god-file** (3,311 lines,
  ratcheted in `tests/test_structure_law.py`) — it still carries
  cadence-driven cached compositing, hit-testing and the ~2,000-line
  tooltip/article HTML bank in one class. The ratchet now scopes its
  owed split precisely: free HTML helpers to `render/article_html.py`
  first, then a `TooltipComposer`, then hit-testing — a future session,
  not this documentation pass (root Rule #20's `.md` requirement is
  satisfied here; the split itself is not).
