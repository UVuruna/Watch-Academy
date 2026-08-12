"""THE SLOW START (owner report 2026-07-28) — the regression pins.

Measured before the fix, on a cold raster cache: the owner's three
watches took **14.78 s** to put a dial on screen (4.20 + 4.79 + 5.67),
every second of it inside `paintEvent`. cProfile attributed it entirely
to 15 metal recolors per watch through `jewel_metal_file` — 3.45 s of
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

MIGRATE-GUI PHASE 1 (owner bar 2026-08-09) added a SECOND dead window
the first round never audited: `AssetCache.pixmap_by_height`'s own
inline WORKING-SET build on a cache miss — decode/downscale/encode a
multi-MB PNG straight inside `paintEvent`, measured at 71.7 s cold on
the owner's machine (`profiling.json`, "Working set warmup"). The laws
pinned in the `WorkingSet` section below mirror the four above for this
second resource, one test each:

5. A cold paint under a WORKING-SET ceiling runs NO inline build — it
   records the recipe and returns `None` (never the full-res original).
6. A source AT OR UNDER its subtree's ceiling is never treated as
   pending at all (the bug this very round shipped once, mid-session,
   before this test caught it: an unconditional ledger entry for EVERY
   asset under a covered subtree, icons and thumbnails included).
7. The background drain builds the recorded copies and clears the
   ledger, one `on_ready` per landed file.
8. `app.warm.run_warm` drains the ledger BEFORE the alphabetical
   whole-tree sweep (VISIBLE-FIRST warmup).
9. A miss after the startup warm (a skin switch, on-demand) still
   drains, exactly like the art ledger's own `kick_art_warm`.
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
    jewels_dir = paths.assets_dir() / "instrument" / "letters" / "latin"
    letters = [jewels_dir / name for name in ("A.png", "B.png", "C.png", "D.png")]
    for letter in letters:
        assert letter.exists()
        asset_recolor.jewel_metal_file(letter, "silver")

    landed = []
    built = warm_pending_art(on_ready=lambda: landed.append(True))

    assert built == len(letters)
    assert len(landed) == len(letters)
    assert pending_art() == []
    for letter in letters:
        assert asset_recolor.jewel_metal_path(letter, "silver").exists()


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
        letter = paths.assets_dir() / "instrument" / "letters" / "latin" / "A.png"
        assert letter.exists(), "the test master must exist"

        # The paint under the NEW finish: records the recipe, observes
        # the miss, stands the gold master in — and rings the notifier.
        stand_in = asset_recolor.jewel_metal_file(letter, "silver")
        assert stand_in == art_file(letter), "the miss must stand the master in"

        assert manager._art_thread is not None, (
            "the miss never kicked a drain — the 2026-08-02 bug is back"
        )
        manager._art_thread.join(timeout=120)
        assert not manager._art_thread.is_alive(), "the drain hung"
        assert pending_art() == [], "the kicked drain left work behind"
        derived = asset_recolor.jewel_metal_path(letter, "silver")
        assert derived.exists(), "the switched finish was never built"
        assert asset_recolor.jewel_metal_file(letter, "silver") == derived
    finally:
        asset_recolor.set_art_stale_notifier(None)


def test_art_ready_bursts_collapse_into_one_repaint(app):
    """0.14.707: the pooled drain lands finishes in bursts, and a full
    composite rebuild per landed file repainted nothing the trailing
    rebuild would not show. One quiet window after the LAST arrival =
    exactly one refresh + one update — and never a whole-cache flush."""
    from PySide6.QtCore import QTimer
    from PySide6.QtTest import QTest

    from app.controller import WatchController
    from config import defaults

    class FakeCache:
        pending_clears = 0

        def clear_pending(self):
            FakeCache.pending_clears += 1

    class FakeCompositor:
        refreshes = 0
        flushes = 0

        def __init__(self):
            self._cache = FakeCache()

        def refresh_composites(self):
            FakeCompositor.refreshes += 1

        def invalidate(self):
            FakeCompositor.flushes += 1

    class FakeWidget:
        updates = 0

        def update(self):
            FakeWidget.updates += 1

    controller = WatchController.__new__(WatchController)
    controller._compositor = FakeCompositor()
    controller._widget = FakeWidget()
    controller._art_repaint_timer = QTimer()
    controller._art_repaint_timer.setSingleShot(True)
    controller._art_repaint_timer.setInterval(defaults.ART_REPAINT_DEBOUNCE_MS)
    controller._art_repaint_timer.timeout.connect(controller._apply_art_now)

    for _ in range(17):                    # a whole drain burst
        controller.apply_pending_art()
    # Deadline, not a fixed window: a loaded machine may delay the
    # timer past any fixed wait and turn the pin into a flake.
    deadline = 5000
    waited = 0
    while FakeCompositor.refreshes == 0 and waited < deadline:
        QTest.qWait(50)
        waited += 50
    QTest.qWait(defaults.ART_REPAINT_DEBOUNCE_MS * 2)   # grace: a 2nd fire?

    assert FakeCompositor.refreshes == 1, "a burst must repaint ONCE"
    assert FakeWidget.updates == 1
    assert FakeCompositor.flushes == 0, "an art repaint must not flush assets"
    assert FakeCache.pending_clears == 1, (
        "the pending working-set markers must get exactly one chance too"
    )


def test_the_menu_status_row_mirrors_the_manager(app):
    """0.14.710 (owner: "INFO LOADING ... NIKAKO LAG STUCK SCREEN"): the
    context menu's status row shows the manager's live warm/drain line
    while background work runs, and hides the moment it is idle."""
    from PySide6.QtGui import QAction
    from PySide6.QtWidgets import QLabel

    from app.controller import WatchController

    controller = WatchController.__new__(WatchController)
    controller._warm_status_label = QLabel()
    controller._warm_status_action = QAction("status")
    controller._warm_status_provider = None
    controller._refresh_warm_status_row()
    assert not controller._warm_status_action.isVisible()

    status = {"line": "[2.1s] working set 40/908 (4%)"}
    controller._warm_status_provider = lambda: status["line"]
    controller._refresh_warm_status_row()
    assert controller._warm_status_action.isVisible()
    assert controller._warm_status_label.text() == status["line"]

    status["line"] = None
    controller._refresh_warm_status_row()
    assert not controller._warm_status_action.isVisible()


def test_art_repaint_keeps_the_rasterized_assets(app, cold_cache):
    """`refresh_composites` drops the composite groups alone — the
    decoded/rasterized assets survive, because a landed finish resolves
    under a NEW cache key and nothing else changed."""
    compositor, day, tick = _dial(build_skin(Settings()))
    compositor.render_offscreen(360.0, 1.0, day, tick)
    held = len(compositor._cache._pixmaps)
    assert held > 0, "the paint decoded nothing — the pin lost its subject"

    compositor.refresh_composites()

    assert len(compositor._cache._pixmaps) == held
    assert compositor._composites == [None] * len(compositor._cached_groups)


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


# --- THE 75-SECOND DEAD CLOCK (owner bar 2026-08-09, MIGRATE-GUI Phase 1) ---
#
# `AssetCache.pixmap_by_height`'s own inline working-set build, never
# audited by the round above: a cache miss under a WORKING_SET_CEILINGS
# subtree used to call `scaled_variant_file(path, ceiling)` (default
# `build=True`) — decode/downscale/encode a multi-MB PNG, INSIDE
# `paintEvent`, on the GUI thread. Fixed the same shape as the metal
# ledger above: a miss RECORDS the recipe and returns `None`; the pixels
# build off the GUI thread and a debounced signal repaints.

@pytest.fixture
def working_set_tree(tmp_path, monkeypatch):
    """An isolated assets tree with one oversized PNG under a covered
    subtree and one UNDERSIZED one under the same subtree — the second
    file is what pins the "small sources are never pending" law."""
    from PySide6.QtGui import QColor, QImage

    from config import defaults
    from render import asset_variants

    tree = tmp_path / "assets" / "weeks"
    tree.mkdir(parents=True)
    big = QImage(900, 600, QImage.Format.Format_ARGB32)
    big.fill(QColor("#8B6914"))
    assert big.save(str(tree / "big.png"))
    small = QImage(200, 150, QImage.Format.Format_ARGB32)
    small.fill(QColor("#2244AA"))
    assert small.save(str(tree / "small.png"))

    monkeypatch.setattr(paths, "assets_dir", lambda: tmp_path / "assets")
    monkeypatch.setattr(
        paths, "settings_path", lambda index=1: tmp_path / "settings.json"
    )
    monkeypatch.setattr(defaults, "WORKING_SET_CEILINGS", {"weeks": 400})
    monkeypatch.setattr(asset_variants, "_PENDING_WORKING", {})
    return tmp_path, tree


def test_cold_working_set_paint_never_builds_inline(app, working_set_tree, monkeypatch):
    """THE PIN (deliverable 1 and 4 of the MIGRATE-GUI round): a cold
    paint under a working-set ceiling must never call the decode/
    downscale/encode builder itself — it records the recipe and stands
    down, returning `None` rather than the full-res original."""
    from render import asset_variants
    from render.assets import AssetCache

    _tmp_path, tree = working_set_tree
    calls = []
    monkeypatch.setattr(
        asset_variants, "build_scaled_copy",
        lambda *a, **k: calls.append(a) or (_ for _ in ()).throw(
            AssertionError("the GUI paint path built a working-set copy inline")
        ),
    )

    cache = AssetCache()
    pixmap = cache.pixmap_by_height(tree / "big.png", 300.0, 1.0)

    assert pixmap is None, "a cold miss must stand down, never the full-res original"
    assert calls == [], "pixmap_by_height must never build inline"
    pending = asset_variants.pending_working()
    assert len(pending) == 1
    assert pending[0].exists() is False


def test_working_set_miss_rings_the_stale_notifier(app, working_set_tree, monkeypatch):
    """The twin of `test_a_finish_switch_after_the_warm_drains_again`'s
    notifier check, for the working-set ledger: a miss observed during a
    paint must ring the installed notifier so a background drain gets
    kicked without waiting for a restart."""
    from render import asset_variants
    from render.assets import AssetCache

    _tmp_path, tree = working_set_tree
    rung = []
    asset_variants.set_working_stale_notifier(lambda: rung.append(True))
    try:
        AssetCache().pixmap_by_height(tree / "big.png", 300.0, 1.0)
        assert rung == [True]
    finally:
        asset_variants.set_working_stale_notifier(None)


def test_asset_at_or_under_the_ceiling_is_never_pending(app, working_set_tree):
    """THE REGRESSION THIS ROUND SHIPPED ONCE, MID-SESSION: treating
    every asset under a covered subtree as needing a working copy —
    icons and thumbnails well under any ceiling included — made those
    permanently 'pending' and silently invisible. A source AT OR UNDER
    the ceiling must resolve on the very FIRST call, no ledger entry, no
    background wait."""
    from render import asset_variants
    from render.assets import AssetCache

    _tmp_path, tree = working_set_tree
    assert asset_variants.working_variant_path(tree / "small.png", 400) == (
        tree / "small.png"
    )

    pixmap = AssetCache().pixmap_by_height(tree / "small.png", 100.0, 1.0)

    assert pixmap is not None, "an undersized source must never come back None"
    assert asset_variants.pending_working() == []


def test_drain_pending_working_builds_and_clears_the_ledger(app, working_set_tree):
    """The batch drain (`app.warm.run_warm`'s VISIBLE-FIRST phase and
    `AppController.kick_working_warm`'s on-demand twin both call this):
    every recorded recipe built exactly once, the ledger left empty, one
    `on_ready` per landed copy — `test_the_drain_builds_a_whole_batch_
    and_leaves_nothing`'s exact shape for the OTHER ledger."""
    from PySide6.QtGui import QImage

    from render import asset_variants

    _tmp_path, tree = working_set_tree
    recorded = asset_variants.working_variant_path(tree / "big.png", 400)
    assert recorded != tree / "big.png"
    assert asset_variants.pending_working() == [recorded]

    landed = []
    built = asset_variants.drain_pending_working(on_ready=lambda: landed.append(True))

    assert built == 1
    assert len(landed) == 1
    assert asset_variants.pending_working() == []
    assert recorded.exists()
    assert QImage(str(recorded)).width() == 400


def test_run_warm_drains_the_working_ledger_before_the_bulk_sweep(monkeypatch):
    """VISIBLE-FIRST warmup (deliverable 2): the ledger IS the active
    skin's own referenced oversized art (a paint is what records it), so
    `app.warm.run_warm` must drain it before the alphabetical whole-tree
    sweep — otherwise a subtree that happens to sort first could hog the
    cold minutes ahead of what is actually on screen."""
    import app.warm as warm_module

    order = []
    monkeypatch.setattr(
        warm_module, "warm_pending_art",
        lambda **k: order.append("art") or 0,
    )
    monkeypatch.setattr(
        warm_module, "drain_pending_working",
        lambda **k: order.append("working_drain") or 0,
    )
    monkeypatch.setattr(
        warm_module, "warm_working_set",
        lambda **k: order.append("working_sweep") or 0,
    )
    monkeypatch.setattr(
        warm_module, "warm_encyclopedia", lambda **k: order.append("encyclopedia")
    )
    monkeypatch.setattr(
        warm_module, "_collect_cache_garbage", lambda **k: order.append("gc")
    )

    warm_module.run_warm()

    assert order == [
        "art", "working_drain", "working_sweep", "encyclopedia", "gc",
    ]


def test_a_working_set_miss_after_the_warm_drains_again(app, working_set_tree):
    """THE 2026-08-02 BUG's twin for the OTHER ledger: the startup warm
    is not the only drain. A miss recorded AFTER it finished (a skin
    switch, a time-travel day pulling in different art) still gets
    built, through `AppController.kick_working_warm` — no restart."""
    from app.watch_manager import AppController
    from render import asset_variants
    from render.assets import AssetCache

    _tmp_path, tree = working_set_tree
    manager = AppController.__new__(AppController)
    manager._quitting = False
    startup = threading.Thread(target=lambda: None)  # the one startup
    startup.start()                                   # warm: came, went
    startup.join()
    manager._warm_thread = startup
    manager._working_lock = threading.Lock()
    manager._working_thread = None
    manager._working_rerun = False
    manager._watches = []
    asset_variants.set_working_stale_notifier(manager.kick_working_warm)
    try:
        cache = AssetCache().pixmap_by_height(tree / "big.png", 300.0, 1.0)
        assert cache is None, "the miss must stand down, not build inline"

        assert manager._working_thread is not None, (
            "the miss never kicked a drain"
        )
        manager._working_thread.join(timeout=120)
        assert not manager._working_thread.is_alive(), "the drain hung"
        assert asset_variants.pending_working() == [], (
            "the kicked drain left work behind"
        )
    finally:
        asset_variants.set_working_stale_notifier(None)


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
