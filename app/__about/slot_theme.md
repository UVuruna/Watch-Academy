# Slot Theme

**Script:** [Slot Theme (script)](../slot_theme.py) · **Flow:** [diagram](../__flow/slot_theme.md)

## Purpose
The mini window replacing the three old 1st/2nd/3rd Slot submenu chains
(R5 MENU REWORK item 3C): three medal icons pick WHICH slot is being
edited (the active one highlighted); below it, that slot's full option
set — the shared [Weekday Theme Grid](weekday_theme_grid.md),
Complications, Astrology, Ascendant and Chinese Zodiac — in tabs.
Enabling/disabling a slot itself is NOT here (that is the `Ctrl+N`
shortcut cycling 0→1→2→3→0) — a 2nd/3rd medal is simply disabled until
its slot exists.

## Connections

### Uses
- [Weekday Theme Grid](weekday_theme_grid.md) — the active slot's
  Weekday tab
- [Theme](theme.md) — `apply_theme`, `size_to_screen`, the tab pill styling
- [Config (folder)](../../config/___config.md) — `constants.SLOT_COMPLICATION_TITLES`,
  `ZODIAC_SLOT_STYLES`, `CHINESE_SLOT_STYLES`

### Used by
- [Watch Controller](controller.md) — `_open_slot_theme` (non-modal, one
  live instance, raised on a second open) builds one `SlotDescriptor`
  per slot from the live settings and re-supplies a fresh triple after
  every pick

## Classes

### SlotDescriptor (dataclass)
One slot's full config plus its own setter callables — `index`, `title`,
`mode_value`, `style_value`, `theme_value`, `roster_value`,
`names_value`, `enabled_value`, `set_mode`, `set_style_mode`,
`set_weekday`, `set_names`.

### SlotThemeDialog(QDialog)
Non-modal, LIVE-APPLY (same justification as [Pointer
Theme](pointer_theme.md)): every option here already applied instantly
in the old menu, so a pick calls its descriptor's setter immediately.

#### Methods
- `_build()`: rebuilds the medal row (one button per descriptor,
  disabled when that slot is off) and the active slot's tab content
  (Weekday / Complications / Astrology / Ascendant / Chinese zodiac +
  a Names checkbox)
- `_select(index)`: switches the active slot and rebuilds
- `refresh(descriptors)`: re-supplies the triple after a pick applies —
  called by the controller
- `set_gate(available, reason)`: grays the whole window in place if it
  happens to be open when the LAST slot turns off — reads each
  descriptor's own `enabled_value` (never a widget's current
  `isEnabled()`, which this method may have already flipped) so a later
  `set_gate(True, ...)` restores exactly the right icons
