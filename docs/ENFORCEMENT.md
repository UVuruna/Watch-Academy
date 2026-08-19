# Enforcement installed here

The guards this project runs, what each one fails on, and the ratchets
that may only shrink. The shared rules are the monorepo's
[Code Rules](../../../rules/CODE.md); this file records only what is
installed HERE. Sibling docs: [Decisions](DECISIONS.md) ·
[Art Pipeline](ART-PIPELINE.md) · [The Dial](DIAL.md)

## The guard runner

`.claude/settings.json` wires two hooks, both relative to the repo root
(`.claude/` stayed at the true root — [THE THREE-FOLDER
MIGRATION](DECISIONS.md#three-folder) — hence the `desktop/` prefix):

```
PostToolUse  python desktop/tests/run_guards.py --fast
Stop         python desktop/tests/run_guards.py
```

Exit 2 blocks. The FULL pass runs only when
`rules/hooks/changed_files.py` says this session changed something —
"cannot tell" always means RUN.

| Guard | Pass | Fails on |
|-------|------|----------|
| `test_structure_law.py` | fast | any `.py` over ~1,000 LOGIC lines outside the RATCHET |
| `test_config_sections.py` | fast | post-definition patching, duplicate dict keys, or a definition above the first section banner, in any `config/*.py` |
| `test_layout_law.py` | fast | THE SPACE & LEGIBILITY LAW, static half — forbidden GUI APIs in GUI sources |
| `test_docs_coverage.py` | full | a source file missing the docs its tier requires, a legacy beside-script doc, or an orphan doc |
| `test_doc_links.py` | full | a broken relative `.md` link, or a doc unreachable from `README.md` |
| `test_old_name.py` | full | any spelling of the old project name in a shipped file, line by line |
| `test_config_cohesion.py` | full | Session 36's config split undone — a `config/*.py` over the threshold, or a moved name still reachable through `defaults` |
| `test_theme_completeness.py` | full | a registered theme with no text, or a theme folder that is neither registered nor in the staging ledger |
| `test_art_reachability.py` | full, art only | art on disk that nothing in the program can reach (walks the whole assets tree — runs only when art, config or registry files were touched) |
| `test_layout_audit.py` | full, GUI only | THE SPACE & LEGIBILITY LAW, runtime half — builds each touched window offscreen and measures it (clipped, elided, scroll+slack, item cut, overlap, contrast). A window's declared minimum must EXIST; its SIZE is printed, never judged |
| `clone_guard.py` (monorepo) | full | a duplicated function body across two files, outside `tests/clone_ratchet.json` |
| `structure_guard.py` (monorepo) | full | a `.py` under `desktop/` over 1,000 logic lines with no entry in `tests/structure_ratchet.json`, a ratcheted file that GREW, or a stale entry |

`test_config_cohesion.py` and `test_theme_completeness.py` are
project-specific and are NOT part of the standard four.

**The screen floor was abolished on 2026-08-18** (owner decree): "1280×720 is nobody's screen; a window is judged on the device profiles it is shot on; what is taller than a screen scrolls; the minimum is information, never a verdict." The old ABSURD MINIMUM failure in `test_layout_audit.py` / `layout_checks_qt.py` is now the informational line `report_minimum()` prints beside each window — the declared minimum against the `pc-low` reference screen. The clipped, starved and contrast teeth are unchanged.

Screenshot evidence for GUI work is produced by the monorepo runner —
`python u:/Coding/UVuruna/rules/tools/uv.py shot --all`, window registry in
`.claude/uv_windows.py` — not by the audit's own shots.

<a id="the-measure"></a>

## THE ONE ARITHMETIC (WA-R15, 2026-08-19) — awaiting the owner's word

Until this round the project measured a file's size three ways, and two
guards inside the SAME `run_guards.py` FULL disagreed about the same file:

| Measure | Used by | `app/controller.py` | `config/defaults.py` |
|---------|---------|--------------------|----------------------|
| non-blank, non-comment | `rules/tools/structure_guard.py` (monorepo) | 899 | 418 |
| total minus declarative tables | `desktop/tests/test_structure_law.py` | 1,218 | 835 |
| raw lines | `desktop/tests/test_config_cohesion.py` | — | **1,036 (RED)** |

That is why `test_config_cohesion.py` was red at HEAD, and why WA-R14
had to leave a ratchet entry on a file it had already brought under the
wall. A law whose guards cannot agree on the number is not enforced, it
is argued about.

**The ruling applied here:** the definition lives in ONE module,
`desktop/tests/line_measure.py`, and it starts from the monorepo's —
non-blank, non-comment lines. On top of it the owner's ruling of
2026-08-05 is kept whole: a top-level declarative table is not
behaviour, so THE STRUCTURE LAW subtracts it. **CONFIG COHESION does
not subtract it**, because a config module is almost all table and a
guard that cannot fire is worse than none — its subject is precisely how
many table rows live in one module.

This makes the project's structure guard never STRICTER than the shared
tool, so a file the shared tool rejects still fails the FULL pass through
`structure_ratchet.json`. The two can no longer disagree in the direction
where "fine" wins.

Both guards were shown FAILING on a planted over-wall module and passing
after it was removed by hand.

**Consequences, all of them shrinks:** `app/controller.py` (885),
`render/compositor.py` (740) and `config/constants.py` (125) left the
structure ratchet; `test_config_cohesion.py` lost both of its
exemptions (`constants.py` 770, `pantheon.py` 344 — a test whose own
docstring promised none) and now walks `config/` RECURSIVELY, so
`config/registry/` is covered for the first time.

<a id="constants-debt"></a>

### The debt this left: `config/constants.py`'s SHAPE — **PAID 2026-08-19**

Its SIZE was settled by THE ONE ARITHMETIC — 125 lines of behaviour
behind 645 lines of declarative tables. Its SHAPE was not: **38
top-level sections** spanning app identity, era notation, weekday
bodies, pointer geometry, ring finishes, zodiac, translation languages,
UI scale and seating is a junk drawer, not a directory. The [OOP
audit](AUDIT-OOP-2026-08-18.md)'s R15 asked for a topic split in the
shape of Session 36 (new `config/<topic>.py` modules, callers repointed,
no re-export shims), and WA-R15 deliberately did NOT do it: no guard
demanded it, it repoints **1,070 references across 142 files**, and the
topic names had to come from the owner's own vocabulary
([The DOMY Canon](../CANON.md), THE RING VOCABULARY in
[The Dial](DIAL.md)), not an agent's guess.

**The owner gave the map and the names on 2026-08-19, and the split
landed the same day.** `config/constants.py` is DELETED. Eleven new
modules were born and nine existing ones grew; every reference was
repointed to the module that now owns the name; **no shim of the deleted
module was left behind** (`rules/CODE.md` — No backward compatibility),
so `constants.NAME` no longer resolves anywhere. Four registry-derived
aliases that predate the round survive under their project-facing names
in `config/ninth.py`, declared and argued at
[Config → THE CONSTANTS SPLIT](../desktop/config/___config.md#the-constants-split)
rather than left to be discovered.

The map, one row per section, with the reason for every destination:
[Config (folder) → THE CONSTANTS
SPLIT](../desktop/config/___config.md#the-constants-split). Every new
module carries its own `__about/` (and `__flow/` for the seven
Algorithmic ones) stating what it holds, why it was separated and who
its neighbours are — the owner's explicit condition for the round.

One commit per destination module:

| Commit | Module |
|--------|--------|
| `0fe05f9` | **NEW** `config/identity.py` |
| `1c1ec22` | `config/dial.py` ← the dial identity block |
| `92290eb` | **NEW** `config/sky.py` |
| `a6b2910` | the two aliased `constants` imports normalised |
| `3fe8164` | **NEW** `config/eras.py` |
| `f3400c6` | `config/registry/week.py` ← the weekday vocabulary |
| `c79b69b` | **NEW** `config/pointer_geometry.py` |
| `ff9bccd` | **NEW** `config/pointer_names.py` |
| `2a86b8a` | `config/calendar_mounts.py` ← rose & calendar star geometry |
| `e6d016d` | `config/watch_face.py` ← WATCH FACE CONTENT KINDS |
| `3a06a11` | `config/archetypes.py` ← TRIO & GENESIS ARM THEMES |
| `381acc4` | **NEW** `config/umbra.py` |
| `e18f7cd` | `config/registry/slots.py` ← the WHEEL slots and arm offsets |
| `973d72b` | `config/cube.py` ← THE CUBE LOOK |
| `6d64003` | **NEW** `config/complications.py` |
| `8b4985b` | **NEW** `config/ring.py` |
| `06ecea8` | **NEW** `config/ninth.py` |
| `4e1a483` | **NEW** `config/zodiac.py` |
| `81a529a` | `config/glow.py` ← GLOW WINDOWS & ECLIPSE VISIBILITY |
| `755124b` | **NEW** `config/ui_ranges.py` |
| `0f7a591` | `config/doctrine.py` ← DUALITY SEATING |
| *(final)* | the three registry aliases collapsed, `constants.py` DELETED, docs |

**One deviation from the map, and it is written down.** WEEKDAY THEMES
and THEME BLURBS & ARTICLES were mapped to `config/registry/week.py`,
but their three names were one-line aliases of `registry.THEMES` /
`.BLURBS` / `.ARTICLES` — and `config/registry/__init__.py` imports
`week.py`, so reading them back there is an import cycle, while
re-deriving them would give one truth two homes. The aliases were
DELETED and their 45 call sites repointed to THE REGISTRY directly; each
alias's comment moved to the derivation site. A second name for the same
object is itself a re-export shim.

**What the split leaves for the next session.**
`config/registry/week.py` is now **987 logic lines** against
`test_config_cohesion.py`'s 1,000-line wall, and that guard has no
ratchet and no exemption list: **the next weekday table added there
needs a split, not a row.** Nothing else in `config/` is close.

## The ratchets — all of them may only SHRINK

Adding an entry to any of them needs the owner's explicit approval in that
same session.

**THE STRUCTURE RATCHET** lives in `desktop/tests/test_structure_law.py`.
Today: **five test files and nothing else** (`test_pointer`,
`test_settings_dialog`, `test_skins`, `test_archetype`, `test_eclipse`),
all owed to a test-hygiene round. Each entry names why it is tolerated
and who owes the split. It measures through
[THE ONE ARITHMETIC](#the-measure), so it holds exactly what the
machine-readable ratchet holds — **nothing** — plus the test files the
monorepo tool does not scan.

**`render/tooltip_composer.py` LEFT the list on 2026-08-19**, and with it
the last product file: the owner gave the word for the cut BY TOOLTIP
FAMILY that its own `owes` line had recorded as debt. 2,239 logic lines
became five files, none near the wall —
`render/tooltip_sky.py` (624), `render/tooltip_ring.py` (748),
`render/tooltip_calendar.py` (504), `render/encyclopedia_targets.py`
(262) and the composer itself (266), which keeps the three doors, the
dispatch and the six shared formatting helpers. **The families are
MIXINS, not collaborators** — the entry's own objection was "three
holders is three back-channels", so the dial stays held ONCE, by the
composer, and the four bases read it through `self._dial`. Not one call
site changed. The move is proved by
`desktop/tests/test_tooltip_families.py`: 959 hover points over seven
dial configurations, a SHA-256 of the HTML per point plus 42
representative tooltips kept verbatim, **recorded from the un-split
composer at commit `6aa49db`** and green after the cut.

**TWO GUARDS, TWO ARITHMETICS — found by WA-R14, closed by WA-R15.**
WA-R14 cut `app/controller.py` into five responsibility mixins beside it
(`controller_shortcuts`, `controller_menu`, `controller_display`,
`controller_dialogs`, `controller_simulation`) and left
`structure_ratchet.json` in that commit — but its entry HERE had to stay
one more round, because this guard read the same file as 1,218 where the
shared tool read 899. Cutting three more slivers out of a 899-line
composition root to satisfy the looser arithmetic would have been exactly
the "unnatural pieces" the owner forbade on 2026-08-18, so the
disagreement was written into the entry instead and
[THE ONE ARITHMETIC](#the-measure) closed it the next commit.

**The refactor round of 2026-08-18** ([OOP
audit](AUDIT-OOP-2026-08-18.md#round-2026-08-18)) moved it a long way in
one night: `app/observatory.py` LEFT the list by becoming the
`app/observatory/` package (charts / panels / dialog, none of them near
the wall); `app/controller.py` fell from 3,436 to 2,538 logic lines when
the skin composition became `app/skin_builder.py`; and
`render/compositor.py` fell from 3,100 to 747 when the tooltip bank
became the collaborator `render/tooltip_composer.py` — which took its
place on the list at 2,238 lines, carrying a written reason and what it
owes. **The owner RATIFIED that entry** when he accepted R13 on
2026-08-18; on 2026-08-19 its `owes` line gained the natural next cut,
BY TOOLTIP FAMILY (sky · ring · calendar), recorded as debt with no code
written. **The round of 2026-08-19 (WA-R14)** then took
`app/controller.py` off the machine-readable list entirely: 2,538 logic
lines became an 899-line composition root plus five mixins, none of them
near the wall. Before that round,
`render/layers.py` had left by being split and `config/pantheon.py`
because the threshold measures logic and 962 of its lines are declarative
cast tables. The ratchet only ever shrinks.

**THE MACHINE-READABLE STRUCTURE RATCHET** lives beside it in
`desktop/tests/structure_ratchet.json`, is **EMPTY since 2026-08-19** —
no `.py` under `desktop/` that the shared tool scans is over the wall at
all — and is read by the monorepo tool
`rules/tools/structure_guard.py` (wired into `run_guards.py` FULL). It is
the same law in a form other tools can read: `{path: {lines, why, owes}}`
measured in non-blank non-comment lines over a 1,000-line wall. It bites in
one place the pytest ratchet cannot — **a ratcheted file that GREW** — which
is the failure that let `app/controller.py` go from the 3,449 lines its own
entry quotes to 4,483 while it "waited for its split". Every split lowers
the recorded number in the same commit; an entry whose file drops under the
wall is deleted — which is what happened to `app/controller.py` itself on
2026-08-19, leaving `render/tooltip_composer.py` as the file's only entry.

**THE ZUBI BASELINE RATCHET (approval 2026-08-09)** lives in
`desktop/tests/zubi_baseline.json`. The runtime layout audit fails ONLY on
findings whose normalized key is absent from it — the owner-frozen
pre-existing backlog, install-only boundary of 2026-08-08. Entries may only
be REMOVED as findings are fixed. Regeneration:

```
DOMY_ZUBI_REBASELINE=1 python -m pytest desktop/tests/test_layout_audit.py -k test_layout_audit
```

It REFUSES to add keys unless `=force`, which is legal only with the owner's
explicit in-session approval.

**THE CLONE RATCHET** lives in `desktop/tests/clone_ratchet.json` and is
**EMPTY** since 2026-08-18. It held one group — the `plate()` diagram
bank, written out in `canon_diagrams.py` and `cube_diagrams.py` — and R1
of the OOP audit absorbed it (and an unratcheted third copy) into
`render/diagram_bank.py: DiagramBank`. The same law still applies: it
shrinks, and a stale entry (a group the code no longer produces) fails
the run so it gets removed by hand. The clone guard is silent on this
project at its own threshold and reports no same-file WARN either.

<a id="theme-completion"></a>

## THE THEME COMPLETION LAW (decree 2026-07-29)

**A theme is not finished when its art is generated. It is finished when it
is SEEN.**

Born from a real, expensive failure: twelve figure casts — Greek Monsters,
Chinese Mythology, The Corporation, three World of Warcraft casts, three
Cyberpunk casts, three Star Wars casts — had **429 image files generated and
correctly placed on disk**, and not one of them was visible anywhere in the
program. They were never registered in `constants.WEEKDAY_THEMES`, so the
dial's picker did not know they existed, and they had no Encyclopedia topic.
The prompt-sheet round that produced them wrote "two wiring rounds left for
later" into [Prompt Coverage](../shared/research/prompts/COVERAGE.md) and
moved on. Later never came, and nothing in the suite could say so.

**Approving a theme commits FOUR deliverables, and they ship TOGETHER:**

1. **The prompt sheet** — the art briefs.
2. **The Encyclopedia articles AND the hover blurbs** — every seat, the dual
   page, the ninth, the theme title.
3. **The dial wiring** — every config table (the full list is the PER-CAST
   CHECKLIST in [Work Plan](../WORKPLAN.md) §The Theme Backlog).
4. **The Encyclopedia seat** — a card in a whole, reachable from Home.

**A round that ships only the sheet MUST, in the same commit, record its own
debt in the STAGING LEDGER** ([Theme
Staging](../shared/research/theme_staging.md)): which cast, what art exists,
what it still owes, which session owes it. Deferring is allowed; deferring
SILENTLY is not.

Enforced, not merely written (`desktop/tests/test_theme_completeness.py`):
no registered theme may be textless, and no theme folder under
`shared/assets/weeks/` may exist without being either registered or listed
in the staging ledger. A future round that generates art and walks away
fails the suite in the same session that did it.
