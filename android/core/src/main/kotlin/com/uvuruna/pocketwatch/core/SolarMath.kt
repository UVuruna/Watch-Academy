package com.uvuruna.pocketwatch.core

import java.time.LocalDate
import java.time.LocalDateTime
import java.time.ZoneOffset
import java.time.ZonedDateTime
import kotlin.math.abs
import kotlin.math.acos
import kotlin.math.asin
import kotlin.math.atan2
import kotlin.math.cos
import kotlin.math.sin
import kotlin.math.tan

/**
 * The NOAA solar equations, ported from the `astral` 3.2 implementation
 * the desktop uses (`astral/sun.py`). The desktop calls astral; the phone
 * cannot, so the arithmetic itself travels — term for term, including
 * astral's own two-pass transit iteration and its refraction model, so
 * both platforms answer the same second.
 *
 * Every angle in this file is degrees unless the name says radians.
 */
object SolarMath {

    /** Which way the sun crosses the requested zenith. */
    enum class Direction { RISING, SETTING }

    /** Thrown where astral raises ValueError: the event does not occur. */
    class EventDoesNotOccur(message: String) : Exception(message)

    private fun rad(d: Double) = Math.toRadians(d)
    private fun deg(r: Double) = Math.toDegrees(r)

    fun geomMeanLongSun(t: Double): Double {
        val l0 = 280.46646 + t * (36000.76983 + 0.0003032 * t)
        return Angles.floorMod360(l0)
    }

    fun geomMeanAnomalySun(t: Double): Double =
        357.52911 + t * (35999.05029 - 0.0001537 * t)

    fun eccentricLocationEarthOrbit(t: Double): Double =
        0.016708634 - t * (0.000042037 + 0.0000001267 * t)

    fun sunEqOfCenter(t: Double): Double {
        val mrad = rad(geomMeanAnomalySun(t))
        val sinm = sin(mrad)
        val sin2m = sin(mrad + mrad)
        val sin3m = sin(mrad + mrad + mrad)
        return sinm * (1.914602 - t * (0.004817 + 0.000014 * t)) +
            sin2m * (0.019993 - 0.000101 * t) +
            sin3m * 0.000289
    }

    fun sunTrueLong(t: Double): Double = geomMeanLongSun(t) + sunEqOfCenter(t)

    fun sunApparentLong(t: Double): Double {
        val omega = 125.04 - 1934.136 * t
        return sunTrueLong(t) - 0.00569 - 0.00478 * sin(rad(omega))
    }

    fun meanObliquityOfEcliptic(t: Double): Double {
        val seconds = 21.448 - t * (46.815 + t * (0.00059 - t * 0.001813))
        return 23.0 + (26.0 + (seconds / 60.0)) / 60.0
    }

    fun obliquityCorrection(t: Double): Double {
        val omega = 125.04 - 1934.136 * t
        return meanObliquityOfEcliptic(t) + 0.00256 * cos(rad(omega))
    }

    fun sunDeclination(t: Double): Double {
        val e = obliquityCorrection(t)
        val lambd = sunApparentLong(t)
        return deg(asin(sin(rad(e)) * sin(rad(lambd))))
    }

    private fun varY(t: Double): Double {
        val y = tan(rad(obliquityCorrection(t)) / 2.0)
        return y * y
    }

    /** The equation of time, in MINUTES. */
    fun eqOfTime(t: Double): Double {
        val l0 = geomMeanLongSun(t)
        val e = eccentricLocationEarthOrbit(t)
        val m = geomMeanAnomalySun(t)
        val y = varY(t)

        val sin2l0 = sin(2.0 * rad(l0))
        val sinm = sin(rad(m))
        val cos2l0 = cos(2.0 * rad(l0))
        val sin4l0 = sin(4.0 * rad(l0))
        val sin2m = sin(2.0 * rad(m))

        val eTime = y * sin2l0 -
            2.0 * e * sinm +
            4.0 * e * y * sinm * cos2l0 -
            0.5 * y * y * sin4l0 -
            1.25 * e * e * sin2m
        return deg(eTime) * 4.0
    }

    /**
     * Hour angle in radians. Throws [EventDoesNotOccur] where astral's
     * `acos` raises "math domain error" — the sun never reaches the zenith.
     */
    fun hourAngle(
        latitude: Double,
        declination: Double,
        zenith: Double,
        direction: Direction,
    ): Double {
        val h = (cos(rad(zenith)) - sin(rad(latitude)) * sin(rad(declination))) /
            (cos(rad(latitude)) * cos(rad(declination)))
        if (h < -1.0 || h > 1.0) {
            throw EventDoesNotOccur("math domain error")
        }
        val ha = acos(h)
        return if (direction == Direction.SETTING) -ha else ha
    }

    /** astral's refraction correction, in degrees, from the zenith angle. */
    fun refractionAtZenith(zenith: Double): Double {
        val elevation = 90 - zenith
        if (elevation >= 85.0) return 0.0

        val te = tan(rad(elevation))
        val correction = when {
            elevation > 5.0 ->
                58.1 / te - 0.07 / (te * te * te) + 0.000086 / (te * te * te * te * te)
            elevation > -0.575 -> {
                val step1 = -12.79 + elevation * 0.711
                val step2 = 103.4 + elevation * step1
                val step3 = -518.2 + elevation * step2
                1735.0 + elevation * step3
            }
            else -> -20.774 / te
        }
        return correction / 3600.0
    }

    /**
     * UTC instant at which the sun transits [zenith] on [date] — astral's
     * `time_of_transit`, two fixed-point passes and all. Observer elevation
     * is 0 here (the desktop's observers carry none).
     */
    fun timeOfTransit(
        latitudeIn: Double,
        longitude: Double,
        date: LocalDate,
        zenith: Double,
        direction: Direction,
        withRefraction: Boolean = true,
    ): ZonedDateTime {
        val latitude = latitudeIn.coerceIn(-89.8, 89.8)
        val refractionAdjustment =
            if (withRefraction) refractionAtZenith(zenith) else 0.0

        val jd = DeepTime.julianDay(date.year, date.monthValue, date.dayOfMonth)
        var adjustment = 0.0
        var timeUtcMinutes = 0.0

        repeat(2) {
            val jc = DeepTime.julianCentury(jd + adjustment)
            val declination = sunDeclination(jc)
            val ha = hourAngle(
                latitude, declination, zenith + refractionAdjustment, direction,
            )
            val delta = -longitude - deg(ha)
            var offset = delta * 4.0 - eqOfTime(jc)
            if (offset < -720.0) offset += 1440.0
            timeUtcMinutes = 720.0 + offset
            adjustment = timeUtcMinutes / 1440.0
        }

        return LocalDateTime.of(date, java.time.LocalTime.MIDNIGHT)
            .plusNanos(minutesToNanos(timeUtcMinutes))
            .atZone(ZoneOffset.UTC)
    }

    /**
     * astral's `minutes_to_timedelta` — it truncates to whole microseconds,
     * so the port truncates the same way rather than rounding.
     */
    private fun minutesToNanos(minutesIn: Double): Long {
        val d = (minutesIn / 1440).toInt()
        var minutes = minutesIn - d * 1440
        minutes *= 60
        val s = minutes.toInt()
        val sfrac = minutes - s
        val us = (sfrac * 1_000_000).toInt()
        return (d.toLong() * 86_400L + s.toLong()) * 1_000_000_000L + us.toLong() * 1_000L
    }

    /**
     * Solar noon (meridian transit) — never fails, which is why the star
     * rotation is computable even in polar night.
     */
    fun noonUtc(longitude: Double, date: LocalDate): ZonedDateTime {
        val jc = DeepTime.julianCentury(
            DeepTime.julianDay(date.year, date.monthValue, date.dayOfMonth)
        )
        val timeUtc = (720.0 - (4 * longitude) - eqOfTime(jc)) / 60.0

        // astral splits and carries by hand; the port mirrors it exactly so
        // the truncation to whole seconds lands identically.
        var hour = timeUtc.toInt()
        var minute = ((timeUtc - hour) * 60).toInt()
        var second = ((((timeUtc - hour) * 60) - minute) * 60).toInt()
        var day = date

        if (second > 59) { second -= 60; minute += 1 } else if (second < 0) { second += 60; minute -= 1 }
        if (minute > 59) { minute -= 60; hour += 1 } else if (minute < 0) { minute += 60; hour -= 1 }
        if (hour > 23) { hour -= 24; day = day.plusDays(1) } else if (hour < 0) { hour += 24; day = day.minusDays(1) }

        return LocalDateTime.of(day.year, day.monthValue, day.dayOfMonth, hour, minute, second)
            .atZone(ZoneOffset.UTC)
    }

    /**
     * Solar zenith angle at an instant — astral's `zenith_and_azimuth`,
     * zenith half only (nothing on this dial reads the azimuth yet).
     */
    fun zenith(
        latitudeIn: Double,
        longitude: Double,
        at: ZonedDateTime,
        withRefraction: Boolean = true,
    ): Double {
        val latitude = latitudeIn.coerceIn(-89.8, 89.8)
        val zone = -at.offset.totalSeconds / 3600.0
        val utc = at.withZoneSameInstant(ZoneOffset.UTC)

        val t = DeepTime.julianCentury(
            DeepTime.julianDay(
                utc.year, utc.monthValue, utc.dayOfMonth,
                (utc.hour * 3600 + utc.minute * 60 + utc.second) / 86400.0,
            )
        )
        val declination = sunDeclination(t)
        val eqtime = eqOfTime(t)

        val solarTimeFix = eqtime + (4.0 * longitude) + (60 * zone)
        var trueSolarTime = at.hour * 60.0 + at.minute + at.second / 60.0 + solarTimeFix
        while (trueSolarTime > 1440) trueSolarTime -= 1440

        var hourangle = trueSolarTime / 4.0 - 180.0
        if (hourangle < -180) hourangle += 360.0

        val csz = (
            cos(rad(latitude)) * cos(rad(declination)) * cos(rad(hourangle)) +
                sin(rad(latitude)) * sin(rad(declination))
            ).coerceIn(-1.0, 1.0)

        var z = deg(acos(csz))
        if (withRefraction) z -= refractionAtZenith(z)
        return z
    }

    /** Sun's elevation above the horizon, in degrees. */
    fun elevation(
        latitude: Double,
        longitude: Double,
        at: ZonedDateTime,
        withRefraction: Boolean = true,
    ): Double = 90.0 - zenith(latitude, longitude, at, withRefraction)

    /** Right ascension — kept for parity of the ported surface. */
    fun sunRtAscension(t: Double): Double {
        val oc = obliquityCorrection(t)
        val al = sunApparentLong(t)
        return deg(atan2(cos(rad(oc)) * sin(rad(al)), cos(rad(al))))
    }

    internal fun absDeg(x: Double) = abs(x)
}
