"""The Ninth and the thirteenth plate — the dial's extra seats.

A theme's Ninth table and which Ninth is active, whether the alternate
Ninth holds the window, which face the centre shows, and the thirteenth
(blue-moon / leap) plate and its art.
"""

from datetime import date
from pathlib import Path

from config import calendar_mounts, constants, defaults, pantheon, paths
from core import angles, continents
from core.clock_state import DayContext, TickState
from render.calendar_mount import calendar_wheel
from render.context import RenderContext
from render.subdial import octa_slot_art
from skins.manifest import SkinDefinition


def thirteenth_plate(key: str) -> tuple[str, Path | None]:
    """(display name, resolved asset path or None) of the Blue Moon
    Law's 13th `key` (one of `constants.THIRTEENTHS`) — mirrors
    `theme_ninth`'s graceful-absent contract (Rule #5): the caller draws
    the name-only fallback when the path is None. Ophiuchus/The Cat
    resolve through the SAME zodiac/chinese registers every sign/animal
    already uses (the "sign"/"primary" looks, matching the Encyclopedia
    ninth-entry icon exactly); Sol/Modrenik read the sourceless
    MONTHS_ART_DIR, exactly like the twelve Slavic months (graceful-
    absent until the owner's prompt sheet lands).

    THE AXLE LAW's ALWAYS-CENTERS (Hestia/Jesus/Prudence/Cunning/Peace/
    Hardness of Heart, CANON §The Axle) resolve through the SAME
    `art_dir` as their OWN roster's twelve rim members — every prompt
    sheet drops the axle's plate in that one folder beside them, so
    there is no second art-dir table to keep in sync (Rule #19). The ONE
    registered `calendar_mounts.CalendarMount` whose own `centre` names this
    key supplies it; every art_dir may legitimately be missing that one
    extra file (art landed for the twelve rim members well ahead of the
    axle's own plate on every one of the four older Dozens, and the
    Sins Dozen has no art at all yet), same graceful-absent contract as
    everything else here. The axle's STEM follows the one no-space rule
    `CalendarMount.art_stems` already applies to its rim members
    (`Just_Indignation`): a filename cannot carry a space, so
    "Hardness of Heart" drops as `Hardness_of_Heart.png` — one rule, no
    second table (Rule #19); single-word axles are unaffected."""
    name, _family, _article = constants.THIRTEENTHS[key]
    if key == "ophiuchus":
        art = octa_slot_art("zodiac/astrology/primary/sign", name)
    elif key == "chinese":
        art = octa_slot_art("zodiac/chinese/primary/bronze", "Cat")
    elif key in ("sol", "modrenik"):
        resolved = paths.art_file(defaults.MONTHS_ART_DIR / f"{name}.png")
        art = resolved if resolved.exists() else None
    else:
        mount = next(
            m for m in calendar_mounts.CALENDAR_MOUNTS.values() if m.centre == key
        )
        art = octa_slot_art(mount.art_dir, name.replace(" ", "_"))
    return name, art


def active_thirteenth(skin: SkinDefinition, day: DayContext) -> str | None:
    """THE BLUE MOON LAW's CORRECTED resolution (owner overrule,
    retiring R12's global "any pointer, any theme" law — its own
    screenshot caught Ophiuchus on the hexa pointer with the Greek
    theme). A 13th ever claims the dial CENTER ONLY on the Calendar
    pointer (`skin.pointer == "calendar"`), in the ONE mode that owns
    it; every other pointer's ordinary center laws (the Sunday dual/
    Ninth windows) reign untouched, unconditionally — this function
    returns None before even looking at `day`.

    `day.thirteenth_candidates` (`core.blue_moon.thirteenth_candidates`,
    computed once a day) is an unordered FACT SET — resolving it to the
    Calendar pointer's OWN showing member reads the ACTIVE settings
    shape, never a date-only "which is more real" tiebreak (that R12
    notion is retired with the precedence machinery itself):

    - A MOUNT that names a thirteenth of its own
      (`calendar_mounts.CalendarMount.centre`) OUTRANKS the wheel whenever both
      are active at once — a mount is a more deliberate SECOND choice
      layered on top of the wheel (owner-documented tiebreak,
      ground-truthed against the settings model: `calendar_mount` is
      fully independent of `palette_style`, so both CAN be active
      together, e.g. the zodiac wheel with the chinese mount).
    - A mount that names NONE and the "off" case both fall through to
      the WHEEL (`calendar_wheel`, palette_style-picked): the zodiac
      wheel claims Ophiuchus, the almanac wheel claims Sol. Every roster
      registered today names a centre (the Emotions Dozen's is PEACE,
      sealed 2026-07-29 — CANON §The Axle), so this branch currently
      fires only for "off"; it stays live for a future roster that seals
      no centre — the Sins Dozen was the last candidate and it was
      sealed WITH its axle (Hardness of Heart) on 2026-07-29, so the
      branch is exercised by a synthetic mount in the tests.

    Whether the claimed member actually SHOWS is still its own
    appearance rule's business — `day.thirteenth_candidates` holds the
    calendar-driven members only on their own trigger+window (so on
    almost every day of the year one of THOSE returns None), but holds
    the ALWAYS-CENTERS (`constants.AXLE_ALWAYS_CENTERS`)
    UNCONDITIONALLY (CANON §The Axle: "ALWAYS-CENTERS stand on EVERY
    date") — so a mount whose `centre` is an axle (Hestia/Jesus/
    Prudence/Cunning/Peace/Hardness of Heart) shows it on literally
    every date, never gated by a window at all."""
    if skin.pointer != "calendar":
        return None
    candidates = day.thirteenth_candidates
    mount = calendar_mounts.CALENDAR_MOUNTS.get(skin.calendar_mount)
    key = mount.centre if mount is not None and mount.centre else (
        "ophiuchus" if calendar_wheel(skin) == "zodiac" else "sol"
    )
    return key if key in candidates else None


def ninth_table_for(theme: str, active_alt: bool) -> dict | None:
    """Which ALT-NINTH TABLE `theme_ninth` consults, or None to keep the
    canonical `constants.WEEKDAY_THEME_NINTHS` entry — THE MECHANISM
    DISPATCH itself (owner Double-Ninth verdicts, 2026-07-29), extracted
    so the WIRING is directly testable without needing a plate to exist
    on disk (`tests/test_weekday_rotation.py`'s art-free pins). Reads
    `constants.NINTH_MECHANISMS`:

    - "easter_egg"  -> `constants.WEEKDAY_THEME_NINTH_EASTER_EGG`
      (continents' Pangea).
    - "daynight"    -> `constants.WEEKDAY_THEME_NINTH_NIGHT` (sw_dyad's
      Exegol).
    - "term_weekly" -> None always: cp_corpo's weekly mandate reads NO
      alt table — the canonical entry's OWN seat roster already names
      both halves, and `on_date` alone (via `rotating_art_file`'s cadence
      override) picks between them (Rule #5, one rotation mechanism).
    - no mechanism, or `active_alt` False -> None (the plain canonical
      plate, unconditionally)."""
    if not active_alt:
        return None
    mechanism = constants.NINTH_MECHANISMS.get(theme)
    if mechanism == "easter_egg":
        return constants.WEEKDAY_THEME_NINTH_EASTER_EGG
    if mechanism == "daynight":
        return constants.WEEKDAY_THEME_NINTH_NIGHT
    return None


def theme_ninth(
    theme: str, active_alt: bool = False, on_date: date | None = None,
) -> tuple[str, Path] | None:
    """(display name, resolved asset path) of `theme`'s Ninth plate, or
    None when the theme names no Ninth (`constants.WEEKDAY_THEME_NINTHS`)
    or its plate has not landed on disk yet — the ONE existence-gated
    lookup `CenterBodyLayer` (paint) and the compositor's hover share
    (Rule #5), matching the graceful-absent law every other Ninth plate
    already follows.

    `active_alt` is the DOUBLE NINTH's alt-face switch (owner Double-
    Ninth verdicts, 2026-07-29 — was `pangea`, continents-only, before
    the law generalized): when True, `ninth_table_for` resolves WHICH
    alt table (if any) `theme`'s own `NINTH_MECHANISMS` entry names —
    continents' Pangea, sw_dyad's Exegol — same graceful-absent gate,
    its own alt plate. cp_corpo's "term_weekly" mechanism never reaches
    an alt table (see `ninth_table_for`); its rotation rides `on_date`
    alone, like every other seat roster.

    `on_date` opts the resolved plate into THE UNIVERSAL ROTATION
    CONVENTION (weekday ALT ROTATION round 2026-07-20/21 — bible_dark's
    Ninth Circle is the first Ninth to ship `alt/` siblings, cp_corpo's
    weekly mandate the first to ride a WEEKLY cadence instead of daily);
    None (every caller before this round) keeps the plain canonical
    file."""
    table = ninth_table_for(theme, active_alt)
    entry = table.get(theme) if table is not None else None
    if entry is None:
        entry = constants.WEEKDAY_THEME_NINTHS.get(theme)
    if entry is None:
        return None
    name, rel = entry
    asset = pantheon.weekday_art(rel)
    if not paths.art_file(asset).exists():
        return None
    if on_date is not None:
        asset = pantheon.rotating_art_file(asset, on_date) or asset
    return name, asset


def ninth_alt_active(ctx: RenderContext) -> bool:
    """Whether `ctx.skin.weekday_theme`'s Ninth shows its ALT face right
    now — THE MECHANISM DISPATCH the paint pass reads (owner Double-
    Ninth verdicts, 2026-07-29), replacing the old `weekday_theme ==
    "continents"` gate the two `theme_ninth` call sites below used to
    repeat (Rule #5 — one dispatch, not a copy per call site):

    - "easter_egg" reads `core.continents`'s sky law from the day's OWN
      pre-built anchors and the live eclipse flag (never recomputed).
    - "daynight" reads the SAME `TickState.is_daylight` `center_face`
      already reads — night is the alt face.
    - every other mechanism (or none) answers False; `theme_ninth` then
      falls back to the canonical plate, rotated by `on_date` alone."""
    mechanism = constants.NINTH_MECHANISMS.get(ctx.skin.weekday_theme)
    if mechanism == "easter_egg":
        return continents.ninth_is_pangea_from_events(
            ctx.day.local_date, ctx.day.season_events, ctx.day.moon_events,
            ctx.tick.eclipse_event is not None,
        )
    if mechanism == "daynight":
        return not ctx.tick.is_daylight
    return False


def ninth_window_anchor(day: DayContext, tick: TickState) -> str | None:
    """Which SOLAR anchor's ±`constants.CENTER_WINDOW_HOURS` window the
    hour hand stands in right now — "noon", "midnight", or None outside
    both. SOLAR, not wall-clock: `day.sun.noon` is the SAME anchor the
    hexagram's own rotation reads (`star_rotation_deg`) — reused via
    `angles.hours_between`, never a parallel clock (Rule #5/#6)."""
    noon_angle = angles.time_to_dial_angle(day.sun.noon)
    if (
        abs(angles.hours_between(tick.hour_angle, noon_angle))
        <= constants.CENTER_WINDOW_HOURS
    ):
        return "noon"
    midnight_angle = (noon_angle + 180.0) % 360.0
    if (
        abs(angles.hours_between(tick.hour_angle, midnight_angle))
        <= constants.CENTER_WINDOW_HOURS
    ):
        return "midnight"
    return None


def center_face(day: DayContext, tick: TickState, has_ninth: bool) -> str:
    """Which face the CENTER seat's Sunday duality shows RIGHT NOW
    (owner seal 2026-07-29, superseding INSTRUCTION #5's shape): the sky
    itself decides — DAYLIGHT the "ruler" (GOOD), NIGHT the "servant"
    (EVIL) — and a theme that names a Ninth shows "ninth" in BOTH solar
    windows (11:30-12:30 and 23:30-00:30 solar, `ninth_window_anchor`).
    Themes with no Ninth ignore the windows: day Ruler, night Servant,
    nothing else."""
    if has_ninth and ninth_window_anchor(day, tick) is not None:
        return "ninth"
    return "ruler" if tick.is_daylight else "servant"


def dual_seat_ninth(day: DayContext, tick: TickState) -> str | None:
    """Which SEAT the Ninth's badge takes over RIGHT NOW on a TWO-BADGE
    Sunday (owner seal 2026-07-29 — the rule the center windows always
    had, extended to the 12h/24h and 06h/18h displays): near solar NOON
    he replaces the "servant" (and stands beside the Ruler), near solar
    MIDNIGHT the "ruler" (and stands beside the Servant); None outside
    the windows. Callers gate on Sunday, `sunday_dual_face` and a theme
    that actually names a Ninth."""
    anchor = ninth_window_anchor(day, tick)
    if anchor == "noon":
        return "servant"
    if anchor == "midnight":
        return "ruler"
    return None
