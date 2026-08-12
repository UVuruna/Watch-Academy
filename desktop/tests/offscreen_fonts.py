"""Real fonts for the offscreen platform — the tofu root cause and cure.

ROOT CAUSE (proved 2026-08-09, and it CORRECTS the previous round's
record): Qt's offscreen QPA plugin on Windows ships an EMPTY platform
font database — ``QFontDatabase.families()`` is 0 in a FRESH offscreen
process before any app code runs — so every text render falls back to
``QFontEngineBox`` and draws .notdef tofu boxes ('8' probes as a 97x97
square). The earlier attribution, "a WatchController lifecycle degrades
the process font roster", was a confound: the suite module that builds
controllers is the SAME module whose import flips the whole process to
offscreen (``test_controller_dialogs.py`` sets ``QT_QPA_PLATFORM`` at
collection time), so "with the controller" and "under the empty-font
platform" were always the same experiment. On the native platform the
identical lifecycle keeps real glyphs (probe 2026-08-09: construct +
del + gc, '8' stays 80.1x44.6 through all three steps).
``test_numerals._require_a_font_database`` had in fact already named
the empty offscreen database on 2026-08-06 — the misdiagnosis
contradicted the repo's own record, which is why it is spelled out
here, at the cure, where the next reader looks first.

THE CURE: register the machine's own font files as APPLICATION fonts —
the offscreen plugin loads them through FreeType even though its
platform database is empty (measured: 208 files in 0.12 s, 102
families; the numeral face and Segoe UI both resolve to real
outlines). Wired at the suite's two app doors — the autouse fixture in
``tests/conftest.py`` and ``test_layout_audit._make_app`` — so guard
audits and extreme-corner teeth measure the PRODUCT's text metrics,
never tofu geometry. The product itself never runs offscreen, which is
why this lives in ``tests/`` and not in ``app/``.
"""

import os
from pathlib import Path


def _font_dirs() -> tuple[Path, ...]:
    """System fonts plus per-user hand-installs — the two default
    numeral faces were recovered and installed by hand, and Windows
    puts hand-installed fonts under the USER profile, not WINDIR."""
    return (
        Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Windows"
        / "Fonts",
    )


def provision() -> bool:
    """Fill an EMPTY platform font database from the machine's font
    files; a no-op when fonts already exist (native platform, or a
    second call). Returns whether real families are available after —
    False only when there is no QGuiApplication to register into, or
    the machine's font directories yielded nothing loadable."""
    from PySide6.QtGui import QFontDatabase, QGuiApplication

    if QGuiApplication.instance() is None:
        return False
    if QFontDatabase.families():
        return True
    for directory in _font_dirs():
        if not directory.is_dir():
            continue
        for path in directory.iterdir():
            if path.suffix.lower() in {".ttf", ".otf", ".ttc"}:
                QFontDatabase.addApplicationFont(str(path))
    return bool(QFontDatabase.families())
