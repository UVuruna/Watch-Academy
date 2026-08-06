"""User runtime state: %APPDATA%/DOMY Watch/settings.json.

Deliberately plain JSON (inspectable, diffable, survives reinstall) and
the ONLY module that reads or writes the settings file. Writes are
atomic (tmp + os.replace). A corrupt file raises SettingsCorruptError —
the caller must surface it visibly (monorepo Rule #1), never reset
silently.
"""

import dataclasses
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from zoneinfo import ZoneInfo

from app.settings_fields import (
    _HEX_COLOR, MERGED_MOUNTS, RETIRED_SLOTS, load_alpha, load_bool, load_choice,
    load_earth_label, load_hex, load_numerals, load_palettes,
    load_rotation_group, load_scale, migrate_palette_key, save_numerals,
)
from app.settings_ring import fold_ring_name, load_named_dict, normalized_ring_card
from config import calendar_mounts, constants, defaults, dial, pantheon
from data.rings import ring_presets


class SettingsCorruptError(Exception):
    """The settings file exists but cannot be parsed/validated."""

    def __init__(self, path: Path, cause: Exception):
        super().__init__(f"Settings file is corrupt: {path} ({cause})")
        self.path = path
        self.cause = cause


@dataclass(frozen=True)
class Settings:
    schema_version: int = defaults.SETTINGS_SCHEMA_VERSION
    # None means "never positioned" — first run centers on the primary screen.
    window_x: int | None = None
    window_y: int | None = None
    diameter: int = dial.DEFAULT_DIAL_DIAMETER
    click_through: bool = False
    # Visibility Z mode (owner 2026-07-17, ROADMAP 15d): "bottom" — the
    # clock stays below every window except the desktop (the default);
    # "top" — always on top of everything (the always-visible small
    # clock). The widget swaps the window flags; not a render setting.
    z_mode: str = "bottom"
    ring: str = "DOMY"                  # ring preset CARD name (bundled or custom)
    ring_tint: str | None = None        # #RRGGBB multiplying ring+hands+Umbra
    # THE OUTER/INNER SPLIT TINT (R-21, owner correction 2026-08-05): the
    # inner minute-track band's own tint — None follows `ring_tint`
    # exactly like every release before the split art existed. Read only
    # when the owner's split art (assets/instrument/ring/outter+inner/)
    # is on disk; a no-op on the single-plate fallback.
    ring_tint_inner: str | None = None
    ring_finish: str = "gold"           # jewel metals (triangle/12h rules)
    # The user's custom ring cards ({name, positions, letters}) — merged
    # with Database/ring_presets.json by data/rings.py.
    custom_rings: tuple = ()
    # THE METAL-SPLIT OPTION (TASK 3, MASON/ICONS round, owner verdicts
    # 2026-07-19, third batch): per-preset choice between the 3-3
    # two-metal split and one finish on all six, for every seal preset
    # that carries its own `triangle` override (Mason/Omega/Templar
    # today) — keyed by preset name, like `theme_metals` below. A
    # preset absent here falls back to `constants.RING_TWO_METALS_DEFAULT`
    # (`app.controller._ring_two_metals` resolves both).
    ring_two_metals: dict = field(default_factory=dict)
    # THE EYE'S SHINE (DOLLAR/EYE round, owner decree 2026-07-27):
    # per-preset choice between the Eye of Providence with the glory
    # of rays and the plain eye, for every preset seating the adaptive
    # eye glyph (the Dollar today) — keyed by preset name, exactly
    # like `ring_two_metals` above; absent presets fall back to
    # `constants.RING_EYE_SHINE_DEFAULT`
    # (`app.controller._ring_eye_shine` resolves both).
    ring_eye_shine: dict = field(default_factory=dict)
    # COMPOSITIONAL RING MODEL (owner decree 2026-08-05): the active
    # preset's inner-band pick, keyed by preset name like
    # `ring_two_metals` (`app.controller._resolve_ring_inner`). Crown
    # text for CUSTOM rings: free-typed inscription + orientation
    # ("top"/"bottom"), keyed by ring name — bundled presets' motto
    # text lives in Database/ring_presets.json instead.
    ring_inner: dict = field(default_factory=dict)
    custom_ring_crown_text: dict = field(default_factory=dict)
    custom_ring_crown_orientation: dict = field(default_factory=dict)
    # THE LOCATION CROWN (RING VERDICTS round, owner decree 2026-08-05):
    # per-ring choice to replace the crown text (a preset's own motto or
    # a custom ring's typed text) with the ACTIVE location ("CITY,
    # COUNTRY") — keyed by ring name exactly like `ring_two_metals`,
    # available for bundled presets AND custom rings alike
    # (`app.controller._compose_skin`).
    ring_crown_location: dict = field(default_factory=dict)
    # Install defaults per the owner's 2026-07-12 list: hexa primary,
    # gradient-dark Umbra, atmosphere Earth, STEEL hands, 720 dial.
    pointer: str = "hexa"
    umbra_form: str = "gradient"
    umbra_contrast: str = "dark"
    palette_style: str = "primary"       # on Calendar: paint = Zodiac wheel,
                                        # light = Almanac wheel
    # The Calendar MOUNT (R9a, DESIGN ZODIAC law; GENERALIZED 2026-07-29):
    # WHICH roster rides the twelve wedges — "off" or any key of
    # `constants.CALENDAR_MOUNTS`. A file written before the
    # generalization keeps its value untouched; a file written before
    # the LIT-WEDGE DELETION (same day) still carries a stale
    # `calendar_lighting` key, which the loader simply ignores.
    calendar_mount: str = "zodiac"
    # THE ARCHETYPE MODE (owner sealed package 2026-07-16): the
    # diamonds carry the archetype figures and the weekday model and
    # all three slots switch OFF — at the RENDER level only, so the
    # slot keys below keep the user's choices untouched.
    archetype_mode: bool = False
    # Whether the ARCHETYPE FIGURES carry their display name (owner
    # 2026-07-18, ROADMAP 15h — Session 21-C): an INDEPENDENT Settings
    # switch, no longer piggybacking on `show_weekday_names` through a
    # menu twin — `ArchetypeLayer` reads THIS key for the figures' names
    # while the weekday Names switches (`show_weekday_names`,
    # `show_info_slot_names`) stay untouched for the weekday bodies.
    archetype_names: bool = True
    # THE CUBE LOOK (owner seal 2026-07-26, CUBE.md §Display laws): the
    # Double-Trinity family wheels — Court / Genesis / Council — render
    # as the corner-view CUBE (wide face rhombi) instead of the Diamond
    # medallion form. Inert on every other wheel.
    cube_look: bool = False
    # THE DAYLIGHT SWITCH (owner 2026-07-27, CUBE.md §The Rose): the
    # Calendar and the Rose may stand in flat full color instead of the
    # day/night law. Inert on every other pointer — never rewritten, so
    # the choice survives a pointer switch.
    daylight: bool = True
    # THE POINTER SHAPE (Pointers REWORK phase 1, owner sheet
    # UV/Pointers.png 2026-07-29): "star" (the diamond stars) or
    # "polygon" (the plain polygon of the same arms — the CUBE hexagon
    # on the Trinity, a touching 12-/24-point star on the Calendar and
    # the Rose). GLOBAL, one shape per watch; the armless Aurora ignores
    # it, and the value is never rewritten for it.
    pointer_shape: str = constants.POINTER_SHAPE_DEFAULT
    # THE EDGE PULL and its two forms (owner sheet: "Smooth concave" vs
    # "V-notched") — meaningful ONLY on the true polygons
    # (trio/cross/hexa/octa), inert on the Calendar's and the Rose's
    # star-shaped polygons and in the star shape itself.
    polygon_curvature: float = constants.POLYGON_CURVATURE_DEFAULT
    polygon_edge: str = constants.POLYGON_EDGE_DEFAULT
    # HIDE NIGHT BORDERS (owner option 2026-07-29): the arm/polygon
    # outline strokes are drawn over the sunlit arcs only, so the night
    # keeps its fills without the overlapping-border mesh. All pointers.
    hide_night_borders: bool = False
    # The Earth marker's label MODE (owner 2026-07-18, ROADMAP 15h — the
    # Design ▸ Earth submenu's FOUR exclusive toggles: Date / Weekday /
    # Date & Weekday / Full Date, `constants.EARTH_LABEL_MODES`).
    # Replaces the old show_earth_date/earth_weekday bool pair (Rule #6 —
    # load() migrates an older file's pair, and the pre-rename
    # archetype_earth_day key, onto this single enum).
    earth_label: str = "date"
    # THE TWO WORLD-MODES (ring_rework.md §1): "geocentric" (the
    # default — today's dial, bit for bit) or "heliocentric" (the
    # star stands, the world turns, and the dial inverts at night).
    # Absent from an older settings file = the default, so every
    # stored watch loads clean. Solar Rotation stays its own switch.
    #
    # The key is `world_mode`, never the bare `mode` this round first
    # wrote (2026-08-06 escalation): `mode` is the most generic word
    # there is, this file is ONE flat namespace of 112 keys, and a
    # hand-seeded profile carrying somebody else's top-level `mode`
    # would have been read as a world-mode. `world_mode` cannot
    # collide, matches `dial.WORLD_MODE_*` and `core.world`, and needs
    # no migration BECAUSE no generation of this file ever wrote a
    # top-level `mode` — an unknown key is simply not read.
    world_mode: str = dial.WORLD_MODE_DEFAULT
    solar_rotation: bool = True
    octa_slot: str = "time"             # South slot MODE
    day_slot_style: str = "sign"        # the DAY slot badge's own style
    info_slot_style: str = "sign"       # the INFO slot's own style
    info_slot_theme: str = "planets"    # the INFO slot's weekday theme
    weekday_slot: str = "weekday"       # the weekday POSITION: bodies, or
                                        # an astrology badge (hexa/aurora)
    # The THIRD slot (owner 2026-07-14: 1st/2nd/3rd Slot system) —
    # same shape as the other two; internal keys stay stable.
    third_slot: str = "date"
    third_slot_style: str = "sign"
    third_slot_theme: str = "planets"
    show_third_slot: bool = False
    earth_style: str = "atmo"
    weekday_theme: str = "planets"
    # The figure ROSTER is PER SLOT (owner 2026-07-15: "1. slot grcki
    # planetary, 2. slot grcki panteon") — picked inside each theme's
    # own dropdown, like the Pointer picks variant + palette.
    weekday_roster: str = "planetary"
    info_slot_roster: str = "planetary"
    third_slot_roster: str = "planetary"
    subdial_style: str = "black"        # complication plates (owner A/B
                                        # 2026-07-15): "theme" tints the
                                        # tapisserie field, "black" keeps
                                        # the standard dark AP field
    # THE SUBDIAL SET (owner decree 2026-07-21, Rsub round): which of
    # the five hand-picked plates (assets/subdial/set1..4, solo) draws
    # — the active jewel finish (ring_finish) still picks the color
    # WITHIN the chosen set. "set1" is the owner's install default.
    subdial_set: str = "set1"
    # THE METAL SHADES (R8a round, owner spec 2026-07-21 night): which
    # selectable shade each metal wears everywhere it appears (ring
    # letters always; badge medallions for gold/silver — bronze badges
    # stay the art as drawn). Names validated against
    # `config.constants.METAL_SHADE_NAMES`; defaults are the shade
    # closest to the pre-redo look (`config.constants.
    # METAL_SHADE_DEFAULT`).
    metal_shade_gold: str = "classic"
    metal_shade_bronze: str = "bronze"
    metal_shade_silver: str = "silver"
    # Artwork source (owner 2026-07-14): the Gemini and ChatGPT
    # generations coexist on disk; this picks which one the dial and
    # the readers show (missing files fall back to the other source).
    art_source: str = constants.ART_SOURCE_DEFAULT
    legend: bool = True
    # Elements switches (owner spec, FINAL.txt #5): each removes one dial
    # element; the day/twilight indication itself always stays.
    show_earth: bool = True
    show_moon: bool = True
    show_weekday: bool = True
    show_pointer: bool = True
    colorful: bool = True               # off -> white Aura instead of hues
    show_seconds: bool = True
    show_octa_slot: bool = False        # canon 2026-07-14: ONE slot only
    show_weekday_names: bool = True     # the day-name text on the bodies
    show_info_slot_names: bool = True   # the day-name text on the info
                                        # slot's second body (owner bug
                                        # 2026-07-13: its OWN switch —
                                        # the two slots were linked)
    moon_hidden_alpha: float = 0.5      # Moon marker opacity below the horizon
    hands: str = "STEEL"                # the hand pack (Design ▸ Hands)
    # Theme rotation (owner spec 2026-07-12; group dropdown
    # 2026-07-14): "none" = the canon, no rotation; a kinship-group
    # title straight from the Weekday menu grouping cycles that whole
    # family; "custom" cycles the CHECKED themes.
    theme_rotation_group: str = "none"
    theme_rotation_minutes: int = 60
    theme_rotation_themes: tuple[str, ...] = constants.WEEKDAY_THEMES
    # The METAL each bronze-plate theme wears (owner 2026-07-12):
    # {"greek"/"norse"/"profession": "gold"/"bronze"/"silver"}; absent
    # theme = bronze (the art as drawn). follow_ring makes all three
    # wear the ring_finish metal instead.
    theme_metals: dict = field(default_factory=dict)
    theme_metal_follow_ring: bool = False
    language: str = "en"                # translation target (en = originals)
    # THE YEAR LINE (Session 16, owner amendment 2026-07-17): the
    # official form's era labels ("bce_ce" default / "bc_ad"), whether
    # positive years carry the suffix (default bare — "2026"), and the
    # optional THIRD calendar beside the always-shown Anno Lucis
    # (none/auc/byzantine/hebrew/hegirae/chinese/maya — maya is the
    # odd one out, a true day count rather than a year offset, MAYA
    # round, owner 2026-07-20).
    era_notation: str = "bce_ce"
    show_era_suffix: bool = False
    third_era: str = "none"
    # QUICK JUMP CITIES (owner slika 12): the user's own places in the
    # Quick Jump ▸ Location submenu — tuples of {name, latitude,
    # longitude, timezone} picked from the location database in
    # Settings; a jump moves the OBSERVER there, the moment stays.
    jump_cities: tuple = ()
    # Location (M6 picker; defaults = the Belgrade preset).
    city_name: str = defaults.DEFAULT_CITY["name"]
    city_path: tuple[str, ...] = ()     # picker combo restore; () = never picked
    latitude: float = defaults.DEFAULT_CITY["latitude"]
    longitude: float = defaults.DEFAULT_CITY["longitude"]
    timezone: str = defaults.DEFAULT_CITY["timezone"]
    # Element size multipliers + the shared hover-enlarge factor
    # (owner EXTRAS): 1.0 = the skin's own size; hovering an element
    # draws it hover_enlarge times larger (1.0 disables the effect).
    earth_scale: float = 1.0
    moon_scale: float = 1.0
    # ONE size for every slot (owner 2026-07-14: the weekday diamonds
    # and the subdials share the SLOT slider — the old separate
    # weekday/south-slot scales are gone).
    slot_scale: float = 1.0
    # RENAMED from `ring_letter_scale` (JEWELS naming sweep, owner ruling
    # 2026-08-06); `load()` reads a stored file's old `ring_letter_scale`
    # key as the fallback when the new key is absent (one-release
    # migration, save writes only the new key).
    ring_jewels_scale: float = 1.0
    hover_enlarge: float = 1.2
    # SATURATION (owner 2026-07-18, Settings ▸ Colors, Session 21-D —
    # moved out of Display/Element sizes into its OWN "Saturation" group
    # beside Palette + Ring tint, split into two independent sliders).
    # POINTER (renamed from "palette_saturation" — one release migrates
    # the old key, see SettingsStore.load): scales the Star+Aura
    # palette's HSV saturation at skin build (`render.layers.
    # palette_for`, the ONE spot the palette flows into both the
    # pointer AND the Aura wedges, so they stay in step) — 1.0 = the
    # owner preset unchanged, 0.0 = grayed to each hue's own brightness.
    pointer_saturation: float = 1.0
    # RING (new, Session 21-D): scales the ring band art's (the ring
    # plate + its letter overlay) HSV saturation, applied AFTER the
    # ring_tint recolor (`render.layers.ring.RingLayer`) — 1.0 unchanged,
    # 0.0 grayed. The Umbra and hands do not read this.
    ring_saturation: float = 1.0
    # Display overrides (None = the skin's own value). The Aura's
    # sunlight and twilight opacities are INDEPENDENT (owner spec).
    star_alpha: float | None = None
    aura_day_alpha: float | None = None
    aura_twilight_alpha: float | None = None
    # THE UMBRA OPACITY (Watch Face Phase 4, R-15, owner-requested): a
    # plain layer-level alpha at composite time
    # (`render.layers.background.BackgroundLayer._draw_umbra`) — 1.0
    # unchanged (fully opaque, today's behavior).
    umbra_alpha: float = 1.0
    # THE MOON TRANSIT OPACITY (Watch Face Phase 4, R-35 — "Moon — hover
    # over Earth" reads as the Moon marker's rim-transit dimming when it
    # meets the Earth marker, `render.daylight.moon_transit_opacity`;
    # there is no mouse-hover state here, only this transit). None = the
    # skin's own `dial.MOON_TRANSIT_OPACITY`.
    moon_transit_alpha: float | None = None
    # THE GHOST OPACITY (Watch Face Phase 4, R-36 — "Inactive icons":
    # the non-active weekday bodies' `WeekdaySpec.ghost_opacity`). None =
    # the active theme's own value (themes differ today).
    ghost_alpha: float | None = None
    # THE UMBRA TINT (Watch Face Phase 4, R-22): "follow" (default)
    # reads `ring_tint`, unchanged from today; "custom" reads `umbra_tint`
    # instead — both through the same `render.painting.tinted_gray`.
    umbra_tint_mode: str = "follow"
    umbra_tint: str | None = None       # #RRGGBB, used only in "custom" mode
    umbra_saturation: float = 1.0       # HSV scale of the active tint (0..1)
    # THE AURA COLORLESS COLORING (Watch Face Phase 4, R-23): active
    # only while `colorful` is off. "follow" tritones `ring_tint` toward
    # white; "white"/"black" are flat; "custom" reads `aura_off_tint`.
    aura_off_tint_mode: str = "white"
    aura_off_tint: str | None = None    # #RRGGBB, used only in "custom" mode
    # THE HANDS FREE COLOR (Watch Face Phase 4, R-24): None follows
    # `ring_tint` like every hand today; a hex overrides it independently.
    hands_tint: str | None = None
    hands_saturation: float = 1.0       # the hand pack's own HSV scale (0..1)
    # THE JEWELS FREE COLOR (Watch Face Phase 4, R-24): an EXTRA tint
    # layered over the ring jewels' metal finish (None = metal only,
    # today's behavior) — `render.layers.ring.RingLayer._draw_ring_glyph`.
    # RENAMED from `jewels_tint` (JEWELS naming sweep, owner ruling
    # 2026-08-06, "one term for one thing"); `load()` reads a stored
    # file's old `jewels_tint` key as the fallback default when the new
    # key is absent (one-release migration, save writes only the new key).
    jewels_tint: str | None = None
    # CROWN TEXT (R-24/Phase-6-debt correction, owner 2026-08-05: "Crown
    # tekst je onaj tekst koji piše oko sata — faith, hope, suffering")
    # — the outer Great Seal CROWN TEXT arc's own opacity/size/color, kept
    # SEPARATE from `ring_jewels_scale`/`jewels_tint` (see
    # `skins.manifest.SkinDefinition`'s matching fields for the full
    # design note). `crown_text_scale` multiplies ON TOP of `ring_jewels_scale`
    # (unaffected, never renamed); `crown_text_tint` resolves independently of
    # `jewels_tint`. RENAMED from `motto_*` (TASK 1, owner ruling
    # 2026-08-06, "one term for one thing"); `load()` reads a stored file's
    # old `motto_alpha`/`motto_scale`/`motto_tint` keys as the fallback
    # default when the new keys are absent (the SAME one-release migration
    # shape `pointer_saturation` uses for `palette_saturation` below).
    crown_text_alpha: float = 1.0
    crown_text_scale: float = 1.0
    crown_text_tint: str | None = None
    # THE LIVE NUMERAL BANDS (ring_rework.md §5 + hour_numerals.md §8):
    # the two hand-drawn numeral bands' own settings, at the ledger's
    # SETTLED defaults. Every one of them carries a default here, so a
    # settings file written before this round loads clean — an absent
    # key is simply the SETTLED value, never a corrupt read. Their
    # ranges and rosters live in `config.dial`; the render side keys its
    # band cache on them (`render.layers.numerals.band_spec`).
    numeral_outer_size: int = dial.NUMERAL_OUTER_SIZE_DEFAULT
    numeral_inner_size: int = dial.NUMERAL_INNER_SIZE_DEFAULT
    numeral_outer_ring_size: float = dial.NUMERAL_OUTER_RING_SIZE_DEFAULT
    numeral_face: str = dial.NUMERAL_OUTER_FACE_DEFAULT
    numeral_inner_face: str = dial.NUMERAL_INNER_FACE_DEFAULT
    crown_face: str = dial.CROWN_FACE_DEFAULT
    numeral_seating: str = dial.NUMERAL_SEATING_DEFAULT
    numeral_relief: str = dial.NUMERAL_RELIEF_DEFAULT
    numeral_depth: float = dial.NUMERAL_DEPTH_DEFAULT
    numeral_light: str = dial.NUMERAL_LIGHT_DEFAULT
    numeral_darkness: float = dial.NUMERAL_DARKNESS_DEFAULT
    numeral_contact_blur: float = dial.NUMERAL_CONTACT_BLUR_DEFAULT
    numeral_border: float = dial.NUMERAL_BORDER_DEFAULT
    crown_time_format: str = dial.CROWN_TIME_FORMAT_DEFAULT
    # Custom palettes keyed "pointer_style" -> tuple of #RRGGBB hues.
    palettes: dict = field(default_factory=dict)


class SettingsStore:
    def __init__(self, path: Path):
        self._path = path

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> Settings:
        """Missing file -> default Settings (documented first-run behavior).
        Corrupt file -> SettingsCorruptError."""
        if not self._path.exists():
            return Settings()
        try:
            # utf-8-sig: hand-edited files saved with a BOM must still parse
            raw = json.loads(self._path.read_text(encoding="utf-8-sig"))
            # THE IDENTITY MARKERS, named out loud (2026-08-06
            # escalation). Both have been required since the first
            # release (0.14.001) and neither is new — but a file
            # without them used to die on a bare `KeyError('window')`,
            # whose entire message is the word `window`. That message
            # read to a later session as "the code now demands a
            # section it never wrote" and cost a round of
            # investigation; naming the file's own top-level keys back
            # to the reader is the difference between a diagnosis and
            # a riddle.
            #
            # They stay REQUIRED on purpose: defaulting them would
            # turn an unreadable file into a SILENT reset of 112
            # settings, which is the one thing this module's docstring
            # forbids. A file the app itself wrote always carries
            # them, so no stored watch is affected.
            if not isinstance(raw, dict):
                raise ValueError(
                    f"not a DOMY Watch settings file: the JSON root is "
                    f"{type(raw).__name__}, not an object"
                )
            missing = [
                key for key in ("schema_version", "window") if key not in raw
            ]
            if missing:
                raise ValueError(
                    "not a DOMY Watch settings file: no "
                    + ", ".join(repr(key) for key in missing)
                    + f" (its own top-level keys: {sorted(raw)})"
                )
            window = raw["window"]
            diameter = int(window["diameter"])
            if not dial.MIN_DIAL_DIAMETER <= diameter <= dial.MAX_DIAL_DIAMETER:
                raise ValueError(f"diameter {diameter} outside allowed range")
            # A bad value here would otherwise KeyError deep inside a
            # paint pass, where Qt swallows the exception.
            choices = {}
            ring_tint = raw.get("ring_tint")
            if ring_tint is not None:
                ring_tint = str(ring_tint).upper()
                if not _HEX_COLOR.match(ring_tint):
                    raise ValueError(f"ring_tint {ring_tint!r} not #RRGGBB")
            # Custom ring cards first — the chosen ring name is checked
            # against bundled + custom together; the name matches case-
            # insensitively (older files stored "domy").
            custom_rings = tuple(
                normalized_ring_card(entry)
                for entry in raw.get("custom_rings", ())
            )
            jump_cities = tuple(
                _normalized_jump_city(entry)
                for entry in raw.get("jump_cities", ())
            )
            by_fold = {
                name.lower(): name for name in ring_presets(custom_rings)
            }
            ring_value = str(raw.get("ring", "DOMY"))
            ring = fold_ring_name(ring_value, by_fold)
            if ring is None:
                raise ValueError(f"ring {ring_value!r} unknown")
            # THE METAL-SPLIT OPTION (TASK 3): per-preset dict, same
            # lenient policy `theme_metals` already uses below — a
            # non-bool value or a name that resolves to nothing loaded
            # (a stale bundled rename, a deleted custom ring) is simply
            # dropped rather than corrupting the whole file over one
            # stale entry.
            is_bool = lambda v: isinstance(v, bool)
            ring_two_metals = load_named_dict(raw, "ring_two_metals", by_fold, is_bool)
            ring_eye_shine = load_named_dict(raw, "ring_eye_shine", by_fold, is_bool)
            ring_inner = load_named_dict(
                raw, "ring_inner", by_fold, constants.RING_INNERS.__contains__
            )
            custom_ring_crown_text = load_named_dict(
                raw, "custom_ring_crown_text", by_fold,
                lambda v: isinstance(v, str) and bool(v),
            )
            custom_ring_crown_orientation = load_named_dict(
                raw, "custom_ring_crown_orientation", by_fold,
                ("top", "bottom").__contains__,
            )
            ring_crown_location = load_named_dict(
                raw, "ring_crown_location", by_fold, is_bool
            )
            # One-time migration (2026-07-12): the South slot became a
            # MODE + per-family STYLE pair — the six old combined
            # values map onto it (external user data, not an API shim).
            legacy_slot = {
                "zodiac_sign": ("zodiac", "sign"),
                "zodiac_logo": ("zodiac", "logo"),
                "zodiac_constellation": ("zodiac", "constellation"),
                "zodiac_text": ("zodiac", "text"),
                "chinese_logo": ("chinese", "bronze"),
                "chinese_text": ("chinese", "text"),
            }
            if raw.get("octa_slot") in legacy_slot:
                mode, style = legacy_slot[raw["octa_slot"]]
                raw["octa_slot"] = mode
                raw.setdefault("info_slot_style", style)
            # Second migration (2026-07-12): the per-FAMILY style keys
            # became per-SLOT styles so the two slots stay independent.
            family_styles = {
                "zodiac": raw.get("zodiac_style"),
                "ascendant": raw.get("ascendant_style"),
                "chinese": raw.get("chinese_style"),
            }
            if "info_slot_style" not in raw:
                style = family_styles.get(raw.get("octa_slot"))
                if style:
                    raw["info_slot_style"] = style
            if "day_slot_style" not in raw:
                style = family_styles.get(raw.get("weekday_slot"))
                if style:
                    raw["day_slot_style"] = style
            # Third migration (2026-07-28): the wheel SLOT keys became
            # POSITIONAL — paint/light/cube named a color doctrine the
            # wheels had long stopped obeying. Every settings file
            # written before that day carries the retired words, both in
            # `palette_style` and in each custom-palette key
            # ("hexa_paint"). This one is not cosmetic: an unknown
            # palettes key RAISES, so without the migration the whole
            # file reads as corrupt and the owner is offered a reset —
            # losing every stored watch. External user data, not an API
            # shim (Rule #6 governs code, not files already on disk).
            if raw.get("palette_style") in RETIRED_SLOTS:
                raw["palette_style"] = RETIRED_SLOTS[raw["palette_style"]]
            if raw.get("calendar_mount") in MERGED_MOUNTS:
                raw["calendar_mount"] = MERGED_MOUNTS[raw["calendar_mount"]]
            if isinstance(raw.get("palettes"), dict):
                raw["palettes"] = {
                    migrate_palette_key(key): hues
                    for key, hues in raw["palettes"].items()
                }
            for key, default, allowed in (
                ("language", "en", tuple(constants.TRANSLATION_LANGUAGES)),
                ("ring_finish", "gold", constants.RING_FINISHES),
                ("pointer", "hexa", tuple(constants.POINTER_POINTS)),
                ("umbra_form", "gradient", constants.UMBRA_FORMS),
                ("umbra_contrast", "dark", constants.UMBRA_CONTRAST_VARIANTS),
                ("palette_style", "primary", constants.PALETTE_STYLES),
                ("pointer_shape", constants.POINTER_SHAPE_DEFAULT,
                 constants.POINTER_SHAPES),
                ("polygon_edge", constants.POLYGON_EDGE_DEFAULT,
                 constants.POLYGON_EDGE_MODES),
                ("calendar_mount", "zodiac", calendar_mounts.CALENDAR_MOUNT_MODES),
                ("octa_slot", "time", constants.OCTA_SLOT_MODES),
                ("day_slot_style", "sign", constants.SLOT_STYLE_VALUES),
                ("info_slot_style", "sign", constants.SLOT_STYLE_VALUES),
                ("info_slot_theme", "planets", constants.WEEKDAY_THEMES),
                ("weekday_slot", "weekday", constants.WEEKDAY_SLOT_MODES),
                ("third_slot", "date", constants.OCTA_SLOT_MODES),
                ("third_slot_style", "sign", constants.SLOT_STYLE_VALUES),
                ("third_slot_theme", "planets", constants.WEEKDAY_THEMES),
                ("earth_style", "atmo", constants.EARTH_STYLES),
                ("weekday_theme", "planets", constants.WEEKDAY_THEMES),
                ("subdial_style", "black", constants.SUBDIAL_STYLES),
                ("subdial_set", "set1", constants.SUBDIAL_SETS),
                ("metal_shade_gold", constants.METAL_SHADE_DEFAULT["gold"],
                 constants.METAL_SHADE_NAMES["gold"]),
                ("metal_shade_bronze", constants.METAL_SHADE_DEFAULT["bronze"],
                 constants.METAL_SHADE_NAMES["bronze"]),
                ("metal_shade_silver", constants.METAL_SHADE_DEFAULT["silver"],
                 constants.METAL_SHADE_NAMES["silver"]),
                ("weekday_roster", "planetary", constants.FIGURE_ROSTERS),
                ("info_slot_roster", "planetary", constants.FIGURE_ROSTERS),
                ("third_slot_roster", "planetary", constants.FIGURE_ROSTERS),
                ("art_source", constants.ART_SOURCE_DEFAULT,
                 constants.ART_SOURCES),
                ("era_notation", "bce_ce", constants.ERA_NOTATIONS),
                ("third_era", "none", constants.THIRD_ERAS),
                ("z_mode", "bottom", constants.Z_MODES),
                ("umbra_tint_mode", "follow", constants.UMBRA_TINT_MODES),
                ("aura_off_tint_mode", "white", constants.AURA_OFF_TINT_MODES),
            ):
                value = str(raw.get(key, default))
                if value not in allowed:
                    raise ValueError(f"{key} {value!r} unknown")
                choices[key] = value
            location = raw.get("location", {})
            latitude = float(location.get("latitude", defaults.DEFAULT_CITY["latitude"]))
            longitude = float(
                location.get("longitude", defaults.DEFAULT_CITY["longitude"])
            )
            if not constants.LATITUDE_RANGE[0] <= latitude <= constants.LATITUDE_RANGE[1]:
                raise ValueError(f"latitude {latitude} outside allowed range")
            if (
                not constants.LONGITUDE_RANGE[0]
                <= longitude
                <= constants.LONGITUDE_RANGE[1]
            ):
                raise ValueError(f"longitude {longitude} outside allowed range")
            timezone = str(location.get("timezone", defaults.DEFAULT_CITY["timezone"]))
            try:
                ZoneInfo(timezone)
            except Exception as exc:
                raise ValueError(f"timezone {timezone!r} unknown: {exc}") from exc
            loaded = Settings(
                schema_version=int(raw["schema_version"]),
                window_x=None if window["x"] is None else int(window["x"]),
                window_y=None if window["y"] is None else int(window["y"]),
                diameter=diameter,
                # Additive keys (still schema 1): absent in older files.
                click_through=load_bool(raw, "click_through", False),
                show_era_suffix=load_bool(raw, "show_era_suffix", False),
                archetype_mode=load_bool(raw, "archetype_mode", False),
                archetype_names=load_bool(raw, "archetype_names", True),
                cube_look=load_bool(raw, "cube_look", False),
                daylight=load_bool(raw, "daylight", True),
                # Pointers REWORK phase 1 (owner sheet 2026-07-29) —
                # additive keys: a file written before it simply gets
                # the star shape, no curvature and today's borders.
                polygon_curvature=load_scale(
                    raw, "polygon_curvature",
                    *constants.POLYGON_CURVATURE_RANGE,
                    constants.POLYGON_CURVATURE_DEFAULT,
                ),
                hide_night_borders=load_bool(
                    raw, "hide_night_borders", False
                ),
                earth_label=load_earth_label(raw),
                world_mode=load_choice(
                    raw, "world_mode", dial.WORLD_MODES,
                    dial.WORLD_MODE_DEFAULT,
                ),
                solar_rotation=load_bool(raw, "solar_rotation", True),
                legend=load_bool(raw, "legend", True),
                show_earth=load_bool(raw, "show_earth", True),
                show_moon=load_bool(raw, "show_moon", True),
                show_weekday=load_bool(raw, "show_weekday", True),
                show_pointer=load_bool(raw, "show_pointer", True),
                colorful=load_bool(raw, "colorful", True),
                show_seconds=load_bool(raw, "show_seconds", True),
                # Canon (owner 2026-07-14): ONE slot out of the box.
                show_octa_slot=load_bool(raw, "show_octa_slot", False),
                show_third_slot=load_bool(raw, "show_third_slot", False),
                show_weekday_names=load_bool(raw, "show_weekday_names", True),
                show_info_slot_names=load_bool(
                    raw, "show_info_slot_names", True
                ),
                moon_hidden_alpha=load_scale(
                    raw, "moon_hidden_alpha", 0.0, 1.0, 0.5
                ),
                hands=(
                    raw["hands"]
                    if isinstance(raw.get("hands"), str) and raw["hands"].strip()
                    else "STEEL"
                ),
                theme_rotation_group=load_rotation_group(raw),
                theme_rotation_minutes=(
                    int(raw["theme_rotation_minutes"])
                    if isinstance(raw.get("theme_rotation_minutes"), int)
                    and 1 <= raw["theme_rotation_minutes"] <= 24 * 60
                    else 60
                ),
                theme_rotation_themes=tuple(
                    theme
                    for theme in raw.get(
                        "theme_rotation_themes", constants.WEEKDAY_THEMES
                    )
                    if theme in constants.WEEKDAY_THEMES
                ) or constants.WEEKDAY_THEMES,
                theme_metals={
                    str(theme): str(metal)
                    for theme, metal in dict(
                        raw.get("theme_metals", {})
                    ).items()
                    if str(theme) in constants.METAL_THEMES
                    # Per-theme allowed set (owner 2026-07-18): planets_art
                    # has no colored/ folder, so "colored" is rejected for
                    # it even though it is metal-capable.
                    and str(metal) in constants.theme_metals(str(theme))
                },
                theme_metal_follow_ring=load_bool(
                    raw, "theme_metal_follow_ring", False
                ),
                city_name=str(location.get("name", defaults.DEFAULT_CITY["name"])),
                city_path=tuple(location.get("path", ())),
                latitude=latitude,
                longitude=longitude,
                timezone=timezone,
                ring=ring,
                custom_rings=custom_rings,
                ring_two_metals=ring_two_metals,
                ring_eye_shine=ring_eye_shine,
                ring_inner=ring_inner,
                custom_ring_crown_text=custom_ring_crown_text,
                custom_ring_crown_orientation=custom_ring_crown_orientation,
                ring_crown_location=ring_crown_location,
                jump_cities=jump_cities,
                ring_tint=ring_tint,
                earth_scale=load_scale(raw, "earth_scale", *constants.ELEMENT_SCALE_RANGE, 1.0),
                moon_scale=load_scale(raw, "moon_scale", *constants.ELEMENT_SCALE_RANGE, 1.0),
                # One-time migration (2026-07-14): the separate weekday
                # and south-slot scales merged into slot_scale — older
                # files inherit their weekday value.
                slot_scale=load_scale(
                    raw, "slot_scale", *constants.ELEMENT_SCALE_RANGE,
                    load_scale(
                        raw, "weekday_scale",
                        *constants.ELEMENT_SCALE_RANGE, 1.0,
                    ),
                ),
                # One-release migration (JEWELS naming sweep, owner ruling
                # 2026-08-06): "ring_letter_scale" is read as the fallback
                # default when the new key is absent.
                ring_jewels_scale=load_scale(
                    raw, "ring_jewels_scale", *constants.ELEMENT_SCALE_RANGE,
                    load_scale(raw, "ring_letter_scale", *constants.ELEMENT_SCALE_RANGE, 1.0),
                ),
                hover_enlarge=load_scale(raw, "hover_enlarge", *constants.HOVER_ENLARGE_RANGE, 1.2),
                # One-release migration (Session 21-D, owner rename for
                # clarity now that RING has its own saturation slider):
                # "palette_saturation" is read as the fallback default
                # when the new key is absent; the file is rewritten
                # under the new key on the next save.
                pointer_saturation=load_scale(
                    raw, "pointer_saturation",
                    *constants.POINTER_SATURATION_RANGE,
                    load_scale(
                        raw, "palette_saturation",
                        *constants.POINTER_SATURATION_RANGE, 1.0,
                    ),
                ),
                ring_saturation=load_scale(
                    raw, "ring_saturation",
                    *constants.RING_SATURATION_RANGE, 1.0,
                ),
                star_alpha=load_alpha(raw, "star_alpha"),
                aura_day_alpha=load_alpha(raw, "aura_day_alpha"),
                aura_twilight_alpha=load_alpha(raw, "aura_twilight_alpha"),
                umbra_alpha=load_scale(raw, "umbra_alpha", 0.0, 1.0, 1.0),
                moon_transit_alpha=load_alpha(raw, "moon_transit_alpha"),
                ghost_alpha=load_alpha(raw, "ghost_alpha"),
                umbra_tint=load_hex(raw, "umbra_tint"),
                umbra_saturation=load_scale(
                    raw, "umbra_saturation", *constants.UMBRA_SATURATION_RANGE, 1.0
                ),
                aura_off_tint=load_hex(raw, "aura_off_tint"),
                hands_tint=load_hex(raw, "hands_tint"),
                hands_saturation=load_scale(
                    raw, "hands_saturation", *constants.HANDS_SATURATION_RANGE, 1.0
                ),
                # One-release migration (JEWELS naming sweep, owner ruling
                # 2026-08-06): "letter_tint" is read as the fallback default
                # when the new key is absent.
                jewels_tint=(
                    load_hex(raw, "jewels_tint")
                    if "jewels_tint" in raw
                    else load_hex(raw, "letter_tint")
                ),
                ring_tint_inner=load_hex(raw, "ring_tint_inner"),
                # RENAMED from `motto_*` (TASK 1, owner ruling 2026-08-06):
                # a stored file's old key is the fallback default when the
                # new one is absent — a saved watch never reads as corrupt
                # or silently drops its Crown Text opacity/size/color.
                crown_text_alpha=load_scale(
                    raw, "crown_text_alpha", 0.0, 1.0,
                    load_scale(raw, "motto_alpha", 0.0, 1.0, 1.0),
                ),
                crown_text_scale=load_scale(
                    raw, "crown_text_scale", *constants.ELEMENT_SCALE_RANGE,
                    load_scale(
                        raw, "motto_scale", *constants.ELEMENT_SCALE_RANGE, 1.0
                    ),
                ),
                crown_text_tint=(
                    load_hex(raw, "crown_text_tint")
                    if "crown_text_tint" in raw
                    else load_hex(raw, "motto_tint")
                ),
                **load_numerals(raw),
                palettes=load_palettes(raw.get("palettes", {})),
                **choices,
            )
            return loaded
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise SettingsCorruptError(self._path, exc) from exc

    def save(self, settings: Settings) -> None:
        payload = {
            "schema_version": settings.schema_version,
            "window": {
                "x": settings.window_x,
                "y": settings.window_y,
                "diameter": settings.diameter,
            },
            "click_through": settings.click_through,
            "ring": settings.ring,
            "ring_tint": settings.ring_tint,
            "ring_finish": settings.ring_finish,
            "custom_rings": [dict(card) for card in settings.custom_rings],
            "ring_two_metals": dict(settings.ring_two_metals),
            "ring_eye_shine": dict(settings.ring_eye_shine),
            "ring_inner": dict(settings.ring_inner),
            "custom_ring_crown_text": dict(settings.custom_ring_crown_text),
            "custom_ring_crown_orientation": dict(
                settings.custom_ring_crown_orientation
            ),
            "ring_crown_location": dict(settings.ring_crown_location),
            "pointer": settings.pointer,
            "umbra_form": settings.umbra_form,
            "umbra_contrast": settings.umbra_contrast,
            "palette_style": settings.palette_style,
            "calendar_mount": settings.calendar_mount,
            "archetype_mode": settings.archetype_mode,
            "archetype_names": settings.archetype_names,
            "cube_look": settings.cube_look,
            "daylight": settings.daylight,
            "pointer_shape": settings.pointer_shape,
            "polygon_curvature": settings.polygon_curvature,
            "polygon_edge": settings.polygon_edge,
            "hide_night_borders": settings.hide_night_borders,
            "earth_label": settings.earth_label,
            "z_mode": settings.z_mode,
            "world_mode": settings.world_mode,
            "solar_rotation": settings.solar_rotation,
            "octa_slot": settings.octa_slot,
            "day_slot_style": settings.day_slot_style,
            "info_slot_style": settings.info_slot_style,
            "info_slot_theme": settings.info_slot_theme,
            "weekday_slot": settings.weekday_slot,
            "third_slot": settings.third_slot,
            "third_slot_style": settings.third_slot_style,
            "third_slot_theme": settings.third_slot_theme,
            "show_third_slot": settings.show_third_slot,
            "earth_style": settings.earth_style,
            "weekday_theme": settings.weekday_theme,
            "subdial_style": settings.subdial_style,
            "subdial_set": settings.subdial_set,
            "metal_shade_gold": settings.metal_shade_gold,
            "metal_shade_bronze": settings.metal_shade_bronze,
            "metal_shade_silver": settings.metal_shade_silver,
            "weekday_roster": settings.weekday_roster,
            "info_slot_roster": settings.info_slot_roster,
            "third_slot_roster": settings.third_slot_roster,
            "art_source": settings.art_source,
            "legend": settings.legend,
            "show_earth": settings.show_earth,
            "show_moon": settings.show_moon,
            "show_weekday": settings.show_weekday,
            "show_pointer": settings.show_pointer,
            "colorful": settings.colorful,
            "show_seconds": settings.show_seconds,
            "show_octa_slot": settings.show_octa_slot,
            "show_weekday_names": settings.show_weekday_names,
            "show_info_slot_names": settings.show_info_slot_names,
            "moon_hidden_alpha": settings.moon_hidden_alpha,
            "hands": settings.hands,
            "theme_rotation_group": settings.theme_rotation_group,
            "theme_rotation_minutes": settings.theme_rotation_minutes,
            "theme_rotation_themes": list(settings.theme_rotation_themes),
            "theme_metals": dict(settings.theme_metals),
            "theme_metal_follow_ring": settings.theme_metal_follow_ring,
            "language": settings.language,
            "era_notation": settings.era_notation,
            "show_era_suffix": settings.show_era_suffix,
            "third_era": settings.third_era,
            "jump_cities": [dict(city) for city in settings.jump_cities],
            "location": {
                "name": settings.city_name,
                "path": list(settings.city_path),
                "latitude": settings.latitude,
                "longitude": settings.longitude,
                "timezone": settings.timezone,
            },
            "earth_scale": settings.earth_scale,
            "moon_scale": settings.moon_scale,
            "slot_scale": settings.slot_scale,
            "ring_jewels_scale": settings.ring_jewels_scale,
            "hover_enlarge": settings.hover_enlarge,
            "pointer_saturation": settings.pointer_saturation,
            "ring_saturation": settings.ring_saturation,
            "star_alpha": settings.star_alpha,
            "aura_day_alpha": settings.aura_day_alpha,
            "aura_twilight_alpha": settings.aura_twilight_alpha,
            "umbra_alpha": settings.umbra_alpha,
            "moon_transit_alpha": settings.moon_transit_alpha,
            "ghost_alpha": settings.ghost_alpha,
            "umbra_tint_mode": settings.umbra_tint_mode,
            "umbra_tint": settings.umbra_tint,
            "umbra_saturation": settings.umbra_saturation,
            "aura_off_tint_mode": settings.aura_off_tint_mode,
            "aura_off_tint": settings.aura_off_tint,
            "hands_tint": settings.hands_tint,
            "hands_saturation": settings.hands_saturation,
            "jewels_tint": settings.jewels_tint,
            "ring_tint_inner": settings.ring_tint_inner,
            "crown_text_alpha": settings.crown_text_alpha,
            "crown_text_scale": settings.crown_text_scale,
            "crown_text_tint": settings.crown_text_tint,
            **save_numerals(settings),
            "palettes": {
                key: list(palette) for key, palette in settings.palettes.items()
            },
        }
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        os.replace(tmp, self._path)

    def quarantine(self) -> Path:
        """Rename the corrupt file to .bak (overwriting an older .bak) so a
        fresh default file can be seeded. Returns the backup path."""
        backup = self._path.with_suffix(".json.bak")
        os.replace(self._path, backup)
        return backup


def _normalized_jump_city(entry: dict) -> dict:
    """One Quick Jump city (Session 16), validated field by field — a
    hand-edited coordinate or timezone must fail HERE, not inside a
    jump (Rule #1)."""
    name = str(entry["name"]).strip()
    if not name:
        raise ValueError("jump city with an empty name")
    latitude = float(entry["latitude"])
    longitude = float(entry["longitude"])
    if not constants.LATITUDE_RANGE[0] <= latitude <= constants.LATITUDE_RANGE[1]:
        raise ValueError(f"jump city {name!r}: latitude {latitude} out of range")
    if not constants.LONGITUDE_RANGE[0] <= longitude <= constants.LONGITUDE_RANGE[1]:
        raise ValueError(f"jump city {name!r}: longitude {longitude} out of range")
    timezone = str(entry["timezone"])
    try:
        ZoneInfo(timezone)
    except Exception as exc:
        raise ValueError(
            f"jump city {name!r}: timezone {timezone!r} unknown: {exc}"
        ) from exc
    return {
        "name": name,
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
    }


def rotation_themes(settings: "Settings") -> tuple[str, ...]:
    """The themes the rotation cycles (owner 2026-07-14): a kinship
    GROUP straight from the Weekday menu grouping, the custom checkbox
    list — or nothing at all ("none", the canon: Planets forever)."""
    group = settings.theme_rotation_group
    if group == "custom":
        return settings.theme_rotation_themes
    for title, keys in pantheon.WEEKDAY_MENU_GROUPS:
        if title == group:
            return keys
    return ()


def slot_layout_target(settings: "Settings") -> int:
    """The FACE LAYOUT the current flags encode, 0-3 (Watch Face R-17 /
    Ctrl+N's `_cycle_slots`): Full face / 1 / 2 / 3 subdials. The SAME
    "strictly 1 → 2 → 3, never a gap" arithmetic
    `render.slot_layout.enabled_slots` enforces at render time — this
    pure reader lets both the controller's cycling shortcut and the
    Watch Face FACE LAYOUT row derive the same number from one place
    (Rule #5) instead of each re-deriving it."""
    return (
        int(settings.show_weekday)
        + int(settings.show_weekday and settings.show_octa_slot)
        + int(
            settings.show_weekday and settings.show_octa_slot
            and settings.show_third_slot
        )
    )


def replace(settings: Settings, **changes) -> Settings:
    """Convenience wrapper over dataclasses.replace for frozen Settings."""
    return dataclasses.replace(settings, **changes)
