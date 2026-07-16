"""Time Travel — the owner's scenario tester.

A small dialog takes any moment (day, month, year, hour, minute) and any
position (latitude, longitude); the dial then renders that situation for
one minute and resets to the present by itself. The entered wall time is
interpreted in the currently configured timezone.
"""

from datetime import datetime

from PySide6.QtCore import QDate, QDateTime, Qt
from PySide6.QtWidgets import (
    QDateTimeEdit,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)

from app.ui_style import style_button
from config import constants, defaults
from config.ui_text import ui


class TimeTravelDialog(QDialog):
    # The third exit (owner 2026-07-15): end the simulation and return
    # the dial to the present immediately (Accepted=1, Rejected=0).
    RETURN_TO_NOW = 2
    def __init__(
        self, latitude: float, longitude: float, parent=None,
        overlay: dict | None = None,
        initial_moment: datetime | None = None,
        coverage: tuple[int, int] | None = None,
    ):
        super().__init__(parent)
        tr = lambda text: ui(overlay or {}, text)  # noqa: E731 — dialog chrome
        self._tr = tr
        # The bundled databases' year span (seasons ∩ moon); a target
        # outside it is refused BEFORE travelling, so Time Travel never
        # reaches the day-build's die-visibly path (owner 2026-07-16).
        self._coverage = coverage
        self.setWindowTitle(f"{constants.APP_NAME} — {tr('Time Travel')}")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        # A running simulation seeds the moment (owner 2026-07-14) —
        # naive, expressed in the configured timezone. The editor spans
        # the whole representable calendar so the owner can dial into deep
        # time and READ the coverage message (owner 2026-07-16); the
        # default 1752 floor would silently swallow an ancient target
        # instead of explaining it. The range is widened BEFORE the value
        # is set, or the seed would clamp on construction.
        self._when = QDateTimeEdit(self)
        self._when.setDateRange(QDate(1, 1, 1), QDate(9999, 12, 31))
        self._when.setDateTime(
            QDateTime(initial_moment)
            if initial_moment is not None
            else QDateTime.currentDateTime()
        )
        self._when.setCalendarPopup(True)
        self._when.setDisplayFormat("dd.MM.yyyy HH:mm")

        low, high = constants.LATITUDE_RANGE
        self._latitude = QDoubleSpinBox(self)
        self._latitude.setRange(low, high)
        self._latitude.setDecimals(4)
        self._latitude.setValue(latitude)
        low, high = constants.LONGITUDE_RANGE
        self._longitude = QDoubleSpinBox(self)
        self._longitude.setRange(low, high)
        self._longitude.setDecimals(4)
        self._longitude.setValue(longitude)

        layout = QFormLayout(self)
        layout.addRow(tr("Moment:"), self._when)
        layout.addRow(tr("Latitude:"), self._latitude)
        layout.addRow(tr("Longitude:"), self._longitude)
        layout.addRow(
            QLabel(
                tr(
                    "The dial shows this situation for {n} seconds, "
                    "then returns to the present."
                ).format(n=defaults.TIME_TRAVEL_DURATION_S)
            )
        )
        # Coverage warning — hidden until an out-of-range OK (owner
        # 2026-07-16): the dialog stays open and no travel starts.
        self._coverage_warning = QLabel(self)
        self._coverage_warning.setWordWrap(True)
        self._coverage_warning.setStyleSheet(
            f"color: {defaults.TIME_TRAVEL_WARNING_COLOR};"
        )
        self._coverage_warning.hide()
        layout.addRow(self._coverage_warning)
        # The shared vivid buttons (owner 2026-07-15: the stylized ones
        # we use), NOW standing on the LEFT — back to the present, the
        # simulation ends immediately.
        row = QHBoxLayout()
        now = QPushButton(tr("Now"), self)
        style_button(now, "home", small=True)
        now.setToolTip(
            tr("Back to the present — the simulation ends immediately.")
        )
        now.clicked.connect(lambda: self.done(self.RETURN_TO_NOW))
        ok = QPushButton(tr("OK"), self)
        style_button(ok, "next", small=True)
        ok.clicked.connect(self.accept)
        cancel = QPushButton(tr("Cancel"), self)
        style_button(cancel, "neutral", small=True)
        cancel.clicked.connect(self.reject)
        row.addWidget(now)
        row.addStretch(1)
        row.addWidget(ok)
        row.addWidget(cancel)
        layout.addRow(row)

    def target_within_coverage(self) -> bool:
        """True when the entered year lies inside the bundled coverage —
        the guard that keeps Time Travel from ever reaching the day
        build's die-visibly path (owner 2026-07-16). Always true when no
        coverage was supplied."""
        if self._coverage is None:
            return True
        first, last = self._coverage
        return first <= self.moment().year <= last

    def accept(self) -> None:
        """Refuse an out-of-range target inline instead of travelling:
        the message shows and the dialog stays open (owner 2026-07-16)."""
        if not self.target_within_coverage():
            first, last = self._coverage
            deep_first, deep_last = defaults.DEEP_TIME_YEAR_RANGE
            self._coverage_warning.setText(
                self._tr(
                    "Time Travel covers {first}–{last} for now — the Deep "
                    "Time data pack extends it to {deep_first}…{deep_last} "
                    "(coming)."
                ).format(
                    first=first, last=last,
                    deep_first=deep_first, deep_last=deep_last,
                )
            )
            self._coverage_warning.show()
            self.adjustSize()
            return
        super().accept()

    def moment(self) -> datetime:
        """Naive wall time — the controller attaches the active timezone."""
        return self._when.dateTime().toPython()

    def latitude(self) -> float:
        return self._latitude.value()

    def longitude(self) -> float:
        return self._longitude.value()
