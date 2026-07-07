"""DOMY Watch entry point."""

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from config import constants


def main() -> int:
    # Must run before QApplication exists: 125%/150% Windows scaling should
    # yield true fractional devicePixelRatio, not a rounded integer.
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName(constants.APP_NAME)
    app.setOrganizationName(constants.ORGANIZATION)
    # The dial is a Qt.Tool window and the settings dialog comes and goes —
    # without this, closing any dialog would quit the whole app.
    app.setQuitOnLastWindowClosed(False)

    from app.controller import AppController

    controller = AppController(app)
    controller.run()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
