package com.uvuruna.pocketwatch.core

/**
 * The dial's identity constants, ported one-for-one from the desktop's
 * `config/constants.py`. These are the SAME numbers, never re-derived —
 * a divergence here is a parity break, and the golden vectors are the
 * tooth that catches it.
 */
object Constants {
    // --- Dial identity -------------------------------------------------
    // A 24-hour face, CLOCKWISE, 12:00 noon at the TOP and 00:00 midnight
    // at the BOTTOM (18:00 right, 06:00 left).
    const val HOURS_PER_REVOLUTION = 24
    const val DIAL_TOP_HOUR = 12

    const val SECONDS_PER_DAY = 86_400
    const val SECONDS_PER_HOUR = 3_600

    /** Raw time-of-day angle has 00:00 at the top; the dial puts noon there. */
    const val DIAL_OFFSET_DEG = 180.0

    /** 12:00 as seconds since local midnight. */
    const val SOLAR_NOON_SECS = 43_200

    /** 240 s of day per dial degree. */
    const val SECONDS_PER_DEGREE = SECONDS_PER_DAY / 360.0

    // --- Sun ------------------------------------------------------------
    /** Degrees below the horizon for dawn/dusk (civil). */
    const val CIVIL_DEPRESSION = 6.0

    /** Solar disc touches the horizon (refraction included). */
    const val HORIZON_ELEVATION_DEG = -0.833

    const val CIVIL_TWILIGHT_ELEVATION_DEG = -6.0

    /** Sun's apparent radius, 32 arc minutes across (astral's own figure). */
    const val SUN_APPARENT_RADIUS = 32.0 / (60.0 * 2.0)

    // --- Year wheel -------------------------------------------------------
    /**
     * UNWRAPPED dial angles of the six season anchors bracketing one
     * calendar year in `seasons_utc.json`: previous December solstice,
     * spring equinox, summer solstice (top of dial after mod 360), autumn
     * equinox, December solstice, next spring equinox. Clockwise,
     * 0 deg = summer solstice = top.
     */
    val YEAR_ANCHOR_ANGLES = doubleArrayOf(180.0, 270.0, 360.0, 450.0, 540.0, 630.0)

    const val ZODIAC_SPAN_DEG = 30.0

    // --- Moon --------------------------------------------------------------
    /** Mean lunar cycle length in days. */
    const val SYNODIC_MONTH_DAYS = 29.53

    /**
     * A principal phase name applies only within +/- half a day of its
     * instant (the common convention).
     */
    const val MOON_PRINCIPAL_WINDOW = 0.5 / SYNODIC_MONTH_DAYS

    /** Cycle fraction between consecutive principal phases. */
    const val MOON_CYCLE_QUARTER = 0.25
}
