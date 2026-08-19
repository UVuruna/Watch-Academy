"""What the user-facing CONTROLS may be set to.

Every entry here answers one question - "what values may the user
pick in this control": the roster of languages the language combo
offers (and the two ORIGINALS pinned at its top), the Encyclopedia's
Ctrl+Wheel zoom range and step, the element-scale and hover-enlarge
ranges, and the four saturation ranges with their slider steps.

It is deliberately NOT `config/ui_text.py`: that module is THE UI
STRING CATALOG - one flat tuple of every translatable chrome string
plus the `ui()` lookup - and a bound is not a string. What the two
share is only that a control reads them; what they ARE differs in
kind, and merging them would have made the catalog a mixed bag the
moment a range needed changing.

Born 2026-08-19, when the owner ruled that `config/constants.py`'s
**38 top-level sections** were a junk drawer, not a directory, and gave
the split its module names himself. Nothing here is new data - every
table below stood in `constants.py` under its own section banner and
moved WHOLE, with its comments; the callers were repointed, and no
re-export shim was left behind (`rules/CODE.md` - No backward
compatibility). The whole map, one row per module, is in
[the folder doc](___config.md).

Layer: config - pure Python, no Qt, no wall clock, no sibling import.
"""

# ═══════════════════════════ TRANSLATION LANGUAGES ═══════════════════════════
# Languages offered in Settings (owner: "all the provider offers") —
# the Google-translate codes the gtx endpoint accepts, code -> English
# display name. ORIGINALS (owner decision 2026-07-11) ship hand-written
# in the app (Database/translations/) and sit pinned at the top of the
# combo; every other language machine-translates on first pick.
TRANSLATION_ORIGINALS = ("en", "sr-Latn")
TRANSLATION_LANGUAGES = {
    "en": "English",
    "af": "Afrikaans", "sq": "Albanian", "am": "Amharic", "ar": "Arabic",
    "hy": "Armenian", "az": "Azerbaijani", "eu": "Basque",
    "be": "Belarusian", "bn": "Bengali", "bs": "Bosnian",
    "bg": "Bulgarian", "ca": "Catalan", "zh-CN": "Chinese (Simplified)",
    "zh-TW": "Chinese (Traditional)", "hr": "Croatian", "cs": "Czech",
    "da": "Danish", "nl": "Dutch", "eo": "Esperanto", "et": "Estonian",
    "fi": "Finnish", "fr": "French", "gl": "Galician", "ka": "Georgian",
    "de": "German", "el": "Greek", "gu": "Gujarati", "he": "Hebrew",
    "hi": "Hindi", "hu": "Hungarian", "is": "Icelandic",
    "id": "Indonesian", "ga": "Irish", "it": "Italian", "ja": "Japanese",
    "kn": "Kannada", "kk": "Kazakh", "ko": "Korean", "lv": "Latvian",
    "lt": "Lithuanian", "mk": "Macedonian", "ms": "Malay",
    "ml": "Malayalam", "mt": "Maltese", "mr": "Marathi",
    "mn": "Mongolian", "ne": "Nepali", "no": "Norwegian",
    "fa": "Persian", "pl": "Polish", "pt": "Portuguese",
    "pa": "Punjabi", "ro": "Romanian", "ru": "Russian",
    "sr": "Serbian (Cyrillic)", "sr-Latn": "Serbian (Latin)",
    "sk": "Slovak", "sl": "Slovenian", "es": "Spanish",
    "sw": "Swahili", "sv": "Swedish", "ta": "Tamil", "te": "Telugu",
    "th": "Thai", "tr": "Turkish", "uk": "Ukrainian", "ur": "Urdu",
    "uz": "Uzbek", "vi": "Vietnamese", "cy": "Welsh",
}

# ═══════════════════════════ UI SCALE & SATURATION RANGES ═══════════════════════════
# The Encyclopedia's Ctrl+MouseWheel ZOOM (owner round R8b item 5b:
# "uvodimo novu funkcionalnost CTRL + MOUSHE WHEEL... za smanjenje
# svega ili povecanje" — one factor scaling fonts, images and gallery
# tiles together). The RANGE bounds are the fixed product invariant
# (same pattern as ELEMENT_SCALE_RANGE above); the live factor itself
# is session-only state on `app.encyclopedia` (never written to
# settings — the owner asked for "the session at least", not
# persistence across restarts). STEP is the zoom delta per wheel notch
# (Qt reports ±120 angleDelta per notch — one notch = one STEP).
ENCYCLOPEDIA_ZOOM_RANGE = (0.6, 2.5)
ENCYCLOPEDIA_ZOOM_STEP = 0.1

# Element size multipliers (Settings sliders, owner EXTRAS) and the
# shared hover-enlarge factor (the element under the cursor draws this
# much larger; 1.0 disables the effect).
ELEMENT_SCALE_RANGE = (0.5, 2.0)
HOVER_ENLARGE_RANGE = (1.0, 2.0)
# The Saturation sliders (owner 2026-07-18, Settings ▸ Colors, Session
# 21-D — moved out of Display/Element sizes into their OWN "Saturation"
# group beside Palette + Ring tint): 0.0 grays the target to its own
# brightness, 1.0 is the owner preset unchanged. The slider itself is
# 0-100; the stored setting is the 0.0-1.0 factor.
# POINTER (formerly "palette_saturation" — renamed for clarity now that
# a second, independent RING slider exists): the Star+Aura palette's
# HSV saturation (`render.skin_geometry.palette_for`).
POINTER_SATURATION_RANGE = (0.0, 1.0)
POINTER_SATURATION_SLIDER_STEP = 1
# RING (new, Session 21-D): the ring band art's HSV saturation — the
# ring plate AND its letter/numeral overlay (`render.layers.ring.RingLayer`,
# after the ring_tint recolor). The Umbra and hands do not read this —
# see layers.md's RingLayer note for the ground-truthed scope.
RING_SATURATION_RANGE = (0.0, 1.0)
RING_SATURATION_SLIDER_STEP = 1
# HANDS (Watch Face Phase 4, R-25): the hand pack's own HSV saturation,
# independent of the ring's — `render.layers.hand.HandLayer` reads it
# alongside its existing `desaturate`/`tint` pipeline (the SAME
# `AssetCache.pixmap_by_height` saturation parameter the ring already
# uses, a bounded reuse — no new recolor math).
HANDS_SATURATION_RANGE = (0.0, 1.0)
HANDS_SATURATION_SLIDER_STEP = 1
# UMBRA (Watch Face Phase 4, R-25): scales the Umbra TINT's own HSV
# saturation before the black->tint->white tritone map runs
# (`render.skin_geometry.saturate_hue`, reused from the Aura's — Rule
# #5) — 0.0 grays the active tint to a plain neutral, 1.0 unchanged.
# A no-op while the Umbra follows Gray (tint is None): there is no hue
# to desaturate.
UMBRA_SATURATION_RANGE = (0.0, 1.0)
UMBRA_SATURATION_SLIDER_STEP = 1
