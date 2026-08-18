"""One visual choice in, a rebuilt skin out.

A mixin of [WatchController](controller.md): every `_set_*` here writes
ONE (or one small family of) `Settings` field(s) and reinstalls the skin
through `self._install_skin(build_skin(...))`. It is the single writer
the menu, the Watch Face window and the shortcuts all share — none of
them touches `Settings` directly.
"""

import random

from app.skin_builder import build_skin
from app.settings_store import replace, rotation_themes
from config.registry.slots import SLOT_KEYS


def _next_rotation_theme(current: str, selected: tuple[str, ...]) -> str:
    """The theme AFTER `current` in the rotation list (cyclic); a
    current theme outside the list starts it from the top."""
    if current in selected:
        return selected[(selected.index(current) + 1) % len(selected)]
    return selected[0]


class _DisplaySettingsMixin:
    """DisplaySettingsMixin — see the module docstring."""

    def _set_ring(self, ring: str) -> None:
        if ring == self._settings.ring:
            return
        self._settings = replace(self._settings, ring=ring)
        self._install_skin(build_skin(self._settings, self._active_location_display))
        self._flush_position()
        # A ring switch may change eligibility for other per-preset
        # toggles — re-gate in place, the same stay-open pattern every
        # other menu re-sync uses.
        self._refresh_menu_gating()

    def _set_ring_eye_shine(self, checked: bool) -> None:
        """DOLLAR/EYE round (owner decree 2026-07-27): the active
        preset's own Eye-of-Providence rays choice, stored keyed by
        preset name (`Settings.ring_eye_shine`)."""
        shine = dict(self._settings.ring_eye_shine)
        shine[self._settings.ring] = checked
        self._settings = replace(self._settings, ring_eye_shine=shine)
        self._install_skin(build_skin(self._settings, self._active_location_display))
        self._flush_position()

    def _set_ring_inner(self, inner: str) -> None:
        """THE COMPOSITIONAL RING MODEL (owner decree 2026-08-05): the
        active preset's own inner-band choice, stored keyed by preset
        name (`Settings.ring_inner`) — the outer stays locked (bundled) or fixed at creation
        (custom), only the inner is ever swapped in place."""
        inner_choices = dict(self._settings.ring_inner)
        inner_choices[self._settings.ring] = inner
        self._settings = replace(self._settings, ring_inner=inner_choices)
        self._install_skin(build_skin(self._settings, self._active_location_display))
        self._flush_position()

    def _set_custom_ring_crown_text(self, text: str) -> None:
        """CROWN TEXT (owner decree 2026-08-05): a custom ring's own
        free-typed crown inscription, stored keyed by ring name
        (`Settings.custom_ring_crown_text`) — empty clears it (no
        crown text drawn)."""
        texts = dict(self._settings.custom_ring_crown_text)
        if text:
            texts[self._settings.ring] = text
        else:
            texts.pop(self._settings.ring, None)
        self._settings = replace(self._settings, custom_ring_crown_text=texts)
        self._install_skin(build_skin(self._settings, self._active_location_display))
        self._flush_position()

    def _set_custom_ring_crown_orientation(self, orientation: str) -> None:
        """CROWN TEXT orientation (owner decree 2026-08-05): "top"
        (arcing from 12 upward) or "bottom", stored keyed by ring name
        (`Settings.custom_ring_crown_orientation`)."""
        orientations = dict(self._settings.custom_ring_crown_orientation)
        orientations[self._settings.ring] = orientation
        self._settings = replace(
            self._settings, custom_ring_crown_orientation=orientations
        )
        self._install_skin(build_skin(self._settings, self._active_location_display))
        self._flush_position()

    def _set_ring_crown_location(self, checked: bool) -> None:
        """THE LOCATION CROWN (RING VERDICTS round, owner decree
        2026-08-05): the active ring's own choice, stored keyed by ring
        name — available for a bundled
        preset (replacing its own crown text) or a custom ring (replacing
        its typed crown text) alike."""
        choices = dict(self._settings.ring_crown_location)
        choices[self._settings.ring] = checked
        self._settings = replace(self._settings, ring_crown_location=choices)
        self._install_skin(build_skin(self._settings, self._active_location_display))
        self._flush_position()

    def _set_hands(self, hands: str) -> None:
        if hands == self._settings.hands:
            return
        self._settings = replace(self._settings, hands=hands)
        self._install_skin(build_skin(self._settings, self._active_location_display))
        self._flush_position()

    def _metal_updates(self, theme: str, metal: str | None) -> dict:
        """The settings delta of an EXPLICIT metal pick (either slot's
        Weekday submenu): remembers the theme's metal and releases
        follow-the-ring, otherwise the ring finish would silently
        override it. Empty when no metal was chosen."""
        if metal is None:
            return {}
        metals = dict(self._settings.theme_metals)
        metals[theme] = metal
        return {"theme_metals": metals, "theme_metal_follow_ring": False}

    def _set_slot(
        self, index: int, mode: str, style: str | None = None,
        theme: str | None = None, metal: str | None = None,
        roster: str | None = None,
    ) -> None:
        """Slot `index`'s content plus its OWN style/theme/metal/roster
        in one click (owner 2026-07-12: the slots are independent —
        setting one never touches another's look).

        THE one writer for all three. Which `Settings` fields it writes
        is `SLOT_KEYS[index]`, not an `if index ==` chain: the bodies of
        the old `_set_south_slot`/`_set_third_slot` were identical but
        for four strings (clone C4, OOP audit 2026-08-18), and the day
        slot's `_set_weekday_badge`/`_set_weekday_theme` were the same
        shape again with a third set."""
        keys = SLOT_KEYS[index]
        updates: dict = {keys["mode"]: mode}
        if style is not None:
            updates[keys["style"]] = style
        if theme is not None:
            updates[keys["theme"]] = theme
            updates.update(self._metal_updates(theme, metal))
        if roster is not None:
            updates[keys["roster"]] = roster
        self._settings = replace(self._settings, **updates)
        self._install_skin(build_skin(self._settings, self._active_location_display))
        self._flush_position()

    def _set_weekday_theme(
        self, theme: str, metal: str | None = None,
        roster: str | None = None,
    ) -> None:
        """Day slot back to the WEEKDAY BODIES wearing `theme` (owner
        menu 2026-07-12: the theme list lives inside Day slot ▸ Weekday,
        so picking a theme also picks the mode; bronze-plate themes
        pick their metal in the same click, pantheon themes their
        roster). The named menu action; `_set_slot` does the writing."""
        self._set_slot(1, "weekday", theme=theme, metal=metal, roster=roster)

    def _configure_theme_rotation(self) -> None:
        """Start/stop the rotation timer per the settings (called at
        startup and after every Settings OK). The GROUP dropdown picks
        what cycles (owner 2026-07-14: a kinship family, the custom
        checkbox list, or none at all); the ORDER is shuffled fresh
        each time (owner spec 2026-07-12: never the same sequence
        twice)."""
        self._rotation_order = list(rotation_themes(self._settings))
        random.shuffle(self._rotation_order)
        if len(self._rotation_order) >= 2:
            self._theme_rotation_timer.start(
                self._settings.theme_rotation_minutes * 60 * 1000
            )
        else:
            self._theme_rotation_timer.stop()

    def _rotate_theme(self) -> None:
        """One rotation step: the next theme of the SHUFFLED order goes
        live (and the menu checkmarks follow)."""
        self._set_display_choice(
            "weekday_theme",
            _next_rotation_theme(
                self._settings.weekday_theme,
                tuple(self._rotation_order),
            ),
        )
        # The timer can fire while the user is browsing the menu —
        # close and RETAIN the replaced one so Qt never deletes a
        # visible popup (stay-open menus, owner 2026-07-13).
        retired = self._menu
        self._menu = self._build_menu()
        self._widget.set_menu(self._menu)
        self._widget.set_show_action(self._show_action)
        self._tray.set_menu(self._menu)
        retired.close()
        self._retired_menu = retired

    def _set_display_choice(self, key: str, value) -> None:
        """Shared setter behind every display choice: persist and
        REBUILD the render config from scratch — a bare scalar replace
        is not enough for choices that swap assets (the weekday theme
        replaces the body images inside apply_display_settings; a
        scalar-only update left the planets on screen — owner bug
        report, FINAL.txt #6)."""
        if getattr(self._settings, key) == value:
            return
        self._settings = replace(self._settings, **{key: value})
        self._install_skin(build_skin(self._settings, self._active_location_display))
        self._flush_position()
        if key in (
            "pointer", "show_weekday", "show_pointer",
            "show_octa_slot", "show_third_slot", "archetype_mode",
        ):
            # These move the whole enablement matrix (the South slot's
            # availability, the weekday-badge availability, Aurora's
            # image-only modes, the Solar rotation lock, the enable
            # chain and the slot check marks) — re-gray the gated
            # entries IN PLACE (owner 2026-07-13: switching the
            # pointer or an element must not close the open menu).
            # `show_weekday_names` dropped OUT of this list (Session
            # 21-C): the menu twin it needed resyncing against is gone —
            # Archetype names is its own Settings switch now
            # (`archetype_names`), so the buried Weekday ▸ Names toggle
            # needs no special re-gating beyond the ordinary slot gating.
            self._refresh_menu_gating()

    def _set_earth_label(self, mode: str, checked: bool) -> None:
        """FOUR mutually exclusive Earth label options (owner 2026-07-18,
        ROADMAP 15h: Date / Weekday / Date & Weekday / Full Date, stored
        as the single `earth_label` enum): `checked=True` selects `mode`
        outright, `checked=False` (clicking the ALREADY active pill
        again) turns the label off entirely. One skin install for the
        whole change; the Design window's own `refresh()` re-reads the
        result fresh (R5 MENU REWORK — no controller-held toggle
        widgets to mirror any more)."""
        new_mode = mode if checked else "off"
        if self._settings.earth_label != new_mode:
            self._settings = replace(self._settings, earth_label=new_mode)
            self._install_skin(build_skin(self._settings, self._active_location_display))
        self._flush_position()

    def _set_visible(self, key: str, checked: bool) -> None:
        """One Visible toggle (owner 2026-07-17; renamed from Elements,
        R5 MENU REWORK item E): the shared display setter, then the
        top-level Visible check follows (it shows only while every
        entry is on)."""
        self._set_display_choice(key, checked)
        self._refresh_visible_check()

    def _refresh_visible_check(self) -> None:
        """The Visible ordinal is checked ONLY when every entry in the
        dropdown is on (owner 2026-07-17, ROADMAP 15e)."""
        self._visible_menu_action.setChecked(
            all(getattr(self._settings, key) for _, key in self._visible_toggles)
        )

    def _toggle_all_visible(self) -> None:
        """Clicking the Visible top-level entry (owner 2026-07-17): all
        on → all off, otherwise → all on. One skin install for the whole
        batch; the child checkboxes and the gating follow."""
        keys = [key for _, key in self._visible_toggles]
        target = not all(getattr(self._settings, key) for key in keys)
        changes = {
            key: target for key in keys if getattr(self._settings, key) != target
        }
        if not changes:
            self._refresh_visible_check()
            return
        self._settings = replace(self._settings, **changes)
        for action, key in self._visible_toggles:
            # Mirror the children without re-entering their handlers.
            action.blockSignals(True)
            action.setChecked(target)
            action.blockSignals(False)
        self._install_skin(build_skin(self._settings, self._active_location_display))
        # Toggling the Pointer/Seconds elements moves the gating matrix.
        self._refresh_menu_gating()
        self._refresh_visible_check()
        self._flush_position()
