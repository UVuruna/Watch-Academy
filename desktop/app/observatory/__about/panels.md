# Panels

**Script:** [Panels (script)](../panels.py)

## Purpose
What sits BESIDE a chart: the "About this chart" info box, the
`ChartPane` that pairs a plot with its own chrome, and `EnlargeDialog`,
the full-screen target a chart is reparented INTO and back out of.

These are the widgets that FRAME a chart without being one — the third
responsibility the [OOP
audit](../../../../docs/AUDIT-OOP-2026-08-18.md) found inside
`app/observatory.py` (R12, 2026-08-18).

## Connections

### Uses
- [Charts](charts.md) — `ChartBase`, the thing being framed
- [Theme](../../__about/theme.md) — the dark dialog surface
- [UI Style](../../__about/ui_style.md) — the vivid pills

### Used by
- [Dialog](dialog.md) — one `ChartPane` per chart; `EnlargeDialog` on
  demand
- `tests/test_observatory.py` — patches `EnlargeDialog` on the DIALOG
  module (that is the globals the consumer reads)

### `EnlargeDialog(QDialog)`
The "Enlarge" target for any panel — TEMPORARILY REPARENTS the SAME
panel widget in (`panel.setParent(self)`) and back to its splitter slot
on close, so zoom/pan/checkbox state carries for free in both
directions; adds an extended legend (current-value readout per series,
polled) and a collapsible info panel (`build_info_panel`). Does NOT set
`WA_DeleteOnClose` (a real fixed crash, see Design Decisions) —
`_close_enlarged` reparents `panel` back FIRST, then calls
`dialog.deleteLater()` explicitly.

## Design Decisions
- **A fixed crash, now regression-pinned**: `EnlargeDialog` used to set
  `WA_DeleteOnClose`, which queued the DIALOG's own C++ destruction via
  `deleteLater()` — since the reparented `panel` was a real Qt child of
  it, that queued deletion could (and did) destroy `panel` before
  `_open_enlarged` reinserted it (`RuntimeError: Internal C++ object
  already deleted`). Fixed by reparenting `panel` back to the splitter
  BEFORE calling `deleteLater()` on the dialog, never after; pinned by a
  real (un-mocked) `QDialog.exec()`-driven test cycling all 5 charts
  twice.
