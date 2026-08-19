"""Every hover the SKY answers — one of the four families
`render/tooltip_composer.py` was cut into (owner 2026-08-19).

The sun face over the centre seat, the moon marker and its lunation
ordinal, the eclipse text with its visibility line, type icon and
article, the Earth marker with its season row and its wet/dry span, the
twilight bands and the deep-time period window with its greetings.

**How the dial is held: it is NOT.** This is a MIXIN on
`TooltipComposer`, so `self._dial` is the composer's one reference and
every method here reads the LIVE skin, day and tick through it — exactly
as it did when these methods sat inside the composer's own body. The
alternative shape, a collaborator constructed with the same dial, was
rejected for a reason the ratchet entry itself had already named: the
composer HOLDS THE DIAL, and three collaborators would be three more
holders — three back-channels that can go stale independently. The call
graph settles it too: `_arm_tooltip` (the ring family) calls
`_wet_dry_block` and `_span_line` from THIS family, `_tick_tooltip` (the
calendar family) calls `_greetings_tooltip` from here, and
`_element_encyclopedia_target` (the targets family) calls
`_season_topic_index`. Collaborators would have needed a path back for
each of those; `self` already is one.

**The door is still `render/tooltip_composer.py`.** Nothing outside it
imports this module: `tooltip_at`, `encyclopedia_target` and
`warm_hover_articles` stay the composer's, and the seventeen test files
that call them changed by not one line.

Layer: render. Documentation: __about/tooltip_sky.md.
"""

import html
import json
import math
from datetime import datetime, time, timedelta
from functools import lru_cache

from PySide6.QtCore import QPointF

from config import (
    defaults, encyclopedia_ui, glow, pantheon, paths, registry, sky,
)
from config.registry import week as week_registry
from core import angles
from core.deep_time import (
    format_anno_lucis, format_official, is_age_of_light, real_year,
)
from core.moon import phase_name
from render.article_html import (
    article_body_html, article_html, centered_html, hover_badge, hover_title,
    teaser,
)
from render.asset_recolor import metal_variant_file
from render.asset_variants import eclipse_solar_type_icon, scaled_variant_file
from render.layers.year_marker import earth_region


@lru_cache(maxsize=1)
def _greetings() -> dict:
    """The owner's Four Greetings (Database/verses.json) — Serbian in
    every language, shown only in the unlocked hidden mode."""
    return json.loads(
        (paths.database_dir() / "verses.json").read_text(encoding="utf-8")
    )["trinity"]


class SkyTooltips:
    def _sun_face_tooltip(self, face: str, active: bool) -> str:
        """ONE face of the dual Sunday (owner 2026-07-13): on the
        Compass and the Seasons each face is its own person — its own
        name, its own plate, its own text (articles.<set>.sun.faces;
        the base article stands in until a theme's split lands). The
        Ruler face keeps the pointer/palette variant paragraph."""
        theme = self._dial.skin.weekday_theme
        ruler = face == "ruler"
        dual_names = (
            self._dial.skin.weekday_set.dual_names
            or pantheon.WEEKDAY_DUAL_NAMES[theme]
        )
        display_name = dual_names[0 if ruler else 1]
        image = metal_variant_file(
            self._dial.skin.weekday_set.bodies.get("sun")
            if ruler
            else self._dial.skin.weekday_set.dual_asset,
            self._dial.skin.weekday_set.metal,
        )
        node = self._dial.symbolism.article(
            self._dial.skin.weekday_set.article_set
            or registry.ARTICLES[theme],
            "sun",
        )
        text = node.get("faces", {}).get(face) or node["base"]
        if ruler:
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
                f"<br/>{html.escape(self._tr(week_registry.WEEKDAY_FULL_NAMES['sun']))}, "
                f"{self._ord(date.day)} {html.escape(self._month(date))} "
                f"{self._year(date)}"
            )
        else:
            # THE WEEKDAY-TITLE LAW: the Sunday faces are Sunday-bound.
            title += (
                f"<br/>"
                f"{html.escape(self._tr(week_registry.WEEKDAY_FULL_NAMES['sun']))}"
            )
        return article_html(image, title, text, tr=self._tr)

    def _moon_text(self) -> str:
        """Moon hover (owner formatting rounds 2026-07-12/13): the
        PHASE NAME is the title — bigger, bold, no label — with the
        principal-phase instant beneath it, then the labeled data."""
        day = self._dial.day
        tick = self._dial.tick
        name = phase_name(tick.moon_fraction)
        title = hover_title(html.escape(self._tr(name)))
        if name in sky.MOON_PHASE_FRACTIONS:
            # A principal phase name holds ±12 h around its instant —
            # show that instant (the nearest principal event by name),
            # dated like the weekday tooltip (owner 2026-07-14:
            # "14th July", not "14 Jul").
            noon = datetime.combine(day.local_date, time(12, 0), day.tzinfo)
            instant = min(
                (event for event in day.moon_events if event[1] == name),
                key=lambda event: abs(event[0] - noon),
            )[0].astimezone(day.tzinfo)
            # centered_html — the ordinal carries real <sup> markup
            # (owner bug 2026-07-14: it printed literally through the
            # escaping centered).
            title += centered_html(
                f"{self._ord(instant.day)} {html.escape(self._month(instant))}"
                f" - {instant:%H:%M}"
            )
        lines = [
            f"{self._label('Illumination')} "
            f"{tick.moon_illumination * 100:.1f}%",
        ]
        if day.moonrise is not None and day.moonset is not None:
            lines.append(
                f"{self._label('Moonrise')} {day.moonrise:%H:%M} - "
                f"{self._label('Moonset')} {day.moonset:%H:%M}"
            )
        elif day.moonrise is not None:
            # The moon skips a rise or a set roughly once a month —
            # show the side that exists on this date.
            lines.append(f"{self._label('Moonrise')} {day.moonrise:%H:%M}")
        elif day.moonset is not None:
            lines.append(f"{self._label('Moonset')} {day.moonset:%H:%M}")
        # NO ECLIPSE LINE HERE ANY MORE (owner correction 2026-08-12):
        # the eclipse is its own body with its own card (`_eclipse_text`),
        # so this one speaks the PHASE — which is all the Moon marker
        # shows on an eclipse day, exactly as on any other.
        cycle_day = tick.moon_fraction * sky.SYNODIC_MONTH_DAYS
        return title + centered_html(
            "",
            *lines,
            "",
            html.escape(
                self._tr("Day {day} of {total}").format(
                    day=f"{cycle_day:.1f}",
                    total=sky.SYNODIC_MONTH_DAYS,
                )
            ),
            self._lunation_ordinal(),
        )

    def _lunation_ordinal(self, next_cycle: bool = False) -> str:
        """"7<sup>th</sup> Moon of 2026" — which lunation of the
        calendar year is running, counted from the year's FIRST New
        Moon (owner correction 2026-07-12): the days BEFORE it still
        ride the lunation that started in December, so they read as
        the PREVIOUS year's last — 12th or 13th, however many that
        year really began (13 roughly one year in three).
        `next_cycle` reads the FOLLOWING lunation instead (owner logic
        2026-07-13: with the Moon on the dial's left — second half of
        its cycle — the ring past 12h already belongs to the NEXT
        moon, December wrapping into the new year's 1st)."""
        day = self._dial.day
        noon = datetime.combine(day.local_date, time(12, 0), day.tzinfo)
        if next_cycle:
            # Slide the reading instant just past the next New Moon —
            # the moon_window covers the neighbor years, so the event
            # is always in the data.
            noon = min(
                when for when, name in day.moon_events
                if name == "New Moon" and when > noon
            ) + timedelta(hours=1)
        year = noon.astimezone(day.tzinfo).year
        count = sum(
            1 for when, name in day.moon_events
            if name == "New Moon" and when.year == year and when <= noon
        )
        if count == 0:
            # Early January, before the year's first New Moon — the
            # moon_window covers the neighbor years (data guarantee).
            year -= 1
            count = sum(
                1 for when, name in day.moon_events
                if name == "New Moon" and when.year == year
            )
        return self._tr("{ordinal} Moon of {year}").format(
            ordinal=self._ord(count), year=year
        )

    def _eclipse_type_icon_tag(self, eclipse) -> str:
        """The small per-TYPE eclipse icon (ECLIPSE ICON WIRING round,
        owner 2026-07-20/21) riding inline before the hover-card's
        eclipse line's own title — distinct from the big category
        EMBLEM plate (`_eclipse_emblem`, untouched): LUNAR reads the
        owner-approved red/gold/blue set, SOLAR the proposed shape-
        matched set (`defaults.eclipse_lunar_type_icon` /
        `render.asset_variants.eclipse_solar_type_icon`). Empty string — never
        a broken `<img>` — when the icon has not landed (Rule #1)."""
        icon = (
            defaults.eclipse_lunar_type_icon(eclipse.type)
            if eclipse.kind == "lunar"
            else eclipse_solar_type_icon(eclipse.type)
        )
        if icon is None:
            return ""
        px = glow.ECLIPSE_TYPE_ICON_PX
        small = scaled_variant_file(icon, 2 * px)
        return f"<img src='{small.as_uri()}' width='{px}' align='middle'/> "

    def _eclipse_visibility_text(self, eclipse) -> str:
        """What the observer can actually make of this eclipse: "Visible
        from here", or the REASON it is not (fix round E, 2026-07-19).

        The event is real either way — the body still stands on the dial,
        muted — so the card never simply omits it. A SOLAR eclipse failing
        the distance gate names the distance; everything else (any lunar
        miss, or a solar sun-down miss) reads "below the horizon", the
        only other gate either kind can fail. Round numbers; the km
        threshold itself is never printed (owner spec: config, not UI
        text)."""
        if eclipse.visible:
            return html.escape(self._tr("Visible from here"))
        if (
            eclipse.kind == "solar"
            and eclipse.distance_km is not None
            and eclipse.distance_km > glow.ECLIPSE_SOLAR_VISIBILITY_KM
        ):
            return html.escape(
                self._tr("path {km} km away").format(
                    km=round(eclipse.distance_km)
                )
            )
        return html.escape(self._tr("below the horizon"))

    def _eclipse_text(self) -> str:
        """THE ECLIPSE'S OWN CARD (owner correction 2026-08-12: "the hover
        should show info about the eclipse, not the same as the earth
        hover").

        Until this round the eclipse had no hover of its own for the same
        reason it had no body of its own: it was a costume, so it spoke
        through the Earth's or the Moon's card — one extra line under a
        date or a phase the reader had not asked about. Now the third body
        answers for itself: its own emblem, its own title, and the four
        things an eclipse actually is — which type, how deep, when it
        peaks here, and whether this observer can see it — closed by the
        chapter's own thesis (THE HOVER TEASER LAW; Space opens the rest).

        `self._ord()` returns safe HTML (a raw `<sup>` in English) and
        MUST NOT be escaped again — escaping a composed line (owner bug
        2026-07-18, Session 21-D) once printed the literal `&lt;sup&gt;`.
        Every free-form piece is escaped on its own before joining."""
        eclipse = self._dial.tick.eclipse_body_event
        if eclipse is None:                      # hover raced the minute
            return ""
        instant = eclipse.instant.astimezone(self._dial.day.tzinfo)
        article = self._eclipse_article(eclipse)
        title = (
            article["title"] if article is not None
            else ("Solar Eclipse" if eclipse.kind == "solar" else "Lunar Eclipse")
        )
        mag = (
            f"{eclipse.magnitude:.2f}" if eclipse.magnitude is not None
            else html.escape(self._tr("unknown"))
        )
        card = (
            hover_badge(self._eclipse_emblem(eclipse))
            + hover_title(html.escape(self._tr(title)))
            + centered_html(
                "",
                f"{self._eclipse_type_icon_tag(eclipse)}"
                f"{self._label('Type')} "
                f"{html.escape(self._tr(eclipse.type.capitalize()))}",
                f"{self._label('Magnitude')} {mag}",
                # THE HOUR IS THE SEAT (owner order 2026-08-12, A1): the
                # instant printed here is the very number the body's dial
                # angle is computed from, so the card explains where the
                # reader is looking.
                f"{self._label('Greatest eclipse')} "
                f"{self._ord(instant.day)} {html.escape(self._month(instant))} "
                f"{instant:%H:%M}",
                f"{self._label('Visibility')} "
                f"{self._eclipse_visibility_text(eclipse)}",
                "",
            )
        )
        if article is not None:
            card += article_body_html(teaser(article["base"]), self._tr)
        return card

    def _eclipse_article(self, eclipse) -> dict | None:
        """The eclipse chapter this body belongs to — "Solar_Total",
        "Lunar_Penumbral" and the rest of the catalog's own vocabulary.
        None (never a crash) for a type no chapter was written for: the
        card then keeps its data rows and simply says less."""
        name = f"{eclipse.kind.capitalize()}_{eclipse.type.capitalize()}"
        try:
            return self._dial.encyclopedia.entry("eclipse", name)
        except KeyError:
            return None

    def _eclipse_emblem(self, eclipse):
        """The active eclipse's category emblem Path (fix round F, owner
        slika 7 — the hover-card badge), or None for an unknown type;
        `hover_badge(None)` degrades to empty, so a missing/unknown
        emblem simply shows no image (graceful-absent)."""
        stem = glow.ECLIPSE_TYPE_EMBLEM.get((eclipse.kind, eclipse.type))
        return glow.ECLIPSE_ART_DIR / f"{stem}.png" if stem else None

    def _earth_text(self) -> str:
        """Earth hover (owner fix-round B, 2026-07-19, SLIKA 4 — the
        card rework): a Date TITLE over the date/day-of-year/week-of-
        year rows, a blank row, the ERA badge (Age of Light/Darkness
        per the CURRENT real year — deep-travel aware, `real_year`
        un-shifts the proxy frame) over an era TITLE and its Anno
        Lucis year line, a blank row, the SEASON badge (the turning-
        point badge while a season event glows, else the current
        season's own badge — the exact art the arm hovers use) over
        the existing Season:/Sign: lines. Three HTML blocks are
        concatenated directly (never passed as `centered_html` LINES)
        — `hover_title`/`hover_badge` already emit their own centered
        div, matching how every other hover in this file layers badge +
        title + `centered_html` (the cardinal-arm block a few hundred
        lines up). The eclipse/season-event line rides ahead of the
        Season: line — inside the season block, right before it — not
        at the very top of the whole card any more, since the card now
        has sections above it."""
        day, date = self._dial.day, self._dial.day.local_date
        last = day.zodiac_end - timedelta(days=1)
        real = real_year(date.year, day.deep_cycles)
        light = is_age_of_light(real)
        era_name = "Age of Light" if light else "Age of Darkness"
        era_file = "Age_of_Light.png" if light else "Age_of_Darkness.png"

        # Fix round E (owner verdict 2026-07-19, slika 1): this row is
        # ONLY the plain date — no bold "Date:" label prefix (the title
        # above already says "Date") and no Anno Lucis pairing (the era
        # block right below restates it via `format_anno_lucis`). The
        # official year alone, deep-travel aware (`real_year` un-shifts
        # the proxy frame first, matching every other year read here).
        date_block = hover_title(html.escape(self._tr("Date"))) + centered_html(
            f"{self._ord(date.day)} {html.escape(self._month(date))} "
            f"{html.escape(format_official(real, self._dial.skin.era_notation, self._dial.skin.show_era_suffix))}",
            self._tr("{ordinal} Day - {ordinal_week} Week").format(
                ordinal=self._ord(date.timetuple().tm_yday),
                ordinal_week=self._ord(date.isocalendar().week),
            ),
            "",
        )

        # THE UNIVERSAL ROTATION CONVENTION (owner decree 2026-07-20):
        # the canonical era badge plus any `_v2`/`alt/` siblings rotate
        # daily by the VIEWED date — the same one the card's own date
        # row reads (deep-travel aware, `real` already un-shifted it).
        era_art = pantheon.rotating_art_file(
            defaults.ERA_ART_DIR / era_file, date
        ) or defaults.ERA_ART_DIR / era_file
        era_block = (
            hover_badge(era_art)
            + hover_title(html.escape(self._tr(era_name)))
            + centered_html(html.escape(format_anno_lucis(real)), "")
        )

        season_event = self._dial.tick.season_event
        if season_event is not None:
            badge = (
                "Equinox" if "Equinox" in season_event
                else season_event.replace(" ", "_")
            )
            season_art = defaults.SEASON_ART_DIR / "turning_point" / f"{badge}.png"
        else:
            season_art = defaults.SEASON_ART_DIR / f"{self._current_season_key()}.png"

        # NO ECLIPSE LINE HERE ANY MORE (owner correction 2026-08-12):
        # this card is the DATE's, and the eclipse now has a body and a
        # card of its own (`_eclipse_text`) — the season event keeps the
        # row it always had.
        tail = []
        if season_event is not None:
            tail.append(html.escape(self._tr(season_event)))
        tail.append(f"{self._label('Season')} {self._season_row()}")
        tail.append(
            f"{self._label('Sign')} {html.escape(day.zodiac_symbol)} "
            f"{html.escape(self._tr(day.zodiac_name))} "
            f"({self._ord(day.zodiac_start.day)} "
            f"{html.escape(self._month(day.zodiac_start))} - "
            f"{self._ord(last.day)} {html.escape(self._month(last))})"
        )
        season_block = hover_badge(season_art) + centered_html(*tail)

        return date_block + era_block + season_block

    def _period_earth_html(self, kind: str) -> str:
        """The active region's own Earth face rides the Day/Night hover
        (owner 2026-07-12): the day art on the Day side, the night art
        on the Night side — atmosphere or clean per the Earth setting."""
        marker = self._dial.skin.year_marker
        region = earth_region(self._dial.day.latitude, self._dial.day.longitude)
        path = marker.variants.get(
            f"{self._dial.skin.earth_style}_{region}_{kind}"
        )
        if path is None:
            return ""
        small = scaled_variant_file(
            path, 2 * encyclopedia_ui.PERIOD_EARTH_IMAGE_PX
        )
        return (
            f"<div align='center'><img src='{small.as_uri()}' "
            f"width='{encyclopedia_ui.PERIOD_EARTH_IMAGE_PX}'/></div>"
        )

    def _season_row(self) -> str:
        """"Summer 20<sup>th</sup> of 94 Days" — the season at the
        current date. The event names already carry the climate zone
        (south flips them), so the season is the starting event's first
        word; the TROPICS read their WET/DRY halves instead (owner
        decision — bounded by the equinoxes, wet centered on the
        hemisphere's high sun)."""
        day = self._dial.day
        noon = datetime.combine(day.local_date, time(12, 0), day.tzinfo)
        if day.zone == "tropics":
            start, end, is_wet = self._wet_dry_span_at(noon)
            day_no = (day.local_date - start.astimezone(day.tzinfo).date()).days + 1
            total = round((end - start).total_seconds() / 86400)
            return self._tr("{season} {ordinal} of {total} Days").format(
                season=self._tr("Wet season" if is_wet else "Dry season"),
                ordinal=self._ord(day_no), total=total,
            )
        events = day.season_events
        index = max(
            i for i, (instant, _) in enumerate(events) if instant <= noon
        )
        start, name = events[index]
        end = events[index + 1][0]
        season = name.split()[0]        # the season STARTS at its event
        day_no = (day.local_date - start.astimezone(day.tzinfo).date()).days + 1
        total = round((end - start).total_seconds() / 86400)
        return self._tr("{season} {ordinal} of {total} Days").format(
            season=self._tr(season), ordinal=self._ord(day_no), total=total,
        )

    def _wet_dry_span_at(self, noon) -> tuple:
        """(start, end, is_wet) of the tropical half-year at `noon`:
        equinox-bounded, wet = the March→September half north of the
        equator and the September→March half south of it. The one
        boundary that can precede the anchor span (the previous
        September equinox, needed in January–March) is synthesized one
        tropical year before its bundled successor — day-count display
        accuracy."""
        anchors = self._dial.day.year_anchors
        equinoxes = [
            (instant, angle)
            for instant, angle in zip(anchors.instants, anchors.angles)
            if angle % 180.0 == 90.0    # 270 / 450 / 630 — the equinoxes
        ]
        synthetic = (
            equinoxes[1][0] - timedelta(days=sky.TROPICAL_YEAR_DAYS),
            equinoxes[1][1] - 360.0,    # the September equinox before the span
        )
        equinoxes.insert(0, synthetic)
        index = max(
            i for i, (instant, _) in enumerate(equinoxes) if instant <= noon
        )
        start, start_angle = equinoxes[index]
        end = equinoxes[index + 1][0]
        starts_in_march = start_angle % 360.0 == 270.0
        is_wet = starts_in_march != self._dial.day.southern_hemisphere
        return start, end, is_wet

    def _current_season_key(self) -> str:
        """The Encyclopedia SEASONS key for the current date — a
        temperate season ("Spring".."Winter") or a tropical half
        ("Wet_Season"/"Dry_Season"). Mirrors `_season_row`."""
        day = self._dial.day
        noon = datetime.combine(day.local_date, time(12, 0), day.tzinfo)
        if day.zone == "tropics":
            _start, _end, is_wet = self._wet_dry_span_at(noon)
            return "Wet_Season" if is_wet else "Dry_Season"
        events = day.season_events
        index = max(
            i for i, (instant, _) in enumerate(events) if instant <= noon
        )
        return events[index][1].split()[0]    # the season STARTS at its event

    def _wet_dry_block(self, span_start_angle: float) -> tuple[bool, str]:
        """The whole wet/dry season block (tropics), in the owner's
        2026-07-13 season format — title → space → bold From/To bounds
        → labeled Duration; returns (is_wet, html) so the caller can
        pick the badge."""
        start = self._anchor_instant(span_start_angle).astimezone(self._dial.day.tzinfo)
        end = self._anchor_instant(span_start_angle + 180.0).astimezone(
            self._dial.day.tzinfo
        )
        starts_in_march = span_start_angle % 360.0 == 270.0
        is_wet = starts_in_march != self._dial.day.southern_hemisphere
        days = (end - start).total_seconds() / 86400
        return is_wet, hover_title(
            html.escape(self._tr("Wet season" if is_wet else "Dry season"))
        ) + centered_html(
            "",
            f"<b>{self._tr('From')}</b> {self._ord(start.day)} "
            f"{self._month(start)} {self._year(start)}",
            f"<b>{self._tr('To')}</b> {self._ord(end.day)} "
            f"{self._month(end)} {self._year(end)}",
            f"{self._label('Duration')} {days:.1f} "
            f"{html.escape(self._tr('Days'))}",
        )

    def _span_line(self, start, end, days: float) -> str:
        """"21st December - 20th March (89.3 Days)" in the active
        language."""
        return (
            f"{self._ord(start.day)} {self._month(start)} - "
            f"{self._ord(end.day)} {self._month(end)} "
            f"({days:.1f} {self._tr('Days')})"
        )

    def _season_name_for(self, start_anchor_angle: float) -> str:
        """The temperate season STARTING at an unwrapped anchor angle —
        read from the zone-correct event names (the south already flips
        them): "Autumn Equinox" starts Autumn."""
        index = self._dial.day.year_anchors.angles.index(start_anchor_angle)
        return self._dial.day.season_events[index][1].split()[0]

    def _anchor_instant(self, unwrapped_angle: float):
        """Season-anchor instant at an unwrapped year-wheel angle."""
        anchors = self._dial.day.year_anchors
        return anchors.instants[anchors.angles.index(unwrapped_angle)]

    def _twilight_tooltip(self, point: QPointF, radius: float) -> str | None:
        """Hovering a twilight band (owner formatting round 2026-07-12):
        a bold Morning/Evening Twilight title, the labeled boundary
        times in the order the light moves, and the band's span in
        minutes AND dial degrees (15° per hour)."""
        import math

        sun = self._dial.day.sun
        distance = math.hypot(point.x(), point.y())
        if distance > radius * self._dial.interior_hit(self._dial.skin.background.aura_radius_fraction):
            return None
        theta = self._dial.world_theta(point)

        def within(start: float, end: float) -> bool:
            span_end = end if end > start else end + 360.0
            value = theta if theta >= start else theta + 360.0
            return start <= value <= span_end

        def band(title: str, a: str, first: datetime,
                 b: str, second: datetime) -> str:
            span = round((second - first).total_seconds() / 60)
            return centered_html(
                f"<b>{html.escape(self._tr(title))}</b>",
                f"{self._label(a)} {first:%H:%M} - "
                f"{self._label(b)} {second:%H:%M}",
                html.escape(f"{span} min - {span / 4:.2f}°"),
                # Owner 2026-07-12 ("add that info somewhere, in a few
                # words"): the band is CIVIL twilight — the 6° is the
                # Sun's depth, not a dial angle.
                html.escape(
                    self._tr("Civil twilight (Sun 6° below the horizon)")
                ),
            )

        angle = angles.time_to_dial_angle
        if sun.dawn is not None and sun.sunrise is not None and within(
            angle(sun.dawn), angle(sun.sunrise)
        ):
            return band(
                "Morning Twilight", "Dawn", sun.dawn, "Sunrise", sun.sunrise
            )
        if sun.sunset is not None and sun.dusk is not None and within(
            angle(sun.sunset), angle(sun.dusk)
        ):
            return band(
                "Evening Twilight", "Sunset", sun.sunset, "Dusk", sun.dusk
            )
        return None

    def _period_tooltip(self, point: QPointF, radius: float) -> str | None:
        """Aura/Umbra hovers (owner formatting round 2026-07-12): a mini
        Earth of the active region on top, then a bold Day/Night title
        with the duration, the labeled sun span, a blank line, and the
        twilight-extended span under its own With Twilight / Complete
        Dark title. Polar days/nights cover the whole wheel."""
        sun = self._dial.day.sun
        distance = math.hypot(point.x(), point.y())
        theta = self._dial.world_theta(point)
        angle = angles.time_to_dial_angle

        def within(start: float, end: float) -> bool:
            span_end = end if end > start else end + 360.0
            value = theta if theta >= start else theta + 360.0
            return start <= value <= span_end

        hours, minutes = (int(part) for part in self._dial.day.day_length.split(":"))
        if sun.sunrise is not None and sun.sunset is not None:
            in_day = within(angle(sun.sunrise), angle(sun.sunset))
        else:
            in_day = self._dial.day.day_length == "24:00"    # polar day / night
        if in_day:
            if distance > radius * self._dial.interior_hit(self._dial.skin.background.aura_radius_fraction):
                return None
            lines = [
                f"<b>{html.escape(self._tr('Day'))}</b> "
                f"{hours}h {minutes:02d}min"
            ]
            if sun.sunrise is not None and sun.sunset is not None:
                lines.append(
                    f"{self._label('Sunrise')} {sun.sunrise:%H:%M} - "
                    f"{self._label('Sunset')} {sun.sunset:%H:%M}"
                )
            if sun.dawn is not None and sun.dusk is not None:
                lines += [
                    "",
                    f"<b>{html.escape(self._tr('With Twilight'))}</b>",
                    f"{self._label('Dawn')} {sun.dawn:%H:%M} - "
                    f"{self._label('Dusk')} {sun.dusk:%H:%M}",
                ]
            return self._period_earth_html("day") + centered_html(*lines)
        if distance > radius * self._dial.interior_hit(self._dial.skin.background.umbra_radius_fraction):
            return None
        night = 24 * 60 - (hours * 60 + minutes)
        lines = [
            f"<b>{html.escape(self._tr('Night'))}</b> "
            f"{night // 60}h {night % 60:02d}min"
        ]
        if sun.sunset is not None and sun.sunrise is not None:
            lines.append(
                f"{self._label('Sunset')} {sun.sunset:%H:%M} - "
                f"{self._label('Sunrise')} {sun.sunrise:%H:%M}"
            )
        if sun.dusk is not None and sun.dawn is not None:
            lines += [
                "",
                f"<b>{html.escape(self._tr('Complete Dark'))}</b>",
                f"{self._label('Dusk')} {sun.dusk:%H:%M} - "
                f"{self._label('Dawn')} {sun.dawn:%H:%M}",
            ]
        return self._period_earth_html("night") + centered_html(*lines)

    def _period_word(self, minutes: int) -> str:
        """The day-period a wall-clock minute falls in on THIS date
        (owner approved 2026-07-12): Day, Night or one of the
        twilights — read off today's sun bounds."""
        sun = self._dial.day.sun

        def mins(when: datetime) -> int:
            return when.hour * 60 + when.minute

        if sun.sunrise is not None and sun.sunset is not None:
            if (
                sun.dawn is not None
                and mins(sun.dawn) <= minutes < mins(sun.sunrise)
            ):
                return self._tr("Morning Twilight")
            if mins(sun.sunrise) <= minutes < mins(sun.sunset):
                return self._tr("Day")
            if (
                sun.dusk is not None
                and mins(sun.sunset) <= minutes < mins(sun.dusk)
            ):
                return self._tr("Evening Twilight")
            return self._tr("Night")
        # Polar day / night spans the whole wheel.
        return self._tr("Day" if self._dial.day.day_length == "24:00" else "Night")

    def _greetings_tooltip(self) -> str:
        """The Four Greetings legend (owner 2026-07-14): the verses
        CENTERED in italic with their line breaks kept, then the
        reading and the watchmaker's commentary as a justified column
        — Serbian in every language, on the 12h/24h ring jewels."""
        data = _greetings()
        gap = encyclopedia_ui.GREETINGS_STANZA_GAP_PX
        # Small margins, not blank lines (owner round two) — Qt
        # collapses the adjacent margins to the larger one.
        stanzas = "".join(
            f"<div align='center' style='margin-top:{gap}px;"
            f"margin-bottom:{gap}px'><i>"
            + "<br/>".join(
                html.escape(line) for line in stanza.split("\n")
            )
            + "</i></div>"
            for stanza in data["verses"].split("\n\n")
        )
        return (
            hover_title(html.escape(data["title"]))
            + stanzas
            + article_body_html(
                data["explanation"] + "\n\n" + data["commentary"]
            )
        )
