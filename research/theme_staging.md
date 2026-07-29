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
this file (folder names in the first cell of any table row): every theme
folder under `assets/weeks/` must be either a registered
`constants.WEEKDAY_THEMES` key or a row here. Deleting a cast's row
without also completing its checklist would make the guard fail again —
the two are locked together on purpose, so a future round cannot
generate art and quietly abandon it (the exact failure that opened this
ledger, see CLAUDE.md's law for the twelve-cast/429-file story).

The file carries TWO tables, and only the first is wiring debt. **The
wiring table is empty as of 2026-07-29** — every cast the law was
written for is registered. The second, §Art Owed, is its mirror image:
casts that are fully wired and worded while some of their PLATES are
still ungenerated. A cast in that table is visible in the program today;
what it owes is images, not code.

## The Wiring Table — empty, the backlog is closed

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

**Completion wave III landed 2026-07-29 (Session 33):** `sw_jedi`,
`sw_sith` and `sw_dyad` left this ledger with all twenty checklist lines
done — registered in `constants.WEEKDAY_THEMES` and `METAL_THEMES`,
seven seat names/dirs/stems apiece, dual, Ninth, title, the NEW
`defaults.WEEKDAY_MENU_GROUPS` "Films" picker group (the second and last
group the backlog's checklist line 12 named), and ONE Encyclopedia card
carrying a three-way Jedi | Sith | Dyad switcher
(`config.encyclopedia_tree.VARIANT_SOURCES` — the backlog's structural
answer 2: one card, never three; it seats in The Human Wheel beside the
Warcraft and Cyberpunk cards, and the eleventh-card overflow widens that
whole's EXISTING named carve-out by one rather than opening a new
exemption, since WORKPLAN-STRUCTURE.md §THE NINE WHOLES hands all three
franchise cards to `worlds` in the same cut). None of the three had a
`taxonomy.THEME_KEY_RENAMES` entry to delete; the folder names were
always their code keys. 184 texts in all (~93,600 characters): 3 × 61 —
7 seat articles, 42 per-wheel variants, the 2 Ruler/Servant face texts,
7 arm blurbs, the theme title, the week-duality page and the Ninth —
plus the one card line the shared card reads.

**THE DYAD'S THREE ROTATING SEATS are wired** through the same
`defaults.WEEKDAY_SEAT_ROSTERS` the Cyberpunk half built one commit
earlier: Tuesday (Finn / Phasma), Wednesday (Maz / DJ) and the Ninth
(The Ghosts / Exegol) — the registry's first PLACE-vs-PLACE Ninth, which
the canon expressly permits. See the PROVISIONAL note in the art-owed
row below for the mechanism question this closes and how to reopen it.

**The wiring table is empty.** The twelve casts CLAUDE.md's THEME
COMPLETION LAW was written for are all registered, worded and seated;
`tests/test_theme_completeness.py`'s *no art sits unseen* guard now
passes on registration alone, with no ledger row carrying it.

**Original debt:** 429 files across 12 casts, ~200 mandatory texts
(~145,000 characters of house voice) across three writing waves —
Session 31 (myth & crafts, 3 casts), Session 32 (gaming, 6 casts),
Session 33 (films, 3 casts). See `WORKPLAN.md` §THE THEME BACKLOG for
the full PER-CAST CHECKLIST and the reasoning behind the wave split. All
three waves landed on 2026-07-29; 554 texts in all.

A row is deleted only in the same commit that finishes its cast's
checklist — see item 20 of the checklist itself: "the cast passes the
theme-completeness guard (Session 30) with NO exemption left."

## Art Owed — wired casts whose plates are incomplete

**These rows are NOT wiring debt.** The casts below are fully
registered, worded and seated; what they still owe is IMAGES. They are
listed here because the law that opened this ledger is about art and
text shipping together, and a cast that ships its text against art the
owner has not generated yet is exactly the kind of gap that must be
written down rather than discovered later. Every missing plate is
graceful-absent by contract (Rule #1's documented path): the seat draws
the procedural disc, the name and the article still resolve, and the
plate lights up the day it lands with no code change.

| Folder | Group | Files on disk | Prompt sheet | Plates still owed |
|---|---|---|---|---|
| `sw_jedi` | films | 22 | [Star Wars Prompts](prompts/starwars/starwars_prompts.md) | 3 seats: the Throne (Luke), the Mirror (Vader) and the Ninth (Yoda). Chewbacca has bronze but no `colored/` twin. |
| `sw_sith` | films | 18 | [Star Wars Prompts](prompts/starwars/starwars_prompts.md) | 4 seats: Wednesday (Jabba) and the Throne (Palpatine) have `colored/` but no BRONZE master, so the three metal looks are dark on them; Saturday (Boba Fett) and the Mirror (Anakin) have nothing at all. |
| `sw_dyad` | films | 3 | [Star Wars Prompts](prompts/starwars/starwars_prompts.md) | 11 of its 12 declared figures — everything except Monday (Rose): the Throne (Rey), the Mirror (Kylo), Thursday (Leia), Friday (Han), Saturday (Hux), and all six roster members of the three rotating seats (Finn/Phasma, Maz/DJ, Ghosts/Exegol). |

**PROVISIONAL — the Dyad's Ninth rotation mechanism (owner call still
open).** The sheet's own "rotation convention" section names two ways to
turn The Ghosts / Exegol and expressly leaves the choice to the owner at
wiring time: (a) the plain date rotation every other rotating seat uses,
or (b) a reuse of `core.continents`'s Zealandia/Pangea TRIGGER, where
the rarer face surfaces only when the sky is doing something. **Session
33 wired (a)** — `defaults.WEEKDAY_SEAT_ROSTERS["sw_dyad"]["ninth"]` —
because Rule #5 says one rotation mechanism rather than two, and the
sheet argues the PAIRING rather than the trigger. The rejected
alternative is (b), and flipping to it is a small, fully named change,
written out in that table's own comment. The regression
`test_sw_dyad_ninth_rotates_through_the_seat_roster` in
`tests/test_weekday_rotation.py` pins which of the two is live, so a
flip has to be deliberate. This note stands until the owner rules.

A row leaves THIS table when its plates land, not when its wiring does.
