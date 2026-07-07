# assets/

Bundled visual assets: the project logo (M7) and bundled skins.

```
📁 assets/
  🖼️ logo.svg              ← project logo (M7; also copied to monorepo logos/)
  📁 skins/
    📁 domy/               ← default bundled skin
      ⚙️ skin.json         ← manifest (M5)
      📁 dial/             ← hexagram.svg, arrow.svg, ring.svg (optional)
      📁 hands/            ← hour + minute hand images (pivot declared in manifest)
      📁 weekday/          ← sun, moon, mars, mercury, jupiter, venus, saturn
      📁 year_marker/      ← Earth per continent (day + night) and moon disc
```

## Year marker naming convention

One image per continent and day-phase; the night variant is shown between
sunset and sunrise:

```
earth_europe_day.png          earth_europe_night.png
earth_north_america_day.png   earth_north_america_night.png
earth_south_america_day.png   earth_south_america_night.png
earth_africa_day.png          earth_africa_night.png
earth_asia_day.png            earth_asia_night.png
earth_australia_day.png       earth_australia_night.png
earth_antarctica_day.png      earth_antarctica_night.png   (optional)
moon_full.png                 (full disc; the terminator mask is drawn procedurally)
```

PNG or SVG both work (detected by extension, rasterized once by the asset
cache). Drop the images into `year_marker/` — the manifest (M5) references
them by these names.

## Connections

### Used by
- [Skins (folder)](../skins/___skins.md) — manifest resolution (M5)
- [Render (folder)](../render/___render.md) — asset cache (M3)
