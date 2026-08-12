package com.uvuruna.pocketwatch.core

import java.time.LocalTime
import java.time.ZonedDateTime

/**
 * Time -> dial-angle mapping. The ONE shared mapping used by the hour
 * hand, every sun-event arc boundary and the solar-noon marker.
 *
 * All angles are degrees, CLOCKWISE, 0 at the top of the dial — the same
 * convention the desktop's `core/angles.py` states, so a canvas rotate in
 * y-down screen coordinates takes them directly.
 */
object Angles {

    /**
     * Dial angle of a local wall-clock time.
     * 12:00 -> 0 (top), 18:00 -> 90 (right), 00:00 -> 180 (bottom),
     * 06:00 -> 270 (left).
     */
    fun timeToDialAngle(t: LocalTime): Double {
        val secs = t.hour * Constants.SECONDS_PER_HOUR + t.minute * 60 + t.second
        return floorMod360(
            secs / Constants.SECONDS_PER_DAY.toDouble() * 360.0 + Constants.DIAL_OFFSET_DEG
        )
    }

    fun timeToDialAngle(t: ZonedDateTime): Double = timeToDialAngle(t.toLocalTime())

    /** Angle of the large hand: one revolution per hour, 0 at the top. */
    fun minuteHandAngle(t: LocalTime): Double =
        (t.minute * 60 + t.second) / Constants.SECONDS_PER_HOUR.toDouble() * 360.0

    fun minuteHandAngle(t: ZonedDateTime): Double = minuteHandAngle(t.toLocalTime())

    /**
     * Dial angle of the moon-cycle marker: new moon at the TOP (0 deg),
     * full moon at the BOTTOM (180 deg), moving clockwise.
     */
    fun moonCycleAngle(fraction: Double): Double = floorMod360(fraction * 360.0)

    /**
     * Dial angle of a FIXED ring position/hour (0 top, clockwise) — the six
     * hexagram seats (12/16/20/24/4/8) and every other ring hour share this
     * one mapping.
     */
    fun ringPositionAngle(position: Int): Double =
        floorMod360(position * 15.0 + Constants.DIAL_OFFSET_DEG)

    /**
     * Shortest SIGNED hours from dial angle [angleB] to [angleA], wrapped to
     * [-12, 12) — 15 deg/hour, the SAME clockwise-from-top mapping
     * `timeToDialAngle` uses.
     */
    fun hoursBetween(angleA: Double, angleB: Double): Double =
        (floorMod360(angleA - angleB + 180.0) - 180.0) / 15.0

    /**
     * Rotation of the star (and solar-noon arrow) from the dial top — the
     * HEXAGRAM ROTATION.
     *
     * Positive rotates clockwise/right: solar noon later than 12:00 local
     * (city west of its zone meridian, or DST active); negative rotates
     * counterclockwise/left. 15 deg per hour of offset.
     *
     * Computed from integer seconds-since-local-midnight, exactly as the
     * desktop does — subtracting datetimes around noon invites sign bugs.
     */
    fun starRotationDeg(solarNoon: ZonedDateTime): Double {
        val secs = solarNoon.hour * Constants.SECONDS_PER_HOUR +
            solarNoon.minute * 60 + solarNoon.second
        return (secs - Constants.SOLAR_NOON_SECS) / Constants.SECONDS_PER_DEGREE
    }

    /** Non-negative remainder modulo 360 — Kotlin's `%` keeps the sign. */
    fun floorMod360(deg: Double): Double {
        val r = deg % 360.0
        return if (r < 0.0) r + 360.0 else r
    }

    /** Fold an angle into (-180, 180]. */
    fun foldAngle(deg: Double): Double {
        val wrapped = floorMod360(deg)
        return if (wrapped > 180.0) wrapped - 360.0 else wrapped
    }
}
