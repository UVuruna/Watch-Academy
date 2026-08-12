package com.uvuruna.pocketwatch.core

import java.time.ZoneOffset
import java.time.ZonedDateTime
import kotlin.math.PI
import kotlin.math.abs
import kotlin.math.cos
import kotlin.math.sin

/**
 * Moon illumination and phase, ported from the desktop's `core/moon.py`.
 *
 * The ILLUMINATION is analytic: the compact Meeus 48.4 elongation series
 * reads the true lit fraction at any instant. The cycle-fraction cosine was
 * exact at the principals but up to ~3 p.p. off mid-phase, so it survives
 * only as [nominalIllumination] — the hypothetical reading of a dial angle,
 * never the live moon.
 */
object Moon {

    /**
     * Sorted principal-phase events (UTC instant, cycle fraction) spanning
     * comfortably around the period of interest. New=0.0, First Quarter=0.25,
     * Full=0.5, Third Quarter=0.75.
     */
    data class MoonWindow(val events: List<Pair<ZonedDateTime, Double>>)

    /**
     * Cycle fraction at [now]: 0.0 new, 0.25 first quarter, 0.5 full, 0.75
     * third quarter. Waxing below 0.5, waning above. Linear interpolation
     * between bracketing principal phases — exact at the anchors.
     */
    fun phaseFraction(now: ZonedDateTime, window: MoonWindow): Double {
        val events = window.events
        require(events.isNotEmpty()) { "empty moon window" }
        if (now.isBefore(events.first().first) || now.isAfter(events.last().first)) {
            throw IllegalArgumentException(
                "$now is outside the moon window " +
                    "(${events.first().first} .. ${events.last().first})"
            )
        }
        for (i in 0 until events.size - 1) {
            val (t0, f0) = events[i]
            val (t1, _) = events[i + 1]
            if (!now.isBefore(t0) && !now.isAfter(t1)) {
                val elapsed = (now.toInstant().toEpochMilli() - t0.toInstant().toEpochMilli())
                    .toDouble() /
                    (t1.toInstant().toEpochMilli() - t0.toInstant().toEpochMilli()).toDouble()
                return floorMod1(f0 + elapsed * Constants.MOON_CYCLE_QUARTER)
            }
        }
        throw IllegalArgumentException("no bracketing phase events around $now")
    }

    /**
     * TRUE lit fraction of the moon disc (0.0 new .. 1.0 full) at an
     * instant — the compact analytic elongation series (Meeus 48.4): sun
     * mean anomaly, moon mean anomaly and mean elongation with the principal
     * periodic terms; k = (1 - cos(D + corrections)) / 2, which is the
     * phase-angle form i = 180deg - D - corrections, k = (1 + cos i)/2.
     */
    fun illumination(whenAt: ZonedDateTime): Double {
        val utc = whenAt.withZoneSameInstant(ZoneOffset.UTC)
        val year = utc.year
        val jdTt = DeepTime.julianDay(
            year, utc.monthValue, utc.dayOfMonth,
            (utc.hour * 3600 + utc.minute * 60 + utc.second) / 86400.0,
        ) + DeepTime.deltaTSeconds(year.toDouble()) / 86400.0
        val t = (jdTt - 2451545.0) / 36525.0

        // Mean elongation of the Moon, sun mean anomaly, moon mean anomaly
        // (Meeus ch. 47 polynomials — degrees).
        val dDeg = 297.8501921 + 445267.1114034 * t - 0.0018819 * t * t +
            t * t * t / 545868.0 - t * t * t * t / 113065000.0
        val mDeg = 357.5291092 + 35999.0502909 * t - 0.0001536 * t * t +
            t * t * t / 24490000.0
        val mpDeg = 134.9633964 + 477198.8675055 * t + 0.0087414 * t * t +
            t * t * t / 69699.0 - t * t * t * t / 14712000.0

        val d = Math.toRadians(Angles.floorMod360(dDeg))
        val m = Math.toRadians(Angles.floorMod360(mDeg))
        val mp = Math.toRadians(Angles.floorMod360(mpDeg))

        val corrected = d + Math.toRadians(
            6.289 * sin(mp) -
                2.100 * sin(m) +
                1.274 * sin(2 * d - mp) +
                0.658 * sin(2 * d) +
                0.214 * sin(2 * mp) -
                0.110 * sin(d)
        )
        return (1.0 - cos(corrected)) / 2.0
    }

    /**
     * The NOMINAL lit fraction of a cycle position — the ring's own cosine
     * mapping. Used only where a dial ANGLE is read hypothetically, never
     * for the live moon; that is [illumination].
     */
    fun nominalIllumination(fraction: Double): Double =
        (1.0 - cos(2.0 * PI * fraction)) / 2.0

    /**
     * English phase name for a cycle fraction. A PRINCIPAL name applies only
     * within +/- half a day of its instant — the common convention: the day
     * after the Third Quarter the moon is already a Waning Crescent.
     */
    fun phaseName(fractionIn: Double): String {
        val fraction = floorMod1(fractionIn)
        val principals = listOf(
            0.0 to "New Moon",
            0.25 to "First Quarter",
            0.5 to "Full Moon",
            0.75 to "Third Quarter",
            1.0 to "New Moon",
        )
        for ((anchor, name) in principals) {
            if (abs(fraction - anchor) <= Constants.MOON_PRINCIPAL_WINDOW) return name
        }
        return when {
            fraction < 0.25 -> "Waxing Crescent"
            fraction < 0.5 -> "Waxing Gibbous"
            fraction < 0.75 -> "Waning Gibbous"
            else -> "Waning Crescent"
        }
    }

    private fun floorMod1(x: Double): Double {
        val r = x % 1.0
        return if (r < 0.0) r + 1.0 else r
    }
}
