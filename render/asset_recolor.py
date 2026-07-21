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
from pathlib import Path

import numpy as np
from PySide6.QtGui import QColor, QImage, QPixmap

from config import defaults, paths, profiling
from config.paths import art_file
from render.assets import AssetCache


def letter_metal_file(path: Path, metal: str) -> Path:
    """The ring letter's GOLD, SILVER or BRONZE finish, derived AT LOAD
    from the GOLD master (owner decree 2026-07-19: "bolje crtati na
    licu mesta nego 15MB fajlova" — retiring the 76 pre-rendered
    `_silver.png`/`_bronze.png` files) — now SHADE-aware (R8a redo,
    owner spec 2026-07-21 night, replacing both the retired straight-
    multiply bronze recipe the owner called "weak" AND the gold
    passthrough): every metal, including gold, runs through
    `AssetCache._recolor_to_shade` (the SAME kernel `_metal_swapped`
    uses for badge medallions, Rule #5) with the WHOLE opaque glyph as
    the mask — a ring letter mixes no gray stone the way a medallion
    does, so unlike the badge's hue-window detection every alpha>0
    pixel simply IS a metal pixel. The active SHADE per metal comes
    from `config.paths.metal_shade` (a Settings choice, not a
    parameter here — same reasoning as `subdial_plate_file`'s active
    set). Disk-cached like every other derived asset, keyed by shade
    and `defaults.METAL_SWAP_VERSION` — paid once per (file, metal,
    shade), never per paint."""
    path = art_file(path)
    if path is None:
        return path
    shade = paths.metal_shade(metal)
    stamp = hashlib.sha1(str(path).encode("utf-8")).hexdigest()[:16]
    cache = (
        paths.settings_path().parent / "raster_cache"
        / f"{stamp}_{int(path.stat().st_mtime)}_letter_{metal}_{shade}"
        f"_v{defaults.METAL_SWAP_VERSION}.png"
    )
    if not cache.exists():
        # QImage end to end (the same R1b threading law _metal_swapped
        # documents) — a future background warmup of letter glyphs must
        # never trip the QPixmap-off-GUI-thread crash class.
        result = AssetCache._letter_recolored(QImage(str(path)), metal, shade)
        try:
            cache.parent.mkdir(parents=True, exist_ok=True)
            if not result.save(str(cache)):
                raise OSError(f"QImage.save returned False for {cache}")
        except OSError as error:
            # A cold cache is only slower, never wrong — but say so.
            print(f"letter metal cache write failed: {error}", file=sys.stderr)
            return path
    return cache


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
        target = QColor(defaults.SUBDIAL_RECOLOR_COLORS[finish])
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


def metal_variant_file(path: Path, metal: str | None) -> Path:
    """A DISK copy of `path` with the hue-selective metal swap applied
    (owner bug 2026-07-13: the legend/Encyclopedia <img> always showed
    the BRONZE file even under the gold/silver look — QToolTip embeds
    files, not pixmaps). Cached in the raster cache keyed by the file's
    mtime, the active SHADE and `defaults.METAL_SWAP_VERSION` (R8a redo,
    2026-07-21 night); None or a non-swap metal returns the original
    path."""
    path = art_file(path)
    if path is None or metal not in defaults.METAL_SWAP_TARGETS:
        return path
    shade = paths.metal_shade(metal)
    stamp = hashlib.sha1(str(path).encode("utf-8")).hexdigest()[:16]
    cache = (
        paths.settings_path().parent / "raster_cache"
        / f"{stamp}_{int(path.stat().st_mtime)}_{metal}_{shade}"
        f"_v{defaults.METAL_SWAP_VERSION}.png"
    )
    if not cache.exists():
        # QImage end to end — this runs on the background hover-warm
        # thread too, where QPixmap is forbidden (R1b find, 2026-07-20:
        # the one off-GUI-thread QPixmap in the codebase, the prime
        # suspect for the untraced whole-app aborts).
        swapped = AssetCache._metal_swapped(QImage(str(path)), metal)
        try:
            cache.parent.mkdir(parents=True, exist_ok=True)
            swapped.save(str(cache))
        except OSError as error:
            # A cold cache is only slower, never wrong — but say so.
            print(f"metal variant cache write failed: {error}", file=sys.stderr)
            return path
    return cache


def tinted_pixmap(source: QPixmap, tint: str) -> QPixmap:
    """Public entry to `AssetCache._tinted`'s TRITONE gradient-map
    recolor (black -> tint -> white; see its own docstring for the
    recipe) — the render pipeline's ring/hand recolors call the private
    method directly (same class, same cache), but ADD WATCH round's
    `app.tray.logo_icon` needs the SAME algorithm for a per-watch tray
    icon tint and lives outside render/ entirely (Rule #5 — one
    algorithm, a clean non-private door for the second caller)."""
    return AssetCache._tinted(source, tint)
