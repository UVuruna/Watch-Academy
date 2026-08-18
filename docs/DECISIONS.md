# Decisions — the owner's sealed verdicts, dated

Every entry is a decision the owner made, with the date he made it. They are
NOT restated in `CLAUDE.md`; that file carries only the standing laws. Read
the entry that touches your job before you argue with the shape of the tree.

Sibling docs: [Art Pipeline](ART-PIPELINE.md) · [The Dial](DIAL.md) ·
[Enforcement](ENFORCEMENT.md) · [Runtime Notes](RUNTIME-NOTES.md)

Superseded plans, kept for the record: [Apply The Three-Folder
Migration](archive/RESTRUCTURE-APPLY.md) · [The Theme
Registry](archive/THEME-REGISTRY.md) · [The Structural
Arc](archive/WORKPLAN-STRUCTURE.md)

<a id="three-folder"></a>

## THE THREE-FOLDER MIGRATION (ballot verdict 2026-08-12)

One repo, three top-level folders: `desktop/` (all existing Python),
`shared/` (`assets/` + `Database/` + `research/` — the truth both platforms
consume and the briefs that make it), `android/` (the future Kotlin phone
edition). Every desktop command runs from `desktop/` unless stated
otherwise; every `assets/`/`Database/` path is `shared/assets/`,
`shared/Database/`. `.claude/` stayed at the TRUE repo root — it did not
move into `desktop/`.

The application was moved out of `Gadgets/` and its folder name joined into
one word on 2026-08-11 by the owner's order: the folder is
`Applications/WatchAcademy/`, the product still reads "Watch Academy"
everywhere a person sees it. Repo: `UVuruna/Watch-Academy`. **DOMY** is the
name of the dial, not of the app — `test_old_name.py` holds that line.

<a id="research-move"></a>

## THE RESEARCH MOVE (ballot verdict 2026-08-14)

`research/` is **`shared/research/`**, never `desktop/research/`. His own
reasoning, and the rule to apply to the next such question — research is
where things are INVESTIGATED and MADE, not a part that serves the running
application. His sealed wording, kept verbatim because the next round is
judged against HIS sentence:

<!-- lang-ok: the owner's own verdict, quoted -->
*"research bi trebao da bude folder gde istražujemo stvari ili pravimo
stvari, a ne deo koji služi za rad aplikacije."*

Verified, not assumed: no runtime module reads it. The prompt sheets make
`shared/assets/`, and `research/ephemeris/` is read ONLY by the build-time
generators `setup/make_deep_time.py` and `setup/make_observatory.py`, which
write `shared/Database/`. Same one-way shape as masters → bakery → assets.

Consequences:

- the 26 Star Wars reference stills moved out of `UV/` to sit beside their
  sheet at `shared/research/prompts/starwars/sw_reference/` — still
  gitignored (third-party film frames), their `←` paths now relative to the
  sheet itself;
- two migration leftovers were deleted with it: the root `Database/` (a
  byte-identical, month-older orphan of `shared/Database/deep_time.sqlite`,
  unreachable since `paths.database_dir()` resolves under `shared/`) and the
  root `tests/run_guards.py` shim.

## The Illustrator masters (decree 2026-08-13)

The `.ai` files are the owner's working files, not the program's; they live
in `UV/illustrator/` and their 240 MB of blobs were stripped from git
history. `desktop/illustrator/` no longer exists — do not recreate it.

## Translation policy (2026-07-16) — NO Serbian translation during development

Texts churn, and translating unfinished text is write-then-delete waste.
Sessions write ENGLISH ONLY; new UI keys may ship untranslated (English is
the documented fallback). The SR bundle is brought to full coverage in ONE
dedicated TRANSLATION session immediately before a build/release — see
[Work Plan](../WORKPLAN.md).

## Accuracy beats speed

This is an astronomical instrument: a slow correct answer beats a fast
plausible one. Pin every fixed behaviour with a golden test before relying
on it.

## Resource economy, stricter than the constitution

Expensive orchestration has burned session limits TWICE on this project.
Multi-agent workflows only when the owner asks, or once per milestone (a
single review at milestone end — never per change), bounded: at most 3
finder agents, at most 1 verifier per finding, and verify only findings that
would change code. `opus` verification only for astronomy math and rendering
geometry.

## MD-first also for NEW files

Create the component's `__about/` doc (purpose, connections) BEFORE creating
the script, not only when modifying an existing one.

## Milestones and the arcs still open

M1 shell ✓, M2 computation core ✓, M3 living dial ✓; M4–M6 were absorbed
along the way. What remains to release is [Roadmap](../ROADMAP.md); the
SESSION ORDER with per-session reading lists and model tiers is [Work
Plan](../WORKPLAN.md) — when the owner names a session, run it as written
there.

**The Android arc (verdicts 2026-08-11):** the phone edition is **Pocket
Watch**; its sealed decisions, the bakery/CONTRACT PACK, the base pack
agreement and THE PARITY LAW live in [Android Charter](../ANDROID.md). Read
it before any phone-related work. Phase 1 (the bakery) happens in THIS repo.

## Standing decisions from the `UV/` inbox

The owner drops free-form specs into the gitignored `UV/` folder (and the
legacy `INSTRUCTION.txt`) at the project root. Read them at session start,
treat them as product decisions, fold them into the proper docs/config — and
leave his own files untouched.

Current standing items: the Sun body is 1.20× the other weekday bodies; dial
pointer skin variants are planned for M5 — hexa (solstices only, default),
cross (solstices + equinoxes), octa (8-point).
