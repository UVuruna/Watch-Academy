"""Archetype-mode geometry and figure drawing.

Which figure the hour hand lights, how large a figure's portrait and art
must be for the arm it stands on, and the draw call that puts a figure
plus its name on the dial. The skin QUERIES (`archetype_key`,
`archetype_active`) live with the other skin queries in
[Skin Geometry](__about/skin_geometry.md).
"""

import math

from PySide6.QtCore import QPointF
from PySide6.QtGui import QImageReader, QPainter

from config import archetypes, constants, dial, paths
from render.context import RenderContext
from render.painting import draw_name_label, draw_pixmap_centered, name_label_px
from render.skin_geometry import arm_half_deg
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
    arms = constants.POINTER_POINTS[pointer]
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


def archetype_art_size(path):
    """The pixel size of REAL archetype art (the owner's glass) — or
    None when the file is missing or a committed 1×1 placeholder (the
    WORKPLAN missing-art rule, ARCHETYPE_ART_MIN_PX). The one place the
    header is read; readiness AND the two-type classification both
    derive from it."""
    resolved = paths.art_file(path)
    if resolved is None or not resolved.exists():
        return None
    size = QImageReader(str(resolved)).size()
    if (
        not size.isValid()
        or size.width() <= archetypes.ARCHETYPE_ART_MIN_PX
        or size.height() <= archetypes.ARCHETYPE_ART_MIN_PX
    ):
        return None
    return size


def archetype_art_ready(path) -> bool:
    """Whether REAL archetype art is on disk (larger than the committed
    1×1 placeholders). While it is not, the renderer draws the figure's
    NAME instead — never a stretched pixel or a crash."""
    return archetype_art_size(path) is not None


def archetype_portrait_height(tip: float, tan_half: float) -> float:
    """The PORTRAIT figure height that exactly INSCRIBES the STANDARD
    aspect (`archetypes.ARCHETYPE_PORTRAIT_STANDARD_ASPECT`, 1:2) into
    its arm's diamond — the old `archetype_fit_height` formula (15g
    clamp era), reintroduced here for ONE purpose only: sizing the
    UNIFORM portrait at the standard aspect, never per-art (owner
    two-type law round two, 2026-07-18, fix round A 2026-07-19). The
    diamond is a rhombus centered at the romb center with along-arm
    half-diagonal tip/2 and perpendicular half-diagonal tip*tan(half)/2;
    a centered inscribed rectangle of half a×b fits iff a/p + b/q <= 1,
    so a figure of aspect `a` scaled to height h (width = a*h) fits up
    to h = tip*tan(half)/(a + tan(half)) — evaluated at the STANDARD
    aspect so a 1:2 lancet inscribes its diamond EXACTLY; art wider than
    1:2 may still overflow sideways until the owner reforces it to the
    standard (transitional, documented, not clamped)."""
    return tip * tan_half / (
        archetypes.ARCHETYPE_PORTRAIT_STANDARD_ASPECT + tan_half
    )


def archetype_figure_size(
    skin: SkinDefinition, radius: float, art_file,
) -> float:
    """THE ONE sizing entry for every archetype figure — arms AND center
    (owner two-type law, 2026-07-18 round two; height law fixed round A
    2026-07-19): the art divides into TWO TYPES by its OWN aspect ratio
    (width/height), classified once — no per-art clamp, no set-minimum.

    - CIRCLE type (aspect >= `ARCHETYPE_PORTRAIT_ASPECT_MAX` — rondels,
      medallions, the square Scale glass, and WIDE art like Saturn's
      rings) wears the SLOT size, `weekday_body_size()` — IDENTICAL to
      the weekday bodies; wide art stays height-based ON PURPOSE (owner:
      "planeta istih dimenzija kao ostale, prstenovi vire" — the ball
      matches every other circle, the rings overflow the frame,
      deliberately — no clamp).
    - PORTRAIT type (aspect < the threshold — the tall lancet vitraž
      windows: persons, temperaments) wears `archetype_portrait_height()`
      — the height inscribing the STANDARD aspect (not the art's own)
      into the diamond, UNIFORM for every portrait in the set.

    Missing/placeholder art (the name-fallback path) reads CIRCLE-sized
    — there is no art to classify."""
    size = archetype_art_size(art_file)
    if size is None or (
        size.width() / size.height() >= archetypes.ARCHETYPE_PORTRAIT_ASPECT_MAX
    ):
        return weekday_body_size(skin, radius)
    tip = radius * skin.star.radius_fraction
    # The DRAWN half-angle (the Cube look widens the family wheels'
    # arms to full rhombi — a lancet inscribes the fatter face).
    tan_half = math.tan(math.radians(arm_half_deg(skin)))
    return archetype_portrait_height(tip, tan_half)


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
        draw_name_label(painter, fig["name"], pos, label_px)
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
        center_height = archetype_figure_size(ctx.skin, ctx.radius, center["file"])
        fits.append(
            name_label_px(
                center["name"], center_height * dial.NAME_LABEL_WIDTH_FRACTION,
            )
        )
    return min(fits)
