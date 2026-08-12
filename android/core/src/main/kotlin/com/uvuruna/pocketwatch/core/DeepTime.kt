package com.uvuruna.pocketwatch.core

import java.time.ZoneOffset
import java.time.ZonedDateTime
import kotlin.math.floor

/**
 * Calendar mathematics shared by the sun and moon ports: the proleptic-
 * Gregorian Julian Day and the Espenak & Meeus 2006 delta-T model, ported
 * from the desktop's `core/deep_time.py`.
 */
object DeepTime {

    /**
     * Proleptic-Gregorian Julian Day (Meeus 7.1 with floor — valid for
     * negative years). [dayFraction] is the fraction of the UT day.
     */
    fun julianDay(year: Int, month: Int, day: Int, dayFraction: Double = 0.0): Double {
        var y = year
        var m = month
        if (m <= 2) {
            y -= 1
            m += 12
        }
        val a = floor(y / 100.0)
        val b = 2 - a + floor(a / 4.0)
        return floor(365.25 * (y + 4716)) +
            floor(30.6001 * (m + 1)) +
            day + b - 1524.5 + dayFraction
    }

    /** Julian Day (UT) of an instant. */
    fun julianDayOf(when_: ZonedDateTime): Double {
        val utc = when_.withZoneSameInstant(ZoneOffset.UTC)
        return julianDay(
            utc.year, utc.monthValue, utc.dayOfMonth,
            (utc.hour * 3600 + utc.minute * 60 + utc.second) / 86400.0,
        )
    }

    fun julianCentury(jd: Double): Double = (jd - 2451545.0) / 36525.0

    /**
     * TT - UT in seconds — the published Espenak & Meeus 2006 piecewise
     * polynomials, transcribed branch for branch from the desktop.
     */
    fun deltaTSeconds(year: Double): Double {
        val y = year
        if (y < -500 || y >= 2150) {
            val u = (y - 1820) / 100
            return -20 + 32 * u * u
        }
        if (y < 500) {
            val u = y / 100
            return 10583.6 - 1014.41 * u + 33.78311 * u.pow(2) - 5.952053 * u.pow(3) -
                0.1798452 * u.pow(4) + 0.022174192 * u.pow(5) + 0.0090316521 * u.pow(6)
        }
        if (y < 1600) {
            val u = (y - 1000) / 100
            return 1574.2 - 556.01 * u + 71.23472 * u.pow(2) + 0.319781 * u.pow(3) -
                0.8503463 * u.pow(4) - 0.005050998 * u.pow(5) + 0.0083572073 * u.pow(6)
        }
        if (y < 1700) {
            val t = y - 1600
            return 120 - 0.9808 * t - 0.01532 * t.pow(2) + t.pow(3) / 7129
        }
        if (y < 1800) {
            val t = y - 1700
            return 8.83 + 0.1603 * t - 0.0059285 * t.pow(2) + 0.00013336 * t.pow(3) -
                t.pow(4) / 1174000
        }
        if (y < 1860) {
            val t = y - 1800
            return 13.72 - 0.332447 * t + 0.0068612 * t.pow(2) + 0.0041116 * t.pow(3) -
                0.00037436 * t.pow(4) + 0.0000121272 * t.pow(5) -
                0.0000001699 * t.pow(6) + 0.000000000875 * t.pow(7)
        }
        if (y < 1900) {
            val t = y - 1860
            return 7.62 + 0.5737 * t - 0.251754 * t.pow(2) + 0.01680668 * t.pow(3) -
                0.0004473624 * t.pow(4) + t.pow(5) / 233174
        }
        if (y < 1920) {
            val t = y - 1900
            return -2.79 + 1.494119 * t - 0.0598939 * t.pow(2) + 0.0061966 * t.pow(3) -
                0.000197 * t.pow(4)
        }
        if (y < 1941) {
            val t = y - 1920
            return 21.20 + 0.84493 * t - 0.076100 * t.pow(2) + 0.0020936 * t.pow(3)
        }
        if (y < 1961) {
            val t = y - 1950
            return 29.07 + 0.407 * t - t.pow(2) / 233 + t.pow(3) / 2547
        }
        if (y < 1986) {
            val t = y - 1975
            return 45.45 + 1.067 * t - t.pow(2) / 260 - t.pow(3) / 718
        }
        if (y < 2005) {
            val t = y - 2000
            return 63.86 + 0.3345 * t - 0.060374 * t.pow(2) + 0.0017275 * t.pow(3) +
                0.000651814 * t.pow(4) + 0.00002373599 * t.pow(5)
        }
        if (y < 2050) {
            val t = y - 2000
            return 62.92 + 0.32217 * t + 0.005589 * t.pow(2)
        }
        // 2050-2150: the long parabola blended toward the modern fit.
        val u = (y - 1820) / 100
        return -20 + 32 * u * u - 0.5628 * (2150 - y)
    }

    private fun Double.pow(n: Int): Double {
        var result = 1.0
        repeat(n) { result *= this }
        return result
    }
}
