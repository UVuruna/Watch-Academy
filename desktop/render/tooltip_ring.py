"""Every hover the RING and the ARMS answer — one of the four families
`render/tooltip_composer.py` was cut into (owner 2026-08-19).

The ring's jewel and word legends, the live crown, and the long
`_arm_tooltip` with the whole seat vocabulary behind it: the archetype
arms and their three-side and tetramorph readings, the two-row centre,
the dual Sunday columns, the Ninth's alternate face, and the thirteenth.

**How the dial is held: it is NOT.** This is a MIXIN on
`TooltipComposer` — see `render/tooltip_sky.py` for the whole
argument. One holder of the dial, `self._dial`, and every method here
reads it live.

`_SOUTH_ANCHOR_FLIP` lives here rather than in the composer because the
arm is its subject; `render/encyclopedia_targets.py` imports it from
here for `_arm_encyclopedia_target`, which flips the same anchors to
find the same seat. One table, two readers, no copy.

**The door is still `render/tooltip_composer.py`.**

Layer: render. Documentation: __about/tooltip_ring.md.
"""

import html
import math
from datetime import timedelta

from PySide6.QtCore import QPointF

from config import (
    archetypes, complications, defaults, dial, encyclopedia_ui, ninth,
    pantheon, registry, zodiac,
)
from config.registry import week as week_registry
from core import angles, continents, world
from core.year_wheel import meteorological_span, zodiac_span
from render.article_html import (
    article_body_html, article_html, article_paragraphs, centered_html,
    hover_badge, hover_title, teaser,
)
from render.asset_recolor import metal_variant_file
from render.asset_variants import scaled_variant_file
from render.archetype_geometry import archetype_art_ready
from render.ninths import (
    active_thirteenth, center_face, dual_seat_ninth, ninth_window_anchor,
    theme_ninth, thirteenth_plate,
)
from render.skin_geometry import archetype_key, palette_for, weekday_slots
from render.slot_layout import sunday_dual_face


def _crown_arc_centre(entry: dict) -> float:
    """One crown-text entry's own arc centre — the axis THE ARC READING
    LAW reflects about (`core.world.arc_centre_deg`). Computed from the
    SAME glyph seats `render.layers.ring.RingLayer._draw_crown_text`
    passes to `arc_seats` (Rule #5), so a word's hover zone and its
    drawn letters can never disagree about where the arc went."""
    return world.arc_centre_deg([theta for _asset, theta in entry["glyphs"]])


# South of the equator the year wheel runs mirrored (+180°) — these
# unwrapped anchor angles trade places (June solstice <-> December,
# March equinox <-> September).
_SOUTH_ANCHOR_FLIP = {270.0: 450.0, 360.0: 540.0, 450.0: 270.0, 540.0: 360.0}


class RingTooltips:
    def _ring_jewel_legend_tooltip(
        self, theta: float, half: float
    ) -> str | None:
        """The per-letter HOVER LEGEND (ROADMAP 15b): `skin.ring.
        jewel_legend` is hour -> {name, reading}, built by
        `app.skin_builder.build_skin` from the active ring preset's
        optional `legend` card (`data.rings.validate_preset`) — the
        Dollar, DOMY and LOOP today (CROSS-WORDS round). Finds the legend entry
        whose OWN jewel position is within `half` degrees of the
        hovered angle (the same half-width the 12h Four Greetings
        trigger uses — every ring jewel occupies the same angular
        slot) and returns its title + reading, or None off any legend
        letter."""
        legend = self._dial.skin.ring.jewel_legend
        if not legend:
            return None
        # WHAT THE ROTATION CARRIES: the cursor arrives in the WORLD
        # frame; a jewel lives in its own (identical in `all_turn`).
        theta = self._dial.jewel_theta(theta)
        for hour, entry in legend.items():
            jewel_theta = angles.ring_position_angle(hour)
            delta = min(
                (theta - jewel_theta) % 360.0,
                (jewel_theta - theta) % 360.0,
            )
            if delta <= half:
                return hover_title(
                    html.escape(entry["name"])
                ) + article_body_html(entry["reading"])
        return None

    def _ring_word_legend_tooltip(
        self, theta: float, distance: float, radius: float
    ) -> str | None:
        """The per-WORD hover on the outer arc text.

        THE ONE TERM ONE HOVER LAW (ring_rework §3, owner ruling
        2026-08-06 — "every crown text carries ITS OWN hover"): when
        the crown-text entry itself carries a `reading` (Database/
        ring_presets.json, `data.rings._validate_crown_text`), every
        word of THAT entry answers with the entry's own reading —
        ANNUIT COEPTIS explains the Latin motto itself, never the
        Anointed Aegis legend of the letter it happens to hang on (the
        exact reported bug the WORD-HOVER round shipped, corrected
        here). Only entries carrying no `reading` of their own (a
        custom ring's free-typed/location crown) fall back to the old
        behaviour: the legend of the SEAT that word belongs to — the
        station words sit ON their station's seat, and the Dollar's
        five words each carry exactly one pinned letter (ANNUIT→A,
        COEPTIS→S, NOVUS→N, ORDO→Ω, SECLORUM→M: the five words spell
        the five letters). Geometry is pre-solved by
        `app.skin_builder.build_skin` into `ring.crown_text[…]["words"]`
        (angular center + half-span per word); here only the band/angle
        test and the reading/legend lookup run. A word with no seat and
        no entry reading, or a seat without a legend entry, stays
        silent — the graceful-absence pattern the letter legend already
        uses."""
        crown_text = self._dial.skin.ring.crown_text
        night_text = self._dial.skin.ring.crown_text_night
        if not crown_text and not night_text:
            return None
        band = dial.RING_CROWN_TEXT_RADIUS_FRACTION
        half_band = dial.RING_CROWN_TEXT_HOVER_HALF_FRACTION
        if not (
            radius * (band - half_band)
            <= distance
            <= radius * (band + half_band)
        ):
            return None
        legend = self._dial.skin.ring.jewel_legend
        # THE ARC READING LAW reaches the hover too (core.world): the
        # drawn arc is REFLECTED, not merely rotated, whenever the world
        # offset carries it across the horizon — so the stored word
        # centre is mapped FORWARD through the same map and compared in
        # screen space, instead of un-rotating the cursor. `_world_theta`
        # already took the offset off, so it goes back on here. Both are
        # identities in Geocentric.
        # WHAT THE ROTATION CARRIES: the SCREEN angle is always the
        # world frame plus the world offset, but the arc itself is
        # placed by the CROWN's own offset — the same number in
        # `all_turn`, 0.0 in `numerals_turn` where the arc stands still.
        screen_theta = (theta + self._dial.world_offset()) % 360.0
        offset = self._dial.jewel_offset()
        # THE INVERTED CROWN TEXTS (owner verdict 2026-08-14): the hover
        # answers for the arcs that are DRAWN — a day entry falls silent
        # once its arc crossed the horizon and its night twin took the
        # seat, by the SAME predicate RingLayer._draw_crown_text paints
        # with (Rule #5: the words and their letters can never disagree
        # about which motto is up).
        for entry, crossed_draws in (
            [(e, False) for e in crown_text]
            + [(e, True) for e in night_text]
        ):
            arc_centre = _crown_arc_centre(entry)
            if night_text and world.arc_crosses_horizon(
                arc_centre, offset
            ) != crossed_draws:
                continue
            entry_reading = entry.get("reading")
            for word in entry.get("words", ()):
                center = world.arc_seat_deg(word["center"], arc_centre, offset)
                delta = min(
                    (screen_theta - center) % 360.0,
                    (center - screen_theta) % 360.0,
                )
                if delta > word["half"]:
                    continue
                if entry_reading is not None:
                    # THE ONE TERM ONE HOVER LAW: the entry speaks for
                    # itself, regardless of which (if any) seat this
                    # word happens to hang on.
                    return hover_title(
                        html.escape(entry_reading["title"])
                    ) + article_body_html(entry_reading["text"])
                if word["seat"] is None:
                    continue
                seat_entry = legend.get(word["seat"] % 24)
                if seat_entry is None:
                    return None
                title = f'{word["text"]} · {seat_entry["name"]}'
                return hover_title(
                    html.escape(title)
                ) + article_body_html(seat_entry["reading"])
        return None

    def _live_crown_tooltip(
        self, theta: float, distance: float, radius: float
    ) -> str | None:
        """The LIVE crown's own hover (ring_rework §1/§3, owner ruling
        2026-08-06 — "the live time/location crowns say whose hour they
        keep"): The One's civil-hour top arc and Templar's Jerusalem-
        hour top arc (`render.layers.numerals.LiveCrownLayer`,
        `dial.RING_LIVE_CROWN`) carry no `crown_text` card entry at all
        — they are rasterized fresh every minute — so their hover text
        lives HERE, in `dial.RING_LIVE_CROWN_READING`, rather than in
        any card. Geometry is approximate on purpose (Rule #7 — the
        live glyphs are never solved into named word spans the way a
        static crown-text entry is): the whole top half of the crown
        band answers, generously covering every digit format the
        setting allows (`hh:mm` / `12h 35min`)."""
        if self._dial.skin.ring_name not in dial.RING_LIVE_CROWN:
            return None
        entry = dial.RING_LIVE_CROWN[self._dial.skin.ring_name]
        band = dial.RING_CROWN_TEXT_RADIUS_FRACTION
        half_band = dial.RING_CROWN_TEXT_HOVER_HALF_FRACTION
        if not (
            radius * (band - half_band)
            <= distance
            <= radius * (band + half_band)
        ):
            return None
        offset = self._dial.world_offset()
        screen_theta = (theta + offset) % 360.0
        anchor = 0.0 if entry["orientation"] == "top" else 180.0
        delta = min(
            (screen_theta - anchor) % 360.0, (anchor - screen_theta) % 360.0
        )
        if delta > dial.RING_LIVE_CROWN_HOVER_HALF_DEG:
            return None
        reading = dial.RING_LIVE_CROWN_READING.get(self._dial.skin.ring_name)
        if reading is None:
            return None
        return hover_title(
            html.escape(reading["title"])
        ) + article_body_html(reading["text"])

    def _arm_tooltip(self, point: QPointF, radius: float, rotation: float) -> str | None:
        """Hover over a star arm (owner spec): hexa arms name their TWO
        zodiac signs; cross/octa cardinal arms give the exact instant of
        the solstice/equinox they point at; octa diagonal arms describe
        their season (dates, duration, the middle date the arrow points
        at). With solar rotation on, a trailing * flags the slight
        offset from the year-wheel positions. (In archetype mode the ARM
        figures answer through `_element_at`/`tooltip_at`, not here.)"""
        # Only INSIDE the drawn diamond (owner bug report): between the
        # arms the wheel itself answers — the Aura's day or the Umbra's
        # night. The ONE arm-diamond geometry lives in `_arm_angle_at`.
        arm_angle = self._dial.arm_angle_at(point, radius, rotation)
        if arm_angle is None:
            return None
        theta = math.degrees(math.atan2(point.x(), -point.y())) % 360.0
        star = "*" if self._dial.skin.solar_rotation else ""

        if self._dial.skin.pointer == "hexa":
            # The 60-deg arc [arm-30, arm+30] spans exactly two signs.
            # Hover rework (owner 2026-07-13 round two): the two signs
            # stand LEFT/RIGHT as two columns — each with its bold
            # title (name + dates, NO glyph), its COLORED logo, then
            # ITS article (base + the active palette's paragraph).
            from render.subdial import octa_slot_art

            style = self._dial.skin.palette_style
            columns = []
            south = self._dial.day.southern_hemisphere
            for offset in (-30.0, 0.0):      # the two signs' START angles
                start_angle = (arm_angle + offset) % 360.0
                if south:
                    # The mirrored year wheel (owner spec 2026-07-12):
                    # the diamond the Earth passes must name the signs
                    # it actually passes there — the opposite half.
                    start_angle = (start_angle + 180.0) % 360.0
                name, _symbol = zodiac.ZODIAC_SIGNS[int(start_angle) // 30]
                start, end = zodiac_span(self._dial.day.year_anchors, start_angle)
                start = start.astimezone(self._dial.day.tzinfo)
                last = end.astimezone(self._dial.day.tzinfo) - timedelta(days=1)
                header = (
                    f"{html.escape(self._tr(name))} "
                    f"({self._ord(start.day)} {html.escape(self._month(start))} - "
                    f"{self._ord(last.day)} {html.escape(self._month(last))})"
                )
                if offset == -30.0 and star:
                    header += html.escape(star)
                colored = octa_slot_art(
                    complications.ZODIAC_STYLE_ART_DIRS["colored"], name
                )
                plate = ""
                if colored is not None and colored.exists():
                    small = scaled_variant_file(
                        colored, 2 * encyclopedia_ui.ARTICLE_IMAGE_WIDTH_PX
                    )
                    plate = (
                        f"<div align='center'><img src='{small.as_uri()}' "
                        f"width='{encyclopedia_ui.ARTICLE_IMAGE_WIDTH_PX}'/></div>"
                    )
                article = self._dial.symbolism.zodiac_article(name)
                text = article["base"]
                # South of the equator the sign wears the opposite
                # arm's hue — its own SOUTH variant paragraph (falls
                # back to the northern one until translated/edited).
                variant = (
                    article["variants"].get(f"{style}_south")
                    if south else None
                ) or article["variants"].get(style)
                if variant:
                    text += "\n\n" + variant
                columns.append(
                    hover_title(header)
                    + plate
                    + article_paragraphs(teaser(text), tr=self._tr)
                )
            # ONE flat table, both columns width-declared (nested
            # tables measured wrong — the popup honors these cells).
            return (
                "<table cellspacing='12'><tr>"
                f"<td width='{encyclopedia_ui.ARTICLE_COLUMN_WIDTH_PX}'>"
                f"{columns[0]}</td>"
                f"<td width='{encyclopedia_ui.ARTICLE_COLUMN_WIDTH_PX}'>"
                f"{columns[1]}</td>"
                "</tr></table>"
            )
        if self._dial.skin.pointer == "trio":
            # Trio arm (owner spec): its theological theme, the day
            # third it CENTERS (the arm tip is the middle of its hue),
            # the weekday pair it carries — and the virtue's ARTICLE.
            start_hour = int((((arm_angle + 180.0) % 360.0) // 15 - 4) % 24)
            end_hour = int((start_hour + 8) % 24)
            bodies = next(
                occupants
                for angle, occupants in weekday_slots(self._dial.skin)
                if angle == arm_angle
            )
            days = " · ".join(
                self._tr(week_registry.WEEKDAY_FULL_NAMES[body]) for body in bodies
            )
            if self._dial.skin.palette_style == "tertiary":
                # The GENESIS wheel (CUBE.md §Double Trinity): the arm
                # speaks its creation office — person, office, hours,
                # days. The office articles are Session 21's writers'
                # work; until they land the hover carries the canon
                # pending line, never a KeyError (the same graceful
                # path every unwritten archetype article walks).
                person, office = archetypes.GENESIS_ARM_OFFICES[arm_angle]
                header = centered_html(
                    f"<b>{html.escape(self._tr(office))}</b>"
                    f"{html.escape(star)}",
                    html.escape(self._tr(person)),
                    f"{start_hour:02d}:00 - {end_hour:02d}:00",
                    html.escape(days),
                )
                return header + "<br/>" + article_body_html(
                    archetypes.ARCHETYPE_PENDING_LINE, tr=self._tr
                )
            theme = archetypes.TRIO_ARM_THEMES[arm_angle]
            header = centered_html(
                f"<b>{html.escape(self._tr(theme))}</b>{html.escape(star)}",
                f"{start_hour:02d}:00 - {end_hour:02d}:00",
                html.escape(days),
            )
            article = self._dial.symbolism.trio_article(theme)
            return (
                hover_badge(defaults.TRINITY_ART_DIR / f"{theme}.png")
                + header + "<br/>"
                + article_body_html(teaser(article["base"]), tr=self._tr)
            )
        if arm_angle % 90.0 == 0.0:
            # Cardinal arms (cross and octa) point at the season events:
            # the exact instant, plus the DAY LENGTH on that date (owner
            # rework). The cross additionally describes its
            # METEOROLOGICAL season — bounds halfway between the anchors,
            # so the season centers on its solstice/equinox.
            anchor_angle = {0.0: 360.0, 90.0: 450.0, 180.0: 540.0, 270.0: 270.0}[
                arm_angle
            ]
            if self._dial.day.southern_hemisphere:
                # The year wheel runs MIRRORED south of the equator
                # (the Earth marker already does) — the arms must point
                # at the mirrored anchors too (owner bug 2026-07-12:
                # Sydney's TOP arm must read the DECEMBER solstice).
                anchor_angle = _SOUTH_ANCHOR_FLIP[anchor_angle]
            index = self._dial.day.year_anchors.angles.index(anchor_angle)
            name = self._dial.day.season_events[index][1]      # zone-correct name
            instant = self._anchor_instant(anchor_angle).astimezone(self._dial.day.tzinfo)
            hours, minutes = self._dial.day.anchor_day_lengths[index].split(":")
            # First block (owner format 2026-07-13: image → title →
            # space → data; both equinoxes share the ONE balance
            # emblem): the turning point with its labeled day length.
            badge = (
                "Equinox" if "Equinox" in name else name.replace(" ", "_")
            )
            head = hover_badge(
                defaults.SEASON_ART_DIR / "turning_point" / f"{badge}.png"
            ) + hover_title(
                f"{html.escape(self._tr(name))}{html.escape(star)}"
            ) + centered_html(
                "",
                f"{self._ord(instant.day)} {html.escape(self._month(instant))} "
                f"{self._year(instant)} - {instant:%H:%M}",
                f"{self._label('Daylight')} {int(hours)}h {int(minutes)}min",
            )
            if self._dial.skin.pointer != "cross":
                return head
            # Second block, split off by a RULE (owner 2026-07-13:
            # two data sets, a line between them): the meteorological
            # season — or the tropics' wet/dry half-year — wearing its
            # own badge.
            if self._dial.day.zone == "tropics":
                # Tropics (owner decision): the cross arms describe
                # the equinox-bounded WET/DRY halves — the solstice
                # arms CENTER theirs, the equinox arms START theirs.
                span_start = 270.0 if anchor_angle in (270.0, 360.0) else 450.0
                is_wet, block = self._wet_dry_block(span_start)
                return head + "<hr/>" + hover_badge(
                    defaults.SEASON_ART_DIR
                    / f"{'Wet' if is_wet else 'Dry'}_Season.png"
                ) + block
            season = self._season_name_for(anchor_angle)
            met_start, met_end = meteorological_span(
                self._dial.day.year_anchors, anchor_angle
            )
            met_start = met_start.astimezone(self._dial.day.tzinfo)
            met_end = met_end.astimezone(self._dial.day.tzinfo)
            met_days = (met_end - met_start).total_seconds() / 86400
            return head + "<hr/>" + hover_badge(
                defaults.SEASON_ART_DIR / "meteorological" / f"{season}.png"
            ) + hover_title(
                html.escape(
                    self._tr("Meteorological {season}").format(
                        season=self._tr(season)
                    )
                )
            ) + centered_html(
                "",
                f"<b>{self._tr('From')}</b> {self._ord(met_start.day)} "
                f"{self._month(met_start)} {self._year(met_start)} - "
                f"{met_start:%H:%M}",
                f"<b>{self._tr('To')}</b> {self._ord(met_end.day)} "
                f"{self._month(met_end)} {self._year(met_end)} - "
                f"{met_end:%H:%M}",
                f"{self._label('Duration')} {met_days:.1f} "
                f"{html.escape(self._tr('Days'))}",
            )
        # Octa diagonal arms point at the QUARTER centers: the four
        # temperate seasons — or, in the tropics, the halves of the
        # wet/dry seasons (owner spec: TL is the first part of the
        # season the top arms span, TR the second...).
        start_angle = {315.0: 270.0, 45.0: 360.0, 135.0: 450.0, 225.0: 540.0}[
            arm_angle
        ]
        if self._dial.day.southern_hemisphere:
            # Mirrored wheel (see the cardinal arms): the quarters the
            # diagonal arms span flip with it.
            start_angle = _SOUTH_ANCHOR_FLIP[start_angle]
        start = self._anchor_instant(start_angle).astimezone(self._dial.day.tzinfo)
        end = self._anchor_instant(start_angle + 90.0).astimezone(self._dial.day.tzinfo)
        middle = start + (end - start) / 2
        days = (end - start).total_seconds() / 86400
        if self._dial.day.zone == "tropics":
            starts_in_march = start_angle in (270.0, 360.0)
            is_wet = starts_in_march != self._dial.day.southern_hemisphere
            if self._dial.overlay:
                half = self._tr("(1st half)" if start_angle in (270.0, 450.0)
                                else "(2nd half)")
            else:
                half = (
                    "(1<sup>st</sup> half)"
                    if start_angle in (270.0, 450.0)
                    else "(2<sup>nd</sup> half)"
                )
            season_line = (
                f"<b>{html.escape(self._tr('Wet season' if is_wet else 'Dry season'))}</b> "
                f"{half}{html.escape(star)}"
            )
            _, whole = self._wet_dry_block(270.0 if starts_in_march else 450.0)
            return hover_badge(
                defaults.SEASON_ART_DIR
                / f"{'Wet' if is_wet else 'Dry'}_Season.png"
            ) + centered_html(
                season_line,
                self._span_line(start, end, days),
                f"{self._tr('Heart:')} {self._ord(middle.day)} "
                f"{self._month(middle)}",
            ) + "<hr/>" + whole
        season = self._season_name_for(start_angle)
        return hover_badge(
            defaults.SEASON_ART_DIR / f"{season}.png"
        ) + centered_html(
            f"<b>{html.escape(self._tr(season))}</b>{html.escape(star)}",
            self._span_line(start, end, days),
            f"{self._tr('Heart:')} {self._ord(middle.day)} {self._month(middle)}",
        )

    def _archetype_arm_tooltip(self, index: int) -> str:
        """One arm figure's archetype legend (owner 2026-07-16): the
        TWO-ROW article per the two-row canon — person+calling, member+
        hearth-role, temperament+age, person+quality, pillar+shadow,
        estate+object. EXCEPT the two THREE-SIDE layouts (owner
        2026-07-17): the Ages (compass light) show the age's text and BOTH
        life registers (the Tree + the Menagerie); the Tetramorph (seasons
        light) show the creature + the evangelist + the element."""
        key = archetype_key(self._dial.skin)
        if key == "compass_secondary":
            return self._archetype_three_side(index)
        if key == "quaternity_secondary":
            return self._tetramorph_three_side(index)
        fig = archetypes.figures(key)[index]
        return self._archetype_two_rows(
            key, fig["name"], fig["row2"], fig["entity"], fig["file"]
        )

    def _archetype_three_side(self, index: int) -> str:
        """The AGES three-side hover (owner 2026-07-17, "oba odmah"): a
        THREE-COLUMN article whose total width stays the TWO-SIDE width —
        the age's text, the Tree register (image + being), the Menagerie
        register (image + being). Each register image resolves from its
        own life/<register> path and shows only when REAL art has landed
        (placeholders fall back to the being name, gracefully as before)."""
        key = "compass_secondary"
        registers = archetypes.ARCHETYPES[key]["registers"]
        tree_fig = registers["tree"][index]
        animals_fig = registers["animals"][index]
        set_name = archetypes.ARCHETYPES[key]["articles"]
        node = self._dial.symbolism.archetype_article(set_name, tree_fig["entity"])
        rows = (node or {}).get("rows") or ()
        # Column 1 — the age name and its text (or the pending line).
        text_col = hover_title(html.escape(self._tr(tree_fig["name"])))
        if rows:
            text_col += article_paragraphs(teaser(rows[0]), tr=self._tr)
        else:
            text_col += centered_html(
                "",
                html.escape(self._tr(archetypes.ARCHETYPE_PENDING_LINE)),
            )

        def register_column(caption: str, fig: dict) -> str:
            image = ""
            if archetype_art_ready(fig["file"]):
                small = scaled_variant_file(
                    fig["file"], 2 * encyclopedia_ui.ARTICLE_THREE_IMAGE_PX
                )
                image = (
                    f"<div align='center'><img src='{small.as_uri()}' "
                    f"width='{encyclopedia_ui.ARTICLE_THREE_IMAGE_PX}'/></div>"
                )
            return (
                hover_title(html.escape(self._tr(caption)))
                + image
                + centered_html(f"<b>{html.escape(self._tr(fig['row2']))}</b>")
            )

        width = encyclopedia_ui.ARTICLE_THREE_COLUMN_WIDTH_PX
        return (
            "<table cellspacing='10'><tr>"
            f"<td width='{width}'>{text_col}</td>"
            f"<td width='{width}'>{register_column('The Tree', tree_fig)}</td>"
            f"<td width='{width}'>"
            f"{register_column('The Menagerie', animals_fig)}</td>"
            "</tr></table>"
        )

    def _tetramorph_three_side(self, index: int) -> str:
        """The TETRAMORPH three-side hover (owner 2026-07-17, ROADMAP 15e:
        "sva 3 ako se podudaraju"): a THREE-COLUMN article — the same
        machinery and total width as the Ages three-side — carrying the
        CREATURE (its glass, name and text), the EVANGELIST it became
        (Mark/Luke/John/Matthew, with his rondel and article), and the
        ELEMENT its fixed-cross season arm holds (Fire/Earth/Water/Air,
        the name in its own wheel hue, with its humoral article). The
        creature node carries the three columns' prose as its rows —
        rows[0] the creature, rows[1] the evangelist, rows[2] the element
        (Session 6 + the Tetramorph completion round); each column
        degrades to its bare title/name when its row (or the evangelist
        rondel) has not landed — never a KeyError."""
        key = "quaternity_secondary"
        fig = archetypes.figures(key)[index]
        set_name = archetypes.ARCHETYPES[key]["articles"]
        node = self._dial.symbolism.archetype_article(set_name, fig["entity"])
        rows = (node or {}).get("rows") or ()
        # Column 1 — the creature (glass + name + text).
        creature_col = hover_title(html.escape(self._tr(fig["name"])))
        if archetype_art_ready(fig["file"]):
            small = scaled_variant_file(
                fig["file"], 2 * encyclopedia_ui.ARTICLE_THREE_IMAGE_PX
            )
            creature_col += (
                f"<div align='center'><img src='{small.as_uri()}' "
                f"width='{encyclopedia_ui.ARTICLE_THREE_IMAGE_PX}'/></div>"
            )
        if rows:
            creature_col += article_paragraphs(teaser(rows[0]), tr=self._tr)
        else:
            creature_col += centered_html(
                "", html.escape(self._tr(archetypes.ARCHETYPE_PENDING_LINE))
            )
        # Column 2 — the Evangelist: his rondel (real art only), his name
        # (the figure's row-2), then his article (rows[1] when written).
        evangelist_col = hover_title(html.escape(self._tr("The Evangelist")))
        ev_file = archetypes.tetramorph_evangelist_file(index)
        if archetype_art_ready(ev_file):
            small = scaled_variant_file(
                ev_file, 2 * encyclopedia_ui.ARTICLE_THREE_IMAGE_PX
            )
            evangelist_col += (
                f"<div align='center'><img src='{small.as_uri()}' "
                f"width='{encyclopedia_ui.ARTICLE_THREE_IMAGE_PX}'/></div>"
            )
        evangelist_col += centered_html(
            f"<b>{html.escape(self._tr(fig['row2']))}</b>"
        )
        if len(rows) > 1:
            evangelist_col += article_paragraphs(teaser(rows[1]), tr=self._tr)
        # Column 3 — the Element: the name in its active wheel hue, then
        # its humoral article (rows[2] when written).
        hue = palette_for(self._dial.skin)[index]
        element_col = hover_title(
            html.escape(self._tr("The Element"))
        ) + centered_html(
            f"<b style='color: {hue}'>"
            f"{html.escape(self._tr(archetypes.tetramorph_element(index)))}</b>"
        )
        if len(rows) > 2:
            element_col += article_paragraphs(teaser(rows[2]), tr=self._tr)
        width = encyclopedia_ui.ARTICLE_THREE_COLUMN_WIDTH_PX
        return (
            "<table cellspacing='10'><tr>"
            f"<td width='{width}'>{creature_col}</td>"
            f"<td width='{width}'>{evangelist_col}</td>"
            f"<td width='{width}'>{element_col}</td>"
            "</tr></table>"
        )

    def _archetype_center_tooltip(self) -> str:
        """The archetype center's legend — the Eye / the Hearth / the
        Seal / the Union / the Throne speak their CANON paragraph."""
        key = archetype_key(self._dial.skin)
        center = archetypes.center(key)
        return self._archetype_two_rows(
            key, center["name"], None, center["entity"], center["file"]
        )

    def _archetype_two_rows(
        self, key: str, name: str, row2: str | None, entity: str, art,
    ) -> str:
        """One archetype legend: the stained glass on top (real art
        only — a 1×1 placeholder never stretches into the popup), the
        figure's name as the title, then the TWO ROWS from the
        archetype's article set. Until Session 6 writes the set the
        hover shows the name, the second-row name and the one-line
        pending stand-in — the documented graceful path, never a
        KeyError."""
        set_name = archetypes.ARCHETYPES[key]["articles"]
        node = self._dial.symbolism.archetype_article(set_name, entity)
        badge = hover_badge(art) if archetype_art_ready(art) else ""
        title = hover_title(html.escape(self._tr(name)))
        rows = (node or {}).get("rows") or ()
        if rows:
            parts = [
                badge, title,
                article_body_html(teaser(rows[0]), tr=self._tr),
            ]
            if row2 is not None and len(rows) > 1:
                # The second row, split off by a rule — the same shape
                # as the cross arms' two data sets (owner pattern).
                parts += [
                    "<hr/>",
                    hover_title(html.escape(self._tr(row2))),
                    article_body_html(teaser(rows[1]), tr=self._tr),
                ]
            return "".join(parts)
        subtitle = (
            centered_html(f"<b>{html.escape(self._tr(row2))}</b>")
            if row2 is not None
            else ""
        )
        return badge + title + subtitle + centered_html(
            "",
            html.escape(self._tr(archetypes.ARCHETYPE_PENDING_LINE)),
        )

    def _dual_face_columns(self, theme: str, faces: tuple[str, str]) -> str:
        """The CENTER seat's TWO-FACE hover CARD (owner verdict B, round
        R3b items 2/4 — "po principu ZODIAC na PRISM diamond hover"):
        two texts side by side, a divider between, each under its own
        emblem — the SAME two-column table `_arm_tooltip`'s hexa
        zodiac-diamond hover builds below (Rule #5), fed by `faces`, a
        pair picked from up to three: "ruler" (GOOD), "servant" (EVIL),
        "ninth" (THE UNFOUND)."""
        spec = self._dial.skin.weekday_set
        dual_names = spec.dual_names or pantheon.WEEKDAY_DUAL_NAMES[theme]
        article_set = spec.article_set or registry.ARTICLES[theme]
        columns = []
        sunday = html.escape(self._tr(week_registry.WEEKDAY_FULL_NAMES["sun"]))
        for face in faces:
            if face == "ninth":
                name, asset = theme_ninth(
                    theme, self._center_ninth_alt(), on_date=self._dial.day.local_date
                )
                text = self._dial.encyclopedia.entry("ninths", name)["base"]
                # The Ninth stands OUTSIDE the circle — no weekday line.
                day_line = ""
            else:
                ruler = face == "ruler"
                name = dual_names[0 if ruler else 1]
                raw = spec.bodies.get("sun") if ruler else spec.dual_asset
                if raw is not None:
                    raw = pantheon.rotating_art_file(raw, self._dial.day.local_date) or raw
                asset = metal_variant_file(raw, spec.metal)
                node = self._dial.symbolism.article(article_set, "sun")
                text = node.get("faces", {}).get(face) or node["base"]
                if ruler:
                    variant = node["variants"].get(self._combo_key())
                    if variant:
                        text += "\n\n" + variant
                # THE WEEKDAY-TITLE LAW: both throne faces are Sunday's.
                day_line = f"<br/>{sunday}"
            columns.append(
                hover_badge(asset)
                + hover_title(
                    f"<b>{html.escape(self._tr(name))}</b>{day_line}"
                )
                + article_paragraphs(teaser(text), tr=self._tr)
            )
        return (
            "<table cellspacing='12'><tr>"
            f"<td width='{encyclopedia_ui.ARTICLE_COLUMN_WIDTH_PX}'>{columns[0]}</td>"
            f"<td width='{encyclopedia_ui.ARTICLE_COLUMN_WIDTH_PX}'>{columns[1]}</td>"
            "</tr></table>"
        )

    def _center_dual_tooltip(self, active: bool) -> str:
        """The CENTER seat's Sunday duality hover (owner INSTRUCTION #5,
        re-shaped by the 2026-07-29 seal): a ghost read on a non-Sunday
        day stays the single GOOD/Ruler article; on the real Sunday, a
        theme with only TWO faces ALWAYS speaks BOTH side by side
        (owner: "HOVER su uvek OBA jedan pored drugog"), a theme with a
        NINTH speaks the showing face alone outside the solar windows
        (GOOD in daylight, EVIL at night — `center_face`) and the
        matching TWO-COLUMN pair inside them (GOOD+NINTH near solar
        noon, EVIL+NINTH near solar midnight — `ninth_window_anchor`)."""
        if not active:
            return self._sun_face_tooltip("ruler", active=False)
        theme = self._dial.skin.weekday_theme
        ninth = theme_ninth(
            theme, self._center_ninth_alt(), on_date=self._dial.day.local_date
        )
        if ninth is None:
            return self._dual_face_columns(theme, ("ruler", "servant"))
        face = center_face(self._dial.day, self._dial.tick, has_ninth=True)
        if face == "ninth":
            beside = (
                "ruler"
                if ninth_window_anchor(self._dial.day, self._dial.tick) == "noon"
                else "servant"
            )
            return self._dual_face_columns(theme, (beside, "ninth"))
        return self._sun_face_tooltip(face, active=True)

    def _center_ninth_alt(self) -> bool:
        """THE DOUBLE NINTH's alt-face flag for the hover (owner
        Double-Ninth verdicts, 2026-07-29 — was `_center_pangea`,
        continents-only, before the law generalized): dispatches by the
        theme's OWN `ninth.NINTH_MECHANISMS` entry, fed from this
        compositor's own day and last tick so the card and the dial
        never disagree.

        - "easter_egg" reads the SAME `core.continents` sky law the
          paint pass reads.
        - "daynight" reads the SAME `TickState.is_daylight` `center_face`
          reads — night is the alt face.
        - every other mechanism (or none) answers False."""
        if self._dial.day is None:
            return False
        mechanism = ninth.NINTH_MECHANISMS.get(self._dial.skin.weekday_theme)
        if mechanism == "easter_egg":
            return continents.ninth_is_pangea_from_events(
                self._dial.day.local_date,
                self._dial.day.season_events,
                self._dial.day.moon_events,
                (
                    self._dial.tick.eclipse_event is not None
                    if self._dial.tick is not None
                    else False
                ),
            )
        if mechanism == "daynight":
            return (
                self._dial.tick is not None and not self._dial.tick.is_daylight
            )
        return False

    def _dual_seat_taken(self) -> str | None:
        """Which TWO-BADGE seat the Ninth borrows RIGHT NOW ("ruler" /
        "servant" / None — owner seal 2026-07-29): mirrors
        `WeekdayLayer`'s own gate exactly (Sunday, `sunday_dual_face`,
        a Ninth that resolves, `dual_seat_ninth`'s solar windows) so
        the hover card and the dial can never disagree."""
        if self._dial.day is None or self._dial.tick is None:
            return None
        today = week_registry.WEEKDAY_BODIES[self._dial.day.weekday_index]
        if today != "sun" or not sunday_dual_face(self._dial.skin):
            return None
        if theme_ninth(
            self._dial.skin.weekday_theme, self._center_ninth_alt(),
            on_date=self._dial.day.local_date,
        ) is None:
            return None
        return dual_seat_ninth(self._dial.day, self._dial.tick)

    def _active_thirteenth(self) -> str | None:
        """THE BLUE MOON LAW's resolved 13th for today+mode (owner
        overrule, CORRECTED 2026-07-2X) — calls the SAME pure resolver
        the paint pass calls (`render.ninths.active_thirteenth`, fed
        the pre-computed `DayContext.thirteenth_candidates` fact set);
        None before the first day build (mirrors `_center_ninth_alt`'s own
        graceful guard)."""
        if self._dial.day is None:
            return None
        daylight = self._dial.tick.is_daylight if self._dial.tick is not None else True
        return active_thirteenth(self._dial.skin, self._dial.day, daylight)

    def _thirteenth_tooltip(self, key: str) -> str:
        """THE BLUE MOON LAW's 13th (owner overrule, CORRECTED
        2026-07-2X): its own article and badge lead, drawn at the
        Calendar pointer's OWN dial center (`render.layers.
        active_thirteenth` gates this to `skin.pointer == "calendar"`
        alone, so no OTHER theme's center face is ever displaced; the
        old "steps aside" closing line is retired with R12's global
        law).

        THE AXLE LAW (CANON §The Axle) splits the closing line in two:
        a calendar-driven 13th is a blue-moon guest, empty every other
        day; an ALWAYS-CENTER (`zodiac.AXLE_ALWAYS_CENTERS`) is the
        axle the twelve turn on, present on literally every date
        instead. An always-center whose Encyclopedia article is not written yet
        (`family is None` in `zodiac.THIRTEENTHS` — the graceful-
        absent contract, same as a missing art plate) skips the
        `entry()` lookup entirely rather than crash on an unwritten
        family/article pair, and the closing line itself becomes the
        teaser (`teaser` reads the text BEFORE the first blank line —
        appending the closing note after an empty base would tease a
        bare " …", not this line)."""
        name, asset = thirteenth_plate(key)
        _display, family, article_name = zodiac.THIRTEENTHS[key]
        axle = key in zodiac.AXLE_ALWAYS_CENTERS
        closing = (
            "The one who does not turn with the twelve: always present, "
            "the Calendar pointer's own dial center." if axle else
            "A blue-moon guest: the Calendar pointer's own dial center, "
            "empty every other day."
        )
        if family is not None:
            marker = "[[The Axle]]" if axle else "[[The Thirteenth]]"
            text = self._dial.encyclopedia.entry(family, article_name)["base"]
            text += f"\n\n{marker} {closing}"
        else:
            text = closing
        title = (
            f"<span style='font-size: {encyclopedia_ui.ARTICLE_TITLE_PX}px'>"
            f"<b>{html.escape(self._tr(name))}</b></span>"
        )
        return article_html(asset, title, text, tr=self._tr)

    def _combo_key(self) -> str:
        """The (pointer, palette) combination the WEEKDAY articles vary
        by — "hexa_primary", "octa_secondary", "cross", "trio". The trio
        still collapses although it gained the Family SECONDARY wheel
        (2026-07-16): the shipped article variants carry one "trio"
        paragraph, and the archetype articles vary by their own grid
        sets instead — a trio_secondary variant wave is Session 6's call."""
        pointer = self._dial.skin.pointer
        if pointer in ("cross", "trio"):
            return pointer
        return f"{pointer}_{self._dial.skin.palette_style}"
