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
`QWidget` subclass; the flags/attributes are set in `__init__` before the
first `show()` (`FramelessWindowHint | Tool | WindowStaysOnBottomHint`,
`WA_TranslucentBackground`, `WA_ShowWithoutActivating`). The Z hint is the
one flag that changes later, via `set_z_mode()` (owner 2026-07-17,
ROADMAP 15e): THREE modes — "bottom" (below all windows, the default,
`WindowStaysOnBottomHint`), "normal" (a plain window, above only while
focused — NO Z hint, the accidental middle mode the owner asked to keep)
and "top" (always on top, `WindowStaysOnTopHint`). A window-flag change
re-parents on Windows, so it is done in ONE place with
hide → `setWindowFlags` → show, preserving the position and guarding the
spontaneous-hide watchdog (`_z_transition`). Qt's StaysOnTop hint DEGRADES
to normal stacking after that swap recreates the native window, so "top"
re-asserts TRUE topmost NATIVELY (`native.assert_topmost`) after the swap
and after every show/reshow (`_assert_topmost`, `reassert_z_order`).
`set_z_mode` returns True when the flags actually changed — the controller
reconnects `screenChanged`, which the native-window recreation drops (the
S18 caveat). The transparent
window margin is LIVE from the settings: `set_dial_diameter(diameter,
margin_fraction)` takes the fraction the controller computes from
`defaults.dial_window_margin_fraction(skin)` on every skin install (owner
slike 1–3 2026-07-17), so a size/hover/letter slider re-sizes the window
to fit exactly.

#### Attributes
- `moved`: Signal emitted on every `moveEvent` (debounced save upstream)

#### Methods
- `mark_closing()`: disarms the spontaneous-hide watchdog before an
  intentional hide/exit
- `mouseDoubleClickEvent()` (owner seal 2026-07-16, REPURPOSED the
  same day): a left double-click on the Omega (24h) ring letter —
  hit-tested via `compositor.hit_omega()` — the FULL ROUND AREA at the
  24h seat (owner slika 9, 2026-07-17) — TOGGLES the reveal window
  (`compositor.trigger_reveal_week()`): the first click HIDES THE
  HANDS for `REVEAL_WEEK_DURATION_S` (with the weekday model on the
  ghosts rise to full in the same gesture; in archetype mode every
  figure draws full), the next click ends it — a toggle-off, not a
  restart. The snap-back QTimer fires only on a START (a stale shot
  after a toggle-off repaints harmlessly); any other double-click
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
