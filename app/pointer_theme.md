# Pointer Theme

**Script:** [Pointer Theme (script)](pointer_theme.py)

## Purpose

The mini WINDOW replacing the old 1st Slot ▸ Weekday submenu chain (R5
MENU REWORK item 3B, owner spec: "sve ove teme koje imamo raspoređeni
po srodnosti kao i do sada ali sada u lepsem vecem meniju sa slikama i
tekstom"): picks the weekday-BODY theme the star pointer's own arms
wear (`Settings.weekday_theme`, the 1st Slot's default "weekday" mode)
— image + name, grouped by kinship, in the shared
[Weekday Theme Grid](weekday_theme_grid.md).

**Interpretation note (agent judgment, flagged for owner confirmation):**
the owner's spec names this window "Pointer theme" without pinning
exactly which setting it edits. The 1st Slot's own weekday-body layer
is the one thing actually drawn ON the pointer's arms, so that is what
this window edits; the FULLER per-slot picture — which MODE a slot
runs (weekday / complications / astrology / ...) and its roster/metal
— lives in [Slot Theme](slot_theme.md) instead, which also reaches the
SAME weekday grid for whichever slot is selected there. See
`app.controller.watch_title`'s sibling doubt list in the round report
for the alternative reading if this guess is wrong.

## Connections

### Uses
- [Weekday Theme Grid](weekday_theme_grid.md) — the shared image+name
  picker.
- [Theme](theme.md) — `apply_theme`, `size_to_screen`.

### Used by
- [Controller](controller.md) — `_open_pointer_theme` (non-modal, one
  live instance, raised on a second open); `_refresh_menu_gating` grays
  the top-level "Pointer Theme…" entry AND live-grays this window's own
  grid while it is open.

## Classes

### PointerThemeDialog
Non-modal (`.show()`), LIVE-APPLY (owner justification: every option
this window absorbs already applied the instant you clicked it in the
old menu — turning that into a transactional OK/Cancel flow would be a
silent behavior change nobody asked for). A tile click calls the
controller's `on_pick(theme)` immediately; `refresh()` rebuilds the
grid so the newly active tile's border moves without closing the
window. `set_gate(available, reason)` grays the grid in place and shows
a banner when the picker becomes unavailable (Archetype mode ON, the
Pointer element hidden in Visible, or the 1st Slot off) while the
window is already open.
