"""Colors section (R-21..R-25, see colors.md) — the Watch Face window's
Colors page: Ring tint, Pointer palette chips, Umbra coloring, Aura
coloring (Colorful-off only), Hands/Jewels free color, Metal shades and
the Saturation sliders — replacing the placeholder page. LIVE-APPLY
(Rule #5, same shape as every other Watch Face section): every pick
calls its setter immediately through `setters`, and the window rebuilds
this page fresh (`window.WatchFaceDialog.refresh`) — there is no
OK/Cancel state to keep in sync (contrast the RETIRED
`app.settings_dialog.colors_section`, whose mixin buffered picks until
the dialog's own OK; Phase 6 FINAL cleanup deleted that copy outright —
this module's `tint_picker` builders are the ONLY ones left, Rule #5).

CORRECTION (owner 2026-08-05, LOUD — both items below were WRONGLY
declared impossible; the owner's own art proved otherwise): R-21's
Outer/Inner ring-tint split and R-24's Crown Text color/size ARE built
this round —

  * R-21's Outer/Inner ring-tint split: the owner's split ring art
    (`assets/instrument/ring/outter/`+`inner/`) became THE
    COMPOSITIONAL RING MODEL (owner decree 2026-08-05) —
    `render.layers.ring.RingLayer._draw_bands` composes both bands
    UNCONDITIONALLY now, each with its OWN tint
    (`ring_tint`/`ring_tint_inner`). The "Inner (Minute track)" row
    below is always live — no more disk-presence gate.
  * R-24's Crown Text color: the outer arc IS the Great Seal crown text
    inscription (`RingSpec.crown_text`) — it always had a seat, just no
    control. `crown_text_tint` (this section) and `crown_text_scale`/`crown_text_alpha`
    (Size/Opacity sections) now read it independently of
    `jewels_tint`/`ring_jewels_scale`. See `skins.manifest.
    SkinDefinition`'s Crown Text fields for the full design note.

DEBT (owner honesty rule — a control that does nothing must never
ship): two items below are NOT built, each recorded where it would
otherwise live —

  * R-25's Jewels saturation as a SEPARATE slider: `ring_saturation`
    already scales the ring plate AND its jewels TOGETHER, a UNIFIED
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
from app.ui_style import tooltip_wrap
from app.watch_face.widgets import pill
from config import constants, dial, palette


def build(settings, setters: dict, tr) -> QWidget:
    layout = QVBoxLayout()
    layout.addWidget(_ring_tint_group(settings, setters, tr))
    layout.addWidget(_palette_group(settings, setters, tr))
    layout.addWidget(_umbra_group(settings, setters, tr))
    layout.addWidget(_aura_group(settings, setters, tr))
    layout.addWidget(_hands_group(settings, setters, tr))
    layout.addWidget(_jewels_group(settings, setters, tr))
    layout.addWidget(_crown_text_group(settings, setters, tr))
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
    Jewels/Umbra-custom/Aura-custom): the preset grids plus the Custom
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
    "Ring tint" in THIS window — the stored key is untouched; the
    retired Settings dialog copy was deleted outright by Phase 6).
    THE COMPOSITIONAL RING MODEL (owner decree 2026-08-05) made the
    outer/inner split the ONLY ring render path, so the "Inner (Minute
    track)" tint picker for `ring_tint_inner` is always live now — no
    more disk-presence gate."""
    group = _tint_group(
        tr, "Ring tint", settings.ring_tint, setters["ring_tint"],
        "Gray (default)", "Pick the ring tint",
    )
    inner = _tint_group(
        tr, "Inner (Minute track)", settings.ring_tint_inner,
        setters["ring_tint_inner"], "Follow outer (default)",
        "Pick the inner (minute track) tint",
    )
    group.layout().addWidget(inner)
    return group


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
    column = QVBoxLayout(group)
    row = QHBoxLayout()

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
        chip.setToolTip(tooltip_wrap(f"{tr(arm_labels[index])} — {hue}"))
        chip.clicked.connect(lambda checked, i=index: pick(i))
        row.addWidget(chip)
    row.addStretch(1)
    # ALG-5 (Zubi fix round 2026-08-09): "Reset to preset" moved OUT of
    # the swatch row into its own row — a text button is not a sibling
    # of twelve identical 34px circles, and in one container the rule
    # rightly demanded they share a size.
    reset = QPushButton(tr("Reset to preset"))
    reset.clicked.connect(
        lambda: setters["palettes"](pointer, style, tuple(preset))
    )
    reset_row = QHBoxLayout()
    reset_row.addWidget(reset)
    reset_row.addStretch(1)
    column.addLayout(row)
    column.addLayout(reset_row)
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
        group.setToolTip(tooltip_wrap(
            tr(
                "Turn off “Colorful” (right-click ▸ Visible) "
                "to color the plain Aura wedges."
            )
        ))
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


def _jewels_group(settings, setters, tr) -> QGroupBox:
    """R-24: Jewels (ring jewels) free color — an EXTRA tint layered
    OVER the metal finish (Gold/Bronze/Silver stay chosen in the Metal
    shades group below); "Gray" (None) leaves the metal finish
    untouched, today's behavior on every release before this Phase.
    Crown Text has its OWN independent tint below (`_crown_text_group`)
    — the two controls no longer share one recolor."""
    return _tint_group(
        tr, "Jewels color", settings.jewels_tint, setters["jewels_tint"],
        "Metal finish only (default)", "Pick the jewels tint",
    )


def _crown_text_group(settings, setters, tr) -> QGroupBox:
    """R-24/Phase-6-debt correction (owner 2026-08-05, LOUD: "Crown
    tekst je onaj tekst koji piše oko sata — faith, hope, suffering") —
    the outer Great Seal crown text arc's own free color, independent of
    `jewels_tint`: "Follow ring" (default, None) reads `ring_tint`
    exactly like the Hands do; a preset or custom hex overrides it.
    Greyed out with a tooltip when the active ring preset carries no
    crown text (`setters["ring_has_crown_text"]`) — the same graceful-truth
    pattern the Aura group's Colorful gate uses above."""
    group = _tint_group(
        tr, "Crown Text color", settings.crown_text_tint, setters["crown_text_tint"],
        "Follow ring (default)", "Pick the Crown Text tint",
    )
    if not setters["ring_has_crown_text"]():
        group.setEnabled(False)
        group.setToolTip(tooltip_wrap(
            tr("The active ring preset carries no Crown Text (Great Seal inscription).")
        ))
    return group


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
    (Hands/Umbra) — Jewels, Pointer and Crown stay OUT, each for its
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
