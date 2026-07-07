# Clock Widget

**Script:** [Clock Widget (script)](widget.py)

## Purpose
The visible product: a frameless, per-pixel-transparent, always-at-bottom
window that shows the dial. In M1 it paints a translucent placeholder disc;
from M3 `paintEvent` delegates to the render compositor.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — window and placeholder tunables

### Used by
- [App Controller](controller.md) — creates it, positions it, listens to `moved`

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
- `mousePressEvent()`: left button starts a native OS window move
- `contextMenuEvent()`: opens the shared menu
- `hideEvent()` / `changeEvent()`: spontaneous-hide watchdog — undoes an
  OS-initiated hide/minimize after `WATCHDOG_RESHOW_MS` (note: Win+D on
  Windows 11 24H2 bypasses these events entirely; see the folder doc)
- `paintEvent()`: M1 placeholder (disc, ring, noon triangle, center dot,
  wordmark)
