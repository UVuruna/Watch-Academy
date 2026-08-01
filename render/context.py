"""The render protocol — the three types every layer speaks.

`Cadence` says how often a layer's content changes, `RenderContext`
carries everything a layer may read for one paint, and `Layer` is the
closed base class the compositor stacks. Every layer paints in a
coordinate system whose origin is the dial centre; dial angles are
degrees CLOCKWISE from the top (the core convention), converted to Qt's
counterclockwise-from-3-o'clock only inside the pie/position helpers in
[Painting](__about/painting.md).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from PySide6.QtGui import QPainter

from core.clock_state import DayContext, TickState
from render.assets import AssetCache
from skins.manifest import SkinDefinition


class Cadence(Enum):
    STATIC = "static"    # rebuild on skin/size/DPI change
    DAILY = "daily"      # rebuild on DayContext change
    MINUTE = "minute"    # painted live every tick


@dataclass(frozen=True)
class RenderContext:
    skin: SkinDefinition
    day: DayContext
    tick: TickState | None           # None while compositing STATIC/DAILY layers
    radius: float                    # logical px, dial radius
    cache: AssetCache
    dpr: float
    rotation: float = 0.0            # Star/Aura/Umbra/slot rotation: the solar
                                     # offset, or 0 in upright mode (the noon
                                     # marker stays solar — day.star_rotation)
    hovered: str | None = None       # element under the cursor ("earth",
                                     # "moon", "octa_slot", "body:<name>") —
                                     # drawn hover_enlarge times larger
    reveal_active: bool = False      # reveal-week (owner 2026-07-16): an
                                     # Omega double-click raises every
                                     # non-active weekday body to full
                                     # opacity for REVEAL_WEEK_DURATION_S
    archetype_lit: int | None = None  # Archetype mode (owner 2026-07-16):


class Layer(ABC):
    cadence: Cadence
    # HOVER-VARIABLE layers (owner 2026-07-17, ROADMAP 15f): even though
    # their content is DAILY, their APPEARANCE changes with the hover-
    # enlarge target and the reveal window, so the compositor NEVER bakes
    # them into the cached composite — it draws them LIVE every frame
    # (their pixmaps are already rasterize-cached). A hover enter/leave or
    # an Omega reveal then rebuilds NOTHING. The WeekdayLayer and the
    # ArchetypeLayer set this True.
    hover_variable: bool = False

    def __init__(self, skin: SkinDefinition, lift: bool = False):
        self._skin = skin
        # The hover Z-LIFT (owner 2026-07-13): the enlarged element must
        # ride ABOVE the hands. A base layer (lift=False) skips its
        # hovered element; HoverLiftLayer owns lift=True twins that
        # draw ONLY it, stacked last.
        self._lift = lift

    def _gate(self, ctx: "RenderContext", element: str) -> bool:
        """True when THIS pass draws `element`: the base pass draws all
        but the hovered one, the lift pass only the hovered one."""
        return (ctx.hovered == element) == self._lift

    @abstractmethod
    def paint(self, painter: QPainter, ctx: RenderContext) -> None: ...
