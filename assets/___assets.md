# assets/

Bundled visual assets: the project logo (M7) and bundled skins.

```
📁 assets/
  🖼️ logo.svg              ← project logo (M7; also copied to monorepo logos/)
  📁 skins/
    📁 domy/               ← default bundled skin
      ⚙️ skin.json         ← manifest, serialized FROM config's DEFAULT_SKIN
      📁 dial/             ← ring.png (full DOMY dial art); base_gray.png retired —
                             the 30-section gray wheel is procedural now
      📁 hands/            ← hour/minute/second.svg (owner canvases 240/290/300,
                             hub 15 design units above the bottom)
      📁 weekday/          ← body art per THEME (SYMBOLISM.md): planets/ (real renders),
                             greek/, norse/, religion/, profession/ (<body>.png — 1×1
                             placeholders until the owner pastes his vectors over them)
      📁 year_marker/      ← earth_{clean|atmo}_{continent}_{day|night}.png (6 continents × 2 styles × day/night)
      📁 zodiac/           ← octa bottom-arm art: sign/, logo/, constellation/ (<Sign>.png),
                             chinese/ (<Animal>.png) — 1×1 placeholders, same convention
    📁 morph/              ← partial skin: its own ring.png + letters (M-12, Π-16, H-8, Ω-0)
      ⚙️ skin.json
      📁 dial/
```

The star and the gray brightness wheel are deliberately NOT assets —
both are simple geometry drawn procedurally (owner decision: keeps the
bundle light, stays sharp at every size, and lets the pointer variant
change the arm count and the contrast setting change the shades at
runtime).

Bundle copies are downscaled working resolutions (ring 1024 px, planets
and Earth markers 256 px); the full-resolution masters stay in `design/`
(untracked owner scratch space) — RE-COPY bundle files whenever the
masters change.

## Year marker naming convention

`earth_<style>_<continent>_<day|night>.png` with style `clean` (default)
or `atmo`, continents: europe, north_america, south_america, africa,
asia, oceania. The night variant is shown between sunset and sunrise. The
moon marker reuses `weekday/moon.png` with a procedural terminator
shadow. PNG or SVG both work (detected by extension, rasterized once by
the asset cache).

## Connections

### Used by
- [Skins (folder)](../skins/___skins.md) — manifest resolution
- [Render (folder)](../render/___render.md) — asset cache
