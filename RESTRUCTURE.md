# RESTRUCTURE — The One-Hierarchy Refactor

**Owner-approved plan (sealed 2026-07-22).** One hierarchy everywhere:
the Encyclopedia halls, the Settings/Design panels and the `assets/`
folder tree all mirror ONE taxonomy defined in ONE config module.
Executed while PromptPainter is token-idle (~20h window from
2026-07-22).

This document is the single reference for the executing agent(s).
Rules it inherits: root CLAUDE.md Rules #3 (MD-first), #6 (no
backward-compat wrappers — update ALL callers), #19 (compute, don't
generate), #20 (no god-files); project CLAUDE.md (accuracy > speed,
English-only in files).

---

## Table of Contents

- [Approved Decisions](#decisions)
- [The Taxonomy](#taxonomy)
- [Naming Convention](#naming)
- [Rotation Rosters — figure-first](#rosters)
- [Folder Relocation Map](#relocation)
- [Theme Renames](#renames)
- [Execution Phases](#phases)
- [Verification Gates](#gates)
- [New Content Specs (Phase 3)](#new-content)

<a id="decisions"></a>

## Approved Decisions (owner, 2026-07-22 session)

1. **One taxonomy, one source of truth** — a new `config/taxonomy.py`
   defines categories → groups → themes → seats → rosters. The
   Encyclopedia, Settings panels, asset path resolution and the
   structure test all read it. Halls/groups are edited in ONE table.
2. **Source folders die** — no more `gemini/` / `chatgpt/` subtrees.
   Source becomes a terminal filename suffix: `_gem` / `_gpt`.
3. **File pattern:** `<Figure>[_vN]_<src>.png` — version (same-subject
   variant) before source; source ALWAYS last; no other suffixes.
4. **Rotation is figure-first** — the `alt/` directory convention and
   seat-named alt files (e.g. Mox saved as `alt/Aldecaldos.png`) are
   ABOLISHED. Every figure's file carries the figure's own name; a
   config roster per seat lists its rotating figures; the daily pick
   selects a FIGURE (image + display name + article together), never a
   bare file. `_vN` remains ONLY for multiple artworks of the SAME
   figure.
5. **Themes vs looks** — Planets/Planet signs/Planets Art are ONE
   theme with three looks. A "look" (art register) is a dimension of a
   theme, never a separate theme.
6. **Renames:** monsters → `age_of_heroes` ("Age of Heroes");
   chinese_myth → `celestial_court` ("Celestial Court"); Star Wars
   third block → `sw_dyad` ("Dyad"); religion → `creeds`,
   religion_alt → `ancient_religions` (display names already sealed
   2026-07-13); bible2 → `bible_ii` ("Bible II").
7. **Child — the Anchor:** the child's hearth-role becomes the Anchor
   (replacing the Dawn as role; the Dawn survives as the stacked
   time-reading). Canon meaning is DUAL: the anchor HOLDS the family
   gathered, and it sits at the BOTTOM — the bottom of the hierarchy,
   which is part of why the mother loves the child: someone to whom
   she can be dominant, someone who sees in her hierarchical
   superiority. (Owner text, 2026-07-22 — expand in CANON at Phase 3.)
8. **Four new Dozens approved** (Calendars category, Phase 3 content):
   Emotions (System B), Virtues+Vices as two registers of one wheel
   (System B), Olympians in six pairs (System A), Apostles in six
   pairs (System A). Layout logic in [New Content Specs](#new-content).
9. **Abstract trinities & dualities get art** (Phase 3): Past/Present/
   Future, thesis/antithesis/synthesis, Judge/Prosecutor/Advocate,
   Faith/Love/Hope, Good/Evil, I/Others.
10. **Prompt sheets follow the new structure** — every existing sheet's
    drop paths are rewritten to the new tree + suffix convention, so
    the next PromptPainter run generates straight into the new homes.

<a id="taxonomy"></a>

## The Taxonomy — five categories

```
1. calendars   — the Dozens (12 + 13th)
2. weeks       — every weekday theme (6+1 / 6+2 / 6+3 / 6+4 is a
                 per-theme property recorded in the roster, not a
                 grouping key)
3. archetypes  — the pointer archetypes (2/3/4/6/8; sixes carry a
                 center = "the seven", octas are 6+2 with the center
                 split into the plus/minus poles)
4. celestial   — sky mechanics: sun, moon, seasons, eclipses, eras,
                 earth faces
5. instrument  — dial furniture (outside the encyclopedia mirror):
                 hands, ring letters, icons, subdials, guide shots
```

### Category 2 groups (owner-approved, balanced)

| Group key | Display | Themes |
|---|---|---|
| `celestial_bodies` | Celestial bodies | planets (looks: canon/signs/art), cosmos, continents |
| `myth` | Mythologies | greek, norse, egypt, slavic, age_of_heroes, celestial_court |
| `faith` | Faith | bible, bible_ii, bible_dark, creeds, ancient_religions |
| `crafts` | Cultures & crafts | alchemy, japan, profession, corporate |
| `societies` | Animal societies | wolf, bee, elephant |
| `inner_wheel` | The Inner Wheel | virtues, sins, moods (+ intelligences as emblem-only family) |
| `gaming` | Gaming | wow_alliance, wow_horde, wow_evil, cp_gangs, cp_street, cp_corpo |
| `films` | Films | sw_jedi, sw_sith, sw_dyad |

The Encyclopedia's five halls REMAIN the GUI presentation layer; the
halls table in `app/encyclopedia.py` becomes a READ of taxonomy data
(hall membership moves into `config/taxonomy.py`). Gallery subgroups
(Clock Bodies / Sky Events / …) stay presentation-only.

### `config/taxonomy.py` contents (new module, ≤ ~500 lines of tables)

- `CATEGORIES` — the five roots with display names.
- `WEEK_GROUPS` — the table above.
- `THEMES` — per theme: key, display title, category/group, looks,
  seat structure (plain / dual / dual+ninth / dual+two-ninths),
  metals capability (replaces `METAL_THEMES` membership),
  asset directory (derived, but stored for the structure test).
- `ROSTERS` — per rotating seat: ordered tuple of figures
  `(stem, display_name, article_key | None)`.
- Existing flat tables in `constants.py` / `defaults.py` that this
  supersedes are DELETED and their readers repointed (Rule #6):
  `WEEKDAY_THEMES`, `METAL_THEMES(+OVERRIDE)`, `WEEKDAY_THEME_TITLES`,
  the hall tuples in `encyclopedia.py`, and every per-theme scatter
  the agent finds via grep. `theme_metals()` & co. move to taxonomy.

<a id="naming"></a>

## Naming Convention

`<Figure>[_vN]_<src>.png` — `src ∈ {gem, gpt}`; owner hand-made art
with no AI source carries NO suffix. Resolution order in
`config/paths.art_file`: active source suffix first, the other suffix
as cross-source fallback (replaces today's cross-source-tree
fallback), then suffixless.

Register subfolders survive (they are structural art sets, not
sources): `primary/`, `colored/`, `pantheon/`, `glass/`, `circle/`
(the 1:1 badge companions — living BESIDE their lancet family).

<a id="rosters"></a>

## Rotation Rosters — figure-first

- `config/defaults.rotating_art_file` is REPLACED by a roster-based
  picker: `roster_pick(theme, seat, on_date)` → the figure tuple;
  index = `on_date.toordinal() % len(roster)`. Art path derives from
  the figure stem; hover/encyclopedia read display name + article key
  from the SAME pick — image and story always travel together.
- Same-figure variants (`_vN`) rotate INSIDE the picked figure
  (era Byzantine v2, Scale versions) — a second, inner pick.
- Synchronized pair rotation (Cyberpunk Power trio, Scale
  Judas/Lucifer) needs no flag — equal roster lengths keep the shared
  ordinal in step, exactly as today.
- The alt→figure identity map for renaming files comes from the
  PROMPT SHEETS (each `X (alt) → .../alt/Seat.png` entry names its
  real figure) — the sheets are authoritative; the agent extracts the
  mapping, renames, then rewrites the sheet entry to the new path.
- `SCALE_ART_STEMS` naming-zoo tolerance dies: scale files are
  renamed to the single convention and the table collapses into the
  roster.

<a id="relocation"></a>

## Folder Relocation Map (roots)

| Old | New | Notes |
|---|---|---|
| `assets/weekday/<src>/<theme>/**` | `assets/weeks/<group>/<theme>/**` | source → suffix; theme renames applied |
| `assets/zodiac/**` | `assets/calendars/zodiac/**` | |
| (chinese mount art, wherever it lives — locate via config) | `assets/calendars/zodiac/chinese/**` | |
| (almanac/months 12-set + slavic months) | `assets/calendars/almanac/**`, `assets/calendars/slavic_months/**` | locate via `months` sheet + config |
| `assets/archetype/<src>/<family>/**` | `assets/archetypes/<family>/**` | incl. tetramorph, evangelist |
| `assets/badge/<src>/circle/<family>/**` | `assets/archetypes/<family>/circle/**` | badge beside its lancet |
| `assets/badge/<src>/scale/**` | `assets/archetypes/scale/**` | the Judas–Lucifer duality |
| `assets/badge/<src>/trinity/**` | `assets/archetypes/trinity/badges/**` | |
| `assets/badge/<src>/season/**` | `assets/celestial/seasons/badges/**` | |
| `assets/eclipse/**` | `assets/celestial/eclipse/**` | |
| `assets/era/**` | `assets/celestial/era/**` | |
| `assets/earth/**` | `assets/celestial/earth/**` | continents theme + Earth marker read here |
| `assets/emblem/**` | `assets/weeks/inner_wheel/<family>/**` | virtue/sin/mood/intelligence |
| `assets/hands`, `ring`, `subdial`, `icons`, `guide`, `instrument` | `assets/instrument/{hands,ring,subdial,icons,guide,…}` | merge carefully; inspect existing `instrument/` first |
| `assets/logo.svg`, `logo-setup.svg` | UNCHANGED | build pipeline contract |
| `assets/_state/**` | restructured in Phase 2 | ledger follows sheets |
| `assets/archetype/<src>/calendar/**` | inspect `calendar_prompts.md` + consumers, then map to `calendars/` or `archetypes/calendar/` | document the verdict in the manifest |

Anything found under `assets/` not listed here: STOP, map it by its
consumer (grep config/render), and record the decision in the
manifest — no file may be dropped or left behind.

<a id="renames"></a>

## Theme Renames (keys, folders, display — all three aligned)

| Old key | New key | Display |
|---|---|---|
| monsters | `age_of_heroes` | Age of Heroes |
| chinese_myth | `celestial_court` | Celestial Court |
| religion | `creeds` | Creeds |
| religion_alt | `ancient_religions` | Ancient religions |
| bible2 | `bible_ii` | Bible II |
| planets + planet_signs + planets_art | `planets` (looks: canon/signs/art) | Planets |
| (wow blocks) | `wow_alliance` / `wow_horde` / `wow_evil` | WoW — Alliance / Horde / Evil |
| (cyberpunk blocks) | `cp_gangs` / `cp_street` / `cp_corpo` | Cyberpunk — Gangs / Street / Corpo |
| (star wars blocks) | `sw_jedi` / `sw_sith` / `sw_dyad` | Star Wars — Jedi / Sith / Dyad |
| Child_Dawn (figure) | `Child_Anchor` | the Child — the Anchor |

User settings on disk may hold old keys — `app/settings_store.py`
gains a ONE-TIME documented migration map applied on load (external
input, so this is not a Rule-#6 violation; it is the documented
fallback pattern).

<a id="phases"></a>

## Execution Phases

**Phase 1 — structure (agent):** `config/taxonomy.py`; file moves +
renames per the maps above (use `git mv`; preserve pixels — NO image
edits); `paths.art_file` suffix resolution; roster picker replacing
`rotating_art_file` + `SCALE_ART_STEMS`; repoint every consumer
(config/render/app/tests); settings key migration; encyclopedia halls
read taxonomy; `test_assets_structure.py` rewritten as the
taxonomy-mirror test; minimal CANON amendment recording the
Child_Anchor rename (expansion is Phase 3). All tests green.

**Phase 2 — sheets & ledger (same agent):** rewrite every
`research/prompts/**` drop path to the new tree + suffix convention;
alt entries renamed to figure-named paths; `_state` ledger
restructured to match (per sheet, source recorded per entry);
regenerate COVERAGE.md paths; update `___assets.md`, affected
`___folder.md` docs, ROSTER.md/build_roster.py.

**Phase 3 — new content (separate round, after Phase 1+2 verified):**
the four Dozen sheets, the abstract trinity/duality sheets, CANON
expansions (Anchor, Dozens, the two systems), encyclopedia article
stubs. Specs below.

**Phase 4 — PromptPainter (separate project, flag only):** it must
inject the source as a filename SUFFIX instead of a path segment.
Do NOT modify that project from this session — report it as a
follow-up for its own session.

<a id="gates"></a>

## Verification Gates (agent MUST satisfy before committing each group)

1. **No file lost:** PNG/SVG count under `assets/` identical before
   and after each move group (excluding intentional deletions — there
   are NONE planned). Produce `research/relocation_manifest.md`:
   every old→new pair, plus per-root counts.
2. **No pixel touched:** moves are `git mv` / renames only.
3. **Tests:** `python -m pytest tests` fully green after Phase 1 and
   again after Phase 2. Golden values untouchable.
4. **No stragglers:** `grep -r "assets/weekday\|assets/archetype/\|assets/badge\|gemini\|chatgpt"` over
   config/render/app/tests/research returns only the settings
   migration map and historical notes explicitly marked as such.
5. **Commits:** version series `0.14.400+`, logical groups (taxonomy /
   moves / code repoint / sheets / docs), message format per root
   CLAUDE.md.

<a id="new-content"></a>

## New Content Specs (Phase 3 reference)

### The two Dozen systems (owner geometry, sealed)

- **System A — zodiac-aligned (12h–14h wedges):** boundaries ON the
  cardinal points → six PAIRS (2 top, 2 bottom, 2 left, 2 right).
  Carries dozens that come in pairs.
- **System B — month-aligned (11h–13h wedges, 15° offset):** wedge
  centers ON the cardinals → one crown, one root, two flanks, six
  opposition axes. Carries dozens defined by opposites.

### The four Dozens

1. **Emotions (System B):** the six prism seats stand at their canon
   hours — Love 12h, Courage 16h, Pride 20h, Hatred 24h, Fear 04h,
   Humility 08h — six new intermediates: Hope 14h, Ambition 18h,
   Envy 22h, Despair 02h, Doubt 06h, Gratitude 10h.
2. **Virtues + Vices (System B, two registers of ONE wheel —
   paint/light doctrine):** Aristotle's twelve — Courage/Cowardice,
   Temperance/Gluttony, Generosity/Greed, Magnificence/Vulgarity,
   Magnanimity/Vanity, Patience/Wrath, Truthfulness/Boastfulness,
   Wit/Buffoonery, Friendliness/Flattery, Modesty/Shamelessness,
   Right Ambition/Over-ambition, Just Indignation/Envy. Crown/root
   assignment proposed at sheet-writing, owner approves.
3. **Olympians (System A, six pairs):** Zeus+Hera (crown pair),
   Apollo+Artemis (flanks — sun/morning left, moon/evening right),
   Ares+Aphrodite, Hephaestus+Athena, Hermes+Dionysus,
   Poseidon+Demeter (root pair).
4. **Apostles (System A, six pairs, sent two by two):** Peter+Andrew
   (crown), James+John, Philip+Bartholomew, Thomas+Matthew,
   James-of-Alphaeus+Thaddaeus, Simon-the-Zealot+Judas (root — Judas
   beside midnight, mirroring prism Hatred at 24h).

### Abstract trinities & dualities to illustrate

Trinities: Judge/Prosecutor/Advocate (the callings), Faith/Love/Hope,
Past/Present/Future, Thesis/Antithesis/Synthesis. Dualities:
Good/Evil, I/Others (love-for-self / love-for-others). House
night-window register, lancet + 1:1 circle companion each, per the
badge system.

### Child — the Anchor (CANON expansion text basis)

The anchor is DUAL: it holds the family gathered (the bond), and it
hangs at the BOTTOM — the bottom of the hierarchy. That bottom seat
is itself part of the family's love mechanics: the mother's love for
the child includes having someone to whom she can be dominant and
principal, someone who sees in her hierarchical superiority. The Dawn
reading (the child as the new day / the future) survives as the
stacked time-reading, per the Triads convention.
