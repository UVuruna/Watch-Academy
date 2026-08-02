"""THE SLOW START (owner report 2026-07-28) — the regression pins.

Measured before the fix, on a cold raster cache: the owner's three
watches took **14.78 s** to put a dial on screen (4.20 + 4.79 + 5.67),
every second of it inside `paintEvent`. cProfile attributed it entirely
to 15 metal recolors per watch through `letter_metal_file` — 3.45 s of
numpy (oklab, guided box filter, specular ramp) plus 0.48 s of PNG
encoding, run synchronously on the GUI thread. On top of that, EVERY
watch started its OWN warm thread, so the same 795 working-set files,
698 Encyclopedia paths and 7,201 hover probes were walked once per watch
(visible in the owner's log as every progress line printed two and three
times).

After: **1.46 s** to three dials, **zero** recolors on the GUI thread.

The four laws pinned here, one test each:

1. A first paint runs NO metal recolor — it stands the masters in.
2. The background drain builds them, and the repaint shows the real metal.
3. The warm runs ONCE for the process, and only after every dial painted.
4. Legend off ⇒ the hover sweep does not run at all.
"""

import os
import threading
from datetime import datetime
from zoneinfo import ZoneInfo

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import astral
import pytest
from PySide6.QtWidgets import QApplication

import render.assets as assets_module
from app.controller import build_skin
from app.settings_store import Settings, replace
from config import paths
from core.clock_state import build_day_context, build_tick_state
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from render import asset_recolor
from render.art_warm import warm_pending_art
from render.asset_recolor import pending_art
from render.assets import AssetCache
from render.compositor import Compositor


@pytest.fixture
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def cold_cache(tmp_path, monkeypatch):
    """A raster cache with nothing in it, and an EMPTY ledger — the state
    every launch after an art wave or a version bump finds itself in
    (the cache key carries the source mtime, the shade and
    METAL_SWAP_VERSION, so any of the three moving empties it)."""
    monkeypatch.setattr(
        paths, "settings_path", lambda index=1: tmp_path / "settings.json"
    )
    monkeypatch.setattr(asset_recolor.paths, "settings_path", paths.settings_path)
    monkeypatch.setattr(asset_recolor, "_PENDING_VARIANTS", {})
    return tmp_path


def _dial(skin):
    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 7, 10, 12, 0, tzinfo=tz)
    day = build_day_context(
        now, astral.Observer(latitude=44.82, longitude=20.46),
        SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    return Compositor(skin, AssetCache()), day, build_tick_state(now, day)


def test_first_paint_runs_no_metal_recolor(app, cold_cache, monkeypatch):
    """THE PIN. A cold first paint must not recolor a single pixel — the
    dial draws its masters and gets out of the way."""
    calls = []
    original = AssetCache._recolored
    monkeypatch.setattr(
        AssetCache, "_recolored",
        staticmethod(lambda *a, **k: (calls.append(a[1]), original(*a, **k))[1]),
    )
    compositor, day, tick = _dial(
        build_skin(replace(Settings(), ring="DOMY", ring_finish="thematic"))
    )
    image = compositor.render_offscreen(360.0, 1.0, day, tick)

    assert not image.isNull()
    assert calls == [], f"first paint recolored {len(calls)} images: {calls}"
    # ...and it did not simply skip the letters: it RECORDED them for the
    # background, which is what makes the deferral honest rather than lossy.
    assert pending_art(), "the paint recorded no work for the warm to do"


def test_background_drain_upgrades_the_dial(app, cold_cache):
    """The other half of the promise (owner: "Kad završi prikaže") — the
    warm builds the real metal and the next paint is genuinely different."""
    compositor, day, tick = _dial(
        build_skin(replace(Settings(), ring="DOMY", ring_finish="thematic"))
    )
    masters = compositor.render_offscreen(360.0, 1.0, day, tick)

    assert warm_pending_art() > 0
    assert pending_art() == [], "the drain left work behind"

    compositor.invalidate()
    dressed = compositor.render_offscreen(360.0, 1.0, day, tick)
    differing = sum(
        1
        for x in range(0, masters.width(), 4)
        for y in range(0, masters.height(), 4)
        if masters.pixelColor(x, y) != dressed.pixelColor(x, y)
    )
    assert differing > 0, "the recolored dial is identical to the master one"


def test_the_warm_starts_once_and_only_after_every_dial_painted(monkeypatch):
    """Owner 2026-07-28: *"zašto bi se stvari učitavale više puta za svaki
    sat kada svi dele iste"*. One thread for the process — and not one
    tick before the last dial is on screen."""
    from app.watch_manager import AppController

    started = []
    monkeypatch.setattr(
        AppController, "_run_warm", lambda self, watches: started.append(watches)
    )
    manager = AppController.__new__(AppController)
    manager._quitting = False
    manager._warm_thread = None
    one, two, three = object(), object(), object()
    manager._watches = [one, two, three]
    manager._armed = {one, two, three}
    pending = set(manager._watches)

    manager._watch_painted(one, pending)
    manager._watch_painted(two, pending)
    assert started == [], "the warm jumped the gun before every dial painted"

    manager._watch_painted(three, pending)
    manager._warm_thread.join(timeout=5)
    assert len(started) == 1, "the warm ran once per watch instead of once"
    assert started[0] == [one, two, three]


def test_the_drain_builds_a_whole_batch_and_leaves_nothing(app, cold_cache):
    """The pooled drain (0.14.704) keeps the serial contract: every
    recorded recipe built exactly once, the ledger left empty, one
    on_ready per landed finish."""
    letters_dir = paths.assets_dir() / "instrument" / "ring" / "letters"
    letters = [letters_dir / name for name in ("A.png", "B.png", "C.png", "D.png")]
    for letter in letters:
        assert letter.exists()
        asset_recolor.letter_metal_file(letter, "silver")

    landed = []
    built = warm_pending_art(on_ready=lambda: landed.append(True))

    assert built == len(letters)
    assert len(landed) == len(letters)
    assert pending_art() == []
    for letter in letters:
        assert asset_recolor.letter_metal_path(letter, "silver").exists()


def test_a_finish_switch_after_the_warm_drains_again(app, cold_cache):
    """THE 2026-08-02 BUG: the startup warm was the ONLY drain of the
    art ledger, so a finish/shade/theme switch AFTER it finished
    recorded recipes nobody ever built — the dial stayed gold until the
    process restarted. The law: a paint that observes a missing finish
    rings `asset_recolor`'s stale notifier, and the manager's
    `kick_art_warm` drains the ledger without any restart."""
    from app.watch_manager import AppController
    from config.paths import art_file

    manager = AppController.__new__(AppController)
    manager._quitting = False
    startup = threading.Thread(target=lambda: None)  # the one startup
    startup.start()                                  # warm: came, went
    startup.join()
    manager._warm_thread = startup
    manager._art_lock = threading.Lock()
    manager._art_thread = None
    manager._art_rerun = False
    manager._watches = []
    asset_recolor.set_art_stale_notifier(manager.kick_art_warm)
    try:
        letter = paths.assets_dir() / "instrument" / "ring" / "letters" / "A.png"
        assert letter.exists(), "the test master must exist"

        # The paint under the NEW finish: records the recipe, observes
        # the miss, stands the gold master in — and rings the notifier.
        stand_in = asset_recolor.letter_metal_file(letter, "silver")
        assert stand_in == art_file(letter), "the miss must stand the master in"

        assert manager._art_thread is not None, (
            "the miss never kicked a drain — the 2026-08-02 bug is back"
        )
        manager._art_thread.join(timeout=120)
        assert not manager._art_thread.is_alive(), "the drain hung"
        assert pending_art() == [], "the kicked drain left work behind"
        derived = asset_recolor.letter_metal_path(letter, "silver")
        assert derived.exists(), "the switched finish was never built"
        assert asset_recolor.letter_metal_file(letter, "silver") == derived
    finally:
        asset_recolor.set_art_stale_notifier(None)


def test_warm_working_set_builds_cold_copies_in_children(tmp_path, monkeypatch):
    """THE 75-SECOND DEAD WINDOW (owner log 2026-07-31): a cold working
    set decoded/scaled/encoded multi-MB PNGs on the warm THREAD, and
    each of those Qt calls held the GIL for seconds — the GUI thread
    could not run a single event handler, so the dial was unmovable and
    the right-click menu dead for the whole cold stretch. The law: cold
    working-set builds happen in CHILD PROCESSES (their own GIL); the
    warm thread only waits and reports."""
    from PySide6.QtGui import QColor, QImage

    from config import defaults
    from render import asset_variants

    tree = tmp_path / "assets" / "weeks"
    tree.mkdir(parents=True)
    source = QImage(900, 600, QImage.Format.Format_ARGB32)
    source.fill(QColor("#8B6914"))
    assert source.save(str(tree / "big.png"))

    monkeypatch.setattr(paths, "assets_dir", lambda: tmp_path / "assets")
    monkeypatch.setattr(
        paths, "settings_path", lambda index=1: tmp_path / "settings.json"
    )
    monkeypatch.setattr(defaults, "WORKING_SET_CEILINGS", {"weeks": 400})

    built = asset_variants.warm_working_set()

    assert built == 1
    cache = asset_variants._scaled_cache_path(tree / "big.png", 400)
    assert cache.exists(), "the cold copy never landed"
    copy = QImage(str(cache))
    assert copy.width() == 400, "the working copy must be scaled to the ceiling"
    # A second pass is a no-op — the scan itself is the verification.
    assert asset_variants.warm_working_set() == 0


def test_legend_off_skips_the_hover_sweep_entirely(app, monkeypatch):
    """The owner's three watches all run with the legend OFF, and his
    2026-07-28 log shows each of them walking the full 40x180 grid to
    report "0 articles spoken". Warming what can never be shown is
    waste; the sweep must not probe at all."""
    compositor, day, tick = _dial(
        build_skin(replace(Settings(), legend=False))
    )
    compositor.set_day(day)
    compositor.render_offscreen(360.0, 1.0, day, tick)   # sets _last_tick

    def forbidden(*args, **kwargs):
        raise AssertionError("the sweep probed with the legend off")

    monkeypatch.setattr(Compositor, "_tooltip_at", forbidden)
    assert compositor.warm_hover_articles(360.0) == 0
