package com.uvuruna.pocketwatch.core

import org.json.JSONObject
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.time.ZonedDateTime

/**
 * The two bundled astronomy databases, read the way the desktop reads
 * them (`data/seasons.py`, `data/moon_phases.py`) — extract and discard,
 * cached per year.
 *
 * The repositories take the raw JSON TEXT rather than a file path: :core
 * stays pure, and the platform side (an Android asset, a test resource,
 * a file) decides where the bytes come from.
 */

/**
 * Seasons repository over `seasons_utc.json`.
 *
 * Field semantics, as verified on the desktop: an entry for calendar year
 * N is self-contained — `start` is the December solstice of year N-1,
 * spring/summer/autumn `.start` are the instants inside year N,
 * `winter.start` is the December solstice OF year N, and `end` is the
 * spring equinox of year N+1.
 */
class SeasonsRepository(jsonText: String) {
    private val root = JSONObject(jsonText)
    private val cache = HashMap<Int, YearWheel.YearAnchors>()

    /** The inclusive (first, last) calendar years the database holds. */
    fun coverage(): Pair<Int, Int> {
        val years = root.keys().asSequence().mapNotNull { it.toIntOrNull() }.toList()
        require(years.isNotEmpty()) { "Seasons database is empty" }
        return years.min() to years.max()
    }

    /** Six anchor instants bracketing [year]. */
    fun yearAnchors(year: Int): YearWheel.YearAnchors = cache.getOrPut(year) {
        val entry = root.optJSONObject(year.toString())
            ?: run {
                val (low, high) = coverage()
                throw IllegalArgumentException(
                    "Seasons database covers $low-$high; no entry for $year"
                )
            }
        YearWheel.YearAnchors(
            year = year,
            instants = listOf(
                parseInstant(entry.getString("start")),
                parseInstant(entry.getJSONObject("spring").getString("start")),
                parseInstant(entry.getJSONObject("summer").getString("start")),
                parseInstant(entry.getJSONObject("autumn").getString("start")),
                parseInstant(entry.getJSONObject("winter").getString("start")),
                parseInstant(entry.getString("end")),
            ),
        )
    }
}

/**
 * Moon phase repository over `moonPhases_utc.json`.
 *
 * Year entries mix month dicts ("1".."12") with year-level aggregate count
 * keys ("New Moon": 12, ...), so month keys are filtered by being digits.
 * Event names use "Third Quarter" while aggregates say "Last Quarter" —
 * normalized on load, exactly as the desktop does.
 */
class MoonPhaseRepository(jsonText: String) {
    private val root = JSONObject(jsonText)
    private val cache = HashMap<Int, Moon.MoonWindow>()

    fun coverage(): Pair<Int, Int> {
        val years = root.keys().asSequence().mapNotNull { it.toIntOrNull() }.toList()
        require(years.isNotEmpty()) { "Moon phases database is empty" }
        return years.min() to years.max()
    }

    /**
     * All principal-phase events of [year] plus its neighbour years, so any
     * instant inside [year] has bracketing events.
     */
    fun moonWindow(year: Int): Moon.MoonWindow = cache.getOrPut(year) {
        if (!root.has(year.toString())) {
            val (low, high) = coverage()
            throw IllegalArgumentException(
                "Moon phases database covers $low-$high; no entry for $year"
            )
        }
        val events = ArrayList<Pair<ZonedDateTime, Double>>()
        for (neighbour in (year - 1)..(year + 1)) {
            // Documented: coverage edge years use a 2-year window.
            val entry = root.optJSONObject(neighbour.toString()) ?: continue
            for (monthKey in entry.keys()) {
                if (monthKey.toIntOrNull() == null) continue // aggregate count keys
                val monthEvents = entry.getJSONObject(monthKey)
                for (iso in monthEvents.keys()) {
                    val name = monthEvents.getString(iso).let {
                        if (it == "Last Quarter") "Third Quarter" else it
                    }
                    val fraction = MOON_PHASE_FRACTIONS[name] ?: continue
                    events.add(parseInstant(iso) to fraction)
                }
            }
        }
        events.sortBy { it.first.toInstant() }
        Moon.MoonWindow(events)
    }

    private companion object {
        val MOON_PHASE_FRACTIONS = mapOf(
            "New Moon" to 0.0,
            "First Quarter" to 0.25,
            "Full Moon" to 0.5,
            "Third Quarter" to 0.75,
        )
    }
}

/** ISO-8601 with offset, as both databases write it. */
internal fun parseInstant(iso: String): ZonedDateTime =
    OffsetDateTime.parse(iso).atZoneSameInstant(ZoneOffset.UTC)
