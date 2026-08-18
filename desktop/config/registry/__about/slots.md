# Slots (registry)

**Script:** [Slots (script)](../slots.py)

## Purpose
`SLOT_KEYS` — the three dial slots and, for each, the `Settings` field
that holds its content mode, style, theme, roster, names and enablement,
plus its UI title.

The three slots behave identically; the only thing that differs between
them is where each answer is stored. Those field names had never been
written down: they were inlined three at a time into `if index == 1:` /
`if index == 2:` chains, and into two setter methods whose bodies the
[OOP audit](../../../../docs/AUDIT-OOP-2026-08-18.md) measured as
identical but for four strings (clones C4 and C6). Naming them once is
what lets ONE `_set_slot(index, ...)` serve all three.

## Connections

### Uses
- nothing — pure data, no imports at all

### Used by
- [Controller](../../../app/__about/controller.md) — `_set_slot` (the
  one writer), `_slot_active`, `_slot_mode_state`, `_slot_theme_state`,
  `_cycle_slot` and `_slot_descriptors`

## Design Decisions
- **The field names are historical and are NOT renamed here.** Slot 1
  is `weekday_slot`, slot 2 `octa_slot`, slot 3 `third_slot`, because
  that is what the settings files already on owners' disks say; a
  rename would silently reset everybody's dial.
- **`names` is shared between slots 2 and 3** (`show_info_slot_names`).
  The two info slots have always drawn their names together. The table
  records that rather than hiding it, so the day it becomes a product
  question there is one place to change.
- **`enabled` is the RAW field, not the effective one.** Slot 3 is only
  visible on top of slot 2, but that chain is a RULE
  (`WatchController._slot_active`), not a stored field — the Watch Face
  window's own "enabled" checkbox reads the raw value, and conflating
  the two would make the checkbox lie.
- **A dict of dicts, not a dataclass.** The consumers index it by the
  role name they already speak (`keys["theme"]`) and pass that straight
  to `getattr`/`replace`; a typed record would buy nothing here and
  cost the table its at-a-glance shape.
