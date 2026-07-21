# assets/

Bundled visual content — ALL of it shared app content (there are no
skin folders: DOMY and MORPH are ring preset names, nothing more).

```
📁 assets/
  🖼️ logo.svg              ← project logo (M7; also copied to monorepo logos/)
  🖼️ logo.svg              ← the owner's GOLD watch — tray icon now, EXE/installer art in M7
  🖼️ logo-setup.svg        ← the rose-gold variant (NSIS wizard art)
  📁 ring/                 ← dial ring faces: domy.png, morph.png (+ future rings)
    📁 letters/            ← the owner's GOLD letter library ONLY (owner decree
                             2026-07-19, "bolje crtati na licu mesta nego 15MB
                             fajlova": the pre-rendered <Stem>_silver.png/
                             <Stem>_bronze.png files and their two generators are
                             retired — silver/bronze are now derived from the gold
                             master AT LOAD, render.assets.letter_metal_file, disk-
                             cached). Active per preset (RING_LETTER_FILES): domy
                             M/D/Y+Omega, morph M/Pi/H+Omega. Overlaid by
                             calculation so the ring TINT never touches them; each
                             preset's ACCENT letter wears the opposite metal (domy
                             inverts its Omega, morph inverts its M)
  📁 hands/                ← hour/minute/second.svg (owner canvases 240/290/300,
                             hub 15 design units above the bottom)
  📁 earth/                ← earth_{clean|atmo}_{continent|pole}_{day|night}.png
                             (+ world.png map; the Continents theme's bodies —
                             see the earth-reuse exception below)
  📁 weekday/              ← body art per THEME: SOURCE first (owner
                             2026-07-14: Gemini and ChatGPT coexist, the
                             user picks in Settings), then the
                             FAMILY/VARIANT tree (owner restructure
                             2026-07-14):
                             <source>/<family>/<variant>/<Entity>.png
                             — source gemini/ or chatgpt/ (a file missing in
                             one source falls back to the other). Every
                             file sits FLAT inside its variant — the Sunday
                             dual included (owner DUAL FLATTEN 2026-07-19:
                             no `dual/` subfolder anywhere; WHO a file is
                             lives only in config, `WEEKDAY_DUAL_FILES`/
                             `WEEKDAY_PANTHEON`, never in a folder name).
                             colored is a variant SIBLING. Families:
                             planets/ → primary/ (real renders) + signs/
                             (glyphs) + art/ (bronze medallions)
                             bible/ → primary/ + secondary/ (Bible II) +
                             dark/ (the night windows)
                             religion/ → primary/ (Creeds) + secondary/
                             (Mysteries)
                             greek|norse|egypt|slavic|wolf|bee|elephant|
                             profession|cosmos/ → primary/ + colored/
                             alchemy|japan/ → primary/
  📁 zodiac/               ← <source>/astrology/ → primary/ (plain logo) +
                             colored/ + sign/ + constellation/ (<Sign>.png);
                             <source>/chinese/ → primary/ + colored/
                             (<Animal>.png)
  📁 emblem/               ← <source>/virtue|sin|mood|intelligence/ — the
                             emblem logo families (Capitalized stems; mood
                             also holds Wheel_of_Moods[_dark].png)
  📁 badge/                ← <source>/season/ (+ turning_point/,
                             meteorological/), <source>/trinity/,
                             <source>/scale/ (the two triangles + Union,
                             ROTATING — see below)
  📁 subdial/              ← NOT art-sourced (owner decree 2026-07-21,
                             Rsub round — deliberately OUTSIDE
                             ART_SOURCED_ROOTS: the plate is its OWN
                             shared thing, orthogonal to the Gemini/
                             ChatGPT pick, not nested under it). Five
                             hand-picked sets: set1/, set2/, set3/,
                             set4/ each hold THREE hand-drawn finishes
                             (gold.png, silver.png, bronze.png — no
                             recolor, `render.assets.subdial_plate_file`
                             returns them as drawn); solo/ holds ONLY
                             silver.png, gold/bronze derived live
                             (`_recolored_plate`, the same recipe the
                             ring letters use). The user picks the SET
                             in Settings (`Settings.subdial_set`); the
                             letter FINISH (ring_finish) still picks
                             the color within it.
  📁 months/               ← NOT art-sourced (owner-sealed R7b 2026-07-21,
                             the SAME subdial precedent — deliberately
                             OUTSIDE ART_SOURCED_ROOTS: a Calendar-pointer
                             mount SET is its own shared thing, not a
                             Gemini/ChatGPT split). <stem>.png, one per
                             Slavic month (Sijecanj..Prosinac, ASCII
                             stems from `defaults.SLAVIC_MONTHS`), the
                             twelve marks the DESIGN ZODIAC law mounts on
                             the Calendar pointer. GRACEFUL-ABSENT — a
                             FUTURE prompt sheet; nothing ships here yet,
                             so the folder does not exist on disk and
                             every consumer hides the mark until it lands.
  📁 era/                  ← <source>/<Name>.png — the Age/Starry-Season
                             rose windows (ROTATING — see below) +
                             <source>/calendar/ (the "Eras of the
                             World" comparison strip, ALSO ROTATING as
                             of the ERA-TRIO round, owner 2026-07-20 —
                             ground-truthed and fixed: it used to
                             bypass `rotating_art_file` entirely)
  📁 archetype/            ← <source>/<archetype>/<Figure>.png — the
                             pointer-archetype stained glass; the
                             Tetramorph figures ROTATE (see below)
  📁 instrument/           ← <source>/ → the Instrument section logo +
                             article images
```

## Rotating families (`alt/`)

THE UNIVERSAL ROTATION CONVENTION (owner decree 2026-07-20, sealed
alongside monorepo root `CLAUDE.md` Rule #19 "Compute, Don't
Generate"): most families freeze on ONE canonical file per name — a
few, where the owner deliberately wants MULTIPLE generated takes shown
in rotation instead of a single frozen master, opt in instead. Beside
the canonical `<dir>/<Name>.png`, additional versions live EITHER as
`<dir>/<Name>_v2.png`-style suffix siblings OR as a same-named file
inside a `<dir>/alt/` subfolder — both pools merge into ONE daily
rotation, picked deterministically by the viewed (or time-traveled)
date's proleptic ordinal. `alt/` is a legal subfolder ANYWHERE under
`assets/` for exactly this reason (`tests/test_assets_structure.py`
`test_alt_folders_mirror_their_parent_names` pins the one real rule:
every file inside an `alt/` folder must mirror a same-named canonical
sibling one level up — an `alt/` file with no canonical twin is an
orphan, since nothing computes a rotation pool for a stem the parent
doesn't also carry).

The mechanism is ONE shared function, `config.defaults.
rotating_art_file(canonical_path, on_date)` — it resolves the active
art SOURCE first (`config.paths.art_file`, so callers keep passing
canonical source-less paths like every other asset table entry), then
pools the resolved directory's own `<Name>`/`<Name>_v*` files with the
same search one level down in `alt/`. It is OPT-IN per consumer, never
wired onto the hot `art_file` path itself. Current adopters:

- **The Scale badge** (Judas/Lucifer, `assets/badge/scale/`) — the
  family the convention was generalized FROM; it keeps its own
  naming-zoo tolerance (more than one valid stem, a `glass/` register
  instead of `alt/` — an established second STYLE, not a generic
  version pool) as a thin caller of the shared machinery
  (`scale_variant_file`).
- **The era/age rose windows** (`assets/era/<source>/`) — the Earth
  hover card's era badge and the Encyclopedia's era entry images both
  resolve through `rotating_art_file`, keyed by the viewed/traveled
  date. Its `calendar/` sub-collection (the "Eras of the World"
  comparison strip) joined the same wiring in the ERA-TRIO round
  (owner 2026-07-20) — the Byzantine v2 emblem, a tetragrammatic-cross-
  with-firesteels take living at `calendar/alt/Byzantine.png`, is the
  strip's first rotation sibling.
- **The Tetramorph figures** (`assets/archetype/<source>/tetramorph/`)
  — `render.layers.ArchetypeLayer` resolves each `rotates=True` figure
  fresh every paint (the layer already paints LIVE, never cached, so a
  day change re-resolves with no extra invalidation).

**Dropping new art:** ChatGPT generations go into the untracked
`chatGPT/` inbox at the project root (informal folder names are fine —
the intake maps them onto the canonical stems), or straight to the
final `assets/<root>/chatgpt/...` path. Prompt sheets state CANONICAL
source-less paths — the source segment decides where the file
physically lives.

The star and the Umbra are deliberately NOT assets — both are simple
geometry drawn procedurally (owner decision: keeps the bundle light,
stays sharp at every size, and lets the pointer variant change the arm
count and the contrast setting change the shades at runtime).

Bundle copies are downscaled working resolutions (ring 1024 px, planets
and Earth markers 256 px); the full-resolution masters stay in `design/`
(untracked owner scratch space) — RE-COPY bundle files whenever the
masters change.

## Earth naming convention

`earth_<style>_<continent>_<day|night>.png` with style `clean` (default)
or `atmo`, continents: europe, north_america, south_america, africa,
asia, oceania, plus the two poles north_pole / south_pole. The night
variant is shown between sunset and sunrise. The moon marker reuses
`weekday/planets/primary/moon.png` with a procedural terminator shadow.
PNG or SVG both work (detected by extension, rasterized once by the asset
cache). `world.png` (the flat map, converted from `UV/earth map.jpg`) is
the Continents Encyclopedia topic's title/gallery image.

### The Continents theme's earth-reuse exception (owner-sealed 2026-07-21)

`assets/earth/` is deliberately NOT sourced (no gemini/chatgpt subtree),
and its faces are reused UNCHANGED as the bodies of the **Continents**
weekday theme — the SIX inhabited continents on the six weekday
columns, the two poles as the Sunday dual (Antarctica the Ruler /
Arctic the Servant), and `zealandia.png` / `pangea.png` (wired ahead of
the owner's art) as the living Ninth. This is an owner-sealed EXCEPTION
to the one-image-one-place law (CANON amendment 2026-07-19): the globes
are quality art never shown large elsewhere, so the theme borrows the
dial's own Earth marker rather than generating a second set. On the dial
the body follows the user's `earth_style` and the live sky's day/night
(`config.defaults.continents_body_art`); the atmo-day face is only the
baked still frame the Encyclopedia gallery previews with. See
[Continents (script)](../core/continents.md) for the Ninth easter-egg
law and [Encyclopedia](../app/encyclopedia.md) for the topic.

## Connections

### Used by
- [Config (folder)](../config/___config.md) — DEFAULT_SKIN + RING_PRESETS paths
- [Render (folder)](../render/___render.md) — asset cache
- [Watch Controller](../app/controller.md) — weekday theme + zodiac art paths
