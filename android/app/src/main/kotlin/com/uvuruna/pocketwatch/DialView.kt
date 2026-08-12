package com.uvuruna.pocketwatch

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.util.AttributeSet
import android.view.View
import com.uvuruna.pocketwatch.core.Angles
import com.uvuruna.pocketwatch.core.Sun
import java.time.LocalDate
import java.time.ZoneId
import java.time.ZonedDateTime
import kotlin.math.cos
import kotlin.math.min
import kotlin.math.sin

/**
 * A PLACEHOLDER dial face — the visible end of the Phase 2 port.
 *
 * It paints the 24-hour circle, the hour seats and the two hands at angles
 * :core computes for the current instant in Belgrade, plus the solar-noon
 * arrow at the hexagram rotation. Nothing here is the real instrument: no
 * plates, no jewels, no ring presets, no crown. Phase 3 replaces this
 * whole file with the :render port.
 */
class DialView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
) : View(context, attrs) {

    private val zone: ZoneId = ZoneId.of("Europe/Belgrade")
    private val observer = Sun.Observer(latitude = 44.82, longitude = 20.46)

    private val rim = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 4f
        color = Color.parseColor("#C8B273")
    }
    private val tick = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 2f
        color = Color.parseColor("#7C8598")
    }
    private val label = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#D7DCE5")
        textAlign = Paint.Align.CENTER
    }
    private val hourHand = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 10f
        strokeCap = Paint.Cap.ROUND
        color = Color.parseColor("#E8E3D3")
    }
    private val minuteHand = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 5f
        strokeCap = Paint.Cap.ROUND
        color = Color.parseColor("#9FB4D8")
    }
    private val noonArrow = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 3f
        color = Color.parseColor("#E5B94E")
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val cx = width / 2f
        val cy = height / 2f
        val radius = min(width, height) / 2f * 0.86f
        label.textSize = radius * 0.09f

        canvas.drawCircle(cx, cy, radius, rim)

        // The 24 hour seats — degrees CLOCKWISE from the TOP, 12:00 at the
        // top and 00:00 at the bottom, straight out of :core.
        for (hour in 0 until 24) {
            val deg = Angles.ringPositionAngle(hour)
            val inner = if (hour % 6 == 0) radius * 0.86f else radius * 0.93f
            canvas.drawLine(
                cx + polarX(deg, inner), cy + polarY(deg, inner),
                cx + polarX(deg, radius), cy + polarY(deg, radius),
                tick,
            )
            if (hour % 3 == 0) {
                val textRadius = radius * 0.74f
                canvas.drawText(
                    hour.toString(),
                    cx + polarX(deg, textRadius),
                    cy + polarY(deg, textRadius) + label.textSize / 3f,
                    label,
                )
            }
        }

        val now = ZonedDateTime.now(zone)

        // Solar noon of today at this observer -> the hexagram rotation.
        val sun = Sun.computeSunDay(observer, LocalDate.now(zone), zone)
        val starDeg = Angles.starRotationDeg(sun.noon)
        canvas.drawLine(
            cx + polarX(starDeg, radius * 0.94f), cy + polarY(starDeg, radius * 0.94f),
            cx + polarX(starDeg, radius * 1.06f), cy + polarY(starDeg, radius * 1.06f),
            noonArrow,
        )

        // The two hands. Hour hand: one revolution per 24 h. Minute hand:
        // one revolution per hour. There is no seconds hand, by design.
        val hourDeg = Angles.timeToDialAngle(now)
        val minuteDeg = Angles.minuteHandAngle(now)
        canvas.drawLine(cx, cy, cx + polarX(hourDeg, radius * 0.55f), cy + polarY(hourDeg, radius * 0.55f), hourHand)
        canvas.drawLine(cx, cy, cx + polarX(minuteDeg, radius * 0.80f), cy + polarY(minuteDeg, radius * 0.80f), minuteHand)
    }

    /** Clockwise-from-top polar coordinates in y-down screen space. */
    private fun polarX(deg: Double, r: Float): Float =
        (r * sin(Math.toRadians(deg))).toFloat()

    private fun polarY(deg: Double, r: Float): Float =
        (-r * cos(Math.toRadians(deg))).toFloat()
}
