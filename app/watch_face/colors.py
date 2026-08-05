"""Colors section (R-21..R-25, see colors.md) — the Watch Face window's
Colors page: Ring tint, Pointer palette chips, Umbra coloring, Aura
coloring (Colorful-off only), Hands/Indices free color, Metal shades and
the Saturation sliders — replacing the placeholder page. LIVE-APPLY
(Rule #5, same shape as every other Watch Face section): every pick
calls its setter immediately through `setters`, and the window rebuilds
this page fresh (`window.WatchFaceDialog.refresh`) — there is no
OK/Cancel state to keep in sync (contrast
`app.settings_dialog.colors_section`, whose mixin buffers picks until
the dialog's own OK; that copy stays until Phase 6 retires it, and now
shares this module's `tint_picker` builders — Rule #5).

DEBT (owner honesty rule — a control that does nothing must never
ship): four items below are NOT built, each recorded where it would
otherwise live —

  * R-21's Outer/Inner ring-tint split (hour markers vs minute track):
    the ring band is ONE baked plate (`render.layers.ring.RingLayer.
    paint`'s `spec.asset`) with no separable layer per element —
    splitting the tint needs new ring ART, not a UI hook.
  * R-24's Crown Text color (and, by extension, Phase 6's proposed Size
    slider for it): no "Crown Text" element exists anywhere in the
    render stack — `render/skin_geometry.py`, `render/layers/ring.py`
    and `skins/manifest.py` were read end to end for this round and
    carry no such seat. The outer arc IS the Great Seal motto
    inscription (`RingSpec.motto`/`motto_metal`), already wired through
    `ring_finish`; nothing else reads as a third, separate text.
  * R-25's Indices saturation as a SEPARATE slider: `ring_saturation`
    already scales the ring plate AND its letters TOGETHER, a UNIFIED
    target sealed by owner decree (Session 21-D, fix round E,
    2026-07-19 — `render.layers.ring.RingLayer`'s own docstring).
    Splitting it back apart reverses that sealed decision without the
    owner asking, so it stays one slider.
  * R-25's Pointer (star-diamond) saturation: fix round E (2026-07-19)
    explicitly REMOVED saturation scaling from the star diamonds by
    owner request (`render.skin_geometry.aura_palette_for`'s own
    docstring: "the star diamonds themselves no longer move with it").
    Reintroducing it under a new name would be the same reversal.

R-23's naming note: the task brief's "Right Click -> Elements ->
Colorless" does not exist verbatim — the Visible menu (renamed from
Elements) carries a "Colorful" toggle instead (`settings.colorful`,
`render.layers.background.BackgroundLayer.paint`'s existing colorless
branch). This section's Aura group gates on `not settings.colorful`,
the closest honest reading of the brief; it is grayed out, not hidden,
while Colorful is on."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog, QComboBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QSlider, QVBoxLayout, QWidget,
)

from app.watch_face import tint_picker
from app.watch_face.widgets import pill
from config import constants, dial, palette


def build(settings, setters: dict, tr) -> QWidget:
    layout = QVBoxLayout()
    layout.addWidget(_ring_tint_group(settings, setters, tr))
    layout.addWidget(_palette_group(settings, setters, tr))
    layout.addWidget(_umbra_group(settings, setters, tr))
    layout.addWidget(_aura_group(settings, setters, tr))
    layout.addWidget(_hands_group(settings, setters, tr))
    layout.addWidget(_indices_group(settings, setters, tr))
    layout.addWidget(_metal_group(settings, setters, tr))
    layout.addWidget(_saturation_group(settings, setters, tr))
    widget = QWidget()
    widget.setLayout(layout)
    return widget


def _tint_group(
    tr, title: str, current: str | None, on_pick, none_label: str,
    dialog_title: str,
) -> QGroupBox:
    """The shared body of every simple tint control here (Ring/Hands/
    Indices/Umbra-custom/Aura-custom): the preset grids plus the Custom
    row plus the live label — one shape, five callers (Rule #5)."""
    group = QGroupBox(tr(title))
    column = QVBoxLayout(group)
    grids, _swatches = tint_picker.build_preset_grids(
        tr, palette.RING_TINT_GROUPS, current, on_pick,
        palette.RING_TINT_NONE_SWATCH,
    )
    column.addLayout(grids)
    row = tint_picker.build_custom_row(
        tr, current, palette.RING_TINT_PICKER_SEED, on_pick, dialog_title,
    )
    row.addWidget(
        QLabel(tint_picker.tint_label_text(tr, current, palette.RING_TINT_GROUPS, none_label))
    )
    column.addLayout(row)
    return group


def _ring_tint_group(settings, setters, tr) -> QGroupBox:
    """R-21 item 1: the Clock/ring tint picker, MOVED here (renamed
    "Ring tint" in THIS window only — the stored key and the Settings
    dialog's own label are untouched; that copy stays until Phase 6)."""
    return _tint_group(
        tr, "Ring tint", settings.ring_tint, setters["ring_tint"],
        "Gray (default)", "Pick the ring tint",
    )


def _palette_group(settings, setters, tr) -> QGroupBox:
    """R-21 item 2: the pointer palette chips, the LIVE-APPLY twin of
    `app.settings_dialog.colors_section._build_palette_group` —
    `setters["palettes"]` (`WatchController._set_watch_face_palette`)
    stores the WHOLE hue tuple at once, the same preset-equals-no-
    override rule the dialog's OK commit already runs."""
    pointer = settings.pointer
    style = palette.effective_palette_style(pointer, settings.palette_style)
    key = f"{pointer}_{style}"
    preset = palette.PALETTE_PRESETS[(pointer, style)]
    hues = list(settings.palettes.get(key, preset))
    arm_labels = palette.pointer_arm_labels(pointer, style)
    group = QGroupBox(
        tr("Palette — {pointer} {style}").format(
            pointer=constants.POINTER_DISPLAY_NAMES[pointer],
            style=style.capitalize(),
        )
    )
    row = QHBoxLayout(group)

    def pick(index: int) -> None:
        chosen = QColorDialog.getColor(QColor(hues[index]), None, "Pick a hue")
        if not chosen.isValid():
            return
        new_hues = list(hues)
        new_hues[index] = chosen.name().upper()
        setters["palettes"](pointer, style, tuple(new_hues))

    for index, hue in enumerate(hues):
        chip = QPushButton()
        tint_picker.round_swatch(chip, hue, dial.PALETTE_SWATCH_PX)
        chip.setToolTip(f"{tr(arm_labels[index])} — {hue}")
        chip.clicked.connect(lambda checked, i=index: pick(i))
        row.addWidget(chip)
    row.addStretch(1)
    reset = QPushButton(tr("Reset to preset"))
    reset.clicked.connect(
        lambda: setters["palettes"](pointer, style, tuple(preset))
    )
    row.addWidget(reset)
    return group


def _umbra_group(settings, setters, tr) -> QGroupBox:
    """R-22: "Follow ring" (default, today's unchanged behavior) or a
    custom hex — the Outer/Inner split some readers might expect does
    not apply to the Umbra (it has no separate bands, only its
    brightness ladder — the split belongs to the Ring, see the module
    docstring's debt note)."""
    group = QGroupBox(tr("Umbra coloring"))
    column = QVBoxLayout(group)
    mode_row = QHBoxLayout()
    for mode, title in (("follow", "Follow ring"), ("custom", "Custom color")):
        mode_row.addWidget(pill(
            tr(title), settings.umbra_tint_mode == mode,
            lambda m=mode: setters["umbra_tint_mode"](m),
        ))
    column.addLayout(mode_row)
    if settings.umbra_tint_mode == "custom":
        column.addWidget(_tint_group(
            tr, "Custom Umbra tint", settings.umbra_tint,
            setters["umbra_tint"], "Gray (default)", "Pick the Umbra tint",
        ))
    return group


def _aura_group(settings, setters, tr) -> QGroupBox:
    """R-23: active only while "Colorful" is OFF (see the module
    docstring's naming note) — the day/twilight wedges then wear ONE
    flat hue: follow-ring-to-white, plain white, plain black, or
    custom. Grayed out (never hidden) while Colorful is on — an honest
    gate, not a dead control."""
    enabled = not settings.colorful
    group = QGroupBox(tr("Aura coloring (while Colorful is off)"))
    if not enabled:
        group.setToolTip(
            tr(
                "Turn off “Colorful” (right-click ▸ Visible) "
                "to color the plain Aura wedges."
            )
        )
    column = QVBoxLayout(group)
    mode_row = QHBoxLayout()
    for mode, title in (
        ("follow", "Follow ring (to white)"), ("white", "White"),
        ("black", "Black"), ("custom", "Custom color"),
    ):
        mode_row.addWidget(pill(
            tr(title), settings.aura_off_tint_mode == mode,
            lambda m=mode: setters["aura_off_tint_mode"](m),
        ))
    column.addLayout(mode_row)
    if settings.aura_off_tint_mode == "custom":
        column.addWidget(_tint_group(
            tr, "Custom Aura off-color", settings.aura_off_tint,
            setters["aura_off_tint"], "White (default)",
            "Pick the Aura off-color",
        ))
    group.setEnabled(enabled)   # cascades to every child above
    return group


def _hands_group(settings, setters, tr) -> QGroupBox:
    """R-24: Hands free color — picking "Gray" (None) reverts to
    following the ring tint, exactly like every release before this
    Phase; a preset or custom hex overrides it independently."""
    return _tint_group(
        tr, "Hands color", settings.hands_tint, setters["hands_tint"],
        "Follow ring (default)", "Pick the hands tint",
    )


def _indices_group(settings, setters, tr) -> QGroupBox:
    """R-24: Indices (ring letters) free color — an EXTRA tint layered
    OVER the metal finish (Gold/Bronze/Silver stay chosen in the Metal
    shades group below); "Gray" (None) leaves the metal finish
    untouched, today's behavior on every release before this Phase.
    Crown Text has no control here — see the module docstring's debt
    note (no such element exists to color)."""
    return _tint_group(
        tr, "Indices color", settings.letter_tint, setters["letter_tint"],
        "Metal finish only (default)", "Pick the indices tint",
    )


def _metal_group(settings, setters, tr) -> QGroupBox:
    """Metal shades — MOVED here from the Settings dialog's Themes
    section (`app.settings_dialog.themes_section._build_metal_shade_
    group`, R8a round): the same three combos, the same stored keys,
    now LIVE instead of OK-committed."""
    group = QGroupBox(tr("Metal shades"))
    form = QFormLayout(group)
    titles = {"gold": tr("Gold"), "bronze": tr("Bronze"), "silver": tr("Silver")}
    current = {
        "gold": settings.metal_shade_gold,
        "bronze": settings.metal_shade_bronze,
        "silver": settings.metal_shade_silver,
    }
    for metal in ("gold", "bronze", "silver"):
        combo = QComboBox()
        for shade in constants.METAL_SHADE_NAMES[metal]:
            combo.addItem(tr(constants.METAL_SHADE_TITLES[shade]), shade)
        index = combo.findData(current[metal])
        if index >= 0:
            combo.setCurrentIndex(index)
        combo.currentIndexChanged.connect(
            lambda _i, c=combo, m=metal: setters[f"metal_shade_{m}"](c.currentData())
        )
        form.addRow(titles[metal], combo)
    return group


def _saturation_group(settings, setters, tr) -> QGroupBox:
    """R-25: the two owner-sealed sliders (Aura/Ring, unchanged) plus
    two bounded additions this Phase's render hooks make possible
    (Hands/Umbra) — Indices, Pointer and Crown stay OUT, each for its
    own reason in the module docstring's debt note."""
    group = QGroupBox(tr("Saturation"))
    form = QFormLayout(group)

    def add_row(title: str, key: str, range_const, step_const) -> None:
        low, high = range_const
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(round(low * 100), round(high * 100))
        slider.setSingleStep(step_const)
        value = round(getattr(settings, key) * 100)
        slider.setValue(value)
        label = QLabel(f"{value}%")
        slider.valueChanged.connect(
            lambda new_value, lab=label: lab.setText(f"{new_value}%")
        )
        slider.sliderReleased.connect(
            lambda: setters[key](slider.value() / 100)
        )
        reset = QPushButton(tr("Default"))

        def do_reset() -> None:
            slider.setValue(100)
            setters[key](1.0)

        reset.clicked.connect(do_reset)
        row = QHBoxLayout()
        row.addWidget(slider)
        row.addWidget(label)
        row.addWidget(reset)
        form.addRow(title, row)

    add_row(
        tr("Aura"), "pointer_saturation",
        constants.POINTER_SATURATION_RANGE, constants.POINTER_SATURATION_SLIDER_STEP,
    )
    add_row(
        tr("Ring"), "ring_saturation",
        constants.RING_SATURATION_RANGE, constants.RING_SATURATION_SLIDER_STEP,
    )
    add_row(
        tr("Hands"), "hands_saturation",
        constants.HANDS_SATURATION_RANGE, constants.HANDS_SATURATION_SLIDER_STEP,
    )
    add_row(
        tr("Umbra"), "umbra_saturation",
        constants.UMBRA_SATURATION_RANGE, constants.UMBRA_SATURATION_SLIDER_STEP,
    )
    return group
