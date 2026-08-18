"""The Observatory — the statistics sibling of the Encyclopedia.

2026-07-16: "kao enciklopedija, samo sa statistikom").

Dark, QPainter-drawn, interactive charts over the long ephemeris data:
the season-duration oscillations (per-series checkboxes), the light−dark
envelope with the Anno Lucis dawn, every measured light/dark peak and
the era spans, the eclipse timeline (nearest past/next from the
traveled moment when the Deep Time pack is present; the bundled density
otherwise), the current location's day-length curve over the year, and
the La2004 Laskar long envelope over +/-200,000 years (charts-only —
ROADMAP 15a2). Series data reads only the committed bundles
(data/observatory.py) — the charts never require deep_time.sqlite.

Fix round D (owner verdicts 2026-07-19): every chart supports
mouse-wheel zoom centered on the cursor, drag-to-pan while zoomed and a
double-click reset, with the y axis auto-fitting the visible x slice on
every change (_ChartBase); a Days/Hours switch governs every
"light − dark" readout (_LineChart.set_y_fmt/set_diff_fmt).

The package's one public name; the split is an implementation detail to
every caller (R12 of the OOP audit, 2026-08-18).
"""

from app.observatory.dialog import ObservatoryDialog

__all__ = ["ObservatoryDialog"]
