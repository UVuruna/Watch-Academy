# DOMY Watch

A transparent 24-hour analog clock widget for the Windows desktop. Only the
dial is visible — no frame, no taskbar entry — like a phone home-screen widget.

**Status:** in development — M1 (transparent shell) and M2 (computation core
with golden tests) done; the living dial (M3) is next.

## The dial

- 24-hour face, clockwise: **12:00 noon at the top, 00:00 midnight at the
  bottom** (18:00 right, 06:00 left). Small hand = hours, large hand = minutes.
- The daylight arc (sunrise → sunset for the chosen city) is rendered bright;
  night is dark/gray; dawn/dusk bands in between.
- A hexagram overlay whose top vertex always points at **true solar noon**.
- 7 celestial bodies mark the weekdays (Sun = Sunday in the center); only the
  current day's body is shown.
- An Earth icon orbits the dial once per year, calibrated to the real
  solstices (summer at the top, winter at the bottom).
- Everything is skinnable: hands, weekday sets, year marker, colors, ring.

## Structure

```
📁 DOMY Watch/
  🐍 main.py            ← entry point
  📁 config/            ← all constants and tunables
  📁 core/              ← pure astronomy/angle computation
  📁 data/              ← repositories over Database/*.json
  📁 skins/             ← skin manifests, validation, merging (M5)
  📁 render/            ← QPainter layers and compositor (M3)
  📁 app/               ← Qt shell: window, tray, settings
  📁 assets/            ← bundled skins and logo
  📁 Database/          ← bundled astronomical/location data
  📁 tests/             ← pytest golden-value suite
  📁 design/            ← mockups and reference images (not bundled)
  📁 illustrator/       ← vector sources for skin assets (not bundled)
  📁 research/          ← one-off analysis scripts and oversized data (not bundled)
```

## Documentation

- [Config (folder)](config/___config.md)
- [Core (folder)](core/___core.md)
- [Data (folder)](data/___data.md)
- [Skins (folder)](skins/___skins.md)
- [Render (folder)](render/___render.md)
- [App (folder)](app/___app.md)
- [Assets (folder)](assets/___assets.md)
- [Database (folder)](Database/___database.md)
- [Tests (folder)](tests/___tests.md)
- [Design (folder)](design/___design.md)
- [Illustrator (folder)](illustrator/___illustrator.md)
- [Research (folder)](research/___research.md)

## Running from source

```bash
pip install -r requirements.txt
python main.py
```

Right-click the dial (or the tray icon) for the menu. Drag with the left
mouse button. The window position is remembered in
`%APPDATA%/DOMY Watch/settings.json`.
