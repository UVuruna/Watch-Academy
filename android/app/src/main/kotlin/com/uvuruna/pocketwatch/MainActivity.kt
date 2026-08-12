package com.uvuruna.pocketwatch

import android.os.Bundle
import android.os.Handler
import android.os.Looper
import androidx.appcompat.app.AppCompatActivity

/**
 * Phase 2's proof-of-life screen: one Activity holding one [DialView].
 *
 * This is NOT the watch. It draws no jewels, no ring, no crown, no plates —
 * it exists so a device can SEE :core computing real angles for a real
 * observer. The complete face is Phase 3 (the :render port) and the widget
 * is Phase 4.
 */
class MainActivity : AppCompatActivity() {

    private val handler = Handler(Looper.getMainLooper())
    private lateinit var dial: DialView

    private val tick = object : Runnable {
        override fun run() {
            dial.invalidate()
            // NO seconds hand: the hour hand moves 0.25 deg/min and the
            // minute hand 6 deg/min, so one repaint per minute suffices —
            // the platform fact the whole port rests on.
            handler.postDelayed(this, 60_000L)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        dial = DialView(this)
        setContentView(dial)
    }

    override fun onResume() {
        super.onResume()
        handler.post(tick)
    }

    override fun onPause() {
        handler.removeCallbacks(tick)
        super.onPause()
    }
}
