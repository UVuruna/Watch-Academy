# Clock Widget

**Script:** [Clock Widget (script)](widget.py)

## Purpose
The visible product: a frameless, per-pixel-transparent, always-at-bottom
window. `paintEvent` delegates to the render compositor — the widget
knows nothing about the dial itself.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — window tunables
- [Compositor](../render/compositor.md) — injected via `set_renderer()`

### Used by
- [App Controller](controller.md) — creates it, positions it, feeds ticks,
  listens to `moved`

## Classes

### ClockWidget
`QWidget` subclass; all flags/attributes are set in `__init__` before the
first `show()` (`FramelessWindowHint | Tool | WindowStaysOnBottomHint`,
`WA_TranslucentBackground`, `WA_ShowWithoutActivating`).

#### Attributes
- `moved`: Signal emitted on every `moveEvent` (debounced save upstream)

#### Methods
- `mark_closing()`: disarms the spontaneous-hide watchdog before an
  intentional hide/exit
- `set_renderer(compositor)` / `set_tick(tick)`: painting inputs; each new
  tick schedules a repaint
- `paintEvent()`: delegates to `compositor.paint(painter, size, dpr, tick)`
- `mousePressEvent()`: left button starts a native OS window move
- `mouseMoveEvent()`: hover tooltips via `compositor.tooltip_at()` —
  small dials pop the full date over the current weekday body, the Earth
  and the Moon markers (large dials write the text directly)
- `contextMenuEvent()`: opens the shared menu
- `hideEvent()` / `changeEvent()`: spontaneous-hide watchdog — undoes an
  OS-initiated hide/minimize after `WATCHDOG_RESHOW_MS` (note: Win+D on
  Windows 11 24H2 bypasses these events entirely; see the folder doc)
