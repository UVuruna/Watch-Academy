"""Disk-cached derived images that are not metal recolors — the
"working set" downscale family, the moon-phase live render, the
subdial plate resolver, and the two computed icon families (calendar
wheel, solar eclipse type). Split out of `assets.py` (surgical sibling
extraction, `research/REFACTOR_PLAN.md` §8). See
[Asset Variants](asset_variants.md) for the full recipe.

`AssetCache.pixmap_by_height` (`assets.py`) reads `working_ceiling`/
`working_variant_path`/`working_stale_notify` back from this module — a
genuine two-way edge between the two files, since `AssetCache` stays in
`assets.py` while these helpers moved here. `assets.py` resolves it
with a LOCAL import inside `pixmap_by_height` instead of a module-level
one, so the two modules' top-level imports never form a cycle; see that
method's own comment for why.

THE LAZY WORKING-SET LEDGER (owner bar 2026-08-09, MIGRATE-GUI Phase 1
— "the 75-second dead clock"): `_PENDING_WORKING`/`working_variant_path`/
`pending_working`/`ensure_working_variant`/`drain_pending_working` mirror
`asset_recolor.py`'s `_PENDING_VARIANTS`/`jewel_metal_path`/`pending_art`/
`ensure_variant`/`warm_pending_art` SHAPE for a different resource: the
GUI paint path used to call `scaled_variant_file(path, ceiling)` (default
`build=True`) on a cache MISS, decoding a multi-MB PNG INSIDE
`paintEvent`. `AssetCache.pixmap_by_height` now only ever NAMES a
working-set copy through `working_variant_path` (pure) and returns
`None` on a miss instead of building or falling back to the full-res
original; the pixels are built off the GUI thread, by
`app.warm.run_warm`'s VISIBLE-FIRST phase at startup or
`app.watch_manager.AppController.kick_working_warm` on demand, both
through `drain_pending_working` below. `scaled_variant_file` itself is
UNCHANGED and stays in service for its own callers (hover tooltips,
Encyclopedia cards/readers) — a distinct, arbitrary-width, build-on-
first-use cache the ledger does not cover.
"""

import math
import os
import sys
import threading
from pathlib import Path

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import (
    QColor, QImage, QImageReader, QPainter, QPainterPath, QPen, QPixmap,
)

from config import (
    constants, defaults, dial, palette, pantheon, paths, profiling, shortcuts,
)
from config.paths import art_file
from render import raster_store
from render.asset_recolor import _recolored_plate, tinted_pixmap


_ring_face_colors: dict[str, QColor] = {}


def ring_face_color(path: Path | None) -> QColor:
    """The ring art's own FACE color — the slot-roundel fill (owner
    2026-07-14: 'boja unutar kruga je RING preset boja'). Sampled once
    per file: walk the top center column to the first opaque band,
    then read a ring of pixels a few steps deeper and take the MEDIAN
    by luminance, so numerals and ticks (the bright minority) never
    win. Missing/unreadable art falls back to the documented color."""
    if path is None:
        return QColor(palette.SLOT_ROUNDEL_FILL_FALLBACK)
    key = str(path)
    cached = _ring_face_colors.get(key)
    if cached is not None:
        return cached
    image = QImage(key)
    color = QColor(palette.SLOT_ROUNDEL_FILL_FALLBACK)
    if not image.isNull():
        center = image.width() // 2
        top = next(
            (
                y for y in range(image.height() // 2)
                if image.pixelColor(center, y).alpha() > 200
            ),
            None,
        )
        if top is not None:
            depth = top + max(3, image.height() // 40)
            radius = image.height() / 2.0 - depth
            samples = []
            for step in range(0, 360, 9):
                angle = math.radians(step)
                probe = image.pixelColor(
                    round(center + radius * math.sin(angle)),
                    round(image.height() / 2.0 - radius * math.cos(angle)),
                )
                if probe.alpha() > 200:
                    samples.append(probe)
            if samples:
                samples.sort(key=lambda c: c.lightness())
                color = samples[len(samples) // 2]
    _ring_face_colors[key] = color
    return color


# The MOON terminator geometry (owner 2026-07-16; quarter-degeneracy
# fix 2026-07-19, live-render round): the lit region is the half-disc
# on the lit side combined (gibbous) or reduced (crescent) with the
# terminator half-ellipse (semi-axis a = R*|cos(2*pi*f)|). ONE shared
# function — `render.layers.year_marker.YearMarkerLayer._draw_moon` (the dial) and
# `moon_phase_image` below (the Encyclopedia's live-rendered Moon
# pages) both call it, so the two never drift apart.
MOON_TERMINATOR_EPSILON = 1e-6   # of the radius — the exact-quarter guard


def moon_lit_region(fraction: float, radius: float) -> QPainterPath:
    """The lit region of a moon disc of `radius` centered at the
    origin (waxing, fraction < 0.5, lit on the right). AT THE EXACT
    QUARTERS (fraction 0.25 / 0.75) the terminator semi-axis is
    mathematically zero: Qt's `addEllipse` on a zero-width rect
    degenerates, and routing that through `united`/`subtracted`
    resolves to an EMPTY path — the moon rendered fully dark instead
    of exactly half-lit (the bug the pre-rendered plates shipped with
    at first/third quarter). Fixed by skipping the boolean op
    entirely whenever the semi-axis collapses and returning the
    half-disc outright — the mathematically exact answer at a
    quarter anyway."""
    size = 2.0 * radius
    lit_right = fraction < 0.5
    half = QPainterPath()
    half.moveTo(0.0, -radius)
    # 90 deg is the top in Qt's CCW system; sweep -180 covers the right
    # half, +180 the left half.
    half.arcTo(
        QRectF(-radius, -radius, size, size),
        90.0, -180.0 if lit_right else 180.0,
    )
    half.closeSubpath()
    semi_axis = radius * abs(math.cos(2.0 * math.pi * fraction))
    if semi_axis <= radius * MOON_TERMINATOR_EPSILON:
        return half
    gibbous = 0.25 < fraction < 0.75
    terminator = QPainterPath()
    terminator.addEllipse(QRectF(-semi_axis, -radius, 2.0 * semi_axis, size))
    return half.united(terminator) if gibbous else half.subtracted(terminator)


def moon_phase_image(
    fraction: float, size: int, master: Path | None = None,
    style: str | None = None,
) -> QImage:
    """The full-moon master art treated by the CURRENT unlit-half style
    for the given illuminated FRACTION — the pure render the
    Encyclopedia's Moon pages call live instead of shipping eight
    pre-baked plates (owner decree 2026-07-19: better to draw on the
    spot than ship 15 MB of files).

    It draws through `render.moon_face.draw_moon_disc`, the SAME
    function the dial uses, so the book and the instrument can never
    disagree about what a crescent looks like. That mattered
    immediately: when the owner retired the translucent wash on
    2026-08-10 this renderer still carried its own copy of it, and the
    Encyclopedia would have gone on printing the retired treatment
    beside a dial that no longer drew it. `style` defaults to
    `constants.MOON_DARK_STYLE_DEFAULT` because these images are cached
    by (phase, size) on disk and shared process-wide — they are not
    per-watch, so they follow the shipped default rather than one
    window's pick.

    QImage end to end (the R1b threading law) — the background
    Encyclopedia warm renders the eight phase plates off the GUI
    thread, where QPixmap is forbidden."""
    # Imported here, not at module scope: `render.moon_face` imports
    # `moon_lit_region` from THIS module, so a top-level import would
    # close the cycle.
    from render.moon_face import draw_moon_disc

    marker = defaults.DEFAULT_SKIN.year_marker
    resolved = art_file(
        master if master is not None
        else pantheon.weekday_art("planets/primary/photo/Moon.png")
    )
    image = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    painter.translate(size / 2.0, size / 2.0)
    painter.setPen(Qt.PenStyle.NoPen)
    radius = size / 2.0
    has_asset = resolved is not None and resolved.exists()

    def paint_face(target: QPainter) -> None:
        """The FULL-moon face: the master art when it resolves, a flat
        lit disc when it does not — the same graceful degradation the
        dial itself falls back to."""
        if has_asset:
            art = QImage(str(resolved)).scaled(
                size, size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            target.drawImage(
                QPointF(-art.width() / 2.0, -art.height() / 2.0), art
            )
            return
        target.setBrush(QColor(marker.moon_lit_color))
        target.drawEllipse(QPointF(0, 0), radius, radius)

    draw_moon_disc(
        painter, fraction, radius,
        style if style is not None else constants.MOON_DARK_STYLE_DEFAULT,
        paint_face, marker.moon_dark_color,
    )
    painter.end()
    return image


def moon_phase_file(fraction: float, name: str, size: int = 800) -> Path:
    """A disk-cached copy of `moon_phase_image` — the Encyclopedia's
    Moon topic wants a PATH like every other article image (owner
    2026-07-19: the eight pre-baked plates in `assets/moon/` are
    retired; this is the live-render replacement, the cost paid once
    per (phase, size) through the raster cache instead of shipping
    ~7 MB of PNGs)."""
    master = art_file(pantheon.weekday_art("planets/primary/photo/Moon.png"))
    cache = (
        paths.settings_path().parent / "raster_cache"
        / f"{raster_store.source_prefix(master)}_moon_{name}_{size}.png"
    )
    if not cache.exists():
        image = moon_phase_image(fraction, size, master)
        try:
            raster_store.atomic_save(image, cache)
        except OSError as error:
            # A cold cache is only slower, never wrong — but say so.
            print(f"moon phase cache write failed: {error}", file=sys.stderr)
            return master
    return cache


def subdial_plate_file(
    finish: str, tint: str | None = None
) -> Path | None:
    """The active SUBDIAL SET's plate for `finish` (owner decree
    2026-07-21, Rsub round — retires the Rule #19 one-master-per-source
    model this function used to implement). The set itself is picked in
    Settings and lives as a `config.paths` module global
    (`paths.subdial_set()`, mirroring the art-source switch exactly) —
    it is NOT threaded as a parameter here since this is its only
    reader, keeping `render.subdial.draw_slot_roundel`'s existing call
    untouched.

    Sets 1-4 are three hand-drawn finishes each: the matching file
    returns AS DRAWN, no recolor, no cache — the seat dimension never
    touched this function even before (only the LIVE shadow,
    `render.subdial._draw_subdial_shadow`, keyed off the seat's own dial
    position, does). The SOLO set ships one hand-drawn file
    (`dial.SUBDIAL_SOLO_FINISH`, silver): silver wins AS DRAWN,
    gold/bronze are disk-cached live recolors of it, exactly like the
    ring jewels derive silver/bronze from gold. A TINT (the "theme"
    plate style, owner 2026-07-15 A/B spec) recolors the dark
    tapisserie field to the clock tint on TOP of whichever plate above
    was resolved — that pass runs even on an already-correct finish,
    into its own cache entry. None = no plate art at all for the active
    set (the layer then draws the procedural circle)."""
    active_set = paths.subdial_set()
    if active_set == "solo":
        master = (
            dial.SUBDIAL_ROOT_DIR / "solo"
            / f"{dial.SUBDIAL_SOLO_FINISH}.png"
        )
        if not master.exists():
            return None
        if finish == dial.SUBDIAL_SOLO_FINISH and tint is None:
            return master
        return _recolored_plate(master, finish, tint)
    plate = dial.SUBDIAL_ROOT_DIR / active_set / f"{finish}.png"
    if not plate.exists():
        return None
    if tint is None:
        return plate
    return _recolored_plate(plate, finish, tint)


def _scaled_cache_path(path: Path, width: int) -> Path:
    """Where `path`'s downscaled-to-`width` copy lives. The source
    STEM rides the name — hover tests and humans can read which face
    a derived file came from."""
    return (
        paths.settings_path().parent / "raster_cache"
        / f"{raster_store.source_prefix(path)}_w{width}_{path.stem}.png"
    )


def working_ceiling(path: Path | None) -> int | None:
    """The WORKING-SET ceiling of an asset (owner 2026-07-15): the
    subtree under assets/ names the largest pixel size the dial can
    ever ask of it — None for trees the dial never draws (guide,
    instrument reader art) and for paths outside assets/."""
    if path is None:
        return None
    try:
        rel = path.relative_to(paths.assets_dir()).as_posix()
    except ValueError:
        return None
    # Keys may be multi-segment (RESTRUCTURE: `celestial/earth` at 800 vs
    # `celestial/seasons` at 1200) — match the longest declared prefix.
    for subtree, ceiling in defaults.WORKING_SET_CEILINGS.items():
        if rel == subtree or rel.startswith(subtree + "/"):
            return ceiling
    return None


# THE LAZY WORKING-SET LEDGER (owner bar 2026-08-09, MIGRATE-GUI Phase 1
# — "the 75-second dead clock"): the mirror of `asset_recolor.py`'s
# `_PENDING_VARIANTS` for this OTHER derived-image family. Root cause of
# the dead window: `AssetCache.pixmap_by_height` used to call
# `scaled_variant_file(path, ceiling)` (default `build=True`) on a cache
# MISS — decode + smooth-downscale + PNG-encode a multi-MB source,
# INSIDE `paintEvent`, on the GUI thread (the same GIL-holding cost
# `warm_working_set`'s own docstring already measured in seconds). Unlike
# a metal recolor, there is no cheap stand-in to draw instead — the only
# "fallback" is the very full-res decode being avoided. So the paint
# path no longer builds AND no longer falls back to the original: a miss
# just RECORDS the (source, ceiling) recipe here (pure, no pixel work)
# and the caller gets back `None` — draw nothing for this element THIS
# frame, exactly like a not-yet-recolored jewel stands in gold, except
# here there is nothing honest to stand in, so the compositor skips it
# and the next repaint (rung by the same background-drain-and-signal
# mechanism `asset_recolor` already uses) shows it once real pixels
# exist. `working_variant_path` is the pure recorder; `pending_working`
# is the drain's worklist; `ensure_working_variant` materializes one
# recorded entry (any thread — QImage end to end, never QPixmap off the
# GUI thread, the R1b law); `drain_pending_working` below is the
# multi-entry, subprocess-backed batch drain both the startup warm
# (`app.warm.run_warm`, ahead of the alphabetical whole-tree sweep) and
# the on-demand kick (`app.watch_manager.AppController.kick_working_warm`,
# installed as this ledger's stale notifier) call.
_PENDING_WORKING: dict[str, tuple[Path, int]] = {}
_WORKING_LOCKS: dict[str, threading.Lock] = {}
_WORKING_LOCKS_GUARD = threading.Lock()

#: Rung by `working_variant_path` the moment a paint records a MISS —
#: the working-set twin of `asset_recolor._ART_STALE_NOTIFIER`. Must
#: stay cheap and thread-agnostic: it is called on the GUI thread inside
#: a paint.
_WORKING_STALE_NOTIFIER = None


def set_working_stale_notifier(notifier) -> None:
    """Install the callable rung when a paint records a MISSING
    working-set copy (`None` uninstalls — tests). One process, one
    notifier, mirroring `asset_recolor.set_art_stale_notifier`."""
    global _WORKING_STALE_NOTIFIER
    _WORKING_STALE_NOTIFIER = notifier


def working_stale_notify() -> None:
    """Ring the installed working-set stale notifier, if any —
    `AssetCache.pixmap_by_height`'s one call site, kept as a plain
    function (rather than a private module attribute reached from
    another module) so the paint path never touches this module's
    globals directly."""
    if _WORKING_STALE_NOTIFIER is not None:
        _WORKING_STALE_NOTIFIER()


def _working_lock(key: str) -> threading.Lock:
    with _WORKING_LOCKS_GUARD:
        lock = _WORKING_LOCKS.get(key)
        if lock is None:
            lock = _WORKING_LOCKS[key] = threading.Lock()
        return lock


def working_variant_path(path: Path, ceiling: int) -> Path:
    """WHERE `path`'s working-set downscale lives, when it needs one at
    all — a header-only computation (no pixel decode) that also RECORDS
    the (source, ceiling) recipe in the lazy ledger (the twin of
    `asset_recolor.jewel_metal_path`/`metal_variant_path`, Rule #5: one
    ledger SHAPE, two families).

    Returns `path` UNCHANGED, and records nothing, when the source is
    already at or under `ceiling` — the same "sources at or under the
    ceiling stay as they are" rule `warm_working_set`'s own tree scan
    and `scaled_variant_file` both already apply. A caller (`AssetCache.
    pixmap_by_height`) tells these two cases apart by comparing the
    return value against `path`: EQUAL means "no working copy needed,
    resolve the original as always" (a missing original still raises
    through the normal decode, exactly like every other asset); UNEQUAL
    means a real recipe was recorded and the cache path may not exist
    yet. Getting this wrong once already cost a round: treating every
    asset under a covered subtree as needing a copy — instrument
    thumbnails and icons included, most of them well under any ceiling —
    made those permanently 'pending' and silently invisible."""
    reader = QImageReader(str(path))
    size = reader.size()
    if not size.isValid() or size.width() <= ceiling:
        return path
    cache = _scaled_cache_path(path, ceiling)
    _PENDING_WORKING.setdefault(str(cache), (path, ceiling))
    return cache


def pending_working() -> list[Path]:
    """Every recorded working-set recipe whose file is still missing —
    in practice the CURRENT skin's own actually-referenced oversized
    art, because a paint is what records it. `app.warm.run_warm` drains
    THIS list before the alphabetical whole-tree sweep for exactly that
    reason (VISIBLE-FIRST warmup, owner bar 2026-08-09)."""
    return [
        Path(key) for key in list(_PENDING_WORKING)
        if not Path(key).exists()
    ]


def ensure_working_variant(path: Path | None) -> Path | None:
    """Materialize a `working_variant_path`-recorded downscale whose
    file is still missing — the ONE place `build_scaled_copy`'s
    decode/downscale/encode pays for a ledger entry (background drain,
    or an eager caller off the GUI thread; QImage end to end, R1b law).
    Paths this module never recorded pass through untouched. Returns the
    SOURCE file when the cache write fails (a cold cache is only slower,
    never wrong — but say so, Rule #1)."""
    if path is None:
        return None
    key = str(path)
    recipe = _PENDING_WORKING.get(key)
    if recipe is None or path.exists():
        return path
    with _working_lock(key):
        if path.exists():
            return path
        source, ceiling = recipe
        try:
            build_scaled_copy(str(source), key, ceiling)
        except OSError as error:
            print(f"working set drain build failed: {error}", file=sys.stderr)
            return source
    return path


def build_scaled_copy(source: str, cache: str, width: int) -> None:
    """Decode `source`, smooth-downscale to `width` px, atomic-save to
    `cache` — the ONE working-copy build, shared by the inline
    cache-miss path (`scaled_variant_file`) and the warmup's subprocess
    pool (Rule #5). Plain-string arguments and no config reads on
    purpose: a spawned child calls this with everything it needs in
    hand. Raises `OSError` on an unreadable source or a failed write —
    each caller keeps its own documented fallback."""
    scaled = QImage(source).scaledToWidth(
        width, Qt.TransformationMode.SmoothTransformation
    )
    if scaled.isNull():
        raise OSError(f"cannot decode image source: {source}")
    raster_store.atomic_save(scaled, Path(cache))


@profiling.timed("Working set warmup")
def warm_working_set(progress=None, should_stop=None) -> int:
    """Generate the DOWNSCALED working copies of every oversized dial
    asset (owner 2026-07-15: the originals ship full-res, the
    installation builds the working set). A no-op once warm; returns
    how many copies were (re)built.

    Cold builds run in a small SUBPROCESS pool (0.14.706, the owner's
    "75 sekundi mrtav sat"): PySide's QImage decode/smooth-scale/encode
    of a multi-MB source holds the GIL for SECONDS per call, so on the
    warm THREAD every such call froze the GUI thread with it — the
    window unmovable, the right-click menu dead, exactly as long as the
    cold items took. Child processes have their own GIL; the warm
    thread only waits on futures (which releases the GIL) and prints
    progress. If the pool cannot start or dies (a frozen build without
    multiprocessing support, an exhausted machine), the build falls
    back to the old in-thread loop — slower and GUI-hostile, but warm
    (Rule #1: degraded and visible, never absent)."""
    from concurrent.futures import as_completed, ProcessPoolExecutor
    from time import perf_counter

    from render import asset_index

    start = perf_counter()
    # SELF-SUFFICIENT, deliberately (regression caught by
    # `tests/test_startup_warm.py` before this shipped): the first draft
    # read the roster and trusted someone else — `app.warm` phase 0 — to
    # have filled it, so a caller that had not refreshed got a sweep
    # that silently built NOTHING and reported success. That is the same
    # class of failure as the bug this whole round is about. A refresh is
    # idempotent and costs ~0.16 s warm, so this pass pays it rather
    # than assume it.
    asset_index.refresh(should_stop=should_stop)
    if should_stop is not None and should_stop():
        return 0
    # THE INDEX IS THE ROSTER (0.14.950, the owner's 91.6-second launch).
    # This used to `rglob` five subtrees and open EVERY png in them —
    # 2,511 files, 3.76 GB — with `QImageReader`, to read one integer it
    # had already read on every previous launch. Cold, on an ordinary
    # HDD, that is the owner's 91.6 seconds, in which his own log proves
    # ZERO images were built. `app.warm` phase 0 has already walked the
    # tree once (~0.015 s, `os.scandir`), so the widths are simply
    # known; a genuinely new or changed file was opened there, once.
    todo: list[tuple[Path, int]] = [
        (source, ceiling)
        for subtree, ceiling in defaults.WORKING_SET_CEILINGS.items()
        for source, width in asset_index.widths_under(subtree)
        # PNG only, exactly as the old `rglob("*.png")` did — the index
        # also carries jpg/svg, which this family has never downscaled.
        if width > ceiling and source.suffix.lower() == ".png"
    ]
    cold = [
        (source, _scaled_cache_path(source, ceiling), ceiling)
        for source, ceiling in todo
        if not _scaled_cache_path(source, ceiling).exists()
    ]

    def report(done: int) -> None:
        if progress is not None and done % 10 == 0:
            elapsed = perf_counter() - start
            progress(
                f"[{elapsed:.1f}s] working set {done}/{len(cold)} "
                f"({done / len(cold) * 100:.0f}%)"
            )

    built = 0
    if cold:
        try:
            workers = max(1, min(defaults.WORKING_SET_WORKERS, os.cpu_count() or 1))
            with ProcessPoolExecutor(max_workers=workers) as pool:
                futures = [
                    pool.submit(build_scaled_copy, str(source), str(cache), width)
                    for source, cache, width in cold
                ]
                for future in as_completed(futures):
                    if should_stop is not None and should_stop():
                        for pending in futures:
                            pending.cancel()
                        break
                    try:
                        future.result()
                        built += 1
                    except OSError as error:
                        # One bad source is one missing working copy —
                        # the dial reads the original (slower, correct).
                        print(
                            f"working set build failed: {error}",
                            file=sys.stderr,
                        )
                    report(built)
        except Exception as error:
            print(
                f"working set pool unavailable ({error}); "
                "building in-thread",
                file=sys.stderr,
            )
            for source, cache, width in cold:
                if should_stop is not None and should_stop():
                    break
                if cache.exists():
                    continue
                try:
                    build_scaled_copy(str(source), str(cache), width)
                    built += 1
                except OSError as inner:
                    print(
                        f"working set build failed: {inner}",
                        file=sys.stderr,
                    )
                report(built)
    if progress is not None and todo:
        progress(
            f"[{perf_counter() - start:.1f}s] working set complete — "
            f"{len(todo)} oversized sources, {built} built cold"
        )
    return built


@profiling.timed("Working set drain")
def drain_pending_working(progress=None, on_ready=None, should_stop=None) -> int:
    """Build every recorded-but-missing working-set copy — the ON-DEMAND
    twin of `warm_working_set`'s alphabetical whole-tree sweep, drained
    by `_PENDING_WORKING` instead of a fresh directory scan (the
    `warm_pending_art`/`pending_art` shape, Rule #5: one drain LOOP, two
    ledgers). `app.warm.run_warm` calls this FIRST, ahead of
    `warm_working_set`'s own sweep (VISIBLE-FIRST warmup, owner bar
    2026-08-09) — the ledger's entries are exactly what the dial's first
    paint already asked for, so draining them first dresses the
    on-screen dial before the alphabetically-first subtree that may not
    even be visible; `app.watch_manager.AppController.kick_working_warm`
    calls this again, mid-session, whenever a later paint records a NEW
    miss the startup sweep never saw (a skin switch, a time-travel day
    that pulls in different archetype art).

    SUBPROCESS pool, exactly like `warm_working_set` and for the same
    reason its own docstring measured: PySide's QImage decode/smooth-
    scale/encode holds the GIL for seconds, so even a background THREAD
    doing this work would starve the GUI thread waiting for its turn at
    the GIL — invisible to it only from a separate process. Falls back
    to an in-thread loop if the pool cannot start (Rule #1: degraded and
    visible, never absent), exactly like `warm_working_set`.

    `on_ready` fires after EACH completed build (`warm_pending_art`'s
    contract) so the caller's shared debounced repaint dresses the dial
    piece by piece instead of waiting for the whole batch. Repeats until
    the ledger stops growing — a paint arriving mid-drain records a
    fresh miss the previous pass never saw, exactly like the art
    ledger's own drain loop."""
    from concurrent.futures import as_completed, ProcessPoolExecutor
    from time import perf_counter

    start = perf_counter()
    built = 0
    attempted: set[str] = set()

    while True:
        jobs = [
            path for path in pending_working() if str(path) not in attempted
        ]
        if not jobs:
            break
        if should_stop is not None and should_stop():
            return built
        attempted.update(str(path) for path in jobs)
        recipes = [
            (path, *_PENDING_WORKING[str(path)]) for path in jobs
        ]  # (cache, source, ceiling)

        def land(cache: Path) -> None:
            nonlocal built
            built += 1
            if on_ready is not None:
                on_ready()
            if progress is not None and built % 5 == 0:
                elapsed = perf_counter() - start
                progress(
                    f"[{elapsed:.1f}s] working set drain {built}/{len(jobs)}"
                )

        try:
            workers = max(1, min(defaults.WORKING_SET_WORKERS, os.cpu_count() or 1))
            with ProcessPoolExecutor(max_workers=workers) as pool:
                futures = {
                    pool.submit(build_scaled_copy, str(source), str(cache), ceiling): cache
                    for cache, source, ceiling in recipes
                }
                for future in as_completed(futures):
                    if should_stop is not None and should_stop():
                        for pending in futures:
                            pending.cancel()
                        break
                    cache = futures[future]
                    try:
                        future.result()
                        land(cache)
                    except OSError as error:
                        print(
                            f"working set drain build failed: {error}",
                            file=sys.stderr,
                        )
        except Exception as error:
            print(
                f"working set drain pool unavailable ({error}); "
                "building in-thread",
                file=sys.stderr,
            )
            for cache, source, ceiling in recipes:
                if should_stop is not None and should_stop():
                    break
                if cache.exists():
                    continue
                try:
                    build_scaled_copy(str(source), str(cache), ceiling)
                    land(cache)
                except OSError as inner:
                    print(
                        f"working set drain build failed: {inner}",
                        file=sys.stderr,
                    )
    if progress is not None and built:
        progress(
            f"[{perf_counter() - start:.1f}s] working set drain complete — "
            f"{built} copies built"
        )
    return built


def scaled_variant_file(
    path: Path | None, width: int, build: bool = True
) -> Path | None:
    """A DISK copy of `path` downscaled to `width` px — the hover
    performance fix (owner 2026-07-13: every first hover decoded the
    full 800×800 plate synchronously inside the tooltip's rich text
    while the popup shows at most a quarter of that; callers pass 2×
    the display width so the tooltip still downsamples for
    crispness). Cached by mtime; sources already small enough return
    the original (the header read costs no pixel decode).
    `build=False` never pays the decode+encode on a cold cache —
    it returns the ORIGINAL path instead, for GUI-thread callers that
    would rather show full-res once than stall (the Encyclopedia's
    gallery cards / reader pages; the background warm builds these
    with `build=True` and the next display is cheap)."""
    path = art_file(path)
    if path is None or not path.exists():
        return path
    source = QImageReader(str(path)).size()
    if not source.isValid() or source.width() <= width:
        return path
    cache = _scaled_cache_path(path, width)
    if not build and not cache.exists():
        return path
    if not cache.exists():
        # QImage, not QPixmap — the working-set warmup calls this off
        # the GUI thread (QPixmap is main-thread-only).
        try:
            build_scaled_copy(str(path), str(cache), width)
        except OSError as error:
            print(
                f"scaled variant cache write failed: {error}",
                file=sys.stderr,
            )
            return path
    return cache


def eclipse_solar_type_icon(type_: str) -> Path | None:
    """The small per-type SOLAR eclipse icon (ECLIPSE ICON WIRING round,
    owner 2026-07-20/21 — the solar pick is PROPOSED, not yet owner-
    confirmed the way lunar's red/gold/blue set is; see
    `defaults.ECLIPSE_SOLAR_TYPE_ICON_SOURCE`'s docstring for the shape-
    matched mapping). Total and partial ride their source file AS
    DRAWN; annular is TRITONE-tinted toward
    `palette.GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR` (the SAME "ring of
    fire" color the dial's own annular glow already uses — Rule #5, one
    color, two places) via `tinted_pixmap`, disk-cached like every
    other derived asset. None for an unknown type or a source that has
    not landed (Rule #1, graceful-absent)."""
    source = defaults.ECLIPSE_SOLAR_TYPE_ICON_SOURCE.get(type_)
    if source is None or not source.exists():
        return None
    if type_ != "annular":
        return source
    cache = (
        paths.settings_path().parent / "raster_cache"
        / f"{raster_store.source_prefix(source)}_eclipse_annular_tint.png"
    )
    if not cache.exists():
        pixmap = QPixmap(str(source))
        if pixmap.isNull():
            raise ValueError(f"cannot load image asset: {source}")
        tinted = tinted_pixmap(
            pixmap, palette.GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR
        )
        try:
            raster_store.atomic_save(tinted, cache)
        except OSError as error:
            # A cold cache is only slower, never wrong — but say so.
            print(
                f"eclipse annular icon cache write failed: {error}",
                file=sys.stderr,
            )
            return source
    return cache


def _computed_icon_cache(name: str, size: int) -> Path:
    """Where a COMPUTED Fast Travel icon is cached, keyed by name and
    SIZE alone — these drawings take no other input, so a given size
    paints exactly once per install."""
    return (
        paths.settings_path().parent / "raster_cache"
        / f"{name}_icon_{size}.png"
    )


def _save_computed_icon(image: QImage, cache: Path, what: str) -> Path:
    """There is no source master to fall back to for a computed glyph
    (unlike every other cache function here), so a failed save RAISES
    rather than silently returning an uncached path (Rule #1)."""
    try:
        raster_store.atomic_save(image, cache)
    except OSError as error:
        print(f"{what} icon cache write failed: {error}", file=sys.stderr)
        raise
    return cache


def _blank_icon(size: int) -> tuple[QImage, QPainter]:
    image = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    return image, painter


def calendar_sheet_icon_file(size: int) -> Path:
    """A COMPUTED calendar SHEET at `size` px for the Fast Travel Flash's
    Date category (owner ballot verdict 2026-08-12, option I1).

    It REPLACES the 12-wedge wheel that stood here since 2026-07-21 —
    his words on the ballot: that wheel "reads as an abstract pie rather
    than a date". A bound page instead: two binding rings, a darker
    header band, a grid of day cells and one cell lit, in the app's own
    gold ramp (`palette.CALENDAR_ICON_GOLD_COLORS`) so it stays in the
    same family as everything else in the flash. Rule #19 — computed, not
    commissioned; Rule #6 — the wheel is gone, not kept alongside."""
    cache = _computed_icon_cache("calendar_sheet", size)
    if cache.exists():
        return cache
    image, painter = _blank_icon(size)
    dark, bright = (QColor(c) for c in palette.CALENDAR_ICON_GOLD_COLORS)
    ink = QColor(palette.CALENDAR_ICON_RING_COLOR)
    margin = size * shortcuts.CALENDAR_SHEET_MARGIN_FRACTION
    page = QRectF(margin, margin, size - 2 * margin, size - 2 * margin)
    radius = size * 0.08
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(bright)
    painter.drawRoundedRect(page, radius, radius)
    header_height = page.height() * shortcuts.CALENDAR_SHEET_HEADER_FRACTION
    painter.setBrush(dark)
    painter.drawRoundedRect(
        QRectF(page.left(), page.top(), page.width(), header_height),
        radius, radius,
    )
    # Square off the header's lower corners so it reads as a band across
    # the page rather than a second rounded card floating on it.
    painter.drawRect(QRectF(
        page.left(), page.top() + header_height / 2,
        page.width(), header_height / 2,
    ))
    # The binding rings stand ABOVE the page edge, which is what makes a
    # rectangle read as a calendar rather than as a card.
    ring_width = max(1.0, size * shortcuts.CALENDAR_ICON_RING_WIDTH_FRACTION)
    painter.setPen(QPen(ink, ring_width))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    rings = shortcuts.CALENDAR_SHEET_RING_COUNT
    for index in range(rings):
        x = page.left() + page.width() * (index + 1) / (rings + 1)
        painter.drawLine(
            QPointF(x, margin * 0.35), QPointF(x, page.top() + header_height * 0.45)
        )
    # The day grid, with today's cell lit in the bright step against the
    # dark ink the other cells are drawn in.
    columns = shortcuts.CALENDAR_SHEET_COLUMNS
    rows = shortcuts.CALENDAR_SHEET_ROWS
    body_top = page.top() + header_height
    body_height = page.height() - header_height
    cell_w = page.width() / (columns + 1)
    cell_h = body_height / (rows + 1)
    painter.setPen(Qt.PenStyle.NoPen)
    lit_column, lit_row = shortcuts.CALENDAR_SHEET_LIT_CELL
    for row in range(rows):
        for column in range(columns):
            x = page.left() + cell_w * (column + 0.75)
            y = body_top + cell_h * (row + 0.6)
            cell = QRectF(x, y, cell_w * 0.62, cell_h * 0.58)
            if (column, row) == (lit_column, lit_row):
                painter.setBrush(dark)
                painter.drawRect(cell.adjusted(
                    -cell_w * 0.10, -cell_h * 0.10,
                    cell_w * 0.10, cell_h * 0.10,
                ))
                continue
            painter.setBrush(ink)
            painter.drawRect(cell)
    painter.end()
    return _save_computed_icon(image, cache, "calendar sheet")


def clock_face_icon_file(size: int) -> Path:
    """A COMPUTED 24-HOUR clock face at `size` px for the Fast Travel
    Flash's Time category (owner ballot verdict 2026-08-12, option H1).

    No clock file exists in `assets/instrument/icons/`, so "the clock SVG
    as until now" had nothing to point at — the spot showed a bare 🕐
    emoji. This draws one in the app's own gold ramp, and draws it as
    THIS watch's dial: twenty-four ticks, the majors at 12/18/00/06, and
    the hand standing at noon — the top, per `DIAL_OFFSET_DEG`. A generic
    twelve-hour clip-art clock would have taught the wrong dial in the
    one place the app announces what a step of TIME means."""
    cache = _computed_icon_cache("clock_face", size)
    if cache.exists():
        return cache
    image, painter = _blank_icon(size)
    dark, bright = (QColor(c) for c in palette.CALENDAR_ICON_GOLD_COLORS)
    ink = QColor(palette.CALENDAR_ICON_RING_COLOR)
    rim = max(1.0, size * shortcuts.CLOCK_ICON_RIM_WIDTH_FRACTION)
    centre = QPointF(size / 2.0, size / 2.0)
    radius = size / 2.0 - rim / 2.0
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(bright)
    painter.drawEllipse(centre, radius, radius)
    painter.setPen(QPen(ink, rim))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(centre, radius, radius)
    ticks = shortcuts.CLOCK_ICON_TICK_COUNT
    for index in range(ticks):
        major = index % shortcuts.CLOCK_ICON_MAJOR_EVERY == 0
        length = radius * (
            shortcuts.CLOCK_ICON_MAJOR_LENGTH_FRACTION if major
            else shortcuts.CLOCK_ICON_TICK_LENGTH_FRACTION
        )
        theta = math.radians(index * 360.0 / ticks)
        outer = QPointF(
            centre.x() + math.sin(theta) * (radius - rim * 0.6),
            centre.y() - math.cos(theta) * (radius - rim * 0.6),
        )
        inner = QPointF(
            centre.x() + math.sin(theta) * (radius - rim * 0.6 - length),
            centre.y() - math.cos(theta) * (radius - rim * 0.6 - length),
        )
        painter.setPen(QPen(dark, rim * (0.9 if major else 0.5)))
        painter.drawLine(inner, outer)
    hand = radius * shortcuts.CLOCK_ICON_HAND_LENGTH_FRACTION
    theta = math.radians(shortcuts.CLOCK_ICON_HAND_ANGLE_DEG)
    painter.setPen(QPen(
        ink, max(1.0, size * shortcuts.CLOCK_ICON_HAND_WIDTH_FRACTION),
        Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
    ))
    painter.drawLine(centre, QPointF(
        centre.x() + math.sin(theta) * hand,
        centre.y() - math.cos(theta) * hand,
    ))
    painter.end()
    return _save_computed_icon(image, cache, "clock face")
