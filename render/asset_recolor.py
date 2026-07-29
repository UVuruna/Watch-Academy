"""Disk-cached recolors derived from a single master file — the metal
finish/tint family split out of `assets.py` (surgical sibling
extraction, `research/REFACTOR_PLAN.md` §8): `letter_metal_file` and
`metal_variant_file` derive gold/silver/bronze from one drawn asset via
`AssetCache`'s hue-selective/whole-glyph recolor kernels; `_recolored_
plate` is the subdial plate's own bezel/field recolor, built the SAME
recipe; `tinted_pixmap` is the public door to `AssetCache`'s TRITONE
gradient-map tint. See [Asset Recolor](asset_recolor.md) for the full
recipe.
"""

import hashlib
import sys
import threading
from pathlib import Path

import numpy as np
from PySide6.QtGui import QColor, QImage, QPixmap

from config import defaults, palette, paths, profiling
from config.paths import art_file
from render.assets import AssetCache


def letter_metal_path(path: Path, metal: str) -> Path:
    """WHERE the ring letter's GOLD, SILVER, BRONZE or THEMATIC finish
    lives on disk — a PURE path computation that also RECORDS the recipe
    in the lazy ledger. NO pixel work (the twin of `metal_variant_path`,
    Rule #5 — one ledger, two families).

    The finish is derived AT LOAD from the GOLD master (owner decree
    2026-07-19: "bolje crtati na licu mesta nego 15MB fajlova" — retiring
    the 76 pre-rendered `_silver.png`/`_bronze.png` files) and is
    SHADE-aware (R8a redo, owner spec 2026-07-21 night): every metal,
    gold included, runs through `AssetCache._recolored` (the SAME door
    badge medallions use) in `alpha` mask mode — a ring letter mixes no
    gray stone the way a medallion does, so unlike the badge's
    chroma-window detection every alpha>0 pixel simply IS a metal pixel.
    The source metal is GOLD here (the master these are drawn on)
    against the badges' bronze; the transform is source-agnostic and is
    simply told which. The active SHADE comes from the watch's display
    context (`config.paths.metal_shade`). Cache key: the master's mtime,
    the metal, the shade and `defaults.METAL_SWAP_VERSION`."""
    path = art_file(path)
    if path is None or not path.exists():
        return path
    shade = paths.metal_shade(metal)
    stamp = hashlib.sha1(str(path).encode("utf-8")).hexdigest()[:16]
    cache = (
        paths.settings_path().parent / "raster_cache"
        / f"{stamp}_{int(path.stat().st_mtime)}_letter_{metal}_{shade}"
        f"_v{defaults.METAL_SWAP_VERSION}.png"
    )
    _PENDING_VARIANTS.setdefault(
        str(cache),
        (path, metal, defaults.METAL_SOURCE_LETTER,
         defaults.METAL_MASK_LETTER, shade),
    )
    return cache


def letter_metal_file(path: Path, metal: str) -> Path:
    """The file the DIAL should draw RIGHT NOW: the derived finish when
    it is already on disk, otherwise the GOLD MASTER.

    Owner decree 2026-07-28 ("FIRST DEFAULT — recolor u pozadini. Kad
    završi prikaže."). This used to recolor synchronously on a cache
    miss, and it was the WHOLE of the slow start: measured on a cold
    raster cache, a watch's first paint ran 15 of these — 3.6 s of numpy
    (oklab, guided box filter, specular ramp) on the GUI thread, times
    one per open watch, before any dial appeared at all. The pixels are
    identical either way; only WHERE they are paid moved. The master is
    the honest stand-in: gold is the metal the letters are actually
    drawn in, so a not-yet-recolored dial is a GOLD dial, never a blank
    one (Rule #1 — a documented, visible fallback, not a silent one).

    `render.art_warm.warm_pending_art` drains the ledger on the
    background thread and the controller repaints; a caller that needs
    the real pixels NOW (an export) uses `ensure_variant` on
    `letter_metal_path`."""
    derived = letter_metal_path(path, metal)
    if derived is None or derived.exists():
        return derived
    return _PENDING_VARIANTS[str(derived)][0]


@profiling.timed("Subdial recolor")
def _recolored_plate(
    master: Path, finish: str, tint: str | None = None
) -> Path:
    """`master` (the resolved plate — the solo set's silver file, or any
    set's file under a "theme" tint request) with its brushed metal
    BEZEL colorized to `finish` — built the SAME recipe the ring
    letters use to derive silver/bronze live from gold (Rule #5,
    `letter_metal_file`): SILVER is the achromatic VALUE alone (no hue
    at all, whatever metal `master` itself happens to be drawn in — the
    letters' "straight desaturation" rule, masked here to the rim
    only); GOLD and BRONZE tint that same achromatic base by their own
    color (the letters' "tint the desaturated result" rule). Only
    bright, unsaturated pixels INSIDE the radial bezel band take the
    recolor — the field's own specular highlights stay neutral (owner
    correction 2026-07-15: without the radial mask the interiors drank
    the metal and the three finishes stopped matching). With a TINT the
    interior (the tapisserie field) is colorized the same way to the
    clock tint (the "theme" plate style); without one the field stays
    as drawn."""
    stamp = hashlib.sha1(str(master).encode("utf-8")).hexdigest()[:16]
    tint_tag = f"_{tint.lstrip('#').lower()}" if tint else ""
    cache = (
        paths.settings_path().parent / "raster_cache"
        / f"{stamp}_{int(master.stat().st_mtime)}"
        f"_subdial{defaults.SUBDIAL_RECOLOR_VERSION}"
        f"_{finish}{tint_tag}.png"
    )
    if cache.exists():
        return cache
    image = QImage(str(master)).convertToFormat(
        QImage.Format.Format_RGBA8888
    )
    width, height = image.width(), image.height()
    stride = image.bytesPerLine() // 4
    buffer = np.frombuffer(image.constBits(), dtype=np.uint8)
    rgba = (
        buffer.reshape(height, stride, 4)[:, :width, :]
        .astype(np.float64) / 255.0
    )
    rgb = rgba[..., :3]
    value = rgb.max(axis=-1)
    minc = rgb.min(axis=-1)
    sat = np.where(value > 0, (value - minc) / np.maximum(value, 1e-6), 0.0)

    def smoothstep(x):
        x = np.clip(x, 0.0, 1.0)
        return x * x * (3.0 - 2.0 * x)

    value_low, value_high = defaults.SUBDIAL_RECOLOR_VALUE_RAMP
    sat_low, sat_high = defaults.SUBDIAL_RECOLOR_SAT_CUTOFF
    # The radial bezel band: 0 across the whole field, ramping to 1
    # where the brushed bezel lives — the metal never reaches the
    # interior highlights.
    rim_low, rim_high = defaults.SUBDIAL_RECOLOR_RIM_RADIUS
    ys, xs = np.mgrid[0:height, 0:width]
    radius = np.hypot(
        xs - (width - 1) / 2.0, ys - (height - 1) / 2.0
    ) / (width / 2.0)
    weight = (
        smoothstep((value - value_low) / (value_high - value_low))
        * (1.0 - smoothstep((sat - sat_low) / (sat_high - sat_low)))
        * smoothstep((radius - rim_low) / (rim_high - rim_low))
    )[..., None]
    if finish == "silver":
        # The achromatic base alone, masked to the rim — the same
        # "silver is a straight desaturation" recipe letters use.
        rim = np.repeat(value[..., None], 3, axis=-1)
    else:
        target = QColor(palette.SUBDIAL_RECOLOR_COLORS[finish])
        finish_rgb = np.array([
            target.redF(), target.greenF(), target.blueF()
        ])
        rim = finish_rgb[None, None, :] * value[..., None]
    if tint:
        # The "theme" plate style: the dark tapisserie field takes the
        # clock tint, luminance-preserving like the rim but lifted by
        # the field gain so the hue actually reads on the dark relief.
        theme = QColor(tint)
        theme_rgb = np.array([
            theme.redF(), theme.greenF(), theme.blueF()
        ])
        lifted = value * defaults.SUBDIAL_RECOLOR_FIELD_GAIN
        field = theme_rgb[None, None, :] * lifted[..., None]
    else:
        field = rgb
    rgba[..., :3] = field * (1.0 - weight) + rim * weight
    out_bytes = np.ascontiguousarray(
        (np.clip(rgba, 0.0, 1.0) * 255.0).round().astype(np.uint8)
    )
    out = QImage(
        out_bytes.tobytes(), width, height, width * 4,
        QImage.Format.Format_RGBA8888,
    ).copy()
    try:
        cache.parent.mkdir(parents=True, exist_ok=True)
        out.save(str(cache))
    except OSError as error:
        # A cold cache is only slower, never wrong — but say so.
        print(f"subdial recolor cache write failed: {error}", file=sys.stderr)
        return master
    return cache


# THE LAZY VARIANT LEDGER (owner order 2026-07-26: "the Encyclopedia
# BLOCKED the main thread for minutes" — root cause: `metal_variant_file`
# used to GENERATE every cold recolor at PATH-RESOLUTION time, and
# `app.encyclopedia._topics()` resolves a couple HUNDRED gold/silver
# paths while the dialog is being BUILT, on the GUI thread. The cache
# key includes the source file's mtime, the active shade and
# METAL_SWAP_VERSION — so every art rename wave, shade change or version
# bump invalidated the whole cache and the NEXT open paid minutes of
# numpy recolors again. Naming a variant and building its pixels are now
# two separate steps): `metal_variant_path` is PURE — it names the cache
# file and records the (source, metal) recipe here; `ensure_variant`
# materializes a recorded path on first actual use — any thread, QImage
# end to end (the R1b law) — or in the background warm
# (`app.encyclopedia_warm`). Per-path locks make a GUI-thread first
# display and the warm thread meeting on the SAME file build it once.
# key -> (source file, target metal, source metal, mask mode, shade).
# The source metal and mask mode used to be hardcoded to the BADGE pair
# inside `ensure_variant`; they became part of the recipe when ring
# LETTERS joined the ledger (owner decree 2026-07-28), because a letter
# is drawn on a GOLD master and masked by ALPHA where a badge is bronze
# and masked by CHROMA. The SHADE rides along for the same round: a
# recipe is recorded under ONE watch's display context and built later on
# a background thread that has none, so the shade cannot be re-read at
# build time — it must be remembered.
_PENDING_VARIANTS: dict[str, tuple[Path, str, str, str, str]] = {}
_VARIANT_LOCKS: dict[str, threading.Lock] = {}
_VARIANT_LOCKS_GUARD = threading.Lock()


def _variant_lock(key: str) -> threading.Lock:
    with _VARIANT_LOCKS_GUARD:
        lock = _VARIANT_LOCKS.get(key)
        if lock is None:
            lock = _VARIANT_LOCKS[key] = threading.Lock()
        return lock


def metal_variant_path(path: Path, metal: str | None) -> Path:
    """WHERE `path`'s hue-selective metal swap lives on disk — a pure
    path computation, NO pixel work (the Encyclopedia resolves hundreds
    of these while building its topic table; generation is deferred to
    `ensure_variant`). Cache key: the file's mtime, the active SHADE and
    `defaults.METAL_SWAP_VERSION` (R8a redo, 2026-07-21 night). None or
    a non-swap metal returns the original path; a source missing from
    disk returns the CANONICAL path unchanged (graceful-absent — the
    caller's own exists() filter hides the look; the old eager code
    crashed on `stat()` here, which is exactly what a rename wave did to
    the Encyclopedia's open)."""
    path = art_file(path)
    if path is None or metal not in defaults.METAL_SWAP_TARGETS:
        return path
    if not path.exists():
        return path
    shade = paths.metal_shade(metal)
    stamp = hashlib.sha1(str(path).encode("utf-8")).hexdigest()[:16]
    cache = (
        paths.settings_path().parent / "raster_cache"
        / f"{stamp}_{int(path.stat().st_mtime)}_{metal}_{shade}"
        f"_v{defaults.METAL_SWAP_VERSION}.png"
    )
    _PENDING_VARIANTS.setdefault(
        str(cache),
        (path, metal, defaults.METAL_SOURCE_BADGE,
         defaults.METAL_MASK_BADGE, shade),
    )
    return cache


def pending_art() -> list[Path]:
    """Every recorded recipe whose file is still missing — the DIAL's
    own not-yet-recolored letters first in practice, because a watch's
    first paint is what records them (owner decree 2026-07-28). The
    background drain (`render.art_warm.warm_pending_art`) walks THIS
    list; a snapshot is taken because the GUI thread keeps recording new
    recipes while the drain runs (the next pass picks those up)."""
    return [
        Path(key) for key in list(_PENDING_VARIANTS)
        if not Path(key).exists()
    ]


def variant_pending(path: Path | None) -> bool:
    """True when `path` is a RECORDED, not-yet-built metal variant —
    the Encyclopedia's exists() filter counts such a path as present
    (its source is on disk; the pixels build on first display or in
    the background warm)."""
    return (
        path is not None
        and str(path) in _PENDING_VARIANTS
        and not path.exists()
    )


def ensure_variant(path: Path | None) -> Path | None:
    """Materialize a `metal_variant_path`-recorded recolor whose file is
    still missing — the ONE place the pixel work happens (first display
    on the GUI thread, or the background warm; QImage end to end, R1b
    law: QPixmap must never be touched off the GUI thread). Paths this
    module never recorded pass through untouched. Returns the SOURCE
    file when the cache write fails (a cold cache is only slower, never
    wrong — but say so, Rule #1)."""
    if path is None:
        return None
    key = str(path)
    recipe = _PENDING_VARIANTS.get(key)
    if recipe is None or path.exists():
        return path
    with _variant_lock(key):
        if path.exists():
            return path
        source, metal, source_metal, mask_mode, shade = recipe
        swapped = AssetCache._recolored(
            QImage(str(source)), metal, source_metal, mask_mode, shade,
        )
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            if not swapped.save(str(path)):
                raise OSError(f"QImage.save returned False for {path}")
        except OSError as error:
            print(f"metal variant cache write failed: {error}", file=sys.stderr)
            return source
    return path


def letter_metal_variant(path: Path, metal: str | None) -> Path:
    """The ring letter's derived finish with its PIXELS GUARANTEED — the
    eager door, for callers that cannot accept the gold master standing
    in (an export, a test measuring the actual metal). Exactly
    `metal_variant_file`'s twin for the letter family (Rule #5).

    The DIAL never uses this: it draws through `letter_metal_file`, which
    returns the master on a cache miss and lets the background warm catch
    up (owner decree 2026-07-28)."""
    return ensure_variant(letter_metal_path(path, metal))


def metal_variant_file(path: Path, metal: str | None) -> Path:
    """A DISK copy of `path` with the hue-selective metal swap applied
    (owner bug 2026-07-13: the legend/Encyclopedia <img> always showed
    the BRONZE file even under the gold/silver look — QToolTip embeds
    files, not pixmaps). The EAGER door — resolve AND materialize in one
    call — for callers that embed the file path immediately (the
    compositor's tooltip <img> tags, the hover warm sweep). Callers that
    only TABLE paths for later display (the Encyclopedia) use
    `metal_variant_path` + `ensure_variant` instead."""
    return ensure_variant(metal_variant_path(path, metal))


def tinted_pixmap(source: QPixmap, tint: str) -> QPixmap:
    """Public entry to `AssetCache._tinted`'s TRITONE gradient-map
    recolor (black -> tint -> white; see its own docstring for the
    recipe) — the render pipeline's ring/hand recolors call the private
    method directly (same class, same cache), but ADD WATCH round's
    `app.tray.logo_icon` needs the SAME algorithm for a per-watch tray
    icon tint and lives outside render/ entirely (Rule #5 — one
    algorithm, a clean non-private door for the second caller)."""
    return AssetCache._tinted(source, tint)
