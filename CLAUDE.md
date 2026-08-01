# CLAUDE.md — Watch Academy

Project guidance for Claude Code. **The universal law is the monorepo
constitution: [UVuruna Constitution](../../CLAUDE.md)** — read it first, then
load ONLY the rulebook your job needs via its [Router](../../CLAUDE.md#router):

| Your job this session | Read |
|-----------------------|------|
| Implement features / fix bugs | [Code Rules](../../rules/CODE.md) + the folder's `___folder.md` |
| Any GUI work | [GUI Rules](../../rules/GUI.md) + [DESIGN.md](../../DESIGN.md) |
| Write / migrate documentation | [Docs Rules](../../rules/DOCS.md) |
| Brainstorm / plan with the owner | [Plan Rules](../../rules/PLAN.md) |
| Split a god-file | [Refactor God-Files](../../REFACTOR-GODFILES.md) |
| Build / release | [Ship Rules](../../rules/SHIP.md) — **this project has no build pipeline yet** |

Nothing from the constitution is restated here. Below are ONLY project facts,
project-specific laws and deltas that TIGHTEN the root rules.

---

## Project Facts (never re-derive these)

- **Product:** transparent frameless 24h desktop clock widget, Windows 11,
  Python 3.13 + PySide6 6.10 + astral 3.2 (+ tzdata). The app is
  **Watch Academy**; **DOMY** is the name of the dial itself. The folder on
  disk is still `Gadgets/DOMY Watch/` — do NOT rename it. Repo:
  `UVuruna/Watch-Academy`.
- **Dial convention:** degrees CLOCKWISE from TOP; 12:00 noon top, 00:00
  midnight bottom, 18:00 right, 06:00 left; `DIAL_OFFSET_DEG = 180`.
  Hour hand = 1 rev/24h, minute hand = 1 rev/h, NO seconds hand.
- **Hexagram:** top vertex ALWAYS points at true solar noon; rotation
  `(noon_secs − 43200)/240` deg, positive = clockwise (west-in-zone/DST).
  Weekday diamond slots ROTATE WITH the hexagram.
- **Year wheel:** piecewise-linear between the six season anchors from
  `Database/seasons_utc.json` — every season spans exactly 90° even though
  real durations differ (owner spec); equinoxes exactly at 90°/270°.
- **Architecture:** one-way flow `config → core (pure, no Qt, no wall clock)
  → data → skins → render → app`; purity is enforced by
  `tests/test_purity.py` (AST-based, covers `core`, `data`, `recolor`).
- **Render structure (since 0.14.688):** `render/context.py` is the layer
  protocol, the geometry/painting modules beside it are the shared
  vocabulary, `render/layers/` holds one module per paint layer, and
  `render/compositor.py` stacks them. `render/layers.py` no longer exists —
  never import from it.
- **Verification:** `python -m pytest tests` (golden values: Belgrade DST
  −4.17°→+10.76°, Tromsø regimes, exact equinoxes, moon 0.7400 on
  2026-07-07, mockup day 20.6.2025 sunrise 04:52/sunset 20:27/noon 12:39).
  **The full suite takes ~18 minutes** — run a targeted subset while working
  and the full suite before committing. `python -m core --city NAME --at ISO`
  eyeballs any moment; the GUI drive recipe is `.claude/skills/verify/SKILL.md`.
- **Win+D ground truth (verified):** the OS raises the desktop layer above
  ALL windows (TOPMOST included), no Qt events arrive — do not chase this
  as a bug; WorkerW glue is the only workaround (optional, M4).
- **Milestones:** M1 shell ✓, M2 computation core ✓, M3 living dial ✓,
  M4–M6 absorbed along the way. What remains to release is
  [Roadmap](ROADMAP.md); the SESSION ORDER with per-session reading lists
  and model tiers is [Work Plan](WORKPLAN.md) — when the owner names a
  session, run it as written there.
- **Canon:** the seating doctrine — the color–virtue–vice–mood web, the two
  rosters, duals, ninths, pointer archetypes — is [The DOMY Canon](CANON.md);
  read it BEFORE any theme, roster or article work. The philosophical core
  (the three-axis Character Cube, the Double Trinity, the Two Crosses, the
  Rose, naming and the writing laws) is [The Cube Canon](CUBE.md) — read it
  BEFORE any character, path, archetype-wheel or naming work.

---

## Enforcement Installed Here

The four guard tests of [Code Rules](../../rules/CODE.md) → Enforcement live
in `tests/`, wired into `.claude/settings.json` hooks
(`PostToolUse` → `python tests/run_guards.py --fast`,
`Stop` → `python tests/run_guards.py`; exit 2 blocks):

| Guard | Fails on |
|-------|----------|
| `tests/test_structure_law.py` | any `.py` over ~1,000 lines outside the RATCHET |
| `tests/test_config_sections.py` | post-definition patching, duplicate dict keys, or a definition above the first section banner, in any `config/*.py` |
| `tests/test_docs_coverage.py` | a source file missing the docs its tier requires, a legacy beside-script doc, or an orphan doc |
| `tests/test_doc_links.py` | a broken relative `.md` link, or a doc unreachable from `README.md` |

Two project-specific guards sit beside them and are NOT part of the standard
four: `tests/test_config_cohesion.py` (pins Session 36's config split — every
`config/*.py` at or under the threshold, and no moved name still reachable
through `defaults`) and `tests/test_theme_completeness.py` (below).

**The RATCHET may only SHRINK.** Adding an entry needs the owner's explicit
approval in that same session.

---

## THE THEME COMPLETION LAW (owner decree 2026-07-29)

**A theme is not finished when its art is generated. It is finished when it
is SEEN.**

Born from a real, expensive failure: twelve figure casts — Greek Monsters,
Chinese Mythology, The Corporation, three World of Warcraft casts, three
Cyberpunk casts, three Star Wars casts — had **429 image files generated and
correctly placed on disk**, and not one of them was visible anywhere in the
program. They were never registered in `constants.WEEKDAY_THEMES`, so the
dial's picker did not know they existed, and they had no Encyclopedia topic.
The prompt-sheet round that produced them wrote "two wiring rounds left for
later" into [Prompt Coverage](research/prompts/COVERAGE.md) and moved on.
Later never came, and nothing in the suite could say so.

**Approving a theme commits FOUR deliverables, and they ship TOGETHER:**

1. **The prompt sheet** — the art briefs.
2. **The Encyclopedia articles AND the hover blurbs** — every seat, the dual
   page, the ninth, the theme title.
3. **The dial wiring** — every config table (the full list is the PER-CAST
   CHECKLIST in [Work Plan](WORKPLAN.md) §The Theme Backlog).
4. **The Encyclopedia seat** — a card in a whole, reachable from Home.

**A round that ships only the sheet MUST, in the same commit, record its own
debt in the STAGING LEDGER** ([Theme Staging](research/theme_staging.md)):
which cast, what art exists, what it still owes, which session owes it.
Deferring is allowed; deferring SILENTLY is not.

**Enforced, not merely written** (`tests/test_theme_completeness.py`): no
registered theme may be textless, and no theme folder under `assets/weeks/`
may exist without being either registered or listed in the staging ledger. A
future round that generates art and walks away fails the suite in the same
session that did it.

---

## Project Deltas (these TIGHTEN the root rules)

- **MD-first also for NEW files:** create the component's `__about/` doc
  (purpose, connections) BEFORE creating the script, not only when modifying
  existing ones.
- **Translation policy (owner 2026-07-16): NO Serbian translation during
  development.** Texts churn — translating unfinished text is write-then-delete
  waste. Sessions write ENGLISH ONLY (new UI keys may ship untranslated;
  English is the documented fallback). The SR bundle is brought to full
  coverage in ONE dedicated TRANSLATION session immediately before a
  build/release (see [Work Plan](WORKPLAN.md)).
- **Accuracy > speed:** this is an astronomical instrument — a slow correct
  answer beats a fast plausible one; pin every fixed behavior with a golden
  test before relying on it.
- **Resource economy, stricter than root:** expensive orchestration has burned
  session limits TWICE on this project. Multi-agent workflows only when the
  owner asks, or once per milestone (a single review at milestone end — never
  per-change), bounded: at most 3 finder agents, at most 1 verifier per
  finding, and verify only findings that would change code. **`opus`
  verification only for astronomy math and rendering geometry.**

---

## Owner's Design Notes Inbox

The owner drops free-form specs into the gitignored `UV/` folder (and the
legacy `INSTRUCTION.txt`) at the project root. Read them at session start,
treat them as product decisions, fold them into the proper docs/config — and
keep the owner's own files untouched.

Current standing decisions from it: Sun body is 1.20× the other weekday
bodies; dial pointer skin variants planned for M5 — hexa (solstices only,
default), cross (solstices + equinoxes), octa (8-point).
