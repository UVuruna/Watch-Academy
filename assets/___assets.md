# assets/

Bundled visual assets: the project logo (M7) and bundled skins.

```
📁 assets/
  🖼️ logo.svg              ← project logo (M7; also copied to monorepo logos/)
  📁 skins/
    📁 domy/               ← default bundled skin
      ⚙️ skin.json         ← manifest (M5; until then DEFAULT_SKIN lives in config)
      📁 dial/             ← ring.png (full DOMY dial art), base_gray.png (fixed 32-section wheel)
      📁 hands/            ← hour.png + minute.png (pivots 0.5/0.68 and 0.5/0.92)
      📁 weekday/          ← sun, moon, mars, mercury, jupiter, venus, saturn (real renders)
      📁 year_marker/      ← earth_{clean|atmo}_{continent}_{day|night}.png (6 continents × 2 styles)
```

The hexagram is deliberately NOT an asset — it is simple geometry drawn
procedurally from six palette colors (owner decision, keeps the bundle
light and the star sharp at every size).

Bundle copies are downscaled working resolutions (ring/base 1024 px,
planets and Earth markers 256 px, ~1.7 MB total); the full-resolution
masters stay in `design/` (untracked owner scratch space).

## Year marker naming convention

`earth_<style>_<continent>_<day|night>.png` with style `clean` (default)
or `atmo`, continents: europe, north_america, south_america, africa,
asia, oceania. The night variant is shown between sunset and sunrise. The
moon marker reuses `weekday/moon.png` with a procedural terminator
shadow. PNG or SVG both work (detected by extension, rasterized once by
the asset cache).

## Connections

### Used by
- [Skins (folder)](../skins/___skins.md) — manifest resolution (M5)
- [Render (folder)](../render/___render.md) — asset cache (M3)
