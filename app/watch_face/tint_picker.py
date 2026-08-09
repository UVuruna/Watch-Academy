"""Shared tint-picker widgets (see tint_picker.md) — the round swatch,
the Lighter/Darker preset grids and the "Custom…" hue picker, extracted
from `app.settings_dialog.colors_section` (Rule #5, Watch Face Phase 4)
so every color control that recolors through a `#RRGGBB` hue — Ring
tint, Umbra tint, Aura-off tint, Hands tint, Jewels tint — draws the
SAME picker instead of five near-identical copies.

Stateless builders: every function takes the CURRENT value and reads it
fresh — there is nothing to keep in sync afterwards, because the Watch
Face window is LIVE-APPLY (`window.WatchFaceDialog.refresh` rebuilds the
whole page on every pick, unlike the OK/Cancel `SettingsDialog`, which
keeps its own buffered state and repaints these widgets in place via
`repaint_selection`).
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout,
)

from config import dial


def round_swatch(
    chip: QPushButton, hue: str, size: int, selected: bool = False
) -> None:
    """Paint-style color circle (owner spec): a plain filled round
    button; the active swatch wears a white ring."""
    border = "2px solid #FFFFFF" if selected else "1px solid #666"
    chip.setFixedSize(size, size)  # layout-law: exempt - round color swatch, square by design, no text
    chip.setStyleSheet(
        f"background-color: {hue}; border: {border};"
        f"border-radius: {size // 2}px;"
        "/* radius-ok: circle content */"
    )


def preset_name(
    hue: str | None, groups: dict[str, dict[str, str | None]]
) -> str | None:
    """The preset NAME matching `hue` inside `groups` (the
    `palette.RING_TINT_GROUPS` shape: {group title: {preset name: hue-or-
    None}}), or None for a custom hex with no matching preset."""
    return next(
        (
            name
            for presets in groups.values()
            for name, preset_hue in presets.items()
            if preset_hue == hue and hue is not None
        ),
        None,
    )


def tint_label_text(
    tr, hue: str | None, groups: dict[str, dict[str, str | None]],
    none_label: str,
) -> str:
    """The hover-matching label (owner 2026-07-15): the preset's NAME
    beside its hex, the bare hex for a custom pick, or `none_label` for
    the untouched/"follow" state."""
    if hue is None:
        return tr(none_label)
    name = preset_name(hue, groups)
    return f"{tr(name)} — {hue}" if name is not None else hue


def build_preset_grids(
    tr, groups: dict[str, dict[str, str | None]], current: str | None,
    on_pick, none_swatch_hue: str,
) -> tuple[QVBoxLayout, list[tuple[QPushButton, str | None]]]:
    """The titled preset grids (owner 2026-07-15: split Lighter/Darker,
    generalized here to any titled grouping) — returns the layout plus
    the swatch list, so an OK/Cancel caller can `repaint_selection` after
    a pick without rebuilding the whole group."""
    # SIDE BY SIDE since the owner's 2026-08-09 review: the titled
    # groups (Lighter/Darker) used to stack vertically, doubling every
    # tint control's height for nothing while the right half of the
    # window stood empty — they now stand as COLUMNS in one row.
    column = QVBoxLayout()
    row_of_groups = QHBoxLayout()
    row_of_groups.setSpacing(24)
    swatches: list[tuple[QPushButton, str | None]] = []
    per_row = dial.RING_TINT_SWATCHES_PER_ROW
    for title, presets in groups.items():
        block = QVBoxLayout()
        label = QLabel(tr(title))
        label.setStyleSheet("font-weight: bold;")
        block.addWidget(label)
        grid = QGridLayout()
        grid.setHorizontalSpacing(4)
        grid.setVerticalSpacing(4)
        for index, (name, hue) in enumerate(presets.items()):
            chip = QPushButton()
            chip.setToolTip(
                f"{tr(name)} — {hue}"
                if hue
                else f"{tr(name)} — {tr('the untouched art')}"
            )
            chip.clicked.connect(lambda checked, chosen=hue: on_pick(chosen))
            round_swatch(
                chip, hue or none_swatch_hue, dial.RING_TINT_SWATCH_PX,
                selected=(hue == current),
            )
            swatches.append((chip, hue))
            grid.addWidget(chip, index // per_row, index % per_row)
        block.addLayout(grid)
        block.addStretch(1)
        row_of_groups.addLayout(block)
    row_of_groups.addStretch(1)
    column.addLayout(row_of_groups)
    return column, swatches


def repaint_selection(
    swatches: list[tuple[QPushButton, str | None]], current: str | None,
    none_swatch_hue: str,
) -> None:
    """Re-ring the swatch matching `current` (OK/Cancel callers only —
    the live-apply Watch Face window rebuilds the page instead)."""
    for chip, hue in swatches:
        round_swatch(
            chip, hue or none_swatch_hue, dial.RING_TINT_SWATCH_PX,
            selected=(hue == current),
        )


def build_custom_row(
    tr, current: str | None, seed: str, on_pick, dialog_title: str = "Pick a hue",
) -> QHBoxLayout:
    """The "Custom…" button opening `QColorDialog`, seeded from
    `current` (or `seed` when unset)."""
    row = QHBoxLayout()
    button = QPushButton(tr("Custom…"))

    def pick() -> None:
        chosen = QColorDialog.getColor(QColor(current or seed), None, dialog_title)
        if chosen.isValid():
            on_pick(chosen.name().upper())

    button.clicked.connect(pick)
    row.addWidget(button)
    row.addStretch(1)
    return row
