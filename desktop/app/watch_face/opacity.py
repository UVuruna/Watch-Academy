"""Opacity section (R-15/R-36 + the moved rows, see opacity.md) — the
Watch Face window's Opacity page, and the FIRST section migrated to THE
ELEMENT CLASSES (owner ballot verdicts 2026-08-14, classes phase): the
sliders + Default/Skin-default buttons became K-270D VALUE KNOBS
(`controls.ValueKnob`, opacity family gold ring) flowing CENTERED per
group. The green default notch replaces the reset button (verdict 7A);
for the OVERRIDE rows its click stores None through `on_reset`, so the
render side genuinely stops overriding — the same law the old "Skin
default" button enforced.

Content is unchanged from the slider era: "Clock body" (the star
diamonds, the Aura's two arcs, the Umbra) and "Bodies on the ring" (the
Moon below the horizon, the inactive weekday icons, the Crown Text) —
LIVE-APPLY, commit on release/wheel/exact entry. The Aurora twilight
gate and the crown-text gate keep their graceful-truth shape (grayed
with a tooltip, never hidden).

History and the alpha-channel survey (which fields exist, which two
alpha-shaped constants stay deliberately unwired, why the Moon groups
moved out) is unchanged from the pre-knob revision — see opacity.md.
"""

from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QWidget

from app.ui_style import tooltip_wrap
from app.watch_face.controls import ValueKnob, ValueUnit, knob_row
from app.watch_face.widgets import FlowLayout


def build(settings, setters: dict, tr) -> QWidget:
    defaults = setters["opacity_skin_defaults"]()
    layout = QVBoxLayout()
    layout.addWidget(_clock_body_group(settings, setters, tr, defaults))
    layout.addWidget(_ring_bodies_group(settings, setters, tr, defaults))
    widget = QWidget()
    widget.setLayout(layout)
    return widget


def _knob(
    tr, settings, setters, key: str, default_value: float, title: str,
    blurb: str, override: bool,
) -> ValueKnob:
    """One opacity knob. `override=True` is the None-follows-the-skin
    law: the notch stores None (`on_reset`), a turn stores the float."""
    current = getattr(settings, key)
    shown = current if current is not None else default_value
    knob = ValueKnob(
        key, tr(title), tr(blurb),
        unit=ValueUnit.PERCENT, low=0, high=100, family="opacity",
        default_value=round(default_value * 100),
        on_change=lambda value, k=key: setters[k](value / 100),
        on_reset=(lambda k=key: setters[k](None)) if override else None,
    )
    knob.set_value(round(shown * 100))
    return knob


def _flow_group(title: str, knobs) -> QGroupBox:
    group = QGroupBox(title)
    column = QVBoxLayout(group)
    flow = FlowLayout()
    for knob in knobs:
        flow.addWidget(knob_row(knob))
    host = QWidget()
    host.setLayout(flow)
    column.addWidget(host)
    return group


def _clock_body_group(settings, setters, tr, defaults: dict) -> QGroupBox:
    star = _knob(
        tr, settings, setters, "star_alpha", defaults["star_alpha"],
        "Pointer", "The star diamonds' opacity — the notch follows the skin.",
        override=True,
    )
    day = _knob(
        tr, settings, setters, "aura_day_alpha", defaults["aura_day_alpha"],
        "Aura — sunlight",
        "The daylight arc's opacity — the notch follows the skin.",
        override=True,
    )
    twilight = _knob(
        tr, settings, setters, "aura_twilight_alpha",
        defaults["aura_twilight_alpha"], "Aura — twilight",
        "The twilight arc's opacity — the notch follows the skin.",
        override=True,
    )
    if settings.pointer == "aurora":
        # Aurora has no separate twilight opacity (owner 2026-07-12: the
        # dedicated dawn/dusk COLORS carry the meaning) — same gate the
        # slider era ran, grayed never hidden.
        twilight.setEnabled(False)
        twilight.setToolTip(tooltip_wrap(tr(
            "Aurora's dawn/dusk colors carry the twilight — no separate opacity."
        )))
    umbra = _knob(
        tr, settings, setters, "umbra_alpha", 1.0, "Umbra",
        "The night shadow's opacity.", override=False,
    )
    return _flow_group(tr("Clock body"), (star, day, twilight, umbra))


def _ring_bodies_group(settings, setters, tr, defaults: dict) -> QGroupBox:
    moon = _knob(
        tr, settings, setters, "moon_hidden_alpha", 0.5,
        "Moon — below horizon",
        "How faint the Moon draws while under the horizon.", override=False,
    )
    ghost = _knob(
        tr, settings, setters, "ghost_alpha", defaults["ghost_alpha"],
        "Inactive icons",
        "The non-active weekday bodies' ghost opacity — the notch follows the skin.",
        override=True,
    )
    crown = _knob(
        tr, settings, setters, "crown_text_alpha", 1.0, "Crown Text",
        "The Great Seal inscription's opacity.", override=False,
    )
    if not setters["ring_has_crown_text"]():
        crown.setEnabled(False)
        crown.setToolTip(tooltip_wrap(tr(
            "The active ring preset carries no Crown Text (Great Seal inscription)."
        )))
    return _flow_group(tr("Bodies on the ring"), (moon, ghost, crown))
