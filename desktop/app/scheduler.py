"""Minute-aligned tick scheduling.

A self-rescheduling single-shot PreciseTimer aimed just past the next
minute boundary. The wall clock is read FRESH on every fire — intervals
are never accumulated, so a late fire after sleep/resume self-corrects
on the next tick. A large gap between expected and actual fire time is
reported as a clock jump so the controller can force a full refresh.
"""

from datetime import datetime, timedelta
from typing import Callable

from PySide6.QtCore import QObject, Qt, QTimer

from config import defaults


class MinuteScheduler(QObject):
    def __init__(
        self,
        on_tick: Callable[[bool], None],
        parent: QObject | None = None,
        per_second: bool = False,
    ):
        """`on_tick(clock_jumped)` fires just after every minute boundary —
        or every second boundary when the seconds hand is enabled."""
        super().__init__(parent)
        self._on_tick = on_tick
        self._per_second = per_second
        self._expected: datetime | None = None
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._timer.timeout.connect(self._fire)

    def start(self) -> None:
        self._schedule()

    def stop(self) -> None:
        self._timer.stop()

    def set_per_second(self, per_second: bool) -> None:
        """Cadence change at runtime (the Seconds element switch). The
        pending shot is re-aimed immediately — waiting it out would leave
        a freshly enabled seconds hand frozen for up to a minute."""
        if per_second == self._per_second:
            return
        self._per_second = per_second
        if self._timer.isActive():
            self._timer.stop()
            self._schedule()

    def _schedule(self) -> None:
        now = datetime.now().astimezone()
        if self._per_second:
            ms = 1000 - now.microsecond // 1000 + defaults.TICK_EPSILON_MS
        else:
            ms = (
                (60 - now.second) * 1000
                - now.microsecond // 1000
                + defaults.TICK_EPSILON_MS
            )
        self._expected = now + timedelta(milliseconds=ms)
        self._timer.start(max(ms, defaults.TICK_EPSILON_MS))

    def _fire(self) -> None:
        now = datetime.now().astimezone()
        jumped = (
            self._expected is not None
            and abs((now - self._expected).total_seconds())
            > defaults.CLOCK_JUMP_THRESHOLD_S
        )
        try:
            self._on_tick(jumped)
        finally:
            # Qt swallows non-SystemExit exceptions raised in timer slots;
            # without this, one escaped exception would leave the single-
            # shot timer unscheduled and freeze the dial forever.
            self._schedule()
