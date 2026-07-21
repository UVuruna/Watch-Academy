# Archetypes

**Script:** [Archetypes (script)](archetypes.py)

## Purpose

The ARCHETYPE MODE's one configuration home (owner-sealed package
2026-07-16, canon in [The DOMY Canon](../CANON.md) §Pointer
Archetypes): the grid mapping every (pointer, palette_style) pair to
its archetype, the per-archetype FIGURE tables (arm angle, stained
glass file, the two-row names, article entity, encyclopedia target),
the CENTER table (the Eye / the Hearth / the Seal / the Union / the
Throne — the Compass has none), the article-set names Session 6 writes
into `Database/symbolism.json`, and the render tunables (name sizing,
the placeholder threshold, the center's noon/midnight lighting window,
the Earth day-label geometry, and the two figure-size tunables below).
**THE TWO-TYPE LAW (owner decree 2026-07-18, round two — screenshots;
height law FIXED round A 2026-07-19 — screenshots showed lancets
overflowing their diamonds and the Trinity center huge):** figure SIZE
is no longer a per-art CLAMP (the 15g machinery —
`archetype_figure_height()`, `archetype_set_height()`,
`archetype_fit_height()` — is deleted); instead every archetype figure
classifies ONCE by its OWN art aspect ratio (width/height), via
`render.layers.archetype_figure_size()`:
- **CIRCLE** type (aspect ≥ `ARCHETYPE_PORTRAIT_ASPECT_MAX` = 0.70 —
  rondels, medallions, the square Scale glass, and WIDE art like
  Saturn's rings) wears `weekday_body_size(skin, radius)` — the SLOT
  size, IDENTICAL to the weekday bodies. Wide art stays height-based on
  purpose (owner: "planeta istih dimenzija kao ostale, prstenovi vire"
  — the ball matches every other circle, the rings overflow the frame,
  deliberately — no clamp). Round A tightened the threshold 0.85 → 0.70
  (measured lancet cluster 0.37–0.58, rondel cluster 0.99–1.03) after
  the ChatGPT-set Providence_Eye center (aspect 0.842) wrongly fell
  PORTRAIT-side under 0.85 and drew at the tall lancet height.
- **PORTRAIT** type (aspect below the threshold — the tall lancet
  vitraž windows: persons, temperaments) wears
  `render.layers.archetype_portrait_height(tip, tan_half)` — the
  INSCRIBED height for the STANDARD aspect
  (`ARCHETYPE_PORTRAIT_STANDARD_ASPECT` = 0.5, i.e. 1:2), not the art's
  own aspect: the owner is reforcing every portrait to exactly 1:2, so
  a lancet at the standard inscribes its diamond EXACTLY; art wider
  than 0.5 may still overflow sideways until reforced (transitional,
  documented, not clamped). UNIFORM for every portrait in the set.

Missing/placeholder art reads CIRCLE-sized (there is no art to
classify). The center follows its OWN art's type exactly like an arm
figure.

The EIGHT archetypes and their grid seats (owner 2026-07-17: the
Seasons split into two — PAINT the Temperaments, LIGHT the Tetramorph):

| Grid key | (pointer, style) | Archetype | Art dir | Center |
|---|---|---|---|---|
| `trinity_paint` | trio · paint | the Courtroom (God / the Devil / Jesus) | `archetype/trinity/` | the Eye |
| `trinity_light` | trio · light | the Family (Child / Mother / Father) | `archetype/family/` | the Hearth |
| `seasons_paint` | cross · paint | the Four Temperaments | `archetype/temperaments/` | the Throne |
| `seasons_light` | cross · light | the Tetramorph (Lion / Ox / Eagle / Man) | `archetype/tetramorph/` | the Throne |
| `prism_paint` | hexa · paint | the Persons (six on the paint wheel) | `archetype/persons/` (+ two Scale reuses) | the Seal |
| `prism_light` | hexa · light | One Soul, the Bond (six pillars) | `archetype/one_soul/` | the Union |
| `compass_paint` | octa · paint | the Eight Walks of Life | `archetype/walks/` | — |
| `compass_light` | octa · light | the Eight Ages | `archetype/life/<register>/` | — |

Aurora and the Calendar have NO archetype — `grid_key()` returns None
there and the menu grays the toggle.

## Design Decisions

- **Canonical, source-less paths.** Figure files are stored as
  `assets/archetype/<archetype>/<file>.png`; `config.paths.art_file`
  inserts the active art source (`assets/archetype/<source>/…`) at
  every disk boundary — "archetype" joined `ART_SOURCED_ROOTS` for
  this. The drop paths match the prompt sheets under
  `research/prompts/archetype/` exactly; 1×1 px placeholders are
  committed at every path (the WORKPLAN missing-art rule) and the
  renderer falls back to the figure's NAME while a file is missing or
  still a placeholder (`ARCHETYPE_ART_MIN_PX`).
- **Two REUSED seats.** Prism paint's Lucifer (Pride) and Judas
  (Weakness/Fear) inherit the owner's Scale glass —
  `assets/badge/<source>/scale/{Lucifer,Judas}_Triangle.png`, the
  files as they exist on disk (owner assets are authoritative; the
  sheet's `scale/glass/` subfolder never materialized).
- **Figure order = lit order.** Each archetype's figures tuple is
  ordered by arm position `k · 360/N`, so the tuple index IS the
  hour-space index `archetype_lit_index()` returns (pinned by test).
- **Seasons figures are COLOR-fixed.** The temperaments (paint) sit on
  the palette hues (Choleric = summer yellow top …), not on the season
  instants — the southern hemisphere does NOT flip them, exactly as the
  palette itself never flips. The LIGHT wheel (owner 2026-07-17) seats
  the TETRAMORPH — the Lion/Ox/Eagle/Man on the FOUR ELEMENTS wheel
  (`_CROSS_ELEMENTS`), each creature on its canonical fixed-cross season
  arm (fire summer, earth autumn, water winter, air spring); row 2 is
  the Evangelist (Mark/Luke/John/Matthew). The Throne is the center of
  both wheels. **The Tetramorph figures ROTATE** (owner decree
  2026-07-20, THE UNIVERSAL ROTATION CONVENTION —
  [Assets (folder)](../assets/___assets.md)): `_fig(..., rotates=True)`
  marks all four; `render.layers.ArchetypeLayer` resolves each
  through `config.defaults.rotating_art_file` fresh every paint (the
  canonical `tetramorph/<Creature>.png` plus its `alt/<Creature>.png`
  twin feed one daily pool) — every OTHER archetype figure and every
  center stays a fixed master, `rotates` defaulting False.
- **The Tetramorph three-side's second column has its OWN art table**
  (owner 2026-07-18) — `TETRAMORPH_EVANGELIST_FILES` /
  `tetramorph_evangelist_file(index)`: the four EVANGELIST rondels at
  `assets/archetype/evangelist/{Mark,Luke,John,Matthew}.png`, indexed in
  the same hour-space order as the figures (0 Mark, 1 Luke, 2 John, 3
  Matthew). Unlike the figures, these have NO committed placeholder — the
  three-side simply shows the evangelist's name alone until the rondel
  lands (`archetype_art_ready`), a 1×1-placeholder-free path. The element
  column reuses `tetramorph_element(index)` and the wheel hue; both column
  articles live in `symbolism.json` as `rows[1]`/`rows[2]` of the creature
  node (see [Symbolism (data)](../data/symbolism.md)).
- **The Ages ship TWO registers** (owner "oba", CANON §Compass
  light): the Tree and the Menagerie both have full file tables;
  `ARCHETYPE_LIFE_REGISTER` picks the rendered one (default `tree`,
  the ★-marked recommendation) until the owner wires a user-facing
  choice.
- **Article sets are named by GRID SEAT** (`archetype_trinity_paint`,
  `archetype_seasons_paint`, `archetype_seasons_light`, …) so a future
  theme rename (One Soul → The Vow) never orphans texts. The Seasons
  rename (`archetype_seasons` → `_paint`, 2026-07-17) stayed consistent
  because `symbolism.json` carries no archetype nodes yet — Session 6
  writes, per entity, a
  `{"rows": [row1, row2]}` node into
  `Database/symbolism.json → articles.<set>`; until then
  `SymbolismRepository.archetype_article()` returns None and the
  hover shows the figure's name plus `ARCHETYPE_PENDING_LINE` —
  never a KeyError. Centers use the entity key `"center"` in the
  same set.
- **Encyclopedia targets are per figure, and mostly None.** Only the
  Walks map today (six estates onto the Professions topic's pages);
  the persons, temperaments, pillars, family and ages have no topics
  yet (Sessions 6/8 add them) — a None target makes the Spacebar
  jump do nothing, gracefully.
- **The CENTER window** (owner seal 2026-07-18, `ARCHETYPE_CENTER_WINDOW_DEG`
  = 15.0, i.e. ±1h): `ArchetypeCenterLayer` (see
  [Layers](../render/layers.md)) burns the center figure FULL only
  while the hour hand stands within this many degrees of TRUE solar
  noon OR TRUE solar midnight — 4 of the 24 hours, ~16.7% of the day —
  and draws it at the weekday `ghost_opacity` the rest of the time,
  exactly like an un-lit arm figure; the reveal gesture still forces it
  full regardless. The pure helper (`render.layers.archetype_center_lit`)
  measures the hour hand's circular distance to the noon-midnight axis
  against this constant — no magic numbers in the layer.

## Connections

### Uses
- [Config (folder)](___config.md) — `paths.assets_dir()`, constants

### Used by
- [Layers](../render/layers.md) — `ArchetypeLayer` /
  `ArchetypeCenterLayer`, the lit-index math, the art-readiness check
- [Compositor](../render/compositor.md) — arm/center hovers, the
  two-row articles, the encyclopedia targets
- [Watch Controller](../app/controller.md) — the menu toggle gating
  (`has_archetype`)

## Functions

- `grid_key(pointer, palette_style)`: the archetype key of a grid
  seat, or None (Aurora/Calendar)
- `has_archetype(pointer)`: whether ANY wheel of this pointer carries
  an archetype — the menu-toggle gate
- `figures(key)`: the ordered figure tuple (resolving the Ages
  register)
- `center(key)`: the center dict or None
- `tetramorph_element(index)` + `TETRAMORPH_ELEMENTS` (owner 2026-07-17,
  ROADMAP 15e): the element name (Fire/Earth/Water/Air) each Tetramorph
  creature rides — one ordering shared with the `seasons_light` figures
  and the Four-Elements wheel hues; the THIRD column of the tetramorph
  three-side hover.
