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

### Session 1 — Quick UX batch → **Sonnet** — CLOSED (owner decree 2026-07-29)

Item 1 shipped long ago (0.14.271, re-verified 2026-07-19); items 2–3
declared superseded/absorbed by the owner — not open debt.
**Say:** "Radi Sesiju 1 iz WORKPLAN.md — tri mala UX zadatka iz
ROADMAP-a (Owner's Queued Feature Tasks 1–3)."
**Reads:** ROADMAP.md queue items 1–3; `app/controller.md`,
`app/widget.md`, `render/compositor.md`.
**Delivers:** (1) HIDDEN hover trigger only at the 12h letter;
(2) Omega double-click reveals ALL weekday bodies at full opacity
for 60 s (center above the hands, non-active bodies only);
(3) Paint/Light choice GRAYED on Trinity and Seasons. Tests + GUI
probe per feature.

### Session 2 — Turning-point glow rework → **Opus** — CLOSED (owner decree 2026-07-29: superseded/absorbed; not open debt)
**Say:** "Radi Sesiju 2 iz WORKPLAN.md — ROADMAP queue task 5."
**Reads:** ROADMAP queue task 5; `render/layers.md`,
`render/compositor.md` (event glow, year marker).
**Delivers:** at a glow event the marker relocates to the ring-band
centerline at its event position; SMALL golden glow for the Sun,
silver for the Moon, straddling the ring; geometry pinned with
golden tests. (Opus: render geometry precision — accuracy > speed.)

### Session 3 — Compass palette pair → **Sonnet** — CLOSED (owner decree 2026-07-29: work absorbed by later palette rounds; not open debt)
**Say:** "Radi Sesiju 3 iz WORKPLAN.md — nove octa palete iz
CANON-a."
**Reads:** CANON.md (Compass primary materials + Eight Ages hues);
`config/___config.md`.
**Delivers:** `PALETTE_PRESETS` octa primary/light replaced with the
APPROVED hues, pin test, before/after offscreen renders for the
owner's eyes.

### Session 4 — Archetype prompt sheets → **Opus**
**Say:** "Radi Sesiju 4 iz WORKPLAN.md — prompt sheetovi za
preostale arhetipe, jedan arhetip = jedan fajl."
**Reads:** CANON.md IN FULL; `research/prompts/___prompts.md`;
`research/prompts/archetype/trinity_prompts.md` as the template;
`research/bond_theme.md`.
**Delivers:** one sheet each for Trinity secondary (Family + the
Hearth), Prism secondary (One Soul pillars), Seasons (temperaments;
tetramorph if approved by then), Compass primary (Walks + objects),
Compass secondary (Ages + the image layer the owner picks — Tree ★ or
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

### Session 6 — Archetype articles wave → **Opus** (writers) — DONE
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
`octa_primary`/`octa_secondary` variant paragraphs in
`Database/symbolism.json` still describe the OLD compass hues
(found in Session 3) — rewrite them to the Walks/Ages wheels.

### Session 7 — The poem Easter egg → **Sonnet** — DONE
**Say:** "Radi Sesiju 7 iz WORKPLAN.md — pesma iza šifre."
**Reads:** ROADMAP queue task 6; CANON.md Seasons section (the poem
text); `app/encyclopedia.md`; the hidden-mode listener in
`app/controller.md` / `app/report.md`.
**Delivered:** typing the cipher reveals the owner's four-greeting
poem in the Encyclopedia, bound to the Seasons; hidden otherwise;
test pins the gate. **Landed already as commit `c88113d`
(0.14.274)** — this session's own re-run (2026-07-19) ground-truthed
the unlock flow and the pinned test
(`test_hidden_mode_binds_the_poem_to_seasons_too`) and found it
exactly spec-shaped; no code changes were needed. See ROADMAP queue
item 6 for the evidence.

### Session 8 — Wider Pantheon topics → **Opus** (writers) — DONE
**Say:** "Radi Sesiju 8 iz WORKPLAN.md — Wider Pantheon
enciklopedijski topici."
**Reads:** CANON.md; `research/pantheon_catalog.md`;
`Database/encyclopedia.json` family structure (the Union ninths).
**Delivered:** four topics — Greek (Dionysus, Hephaestus, Hestia),
Norse (Baldur, Heimdall, Njord), Egyptian (Set, Nut, Geb, Ptah,
Sekhmet), Slavic (Crnobog, Stribog, Jarilo, Rod) — 15 seatless
A-list figures in the new `encyclopedia.json` "wider" family, wired
into The Wider Pantheon gallery group and the translation corpus
(ENGLISH ONLY — the old "SR synced" line is superseded by the owner's
2026-07-16 no-SR-during-development policy). The retired ninths
Set/Baldur/Crnobog folded in; `test_wider_pantheon_topics` pins
coverage/structure/graceful art.

### Session 9 — Mechanical sweep → **Haiku** (Sonnet where judgment is needed) — DONE
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

### Session 17 — the Observatory → **Opus** (owner tier correction 2026-07-17: Fable only for truly cross-system novel work) — DONE
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

### Session 18 — Legend & hover laws → DONE (2026-07-26, 0.14.432)
**Say:** "Radi Sesiju 18 iz WORKPLAN.md — zakoni legende i hovera iz
CUBE.md."
**Reads:** CUBE.md §Display and Legend Laws; `render/compositor.md`
(hover paths, `_hover_title`); `app/controller.md` (the Spacebar
jump).
**Delivered (same session that wrote CUBE.md):** (1) THE
WEEKDAY-TITLE LAW — ghost bodies, Sunday faces and dual-card columns
all name their day beside the title (`test_weekday_title_law_names_
the_day_on_ghost_bodies`); (2) THE LEGEND BOLD LAW — the accents
rainbow machinery deleted end to end (compositor, encyclopedia,
defaults), plain bold on virtue/vice/mood/WEEKDAY only
(`test_legend_highlighting_bolds_the_spine_only`); (3) THE HOVER
TEASER LAW — `_teaser` thesis truncation on every article hover
(instrument cards, ring-letter legends and the Greetings exempt) and
the `_learn_more_footer` on every page-owning hover, clickable
through `LegendPopup.on_link` → the widget's captured-target jump
(`test_hover_teaser_law_truncates_to_the_thesis`,
`test_learn_more_footer_names_both_roads`). 894 tests green.

### Session 19 — Cube prompt sheets → **Opus** — DONE (2026-07-26, 0.14.433)
**Say:** "Radi Sesiju 19 iz WORKPLAN.md — prompt sheetovi za Cube
kanon."
**Reads:** CUBE.md IN FULL; CANON.md §The Cube Canon;
`research/prompts/archetype/trinity_prompts.md` as template.
**Delivered:** four sheets — Genesis (7 files), Council (13 on Route A,
1 on Route B), Character (16) and the Two Crosses (20) — each opening
with a WRITTEN Rule 19 derivation check (the Rose is COMPUTED geometry
and gets no sheet at all; the inversion, the Diamond/Cube toggle, the
blend hues, tints and the ciphers are all derived or text). Every sheet
dry-run clean in PromptPainter; the four new family roots recorded in
`tests/test_prompt_paths.py`; the ledger's §The Cube Wave added to
[Prompt Coverage](research/prompts/COVERAGE.md). The crosses are
LETTERLESS by house rule — FALL/STAR/DOMY/SAFE and the Latin/Greek rows
live in the articles, with an inscribed variant offered as a pathless
PENDING OWNER option. Open for the owner: the Council's route (new
tellings vs reuse), the Genesis centre's name and its 24h display name
(CUBE's "God" vs the Court's "The One"), the crosses' one Faith reuse
candidate, and the six OPEN Character combo figures (Session 21).

### Session 20 — the Cube wheels engine → **Fable** — DONE (2026-07-27, 0.14.436)
**Say:** "Radi Sesiju 20 iz WORKPLAN.md — treći točkovi i Ruža."
**Reads:** CUBE.md IN FULL; the archetype engine docs
(`render/compositor.md`, `app/controller.md`, `data/` docs,
`Database/ring_presets.json` for the Rose).
**Delivered:** (1) the THIRD-WHEEL slot — `palette_style` grew "cube"
on trio/hexa/octa only (`constants.palette_styles_for`; a stored
"tertiary" normalizes to "primary" on other pointers at ONE choke point,
`defaults.effective_palette_style`, and survives the switch back) —
the Design window's wheel row shows Court/Family/**Genesis**,
Paint/Light/**Council**, Walks/Ages/**Character**, and the archetype
grid seats `trinity_genesis`/`prism_council`/`compass_character`
(figures name-fall-back until the owner's glass and Session 21's
articles land); (2) the GENESIS INVERSION — one 180° offset
(`render.layers.arm_offset_deg`) feeds the star diamonds, Aura
wedges, weekday slots, lit-index math and arm hit-test together, and
the plain arm hover speaks its creation office (God—Creator 24h,
Jesus—Preserver 08h, the Devil—Destroyer 16h) with the pending line;
(3) the DIAMOND/CUBE toggle — `Settings.cube_look` (Settings ▸
Display ▸ Archetype): on the Court/Genesis/Council the arm halves
widen to 180/N and the standing star formula tiles the hexagon into
the corner-view cube faces (verified by offscreen render); (4) the
ROSE ring preset — a `{"name": "Rose", "rose": true}` card, pure
computed geometry (Rule 19): the procedural plain hour scale + 24
diamond rays in the band, three octa stars z-ordered −1h
(Historical) / 0h (Modern) / +1h (Archetypal, on top — its rays ON 1h
and 13h), hues `defaults.ROSE_PALETTE` sampled from the owner's
drawing and SHARED with the Character wheel (one tuple), and a
COMPUTED 24-entry per-ray hover legend riding the standing
letter-legend machinery. 24 new goldens in `tests/test_cube_wheels.py`;
922 tests green.

### Session 21 — the Cube Encyclopedia wave → **Opus** (writers) — DONE (2026-07-27, 0.14.460–0.14.464)
**Say:** "Radi Sesiju 21 iz WORKPLAN.md — Cube enciklopedija."
**Reads:** CUBE.md IN FULL (the Article Charter BINDS this session);
CANON.md quote rules.
**Delivered:** (1) THE ARCHETYPES HALL, empty since round R3, now
holds the Cube canon's three topics — **The Cube** (20 pages: the
three axes, the six poles, the eight vertices, the three figure sets,
the coordinate doctrine and the Banknote-axes seal), **The Double
Trinity** (5: Court, Genesis, Council and the 24-field union table,
whose twelve office/process pairs are assigned four to each person)
and **The Two Crosses** (14: both paths, all eight stations,
TRUST/DISTRUST, the Latin and Greek rows, FALL/STAR and DOMY/SAFE) —
39 pages in the new `cube`/`double_trinity`/`crosses` families of
`encyclopedia.json`, every one written in the Charter's four movements
(`[[Thesis]]`/`[[Argument]]`/`[[Correspondences]]`/`[[Quote]]`);
(2) THE THREE WHEELS' ARTICLE SETS — `archetype_trinity_genesis` (4),
`archetype_prism_council` (7) and `archetype_compass_character` (8) —
so the coverage law in `test_archetype.py` lost its exemption and now
checks 67 seats instead of 48, and no wheel speaks the pending line;
(3) THE SPACEBAR CONTRACT — each Cube wheel arm jumps to the page it
argues (every Character arm onto its own pole or vertex); (4) THE SIX
OPEN COMBO FIGURES SEALED under the owner's delegation ("ti pečatiš"):
Alfred Pennyworth / Severus Snape (Devotion), Charles Xavier
(Patronage), Steve Rogers (Conviction), Father Ferapont and Silas
(Mortification); (5) THE THEME NAME sealed — all three kept, "One
Soul" alone wherever one name must stand
(`constants.ONE_SOUL_THEME_NAME/_TITLE`); (6) THE CHARTER REWORK
PASS — **21 articles** rewritten off scene description, art-asset talk
and belles-lettres onto thesis→argument→correspondences→quote. 22 new
pins in `tests/test_cube_encyclopedia.py`; 977 tests green.

### Session 22 — the Renaming → **Sonnet** — DONE (2026-07-27, 0.14.465–0.14.467)
**Say:** "Radi Sesiju 22 iz WORKPLAN.md — WATCH ACADEMY svuda."
**Reads:** CUBE.md §The Name; root CLAUDE.md Rules 22–23.
**Delivered:** WATCH ACADEMY applied at every naming surface that
actually exists today: the README opening paragraph (now Rule #22's
About text, synced via `gh repo edit --description`) plus a new "The
Name" section carrying the proposed tagline and the VIGILATE seal;
the Guide window's `dial_default` slide (the app's closest thing to
an About screen — no dedicated About dialog exists) now introduces
Watch Academy and echoes the tagline in English prose. `constants.
APP_NAME` ("DOMY Watch"), the tray tooltip, every window title, the
mutex, the AppUserModelID and the `%APPDATA%` folder are UNCHANGED —
DOMY remains the dial's own name and the app's technical identity,
exactly as scoped. **CANNOT do yet (infrastructure absent, not a
renaming-session job):** an actual About dialog (none exists — Guide
was chosen over it, see `app/guide.md`) and the Rule 23 self-update
module (no `updates.py`/version source in this project yet) — both
would be new M6/M7 features, not a rename. Seeded the decision
instead so neither has to be re-derived later: `setup/app_info.json`
(new, pre-M7) carries `name`/`description` = Watch Academy while
`exe_name`/`installer_name` stay DOMY-based, pinned by the new
`tests/test_app_info.py`; ROADMAP.md's M7 section records the
`update.repo` value for when self-update eventually lands (that value
was `"UVuruna/DOMY-Watch"` while the repo still bore that name —
CORRECTED to `"UVuruna/Watch-Academy"` on 2026-07-28). The GitHub
repo rename itself was
**not** executed (owner decree: `gh repo rename` never runs
automatically) — flagged as an open question below. 978 tests green.
**UPDATE (found 2026-07-28, Session 23's push):** the owner renamed
the repo himself, outside any session — `git push` now returns "This
repository moved. Please use the new location:
`https://github.com/UVuruna/Watch-Academy.git`". The open question
below is RESOLVED; `update.repo`/the disk folder name are their own,
separate, still-open follow-ups (see below).

### Session 23 — Rose Sunday hover fix + the Duality-Axes config → **Sonnet** — DONE (2026-07-28, 0.14.504–0.14.505)
**Say:** "Radi Sesiju 23 iz WORKPLAN.md — Rose hover bug i duality
config."
**Reads:** CUBE.md §The Rose (Sunday axis, weekday law) and §The
Thirteen Axes (Colour Law, Sacred Axis, the Duality-Axes decree);
`render/compositor.md` (hover paths, hit-tests); `config/___config.md`;
the creeds duality's data seat.
**Delivered:** (1) THE BUG (owner screenshot 2026-07-28): two
`render.compositor` hit-test sites (`_element_at`, `_weekday_body_at`)
hardcoded `constants.SOUTH_SLOT_ANGLE` (24h) for the Servant's own
seat instead of calling `render.layers.servant_seat_angle` like every
draw/label site already did — on the Rose the Servant sits at 06h/
270° instead, so the two Sunday faces drew on the Sunday axis but
hovered at the legacy bottom seat (also silently eating Wednesday's
real 24h hover on Sundays); both sites fixed, pinned by
`test_rose_sunday_hover_fires_on_the_sabbath_seat_not_the_legacy_
bottom` (root Rule 25). (2) THE DUALITY-AXES CONFIG (owner decree
2026-07-28, root Rule 4 — no hardcode): `constants.
DUALITY_RULER_ON_COLD_POLE` lists dual weekday themes whose Sunday
Ruler/Servant reverses the Rose's blind default (Ruler warm/red-18h,
Servant cold/blue-06h); the proof case, **religion: Christianity
(Ruler) pulls to blue/cold, Satanism (Servant) to red/warm** — the
Sacred Axis reversing what the blind default drew. The Compass/
Seasons' vertical Ruler-at-top default never flips (owner decree) —
only the Rose's horizontal Sunday axis is per-theme.
`render.layers.ruler_seat_angle`/`servant_seat_angle`/`weekday_slots`
are the three readers; the flip swaps which arm each face rides,
never its name, plate or article. Four new tests pin the config path
and the creeds orientation; 1049 tests green (one pre-existing,
unrelated failure: an untracked `assets/zodiac/` folder from the
owner's own parallel art generation, outside this session's scope).

### Session 24 — the Sacred rosters → **Opus** (writers) — DONE (2026-07-28, 0.14.520–0.14.521)
**Delivered:** (1) NOTHING TO FOLD — the blanket seal stood, no term
flipped. (2) THE ROSTER ROUND, under FAME FIRST and the ranking
addendum: the **16 new edge readings × 3 sets = 48 seats** peopled
(Prudence/Indifference · Ardor/Vendetta · Steadfastness/Machination ·
Reform/Zealotry · Meekness/Despair · Aspiration/Megalomania ·
Self-Mastery/Disdain · Diligence/Servility), each figure carrying one
named deed, plus the **two sacred corners' echoes** — Jesus and the
Devil themselves in the mythic set, **Maximilian Kolbe / Aslan** and
**Nero / Sauron** in the historical and modern ones; **the centre takes
no figure in any register** (owner verdict — every human exemplar is
ruled by something, The One by nothing). CUBE.md §[The
Rosters](CUBE.md#the-rosters) records the tables, the hooks, the
alternates and the three set-asides (Odysseus for Machination, Marie
Antoinette on the apocryphal line, Machiavelli). (3) THE ROSE §OPEN 48
were ALREADY WRITTEN, as suspected — the 2D eight are the poles' and
combos' sealed figures, the 3D eight the vertex roster — so the round
WIRED them instead of reinventing: `config.cube.ROSTER` now holds all
**26 human cells × 3 registers × 2 readings** (the sealed 108
transcribed, the 48 new added), `cube.FIGURE_SETS` is the one place the
three set words live (the star map's private "myth" retired — the star,
the roster and the disk register finally speak one vocabulary), the two
Cube wheels' rows carry their cube `cell`, and `archetypes.roster_names`
is the name-fallback reader. A structural law fell out and is pinned:
**a figure repeats only between a vertex and its own flat shadow** (the
Character wheel is the Cube at depth zero) — proved from coordinates,
not from a list. 15 new pins in `tests/test_cube_roster.py`, the first
of which fails the moment a name in the engine cannot be found in
CUBE.md; 1089 tests green. **NOT done, and named so no session assumes
it:** the Rose's three stars still DRAW one set of seat names —
`ArchetypeLayer` paints one star's worth of figures, so per-register
figures on the dial (with their hover and hit-test) are a RENDER round,
not a roster one.

### Session 24 — as originally written
**Say:** "Radi Sesiju 24 iz WORKPLAN.md — novi rosteri."
**Reads:** CUBE.md §The Thirteen Axes IN FULL (grid, naming laws,
alternates, rejected list); CANON.md quote rules.
**Delivers:** (1) IF the owner's deeper pass has flipped any term
by then, fold the flips into CUBE.md first (the blanket seal of
2026-07-28 already sealed the whole grid, alias and epigraph —
otherwise nothing to fold); (2) THE
ROSTER ROUND under FAME FIRST **plus the ranking addendum
(2026-07-28: fame, then famous-FOR-the-trait)**: the 16 new edge
readings × 3 sets (48 seats) + the two SACRED seats' historical and
modern echoes (the mythic principals are Jesus and the Devil
themselves — owner: "istorijske ličnosti i moderne filmske uz
ISUS–ĐAVO koji idu u mitsku glavnu tematiku"); check whether the
Rose §OPEN 48 are already satisfied by the sealed vertex/2D rosters
and WIRE, don't reinvent; (3) rosters recorded in CUBE.md tables
and wired into the engine's name fallbacks.

### Session 25 — the Thirteen-Axes texts + sheets → **Opus** (writers) — DONE (2026-07-28, 0.14.522–0.14.525)
**Delivered:** (1) THE TEXTS — the `cube` family grew **20 → 42 pages**:
the doctrine block (The Thirteen Axes' arithmetic; The One in BOTH
descriptions, apophatic and cataphatic, with the empty exemplar column
written as doctrine; The Sacred Axis with its five stations, three
readings and the ONE sentence distinguishing it from the doctrinal
Trinity; The Sixty-Five Terms with the economy and naming laws), the
**nine axis pages** the canon still owed (six edge axes, three vertex
axes — the three primaries already had theirs), the **eight new edge
cells** arguing all sixteen new readings with their six figures each,
and **The Hexagram Projection** carrying both X-rays and the blindness
law. Charter movements throughout; the corpus-wide rule-4 lint stayed
green on first run. (2) TWO CANON CORRECTIONS FOLDED IN: the Y-axis page
is renamed **The Moral Scope Axis** (owner approval 2026-07-28) and
carries the structural gloss *Universalism ↔ Particularism, purple
first*; `research/prompts/___prompts.md`'s stale "the Rose is a RING
PRESET" paragraph is corrected to the sealed POINTER doctrine. (3) THE
READING ORDER is now `config.cube.AXES`' own family order — doctrine,
primaries with their poles, edge axes with the new cells, vertex axes
with their corners, then what the cube reveals — so the sixteen
Spacebar targets of the Character and Prophecy wheels were re-aimed in
the same commit, as the index contract requires. (4) THE SHEETS, under
the coverage law: **73 images** in three sheets — Edge Cells (16
lancets + circles, the family's own CLEAR THIRD PANE device for the
axis held at measure), the Sacred Plates (9 — The One as a figureless
rosette, the Sacred Axis as five unequal bands, and the six people of
the two sacred seats) and Edge Figures (48 deed badges, 32 named / 16
descriptive / 0 reference stills). All three dry-run clean through
PromptPainter. **What the Rule 19 derivation check REMOVED, in
writing:** the twelve human axis pages take no plate (an axis IS its two
ends through the centre, which the Rose already draws) and the hexagram
projection is the dial's own emblem — both left PENDING OWNER, not
closed. (5) NAMED, NOT FILLED: the Activation pole's own 12 figure
badges are the last cells of the Rose with no sheet anywhere
(COVERAGE.md §The Thirteen-Axes Wave) — out of this session's scope,
proposed for the next figure round. 1094 tests green.

### Session 25 — as originally written
**Say:** "Radi Sesiju 25 iz WORKPLAN.md — tekstovi trinaest osa."
**Reads:** CUBE.md §The Thirteen Axes (the Article Charter BINDS);
the sealed rosters from Session 24; `research/prompts/COVERAGE.md`
and a cube-wave sheet as template.
**Delivers:** the Encyclopedia texts: The One (BOTH descriptions —
apophatic AND cataphatic, per decree), the Sacred Axis (five
stations, three readings, the distinguishing sentence from the
doctrinal Trinity), the 13 axis pages, the 16 new edge readings'
articles, the hexagram-projection page (Offices and Being views,
the blindness law); Charter movements throughout; prompt sheets
queued for every article with text (the coverage law), each sheet
opening with the Rule 19 derivation check (most cube geometry is
computed, never drawn).

### Session 26 — the Seating geometry → **Opus** — DONE (2026-07-28, 0.14.510–0.14.515)
**Delivered:** CUBE.md §The Seatings — both wheels solved by exhaustive
search (`core/cube_seating.py`, `config/cube.py`), every seat pinned by
`tests/test_cube_seating.py` (which re-runs the search rather than
trusting the constants), both wheels drawn to `research/seating/*.png`.
**Re-solved the same day** under the owner's FIRST LAW — *"primarna je
simetrija, sekundarna je simbolika"*: the first pass argued every arm
from meaning and let the three primary axes fall on three neighbouring
months; the owner threw it out. The figure is now the hexagram (3 face
axes on a triangle, 3 corner axes on the opposite one, 6 edge axes on the
hexagon between), on the owner's own arms — Calendar 12h/20h/4h with an
inverted version, Rose 12h-24h / 4h-16h / 20h-8h. The rotation↔hour rule
is CLOSED as posed (no rotation of order 24; the dial's half-turn is the
inversion, not a turn) and survives only as the four-watches frame.
Ahead: wiring either seating to a live pointer.
**Say:** "Radi Sesiju 26 iz WORKPLAN.md — geometrija rasporeda."
**Reads:** CUBE.md §The Thirteen Axes (Display Plans, the
24-orientations note) and §The Rose; `render/layers.md`; the
Prophecy Hamiltonian precedent (CUBE.md §Seating the eight).
**Delivers:** the theorem-guided seatings — **Calendar-12** (owner
2026-07-28): each of the twelve arms carries ONE human axis, its
two ends the arm's two personalities, the centre medallion the ONE
central sacred slot; which axis on which month argued from seasonal
kinship; **Rose-24**: the 24 human seats on the 24 rays (dial
adjacency = cube kinship, exhaustive search like the Prophecy
wheel) with the THREE central sacred seats; the rotation↔hour rule
if it falls out (24 orientations = the permutations of the four
diagonals). Golden tests pin every seating; offscreen renders for
the owner's eyes. (Opus: geometry — accuracy > speed.)

### Session 27 — the Encyclopedia rework (celine) → **Opus** — DONE (2026-07-28/29)
**Delivered:** the three-level browser the owner specified live in the
session (eight decisions sealed 2026-07-28):

1. **SIX WHOLES** on a home screen that never scrolls — The Instrument
   (the watch's own wheels, the old Celestial Engine split in two), The
   Celestial Engine (the sky), The Divine, The Human Wheel, The
   Character Cube (promoted out of the empty "Archetypes" hall) and The
   Living World. Each wears one hue of the Rose (`config/
   encyclopedia_tree.py` — the ONE table every screen reads).
2. **THE VARIANT LAW** — registers of one subject merged into one card
   whose ◀ ▶ switcher walks them keeping the reader's position (Greek:
   Planetary | Pantheon | Wider Court; Bible ×3; Creeds ×2; Eclipses
   ×2). Distinct subjects stayed their own cards. The Pantheon roster
   button retired into it (Rule #6).
3. **THE CUBE SPLIT** — the 42-page run became four cards (Doctrine,
   The Thirteen Axes, The Eight Figures, The Projections); the wheel
   table's `enc=("cube", N)` targets are re-aimed by `tree.cube_target`,
   so `config/archetypes.py` was not touched.
4. **THE GUIDE** became the fifth Instrument card, built from the help
   book's own JSON; `app/guide.py` retired, the menu entry now a
   shortcut into the browser.
5. **THE GOD-FILE SPLIT** — `app/encyclopedia.py` (2,766 lines) became
   the nine-module `app/encyclopedia/` package (root Rule #20), each
   with its own `.md`.
6. **THE SCROLL LAWS** — the window's minimum IS the owner's 1280×720
   opening screen; the home screen owns no scroll area at all; both
   scrolling screens have their horizontal bar switched OFF and their
   geometry cannot produce an overwide row.

**Pinned by** `tests/test_encyclopedia_tree.py` (20 laws) plus the
rewritten Encyclopedia block in `tests/test_settings_dialog.py`.
**Ahead:** the coverage wave — 92 pages carry no image SLOT at all and
130 no image FILE; the owner's verdict was "sve generisano", so every
one of them is owed a prompt-sheet entry.

### Session 28 — the 3D Preview integration → **Sonnet** — BLOCKED on the gadget's M2
**Say:** "Radi Sesiju 28 iz WORKPLAN.md — 3D Preview u
Enciklopediji."
**Reads:** `Gadgets/3D Preview/PLAN.md` (the integration contract);
CUBE.md §The Thirteen Axes; `app/encyclopedia/___encyclopedia.md`;
`Database/encyclopedia.json` cube families.
**Delivers:** the DOMY-side half of the contract: an EXPORTER that
computes the Character-Cube model JSON from DOMY's own canon data
(the 65 terms, colors, registers — one source of truth, root Rule
19, never copy-pasted into the gadget); the `preview3d` widget
embedded in an Encyclopedia dialog (seated in the Session 27
**Character Cube** whole, beside its four Cube cards), hover wired through the
teaser law, click through the Spacebar-jump contract; tests on the
exporter's schema and the embed's open path. Runs only after the
gadget's M2 (the four models + Switcher) exists.

### Session 29 — the Pointers rework → **Fable** (orchestrator) — DONE (2026-07-29, 0.14.545 / 0.14.555 / 0.14.556)

Owner sheet `UV/Pointers.png`, run as three sequential agents (opus,
opus, sonnet). Delivered: (1) the SHAPE law — every pointer but Aurora
picks STAR or POLYGON; the polygon is literally the polygon (square /
hexagon / octagon, one vertex per arm tip; Trinity alone draws the
cube), with the curvature slider and its two edge forms (smooth
concave / V-notched) on the four true polygons; the Calendar's star is
two interleaved hexagrams, its polygon a 12-point star; the Rose's
polygon one 24-ray star. (2) The OFFSET wheels — Seasons +45°
(astronomical, boundaries on the cardinals), Rose Prophecy +7.5°
(hours worn :00–:59), and the Rose's Aura finally standing behind its
own hue groups on both wheels — the +7.5° shift was REVOKED in the
correction round below, and both wheels keep every ray on a full hour.
(3) `hide_night_borders` for all.
(4) The Calendar normalized — the lit-wedge feature deleted, the mount
moved into the Pointer Theme window, and the offer registry-driven:
zodiac / almanac / Slavic months / Chinese animals / emotions, each
with its own sealed thirteenth-in-the-center rule (`core/blue_moon`
now table-driven). (5) The three Design-window rows. Tests
1127 → 1219 passed; regression pins on every sealed angle.

### Session 29b — the Pointers CORRECTION round → DONE (2026-07-29)

The owner looked at the live watch and sealed four corrections, which
supersede the matching parts of Session 29 above:

1. **The lead line is universal.** The Rose's black outline was "the
   good example": EVERY drawn arm and polygon face wears it now — trio
   (cube included), cross, hexa, octa, Calendar (both figures), Rose
   (both) — in the star and polygon shapes alike, internal colour
   boundaries included, since each face is stroked as its own path. The
   armless Aurora is the one exception. `palette.ROSE_ARM_OUTLINE` /
   `defaults.ROSE_ARM_OUTLINE_WIDTH` became the pointer-neutral
   `palette.ARM_OUTLINE` / `defaults.ARM_OUTLINE_WIDTH`.
2. **The Prophecy +7.5° shift is REVOKED** — with it
   `constants.ROSE_WHEEL_ASSEMBLY_OFFSET_DEG`, `ROSE_RAY_PITCH_DEG`,
   `rose_assembly_offset_deg()`, `wheel_offset_deg()` and
   `aura_group_offset_deg()`. Both Rose wheels keep every ray tip on a
   FULL hour; the per-wheel difference moved into the BACKGROUND, as
   the owner's own numbers: Legacy tips 10h/11h/12h with the wedge
   9h → 12h (it TRAILS its lead ray), Prophecy tips 11h/12h/13h with
   the wedge 10:30 → 13:30 (CENTERED). One table,
   `constants.AURA_WEDGE_ANCHOR_DEFAULT` / `ROSE_AURA_WEDGE_ANCHOR`.
3. **The daylight switch reaches the background.** With it off the
   Umbra paints FLAT (one circle in the contrast span's lightest shade)
   and the Aura floods the whole circle at the day alpha; with it on
   the CALENDAR's twelve wedges now obey `lit_regions` like every other
   pointer instead of flooding the circle at a fixed alpha
   (`defaults.CALENDAR_WEDGE_ALPHA` deleted with that path). The figure
   FACES keep reading the real sun — the switch flattens the disc
   colouring alone.
4. **UI.** Settings ▸ Display's checkbox is "Daylight - Night"; the
   Design window's "Hide night borders" row greys out whenever it
   cannot act (Calendar/Rose with the daylight switch off).

Tests 1219 → 1251 of this session's own count (suite green); the dead
half-hour law is pinned dead by
`test_both_rose_wheels_keep_every_ray_on_a_full_hour`.



- **Owner art generation** from the sheets: pantheon plates,
  Satanism dual, Eleusis, the scale glass set (incl. the two
  Unions), Cat/Ophiuchus, season badges — and the archetype art
  once Session 4 lands. The wiring already degrades gracefully;
  every drop simply lights up.

## THE THEME BACKLOG — twelve casts on disk, nothing wired

**Read this preamble before opening Session 30, 31, 32 or 33.** It
exists so no agent has to ask what the sessions below are for, and so
no agent re-opens a question that is already closed.

### What was found (2026-07-29)

Twelve figure casts — six themes' worth — have their art GENERATED and
sitting in `assets/weeks/`, and the program cannot show a single one of
them. **429 files, about 215 distinct plates** (each in the two sources,
`_gem` and `_gpt`):

| Cast (folder) | Files | Group on disk | Its prompt sheet |
|---|---|---|---|
| `age_of_heroes` (Greek Monsters) | 38 | `weeks/myth/` | `research/prompts/monsters/greek_monsters_prompts.md` |
| `celestial_court` (Chinese Mythology) | 38 | `weeks/myth/` | `research/prompts/chinese/chinese_myth_prompts.md` |
| `corporate` (The Corporation) | 38 | `weeks/crafts/` | `research/prompts/corporate/corporate_prompts.md` |
| `wow_alliance` / `wow_horde` / `wow_evil` | 38 / 38 / 34 | `weeks/gaming/` | `research/prompts/wow/wow_prompts.md` |
| `cp_gangs` / `cp_street` / `cp_corpo` | 58 / 54 / 50 | `weeks/gaming/` | `research/prompts/cyberpunk/cyberpunk_prompts.md` |
| `sw_jedi` / `sw_sith` / `sw_dyad` | 22 / 18 / 3 | `weeks/films/` | `research/prompts/starwars/starwars_prompts.md` |

**Why they are invisible:** none is in `constants.WEEKDAY_THEMES`, so
the dial's theme picker does not know they exist; and none has an
Encyclopedia topic. `config.taxonomy` knows their FOLDERS — the tree
law is satisfied, the art is correctly placed — but the registry does
not know their KEYS. This was not an accident of one round:
[Prompt Coverage](research/prompts/COVERAGE.md) items 1a and 1b
recorded "two wiring rounds left for later" when the sheets shipped.
Later never came, and nothing in the suite could notice.

**The two costs are not the same size, and that shapes the whole plan:**

- **Wiring** is mechanical: about a dozen config entries per cast, all
  transcribable from the cast's own sheet and its own folder. Hours.
- **TEXT is the real bill.** Not one of the twelve has a single written
  article — not Sun Wukong, not Typhon, not Sylvanas, not Johnny
  Silverhand. At the MANDATORY minimum a cast needs **17 texts**
  (7 seat articles + 7 hover blurbs + title + duality + ninth ≈ 12,000
  characters of house voice); with the optional per-wheel `variants` it
  is 59. Twelve casts is **~200 mandatory texts, ~145,000 characters**.
  That is three writing waves, not one session.

### Three structural questions — ALREADY ANSWERED, do not re-open

1. **Three casts of one franchise are three THEMES on the dial, not a
   third roster value.** `constants.FIGURE_ROSTERS` is a two-value
   GLOBAL switch (`planetary` / `pantheon`) that every theme obeys at
   once; a third value would change every other theme's meaning. The
   disk already settled it — the art shipped as `wow_alliance/`,
   `wow_horde/`, `wow_evil/`, and `taxonomy.WEEK_GROUPS` lists all six
   gaming casts as separate theme folders. Three keys, one picker
   group.
2. **In the ENCYCLOPEDIA those same three casts are ONE card with a
   three-way switcher**, not three cards. That is Session 27's own
   variant law (`config.encyclopedia_tree.VARIANT_SOURCES`, the ◀ ▶
   beside the title), built for exactly this shape and already carrying
   the Planetary/Pantheon merges. The dial shows one cast at a time; the
   reader walks them.
3. **The code KEY is the FOLDER name** — `age_of_heroes`,
   `celestial_court` — not the old sheet names (`monsters`,
   `chinese_myth`). Those two entries in `taxonomy.THEME_KEY_RENAMES`
   exist only because the folders were renamed while the themes were
   art-only; a rename table is for MIGRATING stored user settings, and
   no user has ever had these themes selected. The wave that wires a
   cast **deletes its rename entry** in the same commit.

### THE PER-CAST CHECKLIST — the one table every wave works from

Every cast needs all of this. A wave is not done until each line is
true for each of its casts.

| # | Where | What to add |
|---|---|---|
| 1 | `constants.WEEKDAY_THEMES` | the key |
| 2 | `constants.WEEKDAY_THEME_BLURBS` | key → its own blurb-set name |
| 3 | `constants.WEEKDAY_THEME_ARTICLES` | key → its own article-set name |
| 4 | `constants.WEEKDAY_THEME_NINTHS` | `(display name, "<theme>/primary/bronze/<Stem>.png")` |
| 5 | `constants.METAL_THEMES` | the key — every one of these casts is bronze-plate art with a `colored/` sibling |
| 6 | `defaults.WEEKDAY_THEME_NAMES` | the seven seat DISPLAY names (`sun` … `saturn`) |
| 7 | `defaults.WEEKDAY_THEME_DIRS` | `"<theme>/primary/bronze"` |
| 8 | `defaults.WEEKDAY_THEME_FILES` | the seven seat file STEMS |
| 9 | `defaults.WEEKDAY_DUAL_NAMES` | `(ruler name, servant name)` |
| 10 | `defaults.WEEKDAY_DUAL_FILES` | the servant plate, sourceless |
| 11 | `defaults.WEEKDAY_THEME_TITLES` | the human theme title |
| 12 | `defaults.WEEKDAY_MENU_GROUPS` | the picker group — **new groups "Gaming" and "Films"** for the six gaming and three film casts |
| 13 | `config.encyclopedia_tree` | a seat in a WHOLE, and `VARIANT_SOURCES` for the three-cast merges |
| 14 | `taxonomy.THEME_KEY_RENAMES` | DELETE the entry, if this cast has one (see question 3) |
| 15 | `Database/symbolism.json` → `articles.<set>` | 7 seats, each `{name, base}`; the SUN seat also `{faces: {ruler, servant}}` |
| 16 | `Database/symbolism.json` → `arms[].blurbs.<set>` + `center.blurbs.<set>` | 7 hover lines, ~100–250 characters each |
| 17 | `Database/encyclopedia.json` → `theme_title.<key>` | the theme's own title article |
| 18 | `Database/encyclopedia.json` → `week_duality.<key>` | the dual page's article |
| 19 | `Database/encyclopedia.json` → `ninths.<Ninth name>` | the ninth's article |
| 20 | tests | the cast passes the theme-completeness guard (Session 30) with NO exemption left |

**Optional and explicitly NOT required** (graceful by contract, Rule
#1's documented path): `articles.<set>.<seat>.variants` — the six
per-pointer-wheel readings. A missing `variants` falls back to `base`.
Write them only if the wave has room; never at the cost of a `base`.

**English only** (project rule, root Rule #17). The Serbian bundle is
brought to coverage in Session 15, immediately before the build.

### The order, and why it is this order

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart LR
    S30[S30 - the LAW<br/>guards + ledger] --> S31[S31 - myth and crafts<br/>3 casts]
    S30 --> S32[S32 - gaming<br/>6 casts]
    S30 --> S33[S33 - films<br/>3 casts]
    S31 --> S34[S34 - queue audit]
    S32 --> S34
    S33 --> S34
    G[(3D Preview gadget<br/>its OWN agent, M2)] --> S28[S28 - 3D integration]
```

- **The law comes FIRST**, before a single cast is wired. If the waves
  ran first, the guard would be written to pass whatever the waves
  happened to do; written first, it is the thing the waves are measured
  against — and it is what makes this failure impossible to repeat.
- **Each wave WIRES its own casts.** The owner's rule is that articles,
  prompts and wiring ship together, so splitting "all the text" from
  "all the wiring" would violate the very law being written. Every wave
  therefore ends with its casts VISIBLE — pickable on the dial and
  readable in the Encyclopedia.
- **The waves are independent of each other** and may run in any order;
  they touch disjoint casts and disjoint JSON keys. The only shared
  files are the config tables, so two waves must not edit the same
  table at the same moment — run them sequentially unless the owner
  explicitly asks for parallel agents.
- **The 3D session stays where it is** (Session 28), blocked on the
  gadget's own M2. It is the only task here with an EXTERNAL
  dependency, and by the owner's decree DOMY sessions never implement
  the gadget.

---

### Session 30 — The Theme Completion Law → **Sonnet**

**Say:** *"Radi Sesiju 30 iz WORKPLAN.md — zakon o kompletnoj temi."*

**Reads:** this preamble; `CLAUDE.md` (project);
`research/prompts/COVERAGE.md` §1a/1b; `config/___config.md`;
`tests/test_assets_structure.py` (the guard style to copy).

**Delivers:**

1. **The law is ALREADY WRITTEN** — project [CLAUDE.md](CLAUDE.md)
   §THE THEME COMPLETION LAW, landed 0.14.552 the day the owner
   decreed it, so it cannot be lost if this session slips. This
   session does not rewrite it; it ENFORCES it (items 2 and 3) and
   links it from `COVERAGE.md`.
2. **`research/theme_staging.md` — the STAGING LEDGER.** One row per
   art-only cast: folder, files on disk, its sheet, what it still owes,
   which session owes it. The twelve casts above are its first rows.
3. **Two guard tests** in a new `tests/test_theme_completeness.py`:
   - *no registered theme is textless* — every key in
     `WEEKDAY_THEMES` resolves an article set, a blurb set, a title
     article and (where it has a ninth) a ninth article. This one
     passes today and must never stop passing.
   - *no art sits unseen* — every theme FOLDER under `assets/weeks/`
     is either registered in `WEEKDAY_THEMES` **or** listed in the
     staging ledger with an owed-items line. This one FAILS today with
     twelve names, and each wave deletes its own rows until it passes
     empty. **That failure is the deliverable** — it is the sentence
     the suite could not say before.

**Done when:** the suite is green with the ledger holding exactly the
twelve casts, the law is in `CLAUDE.md`, and `COVERAGE.md` items 1a/1b
point at the ledger instead of describing the debt in prose.

---

### Session 31 — Completion wave I: myth & crafts → **Opus** (writers)

**Say:** *"Radi Sesiju 31 iz WORKPLAN.md — talas I, tri postave."*

**Casts:** `age_of_heroes`, `celestial_court`, `corporate`
(3 × 17 = 51 mandatory texts).

**Reads:** this preamble and the PER-CAST CHECKLIST above;
[The DOMY Canon](CANON.md) — mandatory for any roster work; each cast's
own sheet from the table above (the sheets carry the sealed rosters,
every seat's reasoning and the ninth's argument — that is the writer's
source material, and it is already written); one existing article set
as the VOICE reference (`symbolism.json` → `articles.cosmos`, the most
recent complete set).

**Delivers:** all twenty checklist lines for its three casts, its rows
deleted from the staging ledger, and a Serbian report naming what each
cast now shows on the dial.

**Watch for:** the Greek Monsters cast shares its group folder with the
Greek gods — its articles must not restate the gods' own text, and its
Encyclopedia seat is a card of its own inside the same whole.

---

### Session 32 — Completion wave II: gaming → **Opus** (writers)

**Say:** *"Radi Sesiju 32 iz WORKPLAN.md — talas II, gaming."*

**Casts:** `wow_alliance`, `wow_horde`, `wow_evil`, `cp_gangs`,
`cp_street`, `cp_corpo` (6 × 17 = 102 mandatory texts — the biggest
wave; split into two commits, one per franchise).

**Reads:** as Session 31, plus `research/prompts/wow/wow_prompts.md`
and `research/prompts/cyberpunk/cyberpunk_prompts.md` in full — the
Cyberpunk sheet documents ROTATION SEATS (more than one named figure
sharing a day, resolved through `defaults.rotating_art_file`), a wiring
shape none of the other casts has.

**Delivers:** the checklist for six casts; **two** Encyclopedia cards
(one per franchise), each carrying a three-way variant switcher, NOT
six cards (structural question 2); the two new picker groups.

**Watch for:** the three WoW casts and the three Cyberpunk casts ride
the SAME nine seats with different figures — an article must argue THAT
cast's own figure, never the seat in the abstract (Charter rule 5 in
[The Cube Canon](CUBE.md): three sets on one seat are three different
people, never one character read three ways).

---

### Session 33 — Completion wave III: films → **Opus** (writers)

**Say:** *"Radi Sesiju 33 iz WORKPLAN.md — talas III, Star Wars."*

**Casts:** `sw_jedi`, `sw_sith`, `sw_dyad` (3 × 17 = 51 texts).

**Reads:** as Session 31, plus
`research/prompts/starwars/starwars_prompts.md` in full.

**Delivers:** the checklist for three casts; ONE Encyclopedia card with
a three-way switcher; the "Films" picker group.

**Watch for:** `sw_dyad` has 3 files on disk against the others' 18–22
— **its art is INCOMPLETE**. The wave writes its texts and wires it
exactly like the others (every missing plate is graceful-absent by
contract) and records the shortfall as an "art owed" row in the staging
ledger; it is not a reason to skip the cast. Anakin/Vader, Leia and Han
each appear in two casts at different ages — legitimate repeats, and
each article argues that AGE's own deed.

---

### Session 34 — The generation queue audit → **Haiku**

**Say:** *"Radi Sesiju 34 iz WORKPLAN.md — revizija reda za
generisanje."*

**Runs:** after 31–33, because wiring twelve casts creates new
Encyclopedia pages, and a new page can declare a plate nobody has
drawn.

**Reads:** `research/prompts/COVERAGE.md`;
`tests/test_encyclopedia_tree.py` (the coverage law's own tests).

**Delivers:** the census re-run — every declared plate resolved through
`paths.art_file` + `variant_pending`, every absent one cross-checked
against EVERY sheet under `research/`, **including
`research/rose_round/`, which one earlier audit did not search and so
reported nine files as owed when they already had briefs**; a
PromptPainter `--dry-run` over every touched sheet; the ledger updated
with the true remaining queue. Mechanical work, no judgment — hence
Haiku.

---

### Session 28 — the 3D Preview integration (AMENDED 2026-07-29)

The owner's decree of 2026-07-29 fixes WHICH pages become 3D, and the
answer is the whole Cube family — *"3 Axis main, 4 Axis diagonal
(temena), 6 Axis diagonal (ivice), CUBE"*. Those are exactly the four
models already specified as the gadget's v1 deliverable
(`Gadgets/3D Preview/PLAN.md` §The Four Owner Models), so nothing new
is being designed here; what this session adds is the PAGE LIST on
DOMY's side:

| Encyclopedia page | Today | After |
|---|---|---|
| The Cube | computed isometric (`cube_diagrams.whole_cube`) | the rotatable Cube model |
| The Thirteen Axes | computed (`thirteen_axes`) | the three axis models, switched |
| each of the 13 axis pages | computed (`axis`) | its own axis, lit in 3D |
| Composure · Vigor | computed (`pole`) — added 0.14.551 | their axis in 3D, the seat lit |

Every one of those pages already declares a DRAWER rather than a file,
so the swap is a change of drawer, not a change of contract — the
static figures stay as the fallback for as long as the gadget is
absent. Everything else in the original Session 28 entry stands.

---

## Open Owner Decisions (any session may receive the verdict)

- ~~The 27 PROPOSED terms of the 65-grid~~ — **SEALED 2026-07-28 by
  the owner's blanket approval**: all 27 terms stand, alias **Axis
  Mundi**, epigraph sealed; the owner reserves a deeper pass that
  may flip individual terms (alternates stay on record: Discernment
  / Contemplation / Entitlement / Service). Sessions 24–25
  UNBLOCKED.

- ~~Theme name~~ — SEALED 2026-07-27: the theme keeps **all three**
  names. Titled in full it is **One Soul — The Vow — The Bond**;
  wherever one name must stand alone (Design wheel row, menus, labels,
  watch title) it is **One Soul**. `constants.ONE_SOUL_THEME_TITLE`
  / `ONE_SOUL_THEME_NAME`; record in `research/bond_theme.md`.
- Compass secondary image layer: ★ the Tree / the Menagerie (CANON).
- Seasons tetramorph persons layer: yes/no (CANON).
- ~~**Slavic 13th month**~~ — **RESOLVED 2026-07-29: Modrenik STAYS.**
  The owner's words: *"we went the route of giving everything its
  twelve"* — so the thirteenth is not an exception to be trimmed but
  the axle every Dozen is entitled to. The sealed repo law is
  unchanged (±14 d of the December solstice, in a 13-full-moon year).
  The doctrine behind it is now written: CANON §The Axle — the
  Thirteenth in the Center.
- ~~**Olympians on the Calendar**~~ — **SEALED 2026-07-29: all twelve
  wedges + the center.** Zeus 12–14h, Athena 14–16h, Hephaestus
  16–18h, Artemis 18–20h, Ares 20–22h, Demeter 22–24h, Poseidon
  00–02h, Hermes 02–04h, Dionysus 04–06h, Apollo 06–08h, Aphrodite
  08–10h, Hera 10–12h; **center HESTIA, always present**. Table and
  arguments in CANON §The Olympians. The roster can mount.
- ~~**Apostles on the Calendar**~~ — **SEALED 2026-07-29: all twelve
  wedges + the center.** Peter 12–14h, James the Greater 14–16h, John
  16–18h, Philip 18–20h, Bartholomew 20–22h, Judas Iscariot 22–24h
  (his wedge ENDS at midnight), Simon the Zealot 00–02h, Thomas
  02–04h, Matthew 04–06h, James of Alphaeus 06–08h, Thaddaeus 08–10h,
  Andrew 10–12h; **center JESUS, always present**. CANON §The
  Apostles. The roster can mount.
- ~~**Virtue Wheel** crown/root seating~~ — **SEALED 2026-07-29,
  RE-SEATED.** Magnanimity·Vanity crowns at 12h (Aristotle's own
  *"crown of the virtues"*); Just Indignation·Envy roots at 24h;
  Courage moved to 16h in cross-resonance with the Emotions Dozen. The
  old Courage-crown proposal AND the paint-inverted-through-the-center
  reading are both DEAD — virtue and vice now share ONE seat. Center:
  **Prudence** (light) · **Cunning** (paint), always present. Full
  table, the six axes and their meanings in CANON §The Virtue Wheel.
- ~~**The Sins Dozen** seating and center~~ — **SEALED 2026-07-29.**
  The fifth Dozen, System B: **Pride crowns at 12h** (Gregory's root
  returns to the rim and Vainglory FOLDS INTO IT — one seat, the
  stronger word), **Treachery roots at 24h** (Judas in Satan's mouth,
  the same midnight the Apostles Dozen already gives him), and the 16h
  call delegated to the orchestrator ruled **Violence** (Dante's
  seventh circle; Cruelty weighed and set aside). Center:
  **HARDNESS OF HEART**, always present — the ANTI-PEACE, with
  Blasphemy against the Spirit ABSORBED rather than rejected (Mark 3:5
  → 3:29 are one scene). Full table, the six axes and the CENTER-PAIR
  LAW in CANON §The Sins Dozen and §The Axle; sheet
  `research/prompts/calendars/sins_prompts.md`; mounted and tested.
- ~~**sw_dyad's Ninth mechanism** (Ghosts/Exegol)~~ — **RESOLVED
  2026-07-29: DAYLIGHT/NIGHT switch**, not the date rotation Session 33
  provisionally wired. Day shows The Ghosts, night Exegol
  (`constants.NINTH_MECHANISMS["sw_dyad"] == "daynight"`,
  `constants.WEEKDAY_THEME_NINTH_NIGHT`); `WEEKDAY_SEAT_ROSTERS
  ["sw_dyad"]["ninth"]` is deleted. Part of THE DOUBLE NINTH LAW, see
  [Config (folder)](../config/___config.md) and
  `tests/test_ninth_mechanisms.py`.
- ~~**cp_corpo's Throne/Mirror/Ninth mechanism**~~ — **RESOLVED
  2026-07-29: THE WEEKLY MANDATE.** The ISO calendar week's PARITY,
  not the daily ordinal, decides the ruling triple — even week
  Arasaka, odd week NUSA — for Throne, Mirror AND Ninth together
  (`constants.NINTH_MECHANISMS["cp_corpo"] == "term_weekly"`,
  `config.defaults._pick_weekly_mandate`). `cp_gangs`/`cp_street` stay
  on the plain daily rotation. Pinned by
  `tests/test_weekday_rotation.py` and `tests/test_ninth_mechanisms.py`.
- **A 24-set for the Calendar** — no 24 (+3 center) roster is
  canon-sealed to ride it; the two-per-wedge law is implemented and
  tested, registering one is a single table row once sealed (Rose-24's
  three-figure center render would be new work).
- **`render/layers.py` split** — grown to ~3,700 lines (Rule #20): a
  dedicated refactor session (`render/pointer_shapes.py`) proposed.
- Seven archetypes stay seven (the standing recommendation) or grow
  to thirteen — 13 is the excluded number in this system.
- Odanost as the center's day face, or on a planet seat.
- ~~The Calendar naming~~ — SEALED: pointer **Calendar**, wheels
  **Zodiac/Almanac** in the wheel slot; no wedge medallions,
  pinned 1/2/3 slots, opacity lighting, both lighting modes
  user-selectable.
- The Academy tagline wording (CUBE.md §The Name — *"Watch the
  hours. Watch and learn. Keep the watch."* is PROPOSED).
- ~~GitHub repo rename?~~ — RESOLVED: the owner renamed the GitHub
  repo himself to **`UVuruna/Watch-Academy`** (found 2026-07-28 — a
  Session 23 `git push` to the old `UVuruna/DOMY-Watch` remote came
  back "This repository moved. Please use the new location:
  `https://github.com/UVuruna/Watch-Academy.git`"; GitHub's redirect
  still accepts the old URL, but the canonical one is the new name).
  Session 22 correctly did NOT execute this itself (root CLAUDE.md
  forbids self-granted outward-facing repo actions) — the owner made
  the call independently. **The follow-ups are CLOSED (owner order
  2026-07-28, Session 24):** the local `origin` now points at
  `https://github.com/UVuruna/Watch-Academy.git` (verified with
  `git ls-remote`, so the push no longer travels through GitHub's
  redirect), and `ROADMAP.md`'s M7 `update.repo` reads
  `"UVuruna/Watch-Academy"`. `setup/app_info.json` never carried a
  repo field at all — the seed holds name/description/exe/installer
  only — so nothing was wrong there to fix; the `update` section is
  created by the module that reads it, at M7. The one deliberately
  UNCHANGED item is the disk folder name: "DOMY Watch" stays (CUBE.md's
  scope note allows it — a separate call from the GitHub identity). No
  LIVE address carries the old name any more — it survives only in
  these historical notes, which say so explicitly.
- ~~The Character wheel's OPEN combo figures~~ — SEALED 2026-07-27 by
  Session 21 under the owner's delegation ("ti pečatiš"): Alfred
  Pennyworth / Severus Snape (Devotion), Charles Xavier (Patronage),
  Steve Rogers (Conviction), Father Ferapont and Silas (Mortification).
  The whole combo table in CUBE.md is sealed; no (P) marks remain.
