# Watch Academy

Watch Academy is a transparent 24-hour analog clock widget for the Windows desktop, built around a single dial named DOMY. Only the dial is visible on screen — no frame, no taskbar entry — like a phone home-screen widget.

**Status:** in development — the core is feature-complete (M1 shell,
M2 computation core, M3 living dial, plus the theme/metal/roster skin
system, Settings with the city picker, Encyclopedia, Guide, Time
Travel, translations). What remains to release is listed taxatively
in [Roadmap](ROADMAP.md).

<a id="the-name"></a>

## The Name

The application is **Watch Academy** — its topics are courses (religious,
psychological, philosophical, astronomical), some locked and unlocked over
time; the in-app reference organ keeps its own name, **Encyclopedia** (an
academy holds both its courses and its library). **DOMY** survives as the
name of the dial itself — the watchman of the Academy, and the dark-cross
cipher read in [The DOMY Canon](CANON.md).

English *watch* carries all three meanings this project needs at once: the
timepiece, the act of watching, and the vigil. Proposed tagline (wording
still open to the owner): *"Watch the hours. Watch and learn. Keep the
watch."* Latin seal for inscriptions: **VIGILATE** — the Vulgate's own word
for Mark 13:37, *"quod autem vobis dico, omnibus dico: vigilate"* ("What I
say unto you I say unto all, Watch"). Full doctrine: [The Cube
Canon](CUBE.md#the-name).

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
📁 DOMY Watch/            ← folder name kept; the app is Watch Academy
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

Every `.md` in this project is reachable from here by following links —
enforced by `tests/test_doc_links.py`. Each code folder carries a
`___folder.md` entry point, an `__about/` folder (what each file does) and,
where a file holds a real algorithm, a `__flow/` folder (its logic drawn as a
diagram plus language-neutral pseudocode).

- [Agent Guidance](CLAUDE.md) — how Claude Code works in this project;
  inherits the monorepo constitution
- [Main (Entry Point)](__about/main.md) — what `main.py` does at startup
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
- [Recolor (folder)](recolor/___recolor.md) — the metal transformer: one
  drawn master becomes any metal, live, from rules
- [Skins (folder)](skins/___skins.md)
- [Render (folder)](render/___render.md)
- [App (folder)](app/___app.md)
- [Assets (folder)](assets/___assets.md)
- [Database (folder)](Database/___database.md)
- [Tests (folder)](tests/___tests.md)
- [Setup (folder)](setup/___setup.md)
- [Design (folder)](design/___design.md)
- [Illustrator (folder)](illustrator/___illustrator.md) — vector sources
  (gitignored on disk; the folder doc travels with the repo)
- [Research (folder)](research/___research.md) — image-generation
  prompt sheets live here; see [How to Write a Prompt
  Sheet](../PromptPainter/instructions.md) before authoring a new one
- [Roster — the Master Systematics](ROSTER.md) — every theme, every
  figure, its seat, per-source art coverage (generated:
  `python research/build_roster.py`)

### Structural plans (history, still referenced)

- [The One-Hierarchy Refactor](RESTRUCTURE.md) — the owner-approved
  plan (sealed 2026-07-22) behind today's `assets/` and Encyclopedia shape
- [The Structural Arc](WORKPLAN-STRUCTURE.md) — the plan for the
  config-split sessions
- [Refactor God-Files](REFACTOR-GODFILES.md) — a local copy of the
  monorepo task brief (the canonical one now lives at the repo root)

## Running from source

```bash
pip install -r requirements.txt
python main.py
```

Right-click the dial (or the tray icon) for the menu. Drag with the left
mouse button. The window position is remembered in
`%APPDATA%/DOMY Watch/settings.json`.
