"""Archetype-mode geometry and figure drawing.

Which figure the hour hand lights, how large a figure's portrait and art
must be for the arm it stands on, and the draw call that puts a figure
plus its name on the dial. The skin QUERIES (`archetype_key`,
`archetype_active`) live with the other skin queries in
[Skin Geometry](__about/skin_geometry.md).
"""


from PySide6.QtCore import QPointF
from PySide6.QtGui import QImageReader, QPainter

from config import archetypes, dial, paths, pointer_geometry
from render.context import RenderContext
from render.painting import draw_name_label, draw_pixmap_centered, name_label_px
from render.slot_layout import weekday_body_size
from skins.manifest import SkinDefinition


def archetype_lit_index(
    pointer: str, hour_angle: float, rotation: float = 0.0,
    offset: float = 0.0,
) -> int:
    """The figure whose HOUR-SPACE contains the hour hand (owner
    2026-07-16): the circle divides by arms — trio 3×8h, cross 4×6h,
    hexa 6×4h, octa 8×3h — each space CENTERED on its arm (the arm tip
    is the center of its hue, the standing convention). The spaces
    ride the drawn arms, so the solar rotation shifts them exactly as
    it shifts the diamonds; index = the figures-tuple position.
    `offset` is the Genesis inversion (`arm_offset_deg`) — the trio's
    tertiary wheel counts its spaces from the 24h arm."""
    arms = pointer_geometry.POINTER_POINTS[pointer]
    step = 360.0 / arms
    return int(
        round(((hour_angle - rotation - offset) % 360.0) / step)
    ) % arms


def archetype_center_lit(hour_angle: float, noon_angle: float) -> bool:
    """Whether the archetype CENTER burns FULL (owner seal 2026-07-18):
    true while the hour hand sits within
    `archetypes.ARCHETYPE_CENTER_WINDOW_DEG` of TRUE solar noon OR
    solar midnight (noon + 180). `noon_angle` is `day.star_rotation` —
    the hexagram's top vertex, the SOLAR noon angle, correct in both
    upright and rotating modes (never the drawn rotation). The circular
    distance to noon folds through the midnight mirror to give the
    distance to the noon-midnight AXIS, gated against the window."""
    dist_noon = abs(hour_angle - noon_angle) % 360.0
    dist_noon = min(dist_noon, 360.0 - dist_noon)
    dist_axis = min(dist_noon, 180.0 - dist_noon)
    return dist_axis <= archetypes.ARCHETYPE_CENTER_WINDOW_DEG


#: Decoded PNG header sizes, POSITIVE RESULTS ONLY (owner bug
#: 2026-08-06). `archetype_art_size` opens the file and decodes its
#: header, and Archetype mode calls it for every arm plus the centre on
#: every tick — up to nine file opens per second per watch for a number
#: that cannot change while the app runs. A None is never cached: None
#: means "the glass has not landed yet", exactly the answer that must
#: stay live (same rule as `config.paths._ART_FILE_CACHE`, and the same
#: reset hook clears both when a drain lands).
_ART_SIZES: dict[str, object] = {}


def reset_art_size_cache() -> None:
    """Forget every decoded header: new art has landed on disk."""
    _ART_SIZES.clear()


def archetype_art_size(path):
    """The pixel size of REAL archetype art (the owner's glass) — or
    None when the file is missing or a committed 1×1 placeholder (the
    WORKPLAN missing-art rule, ARCHETYPE_ART_MIN_PX). The one place the
    header is read; readiness AND the two-type classification both
    derive from it."""
    resolved = paths.art_file(path)
    if resolved is None:
        return None
    # The cache answers BEFORE the stat, not after it — a remembered
    # header already proves the file was there, and this runs per arm
    # per tick.
    cached = _ART_SIZES.get(str(resolved))
    if cached is not None:
        return cached
    if not resolved.exists():
        return None
    size = QImageReader(str(resolved)).size()
    if (
        not size.isValid()
        or size.width() <= archetypes.ARCHETYPE_ART_MIN_PX
        or size.height() <= archetypes.ARCHETYPE_ART_MIN_PX
    ):
        return None
    _ART_SIZES[str(resolved)] = size
    return size


def archetype_art_ready(path) -> bool:
    """Whether REAL archetype art is on disk (larger than the committed
    1×1 placeholders). While it is not, the renderer draws the figure's
    NAME instead — never a stretched pixel or a crash."""
    return archetype_art_size(path) is not None


def archetype_figure_size(
    skin: SkinDefinition, radius: float, art_file=None,
) -> float:
    """THE ONE sizing entry for every archetype figure — arms AND
    center. THE DIAL LAW (owner decree 2026-08-04): a dial seat holds
    only a round or square plate at 1:1, so every figure wears the SLOT
    size, `weekday_body_size()`, identical to the weekday bodies. There
    is nothing to classify.

    THE TWO-TYPE LAW IS GONE (same decree). It sorted art by aspect and
    gave the tall lancet vitraz windows their own inscribed height ON
    THE DIAL — the written law that overrode the owner's repeated
    instruction, session after session, because a rule cannot win
    against a law in the code. The lancets now live in the hover's left
    column, and `config.archetypes.dial_plate` resolves every seat to
    its family's `circle` register, so what arrives here is round by
    construction. `art_file` is kept in the signature for its callers
    and no longer read.

    Wide art like Saturn's rings stays height-based on purpose (owner:
    "planeta istih dimenzija kao ostale, prstenovi vire") — the ball
    matches every other circle and the rings overflow the frame."""
    return weekday_body_size(skin, radius)


def draw_archetype_figure(
    painter: QPainter, ctx: "RenderContext", fig: dict, pos: QPointF,
    height: float, opacity: float, named: bool, label_px: float,
) -> None:
    """One archetype figure in its diamond: the stained glass scaled
    into the arm (color visible around it) at `opacity`. `height` is
    already TYPE-CLASSIFIED (`archetype_figure_size` — circle vs
    portrait) and hover-scaled by the caller; `label_px` is the SET-
    UNIFORM label size (owner verdict 2026-07-18, ROADMAP 15h — the
    caller computed it once per paint via `archetype_label_set_px`,
    already hover-scaled). `named` adds the display name in the label
    style. Missing/placeholder art draws the NAME alone — the
    documented fallback until the owner's glass lands."""
    painter.save()
    painter.setOpacity(opacity)
    ready = archetype_art_ready(fig["file"])
    if ready:
        draw_pixmap_centered(painter, ctx, fig["file"], pos, height)
    if named or not ready:
        draw_name_label(painter, fig["name"], pos, label_px, ctx=ctx)
    painter.restore()


def archetype_label_set_px(
    ctx: RenderContext, key: str, arm_width: float,
) -> int:
    """The SET-UNIFORM label size (owner verdict 2026-07-18, ROADMAP
    15h) for ONE archetype layout: every name — the arm figures AND the
    center, kept in the SAME set on purpose (owner's slika showed the
    center joining the arms' ring for uniformity) — wears the size of
    the SMALLEST fitted member. A pure, cheap (text measurement only)
    function so ArchetypeLayer (DAILY) and ArchetypeCenterLayer
    (MINUTE) — two separate paint passes — agree on one size without
    sharing mutable state."""
    target = arm_width * dial.NAME_LABEL_WIDTH_FRACTION
    fits = [name_label_px(fig["name"], target) for fig in archetypes.figures(key)]
    center = archetypes.center(key)
    if center is not None:
        center_height = archetype_figure_size(ctx.skin, ctx.radius)
        fits.append(
            name_label_px(
                center["name"], center_height * dial.NAME_LABEL_WIDTH_FRACTION,
            )
        )
    return min(fits)
