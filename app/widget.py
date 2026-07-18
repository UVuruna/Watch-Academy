"""The transparent desktop clock window.

All window flags/attributes are set in __init__, BEFORE the first show()
— changing them later re-parents and hides the window on Windows.
Painting is delegated to the render compositor; the widget itself knows
nothing about the dial.
"""

from PySide6.QtCore import QEvent, Qt, QTimer, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QMenu, QWidget

from app import native
from config import constants, defaults, winapi

# The hover-bypass key, resolved from the config name (Qt enums do
# not belong in config — Rule: config stays Qt-free).
_HOVER_BYPASS = getattr(
    Qt.KeyboardModifier, defaults.HOVER_BYPASS_MODIFIER
)


class ClockWidget(QWidget):
    """Frameless, per-pixel-transparent, always-at-bottom dial window."""

    moved = Signal()
    typed = Signal(str)                 # printable keys while focused —
                                        # the hidden-mode code listener
    open_encyclopedia = Signal(str, int)  # (topic key, entry index) —
                                        # Spacebar over a themed target
    _space_pressed = Signal()           # the native LL hook's queued hop
                                        # to the GUI thread (SPACE, no focus)

    def __init__(self, diameter: int, menu: QMenu, legend):
        super().__init__()
        self._closing = False
        # Guards the spontaneous-hide watchdog during a deliberate
        # z-mode window-flag swap (owner 2026-07-17): the hide in the
        # middle of hide → setWindowFlags → show must not trigger a
        # reshow race.
        self._z_transition = False
        self._menu = menu
        self._z_mode = "bottom"          # the current Z hint (set below)
        self._legend = legend           # the shared LegendPopup
        self._renderer = None
        self._tick = None
        self._click_through = False
        self._last_hover = None          # last dial-origin cursor (x, y)
        # The transparent margin fraction is LIVE from the settings
        # (owner slike 1–3, 2026-07-17): the controller re-supplies it on
        # every skin install via set_dial_diameter; this default matches
        # the out-of-the-box skin until then.
        self._margin_fraction = defaults.dial_window_margin_fraction(
            defaults.DEFAULT_SKIN
        )

        self.setWindowFlags(self._window_flags("bottom"))
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setWindowTitle(constants.APP_NAME)
        self.setMouseTracking(True)     # hover tooltips on small dials
        # A click gives the dial keyboard focus so the hidden-mode
        # code can be typed on it (owner 2026-07-14).
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        # The native low-level keyboard hook that makes SPACE open the
        # Encyclopedia WHENEVER hover works, focus or not (owner law
        # 2026-07-18). It is live only while the cursor sits on an
        # encyclopedia-capable target (installed/uninstalled from the
        # hover path below). Its callback fires on the GUI thread but we
        # still hop through a QUEUED signal so the modal article opens
        # AFTER the fast hook proc has returned.
        self._space_pressed.connect(
            self._trigger_space_jump, Qt.ConnectionType.QueuedConnection
        )
        self._kbd_hook = native.KeyboardHook(self._space_pressed.emit)
        self.set_dial_diameter(diameter)

    @staticmethod
    def _window_flags(z_mode: str) -> "Qt.WindowType":
        """The frameless tool-window flags with the Z hint for `z_mode`
        (owner 2026-07-17, ROADMAP 15e). THREE modes: "bottom" stays below
        every window except the desktop (WindowStaysOnBottomHint), "normal"
        is a plain window that rides above only while focused (NO Z hint —
        the accidental middle mode the owner asked to keep), "top" rides
        above everything (WindowStaysOnTopHint, re-asserted natively — see
        set_z_mode)."""
        base = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if z_mode == "top":
            return base | Qt.WindowType.WindowStaysOnTopHint
        if z_mode == "bottom":
            return base | Qt.WindowType.WindowStaysOnBottomHint
        return base                      # "normal" — no Z hint

    def set_z_mode(self, z_mode: str) -> bool:
        """Swap the Z hint between the three modes (owner 2026-07-17,
        ROADMAP 15e). Changing window flags re-parents the native window on
        Windows, so it MUST be done in one place: guard the watchdog, hide,
        set the flags, restore the position, show — preserving the exact
        spot. For "top" Qt's StaysOnTop hint DEGRADES to ordinary stacking
        after the swap recreates the window, so topmost is re-asserted
        NATIVELY afterwards (and on every reshow). Returns True when the
        flags actually changed — the caller reconnects `screenChanged`,
        which the native-window recreation drops (the S18 caveat)."""
        self._z_mode = z_mode
        flags = self._window_flags(z_mode)
        if flags == self.windowFlags():
            self._assert_topmost()       # honour a redundant re-request
            return False
        pos = self.pos()
        was_visible = self.isVisible()
        self._z_transition = True
        try:
            if was_visible:
                self.hide()
            self.setWindowFlags(flags)
            self.move(pos)
            if was_visible:
                self.show()
        finally:
            self._z_transition = False
        self._assert_topmost()
        return True

    def _assert_topmost(self) -> None:
        """Re-assert TRUE topmost natively while in the "top" z-mode —
        after a flag swap and after every show (owner 2026-07-17). A no-op
        in the other modes or before the window exists."""
        if self._z_mode == "top" and self.isVisible():
            native.assert_topmost(int(self.winId()))

    def reassert_z_order(self) -> None:
        """Public hook for the controller to re-enforce topmost after the
        first show() and after a monitor/DPI change."""
        self._assert_topmost()

    def mark_closing(self) -> None:
        """Tell the spontaneous-hide watchdog that the coming hide is
        intentional — and tear the SPACE hook down deterministically
        before quit (a leaked low-level hook keeps eating SPACE)."""
        self._closing = True
        self._kbd_hook.uninstall()

    def set_dial_diameter(
        self, diameter: int, margin_fraction: float | None = None
    ) -> None:
        """The window is the dial plus a transparent margin on every
        side (owner spec: the 12/24 letters' overhang and halo, and the
        event glow, were clipped by the window square). `margin_fraction`
        is the LIVE reservation from the current settings (owner slike
        1–3, 2026-07-17); the controller re-supplies it on every skin
        install so a size/hover/letter slider re-sizes the window to fit
        exactly. Omit it to keep the last fraction (e.g. a bare size
        change)."""
        if margin_fraction is not None:
            self._margin_fraction = margin_fraction
        self._dial_diameter = diameter
        self._margin_px = round(diameter * self._margin_fraction)
        self.resize(
            diameter + 2 * self._margin_px, diameter + 2 * self._margin_px
        )

    @property
    def dial_diameter(self) -> int:
        return self._dial_diameter

    @property
    def margin_px(self) -> int:
        return self._margin_px

    def set_menu(self, menu: QMenu) -> None:
        """Swap the shared context menu (rebuilt after Settings — e.g. a
        new custom ring joins Theme ▸ Ring)."""
        self._menu = menu

    def set_click_through(self, enabled: bool) -> None:
        """TRUE click-through: the whole window stops taking mouse input
        (left and right clicks and system hover all pass to whatever lies
        beneath). Recovery is via the tray; hover tooltips come from the
        controller's cursor poller while the mode is on."""
        self._click_through = enabled
        # Toggling click-through cuts off the widget's own mouse events
        # (the controller's cursor poller drives hover from here on), so
        # the hover path can no longer uninstall the SPACE hook — tear it
        # down here or it leaks (owner law 2026-07-18: deterministic
        # teardown). Idempotent in both directions.
        self._kbd_hook.uninstall()
        native.set_click_through(int(self.winId()), enabled)

    # --- Rendering --------------------------------------------------------------

    def set_renderer(self, renderer) -> None:
        """The compositor: paint(painter, size, dpr, tick)."""
        self._renderer = renderer

    def set_tick(self, tick) -> None:
        self._tick = tick
        self.update()

    def paintEvent(self, event) -> None:
        if self._renderer is None or self._tick is None:
            # Documented startup order: the controller delivers the first
            # tick before show(), so this only covers stray early paints.
            return
        painter = QPainter(self)
        painter.translate(self._margin_px, self._margin_px)
        self._renderer.paint(
            painter,
            float(self._dial_diameter),
            self.devicePixelRatioF(),
            self._tick,
        )

    # --- Input ----------------------------------------------------------------

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            # Native OS move: correct across monitors and DPI changes.
            self.windowHandle().startSystemMove()
        else:
            super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        # Omega (24h) double-click — REPURPOSED (owner seal 2026-07-16):
        # HIDES THE HANDS for REVEAL_WEEK_DURATION_S or until the NEXT
        # double-click (a toggle-off, not a restart); the weekday
        # ghost-reveal and the archetype figures fold into the same
        # "show me everything" gesture inside the compositor.
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self._renderer is not None
        ):
            x = event.position().x() - self._margin_px
            y = event.position().y() - self._margin_px
            if self._renderer.hit_omega(x, y, float(self._dial_diameter)):
                started = self._renderer.trigger_reveal_week()
                self.update()
                if started:
                    # Snap BACK on time: without this the expiry would
                    # wait for the next minute tick to repaint (nothing
                    # else schedules a frame at that moment). A stale
                    # shot after a toggle-off repaints harmlessly.
                    QTimer.singleShot(
                        defaults.REVEAL_WEEK_DURATION_S * 1000 + 50,
                        self.update,
                    )
                return
        super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event) -> None:
        # SPACE opens the Encyclopedia at the hovered topic (owner
        # 2026-07-16, ROADMAP queue #8) — handled BEFORE the typed path
        # because " " is printable and would otherwise feed the
        # hidden-mode code buffer. This is the FOCUSED fallback; the
        # unfocused case (owner law 2026-07-18) comes through the native
        # hook, which consumes SPACE so this path never double-fires.
        if event.key() == Qt.Key.Key_Space:
            self._trigger_space_jump()
            return
        text = event.text()
        if text and text.isprintable():
            self.typed.emit(text)
        else:
            super().keyPressEvent(event)

    def _trigger_space_jump(self) -> None:
        """Open the Encyclopedia on the element currently under the
        cursor — the ONE SPACE handler, shared by the focused
        keyPressEvent and the queued native-hook delivery. The target is
        recomputed LIVE from the last dial-origin cursor; a stale or
        off-target hover (`_last_hover` cleared on leave) does nothing, so
        SPACE off the themed elements is inert (owner 15h item 3B)."""
        if self._renderer is None or self._last_hover is None:
            return
        target = self._renderer.encyclopedia_target(
            self._last_hover[0], self._last_hover[1],
            float(self._dial_diameter),
        )
        if target is not None:
            self.open_encyclopedia.emit(target[0], target[1])

    def mouseMoveEvent(self, event) -> None:
        if self._renderer is not None and self._tick is not None:
            if event.modifiers() & _HOVER_BYPASS:
                # The held BYPASS key silences the whole hover system
                # (owner 2026-07-16): a large neighbour legend — e.g.
                # the hexa zodiac diamond's — can cover a smaller
                # target near the screen edge; hold, glide past,
                # release inside the element you actually want. With the
                # hovers silenced the SPACE hook stands down too.
                if self._renderer.set_hover(
                    -1.0e9, -1.0e9, float(self._dial_diameter)
                ):
                    self.update()
                self._legend.dismiss()
                self._last_hover = None
                self._update_space_hook(None)
                super().mouseMoveEvent(event)
                return
            size = float(self._dial_diameter)
            x = event.position().x() - self._margin_px
            y = event.position().y() - self._margin_px
            self._last_hover = (x, y)    # for the Spacebar jump
            if self._renderer.set_hover(x, y, size):
                self.update()           # hover-enlarge target changed
            tip = self._renderer.tooltip_at(x, y, size)
            if tip:
                self._legend.show_html(tip, event.globalPosition().toPoint())
                # A tooltip is a NECESSARY condition for an encyclopedia
                # page (every page-bearing element also speaks a hover),
                # so the target is only worth computing when there IS a
                # tip — install the SPACE hook when it has a page.
                self._update_space_hook(
                    self._renderer.encyclopedia_target(x, y, size)
                )
            else:
                self._legend.dismiss()
                self._update_space_hook(None)
        super().mouseMoveEvent(event)

    def _update_space_hook(self, target) -> None:
        """Arm the native SPACE hook while the cursor sits on an
        encyclopedia-capable target, disarm it otherwise — so SPACE opens
        the article without the dial needing focus, yet never eats SPACE
        from other apps at any other moment (owner law 2026-07-18). Both
        calls are idempotent."""
        if target is not None:
            self._kbd_hook.install()
        else:
            self._kbd_hook.uninstall()

    def leaveEvent(self, event) -> None:
        if self._renderer is not None and self._renderer.set_hover(
            -1.0e9, -1.0e9, float(self._dial_diameter)
        ):
            self.update()               # shrink the enlarged element back
        # The cursor left the dial: the last hover position is now STALE,
        # so clear it (owner 15h item 3B — a stale on-target position let
        # SPACE fire off the dial) and stand the SPACE hook down.
        self._last_hover = None
        self._update_space_hook(None)
        # Crossing INTO the legend popup must not close it — the wheel
        # scrolls the article there; its own leaveEvent hides it.
        self._legend.hide_unless_hovered()
        super().leaveEvent(event)

    def contextMenuEvent(self, event) -> None:
        self._menu.exec(event.globalPos())

    def moveEvent(self, event) -> None:
        super().moveEvent(event)
        self.moved.emit()

    def nativeEvent(self, event_type, message):
        """Clicks outside the dial's inscribed circle fall through to
        whatever lies beneath — the square window corners are not ours.
        (In click-through mode WS_EX_TRANSPARENT bypasses hit testing
        altogether, so this only matters in normal mode.)"""
        if event_type == b"windows_generic_MSG" and native.nchittest_falls_outside(
            int(message)
        ):
            return True, winapi.HTTRANSPARENT
        return super().nativeEvent(event_type, message)

    # --- Spontaneous-hide watchdog ----------------------------------------------
    # An OS-initiated hide/minimize we did not request is undone after a
    # short delay. Verified on Windows 11 24H2: Win+D does NOT trigger these
    # events (it covers the window with the raised desktop layer instead and
    # restores it when Show Desktop mode ends) — this guard covers the other
    # shell actions that genuinely hide or minimize the window.

    def hideEvent(self, event) -> None:
        super().hideEvent(event)
        # A hidden dial has no hover, so stand the SPACE hook down (owner
        # law 2026-07-18: uninstall on hide) — the next hover re-arms it.
        self._kbd_hook.uninstall()
        # A deliberate z-mode flag swap hides the window mid-transition —
        # the watchdog must not fight it (owner 2026-07-17).
        if event.spontaneous() and not self._closing and not self._z_transition:
            QTimer.singleShot(defaults.WATCHDOG_RESHOW_MS, self._reshow)

    def changeEvent(self, event) -> None:
        if (
            event.type() == QEvent.Type.WindowStateChange
            and self.isMinimized()
            and not self._closing
        ):
            QTimer.singleShot(defaults.WATCHDOG_RESHOW_MS, self.showNormal)
        super().changeEvent(event)

    def _reshow(self) -> None:
        if not self._closing:
            self.show()
            # A spontaneous hide re-shows behind the stack; in the "top"
            # z-mode re-assert native topmost so the reshow rides above
            # again (owner 2026-07-17).
            self._assert_topmost()
