# Slot Theme

**Script:** [Slot Theme (script)](slot_theme.py)

## Purpose

The mini WINDOW replacing the three old 1st/2nd/3rd Slot submenu chains
(R5 MENU REWORK item 3C, owner spec: "3 Ikone za 1st, 2nd, 3rd i Koja je
obojena ta je prikazana tj za nju mozemo da biramo — komplikacije,
weekday teme, astrologija... sve"): three medal icons pick WHICH slot
is being edited (the active one highlighted); below it, that slot's
full option set — the shared [Weekday Theme Grid](weekday_theme_grid.md),
Complications (Digital Time / Date / Day length / Seconds), Astrology,
Ascendant and Chinese Zodiac — in tabs.

Enabling/disabling a slot itself moved OFF this window (owner spec item
2's `cycle_slots` shortcut, Ctrl+N, cycles 0→1→2→3→0 through the SAME
1→2→3 chain the app already enforces) — so a 2nd/3rd medal here is
simply disabled (not clickable) until its slot exists; the window's
top-level menu entry itself grays when NO slot is visible at all
(`not Settings.show_weekday`), the bootstrapping case the shortcut
exists to solve.

## Connections

### Uses
- [Weekday Theme Grid](weekday_theme_grid.md) — the active slot's
  Weekday tab.
- [Theme](theme.md) — `apply_theme`, `size_to_screen`, the new
  `QTabWidget`/`QTabBar` pill styling (added this round).
- [Config (folder)](../config/___config.md) —
  `constants.SLOT_COMPLICATION_TITLES`, `ZODIAC_SLOT_STYLES`,
  `CHINESE_SLOT_STYLES`.

### Used by
- [Controller](controller.md) — `_open_slot_theme` (non-modal, one live
  instance, raised on a second open) builds one `SlotDescriptor` per
  slot from the live settings (`_slot_descriptors`) and re-supplies a
  fresh triple after every pick, so the window's content follows the
  live state without closing.

## Classes

### SlotDescriptor
A plain data bundle (`index`, `title`, the slot's current mode/style/
theme/roster/enabled — and its OWN setter callables, `set_mode` /
`set_style_mode` / `set_weekday` / `set_names`) — the SAME shape the
old `build_slot_menu` closure passed around, now crossing a module
boundary instead of staying a local closure.

### SlotThemeDialog
Non-modal, LIVE-APPLY (same justification as
[Pointer Theme](pointer_theme.md): every option here already applied
instantly in the old menu). `refresh(descriptors)` re-supplies the
triple after a pick (called by the controller); `set_gate(available,
reason)` grays the whole window in place if it happens to be open when
the LAST slot turns off.
