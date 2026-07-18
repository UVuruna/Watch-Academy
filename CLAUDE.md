# CLAUDE.md — DOMY Watch

Project-specific guidance for Claude Code. **Inherits ALL rules from the
monorepo root [CLAUDE.md](../../CLAUDE.md)** (mandatory workflow, Rules
#1–#14, markdown guidelines, version/commit system, build pipeline,
py-spy profiling) — read that first; only deltas and project facts live
here.

---

## Project Facts (never re-derive these)

- **Product:** transparent frameless 24h desktop clock widget, Windows 11,
  Python 3.13 + PySide6 6.10 + astral 3.2 (+ tzdata).
- **Dial convention:** degrees CLOCKWISE from TOP; 12:00 noon top, 00:00
  midnight bottom, 18:00 right, 06:00 left; `DIAL_OFFSET_DEG = 180`.
  Hour hand = 1 rev/24h, minute hand = 1 rev/h, NO seconds hand.
- **Hexagram:** top vertex ALWAYS points at true solar noon; rotation
  `(noon_secs − 43200)/240` deg, positive = clockwise (west-in-zone/DST).
  Weekday diamond slots ROTATE WITH the hexagram.
- **Year wheel:** piecewise-linear between the six season anchors from
  `Database/seasons_utc.json` — every season spans exactly 90° even though
  real durations differ (owner spec); equinoxes exactly at 90°/270°.
- **Architecture:** one-way flow `config → core (pure, no Qt, no wall
  clock) → data → skins → render → app`; purity is enforced by
  `tests/test_purity.py` (AST-based).
- **Verification:** `python -m pytest tests` (golden values: Belgrade DST
  −4.17°→+10.76°, Tromsø regimes, exact equinoxes, moon 0.7400 on
  2026-07-07, mockup day 20.6.2025 sunrise 04:52/sunset 20:27/noon 12:39);
  `python -m core --city NAME --at ISO` for eyeballing any moment;
  the GUI drive recipe lives in `.claude/skills/verify/SKILL.md`.
- **Win+D ground truth (verified):** the OS raises the desktop layer above
  ALL windows (TOPMOST included), no Qt events arrive — do not chase this
  as a bug; WorkerW glue is the only workaround (optional, M4).
- **Milestones:** M1 shell ✓, M2 computation core ✓, M3 living dial ✓,
  M4–M6 goals absorbed along the way (hardening, skin system,
  settings/picker); what remains to release is [Roadmap](ROADMAP.md),
  and the SESSION ORDER with per-session reading lists and model
  tiers is [Work Plan](WORKPLAN.md) — when the owner names a
  session, run it as written there.
- **Canon:** the seating doctrine — the color–virtue–vice–mood web,
  the two rosters, duals, ninths, pointer archetypes — is
  [The DOMY Canon](CANON.md); read it BEFORE any theme, roster or
  article work.

## Project Deltas to the Root Rules

- **MD-first also for NEW files:** create the component's `.md`
  (purpose, connections) BEFORE creating the script, not only when
  modifying existing ones.
- **Translation policy (owner 2026-07-16): NO Serbian translation
  during development.** Texts churn — translating unfinished text is
  write-then-delete waste. Sessions write ENGLISH ONLY (new UI keys
  may ship untranslated; English is the documented fallback). The SR
  bundle is brought to full coverage in ONE dedicated TRANSLATION
  session immediately before a build/release (see WORKPLAN).
- **Accuracy > speed:** this is an astronomical instrument — a slow
  correct answer beats a fast plausible one; pin every fixed behavior
  with a golden test before relying on it.
- Communicate in Serbian (Latin); everything in files stays English.

---

## Resource Economy — Stricter Deltas to Root Rule #15

Model economy is now root Rule #15 (inline default, haiku/sonnet/opus
tiering, reuse, tight scoping, one workflow at a time). Because expensive
orchestration has burned session limits TWICE on this project, STRICTER
caps apply here:

- **Multi-agent workflows only when the owner asks, or once per
  milestone** (a single review at milestone end — never per-change),
  bounded: at most 3 finder agents, at most 1 verifier per finding, and
  verify only findings that would change code (doc nits are just fixed).
- **`opus` verification only for astronomy math and rendering geometry.**

---

## Owner's Design Notes Inbox

The owner drops free-form specs into `INSTRUCTION.txt` (and similar files)
in the project root. Treat them as product decisions: fold them into the
proper docs/config, record them in the session memory, and keep the file
untouched (it is the owner's scratchpad, not project documentation).
Current standing decisions from it: Sun body is 1.20× the other weekday
bodies; dial pointer skin variants planned for M5 — hexa (solstices only,
default), cross (solstices + equinoxes), octa (8-point).
