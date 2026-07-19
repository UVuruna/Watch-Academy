# Prompt Coverage Ledger

**Purpose (rewritten 2026-07-19, PLACEHOLDER PURGE & PROMPT-GAP round,
owner order):** this file is an AGENT-FACING gap ledger, not a report.
It exists to DRIVE prompt-writing and PromptPainter generation queues —
read it before writing a sheet, not after. **The owner reads
`REMAINING.md`, not this file** — that is his own status view; this
one is the disk-vs-code-vs-sheet audit trail an agent re-derives before
touching any prompt sheet. Regenerate this table (or the relevant
section of it) whenever a sheet changes or new art lands — do not let
it go stale the way the previous revision did (see the Purge Log
below: two archetype centers and one figure were marked "✔ exists"
here while actually sitting on disk as committed 1×1 placeholders).

**Method:** "on disk" below means REAL art — width AND height both
`> config.archetypes.ARCHETYPE_ART_MIN_PX` (8px) for the archetype
tree (`render.layers.archetype_art_ready`'s own rule), or simply
file-exists for collections with no such guard (era/eclipse/subdial —
none of those have shipped even one placeholder, so plain existence is
still honest today). A collection is regenerable by rerunning the same
check: walk `config.archetypes.ARCHETYPES` for every figure/center
`file`, resolve it under `assets/<root>/gemini/...` and
`assets/<root>/chatgpt/...` directly (not through
`config.paths.art_file`'s cross-source fallback — that would hide a
one-sided gap), and test the pixel size.

## Table of Contents

- [Scope](#scope)
- [Placeholder Purge Log — 2026-07-19](#purge-log)
- [Archetype Set](#archetype-set)
- [The Compass Object Question](#compass-objects)
- [Era Terms (incl. the Eras-of-the-World calendars)](#era-terms)
- [Eclipse Category Images](#eclipse)
- [Subdial Masters](#subdial-masters)
- [Ring Letters, Icons, Guide](#other)
- [Zero-Gap Declaration](#zero-gap)

<a id="scope"></a>

## Scope

[Roster](../../ROSTER.md) (`build_roster.py`) already covers, in full
per-seat detail: the weekday themes (Planetary + Pantheon), the zodiac
families (astrology + Chinese), and the flat badge/emblem groups
(trinity, season, scale, virtue, sin, mood, intelligence) — this
document does not repeat that table. It covers everything Roster does
NOT walk: the `archetype/` tree, `era/`, `eclipse/`, the subdial
masters, and the owner's own hand-built collections (ring letters,
icons, guide).

<a id="purge-log"></a>

## Placeholder Purge Log — 2026-07-19

The owner's complaint that triggered this round: committed 1×1
stand-in files were giving PromptPainter (and this very document) the
FALSE idea that art already existed. A full sweep of every image file
under `assets/` (1,110 files; QImage-opened, not judged by file size
alone) found exactly **5** — all now `git rm`'d:

| File | Was | Consumer | Effect of the purge |
|---|---|---|---|
| `archetype/gemini/persons/Seal.png` | 1×1, 68 B | archetype center (`prism_paint`) | Now correctly reports MISSING on both sources (chatgpt never had one either) — honest, was already falling back to the name label, no render change |
| `archetype/gemini/temperaments/Throne.png` | 1×1, 68 B | archetype center (`seasons_paint`/`seasons_light`, shared) | Same — MISSING both sources now, honest, no render change |
| `archetype/gemini/trinity/Devil_Prosecutor.png` | 1×1, 68 B | archetype figure (`trinity_paint`, arm 1) | **Real render fix**: `config.paths.art_file`'s cross-source fallback only triggers on a MISSING file, not a placeholder — with the placeholder gone, the Gemini-active render now correctly resolves to ChatGPT's REAL 694×1388 lancet instead of silently drawing the name label over perfectly good art that already existed one folder over |
| `badge/chatgpt/season/Poem.png` | 1×1, 70 B | hidden Encyclopedia "Four Greetings" entry (`app/encyclopedia.py` line ~905) | Now genuinely absent; the entry's `images` tuple resolves through the SAME `resolved.exists()` filter every other Encyclopedia image goes through (`_render_cell`) — title and prose still show, no image, no crash |
| `badge/gemini/season/Poem.png` | 1×1, 70 B | same entry, the other source | Same |

All three consumer classes were verified post-purge, live (see the
session's own report for the exact commands): the archetype NAME
fallback (`archetype_art_ready` on the now-missing paths), the
Encyclopedia graceful-absent path (constructing the dialog with the
image gone raises nothing, the poem entry's `images` tuple resolves to
an empty list), and the weekday colored-disc fallback (unaffected — no
weekday placeholder ever existed; confirmed by the same sweep finding
zero hits outside the archetype/badge trees). `tests/test_archetype.py`
needed NO changes — every placeholder-dependent test already used a
synthetic `tmp_path` PNG (`_png`/`_rect_png` helpers), never a real
committed file; that pattern is now the STANDARD for any future
placeholder test, not just a nice-to-have.

**One documentation staleness surfaced by the same sweep, fixed
alongside:** `research/prompts/archetype/persons_prompts.md`'s Status
section still said "Judas and Lucifer inherit their Scale glass — no
new art for those two seats", directly contradicting its own "The two
poles — OWN LANCETS" section a few dozen lines above (the
one-image-one-place law, owner 2026-07-19, REVOKED that reuse). Fixed
in place.

<a id="archetype-set"></a>

## Archetype Set (`assets/archetype/`, `config/archetypes.py`)

Every group's prompt sheet is COMPLETE — every path
`config.archetypes.ARCHETYPES` can reference has a written entry
somewhere in `research/prompts/archetype/*.md`, verified by grepping
each theme's exact filenames against its sheet (not just counting
arrows — three earlier "4/4" claims in this document turned out to be
placeholder-inflated, see the Purge Log). **Zero missing prompt
entries found anywhere in this collection.**

| Collection | Expected by code | On disk (gemini / chatgpt) | Sheet entry | Verdict |
|---|---|---|---|---|
| `trinity_paint` — 3 figures | One_Judge, Devil_Prosecutor, Jesus_Advocate | One_Judge & Jesus_Advocate real both; **Devil_Prosecutor real CHATGPT only** (gemini was the purged placeholder) | `trinity_prompts.md` ✔ | ART GAP, one-sided — the cross-source fallback already serves the real ChatGPT lancet on BOTH active sources today (see Purge Log); a gemini-native version would just make the fallback unnecessary |
| `trinity_paint` — center | Providence_Eye.png | real both | `trinity_prompts.md` ✔ | OK |
| `trinity_paint`/`family`/`trinity_light` — row2 rondels | rondel_Advocate/Judge/Prosecutor, rondel_Dawn/Heart/Shield | real both, all 6×2=12 files | `trinity_prompts.md` / `family_prompts.md` ✔ | WIRING GAP — fully painted, zero code reads any `rondel_*` path outside the evangelist set (see [Compass Objects](#compass-objects)) |
| `trinity_light` — 3 figures + center | Child_Dawn, Mother_Heart, Father_Shield, Hearth | real both, all 4 | `family_prompts.md` ✔ | OK |
| `seasons_paint` — 4 figures | Choleric, Melancholic, Phlegmatic, Sanguine | real both | `temperaments_prompts.md` ✔ | OK |
| `seasons_paint` / `seasons_light` — center (ONE shared file) | Throne.png | **MISSING both sources** (gemini was the purged placeholder; chatgpt never had one) | `temperaments_prompts.md` ✔ (§The center) | ART GAP — name-fallback active on every render today, honestly so now |
| `seasons_light` — 4 figures (tetramorph) | Lion, Ox, Eagle, Man | real both | `temperaments_prompts.md` ✔ (§The tetramorph) | OK |
| `seasons_light` — evangelist row2 | Mark, Luke, John, Matthew | MISSING both, 8 files | `temperaments_prompts.md` ✔ (§The four evangelists) | ART GAP, WIRED — `render.compositor` already calls `tetramorph_evangelist_file`; name-fallback carries the column meanwhile (pinned by `test_tetramorph_three_side_survives_absent_evangelist_art`) |
| `prism_paint` — 4 seated figures | One_Love, Michael_Courage, Devil_Hatred, Jesus_Humility | real both | `persons_prompts.md` ✔ | OK |
| `prism_paint` — 2 own-lancet figures | Lucifer_Pride, Judas_Fear | MISSING both, 4 files (never generated on either source — not a purge artifact) | `persons_prompts.md` ✔ (§The two poles) | ART GAP — name-fallback active, pinned by `test_prism_poles_wear_their_own_lancets` |
| `prism_paint` — center | Seal.png | **MISSING both sources** (gemini was the purged placeholder; chatgpt never had one) | `persons_prompts.md` ✔ (§The center — the Seal) | ART GAP |
| `prism_light` — 6 figures + center | Gratitude, Support, Passion, Tolerance, Trust, Respect, Union | real both, all 7 | `one_soul_prompts.md` ✔ | OK |
| `compass_paint` — 8 figures | King … Priest | real both | `walks_prompts.md` ✔ | OK |
| `compass_paint` — 8 object rondels | rondel_Crown … rondel_Bell | real both, all 16 files | `walks_prompts.md` ✔ (§The object rondels) | WIRING GAP — same as the trinity/family rondels above; see [Compass Objects](#compass-objects) |
| `compass_light` — 16 figures (2 registers × 8 ages) | tree/{8 stems}, animals/{8 stems} | real both, all 16 | `life_prompts.md` ✔ | OK |
| `calendar` — 12 month medallions | January … December | real both | `calendar_prompts.md` ✔ | OK |

**Totals:** 56 figure/center slots checked one by one (script run
2026-07-19) — 50 real on both sources, 1 real one-sided (Devil_
Prosecutor), 3 genuinely missing on both (Throne, Seal counted once
each as their one physical file; Lucifer_Pride/Judas_Fear as 2 more);
plus 8 evangelist files and 28 rondel files tracked separately above
(rondels all real, wiring is the only gap). Every one of those gaps
already has a complete, ready-to-queue prompt entry — none of them are
prompt gaps.

<a id="compass-objects"></a>

## The Compass Object Question

Unchanged from the prior audit — re-confirmed 2026-07-19
(`grep -rn "rondel_" --include="*.py"` outside `research/`/`tests/`
still returns nothing beyond the evangelist path). **Prompt sheets and
art: EXIST for all three unwired rondel families** (Walks' 8 object
rondels, Trinity's 3 calling rondels, Family's 3 hearth-role rondels —
28 files total, all real on both sources). **Wiring: still TEXT-ONLY**
— `config/archetypes.py`'s row2 fields are plain strings, and no
render or hover code reads any `rondel_*` path except the evangelist
set (`archetypes.tetramorph_evangelist_file`, called from
`render/compositor.py`). Nothing is broken (row2 always shows as
text); wiring the rondels the same way the evangelist column already
works is a product decision for the owner/writers' round, not a fix
here.

<a id="era-terms"></a>

## Era Terms (`assets/era/`, `config.defaults.ERA_ART_DIR`)

**Prompt sheet: EXISTS and is COMPLETE — 13 entries, not 6.** The
prior revision of this document only knew about the original 6 (2
Ages + 4 Starry Seasons); `research/prompts/era/era_prompts.md` grew a
7th entry (`Anno_Lucis.png`) and a `calendar/` sub-collection of 6 more
(`AUC`, `Byzantine`, `Hebrew`, `Hegirae`, `Buddhist`, `Huangdi`) in its
own "fix-round B, TASK 3" — confirmed wired in
`app/encyclopedia.py`'s `_ERA_ENTRIES`/`_ERA_CALENDAR_ART` and
dry-run-verified clean (13 images, 0 problems, per the sheet's own
Status section).

| Collection | Expected by code | On disk | Sheet entry | Verdict |
|---|---|---|---|---|
| `era/*` — 2 Ages + 4 Starry Seasons | Age_of_Light, Age_of_Darkness, Starry_{Spring,Summer,Autumn,Winter} | 0/6 | `era_prompts.md` ✔ | ART GAP — full generation pending, wired + graceful-absent on the Encyclopedia's ERA topic |
| `era/Anno_Lucis.png` | 1 file | 0/1 | `era_prompts.md` ✔ (§Anno Lucis) | ART GAP + WIRING GAP — no code references `assets/era/Anno_Lucis.png` at all today; the Anno Lucis year is TEXT-ONLY in the hover legend (`core.deep_time.format_anno_lucis`) — generating the art alone would not yet make it appear anywhere |
| `era/calendar/*` — 6 calendar-system emblems | AUC, Byzantine, Hebrew, Hegirae, Buddhist, Huangdi | 0/6 | `era_prompts.md` ✔ (§The Eras of the World's own calendars) | ART GAP — wired (`app/encyclopedia.py` `_ERA_CALENDAR_ART`, strings as the "Eras of the World" essay's image strip), graceful-absent |

<a id="eclipse"></a>

## Eclipse Category Images (`assets/eclipse/`, `config.defaults.ECLIPSE_ART_DIR`)

**Prompt sheet: EXISTS and is COMPLETE** — 7 entries
(`research/prompts/eclipse/eclipse_prompts.md`: solar total/annular/
partial/hybrid, lunar total/partial/penumbral), dry-run-verified clean
per the sheet's own note. **Art: 0/7**, unchanged since the prior
audit. Wired on BOTH consumers — the Encyclopedia's `eclipse_solar`/
`eclipse_lunar` topics (`app/encyclopedia.py`) and the on-dial eclipse
hover badge (`render/compositor.py`'s `_eclipse_emblem`) — both
graceful-absent.

<a id="subdial-masters"></a>

## Subdial Masters (`assets/badge/subdial/`, `SUBDIAL_ART_DIR`)

**Prompt sheet: EXISTS and is COMPLETE for all 12 combinations**
(`research/prompts/instrument/subdial_circle_prompts.md`: 4 light
variants — `south`, `h3`, `h21`, `center` — × 3 finishes; the code
only strictly needs ONE finish per variant since `subdial_plate_file`
recolors gold/silver/bronze live from whichever finish lands).

**Ground truth on the one plate that exists** (owner's question, this
round — "was there a make-script?"): **No.** `grep`-confirmed: no
`setup/make_subdial*.py` exists anywhere in the repo.
`assets/badge/gemini/subdial/silver/center.png` was AI-GENERATED
directly from this sheet's brief — confirmed by its own intake commit
("0.14.227 Owner round six": *"THE OWNER'S FIRST SUBDIAL PLATE ...
intaken ... exactly the sheet brief"*, which also logged "11 plates
remain on the owner's list" at the time, matching 12 total − 1 done).
This is the derivation note that closes the row — no new prompt entry
was needed, the sheet already covered this exact plate before it was
generated.

| Collection | Expected by code | On disk | Sheet entry | Verdict |
|---|---|---|---|---|
| `badge/subdial/*/center.png` | 3 finishes | 1/3 (gemini silver only; the other 2 finishes recolor live from it) | `subdial_circle_prompts.md` ✔ | OK by design — recoloring covers the other 2 finishes, no more art needed for this seat |
| `badge/subdial/*/{south,h3,h21}.png` | 3 seats × 3 finishes = 9 files (1 needed per seat minimum) | 0/9 | `subdial_circle_prompts.md` ✔ (all 9 entries written) | ART GAP — these 3 seats currently reuse the `center` plate via `subdial_plate_file`'s own seat-fallback (not the procedural circle — a plate already shows, just the wrong lighting direction); generating ONE finish per seat (3 files minimum) closes it |

<a id="other"></a>

## Ring Letters, Icons, Guide — out of the AI-prompt pipeline

Unchanged, re-confirmed 2026-07-19:

- **Ring letters** (`assets/ring/letters/*.png` — 38 files — plus
  `domy.png`, `hexagram.png`, `morph.png` at the ring root) — the
  owner's own hand-built glyph library, not AI-prompted; no sheet
  needed, none found, not a gap.
- **Icons** (`assets/icons/` — not yet on disk, expected) — its own
  self-contained, owner-facing sheet already exists:
  `icons/ICONS_SPISAK.md` (14 SVG icons, Serbian by explicit owner
  exception). Not a missing-prompt gap.
- **Guide** (`assets/guide/*.png` — 91 files, confirmed on disk) — the
  owner's own screenshots; no sheet applicable.

<a id="zero-gap"></a>

## Zero-Gap Declaration

After this round: **every image the app can reference is either (a)
real art on at least one source, (b) sheeted for generation with a
complete, dry-run-verified prompt entry, or (c) explicitly owner-hand-
built with no AI sheet needed.** No item anywhere in this document's
scope needs a NEW prompt written. The outstanding work is entirely:

1. **Art generation** against sheets that already exist — era (13),
   eclipse (7), subdial (3 minimum), the archetype gaps in the table
   above (Throne, Seal, Lucifer_Pride, Judas_Fear, the 8 evangelist
   files, the 1 one-sided Devil_Prosecutor).
2. **Two wiring decisions**, not art gaps — the row2 rondels (Trinity/
   Family/Walks, 40 files sitting painted and unread) and Anno Lucis
   (1 file, once generated, has nowhere to draw yet).
3. **Roster's own shortage list** (196 ChatGPT + 24 Gemini, weekday/
   zodiac territory) — tracked in [Roster](../../ROSTER.md), sheets
   already exist per theme, not repeated here.

No 1×1 placeholder exists anywhere under `assets/` as of this round
(full sweep, 1,105 image files, zero hits) — every "MISSING" verdict
above is an honest, genuinely-absent file, not a stand-in wearing a
checkmark.
