package com.uvuruna.pocketwatch.core

import org.json.JSONArray
import org.json.JSONObject
import java.time.LocalDate
import java.time.LocalTime
import java.time.ZoneId
import java.time.ZonedDateTime
import kotlin.math.abs
import kotlin.math.min
import kotlin.test.Test
import kotlin.test.assertTrue
import kotlin.test.fail

/**
 * THE tooth of the :core port (ANDROID.md, THE PARITY LAW mechanism 2):
 * Kotlin reads the very JSON the Python suite pins, and the port is DONE
 * when every vector is green — no other criterion.
 *
 * Every failure prints ACTUAL vs EXPECTED and the tolerance it broke. A
 * tolerance is never widened to make a vector pass; a red vector means the
 * port is wrong, or the desktop moved and the pack was not re-exported.
 */
class GoldenVectorsTest {

    private val root: JSONObject by lazy {
        JSONObject(ContractPaths.goldenVectors.readText())
    }

    private fun group(name: String): JSONArray =
        root.getJSONObject("groups").optJSONArray(name)
            ?: fail("golden vector group '$name' is missing from the pack")

    private val seasons: SeasonsRepository by lazy {
        SeasonsRepository(ContractPaths.seasonsJson.readText())
    }

    private val moonPhases: MoonPhaseRepository by lazy {
        MoonPhaseRepository(ContractPaths.moonPhasesJson.readText())
    }

    // --- group: hand_angles -------------------------------------------------

    @Test
    fun handAngles() = eachVector("hand_angles") { v, expected, tolerance ->
        val t = LocalTime.parse(v.getJSONObject("inputs").getString("time"))
        assertClose(
            "hour_hand_dial_angle_deg",
            Angles.timeToDialAngle(t),
            expected.getDouble("hour_hand_dial_angle_deg"),
            tolerance.getDouble("hour_hand_dial_angle_deg"),
        )
        assertClose(
            "minute_hand_angle_deg",
            Angles.minuteHandAngle(t),
            expected.getDouble("minute_hand_angle_deg"),
            tolerance.getDouble("minute_hand_angle_deg"),
        )
    }

    // --- group: hexagram_rotation -------------------------------------------

    @Test
    fun hexagramRotation() = eachVector("hexagram_rotation") { v, expected, tolerance ->
        val noonTime = LocalTime.parse(
            v.getJSONObject("inputs").getString("solar_noon_local_time")
        )
        // The formula reads the local wall clock of solar noon alone; any
        // date/zone carrying that clock time gives the same rotation.
        val noon = ZonedDateTime.of(
            LocalDate.of(2026, 1, 1), noonTime, ZoneId.of("UTC"),
        )
        assertClose(
            "star_rotation_deg",
            Angles.starRotationDeg(noon),
            expected.getDouble("star_rotation_deg"),
            tolerance.getDouble("star_rotation_deg"),
        )
    }

    // --- group: belgrade_dst ------------------------------------------------

    @Test
    fun belgradeDst() = eachVector("belgrade_dst") { v, expected, tolerance ->
        val sun = sunDayOf(v.getJSONObject("inputs"))
        assertClose(
            "star_rotation_deg",
            Angles.starRotationDeg(sun.noon),
            expected.getDouble("star_rotation_deg"),
            tolerance.getDouble("star_rotation_deg"),
        )
        assertEqualsReported(
            "regime",
            sun.regime.name.lowercase(),
            expected.getString("regime"),
        )
    }

    // --- group: tromso_regimes ----------------------------------------------

    @Test
    fun tromsoRegimes() = eachVector("tromso_regimes") { v, expected, tolerance ->
        val sun = sunDayOf(v.getJSONObject("inputs"))
        val clockTolerance = tolerance.optInt("clock_minutes", 0)

        assertEqualsReported(
            "regime", sun.regime.name.lowercase(), expected.getString("regime"),
        )
        assertClose(
            "star_rotation_deg",
            Angles.starRotationDeg(sun.noon),
            expected.getDouble("star_rotation_deg"),
            tolerance.getDouble("star_rotation_deg"),
        )
        assertClock("dawn", sun.dawn, expected, clockTolerance)
        assertClock("sunrise", sun.sunrise, expected, clockTolerance)
        assertClock("noon", sun.noon, expected, clockTolerance)
        assertClock("sunset", sun.sunset, expected, clockTolerance)
        assertClock("dusk", sun.dusk, expected, clockTolerance)
    }

    // --- group: mockup_day --------------------------------------------------

    @Test
    fun mockupDay() = eachVector("mockup_day") { v, expected, tolerance ->
        val inputs = v.getJSONObject("inputs")
        val sun = sunDayOf(inputs)
        val clockTolerance = tolerance.optInt("clock_minutes", 0)

        assertClock("sunrise", sun.sunrise, expected, clockTolerance)
        assertClock("noon", sun.noon, expected, clockTolerance)
        assertClock("sunset", sun.sunset, expected, clockTolerance)

        // The year marker sits essentially at the dial top on the mockup
        // day — the vector states the exact reading and how far from
        // 0/360 it may fall.
        val date = LocalDate.parse(inputs.getString("date"))
        val instant = ZonedDateTime.of(date, LocalTime.of(14, 34), ZoneId.of("UTC"))
        val marker = YearWheel.yearMarkerAngle(instant, seasons.yearAnchors(date.year))
        val fromTop = min(marker, 360.0 - marker)
        val limit = tolerance.getDouble("year_marker_deg_from_0_or_360")
        assertTrue(
            fromTop <= limit,
            "year_marker_deg: ACTUAL $marker is $fromTop deg from the dial top, " +
                "tolerance $limit",
        )
        // The pack also states the exact reading, so the port is held to it
        // and not merely to "somewhere near the top" — the interpolation
        // must agree with the desktop's, not just land in the neighbourhood.
        assertClose(
            "year_marker_deg_near_top_at_14_34_utc",
            marker,
            expected.getDouble("year_marker_deg_near_top_at_14_34_utc"),
            1e-6,
        )
    }

    // --- group: equinoxes ---------------------------------------------------

    @Test
    fun equinoxes() = eachVector("equinoxes") { v, expected, tolerance ->
        val instant = parseInstant(v.getJSONObject("inputs").getString("instant_utc"))
        // Anchors are built for the CALENDAR year of the vector's own
        // 2026 wheel — the six anchors bracket it, so the previous
        // December solstice and the next spring equinox belong to it too.
        val anchors = seasons.yearAnchors(anchorYearFor(v.getString("name")))
        val actual = YearWheel.yearMarkerAngle(instant, anchors)
        val target = expected.getDouble("year_marker_deg")
        val limit = tolerance.getDouble("year_marker_deg")
        // 0 and 360 are the same dial point; compare on the circle.
        val delta = min(abs(actual - target), 360.0 - abs(actual - target))
        assertTrue(
            delta <= limit,
            "year_marker_deg: ACTUAL $actual vs EXPECTED $target " +
                "(delta $delta > tolerance $limit)",
        )
    }

    /** Every equinox vector belongs to the 2026 anchor set. */
    private fun anchorYearFor(name: String): Int =
        Regex("(\\d{4})$").find(name)?.groupValues?.get(1)?.toInt() ?: 2026

    // --- group: moon_illumination -------------------------------------------

    @Test
    fun moonIllumination() = eachVector("moon_illumination") { v, expected, tolerance ->
        val instant = parseInstant(v.getJSONObject("inputs").getString("instant_utc"))
        assertClose(
            "phase_fraction",
            Moon.phaseFraction(instant, moonPhases.moonWindow(instant.year)),
            expected.getDouble("phase_fraction"),
            tolerance.getDouble("phase_fraction"),
        )
        assertClose(
            "analytic_illumination",
            Moon.illumination(instant),
            expected.getDouble("analytic_illumination"),
            tolerance.getDouble("analytic_illumination"),
        )
    }

    // --- machinery ----------------------------------------------------------

    private fun sunDayOf(inputs: JSONObject): Sun.SunDay = Sun.computeSunDay(
        Sun.Observer(inputs.getDouble("latitude"), inputs.getDouble("longitude")),
        LocalDate.parse(inputs.getString("date")),
        ZoneId.of(inputs.getString("timezone")),
    )

    /**
     * Runs [check] over every vector of a group, collecting ALL failures so
     * one red vector never hides the next.
     */
    private fun eachVector(
        groupName: String,
        check: (JSONObject, JSONObject, JSONObject) -> Unit,
    ) {
        val vectors = group(groupName)
        val failures = ArrayList<String>()
        for (i in 0 until vectors.length()) {
            val v = vectors.getJSONObject(i)
            try {
                check(
                    v,
                    v.getJSONObject("expected"),
                    v.optJSONObject("tolerance") ?: JSONObject(),
                )
            } catch (e: AssertionError) {
                failures.add("[${v.getString("name")}] ${e.message}")
            } catch (e: Exception) {
                failures.add("[${v.getString("name")}] threw $e")
            }
        }
        if (failures.isNotEmpty()) {
            fail(
                "$groupName: ${failures.size}/${vectors.length()} vectors RED\n" +
                    failures.joinToString("\n")
            )
        }
        println("$groupName: ${vectors.length()}/${vectors.length()} vectors green")
    }

    private fun assertClose(field: String, actual: Double, expected: Double, tolerance: Double) {
        val delta = abs(actual - expected)
        assertTrue(
            delta <= tolerance,
            "$field: ACTUAL $actual vs EXPECTED $expected " +
                "(delta $delta > tolerance $tolerance)",
        )
    }

    private fun assertEqualsReported(field: String, actual: String, expected: String) {
        assertTrue(actual == expected, "$field: ACTUAL '$actual' vs EXPECTED '$expected'")
    }

    /**
     * A "HH:MM" expectation against a local event time, or an explicit null
     * meaning the event does not occur on that day at that latitude.
     */
    private fun assertClock(
        field: String,
        actual: ZonedDateTime?,
        expected: JSONObject,
        toleranceMinutes: Int,
    ) {
        if (!expected.has(field)) return
        if (expected.isNull(field)) {
            assertTrue(
                actual == null,
                "$field: ACTUAL ${actual?.toLocalTime()} vs EXPECTED null " +
                    "(the event must not occur on this day)",
            )
            return
        }
        val want = expected.getString(field)
        if (actual == null) {
            fail("$field: ACTUAL null vs EXPECTED $want (the event was not found)")
        }
        val got = "%02d:%02d".format(actual.hour, actual.minute)
        val deltaMinutes = abs(
            (actual.hour * 60 + actual.minute) -
                (want.substring(0, 2).toInt() * 60 + want.substring(3, 5).toInt())
        )
        assertTrue(
            deltaMinutes <= toleranceMinutes,
            "$field: ACTUAL $got vs EXPECTED $want " +
                "(delta $deltaMinutes min > tolerance $toleranceMinutes min)",
        )
    }
}
