"""Time Travel — the owner's scenario tester.

A small dialog takes any moment and any position (latitude, longitude);
the dial then renders that situation for one minute and resets to the
present by itself. The entered wall time is interpreted in the
currently configured timezone.

Since Session 16 (owner slika 13) the moment editor accepts ANY year of
the active coverage INCLUDING BCE: QDateTimeEdit cannot hold negative
years, so the editor is a day spinbox + month combo + year spinbox + an
ERA combo whose labels follow the era_notation setting ("BCE/CE"
default or "BC/AD" — the year INPUT is official-only, owner amendment
2026-07-17). Internally everything is the astronomical year (1 BCE =
year 0); the moment returned to the controller is the 400-year PROXY
datetime plus its cycle count (core/deep_time.py). The header line
pairs the target with its Anno Lucis year (and the optional third
calendar) via the ONE formatter.
"""

from datetime import datetime

from PySide6.QtCore import Qt, QTime
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTimeEdit,
)

from app.theme import apply_theme
from app.ui_style import style_button
from config import constants, defaults
from config.ui_text import ui
from core.deep_time import (
    astro_from_display,
    canonical_proxy,
    display_from_astro,
    era_names,
    format_official,
    format_year_line,
    month_length,
)

_MONTHS_SHORT = (
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
)


class TimeTravelDialog(QDialog):
    # The third exit (owner 2026-07-15): end the simulation and return
    # the dial to the present immediately (Accepted=1, Rejected=0).
    RETURN_TO_NOW = 2

    def __init__(
        self, latitude: float, longitude: float, parent=None,
        overlay: dict | None = None,
        initial_moment: datetime | None = None,
        initial_cycles: int = 0,
        coverage: tuple[int, int] | None = None,
        core_coverage: tuple[int, int] | None = None,
        era_notation: str = "bce_ce",
        show_era_suffix: bool = False,
        third_era: str = "none",
        deep_pack: bool = False,
    ):
        super().__init__(parent)
        tr = lambda text: ui(overlay or {}, text)  # noqa: E731 — dialog chrome
        self._tr = tr
        # The ACTIVE year span (astronomical years): the bundled seasons
        # ∩ moon intersection, widened to the Deep Time pack span when
        # the pack is present. A target outside it is refused BEFORE
        # travelling (owner 2026-07-16). core_coverage is the bundled
        # minute-exact tier — the precision line reads from it.
        self._coverage = coverage
        self._core_coverage = core_coverage
        self._notation = era_notation
        self._suffix = show_era_suffix
        self._third_era = third_era
        self._deep_pack = deep_pack
        self.setWindowTitle(f"{constants.APP_NAME} — {tr('Time Travel')}")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        # A running simulation seeds the moment (owner 2026-07-14) —
        # the PROXY frame plus its cycles arrive from the controller and
        # convert to the real astronomical calendar here.
        if initial_moment is None:
            raise ValueError(
                "TimeTravelDialog needs the initial moment — the "
                "controller passes now or the running simulation"
            )
        astro_year = (
            initial_moment.year
            - initial_cycles * constants.GREGORIAN_CYCLE_YEARS
        )

        # --- The moment editor (owner slika 13) -----------------------
        self._day = QSpinBox(self)
        self._day.setRange(1, month_length(astro_year, initial_moment.month))
        self._day.setValue(initial_moment.day)
        self._month = QComboBox(self)
        self._month.addItems([tr(month) for month in _MONTHS_SHORT])
        self._month.setCurrentIndex(initial_moment.month - 1)
        self._year = QSpinBox(self)
        self._year.setGroupSeparatorShown(False)
        # The year INPUT is official-only (owner amendment 2026-07-17):
        # the era combo carries the notation's two labels; Anno Lucis
        # and the third calendar are display, not input.
        self._era = QComboBox(self)
        self._era.addItems([tr(name) for name in era_names(era_notation)])
        display_year, era_index = display_from_astro(astro_year)
        self._configure_year_range(era_index)
        self._year.setValue(display_year)
        self._era.setCurrentIndex(era_index)
        self._time = QTimeEdit(self)
        self._time.setDisplayFormat("HH:mm")
        self._time.setTime(QTime(initial_moment.hour, initial_moment.minute))
        moment_row = QHBoxLayout()
        moment_row.addWidget(self._day)
        moment_row.addWidget(self._month)
        moment_row.addWidget(self._year, stretch=1)
        moment_row.addWidget(self._era)
        moment_row.addWidget(self._time)

        low, high = constants.LATITUDE_RANGE
        self._latitude = QDoubleSpinBox(self)
        self._latitude.setRange(low, high)
        self._latitude.setDecimals(4)
        self._latitude.setValue(latitude)
        low, high = constants.LONGITUDE_RANGE
        self._longitude = QDoubleSpinBox(self)
        self._longitude.setRange(low, high)
        self._longitude.setDecimals(4)
        self._longitude.setValue(longitude)

        layout = QFormLayout(self)
        # The DUAL CALENDAR header (Session 16): the target year in the
        # active notation beside its Anno Lucis form, live.
        self._header = QLabel(self)
        layout.addRow(self._header)
        layout.addRow(tr("Moment:"), moment_row)
        layout.addRow(tr("Latitude:"), self._latitude)
        layout.addRow(tr("Longitude:"), self._longitude)
        layout.addRow(
            QLabel(
                tr(
                    "The dial shows this situation for {n} seconds, "
                    "then returns to the present."
                ).format(n=defaults.TIME_TRAVEL_DURATION_S)
            )
        )
        # The coverage and PRECISION TIER lines (owner 2026-07-16, the
        # three tiers documented in-app) — live with the entered year.
        self._coverage_line = QLabel(self)
        self._coverage_line.setWordWrap(True)
        layout.addRow(self._coverage_line)
        self._tier_line = QLabel(self)
        self._tier_line.setWordWrap(True)
        layout.addRow(self._tier_line)
        # Coverage warning — hidden until an out-of-range OK (owner
        # 2026-07-16): the dialog stays open and no travel starts.
        self._coverage_warning = QLabel(self)
        self._coverage_warning.setWordWrap(True)
        self._coverage_warning.setStyleSheet(
            f"color: {defaults.TIME_TRAVEL_WARNING_COLOR};"
        )
        self._coverage_warning.hide()
        layout.addRow(self._coverage_warning)
        # The shared vivid buttons (owner 2026-07-15: the stylized ones
        # we use), NOW standing on the LEFT — back to the present, the
        # simulation ends immediately.
        row = QHBoxLayout()
        now = QPushButton(tr("Now"), self)
        style_button(now, "home", small=True)
        now.setToolTip(
            tr("Back to the present — the simulation ends immediately.")
        )
        now.clicked.connect(lambda: self.done(self.RETURN_TO_NOW))
        ok = QPushButton(tr("OK"), self)
        style_button(ok, "next", small=True)
        ok.clicked.connect(self.accept)
        cancel = QPushButton(tr("Cancel"), self)
        style_button(cancel, "neutral", small=True)
        cancel.clicked.connect(self.reject)
        row.addWidget(now)
        row.addStretch(1)
        row.addWidget(ok)
        row.addWidget(cancel)
        layout.addRow(row)

        self._day.valueChanged.connect(self._refresh)
        self._month.currentIndexChanged.connect(self._refresh)
        self._year.valueChanged.connect(self._refresh)
        self._era.currentIndexChanged.connect(self._on_era)
        apply_theme(self)
        self._refresh()

    # --- The astronomical target ---------------------------------------------

    def astro_year(self) -> int:
        """The entered year as an astronomical year (1 BCE = 0)."""
        return astro_from_display(
            self._year.value(), max(self._era.currentIndex(), 0)
        )

    def moment(self) -> datetime:
        """The naive PROXY wall time (the controller attaches the
        active timezone); pair with cycles() for the real year."""
        proxy, _ = canonical_proxy(
            self.astro_year(), self._month.currentIndex() + 1,
            self._day.value(), self._time.time().hour(),
            self._time.time().minute(),
        )
        return proxy

    def cycles(self) -> int:
        """The proxy cycle count of the entered moment."""
        return canonical_proxy(
            self.astro_year(), self._month.currentIndex() + 1,
            self._day.value(),
        )[1]

    def latitude(self) -> float:
        return self._latitude.value()

    def longitude(self) -> float:
        return self._longitude.value()

    # --- Coverage and the tier lines -------------------------------------------

    def target_within_coverage(self) -> bool:
        """True when the entered year lies inside the ACTIVE coverage —
        the guard that keeps Time Travel from ever reaching the day
        build's die-visibly path (owner 2026-07-16). Always true when no
        coverage was supplied."""
        if self._coverage is None:
            return True
        first, last = self._coverage
        return first <= self.astro_year() <= last

    def accept(self) -> None:
        """Refuse an out-of-range target inline instead of travelling:
        the message shows and the dialog stays open (owner 2026-07-16)."""
        if not self.target_within_coverage():
            first, last = self._coverage
            span = (
                f"{format_official(first, self._notation, self._suffix)} … "
                f"{format_official(last, self._notation, self._suffix)}"
            )
            if self._deep_pack:
                # Tier (iii), documented in-app: beyond the Deep Time
                # span only era lengths are known — no dates.
                message = self._tr(
                    "Time Travel covers {span} — beyond the Deep Time "
                    "span only era lengths are known (Laskar), no exact "
                    "dates."
                ).format(span=span)
            else:
                deep_first, deep_last = defaults.DEEP_TIME_YEAR_RANGE
                message = self._tr(
                    "Time Travel covers {span} for now — the Deep Time "
                    "data pack extends it to {deep_first}…{deep_last} "
                    "(not installed)."
                ).format(
                    span=span, deep_first=deep_first, deep_last=deep_last,
                )
            self._coverage_warning.setText(message)
            self._coverage_warning.show()
            self.adjustSize()
            return
        super().accept()

    # --- Live refresh -----------------------------------------------------------

    def _configure_year_range(self, era_index: int) -> None:
        """The year spinbox bounds for the active era pick. Deliberately
        WIDER than the active coverage (the greater of the coverage and
        the advertised Deep Time span): the owner must be able to DIAL
        an out-of-range year and READ the explanation on OK (owner
        2026-07-16 — a clamped spinbox would silently swallow the
        target instead)."""
        first, last = self._coverage or defaults.DEEP_TIME_YEAR_RANGE
        adv_first, adv_last = defaults.DEEP_TIME_YEAR_RANGE
        if era_index == 1:                   # BCE/BC: 1 BCE = astro 0
            self._year.setRange(1, max(1 - first, 1 - adv_first))
        else:                                # CE/AD
            self._year.setRange(1, max(last, adv_last))

    def _on_era(self) -> None:
        self._configure_year_range(self._era.currentIndex())
        self._refresh()

    def _refresh(self) -> None:
        """Every edit re-clamps the day to the real month length
        (proleptic Gregorian in the astronomical year), refreshes the
        dual-calendar header and the coverage/precision lines, and
        clears a stale refusal."""
        year = self.astro_year()
        self._day.setMaximum(month_length(year, self._month.currentIndex() + 1))
        # The DUAL CALENDAR header (owner amendment 2026-07-17): the
        # official target date with its Anno Lucis year always beside
        # it, plus the optional third calendar — the ONE formatter.
        self._header.setText(
            f"<b>{self._day.value()} "
            f"{self._tr(_MONTHS_SHORT[self._month.currentIndex()])} "
            f"{format_year_line(
                year, self._notation, self._suffix, self._third_era,
                self._month.currentIndex() + 1, self._day.value(),
            )}</b>"
        )
        if self._coverage is not None:
            first, last = self._coverage
            self._coverage_line.setText(
                self._tr("Coverage: {first} … {last}").format(
                    first=format_official(first, self._notation, self._suffix),
                    last=format_official(last, self._notation, self._suffix),
                )
            )
            if self._core_coverage and (
                self._core_coverage[0] <= year <= self._core_coverage[1]
            ):
                tier = self._tr(
                    "Precision: minute-exact (core years {first}–{last})."
                ).format(
                    first=self._core_coverage[0], last=self._core_coverage[1]
                )
            elif first <= year <= last:
                tier = self._tr(
                    "Precision: events exact; the local clock drifts "
                    "±hours at the far extremes (ΔT)."
                )
            else:
                tier = self._tr(
                    "Precision: beyond the data — only era lengths are "
                    "known (Laskar), no dates."
                )
            self._tier_line.setText(tier)
        self._coverage_warning.hide()
