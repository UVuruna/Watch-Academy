# assets/

Bundled visual content — ALL of it shared app content (there are no
skin folders: DOMY and MORPH are ring preset names, nothing more).

```
📁 assets/
  🖼️ logo.svg              ← project logo (M7; also copied to monorepo logos/)
  📁 ring/                 ← dial ring faces: domy.png, morph.png (+ future rings)
    📁 letters/            ← the owner's letter art, {M,D,Y,P,H,Omega}_{gold,silver}.png
                             (12 files, 1×1 placeholders until extracted from the ring) —
                             overlaid by calculation so the ring TINT never touches them;
                             the finish choice flips the metals (Omega always the inverse)
  📁 hands/                ← hour/minute/second.svg (owner canvases 240/290/300,
                             hub 15 design units above the bottom)
  📁 earth/                ← earth_{clean|atmo}_{continent}_{day|night}.png
  📁 weekday/              ← body art per THEME (SYMBOLISM.md), files carry ENTITY names:
                             planets/ (sun..saturn.png, real renders)
                             greek/ (Helios..Cronus.png)   norse/ (Sol..Sabbath.png)
                             religion/ (Christianity..Judaism.png)
                             profession/ (Ruler..Farmer.png)
                             — non-planet files are 1×1 placeholders until the owner
                             pastes his vectors over them (same names)
  📁 zodiac/               ← octa bottom-arm art: sign/, logo/, constellation/ (<Sign>.png),
                             chinese/ (<Animal>.png) — 1×1 placeholders, same convention
```

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
moon marker reuses `weekday/planets/moon.png` with a procedural
terminator shadow. PNG or SVG both work (detected by extension,
rasterized once by the asset cache).

## Connections

### Used by
- [Config (folder)](../config/___config.md) — DEFAULT_SKIN + RING_PRESETS paths
- [Render (folder)](../render/___render.md) — asset cache
- [App Controller](../app/controller.md) — weekday theme + zodiac art paths
