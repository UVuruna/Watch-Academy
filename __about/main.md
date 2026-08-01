# Main (Entry Point)

**Script:** [Main (script)](../main.py) ·
**Flow:** [diagram](../__flow/main.md)

## Purpose

The application's entry point (`python main.py`). Installs crash
forensics before anything else can crash, gives the process its own
taskbar identity, sets the High-DPI rounding policy, refuses a second
running instance, then builds the `AppController` and hands off to
Qt's event loop. Every step here has a documented ORDER dependency —
several must run before `QApplication` exists — which is why it earns
a [flow diagram](../__flow/main.md) instead of being read as plain
top-to-bottom wiring.

## Usage

```bash
pip install -r requirements.txt
python main.py
```

A second launch while one instance is already running shows an
information dialog ("DOMY Watch is already running.") and exits
cleanly (return 0) instead of opening a second dial.

## Connections

### Uses
- `config.constants` — `APP_NAME`, `ORGANIZATION`, `APP_USER_MODEL_ID`,
  `SINGLE_INSTANCE_MUTEX`
- `config.paths` — `user_dir()`, the crash log's `%APPDATA%/DOMY
  Watch/` location
- [Native (Win32 helpers)](../app/__about/native.md) — `set_app_user_model_id`
  (own taskbar icon/grouping) and `acquire_single_instance` (named
  mutex check)
- [Watch Manager](../app/__about/watch_manager.md) — `AppController`, built
  and run once the single-instance check passes

### Used by
- Nobody in the project imports `main.py` — it is the OS/shell entry
  point (`python main.py`, and the PyInstaller entry point once
  `setup/build.py` lands)

## Functions

- `_install_crash_logging()` — opens (append mode)
  `%APPDATA%/DOMY Watch/crash.log` under a timestamped session header
  and installs TWO complementary traps: `faulthandler.enable()` for
  native fatal errors (segfaults out of Qt or the ctypes keyboard
  hook — nothing a Python handler can catch) and a `sys.excepthook`
  wrapper that logs unhandled Python tracebacks before delegating to
  the previous hook (so nothing is swallowed, Rule #1). A log file
  that cannot be opened degrades to unlogged with a stderr note rather
  than blocking startup; the file handle is held in a module-level
  global so it is never garbage-collected out from under
  `faulthandler` while open.
- `main() -> int` — the startup sequence (see
  [flow](../__flow/main.md) for the exact order and why it matters);
  returns 0 immediately if another instance already holds the mutex,
  otherwise returns `app.exec()`'s exit code.
