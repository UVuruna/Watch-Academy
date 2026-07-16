"""Phase III — the LONG ENVELOPE of the light/dark half-year amplitude.

Reads Laskar's La2004 orbital solution (eccentricity + longitude of
perihelion) and derives the northern LIGHT-minus-DARK half-year duration
over the full solution span (-51 Myr .. +21 Myr), then VALIDATES the signed
curve against our DE441-measured `season_halves.json` over the overlap
(Phase I's measured window). Beyond DE441 the day-exact ephemerides are
unreliable, but the ENVELOPE's drivers (eccentricity, climatic precession)
are solved for tens of millions of years — so era LENGTHS and amplitudes
stay robust even where calendar DATES do not.

THE PHYSICS (Kepler's 2nd law, first order in e)
------------------------------------------------
Between the vernal equinox (Sun ecliptic longitude lambda = 0) and the
autumnal equinox (lambda = 180 deg) the Earth traverses the northern LIGHT
half; the DARK half is the return. Expanding the mean anomaly in the true
anomaly nu = lambda - varpi_sun and integrating each half:

    light = T/2 - (2T/pi) * e * sin(varpi_sun)
    dark  = T/2 + (2T/pi) * e * sin(varpi_sun)
    light - dark = -(4T/pi) * e * sin(varpi_sun)

where varpi_sun is the Sun's longitude at perihelion. La2004 stores the
HELIOCENTRIC longitude of perihelion varpi (column 4), and
varpi_sun = varpi + 180 deg, so sin(varpi_sun) = -sin(varpi) and

    light - dark = (4T/pi) * e * sin(varpi)          [signed, days]
    ENVELOPE     = (4T/pi) * e                        [|sin|=1, days]

The two e^2 corrections to the half-year lengths cancel in the DIFFERENCE
(each half picks up the same +/-(3/4)e^2 sin 2nu boundary term), so the
first-order form is exact to O(e^3) ~ 5e-6 — negligible at day level.

TIME ORIGIN: La2004 t is in kiloyears from J2000, so the astronomical
year (0 = 1 BCE) is  year = 2000 + 1000 * t_kyr.

SOURCE (cite in the doc): J. Laskar et al., 2004, A&A 428, 261, "A long-term
numerical solution for the insolation quantities of the Earth". Files
INSOLN.LA2004.BTL.ASC (past) / INSOLP.LA2004.BTL.ASC (future), IMCCE
(https://ssp.imcce.fr/insola/earth/online/earth/La2004/), columns
t[kyr]  e  obliquity[rad]  varpi[rad], step 1 kyr.

    .venv/Scripts/python.exe long_envelope.py all
"""

import os
import sys
import json
import math

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LASKAR = os.path.join(HERE, "laskar")
PAST = os.path.join(LASKAR, "INSOLN.LA2004.BTL.ASC")    # t: 0 .. -51000 kyr
FUTURE = os.path.join(LASKAR, "INSOLP.LA2004.BTL.ASC")  # t: 0 .. +21000 kyr
SEASONS = os.path.join(HERE, "season_halves.json")

OUT_JSON = os.path.join(HERE, "long_envelope.json")
OUT_PNG = os.path.join(HERE, "long_envelope.png")

T_TROPICAL = 365.2422            # mean tropical year, days
COEF = 4.0 * T_TROPICAL / math.pi   # days per unit of (e * sin varpi)

NEAR_KYR = 200                   # +/- window for the owner's chart (kyr)


# --------------------------------------------------------------------------
# load
# --------------------------------------------------------------------------

def _load_btl(path):
    """Parse a La2004 BTL ASCII file -> (t_kyr, e, obliquity, varpi) arrays.
    Fortran 'D' exponents are normalised to 'E'."""
    ts, es, obls, vps = [], [], [], []
    with open(path) as f:
        for line in f:
            parts = line.split()
            if len(parts) < 4:
                continue
            ts.append(float(parts[0].replace("D", "E")))
            es.append(float(parts[1].replace("D", "E")))
            obls.append(float(parts[2].replace("D", "E")))
            vps.append(float(parts[3].replace("D", "E")))
    return (np.array(ts), np.array(es), np.array(obls), np.array(vps))


def load_solution():
    """Full La2004 solution, t ascending from -51000 to +21000 kyr."""
    tn, en, on, vn = _load_btl(PAST)      # 0 .. -51000 (descending)
    tp, ep, op, vp = _load_btl(FUTURE)    # 0 .. +21000 (ascending)
    # reverse past to ascending, drop its t=0 duplicate (future keeps t=0)
    order = np.argsort(tn)
    tn, en, on, vn = tn[order], en[order], on[order], vn[order]
    keep = tn < -1e-9
    t = np.concatenate([tn[keep], tp])
    e = np.concatenate([en[keep], ep])
    obl = np.concatenate([on[keep], op])
    vp_ = np.concatenate([vn[keep], vp])
    return t, e, obl, vp_


def derive(t, e, varpi):
    """Signed light-minus-dark and the envelope, both in days."""
    signed = COEF * e * np.sin(varpi)
    envelope = COEF * e
    return signed, envelope


# --------------------------------------------------------------------------
# validate against the measured DE441 series
# --------------------------------------------------------------------------

def load_measured():
    with open(SEASONS) as f:
        d = json.load(f)
    years = np.array(sorted(int(k) for k in d))
    ld = np.array([d[str(y)][0] - d[str(y)][1] for y in years])  # light - dark
    return years, ld


def validate(verbose=True):
    t, e, obl, varpi = load_solution()
    signed, envelope = derive(t, e, varpi)
    years_m, ld_m = load_measured()

    # Laskar signed curve interpolated onto the measured astronomical years
    t_of_year = (years_m - 2000.0) / 1000.0
    ld_laskar = np.interp(t_of_year, t, signed)

    resid_days = ld_laskar - ld_m
    resid_hr = resid_days * 24.0
    out = {
        "overlap_years": [int(years_m.min()), int(years_m.max())],
        "n_years": int(years_m.size),
        "max_abs_dev_hours": float(np.max(np.abs(resid_hr))),
        "mean_abs_dev_hours": float(np.mean(np.abs(resid_hr))),
        "rms_dev_hours": float(np.sqrt(np.mean(resid_hr ** 2))),
        "mean_signed_bias_hours": float(np.mean(resid_hr)),
        "pearson_r": float(np.corrcoef(ld_laskar, ld_m)[0, 1]),
    }
    # spot values at notable years
    spots = {}
    for y in (2026, 1000, 0, -4078):
        ty = (y - 2000.0) / 1000.0
        lk = float(np.interp(ty, t, signed))
        idx = int(np.where(years_m == y)[0][0]) if y in years_m else None
        me = float(ld_m[idx]) if idx is not None else None
        spots[str(y)] = {"laskar_days": round(lk, 4),
                         "measured_days": (round(me, 4) if me is not None else None)}
    out["spot_checks"] = spots

    # e today (interp at t=0) and the coming eccentricity minimum
    e_today = float(np.interp(0.0, t, e))
    out["e_today"] = round(e_today, 6)

    if verbose:
        print("=== Phase III validation vs DE441 season_halves.json ===")
        print(f"overlap: {out['overlap_years']}  ({out['n_years']} yrs)")
        print(f"max  |dev| : {out['max_abs_dev_hours']:.3f} h")
        print(f"mean |dev| : {out['mean_abs_dev_hours']:.3f} h")
        print(f"rms   dev  : {out['rms_dev_hours']:.3f} h")
        print(f"mean bias  : {out['mean_signed_bias_hours']:+.3f} h "
              f"(Laskar - measured)")
        print(f"pearson r  : {out['pearson_r']:.6f}")
        print(f"e(today)   : {out['e_today']:.6f}")
        print("spot light-dark [days]  laskar / measured:")
        for y, s in spots.items():
            print(f"   {y:>6}:  {s['laskar_days']:+.4f} / "
                  f"{s['measured_days']}")
    return out


# --------------------------------------------------------------------------
# describe the near-future extrema (for the doc + the chart annotations)
# --------------------------------------------------------------------------

def find_extrema():
    t, e, obl, varpi = load_solution()
    signed, envelope = derive(t, e, varpi)

    def feature(lo, hi, kind):
        m = (t >= lo) & (t <= hi)
        tt, ee, en = t[m], e[m], envelope[m]
        i = int(np.argmin(ee) if kind == "min" else np.argmax(ee))
        return {"t_kyr": float(tt[i]),
                "year": int(round(2000 + 1000 * tt[i])),
                "e": float(ee[i]), "envelope_days": float(en[i])}

    e_now = float(np.interp(0.0, t, e))
    env_now = float(np.interp(0.0, t, envelope))
    sgn_now = float(np.interp(0.0, t, signed))

    # global envelope maximum over the whole solution (deep-time context)
    ig = int(np.argmax(envelope))
    glob = {"t_kyr": float(t[ig]), "year": int(round(2000 + 1000 * t[ig])),
            "e": float(e[ig]), "envelope_days": float(envelope[ig])}

    return {
        "now": {"year": 2000, "e": e_now, "envelope_days": env_now,
                "signed_days": sgn_now},
        # the deep amplitude minimum ~26 kyr out (the owner's suspected trough)
        "coming_ecc_min": feature(5, 45, "min"),
        # the first amplitude recovery peak (back to ~today's level)
        "next_local_max": feature(45, 110, "max"),
        # the far larger maximum inside the +/-200 kyr window
        "major_max_200kyr": feature(110, 200, "max"),
        # for context: the biggest amplitude anywhere in the fetched span
        "global_env_max": glob,
        "e_range_full_span": [float(e.min()), float(e.max())],
    }


# --------------------------------------------------------------------------
# committable JSON (per-kiloyear, full span, columnar + rounded)
# --------------------------------------------------------------------------

def write_json():
    t, e, obl, varpi = load_solution()
    signed, envelope = derive(t, e, varpi)
    years = np.round(2000 + 1000 * t).astype(int)

    val = validate(verbose=False)
    ext = find_extrema()

    payload = {
        "meta": {
            "what": "Northern light-minus-dark half-year: signed duration "
                    "and the amplitude envelope, from Laskar La2004.",
            "source": "Laskar et al. 2004, A&A 428, 261. Files "
                      "INSOLN/INSOLP.LA2004.BTL.ASC (IMCCE, ssp.imcce.fr). "
                      "Columns t[kyr] e obliquity[rad] varpi[rad], step 1 kyr.",
            "formula": "signed = (4*T/pi)*e*sin(varpi); "
                       "envelope = (4*T/pi)*e; T = 365.2422 d; "
                       "varpi = heliocentric longitude of perihelion (col 4).",
            "time_origin": "t is kyr from J2000; year = 2000 + 1000*t.",
            "units": "days",
            "span_kyr": [float(t.min()), float(t.max())],
            "span_years": [int(years.min()), int(years.max())],
            "n_rows": int(t.size),
            "caveat": "Era LENGTHS and AMPLITUDES are robust across the whole "
                      "span; calendar DATES of individual events are NOT what "
                      "this data gives (that is Phase I's DE441 job, and only "
                      "within ~15 kyr of the present).",
            "validation_vs_de441": val,
            "extrema": ext,
        },
        # columnar to keep the file compact; index i aligns across arrays.
        # year is NOT stored (it is exactly 2000 + 1000*t_kyr — see meta).
        "t_kyr": [int(round(x)) for x in t],
        "e": [round(float(x), 6) for x in e],
        "signed_light_minus_dark_days": [round(float(x), 3) for x in signed],
        "envelope_days": [round(float(x), 3) for x in envelope],
    }
    with open(OUT_JSON, "w") as f:
        json.dump(payload, f, separators=(",", ":"))
    print(f"json: {OUT_JSON} ({os.path.getsize(OUT_JSON)/1e6:.2f} MB, "
          f"{t.size} rows)")


# --------------------------------------------------------------------------
# the owner's chart (dark, two panels)
# --------------------------------------------------------------------------

# dark-friendly palette: gold = the amplitude data, teal = the DE441 region,
# soft white = reference lines, silver = annotations.
BG = "#0e1014"
PANEL = "#14171d"
GOLD = "#E8B23A"
GOLD_SOFT = "#E8B23A"
TEAL = "#4FB0C6"
SILVER = "#C7CDD6"
INK = "#E6E9EF"
MUTED = "#8A9099"


def build_plot():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    t, e, obl, varpi = load_solution()
    signed, envelope = derive(t, e, varpi)
    ext = find_extrema()
    val = validate(verbose=False)
    ov_lo, ov_hi = val["overlap_years"]

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(13, 9.5), facecolor=BG,
        gridspec_kw={"height_ratios": [1.35, 1.0]})

    for ax in (ax1, ax2):
        ax.set_facecolor(PANEL)
        for s in ax.spines.values():
            s.set_color(MUTED)
            s.set_linewidth(0.6)
        ax.tick_params(colors=MUTED, labelsize=9)
        ax.grid(True, color=INK, alpha=0.08, lw=0.6)
        ax.axhline(0, color=MUTED, lw=0.8, alpha=0.6)

    # ---- Panel 1: the owner's window, +/- 200 kyr ------------------------
    yr = 2000 + 1000 * t
    m = (t >= -NEAR_KYR) & (t <= NEAR_KYR)
    yr1, sg1, en1 = yr[m], signed[m], envelope[m]

    # the breathing envelope: translucent gold band between -env and +env
    ax1.fill_between(yr1, -en1, en1, color=GOLD, alpha=0.14, lw=0,
                     label="amplitude envelope  $\\pm(4T/\\pi)e$")
    ax1.plot(yr1, en1, color=GOLD, lw=1.3, alpha=0.85)
    ax1.plot(yr1, -en1, color=GOLD, lw=1.3, alpha=0.85)
    # the signed light-dark oscillation filling the envelope
    ax1.plot(yr1, sg1, color=GOLD, lw=0.6, alpha=0.9,
             label="light $-$ dark  (signed, precession-driven)")

    # DE441 overlap window, shaded
    ax1.axvspan(ov_lo, ov_hi, color=TEAL, alpha=0.12, lw=0)
    ax1.text(ov_hi, ax1.get_ylim()[1], " DE441 measured\n (Phases I-II)",
             color=TEAL, fontsize=8.5, va="top", ha="left")

    # present
    ax1.axvline(2000, color=INK, lw=1.1, alpha=0.7)
    ax1.text(2000, ax1.get_ylim()[0], " now (2026 CE)\n light $+$%.1f d" %
             ext["now"]["signed_days"], color=INK, fontsize=8.5,
             va="bottom", ha="left")

    # coming eccentricity minimum
    emn = ext["coming_ecc_min"]
    ax1.annotate(
        "coming eccentricity minimum\n"
        f"~{emn['year']:+d}  (e={emn['e']:.4f})\n"
        f"amplitude shrinks to {emn['envelope_days']:.1f} d",
        xy=(emn["year"], emn["envelope_days"]),
        xytext=(emn["year"], emn["envelope_days"] + 4.5),
        color=SILVER, fontsize=8.5, ha="center",
        arrowprops=dict(arrowstyle="->", color=SILVER, lw=1.0))
    ax1.plot([emn["year"]], [emn["envelope_days"]], "o", color=SILVER, ms=5)

    # first recovery peak (amplitude climbs back to ~today's level)
    erp = ext["next_local_max"]
    ax1.annotate(
        f"recovery peak ~{erp['year']:+d}\n({erp['envelope_days']:.1f} d, "
        "~today)",
        xy=(erp["year"], erp["envelope_days"]),
        xytext=(erp["year"], erp["envelope_days"] + 3.0),
        color=SILVER, fontsize=8.0, ha="center",
        arrowprops=dict(arrowstyle="->", color=SILVER, lw=1.0))
    ax1.plot([erp["year"]], [erp["envelope_days"]], "o", color=SILVER, ms=4)

    # the far larger maximum inside the window
    emx = ext["major_max_200kyr"]
    ax1.annotate(
        f"next major maximum ~{emx['year']:+d}\n(e={emx['e']:.4f}, "
        f"{emx['envelope_days']:.1f} d)",
        xy=(emx["year"], emx["envelope_days"]),
        xytext=(emx["year"], emx["envelope_days"] + 2.6),
        color=SILVER, fontsize=8.0, ha="center",
        arrowprops=dict(arrowstyle="->", color=SILVER, lw=1.0))
    ax1.plot([emx["year"]], [emx["envelope_days"]], "o", color=SILVER, ms=4)

    ax1.set_xlim(2000 - 1000 * NEAR_KYR, 2000 + 1000 * NEAR_KYR)
    ax1.set_title("The long envelope of the light $-$ dark half-year  "
                  "(La2004, $\\pm$200,000 years)",
                  color=INK, fontsize=13, pad=10)
    ax1.set_ylabel("light $-$ dark  (days)", color=INK, fontsize=10)
    ax1.set_xlabel("astronomical year  (0 = 1 BCE)", color=MUTED, fontsize=9)
    leg = ax1.legend(loc="lower left", fontsize=8.5, framealpha=0.82,
                     facecolor=PANEL, edgecolor=MUTED)
    for txt in leg.get_texts():
        txt.set_color(INK)

    # ---- Panel 2: the full solution span --------------------------------
    # At 1-kyr sampling the envelope oscillates on the ~100-kyr eccentricity
    # cycle; drawn raw over 72 Myr it is a hairball. Trace instead the PEAK
    # amplitude in each 100-kyr bin (a running max) -> the deep eccentricity
    # beat (100 kyr, 405 kyr, and the 2.4-Myr grand cycle) reads cleanly.
    binw = 100.0  # kyr
    b = np.floor(t / binw).astype(np.int64)
    starts = np.concatenate([[0], np.where(np.diff(b) != 0)[0] + 1])
    peak_env = np.maximum.reduceat(envelope, starts)
    peak_myr = (b[starts] + 0.5) * binw / 1000.0

    tm = 1000 * t / 1e6  # Myr from present (J2000 origin)
    ax2.plot(tm, envelope, color=GOLD, lw=0.3, alpha=0.10)  # raw = upper bound
    ax2.fill_between(peak_myr, 0, peak_env, color=GOLD, alpha=0.16, lw=0)
    ax2.plot(peak_myr, peak_env, color=GOLD, lw=1.3, alpha=0.95,
             label="peak amplitude per 100-kyr window  $(4T/\\pi)e_{max}$")

    # present, and the grand maximum ~27 Myr ago
    ax2.axvline(0, color=INK, lw=1.0, alpha=0.7)
    ax2.text(0.4, peak_env.max() * 0.96, "present", color=INK, fontsize=8.5,
             va="top", ha="left")
    ig = int(np.argmax(peak_env))
    ax2.annotate("grand eccentricity maximum\n"
                 f"~{peak_myr[ig]:.1f} Myr  (e$\\approx$0.067, ~31 d)",
                 xy=(peak_myr[ig], peak_env[ig]),
                 xytext=(peak_myr[ig] + 6, peak_env[ig] - 1),
                 color=SILVER, fontsize=8.0, va="center", ha="left",
                 arrowprops=dict(arrowstyle="->", color=SILVER, lw=1.0))

    ax2.set_xlim(tm.min(), tm.max())
    ax2.set_ylim(0, peak_env.max() * 1.08)
    ax2.set_title("The whole La2004 span  ($-$51 to $+$21 Myr): the "
                  "eccentricity beat modulates the amplitude",
                  color=INK, fontsize=12, pad=8)
    ax2.set_ylabel("peak light $-$ dark amplitude (days)", color=INK,
                   fontsize=10)
    ax2.set_xlabel("million years from present (J2000)", color=MUTED,
                   fontsize=9)
    leg2 = ax2.legend(loc="upper right", fontsize=8.5, framealpha=0.82,
                      facecolor=PANEL, edgecolor=MUTED)
    for txt in leg2.get_texts():
        txt.set_color(INK)

    fig.tight_layout(pad=1.4)
    fig.savefig(OUT_PNG, dpi=130, facecolor=BG)
    print(f"plot: {OUT_PNG} ({os.path.getsize(OUT_PNG)/1e3:.0f} KB)")


# --------------------------------------------------------------------------
# entry
# --------------------------------------------------------------------------

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd in ("validate", "all"):
        validate(verbose=True)
        print()
        ext = find_extrema()
        print("=== extrema ===")
        print(json.dumps(ext, indent=2))
        print()
    if cmd in ("json", "all"):
        write_json()
    if cmd in ("plot", "all"):
        build_plot()


if __name__ == "__main__":
    main()
