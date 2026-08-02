# Clock Widget

**Script:** [Clock Widget (script)](../widget.py) · **Flow:** [diagram](../__flow/widget.md)

## Purpose
The visible product: a frameless, per-pixel-transparent window that
stays below every other window (by default). `paintEvent` delegates
entirely to the render compositor — the widget itself knows nothing
about the dial's contents, only about being a window, taking input and
routing SPACE/hover to the Encyclopedia.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `constants`, `defaults`,
  `dial`, `shortcuts`, `winapi` (window tunables, the shortcut table)
- [Native](native.md) — `KeyboardHook`, `nchittest_falls_outside`
- [Compositor](../../render/__about/compositor.md) — injected via `set_renderer()`

### Used by
- [Watch Controller](controller.md) — creates it, positions it, feeds
  ticks, listens to `moved`/`shortcut_triggered`/`open_encyclopedia`/`typed`

## Classes

### ClockWidget(QWidget)
All window flags/attributes are set in `__init__`, before the first
`show()` — changing them later re-parents and hides the window on
Windows (`FramelessWindowHint | Tool | WindowStaysOnBottomHint` by
default, `WA_TranslucentBackground`, `WA_ShowWithoutActivating`).

#### Signals
- `moved` — every `moveEvent` (debounced save upstream)
- `typed(str)` — printable keys while focused (the hidden-mode code buffer)
- `open_encyclopedia(topic, entry)` — a SPACE jump over a themed target
- `shortcut_triggered(action_id)` — a keyboard shortcut fired while focused
- `first_painted` — emitted ONCE, after the first real paint has reached
  the screen (the manager arms the shared warm thread only once every
  watch has painted)

#### Methods
- `set_z_mode(z_mode) -> bool`: swaps the Z hint between "bottom" /
  "normal" (no hint — rides above only while focused) / "top"
  (`WindowStaysOnTopHint`, re-asserted natively via
  [Native](native.md)'s `assert_topmost` after every flag swap and show,
  since Qt's own hint degrades once the native window is recreated).
  Wraps the swap in hide → `setWindowFlags` → move → show so the
  position survives; returns True when the flags actually changed (the
  controller reconnects `screenChanged`, dropped by the native-window
  recreation)
- `raise_and_focus()`: the "Show" affordance — `raise_()` +
  `activateWindow()`, meant for "normal" z-mode where the dial otherwise
  rides above others only while focused
- `set_dial_diameter(diameter, margin_fraction=None)`: the window is the
  dial plus a transparent margin on every side (for overhanging letters,
  halos and the event glow); `margin_fraction` is supplied live by the
  controller on every skin install
- `paintEvent()`: delegates to `compositor.paint(painter, size, dpr, tick)`;
  emits `first_painted` after the FIRST successful paint. The painter is
  ended on EVERY exit path (owner crash log 2026-07-31: one escaped
  render `ValueError` left the QPainter active and killed every later
  frame) — a failing frame prints its traceback to stderr, stays
  partially drawn, and the next tick paints again
  (`tests/test_paint_safety.py`)
- `mouseDoubleClickEvent()`: a double-click on the Omega (24h) hit area
  toggles the reveal-week window (hides the hands + reveals ghosts/full
  archetype figures for `REVEAL_WEEK_DURATION_S`, or ends it early)
- `keyPressEvent()`: bare SPACE (no modifier) triggers the Encyclopedia
  jump first — it must precede the typed path, since `" "` is printable
  and would otherwise feed the hidden-mode secret buffer. Next, the
  keyboard-shortcut table (`config.shortcuts.SHORTCUTS`, resolved once
  at import time into `_SHORTCUTS`, with `Qt.KeyboardModifier.KeypadModifier`
  masked out of the held modifiers first — a numpad-originated key
  carries that flag alongside whatever the user actually held). Every
  other printable key emits `typed`.
- `_trigger_space_jump()`: the ONE SPACE handler shared by the focused
  `keyPressEvent` and the queued native-hook delivery — resolves the
  live `_last_hover` position through `compositor.encyclopedia_target()`
- `mouseMoveEvent()`: hover tooltips via `compositor.tooltip_at()`;
  holding the bypass modifier (`defaults.HOVER_BYPASS_MODIFIER`) silences
  hovers so the cursor can glide past a large neighbour legend. Arms/
  disarms the native SPACE hook (`_update_space_hook`) based on whether
  the hovered element has a page.
- `contextMenuEvent()`: the dial's own right-click popup — the shared
  menu's "Show" action is hidden here on purpose (you already see the
  dial, that is how you right-clicked it) and restored to the widget's
  own tracked `_z_mode` after the popup closes
- `set_click_through(enabled)`: TRUE pass-through (`WS_EX_TRANSPARENT`
  via [Native](native.md)) — no clicks, no system hover; recovery is via
  the tray, hover via the controller's cursor poller
- `nativeEvent()`: `WM_NCHITTEST` outside the dial's inscribed circle →
  `HTTRANSPARENT`, so a click on the square window's corners falls
  through to whatever lies beneath
- `hideEvent()` / `changeEvent()`: the spontaneous-hide watchdog — an
  OS-initiated hide/minimize this widget did not request is undone after
  `dial.WATCHDOG_RESHOW_MS` (Win+D on Windows 11 24H2 does NOT trigger
  these — the OS raises the desktop layer above everything instead and
  restores the dial itself when Show Desktop ends)
