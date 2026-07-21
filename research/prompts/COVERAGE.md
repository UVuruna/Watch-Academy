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
- [Subdial Plates](#subdial-masters)
- [Slavic Months & Badge 1:1 (ART-INFRA round)](#art-infra-round)
- [Greek Monsters, Chinese Mythology & Theme Title Plates (PROMPT SHEETS round)](#prompt-sheets-round)
- [WoW, Cyberpunk, Star Wars & The Corporation (GAMING + CORPORATION SHEET WAVE, R10)](#gaming-corp-wave)
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
masters, the Calendar-pointer 12-set (`months/`), the BADGE SISTEM
1:1 circles (`badge/circle/`), and the owner's own hand-built
collections (ring letters, icons, guide).

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

**Prompt sheet: EXISTS and is COMPLETE — 18 entries, not 6.** The
prior revision of this document only knew about the original 6 (2
Ages + 4 Starry Seasons); `research/prompts/era/era_prompts.md` grew a
7th entry (`Anno_Lucis.png`) and a `calendar/` sub-collection of 6 more
(`AUC`, `Byzantine`, `Hebrew`, `Hegirae`, `Buddhist`, `Huangdi`) in its
own "fix-round B, TASK 3" — confirmed wired in
`app/encyclopedia.py`'s `_ERA_ENTRIES`/`_ERA_CALENDAR_ART` and
dry-run-verified clean (13 images, 0 problems, per the sheet's own
Status section). The MAYA round (owner 2026-07-20) added a 7th
calendar emblem, `Maya.png`, to the same `calendar/` sub-collection —
14 entries total. The ERA-TRIO round (owner 2026-07-20, "može sve 3")
added three more calendar emblems (`KaliYuga.png`, `Olympiad.png`,
`Unix.png`) plus ONE rotation ALT (`calendar/alt/Byzantine.png`, the
owner's own second Byzantine take) — 18 entries total; the sheet's own
Status section still needs its own fresh dry-run pass on the new
entries. The SAME round also fixed a WIRING gap this table's prior
revision missed: the calendar strip's own consumer
(`app/encyclopedia.py` `_era_image`) used to bypass
`rotating_art_file` entirely, a straight non-rotating lookup — now
every calendar emblem rotates against its own `alt/`/`_v2` siblings
like every other era plate, so the Byzantine v2 emblem is actually
discoverable once both files land.

| Collection | Expected by code | On disk | Sheet entry | Verdict |
|---|---|---|---|---|
| `era/*` — 2 Ages + 4 Starry Seasons | Age_of_Light, Age_of_Darkness, Starry_{Spring,Summer,Autumn,Winter} | 0/6 | `era_prompts.md` ✔ | ART GAP — full generation pending, wired + graceful-absent on the Encyclopedia's ERA topic |
| `era/Anno_Lucis.png` | 1 file | 0/1 | `era_prompts.md` ✔ (§Anno Lucis) | ART GAP + WIRING GAP — no code references `assets/era/Anno_Lucis.png` at all today; the Anno Lucis year is TEXT-ONLY in the hover legend (`core.deep_time.format_anno_lucis`) — generating the art alone would not yet make it appear anywhere |
| `era/calendar/*` — 10 calendar-system emblems | AUC, Byzantine, Hebrew, Hegirae, Buddhist, Huangdi, Maya, Kali Yuga, Olympiad, Unix | 0/10 | `era_prompts.md` ✔ (§The Eras of the World's own calendars) | ART GAP — wired (`app/encyclopedia.py` `_ERA_CALENDAR_ART`, strings as the "Eras of the World" essay's image strip), graceful-absent, NOW ALSO ROTATING (ERA-TRIO round) |
| `era/calendar/alt/Byzantine.png` — the Byzantine v2 rotation ALT | 1 file | 0/1 | `era_prompts.md` ✔ (§The Eras of the World's own calendars, "Byzantine Anno Mundi — v2") | ART GAP — a genuinely new design (tetragrammatic cross, four firesteels), not a regeneration of the canonical prompt; discovered automatically by `rotating_art_file` once both this file AND the canonical `Byzantine.png` exist, no separate code entry needed (THE UNIVERSAL ROTATION CONVENTION) |

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

## Subdial Plates (`assets/subdial/`, formerly `SUBDIAL_ART_DIR`)

**SUPERSEDED TWICE (RULE-19 round 2026-07-20, then Rsub round
2026-07-21 — owner decree, monorepo root `CLAUDE.md`).** Everything
below this line described the twelve-combination sheet (4 seat/light
variants × 3 finishes) as an ART GAP to fill — that framing was the
failure Rule #19 exists to end: the seat never needed its own file
(the shadow is one line of circle math, `render.layers.
_draw_subdial_shadow`), and the finish never needed its own file
either for the ONE-MASTER-PER-SOURCE model that followed
(`_recolored_plate` derived gold/silver/bronze live). The sheet was
run to completion anyway before the owner caught it (12/12 Gemini,
9/12 ChatGPT) and the resulting 20 extra files were deleted the same
round. The one-master model itself is NOW ALSO retired (Rsub round,
2026-07-21): the plate is no longer an art-SOURCE family at all — five
hand-picked sets live under `assets/subdial/<set>/<finish>.png`
(`<set>` = set1..set4, `<finish>` = gold/silver/bronze) plus
`assets/subdial/solo/<finish>.png` (only silver hand-drawn, gold/
bronze still algorithmic) — see
[Subdial Prompts](instrument/subdial_circle_prompts.md) for the full
story and the derivation-check paragraph Rule #19 requires. This row
is CLOSED, not a gap.

<a id="art-infra-round"></a>

## Slavic Months & Badge 1:1 (ART-INFRA round, owner 2026-07-20/21)

Two NEW sheets this round, both **0 generated, sheet complete** —
tracked here the moment they're written, per this file's own charter
("read it before writing a sheet, not after").

- **Slavic Months** — [Months Prompts](months/months_prompts.md).
  Twelve ROUND rose-window medallions, `assets/months/<stem>.png`
  (the SAME sourceless-root precedent as the subdial sets — see
  `assets/___assets.md`), registered in `config.defaults.
  SLAVIC_MONTHS` (R7b, 2026-07-21) and the `months` Encyclopedia topic
  since BEFORE this round; this round supplied the missing ARTWORK
  sheet. **Art: 0/12.** The render of the mounted marks on the
  Calendar pointer is a separate, future round (unchanged scope note,
  carried from `config/defaults.py`'s own SLAVIC_MONTHS comment).
- **Badge 1:1, round one** —
  [Badge 1:1 Prompts](badge/badge_1to1_prompts.md). 38 ROUND circular
  companions for every 2:1 LANCET figure across the seven archetype
  families (Trinity, Family, Temperaments, Persons, One Soul, Walks,
  Life-Tree — the five CENTER rosettes and the already-round
  Tetramorph/Evangelist rondels correctly excluded, they need no
  companion). Drop root `assets/badge/circle/<family>/<Stem>.png`, a
  NEW staging area deliberately outside `assets/archetype/` since the
  hover-card left-column WIRING is undecided (owner call — DO NOT
  invent it). **Art: 0/38.** The Animals register's own 8 Life badges
  (compass_light's non-default alternate) are explicitly scoped OUT of
  round one — a straightforward round-two follow-up if the owner
  activates that register.
- Both sheets pass `tests/test_prompt_paths.py`'s lint: Months via the
  `_DATA_DRIVEN_ROOTS` list (its per-name paths are enumerated in
  `SLAVIC_MONTHS` but built through an f-string inside `app.
  encyclopedia._topics`, invisible to the lint's static scan, exactly
  like weekday/zodiac already are); Badge 1:1 needed exactly ONE
  explicit whitelist entry (`badge/circle/life/tree/Unborn.png`,
  standing for the whole Life-Tree octet) — the other 30 paths are
  already accepted by the lint's own basename-suffix leniency, since
  their filenames coincide with the SOURCE lancets' literal
  `"Stem.png"` strings in `config/archetypes.py` (documented in the
  whitelist's own comment, not a gap).

<a id="prompt-sheets-round"></a>

## Greek Monsters, Chinese Mythology & Theme Title Plates (PROMPT SHEETS round, owner 2026-07-21)

Three NEW sheets this round, all **0 generated, sheets complete** —
tracked here the moment they're written, per this file's own charter.

- **Greek Monsters** —
  [Greek Monsters Prompts](monsters/greek_monsters_prompts.md). A NEW
  weekday theme (single roster, no Pantheon split): six weekday
  bestiary seats, a Sunday dual (Nemean Lion / Cerberus — literal
  brothers, children of Typhon and Echidna), an Excluded Ninth
  (Pegasus), and a title plate (Typhon & Echidna, tracked in the titles
  sheet below). Night-window stained-glass register wearing the
  Olympian family's own Greek-key border, recut as dark leadwork
  instead of bronze relief — "the greek-key border family the god
  medallions already wear but in a darker bestiary register" (owner).
  Drop root `assets/weekday/monsters/{primary,colored}/<Stem>.png`.
  **Art: 0/18** (9 figures × 2 registers). Theme NOT yet registered in
  `config/defaults.py` — sheet-writing only, per this round's own
  scope ("Sheets ONLY... NO app code"); `assets/weekday/**` is a
  data-driven lint root so every path here already passes
  `tests/test_prompt_paths.py` with zero whitelist entries needed.
- **Chinese Mythology** —
  [Chinese Myth Prompts](chinese/chinese_myth_prompts.md). A NEW
  weekday theme, same single-roster shape, NOT to be confused with the
  existing `chinese` zodiac-animal theme
  (`zodiac/chinese_zodiac_prompts.md`). **SEALED v2 (owner 2026-07-21,
  "Bravo, sve mi se sviđa" — the Black Myth: Wukong reading), replacing
  this round's own first cut:** six weekday immortal seats (Guan Yu
  moved Tuesday → Wednesday as the merchant's own patron, Caishen loses
  the seat and guests in Guan Yu's scene instead, Erlang Shen — the
  general who fought Wukong to a standstill — takes Tuesday), a Sunday
  dual (Sun Wukong crowned Ruler, Pride itself, against his own perfect
  false double the Six-Eared Macaque as Servant — the canonical
  tell-them-apart episode the Black Myth finale is built from), an
  Excluded Ninth (Buddha — not the dual's victim but its master: the
  one being who told the true monkey from the false, and the one being
  who EXTINGUISHED the Ninth seat's own sin, Wish, rather than suffered
  it), and a title plate (The Peach Banquet — the sheet's own justified
  pick over "the celestial court panorama," now rhyming directly with
  the Ruler's own Pride: the banquet is the myth-beat that MADE the
  self-taken title). Night-window register wearing its OWN cloud-scroll
  (xiangyun) border in a jade-and-lacquer palette — deliberately NOT
  the Greek key, per the owner's own instruction. Drop root
  `assets/weekday/chinese_myth/{primary,colored}/<Stem>.png`. **Art:
  0/18** (slot count unchanged by the v2 reseat — one figure traded per
  seat, none added). Same data-driven-root, zero-whitelist-needed
  status as Greek Monsters.
- **Theme Title Plates** —
  [Theme Title Prompts](titles/theme_title_prompts.md). Fills the
  documented graceful-absent `title_entry["images"]` slot every weekday
  theme (and two sibling topics, Intelligences and Slavic Months)
  already carries in `app.encyclopedia._weekday_topic` — 24 briefs plus
  2 more (Greek Monsters' Typhon & Echidna, Chinese Mythology's The
  Peach Banquet) NAMED by their own theme sheets but written IN FULL
  here, the canonical root every title plate lives in. **Gap closed
  2026-07-22:** those 2 were cross-referenced since R8c but carried no
  fenced generatable prompt body anywhere until this round (the R10
  report caught it live) — both are now written in full in this sheet.
  NEW canonical sourceless root, `assets/titles/<key>.png` — the SAME
  "NOT art-sourced, one shared file per name" precedent `assets/
  months/` and `assets/subdial/` already set, chosen over per-theme
  folders because a title plate has exactly ONE consumer regardless of
  the theme's own cast register (see the sheet's own "canonical drop
  path" section for the full reasoning). Continents is deliberately
  EXCLUDED — it already has a real, wired title image
  (`assets/earth/world.png`, `defaults.CONTINENTS_TITLE_IMAGE`), the
  owner's own SKIP instruction. **Art: 0/26** in this sheet now (24
  original + the 2 gap-closed entries). This is also the ONE documented
  exception to the
  project's house "no lettering" rule — each plate carries a single
  wordmark (the theme's English display name) in a script matching
  that theme's own culture (owner item 7), the typographic direction
  named explicitly per theme in the sheet's own table.
- All three sheets are dry-run-verified clean (`python main.py
  "<sheet>" --dry-run` from `Gadgets/PromptPainter/`: 18/18, 18/18 and
  26/26 entries load, 0 problems — re-verified 2026-07-22 after the gap
  closed). The Theme Title Plates' 26 paths (all now written IN this
  one file, none cross-referenced any more) are NOT under any existing
  data-driven root and nothing reads `assets/titles/**` yet — all 26
  needed explicit `tests/test_prompt_paths.py` whitelist entries, added
  this round with a shared comment block explaining the new family.

<a id="gaming-corp-wave"></a>

## WoW, Cyberpunk, Star Wars & The Corporation (GAMING + CORPORATION SHEET WAVE, R10, owner-sealed rosters 2026-07-22)

Four NEW sheets this round (Star Wars sealed as a mid-round addendum),
all **0 generated, sheets complete** — tracked here the moment they're
written, per this file's own charter. All four generalize the existing
Planetary/Pantheon "Two Rosters" doctrine (`CANON.md`) from two casts
to THREE parallel casts riding the same nine seats (Corporation is the
one exception — a single roster, same shape as Greek Monsters/Chinese
Mythology).

**PRIMARY REGISTER CORRECTED 2026-07-22:** the first generation pass
(WoW Alliance: Anduin, Khadgar, Muradin at least) surfaced near-
duplicate primary/colored pairs across all four sheets below — each
sheet's own `primary` briefs had drifted into prescribing the SAME
color palette as `colored` (WoW's own border table below, the
"blue-gold lion / red-black wolf / saronite-ice fang" line, describes
what was actually a PRIMARY-register bug). Every primary brief in all
four sheets has been rewritten to the project's monochrome
aged-bronze-relief law (`greek_prompts.md`'s own planetary bronze
plates) — one metal, no other colors, the per-figure identity carried
by the carved MOTIF alone (lions/fangs/saronite-spikes/circuit-traces/
aurebesh-flavor/org-chart-lines). `colored` was already correct and
needed no changes. The register lines below are updated to describe
the CORRECTED split, not the original bug.

- **WoW** — [WoW Prompts](wow/wow_prompts.md). THREE blocks (Alliance /
  Horde / Evil), each a full nine-seat roster (six weekday heroes, a
  Throne/Mirror dual, an Unfound Ninth): Alliance (Anduin … Malfurion,
  Varian Wrynn/Genn Greymane/Turalyon), Horde (Baine … Cairne, Thrall/
  Garrosh/Rexxar), Evil (Kel'Thuzad … Deathwing, Arthas the Lich King
  seated on the Frozen Throne/Illidan/Medivh). `primary` is aged-bronze
  relief (the recolor master), the carved border MOTIF (rampant-lion /
  wolf-fang totem / saronite-and-ice fang) the only per-block
  identifier; `colored` keeps each block's own paint (blue-gold /
  red-black / saronite-ice). No rotation seats. Drop root
  `assets/weekday/wow/<block>/{primary,colored}/<Stem>.png`.
  **Art: 0/54** (27 figures × 2 registers; 3 title plates tracked in
  `titles/theme_title_prompts.md`). Dry-run: 54/54, 0 problems.
- **Cyberpunk 2077** — [Cyberpunk Prompts](cyberpunk/cyberpunk_prompts.md).
  THREE blocks (Gangs / Street / Power), same nine-seat shape. Gangs
  and Street carry ROTATION SEATS — more than one named faction/figure
  sharing a day, via a NEW file convention this round establishes: the
  alt/alt2 sibling's file is named after the SEAT's own canonical stem
  (never the alt figure's own name), pooled by `config.defaults.
  rotating_art_file`'s existing `<Stem>`/`<Stem>_v*` search across the
  canonical directory UNION its `alt/` subfolder — a 3-way rotation
  (Tuesday Gangs: Maelstrom canonical, Barghest in `alt/`, Wraiths as
  `Maelstrom_v2.png`) uses both legal forms at once. Power's trio
  (Saburo Arasaka/Rosalind Myers, Yorinobu/Kurt Hansen, Alt Cunningham/
  Rache Bartmoss) carries a SYNCHRONIZED PAIR ROTATION — not new code,
  just every pole owning exactly 2 candidates so `_pick_rotation`'s
  shared date-ordinal-modulo naturally lands all three on the same
  index, the identical mechanism `scale_variant_file` already uses to
  keep Judas/Lucifer in step. `primary` is aged-bronze relief, the
  circuit-trace (PCB) border motif carved into the same bronze,
  constant across blocks; `colored` is the full-saturated neon-noir
  poster, gang-canonical neon colors per figure. Drop root
  `assets/weekday/cyberpunk/<block>/{primary,colored}/<Stem>.png`.
  **Art: 0/78** (Gangs 28 + Street 26 + Power 24; 3 title plates
  tracked separately). Dry-run: 78/78, 0 problems.
- **Star Wars** — [Star Wars Prompts](starwars/starwars_prompts.md).
  Sealed as a mid-round addendum. THREE sets: Svetla/light (Obi-Wan …
  Chewbacca, Young Luke/The Father-Vader/Yoda — the Mirror brief
  literally overlays Vader's mask across Luke's own face, the reveal
  moment), Tamna/dark (Tarkin … Boba Fett, Palpatine/Anakin-as-servant/
  Darth Plagueis), Nova/the dyad — the ONLY mixed set, because its own
  Ninth is dual: The Ghosts (default) vs. Exegol (rarer face), a PLACE-
  vs-PLACE rotation modeled explicitly on `core/continents.md`'s own
  Zealandia/Pangea precedent (default continent vs. the rarer
  eclipse/turning-point face) rather than a person-vs-person swap.
  Anakin/Vader, Leia and Han each appear TWICE across sets (different
  ages/roles — Svetla's Leia the general vs. Nova's "Old Leia" the
  master, etc.) — six of the sheet's 60 briefs are these legitimate
  repeats, never a duplicate scene. `primary` is aged-bronze relief,
  the aurebesh-flavored tick ornament (letterform-flavor only, same
  documented compromise as `egypt`/`norse`'s title-plate scripts —
  never a genuine readable alphabet, and not even that flavor on
  regular cast plates, which carry zero lettering) carved into the
  same bronze; `colored` is the full-color paint version. Drop root
  `assets/weekday/starwars/<set>/{primary,colored}/<Stem>.png`.
  **Art: 0/60** (30 figures × 2 registers; 3 title plates tracked
  separately). Dry-run: 60/60, 0 problems.
- **The Corporation** — [Corporate Prompts](corporate/corporate_prompts.md).
  Single roster, same closed-set shape as Greek Monsters/Chinese
  Mythology: six executive seats (CHRO … CTO), a Throne/Mirror dual
  (CEO / Chairman of the Board), an Unfound Ninth (The Founder — "the
  ghost seat every company has"). Every one of the 9 figures is an
  explicit ARCHETYPE — "FACELESS OR STYLIZED... no likeness of any real
  person" is written into all 18 individual prompts, not just the
  sheet header, since these are corporate ROLES rather than named
  individuals. `primary` is aged-bronze relief, the org-chart
  line-and-node border motif carved into the same bronze; `colored`
  is the clean annual-report paint version (steel and gold accents).
  No rotation seats. Drop root
  `assets/weekday/corporate/{primary,colored}/<Stem>.png`. **Art:
  0/18** (9 figures × 2 registers; 1 title plate tracked separately).
  Dry-run: 18/18, 0 problems.
- **Ten new title plates** — filed into the existing
  [Theme Title Prompts](titles/theme_title_prompts.md) family (three
  per block/set theme, one for Corporation): `wow_alliance`,
  `wow_horde`, `wow_evil`, `cyberpunk_gangs`, `cyberpunk_street`,
  `cyberpunk_power` (Soulkiller — the FORCE, not a person, the same
  "parent, not seat-holder" device as `wow_evil`'s Sargeras), `
  starwars_svetla`, `starwars_tamna` (Darth Bane, the Rule of Two's own
  doctrinal parent — deliberately NOT Plagueis, already this set's own
  Unfound), `starwars_nova` (The Dyad — two hands reaching across a
  broken lightsaber, the owner's own suggested image) and `corporate`
  (The Boardroom Table — eight marked chairs, one conspicuously bare).
  Same as the monsters/chinese pair (gap closed 2026-07-22, see
  above), all ten are written with FULL prompt bodies directly in
  `titles/theme_title_prompts.md` itself (its own stated intent for
  the family), so each new theme sheet carries only a short pointer,
  never a duplicate. **Art: 0/10.** Dry-run (whole title-plates file):
  36/36, 0 problems.
- All four theme sheets are data-driven (`assets/weekday/**`), so every
  path they declare — including every `alt/`- and `_v*`-suffixed
  rotation sibling — passes `tests/test_prompt_paths.py` with ZERO
  whitelist entries needed. The ten new title-plate paths are NOT
  data-driven (same as the existing 26) and each needed its own
  explicit whitelist entry, added this round in the same comment block
  as the PROMPT SHEETS round's nine.
- None of the four themes are registered in `config/defaults.py` yet
  (`WEEKDAY_THEME_NAMES` etc.) — sheet-writing only, per this round's
  own scope ("Sheets ONLY... NO app code"). The Cyberpunk rotation
  seats and the Star Wars place-dual Ninth additionally need
  `rotating_art_file` (or, for Ghosts/Exegol, possibly a reuse of
  `core.continents`'s own trigger logic) wired to their seats — also
  future work, documented in each sheet's own Status section.

<a id="other"></a>

## Ring Letters, Icons, Guide — out of the AI-prompt pipeline

Unchanged, re-confirmed 2026-07-19:

- **Ring letters** (`assets/ring/letters/*.png` — 38 files — plus
  `domy.png`, `hexagram.png`, `morph.png` at the ring root) — the
  owner's own hand-built glyph library, not AI-prompted; no sheet
  needed, none found, not a gap.
- **Icons** (`assets/icons/` — ON DISK now, 14 files: light.png,
  dark.svg, eclipse_sun.svg, eclipse_moon.png, compass.png,
  north_pole.png, south_pole.png, plus the ART-INFRA round's per-type
  eclipse set — moon_eclipse_red/gold/blue.png and sun_eclipse.png/
  1.png/2.png) — its own self-contained, owner-facing sheet already
  exists: `icons/ICONS_SPISAK.md` (Serbian by explicit owner
  exception). Not a missing-prompt gap; the per-type mapping/wiring
  itself is `config/___config.md`'s ECLIPSE TYPE ICONS note, not an
  AI-prompt gap either (no new icon files needed — the mapping picks
  among files already on disk, one computationally tinted).
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
   eclipse (7), the archetype gaps in the table above (Throne, Seal,
   Lucifer_Pride, Judas_Fear, the 8 evangelist files, the 1 one-sided
   Devil_Prosecutor), plus the ART-INFRA round's two NEW sheets —
   Slavic Months (12) and Badge 1:1 round one (38) — plus the PROMPT
   SHEETS round's three NEW sheets: Greek Monsters (18), Chinese
   Mythology (18) and Theme Title Plates (26, all written directly in
   the one sheet as of the 2026-07-22 gap closure) — plus the GAMING + CORPORATION
   SHEET WAVE's (R10) four NEW sheets: WoW (54), Cyberpunk (78), Star
   Wars (60) and The Corporation (18), plus their own 10 new title
   plates (written directly in `titles/theme_title_prompts.md`, see
   above). Subdial is CLOSED (RULE-19 round, 2026-07-20) — see the
   superseded note above, no more generation needed there.
1a. **Two wiring rounds** the PROMPT SHEETS round explicitly left for
   later (out of THIS round's "sheets only, no app code" scope):
   registering `monsters`/`chinese_myth` in `config/defaults.py`'s
   weekday-theme tables, and filling every theme's
   `title_entry["images"]` tuple with its new `assets/titles/<key>.png`
   plate, mirroring `defaults.CONTINENTS_TITLE_IMAGE`.
1b. **The same two wiring rounds, generalized to the four R10 themes**:
   registering `wow`/`cyberpunk`/`starwars`/`corporate` in
   `config/defaults.py`'s weekday-theme tables (same tables as 1a), and
   filling their own `title_entry["images"]` tuples once their title
   plates land. PLUS two rotation-specific wiring items unique to this
   round: calling `rotating_art_file` on the Cyberpunk Gangs/Street
   rotation seats and the Star Wars Nova Ghosts/Exegol seat (the latter
   possibly reusing `core.continents`'s own Zealandia/Pangea trigger
   logic rather than a plain date-rotation — owner call, documented in
   `starwars_prompts.md`'s own "rotation convention" section, not
   assumed here).
2. **Three wiring decisions**, not art gaps — the row2 rondels
   (Trinity/Family/Walks, 40 files sitting painted and unread), Anno
   Lucis (1 file, once generated, has nowhere to draw yet), and the
   Badge 1:1 hover-card left-column layout (38 files, once generated —
   owner call, DO NOT invent it).
3. **Roster's own shortage list** (196 ChatGPT + 24 Gemini, weekday/
   zodiac territory) — tracked in [Roster](../../ROSTER.md), sheets
   already exist per theme, not repeated here.

No 1×1 placeholder exists anywhere under `assets/` as of this round
(full sweep, 1,105 image files, zero hits) — every "MISSING" verdict
above is an honest, genuinely-absent file, not a stand-in wearing a
checkmark.
