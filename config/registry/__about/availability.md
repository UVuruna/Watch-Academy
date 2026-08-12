# The Availability Field

**Script:** [Availability (script)](../availability.py)

## Purpose

Which `WEEK` themes ship unlocked in the base pack, and which ship
LOCKED — owner-sealed ballot verdict 2026-08-12. Every `WEEK` key
(`config/registry/week.py`) is classified exactly once, in
`AVAILABILITY`, as `"base"` or `"locked"`; nothing here is a second
list kept in sync with a first.

**The exact base set (10 keys):** `planets`, `planet_signs`,
`planets_art`, `cosmos`, `continents`, `profession`, `corporate`,
`virtues`, `sins`, `moods`. Every other `WEEK` key is `"locked"`.

**Scope, exactly as sealed.** Availability governs WEEK THEMES only.
The instrument itself, every ring preset and the whole astronomical
Encyclopedia are always-base by the EARLIER sealed verdict
([Android Charter](../../../ANDROID.md) -> Base Pack Agreement) and are
never gated here — a theme's own articles/blurbs travel WITH the
theme's lock; they are not a second thing to gate separately.

**The desktop unlock trigger (future, not built here).** The existing
`constants.HIDDEN_MODE_SECRET` typed-sequence buffer
(`app.controller.Controller._collect_secret`) already flips a
session-only "hidden mode" flag. That mechanism is untouched by this
module — it is the future trigger a later session wires to
`is_theme_unlocked(theme, all_unlocked=controller._hidden_unlocked)` so
the same secret that unlocks the Four Greetings also unlocks every
LOCKED theme at once. Nothing here builds that wiring, and nothing here
builds GUI gating (picker locks, Encyclopedia locks) — both are a later
session's consumer of this table, not this table's job.

## Connections

### Uses
- [The Week Registry](week.md) — every key it classifies

### Used by
- [Registry derivation](__init__.md) — exposes `base_theme_keys()` and
  `is_theme_unlocked()` on the package's public surface
- *(future)* the picker and the Encyclopedia's lock UI — not built in
  this session, see Purpose above

### Related
- [Android Charter](../../../ANDROID.md) — the earlier sealed verdict
  that keeps the instrument, ring presets and astronomical Encyclopedia
  always-base
