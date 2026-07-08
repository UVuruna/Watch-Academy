# assets/

Bundled visual content. SHARED art (ring faces, weekday themes, zodiac
art) lives at the top level — a skin is a dial DESIGN and references
the shared content with relative paths; skin folders keep only what is
truly theirs.

```
📁 assets/
  🖼️ logo.svg              ← project logo (M7; also copied to monorepo logos/)
  📁 ring/                 ← dial ring faces: domy.png, morph.png (+ future rings)
  📁 weekday/              ← body art per THEME (SYMBOLISM.md), files carry ENTITY names:
                             planets/ (sun..saturn.png, real renders)
                             greek/ (Helios..Cronus.png)   norse/ (Sol..Sabbath.png)
                             religion/ (Christianity..Judaism.png)
                             profession/ (Ruler..Farmer.png)
                             — non-planet files are 1×1 placeholders until the owner
                             pastes his vectors over them (same names)
  📁 zodiac/               ← octa bottom-arm art: sign/, logo/, constellation/ (<Sign>.png),
                             chinese/ (<Animal>.png) — 1×1 placeholders, same convention
  📁 skins/
    📁 domy/               ← default skin: skin.json (serialized FROM config's DEFAULT_SKIN)
      📁 hands/            ← hour/minute/second.svg (owner canvases 240/290/300,
                             hub 15 design units above the bottom)
      📁 year_marker/      ← earth_{clean|atmo}_{continent}_{day|night}.png
    📁 morph/              ← partial skin: skin.json only (its ring lives in assets/ring/)
```

The star and the Umbra are deliberately NOT assets — both are simple
geometry drawn procedurally (owner decision: keeps the bundle light,
stays sharp at every size, and lets the pointer variant change the arm
count and the contrast setting change the shades at runtime).

Bundle copies are downscaled working resolutions (ring 1024 px, planets
and Earth markers 256 px); the full-resolution masters stay in `design/`
(untracked owner scratch space) — RE-COPY bundle files whenever the
masters change.

## Year marker naming convention

`earth_<style>_<continent>_<day|night>.png` with style `clean` (default)
or `atmo`, continents: europe, north_america, south_america, africa,
asia, oceania. The night variant is shown between sunset and sunrise. The
moon marker reuses `weekday/planets/moon.png` with a procedural
terminator shadow. PNG or SVG both work (detected by extension,
rasterized once by the asset cache).

## Connections

### Used by
- [Skins (folder)](../skins/___skins.md) — manifest resolution
- [Render (folder)](../render/___render.md) — asset cache
- [App Controller](../app/controller.md) — weekday theme + zodiac art paths
