# Dialog

**Script:** [Dialog (script)](../dialog.py) · **Flow:**
[diagram](../__flow/dialog.md)

## Purpose
THE OBSERVATORY WINDOW — the shell the charts live in: the splitter, the
chart roster, the controls, the Enlarge route, and the session-only
splitter memory. Everything that knows a WINDOW is open (R12 of the
[OOP audit](../../../../docs/AUDIT-OOP-2026-08-18.md), 2026-08-18).

## Connections

### Uses
- [Charts](charts.md) — the four plot classes and `year_label`
- [Panels](panels.md) — `ChartPane`, `EnlargeDialog`
- [Dialog Base](../../__about/dialog_base.md) — `AcademyDialog`: the
  overlay, the `tr`, the title, the stay-on-top flag
- [Observatory Data](../../../data/__about/observatory.md) ·
  [Deep Time Repository](../../../data/__about/deep_time.md) (OPTIONAL)
- [Sun (core)](../../../core/__about/sun.md) — `day_length_curve`
- [Deep Time (core)](../../../core/__about/deep_time.md)
- [Theme](../../__about/theme.md) — `size_to_screen`

### Used by
- [Watch Controller](../../__about/controller.md) — `_open_observatory()`
  opens (or raises the live) instance with the EFFECTIVE `(moment,
  observer, tz, cycles)` and the optional Deep Time pack

### `ObservatoryDialog(QDialog)`
Normal resizable, non-modal window (`WA_DeleteOnClose` — safe here,
since this dialog only ever LENDS a panel out, never has one reparented
INTO it). A `QSplitter` column of the five titled chart panels inside a
`QScrollArea`, under a dual-calendar header. `_add_panel()` builds one
panel (title + filter row + chart [+ caption]) and registers its
Collapse/Enlarge buttons; `_toggle_collapsed()` hides a chart down to
just its title+filter row; `_open_enlarged()`/`_close_enlarged()` drive
the reparent-in/reparent-out dance.

## Design Decisions
- **`_last_splitter_sizes` is a module-level cache**, not a settings
  key: the last-used panel sizes are remembered for THIS APP RUN only,
  matching that this window's own geometry is likewise never written to
  disk. It lives here, with the window that reads it.
