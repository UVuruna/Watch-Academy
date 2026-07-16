"""Shared setup and root-finding for the DOMY Watch ephemeris pipeline.

Pure computation over the Swiss Ephemeris DE441-derived data files. No app
code, no Qt. The one job here is: given a MONOTONIC ecliptic-angle function
of Julian Day (TT), enumerate every crossing of the 90-degree marks across
the full -13000..+17000 span.

Both the Sun's ecliptic longitude and the Sun-Moon elongation increase
strictly and smoothly with time (the Sun ~0.9856 deg/day, the elongation
~12.19 deg/day), so a single unwrapped-angle marcher serves both.
"""

import os
import swisseph as swe

HERE = os.path.dirname(os.path.abspath(__file__))
EPHE_DIR = os.path.join(HERE, "ephe")

# Span to scan (astronomical years; 0 == 1 BCE). The compressed .se1 Sun/Moon
# files in this set actually cover -12999-05-03 .. +17182-10-15 (probed), a
# touch narrower than the DE441 nominal -13200..+17191. We scan the whole
# usable interval; SCAN_JD_FLOOR clamps the start a hair inside the data.
YEAR_START = -12999
YEAR_END = 17000
SCAN_JD_FLOOR = -3026604.0   # ~ -12999-05-04, just inside the Sun/Moon floor
# Empirical data ceiling is ~JD 7929133.5 (~year 16994). We stop 800 days
# short so the marcher's forward bracketing never probes past the last file.
SCAN_JD_CEIL = 7928333.0     # ~ 16992-11, safely inside the upper limit

# Geocentric apparent ecliptic longitude of date (tropical) — the frame in
# which equinoxes/solstices are DEFINED (0=vernal, 90=summer, 180=autumn,
# 270=winter). SWIEPH selects the Astrodienst compressed files.
FLAGS = swe.FLG_SWIEPH

# Angular tolerance for a crossing, in degrees. 1e-6 deg of Sun motion is
# ~0.1 s of clock time; of Moon elongation ~7 ms. Far finer than the ΔT
# uncertainty, so time precision is limited by ΔT, not by this.
TOL_DEG = 1e-6

SUN_RATE = 0.98565      # deg/day, mean Sun ecliptic motion
ELONG_RATE = 12.19075   # deg/day, mean Sun-Moon elongation rate


def init(ephe_dir: str = EPHE_DIR) -> None:
    swe.set_ephe_path(ephe_dir)


def sun_lon(jd_tt: float) -> float:
    """Apparent geocentric ecliptic longitude of the Sun, degrees [0,360)."""
    xx, _ = swe.calc(jd_tt, swe.SUN, FLAGS)
    return xx[0]


def elongation(jd_tt: float) -> float:
    """Sun-Moon elongation (Moon lon - Sun lon), degrees [0,360)."""
    sun, _ = swe.calc(jd_tt, swe.SUN, FLAGS)
    moon, _ = swe.calc(jd_tt, swe.MOON, FLAGS)
    return (moon[0] - sun[0]) % 360.0


def jd_ut_of(jd_tt: float) -> float:
    """UT Julian Day for a TT instant. ΔT is itself uncertain over
    millennia (hours), so this is the honest best estimate, not exact."""
    return jd_tt - swe.deltat(jd_tt)


def iso_ut(jd_ut: float) -> str:
    """Proleptic-Gregorian ISO-ish stamp for a UT Julian Day."""
    y, m, d, ut = swe.revjul(jd_ut, swe.GREG_CAL)
    hh = int(ut)
    mm = int((ut - hh) * 60)
    ss = int(round((((ut - hh) * 60) - mm) * 60))
    if ss == 60:
        ss = 0
        mm += 1
    if mm == 60:
        mm = 0
        hh += 1
    return f"{y:+06d}-{m:02d}-{d:02d}T{hh:02d}:{mm:02d}:{ss:02d}Z"


class Marcher:
    """Walks a strictly-increasing angle function forward, yielding the JD
    of every crossing of a 90-degree grid. Unwrapping is anchored to the
    last accepted evaluation, valid because every search step stays < 180 deg.
    """

    def __init__(self, fn, jd0: float, rate: float, grid: float = 90.0):
        self.fn = fn
        self.rate = rate
        self.grid = grid
        raw = fn(jd0) % 360.0
        self._ref_u = raw
        # Next grid multiple strictly above the start angle.
        import math
        self._next_target = (math.floor(raw / grid) + 1) * grid

    def _u(self, jd: float) -> float:
        raw = self.fn(jd) % 360.0
        u = raw + 360.0 * round((self._ref_u - raw) / 360.0)
        self._ref_u = u
        return u

    def next_crossing(self, jd: float):
        """Return (jd_cross, target_deg_mod_360) for the next grid crossing
        at or after `jd`, then advance the internal target. `jd` must be at
        or before that crossing."""
        target = self._next_target
        a = jd
        fa = self._u(a) - target            # <= 0
        # Bracket by undershooting on the estimated rate.
        step = max((-fa) / self.rate * 0.95, 1e-3)
        b = a + step
        fb = self._u(b) - target
        guard = 0
        while fb < 0.0:
            a, fa = b, fb
            b = b + max((-fb) / self.rate, 1e-3) + 1e-3
            fb = self._u(b) - target
            guard += 1
            if guard > 200:
                raise RuntimeError(f"failed to bracket target {target} near {jd}")
        # Secant with bisection fallback.
        for _ in range(80):
            denom = (fb - fa)
            c = b - fb * (b - a) / denom if denom != 0 else (a + b) / 2
            if not (a < c < b):
                c = (a + b) / 2
            fc = self._u(c) - target
            if abs(fc) < TOL_DEG:
                self._u(c)  # re-anchor the unwrapper on the accepted root
                self._next_target = target + self.grid
                return c, int(target) % 360
            if fc < 0.0:
                a, fa = c, fc
            else:
                b, fb = c, fc
            if (b - a) < 1e-9:
                break
        result = (a + b) / 2
        self._u(result)
        self._next_target = target + self.grid
        return result, int(target) % 360
