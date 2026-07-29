# Theme Staging Ledger

**Purpose** (Session 30, `WORKPLAN.md` §THE THEME BACKLOG, project
[CLAUDE.md](../CLAUDE.md) §THE THEME COMPLETION LAW): the honest debt
list for every ART-ONLY weekday cast — art already generated and sitting
on disk under `assets/weeks/`, not yet registered in
`constants.WEEKDAY_THEMES`, so the dial's theme picker cannot show it
and the Encyclopedia has no page for it. A cast leaves this ledger the
moment its own wave finishes **every** line of the PER-CAST CHECKLIST
(`WORKPLAN.md` §THE THEME BACKLOG) — never before, and never partially.
The law is that a theme ships wired, worded and seated together, or it
stays listed here as an open, named debt; deferring silently is what the
law exists to end.

`tests/test_theme_completeness.py`'s *no art sits unseen* guard reads
this file (folder names in the first column of the table below): every
theme folder under `assets/weeks/` must be either a registered
`constants.WEEKDAY_THEMES` key or a row here. Deleting a cast's row
without also completing its checklist would make the guard fail again —
the two are locked together on purpose, so a future round cannot
generate art and quietly abandon it (the exact failure that opened this
ledger, see CLAUDE.md's law for the twelve-cast/429-file story).

## The Three Still Owed

**Completion wave I landed 2026-07-29 (Session 31):** `age_of_heroes`,
`celestial_court` and `corporate` left this ledger with all twenty
checklist lines done — registered in `constants.WEEKDAY_THEMES` and
`METAL_THEMES`, seven seat names/dirs/stems, dual, ninth, title, picker
group, an Encyclopedia card of their own, and both stale
`taxonomy.THEME_KEY_RENAMES` entries deleted. 186 texts in all
(~83,700 characters): the 51 mandatory ones, the 6 Ruler/Servant face
texts, 3 card lines for the Encyclopedia's theme screen, and the 126
per-wheel variant readings the corpus lint requires of every registered
theme. Their rows are gone from the table below, which is the only way
a cast may ever leave it.

**Completion wave II, WoW half, landed 2026-07-29 (Session 32):**
`wow_alliance`, `wow_horde` and `wow_evil` left this ledger with all
twenty checklist lines done — registered in `constants.WEEKDAY_THEMES`
and `METAL_THEMES`, seven seat names/dirs/stems apiece, dual, Ninth,
title, the NEW `defaults.WEEKDAY_MENU_GROUPS` "Gaming" picker group, and
ONE Encyclopedia card carrying a three-way Alliance | Horde | Evil
switcher (`config.encyclopedia_tree.VARIANT_SOURCES` — the backlog's
structural answer 2: one card, never three). None of the three had a
`taxonomy.THEME_KEY_RENAMES` entry to delete; the folder names were
always their code keys. 184 texts in all (~112,000 characters): 3 × 61 —
7 seat articles, 42 per-wheel variants, the 2 Ruler/Servant face texts,
7 arm blurbs, the theme title, the week-duality page and the Ninth —
plus the one card line the shared Encyclopedia card reads. Their rows
are gone from the table below, which is the only way a cast may ever
leave it.

**Completion wave II, Cyberpunk half, landed 2026-07-29 (Session 32):**
`cp_gangs`, `cp_street` and `cp_corpo` left this ledger with all twenty
checklist lines done — registered in `constants.WEEKDAY_THEMES` and
`METAL_THEMES`, seven seat names/dirs/stems apiece, dual, Ninth, title,
appended to the "Gaming" picker group the WoW half opened, and ONE
Encyclopedia card carrying a three-way Gangs | Street | Power switcher
(`config.encyclopedia_tree.VARIANT_SOURCES` — the backlog's structural
answer 2: one card, never three; it seats in The Human Wheel beside the
Warcraft card, and the tenth-card overflow is a NAMED carve-out pointing
at the Session 35 cut, never a loosened cap). None of the three had a
`taxonomy.THEME_KEY_RENAMES` entry to delete; the folder names were
always their code keys. 184 texts in all (~118,000 characters): 3 × 61
— 7 seat articles, 42 per-wheel variants, the 2 Ruler/Servant face
texts, 7 arm blurbs, the theme title, the week-duality page and the
Ninth — plus the one card line the shared card reads.

**THE ROTATION SEATS these three owed are wired**, in the one place
every weekday consumer already calls: `defaults.WEEKDAY_SEAT_ROSTERS`
declares a seat's figures (canonical first) and `rotating_art_file`
resolves them, so the dial, the hover legend, the Encyclopedia and the
pickers all turn together with no app-code change. Ten seats carry a
roster — four in Gangs, three in Street, and the Power cast's
synchronized Throne/Mirror/Ninth triad, whose lockstep falls out of the
shared date modulo and equal roster lengths exactly as its sheet
predicted. Twelve plates that no table could otherwise have reached are
now shown; a rotating seat's DISPLAY NAME lists every member of its
roster and its article argues all of them, so the label can never
disagree with the plate. Pinned by four regressions in
`tests/test_weekday_rotation.py`.

| Folder | Group | Files on disk | Prompt sheet | Still owes | Owed by |
|---|---|---|---|---|---|
| `sw_jedi` | films | 22 | [Star Wars Prompts](prompts/starwars/starwars_prompts.md) | Full PER-CAST CHECKLIST (all 20 lines). Shares the wave's new `defaults.WEEKDAY_MENU_GROUPS` "Films" entry with the other two film casts. | Session 33 |
| `sw_sith` | films | 18 | [Star Wars Prompts](prompts/starwars/starwars_prompts.md) | Full PER-CAST CHECKLIST (all 20 lines). Same new "Films" menu group. | Session 33 |
| `sw_dyad` | films | 3 | [Star Wars Prompts](prompts/starwars/starwars_prompts.md) | Full PER-CAST CHECKLIST (all 20 lines), PLUS its place-vs-place Ninth rotation (The Ghosts / Exegol) — either `rotating_art_file` or a reuse of `core.continents`'s Zealandia/Pangea trigger (owner call, documented in the sheet's own "rotation convention" section). Same new "Films" menu group. | Session 33 |

**Original debt:** 429 files across 12 casts, ~200 mandatory texts
(~145,000 characters of house voice) across three writing waves —
Session 31 (myth & crafts, 3 casts), Session 32 (gaming, 6 casts),
Session 33 (films, 3 casts). See `WORKPLAN.md` §THE THEME BACKLOG for
the full PER-CAST CHECKLIST and the reasoning behind the wave split.

**Remaining debt:** 43 files across the 3 casts above — the three
film casts of Session 33. Sessions 31 and 32 between them cleared nine
casts and 386 files, and `sw_dyad`'s Ninth rotation is the last open
wiring question in the whole backlog (the seat-roster mechanism the
Cyberpunk half built is now one of the two options that entry names).

A row is deleted only in the same commit that finishes its cast's
checklist — see item 20 of the checklist itself: "the cast passes the
theme-completeness guard (Session 30) with NO exemption left."
