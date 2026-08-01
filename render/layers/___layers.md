# render/layers/

The dial's Z-ordered paint layers — one module per responsibility, split out
of the 3,881-line `render/layers.py` god-file in commit 0.14.688. Every class
here subclasses `Layer` ([Render Context](../__about/context.md)) and declares
a `Cadence` that tells [Compositor](../__about/compositor.md) how often to
rebuild it (`STATIC` = skin/size/DPI, `DAILY` = day change, `MINUTE` = painted
live every tick). The geometry, path and drawing helpers every layer shares —
`painting`, `skin_geometry`, `shapes`, `slot_layout`, `daylight`,
`calendar_mount`, `ninths`, `archetype_geometry`, `weekday_body`, `subdial`,
`eclipse_glow` — live one level up in `render/`, not here.

## Files

| File | Tier | One line |
|------|------|----------|
| `background.py` | Algorithmic | Umbra brightness wheel + Aura hue wedges over the sunlit arc — [about](__about/background.md) · [flow](__flow/background.md) |
| `star.py` | Algorithmic | the drawn hexagram/polygon arms, filled where the sun is up, bordered everywhere — [about](__about/star.md) · [flow](__flow/star.md) |
| `ring.py` | Algorithmic | outer ring donut/art, hour ticks, 24h numerals, per-skin letters, motto arc — [about](__about/ring.md) · [flow](__flow/ring.md) |
| `weekday.py` | Algorithmic | the seven weekday bodies on the pointer's arm slots, ghost vs. center-only — [about](__about/weekday.md) · [flow](__flow/weekday.md) |
| `slot.py` | Algorithmic | seated subdial complications (date, seconds, ascendant, zodiac, Chinese, weekday) — [about](__about/slot.md) · [flow](__flow/slot.md) |
| `archetype.py` | Algorithmic | Archetype mode's arm figures + centre figure — [about](__about/archetype.md) · [flow](__flow/archetype.md) |
| `hover_lift.py` | Algorithmic | repaints only the hovered element, above the hands, last in z-order — [about](__about/hover_lift.md) · [flow](__flow/hover_lift.md) |
| `hand.py` | Algorithmic | one class, three instances — hour/minute/second hand rotation and sizing — [about](__about/hand.md) · [flow](__flow/hand.md) |
| `center_body.py` | Algorithmic | today's body seated at the dial centre, above the hands | [about](__about/center_body.md) · [flow](__flow/center_body.md) |
| `year_marker.py` | Algorithmic | Earth and Moon markers on the year/lunar wheels, with eclipse glow | [about](__about/year_marker.md) · [flow](__flow/year_marker.md) |
| `__init__.py` | Trivial | package docstring only — no re-exports (see Design Decisions) |

## Z-Order

<a id="z-order"></a>

`render/compositor.py`'s `_build_layers()` reads `skin.z_order` and appends
layers in this order, bottom (painted first) to top (painted last). For the
**default skin** (`config/defaults.py`'s `DEFAULT_SKIN.z_order = (background,
star, weekday_set, ring, year_marker, hands)`) the resulting stack is:

1. `BackgroundLayer` — cached (STATIC/DAILY segment)
2. `StarLayer` — cached
3. `WeekdayLayer` — live, hover-variable (replaced by `ArchetypeLayer` when
   Archetype mode is active — same z slot)
4. `RingLayer` — cached
5. `YearMarkerLayer` — live (MINUTE)
6. `SlotLayer` (angle seats) — only when the skin seats any slot NOT at
   "center"; draws BELOW the hands
7. `HandLayer` × the hand pack's own `z_order` (default hour → minute →
   second) — the seconds instance is skipped when the skin has no seconds
   asset or `show_seconds` is off
8. `CenterBodyLayer` — only when `weekday_set` is in `z_order` and
   `show_weekday` is on (replaced by `ArchetypeCenterLayer` in Archetype
   mode) — ABOVE the hands
9. `SlotLayer` (center seat) — a second instance, only when a slot is seated
   at "center" — ABOVE the hands, same reason as `CenterBodyLayer`
10. `HoverLiftLayer` — always last, always present: repaints only the
    hovered element through lift=True twins of `WeekdayLayer`, `SlotLayer`,
    `YearMarkerLayer`, `ArchetypeLayer` and `ArchetypeCenterLayer` — above
    everything, hands included

Steps 1-5 follow `z_order` directly and are skipped whole when the skin
switches that Element off (`show_pointer`, `show_weekday`,
`show_earth`/`show_moon` both off). Steps 6-9 are conditional on the skin's
slot layout and Archetype mode, not on `z_order` position — "hands" in
`z_order` is the trigger that emits both the angle-seated `SlotLayer` and
every `HandLayer` instance in one place.

## Connections

### Uses
- [Render Context](../__about/context.md) — `Layer`, `Cadence`, `RenderContext`
- [Painting](../__about/painting.md), [Skin Geometry](../__about/skin_geometry.md), [Shapes](../__about/shapes.md), [Slot Layout](../__about/slot_layout.md), [Daylight](../__about/daylight.md), [Calendar Mount](../__about/calendar_mount.md), [Ninths](../__about/ninths.md), [Archetype Geometry](../__about/archetype_geometry.md), [Weekday Body](../__about/weekday_body.md), [Subdial](../__about/subdial.md), [Eclipse Glow](../__about/eclipse_glow.md) — the shared geometry/painting vocabulary every layer draws with
- [Asset Cache](../__about/assets.md), [Asset Recolor](../__about/asset_recolor.md), [Asset Variants](../__about/asset_variants.md) — rasterized/recolored pixmaps
- [Config (folder)](../../config/___config.md) — dial constants, palette, per-skin defaults, archetype/pantheon/continents tables
- [Core (folder)](../../core/___core.md) — `DayContext`/`TickState`, angle conversions, year wheel, moon phase
- [Skins (folder)](../../skins/___skins.md) — `SkinDefinition`, `HandSpec`

### Used by
- [Compositor](../__about/compositor.md) — `_build_layers()` instantiates and z-stacks every layer per `skin.z_order`, then `_plan_steps()` partitions the stack into cached (STATIC/DAILY, hover-invariant) and live (MINUTE or hover-variable) paint steps

## Design Decisions

- **`__init__.py` exports nothing, deliberately** (Rule "No Backward
  Compatibility"): there is no `from render.layers import RingLayer`
  shortcut. Every caller imports from the owning module
  (`from render.layers.ring import RingLayer`) so a file's real dependency
  graph stays visible in its own imports instead of hiding behind a
  package-level re-export list that drifts from what actually exists.
- **`hover_variable` is an escape hatch, not the default.** `WeekdayLayer`
  and `ArchetypeLayer` are logically `Cadence.DAILY` (their content — which
  body is today, which figure is lit — changes once a day), but their
  on-screen SIZE changes the instant the mouse enters/leaves an element or
  an Omega reveal starts. Baking them into the cached DAILY composite would
  mean a hover needs a full rebuild; setting `hover_variable = True` instead
  tells the compositor to paint them live every frame (their own pixmaps are
  already rasterize-cached, so "live" costs a cheap redraw, not a rebuild).
  Every other `Cadence.MINUTE` layer (`SlotLayer`, `HandLayer`,
  `CenterBodyLayer`, `YearMarkerLayer`, `ArchetypeCenterLayer`,
  `HoverLiftLayer`) is already painted live every tick, so it never needs
  the flag.
- **Only 5 of the 10 layer files get a hover-lift twin.** `HoverLiftLayer`
  wires twins for `WeekdayLayer`, `SlotLayer`, `YearMarkerLayer`,
  `ArchetypeLayer` and `ArchetypeCenterLayer` — the layers with individually
  hoverable elements (weekday bodies, subdial slots, Earth/Moon, archetype
  figures) that live BELOW the hands in the base stack and must rise above
  them when enlarged. `CenterBodyLayer` needs none: it is already appended
  after the hands in `_build_layers()`, so `hover_factor()` alone resizes it
  in place — no z-lift required. `BackgroundLayer`, `StarLayer`, `RingLayer`
  and `HandLayer` have no individually-hoverable elements at all.
- **One `SlotLayer` class, two roles.** The `centered: bool` constructor
  flag (not a second class) picks whether an instance draws the angle-seated
  complications (below the hands) or the single center-seated one (above the
  hands) — Rule #5, no duplicate code for two positions of the same
  complications. A third, `lift=True` instance (built by `HoverLiftLayer`)
  draws BOTH kinds of seat when hovered, because `Layer._gate`'s `not
  self._lift` short-circuit skips the `centered` check entirely once
  `lift=True`.
