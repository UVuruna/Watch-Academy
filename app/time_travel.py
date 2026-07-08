"""Time Travel — the owner's scenario tester.

A small dialog takes any moment (day, month, year, hour, minute) and any
position (latitude, longitude); the dial then renders that situation for
one minute and resets to the present by itself. The entered wall time is
interpreted in the currently configured timezone.
"""

from datetime import datetime

from PySide6.QtCore import QDateTime, Qt
from PySide6.QtWidgets import (
    QDateTimeEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
)

from config import constants, defaults


class TimeTravelDialog(QDialog):
    def __init__(self, latitude: float, longitude: float, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{constants.APP_NAME} — Time Travel")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        self._when = QDateTimeEdit(QDateTime.currentDateTime(), self)
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
        layout.addRow("Moment:", self._when)
        layout.addRow("Latitude:", self._latitude)
        layout.addRow("Longitude:", self._longitude)
        layout.addRow(
            QLabel(
                f"The dial shows this situation for "
                f"{defaults.TIME_TRAVEL_DURATION_S} seconds, then returns "
                f"to the present."
            )
        )
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def moment(self) -> datetime:
        """Naive wall time — the controller attaches the active timezone."""
        return self._when.dateTime().toPython()

    def latitude(self) -> float:
        return self._latitude.value()

    def longitude(self) -> float:
        return self._longitude.value()
