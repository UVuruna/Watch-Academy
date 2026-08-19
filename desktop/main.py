"""Watch Academy entry point."""

import faulthandler
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from config import identity, paths

# Held open for faulthandler's whole lifetime — a garbage-collected file
# object would close the fd out from under it.
_crash_log = None


def _install_crash_logging() -> None:
    """Permanent crash forensics (owner 15h item 3C — the occasional,
    unreproducible SPACE crash). Two complementary traps, both APPENDING
    to %APPDATA%/Watch Academy/crash.log under a timestamped session header:

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
        f"\n===== {identity.APP_NAME} session "
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


def _migrate_legacy_user_dir() -> None:
    """THE RENAMING (owner decree 2026-08-10): the per-user folder was
    `%APPDATA%/DOMY Watch` for the app's whole prior life. One atomic
    rename carries an existing install's live state — settings, raster
    cache, crash log, translations — onto the Watch Academy name;
    without it every install would silently reset to defaults (the
    settings-rename-needs-migration rule). Runs BEFORE crash logging,
    which would otherwise create the new folder and block the rename.
    New-folder-exists wins (the migration is history); a locked folder
    just retries on the next start; the measurement override is its own
    isolated world and never migrates anything."""
    if os.environ.get("WATCH_ACADEMY_USER_DIR_OVERRIDE"):
        return
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return
    legacy = Path(appdata) / identity.APP_NAME_LEGACY
    current = Path(appdata) / identity.APP_NAME
    if legacy.is_dir() and not current.exists():
        try:
            legacy.rename(current)
        except OSError as error:
            print(f"user-dir migration deferred: {error}", file=sys.stderr)


def main() -> int:
    # The identity migration FIRST — crash logging right below creates
    # the user dir, and an already-created new dir would block the
    # rename that carries the owner's live state over.
    _migrate_legacy_user_dir()
    # A trace for the next crash BEFORE anything else can crash.
    _install_crash_logging()

    from app import native

    # Give the process its OWN taskbar identity BEFORE any window exists
    # (owner screenshot 2026-07-20: Encyclopedia/Guide/Observatory showed
    # python's own logo in the taskbar) — needs no QApplication and no
    # HWND, so it runs first.
    native.set_app_user_model_id(identity.APP_USER_MODEL_ID)
    # ...and the autostart entry follows the name once, the same decree.
    native.migrate_legacy_autostart()
    # Must run before QApplication exists: 125%/150% Windows scaling should
    # yield true fractional devicePixelRatio, not a rounded integer.
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName(identity.APP_NAME)
    app.setOrganizationName(identity.ORGANIZATION)
    # The dial is a Qt.Tool window and the settings dialog comes and goes —
    # without this, closing any dialog would quit the whole app.
    app.setQuitOnLastWindowClosed(False)

    from app.watch_manager import AppController

    if not native.acquire_single_instance(identity.SINGLE_INSTANCE_MUTEX):
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(
            None, identity.APP_NAME, "Watch Academy is already running."
        )
        return 0

    controller = AppController(app)
    controller.run()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
