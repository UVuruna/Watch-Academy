# The Theme Registry — Discussion Brief

**STATUS: OPEN PROBLEM — brainstorm with the owner FIRST (owner decree
2026-08-01).** Nothing here is implemented. This file is the agenda for a
dedicated session that designs the registry WITH the owner before any code
changes; per [Plan Rules](../../rules/PLAN.md) → Present Before Building, that
session starts by echoing this brief back and filling its open questions.

---

## The Trigger

`config/pantheon.py` derives `WEEKDAY_THEME_FILES` by rule (good — compute,
don't generate), then patches ~30 exceptions onto it AFTER the definition —
the exact pattern THE CONFIG SECTION LAW forbids. The entry sits in
`test_config_sections.py`'s `PATCHING_RATCHET` awaiting resolution. Two narrow
fixes were considered (ratify the exception; fold the exceptions into an
`OVERRIDES` table + one assignment) — **the owner set both aside in favor of a
deeper redesign**: the exceptions are a symptom of theme knowledge being
scattered, not a local formatting problem.

## The Owner's Direction (decree 2026-08-01)

**ONE registry — a single dictionary of ALL themes, grouped by KIND
(kinship):**

- **week-kind** — 9 members (7 weekdays + dual + ninth)
- **calendar-kind** — 13 members (12 + 1)
- …further kinds as the inventory reveals them

**Every member entry declares a defined set of fields** — among them: which
WEEKDAY it represents (week-kind), which MONTH (calendar-kind), and the rest
of the contract the brainstorm defines (art coverage? encyclopedia seat?
theme-file override? palette hooks?).

**The payoff:** when a future theme is added, we know UPFRONT exactly what
must be defined for it — and we know UPFRONT who reads every field. One
place, one contract, no scattering, no post-definition patching ever again.

## What the Session Must Produce

1. **Inventory** — every current theme and WHERE its member data lives today:
   `constants.WEEKDAY_THEMES`, `pantheon.py` tables + patches, the staging
   ledger, Encyclopedia wiring, the per-cast checklist (Work Plan §Theme
   Backlog). The scattering map IS the argument for the registry.
2. **The per-kind contract** — defined with the owner: what every theme MUST
   declare for its members, per kind. (This is the brainstorm core.)
3. **Registry structure** — sections per kind (Config Section Law-compliant),
   one definition, whole, in its section.
4. **Migration plan** — every derived table (including `WEEKDAY_THEME_FILES`)
   becomes COMPUTED FROM the registry in one assignment; today's ~30 patches
   become registry data; no patching remains.
5. **Consumer map** — who reads which field (dial picker, Encyclopedia,
   recolor, staging guard…), written into the registry's docs.
6. **Proof** — byte-identical derived outputs vs today (or intentionally
   changed, each with the owner's sign-off).
7. **Cleanup** — the `PATCHING_RATCHET` entry is deleted; THE THEME
   COMPLETION LAW's guard (`test_theme_completeness.py`) is re-anchored on
   the registry, so an unregistered theme folder or a textless theme fails
   the build from the registry itself.

## Open Questions for the Owner

- Which kinds exist beyond week (9) and calendar (12+1)?
- The full field list per kind — what is REQUIRED vs optional?
- Does the registry also own what the staging ledger tracks today (deferred
  deliverables), or do they stay separate?
- File placement: one `config/registry.py`, or per-kind sections in one file?
