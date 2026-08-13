"""ONE SIZE, ONE PLACE — the Fast Travel flash must stand at the SAME
distance from the dial in the SAME size for EVERY category Ctrl+[
cycles through (owner drift report 2026-08-13: as he cycled, the label
seemed to shift slightly and to change size).

Root cause, measured before it was believed: `QIcon.pixmap()` is DPI
aware and `QPixmap.scaled()` counts DEVICE pixels. A source that can
supply any size (the SVGs, a raster larger than the request) returns
`n * dpr` device pixels already carrying `devicePixelRatio = dpr`,
while the two COMPUTED icons exist at exactly `SUPERSAMPLE * ICON_PX`
px and come back at a dpr of 1. `scaled(28, 28)` therefore produced
22.4 LOGICAL px for one family and 28.0 for the other, so the flash
box was 42 px tall for three categories and 48 for the other three —
and the box is anchored by its BOTTOM edge above the dial, so its text
jumped 3 px between categories.

THE BUG ONLY EXISTS ABOVE 100 % SCALING, which is why it shipped. This
module therefore measures in a SUBPROCESS under `QT_SCALE_FACTOR=1.25`
(the owner's own setting) — a scale factor is read once, when the
QApplication is built, so it cannot be arranged inside a suite that
already has one.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCALE = "1.25"

# The flash's own vertical geometry is integral: the box height, the
# icon's logical size and the plate run's height are all decided in
# whole device pixels, so EVERY category must land on the SAME number,
# not a near one — hence EXACT comparisons below, with no tolerance to
# argue about.
#
# The HORIZONTAL centre is deliberately not asserted. Two things move it
# and neither is this defect: `x = centre - width // 2` on an integer
# widget width leaves an irreducible half pixel of parity, and a flash
# wider than the space beside the dial is legitimately CLAMPED to the
# screen — which is what the 640 px offscreen screen does to the longest
# category here. A test of it would measure the screen, not the bug.


def _measure() -> list[dict]:
    """Render the flash for every category and emit one row each."""
    from PySide6.QtWidgets import QApplication, QWidget

    from app.fast_travel_flash import FastTravelFlash
    from config import defaults, shortcuts
    from render.asset_variants import (
        calendar_sheet_icon_file,
        clock_face_icon_file,
        eclipse_sun_icon_file,
    )

    dial_top, dial_left, dial_size = 400, 300, 420
    app = QApplication.instance() or QApplication([])
    dial = QWidget()
    dial.setGeometry(dial_left, dial_top, dial_size, dial_size)
    dial.show()
    flash = FastTravelFlash()

    rows = []
    for theme in shortcuts.FAST_TRAVEL_THEMES:
        computed = {
            "calendar_sheet": calendar_sheet_icon_file,
            "clock_face": clock_face_icon_file,
            "eclipse_sun": eclipse_sun_icon_file,
        }.get(theme.get("computed_icon"))
        if computed is not None:
            icon_path = computed(
                shortcuts.FAST_TRAVEL_FLASH_ICON_SUPERSAMPLE
                * shortcuts.FAST_TRAVEL_FLASH_ICON_PX
            )
        else:
            key = theme["icon_key"]
            icon_path = defaults.icon_path(key) if key is not None else None
        option = theme["options"][0]
        flash.flash(
            dial, icon_path, theme["emoji"],
            f"{theme['title']} : {option['title']}",
        )
        app.processEvents()
        icon = flash._icon_label.pixmap()
        text = flash._text_label.pixmap()
        rows.append({
            "category": theme["title"],
            "top_y": flash.y(),
            "bottom_y": flash.y() + flash.height(),
            "centre_x": flash.x() + flash.width() / 2,
            "icon_logical_px": icon.width() / icon.devicePixelRatio(),
            "text_logical_px": text.height() / text.devicePixelRatio(),
        })
    return rows


@pytest.fixture(scope="module")
def rows() -> list[dict]:
    environment = dict(os.environ)
    environment["QT_QPA_PLATFORM"] = "offscreen"
    environment["QT_SCALE_FACTOR"] = SCALE
    environment["PYTHONPATH"] = str(PROJECT_ROOT)
    finished = subprocess.run(
        [sys.executable, "-m", "tests.test_fast_travel_flash"],
        cwd=PROJECT_ROOT, env=environment,
        capture_output=True, text=True, timeout=300,
    )
    assert finished.returncode == 0, (
        f"the flash probe failed under QT_SCALE_FACTOR={SCALE}:\n"
        f"{finished.stdout}\n{finished.stderr}"
    )
    measured = json.loads(finished.stdout.strip().splitlines()[-1])
    assert len(measured) >= 2, "the probe measured fewer than two categories"
    return measured


def _spread(measured: list[dict], key: str) -> float:
    values = [row[key] for row in measured]
    return max(values) - min(values)


def _table(measured: list[dict]) -> str:
    return "\n".join(
        f"  {row['category']:<20} top_y={row['top_y']} "
        f"icon={row['icon_logical_px']} text={row['text_logical_px']}"
        for row in measured
    )


def test_every_category_flashes_at_the_same_height(rows) -> None:
    assert _spread(rows, "top_y") == 0 and _spread(rows, "bottom_y") == 0, (
        "the flash box stands at a DIFFERENT distance from the dial per "
        f"category under {SCALE}x scaling:\n{_table(rows)}"
    )


def test_every_category_flashes_at_the_same_size(rows) -> None:
    assert _spread(rows, "icon_logical_px") == 0, (
        "the flash icon's LOGICAL size differs per category - a DPI-aware "
        f"source measured against device pixels:\n{_table(rows)}"
    )
    assert _spread(rows, "text_logical_px") == 0, (
        f"the flash plate run's height differs per category:\n{_table(rows)}"
    )


def test_the_icon_keeps_its_declared_size(rows) -> None:
    from config import shortcuts

    for row in rows:
        assert row["icon_logical_px"] == shortcuts.FAST_TRAVEL_FLASH_ICON_PX, (
            f"{row['category']}: the icon is {row['icon_logical_px']} logical "
            f"px, not the declared {shortcuts.FAST_TRAVEL_FLASH_ICON_PX}"
        )


if __name__ == "__main__":
    print(json.dumps(_measure()))
