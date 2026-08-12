"""Eclipse and event GLOW — strength, state and the radial paint.

An eclipse's render state and how strongly it glows for a given
magnitude, plus the radial-gradient glow the year marker paints behind
an event body.
"""

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QRadialGradient

from config import glow


def draw_event_glow(
    painter: QPainter, pos: QPointF, marker_radius: float, color: str,
    strength: float = 1.0, fringe_color: str | None = None,
) -> None:
    """Radial halo behind a year marker relocated to the ring band
    centerline during a season/moon/eclipse event window (owner rework
    2026-07-16): compact — the halo diameter is twice the marker's — and
    intense, so it reads over any background while STRADDLING the ring.
    `color` is GOLDEN for the Sun's events, SILVER for the Moon's, and
    RED/bronze for an eclipse (ROADMAP 15h item 11). `strength` (0..1)
    scales the core/mid alpha — the eclipse call scales it by the
    catalog MAGNITUDE (`eclipse_glow_strength`); every other caller
    passes the default 1.0, unchanged from before.

    `fringe_color` (LUNAR ECLIPSE OPTION C, owner sealed 2026-07-18): an
    optional thin RING of a second color layered at the OUTER edge of
    the glow — the ozone-band turquoise at the umbra's rim during
    totality — three extra gradient stops (transparent -> peak ->
    transparent) straddling `ECLIPSE_LUNAR_FRINGE_STOP`, added AFTER the
    mid stop and BEFORE the fully-transparent edge so it reads as a
    separate ring rather than a blend with the bronze core. None for
    every other caller, unchanged."""
    halo = marker_radius * glow.GLOW_RADIUS_SCALE
    gradient = QRadialGradient(pos, halo)
    core = QColor(color)
    core.setAlphaF(glow.GLOW_CORE_ALPHA * strength)
    mid = QColor(color)
    mid.setAlphaF(glow.GLOW_MID_ALPHA * strength)
    edge = QColor(color)
    edge.setAlphaF(0.0)
    gradient.setColorAt(0.0, core)
    gradient.setColorAt(glow.GLOW_MID_STOP, mid)
    if fringe_color is not None:
        fringe_transparent = QColor(fringe_color)
        fringe_transparent.setAlphaF(0.0)
        fringe_peak = QColor(fringe_color)
        fringe_peak.setAlphaF(glow.ECLIPSE_LUNAR_FRINGE_ALPHA * strength)
        stop = glow.ECLIPSE_LUNAR_FRINGE_STOP
        half_width = glow.ECLIPSE_LUNAR_FRINGE_HALF_WIDTH
        gradient.setColorAt(stop - half_width, fringe_transparent)
        gradient.setColorAt(stop, fringe_peak)
        gradient.setColorAt(stop + half_width, fringe_transparent)
    gradient.setColorAt(1.0, edge)
    painter.save()
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(gradient))
    painter.drawEllipse(pos, halo, halo)
    painter.restore()


def eclipse_glow_strength(magnitude: float | None) -> float:
    """Glow intensity (0..1 fraction of the normal alpha) scaled by the
    catalog MAGNITUDE (owner idea, ROADMAP 15h item 11): clamped to
    `ECLIPSE_MAGNITUDE_MIN/MAX`, linearly mapped to
    `ECLIPSE_GLOW_STRENGTH_MIN/MAX`. `magnitude` is None only for a
    malformed catalog row — the schema always writes it, so a None
    here reads as the strongest glow rather than guessing (Rule #7:
    no defensive branch for a scenario the schema does not produce)."""
    if magnitude is None:
        return glow.ECLIPSE_GLOW_STRENGTH_MAX
    lo, hi = glow.ECLIPSE_MAGNITUDE_MIN, glow.ECLIPSE_MAGNITUDE_MAX
    fraction = max(0.0, min(1.0, (magnitude - lo) / (hi - lo)))
    lo_strength = glow.ECLIPSE_GLOW_STRENGTH_MIN
    hi_strength = glow.ECLIPSE_GLOW_STRENGTH_MAX
    return lo_strength + fraction * (hi_strength - lo_strength)


def eclipse_render_state(event) -> str:
    """The catalog (kind, type) -> render STATE lookup (owner decree
    2026-07-19, fix round C — `glow.ECLIPSE_TYPE_STATE`). An
    unknown/missing type (should not occur — see the config comment)
    documented-falls-back to the kind's PARTIAL state rather than
    raising, since a malformed catalog row must still render something
    plausible (Rule #1: visible degradation, not a crash)."""
    state = glow.ECLIPSE_TYPE_STATE.get((event.kind, event.type))
    if state is not None:
        return state
    return glow.ECLIPSE_STATE_FALLBACK[event.kind]


def eclipse_state_glow_strength(state: str, magnitude: float | None) -> float:
    """Glow strength for an eclipse render STATE: every state carries a
    fixed TYPE-driven fraction (`glow.ECLIPSE_STATE_GLOW_STRENGTH`)
    EXCEPT "solar_partial", the owner's one named exception, which keeps
    the original magnitude-linear mapping (`eclipse_glow_strength`)."""
    if state == "solar_partial":
        return eclipse_glow_strength(magnitude)
    return glow.ECLIPSE_STATE_GLOW_STRENGTH[state]
