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
  disk is `Applications/WatchAcademy/` — moved out of `Gadgets/` and joined
  into one word on 2026-08-11 by the owner's order (the folder name carries
  no space; the product name still reads "Watch Academy" everywhere a person
  sees it). Repo: `UVuruna/Watch-Academy`.
- **Dial convention:** degrees CLOCKWISE from TOP; 12:00 noon top, 00:00
  midnight bottom, 18:00 right, 06:00 left; `DIAL_OFFSET_DEG = 180`.
  Hour hand = 1 rev/24h, minute hand = 1 rev/h, NO seconds hand.
- **Hexagram:** top vertex ALWAYS points at true solar noon; rotation
  `(noon_secs − 43200)/240` deg, positive = clockwise (west-in-zone/DST).
  Weekday diamond slots ROTATE WITH the hexagram.
- **Year wheel:** piecewise-linear between the six season anchors from
  `shared/Database/seasons_utc.json` — every season spans exactly 90° even
  though real durations differ (owner spec); equinoxes exactly at 90°/270°.
- **Architecture:** one-way flow `config → core (pure, no Qt, no wall clock)
  → data → skins → render → app`; purity is enforced by
  `desktop/tests/test_purity.py` (AST-based, covers `core`, `data`, `recolor`).
- **Render structure (since 0.14.688):** `render/context.py` is the layer
  protocol, the geometry/painting modules beside it are the shared
  vocabulary, `render/layers/` holds one module per paint layer, and
  `render/compositor.py` stacks them. `render/layers.py` no longer exists —
  never import from it.
- **THE THREE-FOLDER MIGRATION (owner ballot verdict 2026-08-12):** one
  repo, three top-level folders — `desktop/` (all existing Python),
  `shared/` (assets/ + Database/ + research/, the truth both platforms
  consume and the briefs that make it), `android/` (the future Kotlin
  phone edition). Every command below runs
  from `desktop/` (`cd desktop` first) unless stated otherwise; every
  `assets/`/`Database/` path is `shared/assets/`/`shared/Database/`.
- **THE RESEARCH MOVE (owner ballot verdict 2026-08-14):** `research/`
  is **`shared/research/`**, never `desktop/research/`. The owner's own
  reasoning, and it is the rule to apply to the next such question:
  research is the folder where things are INVESTIGATED and MADE, not a
  part that serves the running application. His sealed wording, kept
  verbatim because the next round is judged against HIS sentence:
  <!-- lang-ok: the owner's own verdict, quoted -->
  *"research bi trebao da bude folder gde istražujemo stvari ili pravimo stvari, a ne deo koji služi za rad aplikacije."*
  Verified, not assumed: no runtime module reads it — the prompt
  sheets make `shared/assets/`, and `research/ephemeris/` is read ONLY
  by the build-time generators `setup/make_deep_time.py` and
  `setup/make_observatory.py`, which write `shared/Database/`. Same
  one-way shape as masters → bakery → assets. Consequences:
  **(a)** the 26 Star Wars reference stills moved out of `UV/` to sit
  beside their sheet at `shared/research/prompts/starwars/sw_reference/`
  — still gitignored (third-party film frames), and their `←` paths are
  now relative to the sheet itself.
  **(b)** two migration leftovers were deleted with it: the root
  `Database/` (a byte-identical, month-older orphan of
  `shared/Database/deep_time.sqlite`, unreachable since
  `paths.database_dir()` resolves under `shared/`) and the root
  `tests/run_guards.py` shim.
- **THE MASTERS PREFIX (owner ballot verdict 2026-08-14):** a prompt
  sheet's drop path names where a GENERATION LANDS, so it reads
  `masters/…` — never `assets/…`, which named a folder that existed
  nowhere in the repo once THE ART BAKERY was born, leaving
  PromptPainter with no folder its owner could select. **Its Output
  field is the repo root**; the sheet's own path supplies the rest.
  1,475 paths across 66 sheets were rewritten; the tooth is
  `tests/test_prompt_paths.py`, which now reads the `masters/`
  convention and reduces both prefixes to one canonical form (the
  bakery mirrors the trees name for name), while still checking
  folder existence against `shared/assets/` so a clone without
  `masters/` grades the same.
- **THE HALF-GOVERNED AREA (owner verdict 2026-08-14):** the bakery
  claims the top-level names under `masters/` — EXCEPT those in
  `make_art_bake.DEEP_GOVERNED_ROOTS`, where authority is claimed one
  level deeper. `instrument` is the only member and must stay one:
  `shared/assets/instrument/` also holds the 57 letter plates of THE
  ONE PLATE LAW plus guide/hands/icons/ring — ~147 files no master
  will ever claim — so whole-area governance would make every one of
  them a stray, hold `--check` red forever, and let a single
  `--prune-strays` delete the program's alphabet. `VERBATIM_SUBTREES`
  does NOT protect against this: it exempts from re-encoding, not from
  the prune.
- **THE ART BAKERY (owner decree 2026-08-12) — there are now FOUR
  top-level folders, and the fourth is not in git.** `masters/` is the
  owner's gitignored inbox: every research prompt writes its
  full-resolution output there and nothing else ever reads it except
  `desktop/setup/make_art_bake.py`, which downscales to the area's
  `WORKING_SET_CEILINGS` entry and re-encodes to WebP q90 into
  `shared/assets/` — the small, committed tree BOTH platforms read.
  Consequences to hold in mind, all of them load-bearing:
  **(a)** never edit art under `shared/assets/`; edit the master and
  re-run `python -m setup.make_art_bake` (incremental, keyed by the
  master's sha256 in `shared/assets/_bake_manifest.json`).
  **(b)** the shipped art is `.webp`; every config table still names the
  canonical `.png` and `paths.art_file` does the translation — it is the
  single door, do not add a second.
  **(c)** never write `rglob("*.png")` over the assets tree — use
  `paths.art_files_under` / `paths.is_art_file`, because a `*.png` glob
  now matches NOTHING in the baked areas and would pass a guard in
  silence.
  **(d)** `_baked/letters/` is lossless WebP of the EAGER roster only
  (`defaults.EAGER_BAKED_SHADES`, 17 of the 34 pairs); the rest derive
  at runtime as they always could.
  **(e)** a clone without `masters/` is a complete, working program —
  that is the whole point.
  **(f) THE SYNC FLOW (owner order 2026-08-13):** a bake run
  RECONCILES before it bakes — a master taken away takes its shipped
  file and its manifest entry with it, and an emptied folder goes too.
  The prune's reach is exactly the top-level names that exist under
  `masters/` (`governed_subtrees`), never `instrument/letters` or
  anything else the bakery did not make; an unclaimed file inside a
  governed area is REPORTED, and only `--prune-strays` deletes it.
  `--check` is the build gate: writes nothing, exits non-zero on
  drift, called first thing by `setup/make_contract_pack.py` and by
  every future build. The arrow is still one-way — nothing is ever
  written back into `masters/`.
- **The Illustrator masters (owner decree 2026-08-13):** the `.ai`
  files are the owner's working files, not the program's; they live in
  `UV/illustrator/` and their 240 MB of blobs were stripped from git
  history. `desktop/illustrator/` no longer exists — do not recreate it.
- **Verification:** `python -m pytest tests` from inside `desktop/` (golden
  values: Belgrade DST −4.17°→+10.76°, Tromsø regimes, exact equinoxes,
  moon 0.7400 on 2026-07-07, mockup day 20.6.2025 sunrise 04:52/sunset
  20:27/noon 12:39). **The full suite takes ~18 minutes** — run a targeted
  subset while working and the full suite before committing.
  `python -m core --city NAME --at ISO` (from `desktop/`) eyeballs any
  moment; the GUI drive recipe is `.claude/skills/verify/SKILL.md`.
- **THE RING VOCABULARY (owner 2026-08-07 — "JEWELS != NUMERALS", learn
  it once):** the ring band carries FOUR different things and they are
  not variations of each other. Never reason about one as though it were
  another.
  | Term | What it is | How many | How it is drawn |
  |------|-----------|----------|-----------------|
  | **JEWELS** | the letters/glyphs seated on the outer's EMPTY fields | depends on the OUTER mode: full 1, the crosses 4, hexa 6, octa 8 | PLATES |
  | **NUMERALS** | the hour numbers 1–23 filling every seat no jewel took | the rest of the 24 | COMPUTED, and **even/odd wear two different styles** — even is white on a grey border, odd the reverse (`palette.NUMERAL_PARITY_COLORS`). That alternation is the DESIGN, not a defect |
  | **MINUTES** | the inner band's five-minute numbers | per inner variant | COMPUTED, its own face roster |
  | **CROWN** | everything outside the band — its text, the location, the live time | per preset | PLATES |
- **THE ONE PLATE LAW (owner decree 2026-08-07):** everything drawn from
  the PLATE library — the jewels, the whole crown, the duals — is one of
  the owner's plates in `shared/assets/instrument/letters/` (latin, greek,
  numerals, symbols, emblems), taken as the GOLD master and recolored by
  the transformer into one of this app's metals or thematic colours. One
  style, one source, one algorithm: never a font, never a flat colour of
  its own. (The NUMERALS and MINUTES bands are the other half of the
  vocabulary above — computed, with their own face rosters, relief and
  the even/odd parity. They are not exceptions to this law; they are a
  different thing.) `render.letter_plates` is the single door — Greek
  twins alias onto the Latin plate, two-digit numbers compose from the
  digit plates at a uniform INK clearance — and a glyph with no plate
  RAISES rather than falling back, because that fallback is how a whole
  missing digit alphabet once shipped as a font-drawn crown with every
  test green. Tooth: `tests/test_letter_plates.py`.
- **THE ONE COPY RULE (owner 2026-07-28, extended 2026-08-06):** the
  only things that may differ between two watches are the OBSERVER
  (location/timezone) and the VISUAL picks. Every bundled book and
  database is loaded ONCE per process — `render.assets.shared_cache`,
  `data.symbolism.shared_symbolism` / `data.encyclopedia.
  shared_encyclopedia` (one per LANGUAGE), `shared_seasons`,
  `shared_moon_phases`, `shared_deep_time`, `shared_observatory`, and
  the memoized bundled halves of `ring_presets()` / `hand_packs()`.
  Never construct those repository classes directly in app code.
- **Clock jumps (owner bug 2026-08-06, root cause recorded):** a
  WM_TIMECHANGE is BROADCAST to every top-level window and Qt runs it
  through EVERY installed native filter, so N watches saw one SYNC as
  N² wakes; the filter is app-scoped and must be uninstalled in
  `_teardown_windows`. **A clock jump is not a new day** — it rebuilds
  the day context but must never start the hover sweep. The dev machine
  now syncs hourly (`w32time` Automatic, `SpecialPollInterval` 3600),
  so a jump big enough to cross `CLOCK_JUMP_THRESHOLD_S` is rare here —
  do not let that hide a regression; `tests/test_sync_freeze.py` is the
  tooth.
- **Win+D ground truth (verified):** the OS raises the desktop layer above
  ALL windows (TOPMOST included), no Qt events arrive — do not chase this
  as a bug; WorkerW glue is the only workaround (optional, M4).
- **Milestones:** M1 shell ✓, M2 computation core ✓, M3 living dial ✓,
  M4–M6 absorbed along the way. What remains to release is
  [Roadmap](ROADMAP.md); the SESSION ORDER with per-session reading lists
  and model tiers is [Work Plan](WORKPLAN.md) — when the owner names a
  session, run it as written there.
- **Android arc (owner verdicts 2026-08-11):** the phone edition is
  **Pocket Watch** — its sealed decisions, the bakery/CONTRACT PACK, the
  base pack agreement and THE PARITY LAW live in
  [Android Charter](ANDROID.md); read it before any phone-related work.
  Phase 1 (the bakery) happens in THIS repo.
- **Canon:** the seating doctrine — the color–virtue–vice–mood web, the two
  rosters, duals, ninths, pointer archetypes — is [The DOMY Canon](CANON.md);
  read it BEFORE any theme, roster or article work. The philosophical core
  (the three-axis Character Cube, the Double Trinity, the Two Crosses, the
  Rose, naming and the writing laws) is [The Cube Canon](CUBE.md) — read it
  BEFORE any character, path, archetype-wheel or naming work.

---

## Enforcement Installed Here

The four guard tests of [Code Rules](../../rules/CODE.md) → Enforcement live
in `desktop/tests/`, wired into `.claude/settings.json` hooks (`.claude/`
stays at the TRUE repo root per THE THREE-FOLDER MIGRATION, above; its hook
commands run relative to the repo root, hence the `desktop/` prefix)
(`PostToolUse` → `python desktop/tests/run_guards.py --fast`,
`Stop` → `python desktop/tests/run_guards.py`; exit 2 blocks):

| Guard | Fails on |
|-------|----------|
| `desktop/tests/test_structure_law.py` | any `.py` over ~1,000 lines outside the RATCHET |
| `desktop/tests/test_config_sections.py` | post-definition patching, duplicate dict keys, or a definition above the first section banner, in any `config/*.py` |
| `desktop/tests/test_docs_coverage.py` | a source file missing the docs its tier requires, a legacy beside-script doc, or an orphan doc |
| `desktop/tests/test_doc_links.py` | a broken relative `.md` link, or a doc unreachable from `README.md` |

Two project-specific guards sit beside them and are NOT part of the standard
four: `desktop/tests/test_config_cohesion.py` (pins Session 36's config
split — every `config/*.py` at or under the threshold, and no moved name
still reachable through `defaults`) and
`desktop/tests/test_theme_completeness.py` (below).

GUI work here is also governed by the Zubi v2 Algorithmic Teeth & Grader v2
([GUI Rules](../../rules/GUI.md#zubi-v2)) — status: **installed**,
`desktop/tests/layout_checks_qt.py`.

**The RATCHET may only SHRINK.** Adding an entry needs the owner's explicit
approval in that same session.

**THE ZUBI BASELINE RATCHET (owner approval 2026-08-09):** the runtime
layout audit (`desktop/tests/test_layout_audit.py`, part of the FULL Stop
guard) fails ONLY on findings whose normalized key is absent from
`desktop/tests/zubi_baseline.json` — the owner-frozen pre-existing backlog
(`.claude/zubi-v2-findings.md`, install-only boundary of 2026-08-08).
The baseline obeys the same ratchet law: entries may only be REMOVED as
findings are fixed; regeneration runs through
`DOMY_ZUBI_REBASELINE=1 python -m pytest desktop/tests/test_layout_audit.py -k test_layout_audit`
(from the repo root; or drop the `desktop/` prefix when run from inside
`desktop/`) and REFUSES to add keys unless `=force`, which is legal only
with the owner's explicit in-session approval.

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
later" into [Prompt Coverage](shared/research/prompts/COVERAGE.md) and moved on.
Later never came, and nothing in the suite could say so.

**Approving a theme commits FOUR deliverables, and they ship TOGETHER:**

1. **The prompt sheet** — the art briefs.
2. **The Encyclopedia articles AND the hover blurbs** — every seat, the dual
   page, the ninth, the theme title.
3. **The dial wiring** — every config table (the full list is the PER-CAST
   CHECKLIST in [Work Plan](WORKPLAN.md) §The Theme Backlog).
4. **The Encyclopedia seat** — a card in a whole, reachable from Home.

**A round that ships only the sheet MUST, in the same commit, record its own
debt in the STAGING LEDGER** ([Theme Staging](shared/research/theme_staging.md)):
which cast, what art exists, what it still owes, which session owes it.
Deferring is allowed; deferring SILENTLY is not.

**Enforced, not merely written** (`desktop/tests/test_theme_completeness.py`):
no registered theme may be textless, and no theme folder under
`shared/assets/weeks/` may exist without being either registered or listed
in the staging ledger. A
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
