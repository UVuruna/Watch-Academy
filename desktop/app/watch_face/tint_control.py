"""THE COMPACT TINT CONTROL (owner ballot verdict 4A, 2026-08-15) — one
row per target, and the palette one click away instead of seven times
down the page.

What it replaces, measured before it was touched: the SAME grid of 42
preset swatches was drawn seven times on the Colors page — Ring tint,
Inner, Umbra, Aura-off, Hands, Jewels, Crown Text — about 290 circles,
many of them indistinguishable at swatch size (five greys, four
near-identical yellows), and the page ran three screens long. His words
on the ballot: the space was bought with nothing.

The shape now:

    Ring tint   (o)  Change…                    Gunmetal — #2A3439

and "Change…" opens a popover holding, in this order:

1. THE TWELVE SEATS — his own ballot pick, one row, no further click.
2. ALL COLOURS — the full Lighter/Darker grids, one reveal away, built
   by the SAME `tint_picker.build_preset_grids` the page used to call
   directly (Rule #5: the grid has one implementation, it simply moved
   behind a door).
3. CUSTOM — a K-360 hue wheel, which is the one place in this app where
   a value genuinely IS an angle (knob taxonomy, verdict 7). The wheel
   turns the hue live over a preview chip; the pick commits on Apply, so
   a spin does not fire 360 live rebuilds of the watch.

Nothing is lost: every hue the grids ever offered is still reachable,
and so is any hue at all.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QGuiApplication
from PySide6.QtWidgets import (
    QDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton,
    QVBoxLayout, QWidget,
)

from app.ui_style import tooltip_wrap
from app.watch_face import tint_picker
from app.watch_face.controls import KnobKind, ValueKnob, ValueUnit
from config import dial, palette

#: THE TWELVE SEATS (owner ballot verdict 2026-08-15, artifact
#: aae0a35d) — the tints that sit OPEN in the popover with no further
#: click. Scope is his too, in his own words on the ballot: "The same
#: twelve everywhere" — not per control, not last-used. So this is ONE
#: list and every tint control reads it.
#:
#: It lives HERE, not in `config.palette`, and the boundary is
#: responsibility (THE STRUCTURE LAW): the palette owns the HUES, this
#: module owns the PICKER, and "which twelve does the picker open with"
#: is a picker decision. (It sat in palette.py for one round and pushed
#: that module past the config-cohesion threshold, which is how the
#: question got asked at all.)
#:
#: NAMES, not hex: a seat points INTO `palette.RING_TINT_GROUPS`, so
#: retuning a hue there moves the seat with it, and deleting a name
#: breaks loudly at `open_seats()` instead of silently seating nothing.
OPEN_SEAT_NAMES = (
    "Gray", "Gold", "Satin Gold", "Copper", "Silver", "Slate Gray",
    "Glaucous", "Charcoal", "Gunmetal", "Navy", "Bordeaux", "Periwinkle",
)


def open_seats() -> tuple[tuple[str, str | None], ...]:
    """The twelve seats as (name, hue) in the owner's own order — "Gray"
    is the untouched art and carries None, exactly as it does in the
    grids. Raises on a name the grids no longer hold, because a seat
    that quietly disappears is how a ballot verdict gets lost."""
    known = {
        name: hue
        for presets in palette.RING_TINT_GROUPS.values()
        for name, hue in presets.items()
    }
    missing = [name for name in OPEN_SEAT_NAMES if name not in known]
    if missing:
        raise KeyError(
            "OPEN_SEAT_NAMES holds names RING_TINT_GROUPS no longer has: "
            f"{missing}"
        )
    return tuple((name, known[name]) for name in OPEN_SEAT_NAMES)


#: The popover's own swatch size — bigger than the page grid's, because
#: here there is room and the whole point is telling two greys apart.
_SEAT_PX = 34
_PREVIEW_PX = 44


def _seed_hue(current: str | None, seed: str) -> str:
    return current or seed


class TintPopover(QDialog):
    """The palette, opened on demand. A frameless `Qt.Popup` so it
    closes on a click outside — the ordinary behaviour for a picker that
    is not a decision the user has to confirm."""

    def __init__(
        self, tr, current: str | None, groups: dict, none_label: str,
        seed: str, on_pick, parent=None,
    ):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup)
        self._tr = tr
        self._on_pick = on_pick
        self._current = current
        layout = QVBoxLayout(self)

        layout.addWidget(_heading(tr("Picked for you")))
        layout.addLayout(self._seat_row(current, on_pick))

        # ALL COLOURS behind one reveal. Hidden, never absent: the full
        # grid is the promise that the twelve seats cost nothing.
        self._all = QWidget()
        all_column = QVBoxLayout(self._all)
        all_column.setContentsMargins(0, 0, 0, 0)
        grids, _swatches = tint_picker.build_preset_grids(
            tr, groups, current, on_pick, palette.RING_TINT_NONE_SWATCH,
        )
        all_column.addLayout(grids)
        self._all.setVisible(False)
        self._reveal = QPushButton(tr("All colours…"))
        self._reveal.setCheckable(True)
        self._reveal.toggled.connect(self._show_all)
        layout.addWidget(self._reveal)
        layout.addWidget(self._all)

        layout.addWidget(_heading(tr("Custom")))
        layout.addLayout(self._custom_row(current, seed, on_pick))

        footer = QHBoxLayout()
        default = QPushButton(tr(none_label))
        default.setToolTip(tooltip_wrap(tr(
            "Put this target back to its untouched state."
        )))
        default.clicked.connect(lambda: self._commit(None))
        footer.addWidget(default)
        footer.addStretch(1)
        layout.addLayout(footer)

    # ── the three rows ────────────────────────────────────────────────
    def _seat_row(self, current, on_pick) -> QGridLayout:
        """THE TWELVE SEATS, his order, six to a row so two rows of six
        read as a block rather than one long strip."""
        grid = QGridLayout()
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(6)
        for index, (name, hue) in enumerate(open_seats()):
            chip = QPushButton()
            chip.setToolTip(tooltip_wrap(
                f"{self._tr(name)} — {hue}" if hue
                else f"{self._tr(name)} — {self._tr('the untouched art')}"
            ))
            tint_picker.round_swatch(
                chip, hue or palette.RING_TINT_NONE_SWATCH, _SEAT_PX,
                selected=(hue == current),
            )
            chip.clicked.connect(lambda _c=False, h=hue: self._commit(h))
            grid.addWidget(chip, index // 6, index % 6)
        return grid

    def _custom_row(self, current, seed, on_pick) -> QHBoxLayout:
        """The K-360 hue wheel — the app's ONE angular value (knob
        taxonomy, verdict 7). It previews live and commits on Apply, so
        turning the wheel does not fire a rebuild of the watch per
        degree."""
        row = QHBoxLayout()
        start = QColor(_seed_hue(current, seed))
        self._preview = QFrame()
        self._preview.setFixedSize(_PREVIEW_PX, _PREVIEW_PX)  # layout-law: exempt - a colour chip is a fixed square sample, like a swatch
        self._paint_preview(start)
        knob = ValueKnob(
            "custom_hue", self._tr("Hue"),
            self._tr("The custom hue, in degrees around the colour wheel."),
            unit=ValueUnit.PLAIN, low=0, high=359, family="hue",
            kind=KnobKind.K360, on_change=self._turn,
        )
        knob.set_value(float(max(0, start.hue())))
        self._knob = knob
        self._custom = QColor(start)
        row.addWidget(knob)
        row.addWidget(self._preview)
        apply_button = QPushButton(self._tr("Apply"))
        apply_button.clicked.connect(
            lambda: self._commit(self._custom.name().upper())
        )
        row.addWidget(apply_button)
        row.addStretch(1)
        return row

    # ── behaviour ─────────────────────────────────────────────────────
    def _show_all(self, revealed: bool) -> None:
        """Reveal the full grids AND stay on screen.

        THE DEFECT THAT EARNED THIS (proof shot 2026-08-15, caught by
        opening the image rather than by any test): the popover is
        placed under its "Change…" button while it is narrow, and the
        reveal roughly doubles its width. Left to itself it grew to the
        RIGHT, straight off the window — "All colou…" cut mid-word, the
        whole Darker grid gone, the twelve seats cropped to two columns.
        A popup that grows must re-place itself, so the grown box is
        clamped back inside the screen it opened on."""
        self._all.setVisible(revealed)
        # ACTIVATE BEFORE MEASURING: `adjustSize` reads the layout's
        # CURRENT hint, and a widget shown a microsecond ago has not
        # been folded into it yet — the first attempt grew the box to a
        # width the revealed grids still overflowed, so the Darker
        # column was cut inside a popover that had already been resized
        # for it (proof shot 2026-08-15).
        self.layout().activate()
        self.adjustSize()
        screen = self.screen() or QGuiApplication.primaryScreen()
        if screen is None:
            return
        available = screen.availableGeometry()
        frame = self.frameGeometry()
        # Clamp right/bottom first, then left/top, so a box too big for
        # the screen ends flush at the top-left corner and shows its
        # BEGINNING rather than its middle.
        x = min(frame.x(), available.right() - frame.width() + 1)
        y = min(frame.y(), available.bottom() - frame.height() + 1)
        self.move(max(available.x(), x), max(available.y(), y))

    def _turn(self, degrees: float) -> None:
        """The wheel keeps the seed's saturation and value and moves only
        the HUE — a wheel that also flattened the other two would make
        every custom pick the same garish primary."""
        seed = QColor(self._custom)
        self._custom = QColor.fromHsv(
            int(degrees) % 360, seed.saturation() or 180, seed.value() or 200
        )
        # The ring SHOWS the value here, it does not label a family —
        # see the "hue" entry in palette.KNOB_FAMILY_COLORS.
        self._knob.ring_color = self._custom.name().upper()
        self._knob.update()
        self._paint_preview(self._custom)

    def _paint_preview(self, color: QColor) -> None:
        self._preview.setStyleSheet(
            f"background-color: {color.name().upper()};"
            " border: 1px solid #666; border-radius: 4px;"
        )

    def _commit(self, hue: str | None) -> None:
        self.close()
        self._on_pick(hue)


def _heading(text: str) -> QLabel:
    label = QLabel(text)
    label.setStyleSheet("font-weight: bold;")
    return label


def tint_control(
    tr, title: str, current: str | None, groups: dict, none_label: str,
    seed: str, on_pick,
) -> QWidget:
    """One target's whole colour control: swatch, "Change…", and the
    state in words on the right — the row that replaced a repeated
    grid."""
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(QLabel(tr(title)))
    # THE SWATCH LIVES IN ITS OWN CONTAINER (runtime audit ALG-5,
    # 2026-08-15): it is a QPushButton and so is "Change…", and the
    # uniform-siblings rule measures same-kind controls sharing one
    # container — a 22px circle beside an 86px button is exactly the
    # mismatch it is built to catch. The circle is a swatch, not a
    # button of the same family, and the honest way to say so is to stop
    # making them siblings.
    swatch = QPushButton()
    tint_picker.round_swatch(
        swatch, current or palette.RING_TINT_NONE_SWATCH,
        dial.RING_TINT_SWATCH_PX, selected=True,
    )
    swatch_host = QWidget()
    swatch_layout = QHBoxLayout(swatch_host)
    swatch_layout.setContentsMargins(0, 0, 0, 0)
    swatch_layout.addWidget(swatch)
    layout.addWidget(swatch_host)
    change = QPushButton(tr("Change…"))
    change.setToolTip(tooltip_wrap(tr(
        "The twelve picked colours, the full palette, and a custom hue."
    )))
    layout.addWidget(change)
    # THE STATE SITS BESIDE THE CONTROL, not across the row (proof shot
    # 2026-08-15): pushed to the far right by a stretch it was the first
    # thing a narrow window cut — "Gray (…" — and it reads better next
    # to the button it describes anyway. The stretch goes AFTER it, so
    # the leftover width stays leftover.
    state = QLabel(tint_picker.tint_label_text(tr, current, groups, none_label))
    layout.addWidget(state)
    layout.addStretch(1)

    def open_popover() -> None:
        popover = TintPopover(
            tr, current, groups, none_label, seed, on_pick, parent=row,
        )
        popover.move(change.mapToGlobal(change.rect().bottomLeft()))
        popover.show()

    # BOTH the swatch and the button open it: the swatch is the bigger,
    # more obvious target and a user who clicks the colour expects the
    # colours (measured on the old page, where the swatch did nothing).
    change.clicked.connect(open_popover)
    swatch.clicked.connect(open_popover)
    return row
