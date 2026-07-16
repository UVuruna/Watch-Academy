# Roadmap — What Remains to Ship DOMY Watch

The taxative list of everything between today and the GitHub release
(owner request 2026-07-16). Tasks are RECORDED here, not started —
each one is its own round. The seating doctrine behind the theme work
lives in [The DOMY Canon](CANON.md).

## Table of Contents

- [Where We Stand](#where-we-stand)
- [Owner's Queued Feature Tasks](#owner-queue)
- [Engineering Backlog](#engineering-backlog)
- [Waiting on Owner Art](#waiting-on-art)
- [M7 — Build & Release Pipeline](#m7-build-release)

<a id="where-we-stand"></a>

## Where We Stand

- **M1 shell ✓ M2 computation core ✓ M3 living dial ✓** — and the
  M4–M6 goals have landed along the way: single-instance mutex,
  spontaneous-hide watchdog, autostart (HKCU Run), the full theme/
  metal/roster skin system, Settings with the city picker,
  Encyclopedia, Guide, Time Travel, translations (SR bundle synced).
- **Suite:** 235 green tests (`python -m pytest tests`).
- **Autostart today runs SOURCE** — the HKCU Run entry launches
  `pythonw.exe main.py`; the M7 installer will point it at the EXE.
- **`dist/DOMYWatch/DOMYWatch.exe` is an ad-hoc PyInstaller test
  build from 2026-07-08** — stale (predates the roster/slots/Union
  arcs), unsigned, no icon/version resource, no installer. Not a
  release artifact.

<a id="owner-queue"></a>

## Owner's Queued Feature Tasks (2026-07-16)

1. **Hidden hover only at the top.** The HIDDEN hover trigger moves
   to 12h only — the letter/sign/number seated at the top; nowhere
   else on the ring.
2. **Omega double-click = reveal week.** Double-click on Omega (24h)
   raises the opacity of ALL weekday bodies to full — ghosts AND the
   center body where one exists (Trinity, Prism) — with the center
   Z-ORDER above the hands. Lasts 60 s after the LAST double-click.
   Applies only to non-active weekday bodies (everything else is
   already 100%). Purpose: see the whole theme at once, laid out by
   color.
3. **Gray out Paint/Light where it does nothing.** Trinity and
   Seasons have no separate paint/light palette variants — the
   palette style option must be GRAYED (unavailable) while they are
   the active pointer.
4. **Pointer archetypes — SEVEN, one per (pointer, palette)**
   (owner 2026-07-16: seven layouts, rhyming with the week; paint =
   the world's order, light = the home's). The grid, content canon,
   the Trinity light Family palette (green/blue/red), and the
   PROPOSED Compass palette rework (paint = the Walks' materials,
   light = the Eight Ages) are in [The DOMY Canon](CANON.md) — read
   it first. Trinity paint image prompts are READY:
   `research/prompts/archetype/trinity_prompts.md` (stained-glass
   register, drop at `assets/archetype/<source>/trinity/`). Also
   queued here: the per-theme CANONICAL POINTER note "under the
   asterisk" (Encyclopedia/menu). Display rules:
   - Visible only during GLOW windows: one of the 4 moon phases
     (~every 7 days) or one of the 4 sun events (~every 90 days).
   - Moon window: revealed ONLY by double-click on Omega.
   - Sun window: appears as a theme option in the slot submenus and
     in the Encyclopedia, and also on Omega double-click.
   - Trinity archetype articles run in TWO ROWS (like the hexa
     zodiac diamonds in Prism): the person (God/Devil/Jesus) and the
     calling (Judge/Prosecutor/Advocate).
   - Prism: the diagonals carry the OPPOSITIONS (Love–Hatred,
     Humility–Pride, Fear–Courage).
   - Works with Time Travel in any mode.
   - Seasons and Compass archetypes: owner still deciding — do not
     invent them.
5. **Turning-point glow rework** (owner 2026-07-16). At a GLOW
   event (a moon phase / a sun event) the MARKER relocates to the
   RING BAND CENTERLINE — the radius where the hour numerals and
   letters sit — at its event position (New Moon at 12h). The glow
   then straddles the ring (shines inside AND outside the circle),
   so it can be SMALL and any color: today it must be huge to
   survive e.g. a white Compass tip, and a yellow sun-glow fights
   the yellow top arms. New colors: the **Sun glows GOLDEN, the
   Moon glows SILVER**.
6. **The poem Easter egg** (owner 2026-07-16). The owner's
   four-greeting poem (text in [The DOMY Canon](CANON.md), Seasons
   archetype section) stays HIDDEN behind the existing typed
   cipher — when the code is entered, the poem appears in the
   Encyclopedia, bound to the Seasons.
7. **The Dozen pointer** (owner 2026-07-16, `Dozen.png`). A new
   twelve-wedge pointer — 2h per wedge — in two variants: the
   Zodiac Dozen (boundaries on the axes, 15°-shifted RGB wheel,
   current sign lights) and the Month Dozen (wedges centered on the
   axes, pure primaries, June top). Full doctrine, palettes and the
   open verdicts (month alignment a/★b, the shichen day-lighting
   proposal) in [The DOMY Canon](CANON.md) §The Dozen.

<a id="engineering-backlog"></a>

## Engineering Backlog

- **Wider Pantheon Encyclopedia topics** — one per culture for the
  A-list figures no seat could hold (retired ninths stay in
  `encyclopedia.json` for this wave).
- **The Bond theme** (relationship pillars, owner notes 2026-07-16)
  — definition draft in `research/bond_theme.md`; the Child ninth
  and the family triangle approved; the NAME still open
  (One Soul / The Vow / The Bond).
- **OPEN STRATEGIC QUESTION (owner, 2026-07-16):** partition the
  themes per pointer (each pointer only its naturally-aligned
  themes, ≥4 groups, +paint/light = 6) versus keeping themes
  universal. The standing recommendation (agent, same day): keep
  the WEEK layer (weekday themes, 7 bodies) universal; give each
  pointer its native content on the DAY layer (the archetypes —
  already per-pointer); add soft "natural home" pointer
  recommendations per theme instead of hard walls. Owner verdict
  pending — do not restructure until he rules.
- **`research/build_roster.py`** — add pantheon + glass columns,
  regenerate [Roster](ROSTER.md).
- **Compass palette pair implementation** — the APPROVED hues live
  in [The DOMY Canon](CANON.md) (paint = the Walks' materials,
  light = the Eight Ages); replace the two near-identical octa
  presets in `PALETTE_PRESETS` and pin with a test.
- **Win+D WorkerW glue (optional)** — the only workaround for the
  Show Desktop layer; ship or consciously drop.
- **Docs freshness pass** — README status line, PROJECTS.md entry;
  `research/pantheon_roster_report.md` still describes the old
  global roster combo (historical, superseded banner already in
  place).

<a id="waiting-on-art"></a>

## Waiting on Owner Art

Prompt sheets are ready under `research/prompts/` (one theme = one
file). Wiring is live and falls back gracefully until each drop:

- Pantheon plates per the theme sheets (Greek/Norse/Egypt/Slavic).
- Creeds: the Satanism Sunday dual; Ancient religions: Eleusis.
- The scale GLASS set (6 files incl. Union_Meeting + Union).
- Cat (thirteenth) and Ophiuchus; season badges.

<a id="m7-build-release"></a>

## M7 — Build & Release Pipeline

Follow the monorepo build conventions (root CLAUDE.md):

1. `setup/svg_to_ico.py` — multi-res ICO from `assets/logo.svg`
   (+ `logo-setup.svg` for the wizard icon).
2. `setup/app_info.json` — name, version, exe/installer names;
   company data comes from the root `company.json`.
3. `setup/build.py` — version-info generation, PyInstaller
   `--onedir --windowed` (no UAC; exclude unused modules), signing.
4. `setup/create_cert.py` — one-time self-signed cert
   (`setup/cert/`, gitignored, back up externally).
5. `setup/installer.nsi` — NSIS LZMA installer: desktop shortcut +
   autostart sections; autostart via HKCU Run (standard user, no
   elevation) replacing the dev pythonw entry.
6. Root registration — README.md + PROJECTS.md entries; logo copy
   `logos/DOMYWatch.svg` (already present, verify current).
7. Release — smoke the installer on a clean profile, then
   `git tag v{version}` + `gh release create` with
   `dist/DOMYWatch_Setup.exe` as the artifact.
