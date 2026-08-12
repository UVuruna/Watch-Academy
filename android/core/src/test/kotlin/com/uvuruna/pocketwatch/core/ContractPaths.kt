package com.uvuruna.pocketwatch.core

import java.io.File

/**
 * Locating the CONTRACT PACK from a test, robustly.
 *
 * The pack lives at `<repo>/shared/`, and the Gradle working directory can
 * be the module, the android root, or the repo root depending on how the
 * task was invoked — so the search walks upward until it finds the tree.
 */
object ContractPaths {

    val sharedDir: File by lazy {
        var dir: File? = File(".").absoluteFile.normalize()
        while (dir != null) {
            val candidate = File(dir, "shared/contract/golden_vectors.json")
            if (candidate.isFile) return@lazy File(dir, "shared")
            dir = dir.parentFile
        }
        throw IllegalStateException(
            "shared/contract/golden_vectors.json not found above " +
                File(".").absolutePath +
                " — the CONTRACT PACK must be exported before :core can be verified"
        )
    }

    val goldenVectors: File get() = File(sharedDir, "contract/golden_vectors.json")

    val seasonsJson: File get() = File(sharedDir, "Database/seasons_utc.json")

    val moonPhasesJson: File get() = File(sharedDir, "Database/moonPhases_utc.json")
}
