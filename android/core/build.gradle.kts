// :core — PURE Kotlin/JVM. No Android dependency may ever enter here.
// Mirrors the desktop rule that `core` has no Qt and reads no wall clock.
plugins {
    id("org.jetbrains.kotlin.jvm")
}

// The bundled JBR is Java 21 and it is the ONLY JDK on this machine, so no
// toolchain is requested — the byte-code target is pinned to 17 instead,
// which is what :app compiles against.
java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}

kotlin {
    compilerOptions {
        jvmTarget.set(org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17)
    }
}

dependencies {
    // org.json ships INSIDE the Android framework (android.jar), so the
    // artifact is compile-only here: :core codes against the same API the
    // phone already provides and never packages a duplicate into the APK.
    compileOnly("org.json:json:20240303")
    testImplementation("org.json:json:20240303")
    testImplementation(kotlin("test"))
}

tasks.test {
    useJUnitPlatform()
    testLogging {
        events("passed", "skipped", "failed")
        showStandardStreams = true
    }
}
