# Work Plan — the Closing Sessions

The owner's ORDER OF WORK for the coming sessions with fresh agents
(written 2026-07-16, at the owner's request). Each session below
says: WHAT to tell the agent, WHAT the agent must read, WHAT it
delivers, and WHICH model tier the job deserves — so the strongest
agent is never burned on an easy job.

## How to Open Any Session

1. The project `CLAUDE.md` loads automatically — it points the agent
   at everything else and sets the rules (Serbian conversation,
   English files, MD-first, version commits).
2. Tell the agent WHICH session from this file it is running — e.g.
   *"Radi Sesiju 3 iz WORKPLAN.md"* — that is enough; the session
   entry names its own reading list.
3. For ANY theme, roster, article or archetype work the agent MUST
   read [The DOMY Canon](CANON.md) first — the seating doctrine,
   the archetype grid, the two-row canon, the quote and
   color-fidelity rules all live there.
4. [Roadmap](ROADMAP.md) holds the full remaining-work list; this
   file holds the ORDER and the assignments.
5. Every session ends the house way: `python -m pytest tests`
   green, offscreen render/menu probe where UI changed, versioned
   commits (`0.14.xxx description`), push, and a Serbian report.
6. **Missing owner art** (owner rule 2026-07-16): when a feature
   needs an image the owner has not generated yet, commit a 1×1 px
   PNG placeholder at the exact drop path with the exact name — the
   owner overwrites it when the art lands.

## Model Tier Legend

| Tier | Use for |
|---|---|
| **Fable** | multi-system features touching render + articles + menus at once; anything where a wrong abstraction is expensive |
| **Opus** | house-voice ARTICLE writing, render/astronomy geometry, the build pipeline — hard but single-domain |
| **Sonnet** | well-specified features, menu wiring, palettes, config swaps — the spec does the thinking |
| **Haiku** | inventories, link checks, doc sweeps, mechanical regeneration |

## The Sessions, in Order

### Session 1 — Quick UX batch → **Sonnet**
**Say:** "Radi Sesiju 1 iz WORKPLAN.md — tri mala UX zadatka iz
ROADMAP-a (Owner's Queued Feature Tasks 1–3)."
**Reads:** ROADMAP.md queue items 1–3; `app/controller.md`,
`app/widget.md`, `render/compositor.md`.
**Delivers:** (1) HIDDEN hover trigger only at the 12h letter;
(2) Omega double-click reveals ALL weekday bodies at full opacity
for 60 s (center above the hands, non-active bodies only);
(3) Paint/Light choice GRAYED on Trinity and Seasons. Tests + GUI
probe per feature.

### Session 2 — Turning-point glow rework → **Opus**
**Say:** "Radi Sesiju 2 iz WORKPLAN.md — ROADMAP queue task 5."
**Reads:** ROADMAP queue task 5; `render/layers.md`,
`render/compositor.md` (event glow, year marker).
**Delivers:** at a glow event the marker relocates to the ring-band
centerline at its event position; SMALL golden glow for the Sun,
silver for the Moon, straddling the ring; geometry pinned with
golden tests. (Opus: render geometry precision — accuracy > speed.)

### Session 3 — Compass palette pair → **Sonnet**
**Say:** "Radi Sesiju 3 iz WORKPLAN.md — nove octa palete iz
CANON-a."
**Reads:** CANON.md (Compass paint materials + Eight Ages hues);
`config/___config.md`.
**Delivers:** `PALETTE_PRESETS` octa paint/light replaced with the
APPROVED hues, pin test, before/after offscreen renders for the
owner's eyes.

### Session 4 — Archetype prompt sheets → **Opus**
**Say:** "Radi Sesiju 4 iz WORKPLAN.md — prompt sheetovi za
preostale arhetipe, jedan arhetip = jedan fajl."
**Reads:** CANON.md IN FULL; `research/prompts/___prompts.md`;
`research/prompts/archetype/trinity_prompts.md` as the template;
`research/bond_theme.md`.
**Delivers:** one sheet each for Trinity light (Family + the
Hearth), Prism light (One Soul pillars), Seasons (temperaments;
tetramorph if approved by then), Compass paint (Walks + objects),
Compass light (Ages + the image layer the owner picks — Tree ★ or
Menagerie). House rules: stained-glass register family, NO
lettering in images, drop paths declared. **Run this EARLY — the
owner generates art in parallel while later sessions code.**

### Session 5 — The Archetype engine → **Fable**
**Say:** "Radi Sesiju 5 iz WORKPLAN.md — implementacija arhetipskog
sistema."
**Reads:** CANON.md IN FULL (grid, two-row canon, display rules);
ROADMAP queue task 4; `render/`, `app/controller.md`,
`app/encyclopedia.md`, `data/` docs.
**Delivers:** the 7-archetype system live — per-(pointer, palette)
archetype content; visible only in GLOW windows; moon window via
Omega double-click, sun window also as slot theme option and in the
Encyclopedia; TWO-ROW articles; Trinity center Eye / Hearth; works
under Time Travel. The biggest remaining feature — render + data +
menu + encyclopedia at once. (Fable: cross-system.)

### Session 6 — Archetype articles wave → **Opus** (writers)
**Say:** "Radi Sesiju 6 iz WORKPLAN.md — dvoredni artikli za svih 7
arhetipova."
**Reads:** CANON.md IN FULL (persons, natures, quote anchors, the
quote-the-greats and color-fidelity rules); SYMBOLISM.md;
`research/bond_theme.md`; `Database/symbolism.json` structure.
**Delivers:** both rows for every position of all seven archetypes
(courtroom persons+callings, family members+hearth-roles,
temperaments+ages, persons+qualities, pillars+shadows,
estates+objects, ages+beings), with the Bible/philosopher quotes
woven in — **ENGLISH ONLY (translation policy, owner 2026-07-16:
no SR during development; the pre-build Translation session covers
everything at once)**. **MANDATORY in this session:** the ~327
`octa_paint`/`octa_light` variant paragraphs in
`Database/symbolism.json` still describe the OLD compass hues
(found in Session 3) — rewrite them to the Walks/Ages wheels.

### Session 7 — The poem Easter egg → **Sonnet**
**Say:** "Radi Sesiju 7 iz WORKPLAN.md — pesma iza šifre."
**Reads:** ROADMAP queue task 6; CANON.md Seasons section (the poem
text); `app/encyclopedia.md`; the hidden-mode listener in
`app/controller.md` / `app/report.md`.
**Delivers:** typing the cipher reveals the owner's four-greeting
poem in the Encyclopedia, bound to the Seasons; hidden otherwise;
test pins the gate.

### Session 8 — Wider Pantheon topics → **Opus** (writers)
**Say:** "Radi Sesiju 8 iz WORKPLAN.md — Wider Pantheon
enciklopedijski topici."
**Reads:** CANON.md; `research/pantheon_catalog.md`;
`Database/encyclopedia.json` family structure (the Union ninths).
**Delivers:** one topic per culture for the A-list figures no seat
could hold; retired ninthsʼ material reused; SR synced.

### Session 9 — Mechanical sweep → **Haiku** (Sonnet where judgment is needed)
**Say:** "Radi Sesiju 9 iz WORKPLAN.md — mehanički prolaz."
**Reads:** README.md navigation chain; `research/build_roster.py`.
**Delivers:** build_roster.py pantheon + glass columns and ROSTER.md
regenerated; docs freshness pass (stale status lines, PROJECTS.md
registration at the monorepo root); link check of the whole `.md`
chain.

### Session 15 — the Translation wave → **Opus** (runs IMMEDIATELY before Session 10)
**Say:** "Radi Sesiju 15 iz WORKPLAN.md — prevod pred build."
**Reads:** this entry; `data/translations.md`; the merge pipeline
pattern in `research/___research.md` (merge_articles.py).
**Delivers:** the ONE translation pass of the whole cycle (owner
policy 2026-07-16): every untranslated/stale key — articles, UI
strings, encyclopedia pages, moon pages, archetype texts — brought
to a clean bundle==corpus 0/0 audit in `sr-Latn.json`; house voice,
brand terms stay English; the audit numbers printed in the report.

### Session 10 — M7 Build & Release → **Opus**
**Say:** "Radi Sesiju 10 iz WORKPLAN.md — M7 build pipeline i
release."
**Reads:** the monorepo root `CLAUDE.md` (Build & Release System —
the exact 5-step pipeline); ROADMAP.md §M7; `setup/___setup.md`.
**Delivers:** `setup/{svg_to_ico.py, app_info.json, build.py,
create_cert.py, installer.nsi}` per the house conventions; signed
`--onedir` build; NSIS installer with the autostart section
replacing the dev pythonw entry; clean-profile smoke; then asks the
owner about GIT RELEASE (tag + `gh release create` with the
installer artifact).

### Session 11 — the Calendar pointer → **Opus**
**Say:** "Radi Sesiju 11 iz WORKPLAN.md — Calendar pointer."
**Reads:** CANON.md §The Dozen (BOTH variants, the palettes, the
owner's verdicts on the open points); `Dozen.png` (root);
`render/layers.md`, `skins/manifest.md`, `config/___config.md`
(palette system).
**Delivers:** the twelve-wedge pointer with its two variants —
Zodiac Dozen (sign boundaries on the axes, 15°-shifted wheel,
current sign lights, existing zodiac art speaks the articles) and
Month Dozen (axis-centered wedges, pure primaries; its OWN
real-calendar year mapping with one tick ≈ one day and the 1st of
each month on a wedge line; the Earth marker's day-ARROW pointing
at its exact tick; the Chinese double-hours lighting following the
hand, reusing the existing animal medallions); palettes and the
per-month mapping pinned with golden tests, offscreen renders for
the owner's eyes. (Opus: render geometry + a second year mapping.
May run before or after Session 5 — the owner names the order.)

### Session 12 — the UI batch II → **Opus** (launched 2026-07-16)
**Say:** "Radi Sesiju 12 iz WORKPLAN.md."
**Reads:** ROADMAP queue items 7–10.
**Delivers:** Calendar wedge hovers wearing the colored logos;
SPACEBAR → Encyclopedia at the hovered topic; the Encyclopedia
image-clipping fix (REPEAT complaint — screenshot-verified); the
Seasons topic split into Moon / Seasons / Sun with the missing Moon
cycles article.

### Session 13 — the Ephemeris pipeline → **Opus** (launched 2026-07-16)
**Say:** "Radi Sesiju 13 iz WORKPLAN.md."
**Reads:** ROADMAP queue item 12; `prompt.txt` background (owner's
Sonnet transcript); `Anno Lucis.png`.
**Delivers:** `research/ephemeris/` — the Swiss-Ephemeris pipeline
(~97 MB data, gitignored), the events database (sun ~122k, moon
~1.5M), the pinned ANNO LUCIS year with a verification plot, and
the doc. App integration (dual calendar, full installation) is a
LATER session.

### Session 16 — Deep Time integration → **Fable** (the big database enters the app) (launched 2026-07-17)
**Say:** "Radi Sesiju 16 iz WORKPLAN.md."
**Reads:** ROADMAP queue item 12 (all phases); `research/ephemeris/___ephemeris.md`;
`data/seasons.md`, `data/moon_phases.md`, `app/time_travel.md`.
**Delivers:** the FULL-installation data pack — a compact app-side
database built FROM `research/ephemeris/events.sqlite` (sun events,
moon phases, eclipses with geometry) that the app detects at
startup: Time Travel then spans −13000…+17000 (without it, the
bundled 1560–2640 with the friendly clamp from the hotfix); the
DUAL CALENDAR everywhere years show (AD + Anno Lucis, A.L. = CE +
4079); Quick Jump grows the ECLIPSE navigation — four groups (Moon,
Moon Eclipse, Sun, Sun Eclipse), each with prev/next (owner layout
2026-07-16; placeholder emoji 🌑/🌘 until the owner draws the two
small icons); the on-dial ECLIPSE DISPLAY per the owner's pick from
the brainstorm (ROADMAP item 12, display options). ΔT honesty
strings in the hovers at deep-time extremes.

### Session 17 — the Observatory → **Opus** (owner tier correction 2026-07-17: Fable only for truly cross-system novel work)
**Say:** "Radi Sesiju 17 iz WORKPLAN.md."
**Reads:** ROADMAP queue item 15 (the charts list);
`research/ephemeris/season_halves.json` + `eclipses_summary.json`;
the dataviz notes; `app/encyclopedia.md` (the dialog family).
**Delivers:** a right-click window beside the Encyclopedia — "like
an encyclopedia, only with statistics" (owner) — dark
QPainter-drawn interactive charts over the long data: the
season-duration oscillations with PER-SERIES CHECKBOXES (four
seasons, light/dark halves — the owner's own graph, live), the
light−dark envelope with Anno Lucis and the era spans marked, the
eclipse timeline (nearest past/next from any traveled moment), the
current location's day-length curve over the year; series data
ships as compact bundled JSON (decimated where needed).

## Running in Parallel (no agent needed)

- **Owner art generation** from the sheets: pantheon plates,
  Satanism dual, Eleusis, the scale glass set (incl. the two
  Unions), Cat/Ophiuchus, season badges — and the archetype art
  once Session 4 lands. The wiring already degrades gracefully;
  every drop simply lights up.

## Open Owner Decisions (any session may receive the verdict)

- Theme name: ★ One Soul / The Vow / The Bond
  (`research/bond_theme.md`).
- Compass light image layer: ★ the Tree / the Menagerie (CANON).
- Seasons tetramorph persons layer: yes/no (CANON).
- Seven archetypes stay seven (the standing recommendation) or grow
  to thirteen — 13 is the excluded number in this system.
- Odanost as the center's day face, or on a planet seat.
- ~~The Calendar naming~~ — SEALED: pointer **Calendar**, wheels
  **Zodiac/Almanac** in the Paint/Light slot; no wedge medallions,
  pinned 1/2/3 slots, opacity lighting, both lighting modes
  user-selectable.
