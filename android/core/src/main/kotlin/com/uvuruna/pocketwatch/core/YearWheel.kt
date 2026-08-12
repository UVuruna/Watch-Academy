package com.uvuruna.pocketwatch.core

import java.time.LocalDate
import java.time.YearMonth
import java.time.ZonedDateTime

/**
 * Year-marker angle: piecewise-linear between REAL season instants —
 * ported from the desktop's `core/year_wheel.py`.
 *
 * Anchored so the summer solstice sits exactly at the dial top (0 deg) and
 * the winter solstice at the bottom (180 deg), with the equinoxes exactly
 * at 90/270 deg. Plain linear interpolation over the whole tropical year is
 * NOT equivalent — it puts the autumn equinox at ~92.3 deg, a visible error
 * the golden vectors reject. Each of the FOUR astronomical seasons spans
 * exactly 90 deg of the wheel regardless of its real duration; the six
 * anchors bracket one calendar year and therefore span 450 deg unwrapped.
 */
object YearWheel {

    /**
     * Six season instants bracketing one calendar year, paired with their
     * unwrapped dial angles ([Constants.YEAR_ANCHOR_ANGLES]).
     *
     * instants[0] is the December solstice BEFORE the year, instants[5] the
     * spring equinox AFTER it — any timestamp inside the calendar year falls
     * between two anchors without stitching neighbour years.
     */
    data class YearAnchors(
        val year: Int,
        val instants: List<ZonedDateTime>,
        val angles: DoubleArray = Constants.YEAR_ANCHOR_ANGLES,
    ) {
        init {
            require(instants.size == angles.size) {
                "expected ${angles.size} anchors, got ${instants.size}"
            }
        }

        override fun equals(other: Any?): Boolean =
            other is YearAnchors && year == other.year && instants == other.instants

        override fun hashCode(): Int = 31 * year + instants.hashCode()
    }

    /** Dial angle of the year marker (degrees, clockwise, 0 = top). */
    fun yearMarkerAngle(now: ZonedDateTime, anchors: YearAnchors): Double =
        Angles.floorMod360(unwrappedAngle(now, anchors))

    /**
     * The ALMANAC wheel's wedge index (0..11) of a calendar month, counted
     * CLOCKWISE from the top wedge = June: June 0, July 1, ... December 6,
     * January 7, ... May 11.
     */
    fun almanacMonthIndex(month: Int): Int = Math.floorMod(month - 6, 12)

    /**
     * Public inverse of [yearMarkerAngle]: the calendar instant whose
     * year-marker angle equals [dialAngle] — un-mirroring the southern wheel
     * first (the marker runs +180 deg south of the equator).
     */
    fun instantAtMarkerAngle(
        anchors: YearAnchors,
        dialAngleIn: Double,
        southern: Boolean = false,
    ): ZonedDateTime {
        val dialAngle =
            if (southern) Angles.floorMod360(dialAngleIn - 180.0) else dialAngleIn
        val unwrapped = if (dialAngle >= 180.0) dialAngle else dialAngle + 360.0
        return instantAt(anchors, unwrapped)
    }

    /**
     * Cusp instants of the sign starting at [startDialAngle] (0 = Cancer's
     * first point, the summer solstice).
     */
    fun zodiacSpan(
        anchors: YearAnchors,
        startDialAngle: Double,
    ): Pair<ZonedDateTime, ZonedDateTime> {
        val unwrapped =
            if (startDialAngle >= 180.0) startDialAngle else startDialAngle + 360.0
        return instantAt(anchors, unwrapped) to
            instantAt(anchors, unwrapped + Constants.ZODIAC_SPAN_DEG)
    }

    /**
     * Meteorological season bounds around the anchor at the UNWRAPPED
     * [centerAngle]: each bound lies HALFWAY between neighbouring anchor
     * instants, so every season CENTERS on its solstice/equinox.
     */
    fun meteorologicalSpan(
        anchors: YearAnchors,
        centerAngle: Double,
    ): Pair<ZonedDateTime, ZonedDateTime> {
        val index = anchors.angles.indexOfFirst { it == centerAngle }
        require(index > 0 && index < anchors.instants.size - 1) {
            "no interior anchor at $centerAngle"
        }
        val before = anchors.instants[index - 1]
        val center = anchors.instants[index]
        val after = anchors.instants[index + 1]
        return midpoint(before, center) to midpoint(center, after)
    }

    /**
     * Interpolated UNWRAPPED angle (180..630 over the anchor span).
     *
     * Throws when [now] is outside the anchor span — that means the anchors
     * were built for the wrong year and must be visible, not interpolated
     * blindly.
     */
    fun unwrappedAngle(now: ZonedDateTime, anchors: YearAnchors): Double {
        val instants = anchors.instants
        if (now.isBefore(instants.first()) || now.isAfter(instants.last())) {
            throw IllegalArgumentException(
                "$now is outside the anchor span of year ${anchors.year} " +
                    "(${instants.first()} .. ${instants.last()})"
            )
        }
        val hi = bisectRight(instants, now)
        if (hi == instants.size) return anchors.angles.last() // now == last anchor exactly
        val lo = hi - 1
        val t0 = instants[lo]
        val t1 = instants[hi]
        val a0 = anchors.angles[lo]
        val a1 = anchors.angles[hi]
        val fraction = (now.toInstant().toEpochMilli() - t0.toInstant().toEpochMilli())
            .toDouble() /
            (t1.toInstant().toEpochMilli() - t0.toInstant().toEpochMilli()).toDouble()
        return a0 + fraction * (a1 - a0)
    }

    /**
     * Inverse interpolation: the instant at an unwrapped wheel angle. The
     * last segment extrapolates for the (edge-only) cusp just past the final
     * anchor.
     */
    fun instantAt(anchors: YearAnchors, unwrappedAngle: Double): ZonedDateTime {
        var hi = anchors.angles.count { it <= unwrappedAngle }
        hi = hi.coerceIn(1, anchors.angles.size - 1)
        val lo = hi - 1
        val a0 = anchors.angles[lo]
        val a1 = anchors.angles[hi]
        val t0 = anchors.instants[lo]
        val t1 = anchors.instants[hi]
        val fraction = (unwrappedAngle - a0) / (a1 - a0)
        val spanMillis = t1.toInstant().toEpochMilli() - t0.toInstant().toEpochMilli()
        return t0.plusNanos(Math.round(fraction * spanMillis * 1_000_000.0))
    }

    /**
     * Dial angle of the Earth marker on the CALENDAR pointer's Almanac
     * wheel — its OWN real-calendar mapping: every month spans exactly
     * 30 deg with the 1st of the month on its wedge-START line, and day D
     * sits (D-1)/days_in_month of the way into the wedge.
     */
    fun almanacMarkerAngle(whenAt: LocalDate): Double {
        val wedgeDeg = 30.0
        val daysInMonth = YearMonth.of(whenAt.year, whenAt.month).lengthOfMonth()
        val index = almanacMonthIndex(whenAt.monthValue)
        val wedgeStart = index * wedgeDeg - wedgeDeg / 2
        val into = (whenAt.dayOfMonth - 1) / daysInMonth.toDouble() * wedgeDeg
        return Angles.floorMod360(wedgeStart + into)
    }

    /** Python's `bisect.bisect_right` over a sorted instant list. */
    private fun bisectRight(items: List<ZonedDateTime>, value: ZonedDateTime): Int {
        var lo = 0
        var hi = items.size
        while (lo < hi) {
            val mid = (lo + hi) / 2
            if (value.isBefore(items[mid])) hi = mid else lo = mid + 1
        }
        return lo
    }

    private fun midpoint(a: ZonedDateTime, b: ZonedDateTime): ZonedDateTime {
        val halfMillis = (b.toInstant().toEpochMilli() - a.toInstant().toEpochMilli()) / 2
        return a.plusNanos(halfMillis * 1_000_000L)
    }
}
