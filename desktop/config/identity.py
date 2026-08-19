"""What this build IS and calls itself.

The product's own fixed names - the one Windows sees in a taskbar
group, the one %APPDATA% is named after, the retired name the
one-time migrations still have to recognise - plus the two other
strings that identify the BUILD rather than anything it draws: the
typed word that unlocks the hidden extras, and which artwork
generations this build ships. None of them is geometry, sky, ring or
theme; none of them is user-tunable; nothing else in `config/` is
needed to read one, so this module is a leaf and `config/paths.py`
can lean on it without a cycle.

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

# ════════════════════════════ APP IDENTITY ════════════════════════════
APP_NAME = "Watch Academy"

# The retired product name, kept ONLY for the one-time migrations that
# carry an existing install onto the new identity (the %APPDATA% folder
# in main._migrate_legacy_user_dir, the HKCU Run value in
# app.native.migrate_legacy_autostart). THE RENAMING (owner decree
# 2026-08-10): the app is Watch Academy everywhere; DOMY survives only
# as the dial's own name and its dark-cross ring preset.
APP_NAME_LEGACY = "DOMY Watch"
ORGANIZATION = "UVuruna"
SINGLE_INSTANCE_MUTEX = "WatchAcademy.SingleInstance"

# Windows taskbar/AppUserModelID identity (owner screenshot 2026-07-20):
# without an explicit ID, Windows groups every window this interpreter
# opens under python.exe's OWN identity and can fall back to ITS icon
# for the taskbar button — see app.native.set_app_user_model_id.
APP_USER_MODEL_ID = "UVuruna.WatchAcademy"

# ════════════════════════════ HIDDEN MODE ════════════════════════════
# Typing this character sequence while the dial has focus unlocks the
# hidden extras (owner 2026-07-14) — for now the Four Greetings verses
# page in the Encyclopedia's Trinity topic. The owner sets the final
# sequence here; the unlock persists in settings.
HIDDEN_MODE_SECRET = "36m36u36v"

# ══════════════════════════ ARTWORK SOURCES ══════════════════════════
# The Gemini and ChatGPT generations COEXIST (owner 2026-07-14). Since
# the RESTRUCTURE (2026-07-22) the source is NO LONGER a folder segment
# — it is a terminal filename SUFFIX (`<Figure>[_vN]_<src>.png`, source
# last: `_gem`/`_gpt`). The user picks the active source in Settings;
# `config.paths.art_file` resolves the suffix at every disk boundary,
# falling back to the other source and then the suffix-less name (owner
# hand-made art). There is no longer a per-root registry — every PNG is
# resolved uniformly by filename suffix.
ART_SOURCES = ("gemini", "chatgpt")
ART_SOURCE_DEFAULT = "gemini"
ART_SOURCE_TITLES = {"gemini": "Gemini", "chatgpt": "ChatGPT"}
