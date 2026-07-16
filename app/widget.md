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
- `mouseDoubleClickEvent()` (owner 2026-07-16): a left double-click on
  the Omega (24h) ring letter — hit-tested via
  `compositor.hit_omega()`, the same geometry family as the ring
  letters/ticks — starts (or restarts) the 60-second reveal-week
  window (`compositor.trigger_reveal_week()`); any other double-click
  falls through to Qt's default handling
- `keyPressEvent()`: SPACE is handled FIRST (owner 2026-07-16, ROADMAP
  queue #8) — over a themed hover target (weekday body, astrology/
  ascendant/Chinese slot, hexa sign diamond, Calendar wedge) it asks
  `compositor.encyclopedia_target()` for the last hover position and
  emits `open_encyclopedia(topic, entry)`; because " " is printable this
  MUST precede the typed path (otherwise Space would feed the hidden-mode
  code buffer). A target with no encyclopedia topic does nothing. Every
  other printable key still emits `typed`. `mouseMoveEvent` records the
  last dial-origin cursor (`_last_hover`) that the jump reads
- `open_encyclopedia`: Signal(topic key, entry index) — the controller
  opens the Encyclopedia on that page
- `set_renderer(compositor)` / `set_tick(tick)`: painting inputs; each new
  tick schedules a repaint
- `paintEvent()`: delegates to `compositor.paint(painter, size, dpr, tick)`
- `mousePressEvent()`: left button starts a native OS window move
- `mouseMoveEvent()`: hover tooltips via `compositor.tooltip_at()` —
  small dials pop the full date over the current weekday body, the Earth
  and the Moon markers (large dials write the text directly). Holding
  the BYPASS key (`defaults.HOVER_BYPASS_MODIFIER`, Ctrl) SILENCES
  hovers while the cursor travels (owner 2026-07-16: near the screen
  edge a large neighbour legend covered the smaller weekday body —
  hold, glide past, release inside the wanted element); the
  controller's click-through poller obeys the same key
- `contextMenuEvent()`: opens the shared menu
- `set_click_through()`: TRUE pass-through (`WS_EX_TRANSPARENT`) — no
  clicks, no system hover; recovery via the tray, hover via the
  controller's cursor poller
- `nativeEvent()`: WM_NCHITTEST → `HTTRANSPARENT` outside the dial's
  inscribed circle — corner clicks reach whatever lies beneath (normal
  mode; click-through bypasses hit testing altogether)
- `hideEvent()` / `changeEvent()`: spontaneous-hide watchdog — undoes an
  OS-initiated hide/minimize after `WATCHDOG_RESHOW_MS` (note: Win+D on
  Windows 11 24H2 bypasses these events entirely; see the folder doc)
