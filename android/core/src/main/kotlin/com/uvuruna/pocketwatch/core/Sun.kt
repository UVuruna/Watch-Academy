package com.uvuruna.pocketwatch.core

import java.time.Duration
import java.time.LocalDate
import java.time.ZoneId
import java.time.ZonedDateTime

/**
 * Sun events and daylight-regime classification — the Kotlin twin of the
 * desktop's `core/sun.py`.
 *
 * The five events are computed INDIVIDUALLY, exactly as the desktop does:
 * an all-or-nothing call fails at high latitudes even when four of the five
 * events exist, and the failure cannot tell polar day from polar night.
 * Solar noon never fails (meridian transit is always defined), so the star
 * rotation stays computable even in polar night.
 */
object Sun {

    enum class DaylightRegime {
        /** sunrise/sunset and dawn/dusk all exist */
        NORMAL,

        /** sunrise/sunset exist, sky never fully dark */
        WHITE_NIGHTS,

        /** sun never rises, but twilight occurs */
        TWILIGHT_ONLY,

        /** sun never sets */
        POLAR_DAY,

        /** sun never comes near the horizon */
        POLAR_NIGHT,
    }

    /** An observer: a place on the globe. No elevation — the desktop has none. */
    data class Observer(val latitude: Double, val longitude: Double)

    /**
     * The five sun events of one local calendar day, in local time. Any of
     * dawn/sunrise/sunset/dusk is null when the event does not occur on that
     * day at that latitude — documented behavior, never an error.
     */
    data class SunDay(
        val dawn: ZonedDateTime?,
        val sunrise: ZonedDateTime?,
        val noon: ZonedDateTime,
        val sunset: ZonedDateTime?,
        val dusk: ZonedDateTime?,
        val regime: DaylightRegime,
    )

    fun computeSunDay(observer: Observer, localDate: LocalDate, zone: ZoneId): SunDay {
        val dawn = eventOrNull {
            transitOnLocalDate(
                observer, localDate, zone,
                90.0 + Constants.CIVIL_DEPRESSION, SolarMath.Direction.RISING,
            )
        }
        val sunrise = eventOrNull {
            transitOnLocalDate(
                observer, localDate, zone,
                90.0 + Constants.SUN_APPARENT_RADIUS, SolarMath.Direction.RISING,
            )
        }
        var noon = SolarMath.noonUtc(observer.longitude, localDate)
            .withZoneSameInstant(zone)
        if (noon.toLocalDate() != localDate) {
            // astral's noon() lacks the local-date re-search the other events
            // have: in UTC+13/+14 zones the transit of the requested UTC day
            // lands on the NEXT local day — mirror the desktop's adjustment by
            // asking for the neighboring UTC day.
            val shiftDays = if (noon.toLocalDate() > localDate) 1L else -1L
            noon = SolarMath.noonUtc(observer.longitude, localDate.minusDays(shiftDays))
                .withZoneSameInstant(zone)
        }
        val sunset = eventOrNull {
            transitOnLocalDate(
                observer, localDate, zone,
                90.0 + Constants.SUN_APPARENT_RADIUS, SolarMath.Direction.SETTING,
            )
        }
        val dusk = eventOrNull {
            transitOnLocalDate(
                observer, localDate, zone,
                90.0 + Constants.CIVIL_DEPRESSION, SolarMath.Direction.SETTING,
            )
        }

        return SunDay(
            dawn = dawn,
            sunrise = sunrise,
            noon = noon,
            sunset = sunset,
            dusk = dusk,
            regime = classify(observer, noon, dawn, sunrise, sunset, dusk),
        )
    }

    /**
     * astral's per-event local-date re-search: compute the transit for the
     * requested day, and if it lands on the neighbouring LOCAL date, retry
     * from that neighbour's UTC day. Still wrong -> the event does not occur.
     */
    private fun transitOnLocalDate(
        observer: Observer,
        date: LocalDate,
        zone: ZoneId,
        zenith: Double,
        direction: SolarMath.Direction,
    ): ZonedDateTime {
        var tot = SolarMath.timeOfTransit(
            observer.latitude, observer.longitude, date, zenith, direction,
        ).withZoneSameInstant(zone)

        if (tot.toLocalDate() != date) {
            val delta = if (tot.toLocalDate() < date) 1L else -1L
            tot = SolarMath.timeOfTransit(
                observer.latitude, observer.longitude, date.plusDays(delta),
                zenith, direction,
            ).withZoneSameInstant(zone)
            if (tot.toLocalDate() != date) {
                throw SolarMath.EventDoesNotOccur(
                    "Unable to find the event on the date specified"
                )
            }
        }
        return tot
    }

    private inline fun eventOrNull(block: () -> ZonedDateTime): ZonedDateTime? =
        try {
            block()
        } catch (_: SolarMath.EventDoesNotOccur) {
            null
        }

    private fun classify(
        observer: Observer,
        noon: ZonedDateTime,
        dawn: ZonedDateTime?,
        sunrise: ZonedDateTime?,
        sunset: ZonedDateTime?,
        dusk: ZonedDateTime?,
    ): DaylightRegime {
        if (sunrise != null || sunset != null) {
            // The sun crosses the horizon; the sky may or may not get fully dark.
            return if (dawn != null || dusk != null) {
                DaylightRegime.NORMAL
            } else {
                DaylightRegime.WHITE_NIGHTS
            }
        }
        if (dawn != null || dusk != null) return DaylightRegime.TWILIGHT_ONLY

        // Only noon exists — decide by how high the sun gets at its best.
        // GEOMETRIC elevation: the -0.833 threshold already contains
        // refraction, and apparent elevation would count it twice.
        val noonElevation = SolarMath.elevation(
            observer.latitude, observer.longitude, noon, withRefraction = false,
        )
        if (noonElevation > Constants.HORIZON_ELEVATION_DEG) return DaylightRegime.POLAR_DAY
        if (noonElevation > Constants.CIVIL_TWILIGHT_ELEVATION_DEG) {
            // All-day twilight: the sun stays between the horizon and civil
            // depression, so no event boundary exists on this day.
            return DaylightRegime.TWILIGHT_ONLY
        }
        return DaylightRegime.POLAR_NIGHT
    }

    /**
     * Daylight duration of the day in whole minutes. Polar day is 1440,
     * polar night / twilight-only 0; inverted midnight-sun days take the
     * complement of the dark gap; one-sided transitional days measure
     * against the local midnights.
     */
    fun dayLengthMinutes(sun: SunDay): Int {
        if (sun.regime == DaylightRegime.POLAR_DAY) return 24 * 60
        if (sun.regime == DaylightRegime.POLAR_NIGHT ||
            sun.regime == DaylightRegime.TWILIGHT_ONLY
        ) {
            return 0
        }
        val fullDay = Duration.ofDays(1)
        val rise = sun.sunrise
        val set = sun.sunset
        val lit: Duration = when {
            rise != null && set != null ->
                if (set.isBefore(rise)) {
                    fullDay.minus(Duration.between(set, rise))
                } else {
                    Duration.between(rise, set)
                }
            else -> {
                val dayStart = sun.noon.toLocalDate().atStartOfDay(sun.noon.zone)
                when {
                    rise != null -> Duration.between(rise, dayStart.plus(fullDay))
                    set != null -> Duration.between(dayStart, set)
                    sun.regime == DaylightRegime.WHITE_NIGHTS -> fullDay
                    else -> Duration.ZERO
                }
            }
        }
        return Math.round(lit.seconds / 60.0).toInt()
    }

    /** The readable form of [dayLengthMinutes] — "H:MM". */
    fun dayLengthHm(sun: SunDay): String {
        val minutes = dayLengthMinutes(sun)
        return "${minutes / 60}:${(minutes % 60).toString().padStart(2, '0')}"
    }
}
