# DOMY Watch

A transparent 24-hour analog clock widget for the Windows desktop. Only the
dial is visible — no frame, no taskbar entry — like a phone home-screen widget.

**Status:** in development — the core is feature-complete (M1 shell,
M2 computation core, M3 living dial, plus the theme/metal/roster skin
system, Settings with the city picker, Encyclopedia, Guide, Time
Travel, translations). What remains to release is listed taxatively
in [Roadmap](ROADMAP.md).

## The dial

- 24-hour face, clockwise: **12:00 noon at the top, 00:00 midnight at the
  bottom** (18:00 right, 06:00 left). Small hand = hours, large hand = minutes.
- The daylight arc (sunrise → sunset for the chosen city) is rendered bright;
  night is dark/gray; dawn/dusk bands in between.
- A hexagram overlay whose top vertex always points at **true solar noon**.
- 7 celestial bodies mark the weekdays (Sun = Sunday in the center); the
  current day's body is highlighted — the others are faint ghosts or fully
  hidden, per skin settings.
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
  📁 skins/             ← typed render configuration (unit dataclasses)
  📁 render/            ← QPainter layers and compositor (M3)
  📁 app/               ← Qt shell: window, tray, settings
  📁 assets/            ← shared art: ring faces, hands, earth, weekday themes, zodiac
  📁 Database/          ← bundled astronomical/location data
  📁 tests/             ← pytest golden-value suite
  📁 design/            ← mockups and reference images (not bundled)
  📁 illustrator/       ← vector sources for skin assets (not bundled)
  📁 research/          ← one-off analysis scripts and oversized data (not bundled)
```

## Documentation

- [Work Plan](WORKPLAN.md) — the ORDER of the closing sessions:
  what to tell each fresh agent, what it reads, what it delivers,
  and which model tier the job deserves
- [Roadmap](ROADMAP.md) — everything left between today and the
  GitHub release, including the owner's queued feature tasks
- [The DOMY Canon](CANON.md) — the seating doctrine: the
  color–virtue–vice–mood web, the two rosters, duals, ninths and
  pointer archetypes — read before any theme/roster work
- [DOMY Symbolism](SYMBOLISM.md) — the dial's symbolic cosmology (days,
  gods, religions, colors, virtues and vices)
- [Config (folder)](config/___config.md)
- [Core (folder)](core/___core.md)
- [Data (folder)](data/___data.md)
- [Skins (folder)](skins/___skins.md)
- [Render (folder)](render/___render.md)
- [App (folder)](app/___app.md)
- [Assets (folder)](assets/___assets.md)
- [Database (folder)](Database/___database.md)
- [Tests (folder)](tests/___tests.md)
- [Setup (folder)](setup/___setup.md)
- [Design (folder)](design/___design.md)
- [Research (folder)](research/___research.md) — image-generation
  prompt sheets live here; see [How to Write a Prompt
  Sheet](../PromptPainter/instructions.md) before authoring a new one
- [Roster — the Master Systematics](ROSTER.md) — every theme, every
  figure, its seat, per-source art coverage (generated:
  `python research/build_roster.py`)

## Running from source

```bash
pip install -r requirements.txt
python main.py
```

Right-click the dial (or the tray icon) for the menu. Drag with the left
mouse button. The window position is remembered in
`%APPDATA%/DOMY Watch/settings.json`.
