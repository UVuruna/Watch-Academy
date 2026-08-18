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

## The ratchets — all of them may only SHRINK

Adding an entry to any of them needs the owner's explicit approval in that
same session.

**THE STRUCTURE RATCHET** lives in `desktop/tests/test_structure_law.py`.
Today: `app/controller.py`, `render/compositor.py`, `config/constants.py`,
`app/observatory.py`, and five test files owed to a test-hygiene round
(`test_pointer`, `test_settings_dialog`, `test_skins`, `test_archetype`,
`test_eclipse`). Each entry names why it is tolerated and who owes the
split. Two files have already LEFT the list — `render/layers.py` by being
split, `config/pantheon.py` because the threshold now measures logic and 962
of its lines are declarative cast tables.

**THE MACHINE-READABLE STRUCTURE RATCHET** lives beside it in
`desktop/tests/structure_ratchet.json` and is read by the monorepo tool
`rules/tools/structure_guard.py` (wired into `run_guards.py` FULL). It is
the same law in a form other tools can read: `{path: {lines, why, owes}}`
measured in non-blank non-comment lines over a 1,000-line wall. It bites in
one place the pytest ratchet cannot — **a ratcheted file that GREW** — which
is the failure that let `app/controller.py` go from the 3,449 lines its own
entry quotes to 4,483 while it "waited for its split". Every split lowers
the recorded number in the same commit; an entry whose file drops under the
wall is deleted.

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

**THE CLONE RATCHET** lives in `desktop/tests/clone_ratchet.json`, written
from the clones that existed on 2026-08-18. Same law: it shrinks, and a
stale entry (a group the code no longer produces) fails the run so it gets
removed by hand.

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
