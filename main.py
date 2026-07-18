"""DOMY Watch entry point."""

import faulthandler
import os
import sys
import traceback
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from config import constants, paths

# Held open for faulthandler's whole lifetime — a garbage-collected file
# object would close the fd out from under it.
_crash_log = None


def _install_crash_logging() -> None:
    """Permanent crash forensics (owner 15h item 3C — the occasional,
    unreproducible SPACE crash). Two complementary traps, both APPENDING
    to %APPDATA%/DOMY Watch/crash.log under a timestamped session header:

    - faulthandler dumps the NATIVE fatal-error traceback (a real crash —
      e.g. a segfault out of Qt or the ctypes keyboard hook — that no
      Python handler can catch);
    - a sys.excepthook records unhandled PYTHON tracebacks BEFORE
      delegating to the previous hook.

    This only ADDS a trace; the original hook still runs, so nothing is
    swallowed (Rule #1). A log that cannot be opened must not stop the
    app from starting — it degrades to unlogged with a stderr note."""
    global _crash_log
    try:
        log_dir = paths.user_dir()
        log_dir.mkdir(parents=True, exist_ok=True)
        _crash_log = open(log_dir / "crash.log", "a", encoding="utf-8")
    except OSError as error:
        print(f"crash log unavailable: {error}", file=sys.stderr)
        return
    _crash_log.write(
        f"\n===== {constants.APP_NAME} session "
        f"{datetime.now():%Y-%m-%d %H:%M:%S} (pid {os.getpid()}) =====\n"
    )
    _crash_log.flush()
    faulthandler.enable(file=_crash_log)

    previous_hook = sys.excepthook

    def _log_and_delegate(exc_type, exc, tb) -> None:
        traceback.print_exception(exc_type, exc, tb, file=_crash_log)
        _crash_log.flush()
        previous_hook(exc_type, exc, tb)

    sys.excepthook = _log_and_delegate


def main() -> int:
    # A trace for the next crash BEFORE anything else can crash.
    _install_crash_logging()
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

    from app import native
    from app.controller import AppController

    if not native.acquire_single_instance(constants.SINGLE_INSTANCE_MUTEX):
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(
            None, constants.APP_NAME, "DOMY Watch is already running."
        )
        return 0

    controller = AppController(app)
    controller.run()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
