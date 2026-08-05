"""The shared `SlotDescriptor` contract — one per weekday-body slot
(1st/2nd/3rd), each carrying its OWN setter callables. Originally
defined in the now-retired `app.slot_theme` window (Phase 6 FINAL
cleanup deleted it); the Watch Face window's Themes & Slots section
(`app/watch_face/themes.py`/`theme_tree.py`) is now the ONLY reader,
but the type lives in its own small module rather than inside
`watch_face/` so `controller.py` (the producer) never has to import
from the package it composes (Rule #5, no duplicate copies of the
shape either side of that boundary).
"""

from dataclasses import dataclass
from typing import Callable


@dataclass
class SlotDescriptor:
    """One slot's full config + its OWN setter callables."""

    index: int
    title: str
    mode_value: str
    style_value: str
    theme_value: str
    roster_value: str
    names_value: bool
    enabled_value: bool
    set_mode: Callable[[str], None]
    set_style_mode: Callable[[str, str], None]
    set_weekday: Callable[..., None]
    set_names: Callable[[bool], None]
