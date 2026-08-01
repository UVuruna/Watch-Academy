# Archetypes

**Script:** [Archetypes (script)](../archetypes.py) · **Flow:** [diagram](../__flow/archetypes.md)

## Purpose

The ARCHETYPE MODE's one configuration home (owner-sealed package
2026-07-16, canon in `CANON.md` §Pointer Archetypes): the grid mapping
every `(pointer, palette_style)` pair to its archetype, the
per-archetype FIGURE tables (arm angle, art file, the two-row names,
article entity, encyclopedia target), the CENTER table (the Eye / the
Hearth / the Seal / the Union / the Throne — the Compass has none),
and the render tunables (figure-size classification, the placeholder
threshold, the center's noon/midnight lighting window, the Earth
day-label geometry).

## The eleven archetypes

| Grid key | (pointer, style) | Archetype | Center |
|---|---|---|---|
| `trinity_primary` | trio · primary | the Courtroom (God / the Devil / Jesus) | the Eye |
| `trinity_secondary` | trio · secondary | the Family (Child / Mother / Father) | the Hearth |
| `trinity_genesis` | trio · tertiary | GENESIS — the creation trio, INVERTED | the Beginning |
| `quaternity_primary` | cross · primary | the Four Temperaments | the Throne |
| `quaternity_secondary` | cross · secondary | the Tetramorph (Lion / Ox / Eagle / Man) | the Throne |
| — | cross · tertiary | **Seasons — no archetype yet** | — |
| `prism_primary` | hexa · primary | the Persons (six) | the Seal |
| `prism_secondary` | hexa · secondary | One Soul — The Vow — The Bond | the Union |
| `prism_council` | hexa · tertiary | the COUNCIL — all six Double-Trinity offices | the Lord's Day |
| `compass_primary` | octa · primary | the Eight Walks of Life | — |
| `compass_secondary` | octa · secondary | the Eight Ages | — |
| `compass_character` | octa · tertiary | CHARACTER — the Cube at depth zero | — |
| `rose_vertices` | rose · secondary | the Eight Vertices (Prophecy wheel) | — |

Aurora and the Calendar have NO archetype — `grid_key()` returns None
there and the menu grays the toggle; the same None is the documented
answer for the Quaternity's Seasons wheel (a slot exists since
2026-07-28 but no figures seat it yet). `rose · primary` reuses
`compass_character` (Rule #5: the Rose's Legacy wheel IS the 2D
Character wheel — one figure seated once).

## Figure sizing — THE TWO-TYPE LAW

Figure SIZE is not a per-art clamp; every figure classifies ONCE by
its OWN art aspect ratio (width/height), via `render.layers.
archetype_figure_size()`:

- **CIRCLE** type (aspect ≥ `ARCHETYPE_PORTRAIT_ASPECT_MAX` = 0.70 —
  rondels, medallions, the square Scale glass, wide art like Saturn's
  rings) wears the SLOT size, identical to the weekday bodies.
- **PORTRAIT** type (aspect below 0.70 — the tall lancet vitraž
  windows) wears the INSCRIBED height for the STANDARD aspect
  (`ARCHETYPE_PORTRAIT_STANDARD_ASPECT` = 0.5, i.e. 1:2) — uniform for
  every portrait in a set, regardless of that art's own aspect.

Missing/placeholder art reads CIRCLE-sized (there is no art to
classify).

## Connections

### Uses
- [Config (folder)](../___config.md) — `paths.assets_dir()`
- [Character Cube](cube.md) — `FIGURE_SETS` and `ROSTER`: the three
  registers and the people who hold each cube seat (`roster_names`)

### Used by
- [Render (folder)](../../render/___render.md) — `ArchetypeLayer` /
  `ArchetypeCenterLayer`, the lit-index math, the art-readiness check
- [Compositor](../../render/__about/compositor.md) — arm/center hovers, the
  two-row articles, the encyclopedia targets
- [Watch Controller](../../app/__about/controller.md) — the menu toggle gating
  (`has_archetype`)

## Functions

- `grid_key(pointer, palette_style)`: the archetype key of a grid
  seat, or None (Aurora/Calendar/the Seasons wheel)
- `has_archetype(pointer)`: whether ANY wheel of this pointer carries
  an archetype
- `figures(key)`: the ordered figure tuple (resolving the Ages
  register)
- `roster_names(key, index, register)`: the two figures one arm seats
  in one figure set — only `compass_character` and `rose_vertices`
  answer (their rows carry a `cell`); every other archetype RAISES,
  its arms are not cube seats
- `center(key)`: the center dict or None
- `tetramorph_element(index)` / `tetramorph_evangelist_file(index)`:
  the Tetramorph three-side hover's second and third columns, sharing
  the figures' own hour-space ordering

## Design Decisions

- **Canonical, source-less paths.** Figure files are stored suffix-less
  under `assets/archetypes/<family>/<register>/<look>/`; `config.
  paths.art_file` inserts the active art source at every disk boundary.
- **Two REUSED seats.** Prism primary's Lucifer (Pride) and Judas
  (Fear) inherit the owner's Scale glass — the triangles belong to the
  Scale badge alone, an explicit exception to one-image-one-place.
- **Figure order = lit order.** Each archetype's figures tuple is
  ordered by arm position, so the tuple index IS the hour-space index.
- **Seasons figures are COLOR-fixed.** The Temperaments sit on the
  palette hues, never on season instants — the southern hemisphere does
  NOT flip them. The Tetramorph figures ROTATE
  (`_fig(..., rotates=True)`) through THE UNIVERSAL ROTATION
  CONVENTION — every other figure and every center stays a fixed
  master.
- **The two Cube wheels carry their CUBE CELL.** Each row of
  `compass_character` and `rose_vertices` records the `(x, y, z)` seat
  its two names hold, so the arm resolves its three registers' people
  from [Character Cube](cube.md)'s one roster table instead of
  repeating any name here.
- **The Ages ship TWO registers** (Tree and Menagerie, both full file
  tables); `ARCHETYPE_LIFE_REGISTER` picks the rendered one.
- **A CENTER may declare its own encyclopedia target too** — the
  center table takes the same optional `enc` key an arm figure
  carries; today only `prism_secondary`'s Union uses it.
- **The CENTER window** (`ARCHETYPE_CENTER_WINDOW_DEG` = 15.0, ±1h):
  `ArchetypeCenterLayer` burns the center figure full only within this
  many degrees of true solar noon OR midnight — the rest of the time it
  draws at the weekday `ghost_opacity`, exactly like an un-lit arm
  figure.
