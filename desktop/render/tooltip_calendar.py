"""Every hover the CALENDAR answers — one of the four families
`render/tooltip_composer.py` was cut into (owner 2026-08-19).

The Calendar pointer's own wedges (zodiac, Slavic months, the Chinese
mount) with the mount seats behind them, the weekday bodies, the tick
readout, and the three sign readings the seats print — zodiac, Chinese
and the ascendant.

**How the dial is held: it is NOT.** This is a MIXIN on
`TooltipComposer` — see `render/tooltip_sky.py` for the whole
argument. One holder of the dial, `self._dial`, and every method here
reads it live.

`_MONTHS` and `_MONTHS_SHORT` live here — month names are calendar
vocabulary — and the composer imports them for its two shared helpers
`_month()` / `_month_short()`, which it keeps because every family
formats a date.

**The door is still `render/tooltip_composer.py`.**

Layer: render. Documentation: __about/tooltip_calendar.md.
"""

import html
import math
from datetime import timedelta

from PySide6.QtCore import QPointF

from config import (
    calendar_mounts,
    complications,
    defaults,
    dial,
    encyclopedia_ui,
    pantheon,
    paths,
    pointer_geometry,
    registry,
    ring,
    sky,
    zodiac,
)
from config.registry import week as week_registry
from core.moon import nominal_illumination, phase_name
from core.year_wheel import instant_at_marker_angle, zodiac_span
from render.article_html import (
    article_body_html, article_html, centered, centered_html, hover_badge,
    hover_title, teaser,
)
from render.asset_recolor import metal_variant_file
from render.asset_variants import scaled_variant_file
from render.calendar_mount import chinese_mount_dimmed_index
from render.painting import dial_point


_MONTHS = (
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
)


_MONTHS_SHORT = (
    "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
    "Oct", "Nov", "Dec",
)


class CalendarTooltips:
    def _calendar_tooltip(self, point: QPointF, radius: float) -> str | None:
        """The Calendar wedge hover (owner 2026-07-16, kept modest —
        full articles arrive with the archetype engine). Almanac: the
        month name and the wedge's Chinese double-hour animal with its
        clock span, above OUR Chinese COLORED medallion of that animal.
        Zodiac: the sign name with its date span (the existing
        year-wheel cusps), above the sign's COLORED LOGO art — never a
        unicode glyph standing in for the art (owner 2026-07-16, ROADMAP
        queue #7)."""
        from render.calendar_mount import calendar_wheel
        from render.subdial import octa_slot_art

        distance = math.hypot(point.x(), point.y())
        outer = radius * self._dial.interior_hit(self._dial.skin.background.aura_radius_fraction)
        if not (radius * self._dial.interior_hit(0.08) <= distance <= outer):
            return None
        theta = self._dial.world_theta(point)
        step = pointer_geometry.CALENDAR_WEDGE_DEG
        day = self._dial.day
        if calendar_wheel(self._dial.skin) == "almanac":
            index = int((theta + step / 2.0) // step) % 12
            month = (index + 5) % 12 + 1
            animal = zodiac.CHINESE_ANIMALS[(index - 6) % 12]
            center_hour = (2 * index - 12) % 24
            start_hour, end_hour = (center_hour - 1) % 24, (center_hour + 1) % 24
            art = octa_slot_art(
                complications.CHINESE_STYLE_ART_DIRS["colored"], animal
            )
            return hover_badge(art) + centered_html(
                f"<b>{html.escape(self._tr(_MONTHS[month - 1]))}</b>",
                "",
                html.escape(self._tr(animal)),
                f"{start_hour:02d}:00 - {end_hour:02d}:00",
            )
        # Zodiac: the sign whose wedge starts at this angle (south mirrors
        # the wheel, as the star-arm hover does).
        start_angle = int(theta // step) * step
        if day.southern_hemisphere:
            start_angle = (start_angle + 180.0) % 360.0
        return self._zodiac_wedge_html(int(start_angle) // 30)

    def _zodiac_wedge_html(self, index: int) -> str:
        """Sign name + date span + the COLORED badge for the FIXED
        `zodiac.ZODIAC_SIGNS[index]` wedge identity — factored out of
        `_calendar_tooltip`'s own zodiac branch (Rule #5) so the mounted
        zodiac mark hover (`_calendar_mount_tooltip`, drawn on this exact
        wedge, never hemisphere-mirrored) speaks the identical text the
        background wedge hover already does."""
        from render.subdial import octa_slot_art

        day = self._dial.day
        name, symbol = zodiac.ZODIAC_SIGNS[index]
        start, end = zodiac_span(
            day.year_anchors, index * pointer_geometry.CALENDAR_WEDGE_DEG
        )
        start = start.astimezone(day.tzinfo)
        last = end.astimezone(day.tzinfo) - timedelta(days=1)
        art = octa_slot_art(complications.ZODIAC_STYLE_ART_DIRS["colored"], name)
        return hover_badge(art) + centered_html(
            f"<b>{html.escape(symbol)} {html.escape(self._tr(name))}</b>",
            f"{self._ord(start.day)} {html.escape(self._month(start))} - "
            f"{self._ord(last.day)} {html.escape(self._month(last))}",
        )

    def _months_wedge_html(self, index: int) -> str:
        """The mounted Slavic-months mark's hover (owner spec: "month
        name + gloss"): the Croatian proper noun as the bold title, the
        English gloss beneath, above the plate art — graceful-absent
        (owner R7b contract) via the SAME `hover_badge` empty-string
        rule every other emblem uses until the prompt sheet lands."""
        month = (index + 5) % 12 + 1
        croatian, gloss, stem, _gregorian = next(
            entry for entry in calendar_mounts.SLAVIC_MONTHS if entry[3] == month
        )
        art = paths.art_file(defaults.MONTHS_ART_DIR / f"{stem}.png")
        art = art if art.exists() else None
        return hover_badge(art) + centered_html(
            f"<b>{html.escape(self._tr(croatian))}</b>",
            html.escape(self._tr(gloss)),
        )

    def _chinese_mount_wedge_html(self, index: int) -> str:
        """The mounted Chinese MONTHLY animal's hover (owner R12: "animal
        + its month"): the animal's name over its own colored badge,
        its Gregorian month beneath — the SAME register the year-zodiac
        Chinese slot hover already reads. While this exact wedge is the
        one lending its month to The Cat (`chinese_mount_dimmed_index`),
        a short note says so."""
        from render.subdial import octa_slot_art

        gregorian = (index + 5) % 12 + 1
        animal = zodiac.CHINESE_MONTH_BRANCH_ANIMALS[gregorian]
        art = octa_slot_art("zodiac/chinese/primary/colored", animal)
        # THE BRANCH'S TRUE SPAN (owner 2026-08-05): the wedge is a
        # Gregorian seat, but the branch itself opens on its own solar
        # term and closes the day before the next — so the hover says
        # from when to when, and says "approx." because the term drifts
        # about a day with the leap cycle.
        (open_m, open_d), (close_m, close_d), term = (
            zodiac.chinese_branch_span(gregorian)
        )
        lines = [
            f"<b>{html.escape(self._tr(animal))}</b>",
            html.escape(self._tr(_MONTHS[gregorian - 1])),
            "≈ {0} {1} – {2} {3} · {4}".format(
                open_d, html.escape(self._tr(_MONTHS_SHORT[open_m - 1])),
                close_d, html.escape(self._tr(_MONTHS_SHORT[close_m - 1])),
                html.escape(term),
            ),
        ]
        if self._dial.day is not None and index == chinese_mount_dimmed_index(self._dial.day):
            lines.append(
                html.escape(self._tr("lending its month to The Cat this year"))
            )
        return hover_badge(art) + centered_html(*lines)

    def _mount_seat_html(self, mount: str, index: int) -> str:
        """The generic mounted-seat hover: the member's name over its own
        plate, graceful-absent through the SAME `hover_badge`
        empty-string rule every other emblem uses. Serves every roster
        that has nothing richer to say than its name (the Emotions
        Dozen, the Month Dozen) — the three sets that DO (a sign's dates,
        a month's gloss, an animal's month) keep their own writers
        above."""
        from render.calendar_mount import calendar_mount_entries

        daylight = self._dial.tick.is_daylight if self._dial.tick is not None else True
        name, art = calendar_mount_entries(mount, daylight)[index]
        # A TWO-DEPICTION seat names BOTH faces (owner ruling 2026-08-05):
        # the dial can only show one at a time, so the hover is where a
        # vice is read at noon. The SHOWN face leads, its opposite follows.
        other = calendar_mounts.CALENDAR_MOUNTS[mount].paint
        if other is not None:
            opposite = (
                other.members[index] if daylight
                else calendar_mounts.CALENDAR_MOUNTS[mount].members[index]
            )
            title = (
                f"<b>{html.escape(self._tr(name))}</b>"
                f" · {html.escape(self._tr(opposite))}"
            )
        else:
            title = f"<b>{html.escape(self._tr(name))}</b>"
        return hover_badge(art) + centered_html(title)

    def _calendar_mount_tooltip(self, point: QPointF, radius: float) -> str | None:
        """The mounted set's seat under the cursor (DESIGN ZODIAC law,
        R9a round; GENERALIZED 2026-07-29) — a small circular target at
        CALENDAR_MOUNT_RADIUS_FRACTION, outranking the broader
        whole-wedge hover beneath it (checked first in `_tooltip_at`).
        Off while no set is mounted. The seat COUNT comes from the
        roster's own registry entry, so a 24-set is hit-tested on all
        twenty-four of its seats without a second loop."""
        mount = self._dial.skin.calendar_mount
        if mount == "off":
            return None
        from render.calendar_mount import calendar_mount_angle, calendar_mount_mark_height
        from render.painting import dial_point

        mount_radius = radius * self._dial.interior_hit(calendar_mounts.CALENDAR_MOUNT_RADIUS_FRACTION)
        hit_radius = calendar_mount_mark_height(mount, radius) / 2.0
        for index in range(calendar_mounts.CALENDAR_MOUNTS[mount].seats):
            center = dial_point(calendar_mount_angle(mount, index), mount_radius)
            dx, dy = point.x() - center.x(), point.y() - center.y()
            if dx * dx + dy * dy <= hit_radius * hit_radius:
                if mount == "zodiac":
                    return self._zodiac_wedge_html(index)
                if mount == "chinese":
                    return self._chinese_mount_wedge_html(index)
                if mount == "months":
                    return self._months_wedge_html(index)
                return self._mount_seat_html(mount, index)
        return None

    def _weekday_tooltip(
        self, body: str, active: bool, theme: str | None = None,
        slot_metal: str | None = None, roster: str | None = None,
    ) -> str:
        """The body's ARTICLE — its themed art on top, then the entity
        NAME as a bigger title (owner spec 2026-07-11: the god / planet
        / calling the medallion shows), base plus the paragraph of the
        ACTIVE (pointer, palette) combination; the active day adds
        "Thursday, 9th July 2026" under the name (owner spec), ghosts
        show name and article alone. `theme` overrides the main theme
        (the info slot's second weekday, owner 2026-07-12). The SUN
        shows BOTH Sunday plates side by side wherever it appears as
        one image (owner 2026-07-13) — the extended base text already
        tells the two faces."""
        theme = theme or self._dial.skin.weekday_theme
        article_set = registry.ARTICLES[theme]
        article_body = body
        # THE UNIVERSAL ROTATION CONVENTION (weekday ALT ROTATION round
        # 2026-07-20/21): `self._dial.day` is None before the first tick
        # (this method is unit-tested directly, `self._dial.day` unset —
        # `test_seated_slot_wears_its_own_roster`) — the SAME graceful-
        # absent guard `_center_ninth_alt` already uses for the identical
        # hazard.
        on_date = self._dial.day.local_date if self._dial.day is not None else None
        # The weekday-set shortcut holds only while the ROSTER matches
        # too (owner 2026-07-15: slot 1 Greek Planetary beside slot 2
        # Greek Pantheon — same theme, two casts); a caller that names
        # no roster follows the set as dressed.
        same_unit = theme == self._dial.skin.weekday_theme and roster in (
            None,
            "pantheon"
            if self._dial.skin.weekday_set.body_articles is not None
            else "planetary",
        )
        if same_unit and self._dial.skin.weekday_set.body_articles is not None:
            # The PANTHEON roster (owner 2026-07-15): each seat's
            # article follows the FIGURE actually shown there —
            # fallen-back seats keep the planetary text.
            article_set, article_body = (
                self._dial.skin.weekday_set.body_articles[body]
            )
        if same_unit:
            display_name = self._dial.skin.weekday_set.body_names[body]
            image = self._dial.skin.weekday_set.bodies.get(body)
            metal = self._dial.skin.weekday_set.metal
        elif theme == "planets":
            display_name = defaults.DEFAULT_SKIN.weekday_set.body_names[body]
            image = pantheon.weekday_theme_body_art(
                "planets", body, on_date=on_date,
            )
            metal = None
        else:
            # A SEATED slot's SECOND weekday: resolve the art exactly
            # like its layer — the slot's OWN metal, colored/ included
            # (owner bug 2026-07-13: the legend always showed bronze),
            # and the slot's OWN roster (owner 2026-07-15): a pantheon
            # seat speaks the figure actually shown there, a seat
            # whose plate has not landed keeps the planetary bundle
            # whole — the same safety law as the classic unit.
            metal = (
                slot_metal
                if theme in registry.METAL_THEMES
                and slot_metal in defaults.METAL_SWAP_TARGETS
                else None
            )
            seat = (
                pantheon.pantheon_seat(theme, body)
                if roster == "pantheon" else None
            )
            if seat is not None:
                image, display_name, (article_set, article_body) = seat
                if on_date is not None:
                    image = pantheon.rotating_art_file(image, on_date) or image
            else:
                display_name = pantheon.WEEKDAY_THEME_NAMES[theme][body]
                # THE ONE weekday-body resolver (Rule #5 — shared with
                # `app.controller` and `render.weekday_body._draw_weekday_slot`;
                # `on_date` wires THE UNIVERSAL ROTATION CONVENTION so
                # the legend never shows a different day's pick than the
                # slot it describes).
                image = pantheon.weekday_theme_body_art(
                    theme, body, on_date=on_date,
                    colored=(
                        slot_metal == "colored"
                        and theme in registry.METAL_THEMES
                    ),
                )
        if same_unit and image is not None and on_date is not None:
            # `spec.bodies` is BAKED at settings-apply time (never per
            # day) — re-resolve the live rotation on top of it, exactly
            # like `render.weekday_body.draw_weekday_body`'s own override.
            image = pantheon.rotating_art_file(image, on_date) or image
        image = metal_variant_file(image, metal)
        if body == "sun":
            # The dual center's TWO plates in one legend (owner
            # 2026-07-13: "u prism i trinity treba legend sa 2 slike").
            if same_unit:
                dual_image = self._dial.skin.weekday_set.dual_asset
            else:
                # ONE DOOR for "which Sunday does this roster wear"
                # (`pantheon.weekday_dual_rel`, extracted 2026-08-15):
                # the pantheon dual wins only when its plate is on
                # disk, otherwise the WHOLE planetary pair stays (the
                # classic unit's Sunday law). The Artwork previews ask
                # the same door — they used to ask nothing at all and
                # drew the planetary dual for both rosters.
                dual_rel = (
                    pantheon.weekday_dual_rel(theme, roster)
                    or pantheon.WEEKDAY_DUAL_FILES[theme]
                )
                dual_image = pantheon.weekday_art(f"{dual_rel}.png")
            image = (image, metal_variant_file(dual_image, metal))
        node = self._dial.symbolism.article(article_set, article_body)
        text = node["base"]
        variant = node["variants"].get(self._combo_key())
        if variant:
            text += "\n\n" + variant
        title = (
            f"<span style='font-size: {encyclopedia_ui.ARTICLE_TITLE_PX}px'>"
            f"<b>{html.escape(self._tr(display_name))}</b>"
            f"</span>"
        )
        if active:
            date = self._dial.day.local_date
            title += (
                f"<br/>{html.escape(self._tr(week_registry.WEEKDAY_FULL_NAMES[body]))}, "
                f"{self._ord(date.day)} {html.escape(self._month(date))} "
                f"{self._year(date)}"
            )
        else:
            # THE WEEKDAY-TITLE LAW (owner, repeated many times —
            # CUBE.md §Display and Legend Laws): every weekday-bound
            # badge names ITS day beside the title; the active body's
            # full date line above already carries it.
            title += (
                f"<br/>"
                f"{html.escape(self._tr(week_registry.WEEKDAY_FULL_NAMES[body]))}"
            )
        return article_html(image, title, text, tr=self._tr)

    def _tick_tooltip(self, point: QPointF, radius: float) -> str | None:
        """The ring tick band (owner spec 2026-07-12, organized to the
        DOMY letters, formatting round two): hovering any of the 360
        arrows reads that ANGLE on every wheel in titled sections
        separated by blank lines — DAY (labeled time and degree plus
        the day-period word), YEAR (labeled date with the anchor event,
        labeled season with the day/week ordinals) and MOON (the
        running lunation, then the cycle reading at that angle — new
        at the top, full at the bottom, as the marker rides)."""
        distance = math.hypot(point.x(), point.y())
        theta = self._dial.world_theta(point)
        # The unlocked hidden mode (owner 2026-07-16, top-only round):
        # ONLY the 12h ring LETTER — M on DOMY, whatever glyph another
        # ring seats there — opens the Four Greetings. Only the letter
        # band OUTSIDE the tick scale: the ticks at that angle keep
        # their own day/year/moon reading. The 24h (Omega) letter used
        # to share this trigger; it now belongs to the reveal-week
        # double-click instead (see Compositor.hit_omega).
        half = encyclopedia_ui.GREETINGS_JEWEL_HALF_DEG
        # THE INWARD-GROWTH LAW (owner verdict 2026-08-09): the jewel
        # band rides the hour band's centreline, so its inner boundary
        # moves inward with it; the tick reading zone below scales with
        # the interior world. Both are identity at ring_size <= 1.0.
        in_jewel_band = (
            radius * self._dial.band_hit(dial.TICK_HOVER_OUTER_FRACTION)
            < distance
            <= radius * self._dial.band_hit(encyclopedia_ui.GREETINGS_JEWEL_OUTER_FRACTION)
        )
        # The 12h seat is a JEWEL, so the trigger is read in the jewels'
        # own frame (the identity in `all_turn`).
        jewel_theta = self._dial.jewel_theta(theta)
        if (
            in_jewel_band
            and self._dial.hidden_unlocked
            and (jewel_theta <= half or jewel_theta >= 360.0 - half)
        ):
            return self._greetings_tooltip()
        # The per-letter HOVER LEGEND (owner ROADMAP 15b, "malo legende
        # oko tih naših odabira"): a ring preset may carry a `legend`
        # per position (Database/ring_presets.json — the Dollar, DOMY
        # and LOOP today, CROSS-WORDS round 2026-07-27) — what that
        # letter stands for, quoted verbatim from CANON.md's Banknote
        # table. Checked on every letter the active preset seats,
        # independent of the hidden-mode unlock (unlike the Four
        # Greetings, this is not an Easter egg); a preset without a
        # legend (The One/Templar, every custom ring) falls through
        # unchanged.
        if in_jewel_band:
            legend = self._ring_jewel_legend_tooltip(theta, half)
            if legend is not None:
                return legend
        # The arc WORDS answer too (WORD-HOVER round, owner 2026-07-27:
        # "HOVER tekst osim na slova treba i na reči") — the band just
        # outside the ring where the crown-text/station words draw.
        word_legend = self._ring_word_legend_tooltip(theta, distance, radius)
        if word_legend is not None:
            return word_legend
        live_crown = self._live_crown_tooltip(theta, distance, radius)
        if live_crown is not None:
            return live_crown
        if not (
            radius * self._dial.interior_hit(dial.TICK_HOVER_INNER_FRACTION)
            <= distance
            <= radius * self._dial.band_hit(dial.TICK_HOVER_OUTER_FRACTION)
        ):
            return None
        minutes = round((((theta - 180.0) % 360.0) / 15.0) * 60) % (24 * 60)
        line_time = (
            f"{self._label('Time')} {minutes // 60:02d}:{minutes % 60:02d} - "
            f"{self._label('Angle')} {theta:.1f}° - "
            + html.escape(self._period_word(minutes))
        )

        day = self._dial.day
        instant = instant_at_marker_angle(
            day.year_anchors, theta, day.southern_hemisphere
        )
        local = instant.astimezone(day.tzinfo)
        line_date = (
            f"{self._label('Date')} {self._ord(local.day)} "
            f"{html.escape(self._month(local))} {self._year(local)}"
        )
        event = next(
            (
                name for when, name in day.season_events
                if when.astimezone(day.tzinfo).date() == local.date()
            ),
            None,
        )
        if event is not None:
            line_date += f" - {html.escape(self._tr(event))}"
        line_year = html.escape(
            self._tr("{ordinal} Day - {ordinal_week} Week")
        ).format(
            ordinal=self._ord(local.timetuple().tm_yday),
            ordinal_week=self._ord(local.isocalendar().week),
        )
        if day.zone != "tropics":
            passed = [
                (when, name) for when, name in day.season_events
                if when <= instant
            ] or [day.season_events[0]]
            season = max(passed)[1].split()[0]
            line_year = (
                f"{self._label('Season')} "
                f"{html.escape(self._tr(season))} - {line_year}"
            )

        fraction = theta / 360.0
        # Which lunation the hovered ANGLE belongs to (owner logic
        # 2026-07-13): the cycle runs one full ring from the 12h New
        # Moon point. Moon on the LEFT (second half) → the right half
        # of the ring, past 12h again, is already the NEXT moon; Moon
        # on the RIGHT (first half) → the whole ring is the current
        # one (behind it the young past, ahead of it the rest).
        next_cycle = self._dial.tick.moon_fraction > 0.5 and fraction < 0.5
        cycle_day = f"{fraction * sky.SYNODIC_MONTH_DAYS:.1f}"
        line_moon = (
            f"{self._label('Illumination')} "
            f"{nominal_illumination(fraction) * 100:.1f}% - "
            f"{html.escape(self._tr(phase_name(fraction)))} - "
            + html.escape(
                self._tr("Day {day} of {total}").format(
                    day=cycle_day, total=sky.SYNODIC_MONTH_DAYS
                )
            )
        )
        return centered_html(
            f"<b>{html.escape(self._tr('Day'))}</b>",
            line_time,
            "",
            f"<b>{html.escape(self._tr('Year'))}</b>",
            line_date,
            line_year,
            "",
            f"<b>{html.escape(self._tr('Moon'))}</b>",
            self._lunation_ordinal(next_cycle=next_cycle),
            line_moon,
        )

    def _zodiac_line(self) -> str:
        """"♋ Cancer — 21 Jun – 22 Jul" (sign with its date span)."""
        day = self._dial.day
        last = day.zodiac_end - timedelta(days=1)    # end is the next sign's first day
        return (
            f"{day.zodiac_symbol} {self._tr(day.zodiac_name)} — "
            f"{day.zodiac_start.day} {self._month_short(day.zodiac_start)} – "
            f"{last.day} {self._month_short(last)}"
        )

    def _zodiac_image_trio(self, style: str | None, sign: str) -> str:
        """The Astrology hover's image row (owner 2026-07-13): the
        ACTIVE style's art LARGE in the middle — filling the image
        band — and the two remaining styles small at its sides (text
        mode leads with the colored logo)."""
        from render.subdial import octa_slot_art

        dirs = complications.ZODIAC_STYLE_ART_DIRS
        main_style = style if style in dirs else "colored"
        sides = {
            "logo": ("sign", "constellation"),
            "colored": ("sign", "constellation"),
            "sign": ("logo", "constellation"),
            "constellation": ("sign", "logo"),
        }[main_style]
        side_px = round(
            encyclopedia_ui.ASTRO_MAIN_IMAGE_PX * encyclopedia_ui.ASTRO_SIDE_IMAGE_FRACTION
        )

        def img(folder: str, px: int) -> str:
            path = octa_slot_art(folder, sign)
            if path is None or not path.exists():
                return ""
            small = scaled_variant_file(path, 2 * px)
            return f"<img src='{small.as_uri()}' width='{px}' align='middle'/>"

        return (
            "<div align='center'>"
            + img(dirs[sides[0]], side_px)
            + img(dirs[main_style], encyclopedia_ui.ASTRO_MAIN_IMAGE_PX)
            + img(dirs[sides[1]], side_px)
            + "</div>"
        )

    def _zodiac_text(self, style: str | None = None) -> str:
        """Zodiac slot hover (owner rework, formatting 2026-07-13):
        the sign name as the bold title with its span beneath, the
        image TRIO led by the active style, then the sign's ARTICLE
        (base only — the palette variants speak in hexa arm colors)."""
        day = self._dial.day
        last = day.zodiac_end - timedelta(days=1)
        header = hover_title(html.escape(self._tr(day.zodiac_name))) + centered(
            f"{day.zodiac_start.day} {self._month_short(day.zodiac_start)} – "
            f"{last.day} {self._month_short(last)}",
        )
        article = self._dial.symbolism.zodiac_article(day.zodiac_name)
        return (
            header
            + self._zodiac_image_trio(style, day.zodiac_name)
            + article_body_html(teaser(article["base"]), tr=self._tr)
        )

    def _chinese_text(self, style: str | None = None) -> str:
        """Chinese slot hover (owner rework): the year name and span,
        then the animal's ARTICLE with the owner's medallion on top —
        in the ACTIVE style's look (owner bug 2026-07-13: the legend
        always showed the bronze plate): colored takes its own art,
        gold/silver ride the selective swap."""
        from render.subdial import octa_slot_art

        day = self._dial.day
        element, animal = day.chinese_name.split()
        header = centered(
            self._tr("{element} {animal}").format(
                element=self._tr(element), animal=self._tr(animal)
            ),
            f"{day.chinese_start.day} {self._month_short(day.chinese_start)} "
            f"{self._year(day.chinese_start)} – "
            f"{day.chinese_end.day} {self._month_short(day.chinese_end)} "
            f"{self._year(day.chinese_end)}",
        )
        # The animal's article, then the ELEMENT paragraph qualifying
        # THIS return of it (owner spec — each return wears a new one).
        text = (
            self._dial.symbolism.chinese_article(animal)["base"]
            + "\n\n"
            + self._dial.symbolism.chinese_element(element)["base"]
        )
        folder = complications.CHINESE_STYLE_ART_DIRS.get(style, "zodiac/chinese/primary/bronze")
        image = metal_variant_file(
            octa_slot_art(folder, animal),
            style if style in defaults.METAL_SWAP_TARGETS else None,
        )
        return header + "<br/>" + article_html(
            image, None, text, tr=self._tr,
        )

    def _ascendant_text(self, style: str | None = None) -> str:
        """The Ascendant hover (owner request 2026-07-12, formatting
        2026-07-13): "Ascendant" as the bold title, the rising sign
        beneath it, the image TRIO led by the active style, then the
        sign's article."""
        sign = self._dial.tick.ascendant_sign
        symbol = dict(zodiac.ZODIAC_SIGNS)[sign]
        header = hover_title(
            html.escape(self._tr("Ascendant"))
        ) + centered(f"{symbol} {self._tr(sign)}")
        article = self._dial.symbolism.zodiac_article(sign)
        return (
            header
            + self._zodiac_image_trio(style, sign)
            + article_body_html(teaser(article["base"]), tr=self._tr)
        )
