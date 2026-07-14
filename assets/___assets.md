# assets/

Bundled visual content — ALL of it shared app content (there are no
skin folders: DOMY and MORPH are ring preset names, nothing more).

```
📁 assets/
  🖼️ logo.svg              ← project logo (M7; also copied to monorepo logos/)
  🖼️ logo.svg              ← the owner's GOLD watch — tray icon now, EXE/installer art in M7
  🖼️ logo-setup.svg        ← the rose-gold variant (NSIS wizard art)
  📁 ring/                 ← dial ring faces: domy.png, morph.png (+ future rings)
    📁 letters/            ← the owner's GOLD letter library: latin SVG (D,G,H,I,M,P,S,
                             U,V,X,Y,Z) + greek PNG (Omega,Phi,Pi,Psi,Sigma,Theta),
                             plus PRE-RENDERED <Stem>_silver.png for the active letters
                             (setup/make_silver_letters.py — rerun when a new letter
                             becomes active). Active per preset (RING_LETTER_FILES):
                             domy M/D/Y+Omega, morph M/Pi/H+Omega. Overlaid by
                             calculation so the ring TINT never touches them; each
                             preset's ACCENT letter wears the opposite metal (domy
                             inverts its Omega, morph inverts its M)
  📁 hands/                ← hour/minute/second.svg (owner canvases 240/290/300,
                             hub 15 design units above the bottom)
  📁 earth/                ← earth_{clean|atmo}_{continent}_{day|night}.png
  📁 weekday/              ← body art per THEME: SOURCE first (owner
                             2026-07-14: Gemini and ChatGPT coexist, the
                             user picks in Settings), then the
                             FAMILY/VARIANT tree (owner restructure
                             2026-07-14):
                             <source>/<family>/<variant>/[dual/]<Entity>.png
                             — source gemini/ or chatgpt/ (a file missing in
                             one source falls back to the other), dual/
                             sits INSIDE each variant, colored is a variant
                             SIBLING. Families:
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
                             <source>/scale/ (the two triangles + Union)
  📁 instrument/           ← <source>/ → the Instrument section logo +
                             article images
```

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
asia, oceania. The night variant is shown between sunset and sunrise. The
moon marker reuses `weekday/planets/primary/moon.png` with a procedural
terminator shadow. PNG or SVG both work (detected by extension,
rasterized once by the asset cache).

## Connections

### Used by
- [Config (folder)](../config/___config.md) — DEFAULT_SKIN + RING_PRESETS paths
- [Render (folder)](../render/___render.md) — asset cache
- [App Controller](../app/controller.md) — weekday theme + zodiac art paths
