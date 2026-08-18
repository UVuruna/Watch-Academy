# Shared

**Script:** [Shared (script)](../_shared.py)

## Purpose
`Shared` — THE ONE COPY RULE's mechanism, written once.

The project law: every bundled book and database is loaded ONCE per
process and reached through its `shared_*` accessor, and app code never
constructs a repository class. The law was kept; its four-line mechanism
was retyped eight times, once per repository, with two variations that
kept the copies just different enough to keep copying — the Encyclopedia
and the Symbolism book hold one copy PER LANGUAGE, and the Deep Time
pack may legitimately resolve to None, which forced a second `_DETECTED`
flag beside the cell so "absent" would not be re-detected forever ([OOP
audit](../../../docs/AUDIT-OOP-2026-08-18.md), section 1).

## Connections

### Uses
- nothing — pure Python, no Qt, no wall clock, no I/O of its own

### Used by
- [Deep Time](deep_time.md) · [Encyclopedia](encyclopedia.md) ·
  [Locations](locations.md) · [Moon Phases](moon_phases.md) ·
  [Observatory](observatory.md) · [Seasons](seasons.md) ·
  [Symbolism](symbolism.md) — each keeps its own named `shared_*`
  accessor and holds one `Shared` behind it
- [Assets](../../render/__about/assets.md) — `shared_cache()`, the
  process-wide rasterized-image cache; the same rule for RAM rather
  than for a book

## Design Decisions
- **The named accessors stay.** `shared_seasons()`,
  `shared_encyclopedia(language)` and the rest ARE the law's public
  door and each carries its own history in its docstring; what moved is
  only the four lines of mechanism underneath. A single generic
  `shared(Repository)` at every call site would have deleted that
  history and let app code name a repository class again — the exact
  thing the law forbids.
- **MEMBERSHIP decides, not `is None`.** A copy that is legitimately
  None — the Deep Time pack when it is not installed — is remembered as
  such, so the `_DETECTED` flag `deep_time.py` needed beside its cell
  is gone rather than generalised.
- **`kwargs` are honored on the FIRST ask only**, which is what
  `shared_seasons(deep=...)` and `shared_moon_phases(deep=...)` already
  documented. Making later calls re-apply them would mean rebuilding
  the copy, which is the opposite of the rule.
- **No locking.** These are built on the GUI thread during startup and
  read everywhere afterwards; the previous eight hand-written versions
  had no lock either, and adding one here would be a behaviour change
  wearing a refactor's clothes.
