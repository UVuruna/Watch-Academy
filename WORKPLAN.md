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
`octa_paint`/`octa_light` variant paragraphs in
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
"cube" normalizes to "paint" on other pointers at ONE choke point,
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
(`constants.PRISM_LIGHT_THEME_NAME/_TITLE`); (6) THE CHARTER REWORK
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
`tests/test_app_info.py`; ROADMAP.md's M7 section records that
`update.repo` stays `"UVuruna/DOMY-Watch"` (repo NOT renamed) when
self-update eventually lands. The GitHub repo rename itself was
**not** executed (owner decree: `gh repo rename` never runs
automatically) — flagged as an open question below. 978 tests green.

### Session 23 — Rose Sabbath hover fix + the Duality-Axes config → **Sonnet**
**Say:** "Radi Sesiju 23 iz WORKPLAN.md — Rose hover bug i duality
config."
**Reads:** CUBE.md §The Rose (Sabbath axis, weekday law) and §The
Thirteen Axes (Colour Law, Sacred Axis, the Duality-Axes decree);
`render/compositor.md` (hover paths, hit-tests); `config/___config.md`;
the creeds duality's data seat.
**Delivers:** (1) THE BUG (owner screenshot 2026-07-28): on the Rose
the two Sunday faces DRAW on the Sabbath axis (Servant blue 06h,
Ruler red 18h) but their HOVER still fires at the legacy bottom
seat — reproduce with the GUI probe first, fix so hover hits the
drawn seats, pin with a regression test named after the failure
(root Rule 25). (2) THE DUALITY-AXES CONFIG (owner decree
2026-07-28, root Rule 4 — no hardcode): a config that, for EVERY
dual theme, places its two members on the vertical (yellow ↔
purple) and horizontal (blue ↔ red) axes; default: the PRIMARY
member pulls to the top; the horizontal is per-theme. First entry
and the proof case: **creeds flips — Christianity BLUE (christic,
cold), Satanism RED (diabolic, warm)** — today's assignment is
reversed. Consumed by the Rose, the Octa and Seasons(4). Tests pin
the config path and the creeds orientation.

### Session 24 — the Sacred rosters → **Opus** (writers) — UNBLOCKED (blanket seal 2026-07-28)
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

### Session 25 — the Thirteen-Axes texts + sheets → **Opus** (writers)
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

### Session 26 — the Seating geometry → **Opus**
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

### Session 27 — the Encyclopedia rework (celine) → **owner + another agent**
The owner drives this one himself with a separate agent: the Cube
canon now claims a large share of the Encyclopedia, so the whole
Encyclopedia UI splits into a few top-level WHOLES (celine) with
their themes inside. Recorded here so no session collides with it —
this plan only reserves the seat and defers the spec to the owner.

## Running in Parallel (no agent needed)

- **Owner art generation** from the sheets: pantheon plates,
  Satanism dual, Eleusis, the scale glass set (incl. the two
  Unions), Cat/Ophiuchus, season badges — and the archetype art
  once Session 4 lands. The wiring already degrades gracefully;
  every drop simply lights up.

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
  watch title) it is **One Soul**. `constants.PRISM_LIGHT_THEME_TITLE`
  / `PRISM_LIGHT_THEME_NAME`; record in `research/bond_theme.md`.
- Compass light image layer: ★ the Tree / the Menagerie (CANON).
- Seasons tetramorph persons layer: yes/no (CANON).
- Seven archetypes stay seven (the standing recommendation) or grow
  to thirteen — 13 is the excluded number in this system.
- Odanost as the center's day face, or on a planet seat.
- ~~The Calendar naming~~ — SEALED: pointer **Calendar**, wheels
  **Zodiac/Almanac** in the Paint/Light slot; no wedge medallions,
  pinned 1/2/3 slots, opacity lighting, both lighting modes
  user-selectable.
- The Academy tagline wording (CUBE.md §The Name — *"Watch the
  hours. Watch and learn. Keep the watch."* is PROPOSED).
- **GitHub repo rename?** (raised by Session 22, the Renaming): the
  repo is still `UVuruna/DOMY-Watch` and the disk folder is still
  "DOMY Watch" — CUBE.md's scope note allows the disk folder to stay
  regardless, but the repo name is a separate owner call. Session 22
  did NOT rename it (root CLAUDE.md forbids self-granted destructive/
  outward-facing repo actions without an explicit ask); a rename to
  something Watch-Academy-shaped is a live option if the owner wants
  the GitHub identity to match the sealed application name.
- ~~The Character wheel's OPEN combo figures~~ — SEALED 2026-07-27 by
  Session 21 under the owner's delegation ("ti pečatiš"): Alfred
  Pennyworth / Severus Snape (Devotion), Charles Xavier (Patronage),
  Steve Rogers (Conviction), Father Ferapont and Silas (Mortification).
  The whole combo table in CUBE.md is sealed; no (P) marks remain.
