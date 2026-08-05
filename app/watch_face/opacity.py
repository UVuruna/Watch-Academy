"""Opacity section (R-15/R-35/R-36 + the moved rows, see opacity.md) —
the Watch Face window's Opacity page: every render alpha channel this
Phase's render hooks make speakable, grouped "Clock body" (the star
diamonds, the Aura's two arcs, the Umbra) and "Bodies on the ring" (the
Moon below the horizon, the Moon/Earth transit, the inactive weekday
icons, the Crown Text) — replacing the placeholder page. LIVE-APPLY
(Rule #5): every slider release calls its setter through `setters`; the
window rebuilds this page fresh on the next pick, like every other
Watch Face section.

Four rows were MOVED here from the RETIRED `app.settings_dialog.
display_section._build_opacity_group` (Pointer/Aura sunlight/Aura
twilight/Moon below horizon) — Phase 6 FINAL cleanup deleted that copy
outright; this module is now the ONLY reader/writer of those four
`Settings` fields. Three rows are NEW this Phase:

  * R-15 Umbra opacity (owner-requested): a plain layer-alpha
    multiplier at composite time
    (`render.layers.background.BackgroundLayer._draw_umbra`).
  * R-35 "Moon — hover over Earth": this dial has no mouse-hover state
    on the Moon marker — the render concept the brief's wording reads
    as is the Moon's existing rim-TRANSIT dimming when it visually
    meets the Earth marker (`render.daylight.moon_transit_opacity`),
    the closest honest match found.
  * R-36 "Inactive icons": the non-active weekday bodies' existing
    ghost opacity (`skins.manifest.WeekdaySpec.ghost_opacity`).

Every render alpha channel found while implementing this round (the
open-list note this module owes, per the task brief): the six rows
above are every alpha a `Settings`-reachable render hook could bind
to. Two more alpha-shaped fields turned up and are NOT wired — both are
owner-tuned ART CONSTANTS with no settings hook anywhere today (not
even in the OLD Settings dialog this Phase is replacing), so adding one
now would be a new feature this task never asked for, not a move:
`skins.manifest.YearMarkerSpec.moon_shadow_alpha` (the terminator
darkness drawn over the Moon disc) and the reveal-week opacity ramp
tied to `defaults.REVEAL_WEEK_DURATION_S`. Left alone, undebted — no
control anywhere points at them for this round to remove.

CROWN TEXT OPACITY (R-24/Phase-6-debt correction, owner 2026-08-05:
"Crown tekst je onaj tekst koji piše oko sata — faith, hope,
suffering") — the outer Great Seal motto arc IS this element
(`skins.manifest.SkinDefinition.motto_alpha`,
`render.layers.ring.RingLayer._draw_motto`); a plain DIRECT row (like
`umbra_alpha` — no per-skin variance exists to reset to), greyed out
with a tooltip when the active ring preset carries no motto
(`setters["ring_has_motto"]`, the SAME graceful-truth shape
`aura_group`'s Colorful gate uses in `colors.py`)."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout, QGroupBox, QHBoxLayout, QLabel, QPushButton, QSlider,
    QVBoxLayout, QWidget,
)


def build(settings, setters: dict, tr) -> QWidget:
    defaults = setters["opacity_skin_defaults"]()
    layout = QVBoxLayout()
    layout.addWidget(_clock_body_group(settings, setters, tr, defaults))
    layout.addWidget(_ring_bodies_group(settings, setters, tr, defaults))
    widget = QWidget()
    widget.setLayout(layout)
    return widget


def _override_row(
    tr, settings, setters, key: str, default_value: float, title: str,
    form: QFormLayout,
) -> QSlider:
    """A None-override row (owner spec: None follows the skin's own
    value) — "Skin default" resets the STORED override to None, not
    merely the slider position, so the render side actually stops
    overriding."""
    current = getattr(settings, key)
    value = round((current if current is not None else default_value) * 100)
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setRange(0, 100)
    slider.setValue(value)
    label = QLabel(f"{value}%")
    slider.valueChanged.connect(lambda v, lab=label: lab.setText(f"{v}%"))
    slider.sliderReleased.connect(lambda: setters[key](slider.value() / 100))
    reset = QPushButton(tr("Skin default"))
    default_pct = round(default_value * 100)

    def do_reset() -> None:
        slider.setValue(default_pct)
        setters[key](None)

    reset.clicked.connect(do_reset)
    row = QHBoxLayout()
    row.addWidget(slider)
    row.addWidget(label)
    row.addWidget(reset)
    form.addRow(tr(title), row)
    return slider


def _direct_row(
    tr, settings, setters, key: str, default_value: float, title: str,
    form: QFormLayout,
) -> QSlider:
    """A plain-value row (no None state — the field always carries its
    own float, like `moon_hidden_alpha` always has)."""
    value = round(getattr(settings, key) * 100)
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setRange(0, 100)
    slider.setValue(value)
    label = QLabel(f"{value}%")
    slider.valueChanged.connect(lambda v, lab=label: lab.setText(f"{v}%"))
    slider.sliderReleased.connect(lambda: setters[key](slider.value() / 100))
    reset = QPushButton(tr("Default"))
    default_pct = round(default_value * 100)

    def do_reset() -> None:
        slider.setValue(default_pct)
        setters[key](default_value)

    reset.clicked.connect(do_reset)
    row = QHBoxLayout()
    row.addWidget(slider)
    row.addWidget(label)
    row.addWidget(reset)
    form.addRow(tr(title), row)
    return slider


def _clock_body_group(settings, setters, tr, defaults: dict) -> QGroupBox:
    group = QGroupBox(tr("Clock body"))
    form = QFormLayout(group)
    _override_row(
        tr, settings, setters, "star_alpha", defaults["star_alpha"],
        "Pointer", form,
    )
    _override_row(
        tr, settings, setters, "aura_day_alpha", defaults["aura_day_alpha"],
        "Aura — sunlight", form,
    )
    twilight_slider = _override_row(
        tr, settings, setters, "aura_twilight_alpha",
        defaults["aura_twilight_alpha"], "Aura — twilight", form,
    )
    if settings.pointer == "aurora":
        # Aurora has no separate twilight opacity (owner 2026-07-12: the
        # dedicated dawn/dusk COLORS carry the meaning) — same gate the
        # OLD Settings copy runs.
        twilight_slider.setEnabled(False)
    _direct_row(tr, settings, setters, "umbra_alpha", 1.0, "Umbra", form)
    return group


def _ring_bodies_group(settings, setters, tr, defaults: dict) -> QGroupBox:
    group = QGroupBox(tr("Bodies on the ring"))
    form = QFormLayout(group)
    _direct_row(
        tr, settings, setters, "moon_hidden_alpha", 0.5,
        "Moon — below horizon", form,
    )
    _override_row(
        tr, settings, setters, "moon_transit_alpha",
        defaults["moon_transit_alpha"], "Moon — hover over Earth", form,
    )
    _override_row(
        tr, settings, setters, "ghost_alpha", defaults["ghost_alpha"],
        "Inactive icons", form,
    )
    crown_slider = _direct_row(
        tr, settings, setters, "motto_alpha", 1.0, "Crown Text", form,
    )
    if not setters["ring_has_motto"]():
        crown_slider.setEnabled(False)
        crown_slider.setToolTip(
            tr("The active ring preset carries no Crown Text (Great Seal motto).")
        )
    return group
