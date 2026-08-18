# Runtime notes — verified ground truth and closed root causes

Facts established by measurement or by a bug that was actually solved. Do not
re-investigate them; do not let a later regression hide behind them. Sibling
docs: [Decisions](DECISIONS.md) · [The Dial](DIAL.md) ·
[Enforcement](ENFORCEMENT.md)

## Verification and golden values

`python -m pytest tests` from inside `desktop/`. Golden values the suite
pins: Belgrade DST −4.17° → +10.76°, the Tromsø regimes, exact equinoxes,
moon 0.7400 on 2026-07-07, mockup day 20.6.2025 sunrise 04:52 / sunset 20:27
/ noon 12:39.

**The full suite takes ~18 minutes.** Run a targeted subset while working and
the full suite before committing. `python -m core --city NAME --at ISO` (from
`desktop/`) eyeballs any moment; the GUI launch/drive recipe is
`.claude/skills/verify/SKILL.md`.

## Clock jumps (owner bug 2026-08-06 — root cause recorded)

A `WM_TIMECHANGE` is BROADCAST to every top-level window and Qt runs it
through EVERY installed native filter, so N watches saw one SYNC as N² wakes.
The filter is app-scoped and must be uninstalled in `_teardown_windows`.

**A clock jump is not a new day** — it rebuilds the day context but must
never start the hover sweep.

The dev machine now syncs hourly (`w32time` Automatic, `SpecialPollInterval`
3600), so a jump big enough to cross `CLOCK_JUMP_THRESHOLD_S` is rare here.
Do not let that hide a regression; `desktop/tests/test_sync_freeze.py` is the
tooth.

## Win+D ground truth (verified, Win11 24H2)

The OS raises the desktop layer above ALL windows, TOPMOST included, and no
Qt events arrive. Nothing window-level restores visibility until Show Desktop
mode ends. Do not chase this as a bug; WorkerW glue is the only workaround
(optional, M4).
